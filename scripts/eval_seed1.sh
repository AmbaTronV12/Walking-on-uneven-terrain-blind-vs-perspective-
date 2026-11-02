#!/bin/bash
cd ~/projects/mjlab
NOTES=~/projects/terrain-walker/EXPERIMENTS.md
echo "--- baris Folder di catatan (4 terakhir) ---"
grep "^- Folder:" $NOTES | tail -4
F10=$(grep "^- Folder:" $NOTES | tail -2 | head -1 | sed 's/^- Folder: //')
F7=$(grep "^- Folder:" $NOTES | tail -1 | sed 's/^- Folder: //')
echo "Run10 seed1: [$F10]"; echo "Run7  seed1: [$F7]"
echo "--- 3 folder run terbaru ---"
ls -td logs/rsl_rl/k1_velocity/*/ | head -3
if [ ! -f "${F10}model_9998.pt" ] || [ ! -f "${F7}model_9998.pt" ]; then
  echo "CHECKPOINT TIDAK DITEMUKAN di folder di atas. Kirim keluaran ini ke Claude."
  ls "$F10" "$F7" 2>&1 | head -20
  exit 1
fi
nvidia-smi --query-gpu=memory.used,temperature.gpu --format=csv

run_eval () {  # task ckpt label seed
  for t in flat pyramid_stairs pyramid_stairs_inv hf_pyramid_slope hf_pyramid_slope_inv random_rough wave_terrain; do
    echo "=== $3 $t seed$4 ==="
    systemd-inhibit --what=idle:sleep --why="eval RL" \
    uv run python -u ~/projects/terrain-walker/scripts/eval_policy.py \
      --task $1 --checkpoint $2 --label $3 --seed $4 --terrain-type $t \
      --out-dir ~/projects/terrain-walker/eval_t 2>&1 \
      | grep -E "EVAL\] (episodes|mean_distance)|Error|Traceback"
  done
}
for S in 0 1; do
  run_eval Mjlab-Velocity-Rough-Perceptive-Booster-K1 ${F10}model_9998.pt run10s1 $S
  run_eval Mjlab-Velocity-Rough-Blind-Booster-K1 ${F7}model_9998.pt run7s1 $S
done
echo "=== SELESAI ==="
python3 ~/projects/terrain-walker/scripts/compare_terrain.py run7_rough-blind run7s1 run10 run10s1
