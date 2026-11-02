"""Booster K1 constants."""

import math
from pathlib import Path

import mujoco

from mjlab import MJLAB_SRC_PATH
from mjlab.actuator import BuiltinPositionActuatorCfg
from mjlab.entity import EntityArticulationInfoCfg, EntityCfg
from mjlab.utils.spec_config import CollisionCfg

##
# MJCF and assets.
##

K1_XML: Path = (
  MJLAB_SRC_PATH / "asset_zoo" / "robots" / "booster_k1" / "xmls" / "k1.xml"
)
assert K1_XML.exists()


def get_spec() -> mujoco.MjSpec:
  return mujoco.MjSpec.from_file(str(K1_XML))


##
# Actuator config.
#
# Armature and effort limits come from K1_22dof.xml. Leg gains follow the G1
# recipe (stiffness = armature * w^2) but with a 5 Hz natural frequency, because
# 10 Hz gives very small action scales on K1. Arm/head stiffness is set directly
# since the XML armature (0.001) is too small to derive a useful gain.
# These are starting values: tune them after the standing test.
##

DAMPING_RATIO = 2.0
LEG_NATURAL_FREQ_HZ = 5.0
_W = 2.0 * math.pi * LEG_NATURAL_FREQ_HZ


def _leg_actuator(names, armature, effort):
  return BuiltinPositionActuatorCfg(
    target_names_expr=names,
    stiffness=armature * _W**2,
    damping=2.0 * DAMPING_RATIO * armature * _W,
    effort_limit=effort,
    armature=armature,
  )


def _soft_actuator(names, armature, stiffness, effort):
  return BuiltinPositionActuatorCfg(
    target_names_expr=names,
    stiffness=stiffness,
    damping=2.0 * DAMPING_RATIO * math.sqrt(stiffness * armature),
    effort_limit=effort,
    armature=armature,
  )


K1_ACTUATOR_HIP_PITCH = _leg_actuator((".*_hip_pitch_joint",), 0.0478125, 68.0)
K1_ACTUATOR_HIP_ROLL = _leg_actuator((".*_hip_roll_joint",), 0.0339552, 43.0)
K1_ACTUATOR_HIP_YAW = _leg_actuator((".*_hip_yaw_joint",), 0.0282528, 38.3)
K1_ACTUATOR_KNEE = _leg_actuator((".*_knee_pitch_joint",), 0.095625, 112.0)
K1_ACTUATOR_ANKLE = _leg_actuator(
  (".*_ankle_pitch_joint", ".*_ankle_roll_joint"), 0.0565, 38.3
)
K1_ACTUATOR_ARM = _soft_actuator(
  (
    ".*_shoulder_pitch_joint",
    ".*_shoulder_roll_joint",
    ".*_elbow_pitch_joint",
    ".*_elbow_yaw_joint",
  ),
  armature=0.001,
  stiffness=20.0,
  effort=14.0,
)
K1_ACTUATOR_HEAD = _soft_actuator(
  (".*head_yaw_joint", ".*head_pitch_joint"),
  armature=0.002,
  stiffness=10.0,
  effort=6.0,
)

##
# Keyframe config.
#
# Trunk-to-sole height with straight legs is about 0.55 m. Hip + knee + ankle
# pitch sum to zero so the feet are flat. Sign convention assumed same as G1.
##

HOME_KEYFRAME = EntityCfg.InitialStateCfg(
  pos=(0, 0, 0.56),
  joint_pos={
    ".*_hip_pitch_joint": -0.25,
    ".*_knee_pitch_joint": 0.5,
    ".*_ankle_pitch_joint": -0.25,
    "left_shoulder_roll_joint": -1.2,
    "right_shoulder_roll_joint": 1.2,
  },
  joint_vel={".*": 0.0},
)

##
# Collision config: only the feet collide (with the terrain).
##

FEET_ONLY_COLLISION = CollisionCfg(
  geom_names_expr=(r"^(left|right)_foot_collision$",),
  contype=0,
  conaffinity=1,
  condim=3,
  priority=1,
  friction=(0.6,),
)

##
# Final config.
##

K1_ARTICULATION = EntityArticulationInfoCfg(
  actuators=(
    K1_ACTUATOR_HIP_PITCH,
    K1_ACTUATOR_HIP_ROLL,
    K1_ACTUATOR_HIP_YAW,
    K1_ACTUATOR_KNEE,
    K1_ACTUATOR_ANKLE,
    K1_ACTUATOR_ARM,
    K1_ACTUATOR_HEAD,
  ),
  soft_joint_pos_limit_factor=0.9,
)


def get_k1_robot_cfg() -> EntityCfg:
  """Get a fresh K1 robot configuration instance."""
  return EntityCfg(
    init_state=HOME_KEYFRAME,
    collisions=(FEET_ONLY_COLLISION,),
    spec_fn=get_spec,
    articulation=K1_ARTICULATION,
  )


K1_ACTION_SCALE: dict[str, float] = {}
for a in K1_ARTICULATION.actuators:
  assert isinstance(a, BuiltinPositionActuatorCfg)
  e = a.effort_limit
  s = a.stiffness
  names = a.target_names_expr
  assert e is not None
  for n in names:
    K1_ACTION_SCALE[n] = 0.25 * e / s


if __name__ == "__main__":
  for pattern, scale in K1_ACTION_SCALE.items():
    print(f"{pattern:35s} action scale = {scale:.3f} rad")
