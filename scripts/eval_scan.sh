#!/bin/bash
cd ~/projects/mjlab || exit 1
R9=logs/rsl_rl/k1_velocity/2026-10-28_19-13-03/model_14997.pt
[ -f "$R9" ] || { echo "STOP: tidak ada $R9"; exit 1; }
OUT=~/projects/terrain-walker/eval_scan
for H in 0.15 0.18; do
  for S in 0 1; do
    for M in zero shuffle; do
      echo "=== run9 scan=$M h=$H seed=$S $(date +%H:%M) ==="
      uv run python -u ~/projects/terrain-walker/scripts/eval_policy_scan.py \
        --task Mjlab-Velocity-Stairs-Perceptive-Booster-K1 --checkpoint $R9 \
        --label run9_scan-$M --seed $S --stair-height $H --scan-mode $M --out-dir $OUT
    done
  done
done
echo "=== SELESAI $(date +%H:%M) ==="
