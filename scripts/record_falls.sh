#!/bin/bash
# Rekam ulang sampai robot yang direkam benar-benar jatuh (cek CSV run yang sama).
cd ~/projects/terrain-walker
mkdir -p videos/keep
[ -d videos/clips_backup ] || cp -r videos/clips videos/clips_backup
TARGETS="run7_stairs_h0.18 run9_stairs_h0.18 run7_slope_L0.8 run9_slope_L0.8"
rm -f videos/keep/*.mp4
for k in 0 1 2 3 4 5 6 7; do
  echo "=== REC_ENV=$k ($(date +%H:%M:%S)) ==="
  REC_ENV=$k REC_ELEV=-35 REC_AZ=90 REC_DIST=5 bash scripts/record_failures.sh > /tmp/rec_k$k.log 2>&1
  for n in $TARGETS; do
    [ -f videos/keep/$n.mp4 ] && continue
    csv=$(ls eval_rec/rec_${n}_speed*.csv | head -1)
    if [ "$(python3 scripts/fell_check.py "$csv" $k)" = "1" ]; then
      cp videos/clips/$n/rl-video-step-0.mp4 videos/keep/$n.mp4
      echo "   DAPAT: $n (env $k jatuh)"
    fi
  done
  [ "$(ls videos/keep/*.mp4 2>/dev/null | wc -l)" -ge 4 ] && break
done
for n in $TARGETS; do
  if [ -f videos/keep/$n.mp4 ]; then
    cp videos/keep/$n.mp4 videos/clips/$n/rl-video-step-0.mp4
  else
    echo "   TIDAK ADA robot jatuh untuk $n (klip lama dipakai)"
    cp videos/clips_backup/$n/rl-video-step-0.mp4 videos/clips/$n/rl-video-step-0.mp4
  fi
done
echo SELESAI
