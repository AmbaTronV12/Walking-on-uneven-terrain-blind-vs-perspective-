#!/bin/bash
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
[ -f $FONT ] || { echo "Font tidak ada: $FONT"; exit 1; }
C=~/projects/terrain-walker/videos/clips
T=/tmp/demo_parts
OUT=~/projects/terrain-walker/videos/demo_draft.mp4
mkdir -p $T && rm -f $T/*.mp4 $T/list.txt
card () {  # nama teks detik
  ffmpeg -y -loglevel error -f lavfi -i color=c=black:s=960x540:d=$3:r=30 \
    -vf "drawtext=fontfile=$FONT:text='$2':fontcolor=white:fontsize=34:x=(w-text_w)/2:y=(h-text_h)/2" \
    -pix_fmt yuv420p $T/$1.mp4
}
seg () {  # nama klip teks
  ffmpeg -y -loglevel error -i $C/$2/rl-video-step-0.mp4 \
    -vf "scale=960:540:force_original_aspect_ratio=decrease,pad=960:540:(ow-iw)/2:(oh-ih)/2,fps=30,drawtext=fontfile=$FONT:text='$3':fontcolor=white:fontsize=24:x=20:y=h-60:box=1:boxcolor=black@0.6:boxborderw=10" \
    -pix_fmt yuv420p -an $T/$1.mp4
}
card 01 "Berjalan di Medan Tidak Rata - Robot Booster K1" 3
seg  02 run10_random_rough "Run 10 (perceptive) di medan kasar - robot berjalan stabil"
seg  03 run10_slope_L0.8   "Run 10 di lereng curam - tidak jatuh tetapi hampir tidak maju (1,2 m)"
seg  04 run7_slope_L0.8    "Run 7 (blind) di lereng 39 derajat - contoh satu robot jatuh"
seg  05 run9_slope_L0.8    "Run 9 (perceptive) di lereng 39 derajat - contoh satu robot jatuh"
seg  06 run9_stairs_h0.18  "Tangga 0,18 m - Run 9 (perceptive) - contoh satu robot jatuh"
seg  07 run7_stairs_h0.18  "Tangga 0,18 m - Run 7 (blind) turun dengan baik lalu menabrak tangga"
card 08 "Satu seed, hasil indikatif - lihat laporan" 4
printf "file '%s'\n" $T/0*.mp4 > $T/list.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i $T/list.txt -c:v libx264 -pix_fmt yuv420p $OUT \
  && echo "OK: $OUT" && ls -la $OUT
