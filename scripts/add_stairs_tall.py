import os
R = os.path.expanduser("~/projects/mjlab/src/mjlab")

# 1) set medan baru di terrains/config.py
p = f"{R}/terrains/config.py"
s = open(p).read()
if "STAIRS_TALL_TERRAINS_CFG" in s:
    print("config.py sudah dipatch")
else:
    marker = "ALL_TERRAINS_CFG = TerrainGeneratorCfg("
    assert s.count(marker) == 1, "marker ALL_TERRAINS_CFG tidak unik"
    new = '''STAIRS_TALL_TERRAINS_CFG = TerrainGeneratorCfg(
  size=(8.0, 8.0),
  border_width=20.0,
  num_rows=10,
  num_cols=4,
  curriculum=True,
  sub_terrains={
    "flat": flat(proportion=0.25),
    "easy_stairs": pyramid_stairs(
      proportion=0.35,
      step_height_range=(0.02, 0.06),
      step_width=0.40,
    ),
    "moderate_stairs": pyramid_stairs(
      proportion=0.25,
      step_height_range=(0.06, 0.12),
      step_width=0.35,
      platform_width=2.5,
      border_width=0.8,
    ),
    "challenging_stairs": pyramid_stairs(
      proportion=0.15,
      step_height_range=(0.12, 0.20),
      step_width=0.30,
      platform_width=2.0,
      border_width=0.5,
    ),
  },
  add_lights=True,
)

'''
    open(p, "w").write(s.replace(marker, new + marker))
    print("config.py OK")

# 2) fungsi env di k1/env_cfgs.py
p = f"{R}/tasks/velocity/config/k1/env_cfgs.py"
s = open(p).read()
if "booster_k1_stairs_tall_blind_env_cfg" in s:
    print("env_cfgs.py sudah dipatch")
else:
    marker = "def booster_k1_rough_perceptive_env_cfg("
    assert s.count(marker) == 1, "marker rough_perceptive tidak unik"
    new = '''def _use_tall_stairs(cfg, play):
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


'''
    open(p, "w").write(s.replace(marker, new + marker))
    print("env_cfgs.py OK")

# 3) daftarkan task di k1/__init__.py
p = f"{R}/tasks/velocity/config/k1/__init__.py"
s = open(p).read()
if "StairsTall" in s:
    print("__init__.py sudah dipatch")
else:
    imp = "  booster_k1_stairs_blind_env_cfg,\n"
    assert s.count(imp) == 1, "baris import tidak unik"
    s = s.replace(imp, imp + "  booster_k1_stairs_tall_blind_env_cfg,\n  booster_k1_stairs_tall_perceptive_env_cfg,\n")
    s += '''
register_mjlab_task(
  task_id="Mjlab-Velocity-StairsTall-Blind-Booster-K1",
  env_cfg=booster_k1_stairs_tall_blind_env_cfg(),
  play_env_cfg=booster_k1_stairs_tall_blind_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Mjlab-Velocity-StairsTall-Perceptive-Booster-K1",
  env_cfg=booster_k1_stairs_tall_perceptive_env_cfg(),
  play_env_cfg=booster_k1_stairs_tall_perceptive_env_cfg(play=True),
  rl_cfg=booster_k1_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)
'''
    open(p, "w").write(s)
    print("__init__.py OK")
