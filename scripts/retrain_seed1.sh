#!/bin/bash
cd ~/projects/mjlab
NOTES=~/projects/terrain-walker/EXPERIMENTS.md
LOGDIR=~/projects/terrain-walker/train_logs

run () {  # task load_run load_ckpt tag
  echo "=== mulai $4 $(date '+%H:%M') ==="
  WANDB_MODE=disabled systemd-inhibit --what=idle:sleep --why="training RL" \
    uv run train $1 --env.scene.num-envs 768 --agent.max-iterations 5000 --agent.save-interval 200 \
    --agent.resume True --agent.load-run $2 --agent.load-checkpoint $3 \
    --agent.seed 1 --env.seed 1 2>&1 \
    | tee $LOGDIR/$4.log \
    | grep --line-buffered -E "Learning iteration|Mean reward|ETA|Error|Traceback"
  FOLDER=$(ls -td logs/rsl_rl/k1_velocity/*/ | head -1)
  cat >> $NOTES << NOTE

## $4 selesai ($(date '+%Y-%m-%d %H:%M'))
- Task: $1, init dari $2/$3, agent.seed 1, env.seed 1, 768 env, 5000 iterasi tambahan
- Folder: $FOLDER
- Log penuh: $LOGDIR/$4.log
- Tujuan: sampel pelatihan kedua untuk memisahkan efek height scan dari variasi pelatihan
NOTE
  echo "=== selesai $4 $(date '+%H:%M') ==="
}

run Mjlab-Velocity-Rough-Perceptive-Booster-K1 2026-10-30_perceptive-init-from-flat model_9998.pt run10_seed1
run Mjlab-Velocity-Rough-Blind-Booster-K1 2026-10-28_08-32-06 model_4999.pt run7_seed1
echo "=== SEMUA SELESAI ==="
