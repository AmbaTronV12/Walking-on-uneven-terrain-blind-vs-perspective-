#!/bin/bash
cd ~/projects/mjlab || exit 1
NOTES=~/projects/terrain-walker/EXPERIMENTS_FULL.md
OUT=~/projects/terrain-walker/eval_tall
folder_of () {  # tag -> nama folder run
  awk -v t="## $1 selesai" 'index($0,t)==1{f=1;next} f&&/^- Folder:/{print $3; exit}' $NOTES | xargs -r basename
}
F9T=$(folder_of run9_tall); F8T=$(folder_of run8_tall)
echo "run9_tall=$F9T run8_tall=$F8T"
[ -n "$F9T" ] && [ -n "$F8T" ] || { echo "STOP: folder tidak ketemu di catatan"; exit 1; }
CK=model_14997.pt
B=logs/rsl_rl/k1_velocity
for f in $B/$F9T/$CK $B/$F8T/$CK $B/2026-10-28_19-13-03/$CK $B/2026-10-28_17-53-58/$CK; do
  [ -f "$f" ] || { echo "STOP: tidak ada $f"; exit 1; }
done
ev () {  # task ckpt label h seed
  echo "=== $3 h=$4 seed=$5 $(date +%H:%M) ==="
  uv run python -u ~/projects/terrain-walker/scripts/eval_policy.py --task $1 --checkpoint $2 \
    --label $3 --seed $5 --stair-height $4 --out-dir $OUT 2>&1 | grep -E "EVAL\] (fixed|csv)|Error|Traceback|KeyError"
}
for H in 0.12 0.15 0.18 0.20; do
  for S in 0 1; do
    ev Mjlab-Velocity-StairsTall-Perceptive-Booster-K1 $B/$F9T/$CK run9_tall-perceptive $H $S
    ev Mjlab-Velocity-StairsTall-Blind-Booster-K1 $B/$F8T/$CK run8_tall-blind $H $S
  done
done
for S in 0 1; do
  ev Mjlab-Velocity-Stairs-Perceptive-Booster-K1 $B/2026-10-28_19-13-03/$CK run9_stairs-perceptive 0.20 $S
  ev Mjlab-Velocity-Stairs-Blind-Booster-K1 $B/2026-10-28_17-53-58/$CK run8_stairs-blind 0.20 $S
done
echo "=== SELESAI $(date +%H:%M) ==="
