#!/bin/bash
cd ~/projects/mjlab || exit 1
NOTES=~/projects/terrain-walker/EXPERIMENTS_FULL.md
LOGDIR=~/projects/terrain-walker/train_logs
mkdir -p "$LOGDIR"
if [ ! -d logs/rsl_rl/k1_velocity ]; then echo "STOP: folder logs tidak ditemukan"; exit 1; fi
AC=$(cat /sys/class/power_supply/A*/online 2>/dev/null | head -1)
if [ "$AC" = "0" ]; then echo "STOP: charger belum terpasang"; exit 1; fi
for m in 2026-10-28_19-30-00_perceptive-init/model_9998.pt 2026-10-28_12-23-06/model_9998.pt; do
  [ -f logs/rsl_rl/k1_velocity/$m ] || { echo "STOP: checkpoint awal $m tidak ada"; exit 1; }
done
run () {  # task load_run load_ckpt tag
  echo "=== mulai $4 $(date '+%H:%M') ==="
  WANDB_MODE=disabled systemd-inhibit --what=idle:sleep --why="training RL" \
    uv run train $1 --env.scene.num-envs 768 --agent.max-iterations 5000 --agent.save-interval 200 \
    --agent.resume True --agent.load-run $2 --agent.load-checkpoint $3 2>&1 \
    | tee $LOGDIR/$4.log \
    | grep --line-buffered -E "Learning iteration|Mean reward|ETA|Error|Traceback"
  FOLDER=$(ls -td logs/rsl_rl/k1_velocity/*/ | head -1)
  cat >> $NOTES << NOTE

## $4 selesai ($(date '+%Y-%m-%d %H:%M'))
- Task: $1, init dari $2/$3, 768 env, 5000 iterasi tambahan, seed bawaan
- Medan: STAIRS_TALL_TERRAINS_CFG (easy 0,02-0,06 | moderate 0,06-0,12 | challenging 0,12-0,20 m)
- Folder: $FOLDER
- Log penuh: $LOGDIR/$4.log
- Tujuan: uji apakah lonjakan jatuh Run 9 di tangga 0,18 m karena tinggi tangga latihan maksimum hanya 0,10 m
NOTE
  echo "=== selesai $4 $(date '+%H:%M') ==="
}
run Mjlab-Velocity-StairsTall-Perceptive-Booster-K1 2026-10-28_19-30-00_perceptive-init model_9998.pt run9_tall
run Mjlab-Velocity-StairsTall-Blind-Booster-K1 2026-10-28_12-23-06 model_9998.pt run8_tall
echo "=== SEMUA SELESAI ==="
