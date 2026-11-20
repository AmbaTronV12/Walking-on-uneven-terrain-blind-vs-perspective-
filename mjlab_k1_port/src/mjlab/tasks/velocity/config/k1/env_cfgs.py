"""Booster K1 velocity environment configurations."""

from mjlab.asset_zoo.robots.booster_k1.k1_constants import (
  K1_ACTION_SCALE,
  get_k1_robot_cfg,
)
from mjlab.envs import ManagerBasedRlEnvCfg
from mjlab.envs import mdp as envs_mdp
from mjlab.envs.mdp.actions import JointPositionActionCfg
from mjlab.managers.event_manager import EventTermCfg
from mjlab.sensor import (
  ContactMatch,
  ContactSensorCfg,
  ObjRef,
  RayCastSensorCfg,
  RingPatternCfg,
  TerrainHeightSensorCfg,
)
from mjlab.tasks.velocity.mdp import UniformVelocityCommandCfg
from mjlab.tasks.velocity.velocity_env_cfg import make_velocity_env_cfg


def booster_k1_rough_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create Booster K1 rough terrain velocity configuration."""
  cfg = make_velocity_env_cfg()

  cfg.sim.mujoco.ccd_iterations = 500
  cfg.sim.contact_sensor_maxmatch = 500
  cfg.sim.nconmax = 70

  cfg.scene.entities = {"robot": get_k1_robot_cfg()}

  # Set raycast sensor frame to the K1 trunk.
  for sensor in cfg.scene.sensors or ():
    if sensor.name == "terrain_scan":
      assert isinstance(sensor, RayCastSensorCfg)
      assert isinstance(sensor.frame, ObjRef)
      sensor.frame.name = "trunk"

  site_names = ("left_foot", "right_foot")
  geom_names = ("left_foot_collision", "right_foot_collision")

  # Wire foot height scan to per-foot sites.
  for sensor in cfg.scene.sensors or ():
    if sensor.name == "foot_height_scan":
      assert isinstance(sensor, TerrainHeightSensorCfg)
      sensor.frame = tuple(
        ObjRef(type="site", name=s, entity="robot") for s in site_names
      )
      sensor.pattern = RingPatternCfg.single_ring(radius=0.03, num_samples=6)

  feet_ground_cfg = ContactSensorCfg(
    name="feet_ground_contact",
    primary=ContactMatch(
      mode="subtree",
      pattern=r"^(left_ankle_roll_link|right_ankle_roll_link)$",
      entity="robot",
    ),
    secondary=ContactMatch(mode="body", pattern="terrain"),
    fields=("found", "force"),
    reduce="netforce",
    num_slots=1,
    track_air_time=True,
  )
  cfg.scene.sensors = (cfg.scene.sensors or ()) + (feet_ground_cfg,)

  if cfg.scene.terrain is not None and cfg.scene.terrain.terrain_generator is not None:
    cfg.scene.terrain.terrain_generator.curriculum = True

  joint_pos_action = cfg.actions["joint_pos"]
  assert isinstance(joint_pos_action, JointPositionActionCfg)
  joint_pos_action.scale = K1_ACTION_SCALE

  cfg.viewer.body_name = "trunk"

  twist_cmd = cfg.commands["twist"]
  assert isinstance(twist_cmd, UniformVelocityCommandCfg)
  twist_cmd.viz.z_offset = 0.75

  cfg.events["foot_friction"].params["asset_cfg"].geom_names = geom_names
  cfg.events["base_com"].params["asset_cfg"].body_names = ("trunk",)

  # Pose tolerances (std). K1 has no waist or wrists, so those patterns are
  # omitted (a pattern that matches no joint may raise an error).
  cfg.rewards["pose"].params["std_standing"] = {".*": 0.05}
  cfg.rewards["pose"].params["std_walking"] = {
    # Lower body.
    r".*hip_pitch.*": 0.3,
    r".*hip_roll.*": 0.15,
    r".*hip_yaw.*": 0.15,
    r".*knee.*": 0.35,
    r".*ankle_pitch.*": 0.25,
    r".*ankle_roll.*": 0.1,
    # Arms.
    r".*shoulder_pitch.*": 0.15,
    r".*shoulder_roll.*": 0.15,
    r".*elbow.*": 0.15,
    # Head.
    r".*head.*": 0.1,
  }
  cfg.rewards["pose"].params["std_running"] = {
    # Lower body.
    r".*hip_pitch.*": 0.5,
    r".*hip_roll.*": 0.2,
    r".*hip_yaw.*": 0.2,
    r".*knee.*": 0.6,
    r".*ankle_pitch.*": 0.35,
    r".*ankle_roll.*": 0.15,
    # Arms.
    r".*shoulder_pitch.*": 0.5,
    r".*shoulder_roll.*": 0.2,
    r".*elbow.*": 0.35,
    # Head.
    r".*head.*": 0.1,
  }

  cfg.rewards["upright"].params["asset_cfg"].body_names = ("trunk",)
  cfg.rewards["body_ang_vel"].params["asset_cfg"].body_names = ("trunk",)

  for reward_name in ["foot_clearance", "foot_slip"]:
    cfg.rewards[reward_name].params["asset_cfg"].site_names = site_names

  cfg.rewards["body_ang_vel"].weight = -0.05
  cfg.rewards["angular_momentum"].weight = -0.02
  cfg.rewards["air_time"].weight = 0.0  # Same as G1 baseline.

  # Apply play mode overrides.
  if play:
    cfg.episode_length_s = int(1e9)

    cfg.observations["actor"].enable_corruption = False
    cfg.events.pop("push_robot", None)
    cfg.terminations.pop("out_of_terrain_bounds", None)
    cfg.curriculum = {}
    cfg.events["randomize_terrain"] = EventTermCfg(
      func=envs_mdp.randomize_terrain,
      mode="reset",
      params={},
    )

    if cfg.scene.terrain is not None:
      if cfg.scene.terrain.terrain_generator is not None:
        cfg.scene.terrain.terrain_generator.curriculum = False
        cfg.scene.terrain.terrain_generator.num_cols = 5
        cfg.scene.terrain.terrain_generator.num_rows = 5
        cfg.scene.terrain.terrain_generator.border_width = 10.0

  return cfg


def booster_k1_flat_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """Create Booster K1 flat terrain velocity configuration."""
  cfg = booster_k1_rough_env_cfg(play=play)

  cfg.sim.njmax = 300
  cfg.sim.mujoco.ccd_iterations = 50
  cfg.sim.contact_sensor_maxmatch = 64
  cfg.sim.nconmax = None

  # Switch to flat terrain.
  assert cfg.scene.terrain is not None
  cfg.scene.terrain.terrain_type = "plane"
  cfg.scene.terrain.terrain_generator = None

  # Remove raycast sensor and height scan (no terrain to scan).
  cfg.scene.sensors = tuple(
    s for s in (cfg.scene.sensors or ()) if s.name != "terrain_scan"
  )
  del cfg.observations["actor"].terms["height_scan"]
  del cfg.observations["critic"].terms["height_scan"]

  cfg.terminations.pop("out_of_terrain_bounds", None)

  # Disable terrain curriculum (not present in play mode since rough clears all).
  cfg.curriculum.pop("terrain_levels", None)

  if play:
    twist_cmd = cfg.commands["twist"]
    assert isinstance(twist_cmd, UniformVelocityCommandCfg)
    twist_cmd.ranges.lin_vel_x = (-0.5, 1.0)
    twist_cmd.ranges.ang_vel_z = (-0.7, 0.7)

  return cfg


def booster_k1_rough_blind_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """K1 rough terrain, blind: no height scan anywhere (same obs size as flat)."""
  cfg = booster_k1_rough_env_cfg(play=play)
  cfg.scene.sensors = tuple(
    s for s in (cfg.scene.sensors or ()) if s.name != "terrain_scan"
  )
  del cfg.observations["actor"].terms["height_scan"]
  del cfg.observations["critic"].terms["height_scan"]

  # K1 is slow (nominal ~0.5 m/s): keep the first velocity stage only.
  if "command_vel" in cfg.curriculum:
    cfg.curriculum["command_vel"].params["velocity_stages"] = [
      {"step": 0, "lin_vel_x": (-1.0, 1.0), "ang_vel_z": (-0.5, 0.5)},
    ]
  return cfg


def booster_k1_stairs_blind_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """K1 blind on the stairs-focused terrain set (box stairs + flat)."""
  from dataclasses import replace

  from mjlab.terrains.config import STAIRS_TERRAINS_CFG

  cfg = booster_k1_rough_blind_env_cfg(play=play)
  assert cfg.scene.terrain is not None
  gen = replace(STAIRS_TERRAINS_CFG)
  if play:
    gen.curriculum = False
    gen.num_rows = 5
    gen.num_cols = 5
    gen.border_width = 10.0
  cfg.scene.terrain.terrain_generator = gen
  return cfg


def booster_k1_stairs_perceptive_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """K1 perceptive (height scan) on the stairs-focused terrain set."""
  from dataclasses import replace

  from mjlab.terrains.config import STAIRS_TERRAINS_CFG

  cfg = booster_k1_rough_env_cfg(play=play)
  assert cfg.scene.terrain is not None
  gen = replace(STAIRS_TERRAINS_CFG)
  if play:
    gen.curriculum = False
    gen.num_rows = 5
    gen.num_cols = 5
    gen.border_width = 10.0
  cfg.scene.terrain.terrain_generator = gen

  # Same velocity cap as the blind variants (K1 is slow).
  if "command_vel" in cfg.curriculum:
    cfg.curriculum["command_vel"].params["velocity_stages"] = [
      {"step": 0, "lin_vel_x": (-1.0, 1.0), "ang_vel_z": (-0.5, 0.5)},
    ]
  return cfg


def _use_tall_stairs(cfg, play):
  from dataclasses import replace

  from mjlab.terrains.config import STAIRS_TALL_TERRAINS_CFG

  assert cfg.scene.terrain is not None
  gen = replace(STAIRS_TALL_TERRAINS_CFG)
  if play:
    gen.curriculum = False
    gen.num_rows = 5
    gen.num_cols = 5
    gen.border_width = 10.0
  cfg.scene.terrain.terrain_generator = gen
  return cfg


def booster_k1_stairs_tall_blind_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """K1 blind, stairs up to 0.20 m (tall-stairs experiment)."""
  return _use_tall_stairs(booster_k1_stairs_blind_env_cfg(play=play), play)


def booster_k1_stairs_tall_perceptive_env_cfg(
  play: bool = False,
) -> ManagerBasedRlEnvCfg:
  """K1 perceptive, stairs up to 0.20 m (tall-stairs experiment)."""
  return _use_tall_stairs(booster_k1_stairs_perceptive_env_cfg(play=play), play)


def booster_k1_rough_perceptive_env_cfg(play: bool = False) -> ManagerBasedRlEnvCfg:
  """K1 perceptive (height scan) on the full rough terrain mix, velocity capped."""
  cfg = booster_k1_rough_env_cfg(play=play)
  # Same velocity cap as the blind rough variant (K1 is slow).
  if "command_vel" in cfg.curriculum:
    cfg.curriculum["command_vel"].params["velocity_stages"] = [
      {"step": 0, "lin_vel_x": (-1.0, 1.0), "ang_vel_z": (-0.5, 0.5)},
    ]
  return cfg
