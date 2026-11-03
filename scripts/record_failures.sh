#!/bin/bash
cd ~/projects/mjlab
L=logs/rsl_rl/k1_velocity
rec () {  # name task ckpt extra-args...
  local name=$1 task=$2 ckpt=$3; shift 3
  export REC_DIR=~/projects/terrain-walker/videos/clips/$name
  mkdir -p $REC_DIR
  echo "=== klip $name ==="
  uv run python -u ~/projects/terrain-walker/scripts/record_policy.py \
    --task $task --checkpoint $ckpt --label rec_$name \
    --num-envs 8 --episodes-per-env 1 --episode-s 12 "$@" \
    --out-dir ~/projects/terrain-walker/eval_rec 2>&1 \
    | grep -E "terrain type|fixed|EVAL\] (episodes|mean_distance)|Recording|Error|Traceback"
  ls -la $REC_DIR | grep mp4 || echo "!! tidak ada mp4 untuk $name"
}
P=Mjlab-Velocity-Rough-Perceptive-Booster-K1
rec run10_random_rough $P $L/2026-10-30_23-17-57/model_9998.pt --terrain-type random_rough
rec run10_slope_L0.8 $P $L/2026-10-30_23-17-57/model_9998.pt --terrain-type hf_pyramid_slope --level 0.8
rec run7_slope_L0.8 Mjlab-Velocity-Rough-Blind-Booster-K1 $L/2026-10-28_12-23-06/model_9998.pt --terrain-type hf_pyramid_slope --level 0.8
rec run9_slope_L0.8 Mjlab-Velocity-Rough-Booster-K1 $L/2026-10-28_19-13-03/model_14997.pt --terrain-type hf_pyramid_slope --level 0.8
rec run9_stairs_h0.18 Mjlab-Velocity-Stairs-Perceptive-Booster-K1 $L/2026-10-28_19-13-03/model_14997.pt --stair-height 0.18
rec run7_stairs_h0.18 Mjlab-Velocity-Stairs-Blind-Booster-K1 $L/2026-10-28_12-23-06/model_9998.pt --stair-height 0.18
echo "=== SELESAI ==="
find ~/projects/terrain-walker/videos/clips -name "*.mp4" -exec ls -la {} \;
