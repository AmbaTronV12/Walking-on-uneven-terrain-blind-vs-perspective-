#!/bin/bash
# Percobaan B: sapuan tinggi tangga halus untuk Run 8 (blind) dan Run 9 (perceptive)
cd ~/projects/mjlab || exit 1
R8=logs/rsl_rl/k1_velocity/2026-10-28_17-53-58/model_14997.pt
R9=logs/rsl_rl/k1_velocity/2026-10-28_19-13-03/model_14997.pt
for f in "$R8" "$R9"; do
  [ -f "$f" ] || { echo "STOP: tidak ada $f (drive Windows sudah di-mount?)"; exit 1; }
done
OUT=~/projects/terrain-walker/eval_h
for H in 0.14 0.16 0.17; do
  for S in 0 1; do
    echo "=== run8 h=$H seed=$S $(date +%H:%M) ==="
    uv run python -u ~/projects/terrain-walker/scripts/eval_policy.py \
      --task Mjlab-Velocity-Stairs-Blind-Booster-K1 --checkpoint $R8 \
      --label run8_stairs-blind --seed $S --stair-height $H --out-dir $OUT
    echo "=== run9 h=$H seed=$S $(date +%H:%M) ==="
    uv run python -u ~/projects/terrain-walker/scripts/eval_policy.py \
      --task Mjlab-Velocity-Stairs-Perceptive-Booster-K1 --checkpoint $R9 \
      --label run9_stairs-perceptive --seed $S --stair-height $H --out-dir $OUT
  done
done
echo "=== SELESAI $(date +%H:%M) ==="
