#!/bin/bash
cd ~/projects/mjlab || exit 1
NOTES=~/projects/terrain-walker/EXPERIMENTS_FULL.md
LOGDIR=~/projects/terrain-walker/train_logs
mkdir -p "$LOGDIR"

# --- pemeriksaan awal ---
if [ ! -d logs/rsl_rl/k1_velocity ]; then
  echo "STOP: folder logs tidak ditemukan (drive Windows belum di-mount?)"; exit 1
fi
AC=$(cat /sys/class/power_supply/A*/online 2>/dev/null | head -1)
if [ "$AC" = "0" ]; then echo "STOP: charger belum terpasang"; exit 1; fi
for m in 2026-10-30_perceptive-init-from-flat/model_9998.pt 2026-10-28_08-32-06/model_4999.pt; do
  [ -f logs/rsl_rl/k1_velocity/$m ] || { echo "STOP: checkpoint awal $m tidak ada"; exit 1; }
done
nvidia-smi --query-gpu=memory.used,temperature.gpu --format=csv

run () {  # task load_run load_ckpt tag
  echo "=== mulai $4 $(date '+%H:%M') ==="
  WANDB_MODE=disabled systemd-inhibit --what=idle:sleep --why="training RL" \
    uv run train $1 --env.scene.num-envs 768 --agent.max-iterations 5000 --agent.save-interval 200 \
    --agent.resume True --agent.load-run $2 --agent.load-checkpoint $3 \
    --agent.seed 2 --env.seed 2 2>&1 \
    | tee $LOGDIR/$4.log \
    | grep --line-buffered -E "Learning iteration|Mean reward|ETA|Error|Traceback"
  FOLDER=$(ls -td logs/rsl_rl/k1_velocity/*/ | head -1)
  cat >> $NOTES << NOTE

## $4 selesai ($(date '+%Y-%m-%d %H:%M'))
- Task: $1, init dari $2/$3, agent.seed 2, env.seed 2, 768 env, 5000 iterasi tambahan
- Folder: $FOLDER
- Log penuh: $LOGDIR/$4.log
- Tujuan: sampel pelatihan ketiga (seed 2) untuk menguatkan perbandingan blind vs perceptive
NOTE
  echo "=== selesai $4 $(date '+%H:%M') ==="
}

run Mjlab-Velocity-Rough-Perceptive-Booster-K1 2026-10-30_perceptive-init-from-flat model_9998.pt run10_seed2
run Mjlab-Velocity-Rough-Blind-Booster-K1 2026-10-28_08-32-06 model_4999.pt run7_seed2
echo "=== SEMUA SELESAI ==="
