#!/bin/bash
cd ~/projects/mjlab || exit 1
NOTES=~/projects/terrain-walker/EXPERIMENTS_FULL.md
echo "--- baris Folder di catatan (3 terakhir) ---"
grep "^- Folder:" $NOTES | tail -3
F10=$(grep "^- Folder:" $NOTES | tail -2 | head -1 | sed 's/^- Folder: //')
F7=$(grep "^- Folder:" $NOTES | tail -1 | sed 's/^- Folder: //')
echo "Run10 seed2: [$F10]"; echo "Run7  seed2: [$F7]"
echo "--- 2 folder run terbaru ---"
ls -td logs/rsl_rl/k1_velocity/*/ | head -2
L1=$(ls -td logs/rsl_rl/k1_velocity/*/ | head -1)
L2=$(ls -td logs/rsl_rl/k1_velocity/*/ | head -2 | tail -1)
if [ "$F7" != "$L1" ] || [ "$F10" != "$L2" ]; then
  echo "STOP: folder di catatan tidak sama dengan 2 folder terbaru. Kirim keluaran ini ke Claude."; exit 1
fi
C10=$(ls -v ${F10}model_*.pt | tail -1)
C7=$(ls -v ${F7}model_*.pt | tail -1)
echo "Checkpoint Run10: $C10"; echo "Checkpoint Run7 : $C7"
nvidia-smi --query-gpu=memory.used,temperature.gpu --format=csv

run_eval () {  # task ckpt label seed
  for t in flat pyramid_stairs pyramid_stairs_inv hf_pyramid_slope hf_pyramid_slope_inv random_rough wave_terrain; do
    echo "=== $3 $t seed$4 $(date '+%H:%M') ==="
    systemd-inhibit --what=idle:sleep --why="eval RL" \
    uv run python -u ~/projects/terrain-walker/scripts/eval_policy.py \
      --task $1 --checkpoint $2 --label $3 --seed $4 --terrain-type $t \
      --out-dir ~/projects/terrain-walker/eval_t 2>&1 \
      | grep -E "EVAL\] (episodes|mean_distance)|Error|Traceback"
  done
}
for S in 0 1; do
  run_eval Mjlab-Velocity-Rough-Perceptive-Booster-K1 $C10 run10s2 $S
  run_eval Mjlab-Velocity-Rough-Blind-Booster-K1 $C7 run7s2 $S
done
echo "=== SELESAI $(date '+%H:%M') ==="
