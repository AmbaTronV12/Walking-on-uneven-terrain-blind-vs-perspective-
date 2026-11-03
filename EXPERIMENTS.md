# Catatan Eksperimen (ringkas): Walking on Uneven Terrain

Robot: Booster K1 (22 sendi) | Simulator: mjlab (MuJoCo Warp), commit dasar 8bb2bc9e187797689ec82c78c35019afd2fd0376 | Algoritma: PPO (rsl_rl) | GPU: RTX 4050 6 GB
Log lengkap kronologis: `EXPERIMENTS_FULL.md` (tidak diubah). Berkas ini merangkum keputusan dan hasil akhir.

## 1. Persiapan (27 Okt)
- Go1 datar (10.000 iterasi, reward 79,2, episode length 994) dipakai sebagai pemanasan alur kerja; G1 diuji singkat; K1 dipilih sebagai robot utama.
- K1 dipasang ke mjlab: `asset_zoo/robots/booster_k1/k1_constants.py`, `tasks/velocity/config/k1/{env_cfgs,rl_cfg,__init__}.py`. Data motor dari `K1_22dof.xml`, pose awal dengan lengan turun, gain kaki 5 Hz, hanya telapak kaki yang bertabrakan.
- Uji 300 iterasi: K1 berdiri dan tidak jatuh (episode length 500; G1 pada iterasi sekitar 350: 55).
- Ukuran jumlah robot datar: 512 robot 23 ribu steps/s, 1024 robot 38 ribu, 2048 robot 45 ribu (kenaikan mengecil).

## 2. Run utama

| Run | Task | Titik awal | Medan latih | Hasil kunci (iterasi akhir) |
|---|---|---|---|---|
| 5 | Flat-Booster-K1 | Dari nol | Datar | Reward 72,97; episode length 985; 2048 robot, 5000 iterasi, 55 menit |
| 6 | Rough-Booster-K1 (perceptive) | Dari nol | Kasar campuran | Reward 12,75; robot diam; level medan 0,01 (GAGAL) |
| 7 | Rough-Blind-Booster-K1 | Run 5 (model_4999) | Kasar campuran | Reward 29,34; level medan 4,59; episode length 881 |
| 8 | Stairs-Blind-Booster-K1 | Run 7 | Tangga | Reward 48,25; level medan 6,06 |
| 9 | Stairs-Perceptive-Booster-K1 | Run 7 + 187 kolom nol | Tangga | Reward 59,20; level medan 6,03; episode length 1000 |
| 10 | Rough-Perceptive-Booster-K1 | Run 5 + 187 kolom nol | Kasar campuran | Reward 35,36 (satu titik data); level medan 5,41 |

Run 7 dan Run 10 diulang dengan seed latih 1 (`--agent.seed 1 --env.seed 1`). Run 7 dan 10: 768 robot, 5000 iterasi lanjutan.
Folder run: lihat `EXPERIMENTS_FULL.md` (Run 7 = `2026-10-28_12-23-06`, Run 8 = `17-53-58`, Run 9 = `19-13-03`, Run 10 = `2026-10-30_23-17-57`, Run 7 seed 1 = `2026-10-31_02-49-31`, Run 10 seed 1 = `2026-10-31_01-58-35`).

### Keputusan penting dan alasannya
- Run 6 gagal: dari nol di medan sulit robot memilih berdiri diam (dugaan, belum terbukti). Maka semua run berikutnya dilanjutkan dari model datar.
- Kecepatan perintah dikunci pada tahap 1 (sampai 1 m/s): tahap 2 kurikulum (sampai 2 m/s) diduga melampaui kemampuan K1 (nominal sekitar 0,5 m/s).
- Run 10 dibuat dengan titik awal, medan, dan iterasi sama dengan Run 7 (bukan dilanjutkan dari Run 7), supaya hanya height scan yang berbeda.
- Perluasan bobot perceptive: kolom baru bernilai nol (aktor 78 menjadi 265, kritik 90 menjadi 277), jadi kebijakan awal identik dengan blind.

## 3. Protokol evaluasi (`scripts/eval_policy.py`)
- Tanpa viewer; perintah maju dibekukan 0,5 m/s; kurikulum dimatikan; 32 robot x 3 episode x 20 s (1000 langkah); dua seed evaluasi (n = 192 per sel untuk Run 7 dan 10, n = 96 untuk Run 8 dan 9).
- Jatuh asli = terminasi selain habis waktu dan bukan keluar tepi medan (|x| atau |y| >= 29,5). Alasan: uji 0,8 m/s menunjukkan semua "jatuh" adalah robot keluar peta; jarak perintah kini dibatasi sekitar 12 m.
- Metrik: persen jatuh asli, jarak (perpindahan), kecepatan efektif, sway (norma kecepatan sudut roll/pitch), vel_err.
- Batasan: episode dalam satu robot berbagi medan; GPU tidak deterministik; satu seed evaluasi untuk Run 8 dan 9.
- Satuan `fell_over` di log latihan = jumlah robot yang berakhir per kejadian reset, bukan persen.
- Kemiringan: `slope_range` adalah gradien (rise/run); level 0,2 / 0,4 / 0,6 / 0,8 kira-kira 11 / 22 / 31 / 39 derajat.

## 4. Hasil

### 4.1 Tangga (seed 0, 0,5 m/s, tinggi tetap)
Jatuh % (Run 7 / Run 8 / Run 9): 0,10 m: 10,4 / 0 / 1,0. 0,12 m: 22,9 / 3,1 / 4,2. 0,15 m: 53,1 / 8,3 / 10,4. 0,18 m: 61,5 / 22,9 / 55,2.
Dua seed pada 0,18 m: Run 8 17,7 persen, Run 9 54,2 persen. Batas tinggi latih 0,10 m. Hipotesis (height scan di luar rentang latih) belum diuji.

