"""Controlled evaluation of a trained mjlab velocity policy (no viewer)."""

import argparse
import csv
from dataclasses import asdict, replace
from pathlib import Path

import torch

import mjlab.tasks  # noqa: F401  (populates the task registry)
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import MjlabOnPolicyRunner, RslRlVecEnvWrapper
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.utils.torch import configure_torch_backends


def main():
  p = argparse.ArgumentParser()
  p.add_argument("--task", required=True)
  p.add_argument("--checkpoint", required=True)
  p.add_argument("--label", required=True)
  p.add_argument("--num-envs", type=int, default=32)
  p.add_argument("--episodes-per-env", type=int, default=3)
  p.add_argument("--speed", type=float, default=0.5)
  p.add_argument("--seed", type=int, default=0)
  p.add_argument("--stair-height", type=float, default=None)
  p.add_argument("--terrain-type", default=None)
  p.add_argument("--level", type=float, default=None)
  p.add_argument("--episode-s", type=float, default=20.0)
  p.add_argument("--out-dir", default="~/projects/terrain-walker/eval")
  a = p.parse_args()

  configure_torch_backends()
  device = "cuda:0" if torch.cuda.is_available() else "cpu"
  torch.manual_seed(a.seed)

  env_cfg = load_env_cfg(a.task, play=True)
  agent_cfg = load_rl_cfg(a.task)
  env_cfg.scene.num_envs = a.num_envs
  env_cfg.episode_length_s = a.episode_s
  print("[EVAL] episode_length_s =", env_cfg.episode_length_s)

  # Freeze the command: constant forward speed, nothing else.
  print("[EVAL] curriculum terms before:", list(env_cfg.curriculum.keys()))
  for k in list(env_cfg.curriculum.keys()):
    env_cfg.curriculum.pop(k)
  cmd = env_cfg.commands["twist"]
  cmd.ranges = replace(
    cmd.ranges,
    lin_vel_x=(a.speed, a.speed),
    lin_vel_y=(0.0, 0.0),
    ang_vel_z=(0.0, 0.0),
    heading=None,
  )
  cmd.heading_command = False
  cmd.rel_standing_envs = 0.0
  cmd.rel_world_envs = 0.0
  cmd.rel_forward_envs = 0.0
  cmd.init_velocity_prob = 0.0

  if a.stair_height is not None:
    gen = env_cfg.scene.terrain.terrain_generator
    src = gen.sub_terrains["challenging_stairs"]
    stairs = replace(
      src, proportion=1.0, step_height_range=(a.stair_height, a.stair_height)
    )
    env_cfg.scene.terrain.terrain_generator = replace(
      gen, sub_terrains={"fixed_stairs": stairs}
    )
    print("[EVAL] fixed stair height:", a.stair_height)

  if a.terrain_type is not None:
    gen = env_cfg.scene.terrain.terrain_generator
    src = gen.sub_terrains[a.terrain_type]
    if a.level is not None:
      for fld in ("step_height_range", "slope_range", "noise_range", "amplitude_range"):
        if hasattr(src, fld):
          lo, hi = getattr(src, fld)
          v = lo + a.level * (hi - lo)
          src = replace(src, **{fld: (v, v)})
          print("[EVAL]", fld, "fixed at", round(v, 4))
          break
    src = replace(src, proportion=1.0)
    env_cfg.scene.terrain.terrain_generator = replace(
      gen, sub_terrains={a.terrain_type: src}
    )
    print("[EVAL] terrain type:", a.terrain_type, "level:", a.level)

  env = ManagerBasedRlEnv(cfg=env_cfg, device=device, render_mode=None)
  uenv = env
  env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
  runner_cls = load_runner_cls(a.task) or MjlabOnPolicyRunner
  runner = runner_cls(env, asdict(agent_cfg), device=device)
  runner.load(a.checkpoint, load_cfg={"actor": True}, strict=True, map_location=device)
  policy = runner.get_inference_policy(device=device)

  robot = uenv.scene["robot"]
  dt = uenv.step_dt
  n = uenv.num_envs

  def pos_xy():
    d = robot.data
    if hasattr(d, "root_link_pos_w"):
      return d.root_link_pos_w[:, :2].clone()
    return d.root_link_pose_w[:, :2].clone()

  uenv.reset(seed=a.seed)
  obs = env.get_observations()

  start = pos_xy()
  prev = start.clone()
  ep_len = torch.zeros(n, device=device)
  sway_sum = torch.zeros(n, device=device)
  verr_sum = torch.zeros(n, device=device)
  done_eps = torch.zeros(n, dtype=torch.long, device=device)
  rows = []

  max_steps = a.episodes_per_env * uenv.max_episode_length + 5
  with torch.inference_mode():
    for step_i in range(max_steps):
      if step_i % 100 == 0:
        print(f"[EVAL] step {step_i}/{max_steps}", flush=True)
      actions = policy(obs)
      obs, _, _, _ = env.step(actions)
      terminated = uenv.reset_terminated.clone()
      timed_out = uenv.reset_time_outs.clone()
      done = terminated | timed_out
      ep_len += 1
      sway_sum += torch.norm(robot.data.root_link_ang_vel_b[:, :2], dim=-1)
      verr_sum += torch.norm(
        uenv.command_manager.get_command("twist")[:, :2]
        - robot.data.root_link_lin_vel_b[:, :2],
        dim=-1,
      )
      for i in done.nonzero(as_tuple=False).flatten().tolist():
        if done_eps[i] >= a.episodes_per_env:
          continue
        dist = torch.norm(prev[i] - start[i]).item()
        length = ep_len[i].item()
        rows.append(
          dict(
            label=a.label, env=i, episode=int(done_eps[i]),
            fell=int(terminated[i].item()), length_steps=int(length),
            distance_m=round(dist, 3),
            start_x=round(start[i, 0].item(), 2),
            start_y=round(start[i, 1].item(), 2),
            end_x=round(prev[i, 0].item(), 2),
            end_y=round(prev[i, 1].item(), 2),
            commanded_m=round(a.speed * length * dt, 3),
            sway=round(sway_sum[i].item() / length, 4),
            vel_err=round(verr_sum[i].item() / length, 4),
          )
        )
        done_eps[i] += 1
      if done.any():
        ids = done.nonzero(as_tuple=False).flatten()
        start[ids] = pos_xy()[ids]
        ep_len[ids] = 0
        sway_sum[ids] = 0
        verr_sum[ids] = 0
      prev = pos_xy()
      if bool((done_eps >= a.episodes_per_env).all()):
        break

  out_dir = Path(a.out_dir).expanduser()
  out_dir.mkdir(parents=True, exist_ok=True)
  tag = f"_h{a.stair_height}" if a.stair_height is not None else ""
  if a.terrain_type is not None:
    tag += f"_{a.terrain_type}" + (f"_L{a.level}" if a.level is not None else "")
  out = out_dir / f"{a.label}_speed{a.speed}_seed{a.seed}{tag}.csv"
  with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

  m = len(rows)
  falls = sum(r["fell"] for r in rows)
  mean = lambda k: sum(r[k] for r in rows) / m
  prog = sum(r["distance_m"] / max(r["commanded_m"], 1e-6) for r in rows) / m
  print(f"\n[EVAL] {a.label}  task={a.task}  speed={a.speed}  seed={a.seed}")
  print(f"[EVAL] episodes={m}  falls={falls}  fall_rate={falls / m:.3f}")
  print(f"[EVAL] mean_distance={mean('distance_m'):.2f} m  progress_ratio={prog:.2f}")
  print(f"[EVAL] mean_length={mean('length_steps'):.0f} steps  sway={mean('sway'):.3f}  vel_err={mean('vel_err'):.3f}")
  print(f"[EVAL] csv: {out}")
  env.close()


if __name__ == "__main__":
  main()
