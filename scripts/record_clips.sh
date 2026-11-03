#!/bin/bash
cd ~/projects/mjlab
OUT=~/projects/terrain-walker/videos
mkdir -p $OUT
record () {  # task checkpoint_file name
  local folder=$(dirname $2)
  local mp4=$folder/videos/play/rl-video-step-0.mp4
  local before=$(stat -c %Y $mp4 2>/dev/null || echo 0)
  echo "=== rekam $3 ==="
  setsid uv run play $1 --checkpoint-file $2 --num-envs 5 --video True --video-length 800 > /tmp/play_$3.log 2>&1 &
  local pid=$!
  local waited=0
  while [ $waited -lt 420 ]; do
    sleep 5; waited=$((waited+5))
    if [ -f $mp4 ] && [ $(stat -c %Y $mp4) -gt $before ]; then
      sleep 6
      kill -- -$pid 2>/dev/null; pkill -f "play $1" 2>/dev/null
      cp $mp4 $OUT/$3.mp4 && echo "OK: $OUT/$3.mp4 ($(du -h $OUT/$3.mp4 | cut -f1))"
      return
    fi
  done
  kill -- -$pid 2>/dev/null; pkill -f "play $1" 2>/dev/null
  echo "GAGAL/TIMEOUT untuk $3, cek /tmp/play_$3.log"
}
L=logs/rsl_rl/k1_velocity
record Mjlab-Velocity-Rough-Perceptive-Booster-K1 $L/2026-10-30_23-17-57/model_9998.pt run10_rough_perceptive
record Mjlab-Velocity-Rough-Blind-Booster-K1 $L/2026-10-28_12-23-06/model_9998.pt run7_rough_blind
record Mjlab-Velocity-Stairs-Blind-Booster-K1 $L/2026-10-28_17-53-58/model_14997.pt run8_stairs_blind
record Mjlab-Velocity-Stairs-Perceptive-Booster-K1 $L/2026-10-28_19-13-03/model_14997.pt run9_stairs_perceptive
echo "=== SELESAI ==="
ls -la $OUT