### 4.2 Run 7 vs Run 10, dua seed latih (jatuh % / jarak m, dua seed evaluasi digabung)

| Medan | Run 7 (42) | Run 7 (1) | Run 10 (42) | Run 10 (1) |
|---|---|---|---|---|
| Datar | 0 / 9,4 | 0 / 9,2 | 0 / 7,4 | 0 / 8,5 |
| Tangga naik | 1,0 / 8,7 | 1,0 / 8,8 | 0 / 5,5 | 0 / 8,0 |
| Tangga turun | 0 / 7,1 | 2,6 / 7,9 | 0 / 7,1 | 0,5 / 8,5 |
| Lereng naik | 35,4 / 6,3 | 21,4 / 7,0 | 9,9 / 4,5 | 7,3 / 4,7 |
| Cekungan | 25,0 / 3,2 | 26,6 / 2,5 | 16,1 / 4,7 | 25,0 / 4,6 |
| Kasar acak | 14,1 / 4,2 | 11,5 / 3,8 | 12,0 / 5,9 | 15,6 / 6,6 |
| Gelombang | 16,1 / 4,8 | 18,8 / 4,3 | 15,1 / 6,6 | 16,7 / 7,2 |

### 4.3 Lereng naik per kemiringan (seed 0, n = 96; jatuh % / jarak m)

| Gradien (derajat) | Run 7 | Run 8 | Run 9 | Run 10 |
|---|---|---|---|---|
| 0,2 (11) | 3,1 / 8,3 | 3,1 / 8,5 | 0,0 / 8,9 | 5,2 / 7,2 |
| 0,4 (22) | 5,2 / 7,4 | 3,1 / 7,3 | 9,4 / 7,9 | 8,3 / 5,8 |
| 0,6 (31) | 33,3 / 6,1 | 25,0 / 6,5 | 41,7 / 5,8 | 10,4 / 2,1 |
| 0,8 (39) | 65,6 / 4,8 | 54,2 / 5,2 | 68,8 / 4,5 | 6,2 / 1,6 |

Kecepatan efektif (m/s), Run 7 vs Run 10 (dua seed): datar 0,47 / 0,37; lereng 0,6: 0,47 / 0,11; lereng 0,8: 0,57 / 0,09; kasar acak 0,25 / 0,32; gelombang 0,33 / 0,42.

### 4.4 Penggabungan bobot (2026-11-03)
- Interpolasi aktor (1 - a) x Run 7 + a x Run 10 (`scripts/merge_actors.py`; lapisan pertama Run 7 ditulis ulang ke ruang normalisasi Run 10, kolom height scan = 0). Kriteria ditetapkan sebelum evaluasi.
- a = 0,5 (jatuh % / jarak m): datar 0 / 7,9; lereng 22,4 / 6,6; kasar acak 18,8 / 4,0; gelombang 13,0 / 4,5. Kriteria jatuh lereng sekitar 8-10 persen dan jarak datar sekitar 9 m gagal; tidak ada sinergi. Nilai a lain tidak dievaluasi.

## 5. Kesimpulan
- Keunggulan perceptive hanya konsisten pada jarak tempuh di kasar acak dan gelombang (sekitar 40-70 persen lebih jauh dengan jatuh setara).
- Di lereng curam Run 10 jarang jatuh karena hampir berhenti, bukan karena mendaki lebih baik.
- Tangga dan datar: setara. Cekungan: tumpang tindih. Penggabungan bobot: tidak ada sinergi.
- Hanya dua seed latih per resep; semua kesimpulan bersifat indikatif.

### Klaim yang ditarik
"Run 10 lebih sedikit jatuh di lereng" (karena berhenti); "height scan membantu kasar acak dan gelombang" (hanya jarak); "Run 10 lebih buruk di gelombang" dan "Run 10 lambat di tangga" (variasi seed latih); "Run 9 lebih sering jatuh pada 0,8 m/s" (artefak tepi peta); "Run 8/9 melupakan medan lain" (tidak didukung).

## 6. Video demo (2026-11-03)
- Klip play bawaan tidak representatif. `scripts/record_policy.py` merekam 8 robot, perintah beku 0,5 m/s, episode 12 s, kamera atas dan samping (`REC_ELEV=-35 REC_AZ=90 REC_DIST=5`; elevasi harus negatif agar kamera di atas).
- Satu klip merekam satu robot (`REC_ENV`); `scripts/record_falls.sh` mengulang sampai robot yang direkam tercatat jatuh di CSV run yang sama. `scripts/compile_demo.sh` menyusun `videos/demo_draft.mp4` (79 detik, 960x540).
- Run 7 di tangga 0,18 m: menuruni beberapa anak tangga dengan baik, lalu jatuh menabrak anak tangga di depannya (keterbatasan blind).

## 7. Catatan operasional
- Setelah reboot drive Windows harus di-mount ulang: `udisksctl mount -b /dev/nvme0n1p3` (`logs` adalah symlink ke `/media/arya/Windows/UbuntuProject/rl_data/logs`).
- Batas aman VRAM 5 GB: 1024 robot rough memakai sekitar 5,7 GB (tidak dipakai); Run 7 sampai 10 memakai 768 robot.
- Ide lanjutan: lebih banyak seed latih, pelatihan dengan dropout pada height scan, menyelidiki mengapa Run 10 berhenti di lereng curam.
