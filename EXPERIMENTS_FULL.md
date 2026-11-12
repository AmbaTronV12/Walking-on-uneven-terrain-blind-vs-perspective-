# Catatan Eksperimen: Walking on Uneven Terrain

Versi mjlab (commit): 8bb2bc9e187797689ec82c78c35019afd2fd0376
Robot: Unitree Go1 | GPU: RTX 4050 6 GB

## Run 1: Baseline flat (selesai)
- Task: Mjlab-Velocity-Flat-Unitree-Go1
- Robot paralel: 512 | Iterasi: 10.000 | Total steps: 122.880.000
- Folder log: logs/rsl_rl/go1_velocity/2026-10-27_11-27-27
- Durasi: 1 jam 8 menit 34 detik | Kecepatan: sekitar 30.000 steps/detik
- Suhu GPU: 57-60 C | VRAM: sekitar 400 MiB
- Hasil akhir: mean reward 79,20 | episode length 994 | fell_over 0,10
- Pembanding (iterasi sekitar 547): reward 49,79 | fell_over 0,22
- Pengamatan: (diisi setelah menonton robotnya)

## Run 2: Rough terrain (belum dijalankan)

## Pengamatan Run 1 (Go1 flat, model_9999.pt, ditonton di viewer)
- Robot berjalan lancar dan tidak jatuh (pengamatan visual saat play)
- Pengamatan tambahan: -

## Uji coba G1 flat (tes kecil, bukan training penuh)
- Task: Mjlab-Velocity-Flat-Unitree-G1 | Robot paralel: 512
- Steps per second: 23.129 (Go1: sekitar 30.000)
- VRAM: sekitar 500 MiB | Suhu GPU: 56 C
- Menit ke-3 (sekitar iterasi 350): fell_over 9,88 | episode length 55 | reward 0,57 (Go1 menit ke-4: 0,22 | 940 | 49,79). ETA training penuh sekitar 4 jam
- Keputusan: G1 jadi robot utama (final project magang, tenggat sekitar 1 bulan). Go1 jadi pembanding dan cadangan.

## Ukuran jumlah robot G1 flat (tes 2-4 menit)
- 512 : 23.129 steps/s | 0,53 s/iter | VRAM ~500 MiB | GPU 49% | 56 C
- 1024: 37.666 steps/s | 0,65 s/iter | VRAM ~675 MiB | GPU 65% | 60 C
- 2048: 45.381 steps/s | 1,08 s/iter | VRAM ~977 MiB | GPU 83% | 60 C
- Kenaikan: 512 ke 1024 sekitar +63%, 1024 ke 2048 sekitar +20% (mulai mengecil)
- Keputusan sementara flat: 2048 robot (rough tetap 512), jumlah iterasi dibatasi
- Folder log Run 2 (G1 flat): logs/rsl_rl/g1_velocity/2026-10-27_14-18-34 (checkpoint terakhir model_9999.pt)
- Folder lain di g1_velocity: sisa tes ukuran robot, bukan hasil training penuh

## Temuan konfigurasi (dari kode mjlab)
- Reward air_time dimatikan lewat bobot: cfg.rewards["air_time"].weight = 0.0 (G1: config/g1/env_cfgs.py baris 155; Go1: baris 208). track_air_time=True, jadi sensornya aktif tapi tidak dipakai sebagai reward.
- Interval save bawaan task rough G1 = 50. Pengaturan 200 harus ditulis di perintah: --agent.save-interval 200
- Folder log dibedakan lewat --agent.experiment-name (opsi tersedia)
- Kode mjlab tidak diubah (git status hanya menunjukkan folder logs)
- air_time bobot 0,0 berada di dalam unitree_g1_rough_env_cfg (baris 155); fungsi flat mulai baris 188. Belum diubah.
- Opsi resume tersedia: --agent.resume True, --agent.load-run, --agent.load-checkpoint. Experiment-name jangan diganti saat resume dari run flat.
- Rencana: tes 30 iterasi rough dari checkpoint flat (run 2026-10-27_14-18-34, model_9999.pt)

## Tes resume rough dari checkpoint flat (gagal)
- Perintah: train Mjlab-Velocity-Rough-Unitree-G1 --agent.resume True --agent.load-run 2026-10-27_14-18-34 --agent.load-checkpoint model_9999.pt
- Hasil: size mismatch. Actor input checkpoint flat 99, model rough 286 (selisih 187, kemungkinan height_scan).
- Penyebab: konfigurasi flat menghapus sensor terrain_scan dan height_scan dari observasi actor dan critic.
- Temuan: flat diturunkan dari rough (unitree_g1_rough_env_cfg), maka bobot air_time = 0 terwarisi. Task rough bawaan adalah varian perceptive.
- Keputusan: Run 3 rough dilatih dari nol, 512 robot, 10.000 iterasi, save-interval 200 (perkiraan 2 jam 10 menit)
- Ide eksperimen berikutnya: varian blind (hapus height_scan dari rough) untuk perbandingan blind vs perceptive

## K1: XML terverifikasi (27 Okt, 22:00)
- k1.xml valid: joint 23 (22 sendi + 1 joint bebas), aktuator 0, body 26. foot_collision kiri dan kanan ada (baris 142 dan 178). ground dan blok actuator sudah dihapus.
- Catatan: default geom contype=0 conaffinity=0 (telapak tidak bertabrakan kalau tidak diatur dari Python). z awal badan di XML 1,0 vs sekitar 0,55 m perkiraan tinggi berdiri. Timestep XML 0,001.
- Belum dilakukan: k1_constants.py, env_cfgs.py, rl_cfg.py, __init__.py (task), tes berdiri.

## K1: data motor terverifikasi dari K1_22dof.xml (27 Okt, 22:16)
- armature dan forcerange cocok dengan tabel chat sebelumnya (hip_pitch 68, hip_roll 43, hip_yaw 38,3, knee 112, ankle 38,3, lengan 14, kepala 6 N.m).
- Rentang: knee 0 s/d 2,321 (kaki lurus di batas), hip_roll dan elbow_yaw kanan adalah cermin kiri, ankle_pitch -0,87 s/d 0,345.
- Tinggi badan ke telapak kaki lurus sekitar 0,55 m (hitungan dari offset body), XML menaruh badan di 1,0.
- File G1 yang akan dijadikan acuan: unitree_g1/g1_constants.py, tasks/velocity/config/g1/{env_cfgs,rl_cfg,__init__}.py
- Ruang Ubuntu 6,3 GB. booster_assets (365 MB) dipindah ke drive Windows.

## K1: file dibuat (27 Okt, malam)
- Dibuat: asset_zoo/robots/booster_k1/k1_constants.py; tasks/velocity/config/k1/{env_cfgs,rl_cfg,__init__}.py. File G1 tidak diubah.
- XML K1: ditambah site left_foot dan right_foot (di bawah geom foot_collision).
- Keputusan: gain kaki dengan 5 Hz (G1 memakai 10 Hz), gain lengan 20, kepala 10 (nilai awal). Hanya telapak yang bertabrakan, tanpa self-collision. air_time weight 0 seperti G1.
- Task: Mjlab-Velocity-Flat-Booster-K1 (belum diuji). Rough dan tangga belum dibuat.
- Belum diverifikasi: tanda sendi, tinggi awal 0,56, pendaftaran task, sensor imu, timestep.

## K1 vs G1, agen zero (27 Okt, 23:14)
- G1 zero: robot yang terlihat bertahan dalam posisi jongkok (lutut ditekuk).
- K1 zero tanpa reset: 2 dari 4 berdiri tegak, 2 terbalik di lantai. Kestabilan K1 marginal.
- Catatan: K1 hanya telapak kaki yang bertabrakan, jadi robot yang jatuh dapat menembus lantai (dugaan).
- Berikutnya: training pendek 300 iterasi K1 flat 512 robot, bandingkan dengan G1 di iterasi sekitar 350 (reward 0,57; episode length 55; fell_over 9,88).

## Run 3: K1 flat, training pendek (27 Okt, 23:19)
- Task: Mjlab-Velocity-Flat-Booster-K1 | 512 robot | 300 iterasi | 3.686.400 steps | 2 menit 32 detik | 24.687 steps/s
- Hasil iterasi 299: reward 9,45 | episode length 499,8 | fell_over 1,25 | time_out 0,33 | track_lin 0,31 | upright 0,42 | action std 0,71 | action_rate_l2 -0,82
- Pembanding G1 (iterasi sekitar 350): reward 0,57 | episode length 55 | fell_over 9,88 | upright 0,044 | action std 0,50
- Kesimpulan sementara: K1 belajar jauh lebih cepat di awal. Belum tentu hasil akhir lebih baik (G1 matang di 10.000 iterasi). Aksi mungkin masih kasar.
- Catatan: kurikulum kecepatan bawaan naik sampai 2 m/s di G1; K1 nominal sekitar 0,5 m/s (lembar spesifikasi tim RoboCup). Keputusan batas kecepatan ditunda sampai baseline selesai.

## K1 hasil tonton Run 3 (27 Okt, 23:25)
- Policy 300 iterasi: K1 berdiri tegak, tidak ada yang jatuh (upright 0,99). Penalti sekitar nol berarti robot diam. Berjalan belum diuji.
- Pengamatan: lengan terentang ke samping (keyframe hanya mengatur kaki). Reward pose mungkin mengikat lengan ke posisi itu. Keputusan: ukur tanda sendi bahu, turunkan lengan di keyframe sebelum training panjang.
- Run 3 (300 iterasi) hanya dipakai sebagai uji awal dan akan diganti oleh run baru.

## K1 lengan turun terverifikasi (27 Okt, 23:33)
- k1_constants.py baris 100-101: left_shoulder_roll -1,2, right_shoulder_roll +1,2. Viewer (agen zero, 2 robot): lengan menggantung, 2 dari 2 berdiri (sampel kecil).
- Temuan: aksi nol menahan pose keyframe (bukan posisi sendi nol).
- Berikutnya: Run 4 (512 robot, 300 iterasi) sebagai pembanding Run 3, lalu Run 5 (2048 robot, 5000 iterasi, save-interval 200).

## Run 4: K1 flat, lengan turun, 300 iterasi (27 Okt, 23:38)
- 512 robot, 300 iterasi, 2 menit 32 detik, 23.800 steps/s, 0,52 s/iter.
- Iterasi 299: reward 9,42 | episode length 555,0 | fell_over 1,31 | time_out 0,19 | track_lin 0,26 | upright 0,52 | action_rate_l2 -0,97 | action std 0,69
- Run 3 (lengan terentang): reward 9,45 | episode length 499,8 | fell_over 1,25 | upright 0,42. Hasil setara, selisih dalam variasi antar run (satu kali latihan masing-masing).
- Kurikulum kecepatan (velocity_env_cfg.py baris 405-408): tahap 1 lin_vel_x -1..1, ang_vel_z -0,5..0,5; tahap 2 pada step 5000*24: -1,5..2,0 dan +-0,7; tahap 3 pada step 10000*24: -2..3. Training 5000 iterasi hanya melewati tahap 1.
- Berikutnya: Run 5, K1 flat, 2048 robot, 5000 iterasi, save-interval 200.

---

## Run 5: K1 flat, training panjang

| Item | Isi |
|---|---|
| Tanggal / mulai | 2026-10-28, 08:30 WIB |
| Robot / task | Booster K1 / `Mjlab-Velocity-Flat-Booster-K1` |
| Branch | `k1-port` |
| Jumlah robot | 2048 |
| Iterasi | 5000 (save-interval 200) |
| Medan | Datar (tanpa height scan, jadi buta/blind) |
| Tujuan | Baseline K1 jalan stabil di datar sebelum rough/tangga |

### Kecepatan dan beban (awal run)
| Metrik | Nilai |
|---|---|
| Steps/detik | ~75.700 |
| Waktu per iterasi | 0.65 s |
| ETA awal | 0:55 |
| Suhu GPU | 58 °C (naik dari 43 °C) |
| Beban GPU | 55–75% |
| VRAM | 843 MiB (masih sangat longgar) |

### Kondisi awal (iterasi ~50)
- Mean reward -1.01, episode length 51, fell_over 39.
- Curriculum kecepatan sudah di batas penuh (x/y ±1.0, yaw ±0.5).
- Wajar untuk awal; dinilai ulang setelah beberapa ratus iterasi.

### Hasil akhir (isi setelah selesai)
| Metrik | Nilai |
|---|---|
| Durasi total | |
| Mean reward akhir | |
| Mean episode length | |
| fell_over (%) | |
| error_vel_xy / error_vel_yaw | |
| Suhu maks GPU | |
| Folder run | `logs/rsl_rl/k1_velocity/<tanggal_jam>` |
| Checkpoint terakhir | `model_4999.pt` |

### Pengamatan di viewer (isi setelah play)
- Berdiri/jalan stabil? Jatuh saat apa?
- Ikuti perintah kecepatan?

### Catatan / ide berikutnya
- VRAM hanya 843 MiB, coba flat 4096 robot untuk run berikutnya.
- Lanjut: daftarkan task K1 rough dan tangga.

## Run 5: hasil akhir (selesai, 28 Okt 09:27)
Catatan: tabel kosong "Hasil akhir" di atas digantikan bagian ini. Di blok awal tertulis "fell_over 39%", tetapi satuannya belum dipastikan sebagai persen, jadi baca sebagai angka apa adanya.

| Item | Nilai |
|---|---|
| Folder run | logs/rsl_rl/k1_velocity/2026-10-28_08-32-06 |
| Durasi | 0:54:51 (0,64 s/iter, 77.322 steps/s) |
| Total steps | 245.760.000 (5000 iterasi, 2048 robot) |
| Checkpoint | model_0 sampai model_4800 tiap 200, plus model_4999.pt, plus file .onnx |
| Mean reward | 72,97 |
| Mean episode length | 985,01 (maks 1000) |
| fell_over / time_out | 0,1579 / 2,2632 |
| error_vel_xy / error_vel_yaw | 0,5387 / 0,6826 |
| track_linear / track_angular | 1,5119 / 1,3673 |
| upright / pose | 0,9516 / 0,6683 |
| action_rate_l2 / action std | -0,7492 / 0,42 |
| Kurikulum kecepatan | x -1,03..1,05, y +-1,0, yaw +-0,51 (masih tahap 1) |
| Suhu maks GPU | belum dicatat (awal run 58 C) |

- Pembanding Go1 flat (10.000 iterasi): reward 79,20 | episode length 994 | fell_over 0,10. K1 mendekati dengan separuh iterasi. Bobot reward berbeda per robot, jadi hanya gambaran kasar.
- Dugaan: error kecepatan masih besar (0,54) karena K1 nominal sekitar 0,5 m/s atau robot sering diam. Belum diverifikasi, perlu dilihat di viewer.
- Kendala: uv run play dengan --env.scene.num-envs gagal (opsi tidak dikenali di play). Flag jumlah robot untuk play dicari lewat --help.
- Berikutnya: tonton model_4999.pt (apakah melangkah, mulus, mengikuti perintah, jatuh), lalu daftarkan task K1 rough dan tangga.

### Uji jalan manual Run 5 (28 Okt, 09:56)
- Twist diaktifkan, perintah manual lin_vel_x, lin_vel_y, ang_vel_z di viewer (model_4999.pt).
- Hasil (pengamatan Arya): semua stabil, tidak ada yang jatuh.
- Belum dicatat: kecepatan maksimum yang masih stabil, apakah kaki jelas melangkah.
- Keputusan: titik cek 3 Nov terpenuhi (K1 berdiri dan berjalan di datar). K1 tetap robot utama, G1 tidak jadi cadangan.
- Berikutnya: daftarkan task K1 rough (perceptive) dan siapkan varian blind; cek sub-terrain tangga di konfigurasi terrain.

## Uji asap K1 rough (28 Okt, 10:03)
- Task Mjlab-Velocity-Rough-Booster-K1, 512 robot, 20 iterasi: lolos tanpa error. 19.755 steps/s, 0,62 s/iter, ETA 10.000 iterasi sekitar 1 jam 45 menit (perkiraan).
- Iterasi 19: reward -2,51 | fell_over 8,04 | episode length 60,75 (awal, belum bermakna). Level terrain rata-rata 0,13, maks 3.
- Peringatan: timestep parent 0,002 dipakai, bukan 0,001 dari XML K1 (sama seperti G1). MULTICCD: pasangan HFIELD-BOX hanya 1 kontak per pasangan (dampak ke lereng belum diketahui).
- Folder uji 20 iterasi di logs/rsl_rl/k1_velocity bukan hasil training.

## Run 6: K1 rough perceptive
- Mulai: 2026-10-28 10:07 WIB | Task: Mjlab-Velocity-Rough-Booster-K1 | 512 robot | 10.000 iterasi | save-interval 200
- Folder run (terbaru saat dicatat): logs/rsl_rl/k1_velocity/2026-10-28_10-01-36
- Medan: ROUGH_TERRAINS_CFG (tangga 40%, lereng 20%), curriculum terrain aktif | Perceptive (height scan) | dari nol
- Hasil: (diisi setelah selesai)

### Beban Run 6 (28 Okt, 10:09, menit ke-1)
- Kecepatan 0,68 s/iter (sekitar 18.000 steps/s), ETA awal 1:42:34 (selesai sekitar 11:50).
- VRAM 3.099 MiB (flat 2048 robot: 843 MiB; selisih karena height scan) | GPU 47-56% | suhu 60 C dan naik pelan.
- Keputusan: tetap 512 robot (1024 berisiko melewati batas VRAM 5 GB).
- Iterasi awal: terrain_levels 0 semua, fell_over 8,08 (belum bermakna).
- Selagi training: edit varian blind (booster_k1_rough_blind_env_cfg, task Mjlab-Velocity-Rough-Blind-Booster-K1). Aktor tanpa height_scan, kritik tetap. Belum diuji. Backup: ~/Documents/k1_env_cfgs.py.bak dan k1_init_v2.py.bak.

### Hasil akhir Run 6 (28 Okt, 11:52): K1 rough perceptive, BELUM BAGUS
- Durasi 1:40:21 | 122.880.000 steps | 20.955 steps/s | 0,59 s/iter | VRAM 3.099 MiB | suhu maks belum dicatat.
- Iterasi 9999: reward 12,75 | episode length 541,69 | fell_over 1,0 | time_out 0,4286 | error_vel_xy 1,4959 | error_vel_yaw 0,6042 | track_linear 0,1184 | track_angular 0,4883 | upright 0,4636 | pose 0,3035 | action_rate_l2 -0,7596 | action std 0,62.
- Curriculum terrain: level rata-rata 0,0117, maks 2,0 (pyramid_stairs 0,0 | pyramid_stairs_inv 0,0 | hf_pyramid_slope 0,0577 | wave_terrain 0,0385). Curriculum terrain nyaris tidak maju.
- Curriculum kecepatan sudah tahap 2: x -1,5..2,0 | y +-1,0 | yaw +-0,7.
- Dugaan (belum terbukti): tahap 2 dipicu jumlah langkah (iterasi 5000), perintah sampai 2 m/s melebihi kemampuan K1 (nominal sekitar 0,5 m/s), sehingga error naik dan robot gagal naik level terrain. Alternatif: rough memang jauh lebih sulit.
- Berikutnya: jalankan scripts/summarize_run.py untuk melihat kapan reward turun, periksa kode curriculum, lalu tentukan batas kecepatan K1 sebelum Run 7 (blind) agar perbandingan adil.

### Kriteria curriculum terrain dan uji 1024 robot (28 Okt, 12:05)
- terrain_levels_vel (tasks/velocity/mdp/curriculums.py baris 25): naik level jika jarak tempuh > min(0,8 x jarak perintah, ukuran petak/2 = 4 m) dan jarak perintah >= 1 m. Turun jika jarak tempuh < 0,5 x jarak perintah (jatuh cepat tetap dibebani sisa waktu episode).
- Artinya level rata-rata sekitar 0 sejak iterasi 500 = hampir tidak ada robot yang berjalan 4 m dalam satu episode. Penyebab belum diketahui (medan, height scan, atau data kurang).
- Play Run 6 (model_9999, 16 robot, rough): Twist aktif tapi perintah 0 sehingga robot diam; itu belum menjadi bukti masalah. Dugaan ground bawaan: lubang tangga terbalik terlihat jelas di viewer, jadi tidak ada bidang datar yang menutupnya (dicek lewat grep plane/ground/floor di k1.xml dan k1_constants.py).
- Uji 1024 robot gagal: Warp CUDA error 2 out of memory. Saat itu viewer play kemungkinan masih berjalan dan memakai VRAM. Belum disimpulkan; diulang setelah GPU bersih.
- Berikutnya: uji perintah lin_vel_x 0,5 di tiap jenis medan, ulangi uji 1024 dari kondisi bersih.

### Cek ground bawaan K1 (28 Okt, 12:03)
- grep plane|ground|floor di k1.xml dan k1_constants.py: hanya k1.xml baris 11-12 (tekstur dan material bernama "plane", tampilan kotak-kotak). Tidak ada geom lantai, tidak ada hasil di k1_constants.py. Lantai di viewer berasal dari terrain generator.
- Viewer rough dengan perintah penuh (lin_vel 1,0 | ang_vel 0,5): pengamatan menyusul (maju atau tidak, jatuh di medan mana). Disarankan uji ulang pada lin_vel_x 0,5 (nominal K1).

### Kesimpulan Run 6 dan keputusan Run 7 (28 Okt, 12:20)
- Run 6 (rough perceptive dari nol): policy berdiri diam (dikonfirmasi uji viewer dengan dan tanpa Twist). Curriculum terrain macet di level 0.
- Dugaan (belum terbukti): berdiri adalah solusi aman di medan sulit dari nol; kontak telapak-heightfield 1 titik (MULTICCD) mungkin memperburuk.
- Keputusan: Run 7 = rough blind, warm start dari Run 5 (flat model_4999). Varian blind diperbaiki: height_scan dihapus dari aktor dan kritik, sensor terrain_scan dihapus, ukuran input sama dengan flat (99) sehingga resume mungkin dilakukan.
- Resume mereset penghitung langkah, kurikulum kecepatan kembali ke tahap 1 (+-1 m/s) selama 5000 iterasi pertama; Run 7 dibatasi sekitar 5000 iterasi.
- Perceptive vs blind: perceptive dari nol gagal; dibahas lagi setelah blind berhasil.
- Backup: ~/Documents/k1_env_cfgs_v3.py.bak dan k1_init_v3.py.bak.

### Uji asap rough blind 1024 robot dengan kurikulum terkunci (28 Okt, 12:25)
- Lolos 20 iterasi: 32.906 steps/s | 0,75 s/iter | suhu maks 56 C | VRAM puncak 5.691 MiB dari 6.141 MiB (93%).
- lin_vel_x -1,0..1,0 dan yaw +-0,5: kunci tahap 1 berfungsi. Level terrain rata-rata 2,31 | reward 15,30 | episode length 265 | time_out 0,62.
- Keputusan: Run 7 memakai 768 robot (1024 melewati batas aman VRAM 5 GB; keuntungan kecepatan hanya sekitar 12%).

## Run 7: K1 rough blind, warm start dari Run 5
- Mulai: 2026-10-28 12:22 WIB | Task: Mjlab-Velocity-Rough-Blind-Booster-K1 | 768 robot | 5000 iterasi (nomor sekitar 5000 sampai 10.000) | save-interval 200
- Resume dari: k1_velocity/2026-10-28_08-32-06 model_4999.pt | Folder run: logs/rsl_rl/k1_velocity/2026-10-28_12-20-23
- Medan: ROUGH_TERRAINS_CFG (tangga 40%, lereng 20%), curriculum terrain | Blind (tanpa height scan) | kecepatan terkunci tahap 1 (x +-1,0, yaw +-0,5)
- Hasil: (diisi setelah selesai)

### Hasil akhir Run 7 (28 Okt, 13:21): K1 rough blind, warm start dari Run 5, BERHASIL
- Durasi 0:52:28 | 92.160.000 steps | 28.628 steps/s | 0,64 s/iter | 768 robot | VRAM dan suhu maks belum dicatat.
- Iterasi 9998: reward 29,34 | episode length 881,12 | fell_over 0,3333 | time_out 1,2667 | error_vel_xy 0,9038 | error_vel_yaw 1,1812 | track_linear 0,9600 | track_angular 0,8007 | upright 0,8611 | pose 0,3996 | action_rate_l2 -1,4742 | foot_clearance -0,1339 | action std 0,62.
- Curriculum terrain: rata-rata 4,59, maks 9 | flat 5,67 | pyramid_stairs 5,73 | pyramid_stairs_inv 4,39 | hf_pyramid_slope 5,00 | hf_pyramid_slope_inv 0,91 | random_rough 4,15 | wave 4,30.
- Kecepatan terkunci tahap 1 (x +-1,0, yaw +-0,5) sepanjang run.
- Pembanding Run 6 (perceptive dari nol): reward 12,75 | episode length 541 | level terrain 0,01. Warm start dari policy flat menyelesaikan masalah berdiri diam.
- Catatan lemah: hf_pyramid_slope_inv hanya 0,91 (dugaan: cekungan sulit bagi policy blind, belum diverifikasi); tracking lebih buruk dari Run 5; gerakan menyentak (action_rate_l2 -1,47) dan kaki kurang terangkat (foot_clearance -0,13).
- Belum diverifikasi: tinggi anak tangga pada level 5,7 (dugaan linear 0 sampai 0,1 m).
- Berikutnya: lihat kurva dengan summarize_run.py, tonton policy di viewer (tangga, cekungan, jatuh di mana), lalu Run 8 di STAIRS_TERRAINS_CFG dari checkpoint Run 7; perceptive lewat penambahan kolom nol ke bobot Run 7 (belum dicoba).

### Review Run 7: kurva dan viewer (28 Okt, 17:45)
- Folder Run 7: logs/rsl_rl/k1_velocity/2026-10-28_12-23-06 | checkpoint terakhir model_9998.pt (resume dimulai dari iterasi 4999).
- Kurva: reward puncak 39,29 (iter 5249), turun ke 26-29 dan datar sejak sekitar iter 7000 (level terrain naik dari 3,8 ke 4,6-4,9, jadi medan makin sulit). Episode length 850-910 di akhir. Level terrain dan reward mendatar sejak sekitar iter 7000; menambah iterasi di setup yang sama kemungkinan kecil membantu (dugaan). error_vel_xy sekitar 0,8-1,0, tidak membaik.
- Viewer (16 robot, pengamatan Arya): hampir tidak ada yang jatuh. Langkah di tangga sering tersandung. Jatuh hanya di petak terrain paling kasar; bidang lain tidak pernah terlihat jatuh. Panel reward: foot_clearance -0,15 sampai -0,18 dan action_rate_l2 sampai -0,66 (penalti terbesar).
- Interpretasi: tersandung di tangga wajar untuk policy blind (tidak tahu tepi anak tangga); kaki kurang terangkat.
- Pembaruan hipotesis: Run 7 sukses di heightfield (lereng 5,0 | gelombang 4,3 | rough acak 4,2), sehingga peringatan MULTICCD (HFIELD-BOX 1 kontak) tampaknya bukan penyebab utama kegagalan Run 6; penyebab lebih mungkin berdiri diam dari nol.
- Cekungan (slope_inv) level 0,9 tapi robot tidak terlihat jatuh: kemungkinan tidak naik level karena keluar dari cekungan butuh mendaki (belum diverifikasi).
- Rencana: Run 8 = blind di STAIRS_TERRAINS_CFG (warm start Run 7, model_9998). Run 9 = perceptive di terrain yang sama, bobot Run 7 diperluas 187 input height scan (kolom nol), iterasi sama, untuk perbandingan blind vs perceptive. Backup: ~/Documents/k1_env_cfgs_v5.py.bak dan k1_init_v5.py.bak.

### Uji asap stairs blind (28 Okt, 17:50)
- Task Mjlab-Velocity-Stairs-Blind-Booster-K1 (STAIRS_TERRAINS_CFG, blind, kurikulum kecepatan terkunci), 768 robot, 20 iterasi, resume dari Run 7 (k1_velocity/2026-10-28_12-23-06, model_9998.pt). Lolos, tanpa error. list-envs menampilkan 4 task K1 (Flat, Rough, Rough-Blind, Stairs-Blind).
- Iterasi 10017: reward 16,60 | episode length 410,90 | fell_over 0,1667 | time_out 1,0 | error_vel_xy 0,3600 | error_vel_yaw 0,5710. Level terrain rata-rata 2,60, maks 6 (flat 2,53 | easy 2,67 | moderate 2,45 | challenging 2,84). lin_vel_x tetap -1,0..1,0.
- Catatan: kecepatan hanya 14.754 steps/s dan 1,25 s/iter (uji 768 sebelumnya sekitar 29.000 dan 0,63). Penyebab belum diketahui (dugaan: charger atau proses lain di GPU).

## Run 8: K1 stairs blind, warm start dari Run 7
- Mulai: 2026-10-28 18:53 WIB | Task: Mjlab-Velocity-Stairs-Blind-Booster-K1 | 768 robot | 5000 iterasi (nomor sekitar 10.000 sampai 15.000) | save-interval 200
- Resume dari: k1_velocity/2026-10-28_12-23-06 model_9998.pt | Folder run: logs/rsl_rl/k1_velocity/2026-10-28_17-53-58
- Medan: STAIRS_TERRAINS_CFG (flat 0,25 | easy 0,35 | moderate 0,25 | challenging 0,15), curriculum terrain | Blind | kecepatan terkunci tahap 1
- Hasil: (diisi setelah selesai)

### Hasil akhir Run 8 (28 Okt, 18:54): K1 stairs blind, warm start dari Run 7
- Durasi 0:48:29 | 92.160.000 steps | 31.645 steps/s | 0,58 s/iter | 768 robot | VRAM dan suhu maks belum dicatat.
- Folder run (terbaru saat dicatat, harus berjam sekitar 17:5x): logs/rsl_rl/k1_velocity/2026-10-28_17-53-58
- Iterasi 14997: reward 48,25 | episode length 989,54 | fell_over 0,0 | time_out 1,4286 | error_vel_xy 0,6741 | error_vel_yaw 1,0009 | track_linear 1,4161 | track_angular 1,1193 | upright 0,9868 | pose 0,5706 | action_rate_l2 -1,3154 | foot_clearance -0,1269 | action std 0,55.
- Curriculum terrain: rata-rata 6,06, maks 9 (flat 6,05 | easy 6,15 | moderate 5,97 | challenging 6,05). Kecepatan tetap terkunci tahap 1.
- Perbandingan dengan Run 7 (rough, blind) tidak langsung: terrain Run 8 hanya datar dan tangga kotak.
- Belum diverifikasi: tinggi anak tangga pada level 6 (dugaan linear: challenging sekitar 0,09 m, moderate sekitar 0,07 m, easy sekitar 0,04 m). Dicek lewat kode terrain_generator (difficulty).
- Kecepatan kembali normal setelah uji asap yang lambat (penyebab belum diketahui).
- Berikutnya: tonton di viewer, periksa pemetaan level, Run 9 = perceptive di terrain yang sama dengan bobot Run 7 diperluas input height scan.

### Viewer Run 8 dan temuan struktur (28 Okt, 19:05)
- Viewer Run 8 (stairs blind, pengamatan Arya): naik tangga dengan pola langkah-susul (satu kaki naik, kaki lain menyusul ke anak tangga yang sama, baru lanjut). Tersandung berkurang dibanding Run 7. Tidak ada yang jatuh.
- terrain_generator.py baris 254-258: difficulty = lower + (upper - lower) * t, difficulty_range bawaan (0,0 sampai 1,0). Definisi t dan pemakaian difficulty di fungsi tangga belum dicek; tinggi anak tangga per level masih dugaan.
- Checkpoint rsl_rl: kunci actor_state_dict, critic_state_dict, optimizer_state_dict, iter, infos (bukan model_state_dict).
- velocity_env_cfg.py: actor_terms berisi height_scan (baris 105, terrain_scan). critic_terms = {**actor_terms, ...} lalu height_scan ditimpa dengan sensor foot_height_scan (baris 117-124). Dugaan: perluasan bobot untuk perceptive butuh dua lebar kolom baru (aktor 187, kritik lebih kecil), belum dikonfirmasi dari ukuran bobot.
- Berikutnya: konfirmasi ukuran bobot dan urutan term, lalu script perluasan bobot untuk Run 9 (perceptive di STAIRS_TERRAINS_CFG).

### Pemetaan level ke tinggi tangga dan struktur bobot (28 Okt, 19:15)
- terrain_generator.py: t = baris / max(num_rows-1, 1); difficulty = lower + (upper-lower)*t (difficulty_range bawaan 0,0..1,0). primitive_terrains.py: step_height = step_height_range[0] + difficulty*(step_height_range[1]-step_height_range[0]). Dengan 10 baris, level L berarti difficulty L/9.
- Perkiraan tinggi anak tangga dari level rata-rata (bukan tinggi maksimum satu robot): Run 8 easy (6,15) 4,1 cm | moderate (5,97) 7,0 cm | challenging (6,05) 9,3 cm. Run 7 pyramid_stairs (5,73) 6,4 cm | pyramid_stairs_inv (4,39) 4,9 cm. Level maksimum 9: 5, 8, 10 cm.
- Ukuran input Run 7 (blind): aktor 78, kritik 90 (aktor: 3+3+3+22+22+22+3; kritik tambah foot_height 2, foot_air_time 2, foot_contact 2, foot_contact_forces 6).
- Koreksi: kritik memakai terrain_scan (187 titik, tanpa noise) untuk height_scan, bukan foot_height_scan. Pada versi perceptive: aktor 265 (187 kolom di akhir), kritik 277 (187 kolom disisipkan di indeks 78, sebelum 12 term kaki).
- Run 8 (viewer): langkah-susul di tangga; tersandung berkurang; tidak ada yang jatuh.
- Rencana Run 9: task Mjlab-Velocity-Stairs-Perceptive-Booster-K1; bobot Run 7 diperluas lewat scripts/expand_to_perceptive.py (kolom baru nol, normalizer mean 0 dan var 1, state optimizer diperluas) ke folder logs/rsl_rl/k1_velocity/2026-10-28_19-30-00_perceptive-init. Pengaturan sama dengan Run 8 (768 robot, 5000 iterasi, terrain sama, titik awal Run 7 model_9998) untuk perbandingan blind vs perceptive.
- Backup: ~/Documents/k1_env_cfgs_v6.py.bak dan k1_init_v6.py.bak.

### Uji asap stairs perceptive dengan bobot diperluas (28 Okt, 19:11)
- Script scripts/expand_to_perceptive.py: aktor (512, 78) menjadi (512, 265), kritik (512, 90) menjadi (512, 277), 4 tensor optimizer diperluas. Hasil di logs/rsl_rl/k1_velocity/2026-10-28_19-30-00_perceptive-init/model_9998.pt (checkpoint Run 7 tidak diubah).
- Uji 20 iterasi (768 robot, resume dari folder tersebut): lolos, tanpa size mismatch. 30.765 steps/s | 0,60 s/iter. Iterasi 10017: reward 17,04 | episode length 427,70 | fell_over 0,2222 | time_out 1,1667 | level terrain 2,60 | error_vel_xy 0,3665. Hampir sama dengan uji asap Run 8 (16,60 | 410,90 | 0,1667 | 2,60), sesuai harapan karena bobot baru nol.
- Batasan: uji ini hanya membuktikan perluasan tidak merusak policy, bukan bahwa height scan akan dipakai. Risiko: normalizer untuk 187 input baru beradaptasi lambat (mean 0, var 1, hitungan sampel lama besar).

## Run 9: K1 stairs perceptive, warm start dari Run 7 (bobot diperluas)
- Mulai: 2026-10-28 19:12 WIB | Task: Mjlab-Velocity-Stairs-Perceptive-Booster-K1 | 768 robot | 5000 iterasi (nomor sekitar 10.000 sampai 15.000) | save-interval 200
- Resume dari: k1_velocity/2026-10-28_19-30-00_perceptive-init model_9998.pt | Folder run: logs/rsl_rl/k1_velocity/2026-10-28_19-10-58
- Medan: STAIRS_TERRAINS_CFG (sama dengan Run 8), curriculum terrain | Perceptive (height scan 187 titik) | kecepatan terkunci tahap 1
- Pembanding: Run 8 (blind, pengaturan identik). Hasil: (diisi setelah selesai)

### Hasil akhir Run 9 (28 Okt, 20:05): K1 stairs perceptive vs Run 8 blind
- Durasi 0:50:01 | 92.160.000 steps | 31.406 steps/s | 0,59 s/iter | 768 robot | VRAM dan suhu maks belum dicatat | folder (terbaru saat dicatat, harus berjam sekitar 19:1x): logs/rsl_rl/k1_velocity/2026-10-28_19-13-03
- Iterasi 14997 (Run 9): reward 59,20 | episode length 1000,00 | fell_over 0,0 | time_out 1,6364 | error_vel_xy 0,6787 | error_vel_yaw 0,8265 | track_linear 1,4240 | track_angular 1,2678 | upright 0,9872 | pose 0,6110 | action_rate_l2 -1,0440 | foot_clearance -0,1189 | action std 0,49.
- Level terrain Run 9: rata-rata 6,03, maks 9 (flat 5,91 | easy 6,18 | moderate 5,97 | challenging 5,97).
- Pembanding Run 8 (blind, iterasi 14997): reward 48,25 | episode length 989,54 | fell_over 0,0 | level 6,06 | track_angular 1,12 | error_vel_yaw 1,00 | action_rate_l2 -1,32 | action std 0,55.
- Interpretasi: perceptive lebih tinggi di reward (+11), tracking sudut, dan kehalusan gerak; level terrain dan fell_over sama. Batasan: satu run per varian, satu snapshot iterasi akhir, variasi antar seed belum diketahui; selisih bisa sebagian berasal dari action std lebih kecil. Belum cukup untuk klaim bahwa height scan dipakai untuk melewati tangga.
- Berikutnya: evaluasi terkontrol (tinggi tangga tetap, perintah tetap, banyak percobaan, termasuk tinggi di luar rentang latihan) untuk membandingkan Run 7, Run 8, Run 9; rekam video demo (termasuk kegagalan).

### Viewer Run 9 dan peta folder (28 Okt, 20:30)
- Viewer Run 9 (stairs perceptive, pengamatan Arya): jarang tersandung; langkah bergantian kiri-kanan (bukan langkah-susul seperti Run 8); robot terlihat lebih goyang karena gaya bergantian.
- Angka training tidak menunjukkan ketidakstabilan lebih besar: body_ang_vel Run 9 -0,0080 vs Run 8 -0,0102; upright sama 0,987; fell_over 0 di keduanya. Kesan goyang masih visual, perlu diukur di evaluasi.
- Perubahan gaya langkah sejalan dengan pemakaian height scan, tetapi belum bukti (bisa juga karena iterasi tambahan).
- Folder (dari urutan mtime dan jam mulai, dikonfirmasi dengan summarize_run): Run 7 = k1_velocity/2026-10-28_12-23-06 | Run 8 = 2026-10-28_17-53-58 | Run 9 = 2026-10-28_19-13-03. Uji asap: 17-49-07 (stairs blind) dan 19-10-58 (stairs perceptive). Hasil perluasan bobot: 2026-10-28_19-30-00_perceptive-init.
- Berikutnya: bandingkan kurva Run 8 vs 9; script evaluasi terkontrol (butuh struktur scripts/play.py); rekam video demo.

### Perbandingan kurva Run 8 vs Run 9 (28 Okt, 20:40)
- Folder terkonfirmasi (kedua tabel summarize_run mulai iter 9998, selesai 14997): Run 8 = 2026-10-28_17-53-58, Run 9 = 2026-10-28_19-13-03.
- mean_reward: Run 9 lebih tinggi hampir di setiap titik; selisih muncul sejak iter 10248 (44,56 vs 41,69) dan melebar sampai akhir (59,20 vs 48,25).
- terrain_levels/mean: datar ~6,0 di kedua run (tidak naik); perbedaan ada pada kualitas jalan di level yang sama, bukan level yang dicapai.
- mean_episode_length mendekati 1000 di kedua run.
- fell_over (satuan belum dipastikan): TIDAK nol sepanjang training. Run 8 maks 0,25 (iter 10498) dan 0,23 (iter 10748); Run 9 maks 0,15. Koreksi: catatan sebelumnya "fell_over 0 di keduanya" hanya berlaku untuk nilai akhir.
- error_vel_xy akhir hampir sama (0,67 vs 0,68), jadi klaim yaw tracking lebih baik pada Run 9 tidak dipakai.
- Batasan: satu run per varian, belum ada seed lain; selisih reward = indikasi, bukan bukti.
- Opsi play yang tersedia: --video, --video-length (default 200), --video-height/width, --num-envs, --no-terminations. Opsi pemilihan checkpoint belum dicek.

### Perekaman video percobaan (28 Okt, 21:10)
- Mekanisme: play.py memakai VideoRecorder dengan step_trigger step==0, jadi hanya satu klip (video_length langkah) per sekali jalan, disimpan di <folder checkpoint>/videos/play/rl-video-step-0.mp4. Viewer tidak keluar sendiri; video selesai ditulis setelah video_length langkah.
- Perintah: uv run play Mjlab-Velocity-Stairs-Perceptive-Booster-K1 --checkpoint-file logs/rsl_rl/k1_velocity/2026-10-28_19-13-03/model_14997.pt --num-envs 5 --video True --video-length 400
- Hasil: klip percobaan Run 9, 1,2 MB, disalin ke ~/projects/terrain-walker/videos/run9_stairs-perceptive_trial400.mp4. Ini klip uji perekaman, bukan demo final.
- Catatan: peringatan solver "linesearch iterations limit reached (ls_iterations 20)" muncul berulang di tangga; sudah dicatat sebagai batasan simulasi, konfigurasi tidak diubah agar sama dengan kondisi training.
- Berikutnya: script evaluasi terkontrol (butuh isi step() dan velocity_command), lalu video demo termasuk kegagalan.

### Koreksi satuan fell_over dan script evaluasi (28 Okt, 21:30)
- Dari termination_manager.reset(): Episode_Termination/<nama> = count_nonzero (JUMLAH env yang berakhir karena sebab itu pada satu reset), bukan persen; logger lalu merata-ratakannya. Angka 0,25 = rata-rata ~0,25 env per kejadian reset. Cukup untuk membandingkan run, bukan tingkat jatuh sebenarnya.
- step() mengembalikan reset_terminated (jatuh) terpisah dari reset_time_outs (selesai normal).
- Perintah kecepatan: term "twist" (UniformVelocityCommand). Evaluasi membekukan ranges (lin_vel_x tetap, y=0, yaw=0), heading_command=False, rel_*_envs=0, dan mengosongkan curriculum agar command_vel tidak menimpa.
- Dibuat scripts/eval_policy.py (tanpa viewer): per episode dicatat fell, length, distance, sway (norma ang_vel roll/pitch rata-rata), vel_err; CSV ke ~/projects/terrain-walker/eval/. Belum diuji; langkah berikut: smoke test 4 env x 1 episode.
- Belum ada: tinggi anak tangga tetap (butuh STAIRS_TERRAINS_CFG).

### Temuan: mode play tidak punya batas episode (28 Okt, 21:35)
- Smoke test eval_policy: max_steps terhitung 50000000005 karena load_env_cfg(task, play=True) mengatur episode_length_s sangat besar (agar viewer tidak reset). Akibatnya tidak ada time-out, episode hanya berakhir bila jatuh.
- Perbaikan di scripts/eval_policy.py: argumen --episode-s (default 20.0 = 1000 langkah, sama dengan training) dan env_cfg.episode_length_s = a.episode_s.
- Kecepatan: 4 env, ~800 langkah per sekitar 1 menit (Stairs-Perceptive, GPU RTX 4050).
- Implikasi viewer: di play, robot yang tidak jatuh tidak pernah di-reset oleh waktu.

### Smoke test eval_policy berhasil (28 Okt, 21:35)
- Run 9 (Stairs-Perceptive, model_14997), 4 env x 1 episode, perintah 0,5 m/s tetap, episode 20 s (1000 langkah): falls 0/4, mean_distance 8,57 m (progress 0,86 dari 10 m), sway 0,138, vel_err 0,123. CSV: ~/projects/terrain-walker/eval/smoke_run9_speed0.5_seed0.csv.
- Hanya validasi script (4 episode), belum hasil untuk laporan.
- Rencana eval penuh: 32 env x 3 episode, seed 0, medan tangga yang sama untuk semua. Run 7 (Rough-Blind, model_9998) dan Run 8 (model_14997) diputar di task Stairs-Blind (obs 78 sama); Run 9 di Stairs-Perceptive.
- Batasan: tinggi tangga belum tetap (grid bawaan mode play); sweep tinggi menunggu STAIRS_TERRAINS_CFG.

### Evaluasi terkontrol pertama, seed 0, 0,5 m/s (28 Okt, 21:45)
- Setup: Stairs grid bawaan mode play (5x5, tanpa kurikulum), 32 env x 3 episode = 96 episode/run, episode 20 s, perintah maju 0,5 m/s tetap. Run 7 dan 8 di task Stairs-Blind, Run 9 di Stairs-Perceptive.
- Hasil (n=96): jatuh 0/96 di semua run. Jarak: R7 8,64 m, R8 8,61 m, R9 8,69 m (progress 0,86/0,86/0,87). sway: R7 0,187, R8 0,177, R9 0,128. vel_err: R7 0,130, R8 0,139, R9 0,112.
- Interpretasi: uji terlalu mudah untuk membedakan (floor effect, tidak ada jatuh); Run 7 yang tidak dilatih tangga setara Run 8. Selisih nyata hanya di sway dan vel_err (Run 9 terendah, sekitar 30% lebih kecil sway). Kesan visual "Run 9 kurang stabil" tidak didukung metrik roll/pitch; sway tidak mengukur goyangan yaw.
- Batasan: satu seed; 3 episode per env berbagi medan sehingga tidak independen; tinggi tangga tidak tetap. Belum disebut terbukti.
- Berikutnya: kecepatan 0,8 m/s, seed 1, tabel dengan galat baku antar env, lalu sweep tinggi tangga (butuh STAIRS_TERRAINS_CFG).

### Evaluasi: seed 1 dan kecepatan 0,8 m/s (28 Okt, 22:00)
- Tabel per env (mean±SE antar 32 env), n=96 episode/run. 0,5 m/s seed0/seed1: sway R7 0,187/0,199, R8 0,177/0,175, R9 0,128/0,137 (SE 0,002-0,005); vel_err R7 0,130/0,141, R8 0,139/0,132, R9 0,112/0,119; jatuh 0 semua. Run 9 paling halus di kedua seed; selisih sway jauh di atas SE, selisih vel_err ke Run 8 tipis.
- 0,8 m/s seed0: jatuh R7 1,0% (1/96), R8 2,1% (2/96), R9 9,4% (9/96); jarak R7 13,68, R8 13,65, R9 14,16 m; sway 0,210/0,199/0,184; vel_err 0,145/0,151/0,134.
- Interpretasi sementara: Run 9 mengikuti perintah lebih dekat dan lebih halus pada kecepatan nominal tetapi lebih sering jatuh pada kecepatan tinggi (sejalan dengan kesan viewer "kurang stabil"). Baru satu seed pada 0,8 m/s dan jumlah jatuh kecil; belum terbukti.
- STAIRS_TERRAINS_CFG: size 8x8, num_rows 10, num_cols 4, curriculum True; flat 0,25; easy_stairs 0,02-0,05 (lebar 0,40); moderate 0,05-0,08 (0,35); challenging 0,08-0,10 (0,30). Tinggi maksimum training 0,10 m, jadi evaluasi default tidak pernah melewati batas training.
- Berikutnya: seed 1 pada 0,8; analisis episode yang jatuh; opsi --stair-height; sweep tinggi 0,10/0,12/0,15/0,20 m.
- Pertanyaan terbuka: apakah robot naik atau turun tangga di medan play (arah awal acak).

### Seed 1 pada 0,8 m/s dan dugaan artefak tepi medan (28 Okt, 22:10)
- 0,8 m/s seed1: jatuh R7 3/96 (3,1%), R8 0/96, R9 15/96 (15,6%). Gabungan 2 seed (192 ep): R7 4 (2,1%), R8 2 (1,0%), R9 24 (12,5%). Sway seed1 R7 0,181, R8 0,185, R9 0,167; vel_err 0,121/0,140/0,114; jarak 13,87/14,30/14,37 m. Run 9 tetap sway dan vel_err terendah di kedua seed.
- Pola: episode yang jatuh berakhir di langkah 888-1000 dari 1000 (seed0: R7 939; R8 984, 961; R9 931, 946, 949, 950, 930, 888, 944, 991, 1000), jarak sekitar 13,5-16 m. Waktu jatuh menumpuk di akhir, bukan tersebar.
- Dugaan (belum diuji): robot yang lahir di tile terluar berjalan keluar tepi medan (grid 5x5 tile 8 m + border 10 m; tepi sekitar 30 m dari tengah, tile terluar sekitar 16 m dari tengah, 16+14=30). Pada 0,5 m/s jarak maks 10 m sehingga tidak tercapai (0 jatuh). Run 9 menempuh jarak terjauh sehingga paling sering sampai tepi. Jika benar, selisih jatuh Run 9 lebih artefak evaluasi daripada kelemahan policy.
- Arah jalan robot di medan play acak (pengamatan Arya): ada yang naik, turun, menyamping, serong, atau menghadap berbalik; evaluasi adalah campuran, bukan tangga lurus. Wajib ditulis di bagian metode laporan.
- Uji fixed stair height 0,12 m berhasil jalan (smoke, Run 9, 4 env x 1 ep): 0 jatuh, sway 0,207, vel_err 0,159, progress 0,85.
- Berikutnya: script mencatat start/end x,y per episode; ulangi 0,8 m/s seed 0 dan 1 (CSV lama disimpan di eval/v1/); periksa koordinat akhir episode yang jatuh.

### Jatuh pada 0,8 m/s adalah artefak tepi medan (28 Okt, 22:05)
- Script kini mencatat start/end x,y. Run 9 pada 0,8 m/s (ulangan): seed0 10 jatuh, seed1 13 jatuh; SEMUA berakhir di |x| atau |y| sekitar 30 m (29,8-30,3) = tepi medan (grid 5x5 tile 8 m + border 10 m). Konfirmasi Arya: robot keluar medan bila lurus terlalu lama atau episode panjang.
- Ditarik kembali: klaim "Run 9 lebih sering jatuh pada 0,8 m/s" dan "Run 9 menempuh jarak terjauh" (jarak 0,8 m/s dibatasi geometri medan). Hasil 0,5 m/s (jarak maks 10 m, tidak sampai tepi) tidak terpengaruh.
- Hasil antar-ulang tidak identik walau seed sama (jatuh 0,8 m/s: R7 1,3 -> 4,8; R8 2,0 -> 1,2; R9 9,15 -> 10,13): ada noise antar-ulang (diduga GPU tidak deterministik). Catat di batasan laporan.
- Aturan evaluasi berikutnya: jarak perintah maksimum sekitar 12 m (--episode-s = 12/kecepatan). Ulangan 0,8 m/s memakai --episode-s 14 ke eval_ep14/. CSV putaran sebelumnya ada di eval/ dan eval/v1/.
- Pemeriksaan jatuh R7/R8 di tepi: tabel edge/real dari CSV 0,8 m/s (belum dilihat).

### Penyapuan tinggi tangga tetap, 0,5 m/s, seed 0 (29 Okt, 22:30)
- Setup: --stair-height H (tipe challenging_stairs, lebar anak tangga 0,30 m, platform tengah 2 m), 32 env x 3 episode = 96 ep/run, episode 20 s, arah lahir acak. Urutan run dalam output dari urutan perulangan (R7, R8, R9); label diverifikasi dari nama file CSV di eval_h/.
- Jatuh (%) / sway / jarak (m): 0,10 m: R7 10,4/0,297/7,64; R8 0,0/0,255/7,46; R9 1,0/0,214/8,26. 0,12 m: R7 22,9/0,358/6,79; R8 3,1/0,271/7,53; R9 4,2/0,242/8,02. 0,15 m: R7 53,1/0,428/6,23; R8 8,3/0,308/7,05; R9 10,4/0,287/7,21. 0,18 m: R7 61,5/0,448/5,89; R8 22,9/0,366/6,65; R9 55,2/0,381/5,80.
- vel_err: 0,10 m R7 0,204, R8 0,229, R9 0,172; 0,12 m 0,234/0,227/0,195; 0,15 m 0,249/0,244/0,235; 0,18 m 0,274/0,266/0,273.
- Interpretasi: latihan di tangga (R8, R9) jauh lebih tahan daripada R7 di semua tinggi. R8 vs R9 bersaing di 0,10-0,15 m (R9 lebih halus dan lebih jauh, jatuh sama atau sedikit lebih banyak; selisih 1-2 jatuh belum bisa dibedakan). Pada 0,18 m (jauh di atas batas training 0,10 m) R9 jatuh 55,2% vs R8 22,9%.
- Hipotesis belum diuji: policy perceptive lebih rapuh di luar rentang height scan yang pernah dilihat; blind menurun lebih landai. Bisa juga penyebab lain (tinggi 0,18 m mendekati ukuran kaki K1).
- Batasan: satu seed, 3 ep/env tidak independen, arah acak (campuran naik/turun/menyamping). Tidak ada risiko artefak tepi (jarak maks 10 m).
- Berikutnya: ulangi 0,15 dan 0,18 m dengan seed 1 (R8 dan R9).

### Penyapuan tinggi tangga, seed 1 (29 Okt, 22:25)
- Run 8 / Run 9, 0,5 m/s, 96 ep per sel (urutan dari perulangan: R8 lalu R9 per tinggi). 0,15 m: R8 8 jatuh (8,3%), jarak 6,86, sway 0,316, vel_err 0,265; R9 10 (10,4%), 7,30, 0,286, 0,223. 0,18 m: R8 12 (12,5%), 6,99, 0,341, 0,262; R9 51 (53,1%), 6,01, 0,372, 0,269.
- Gabungan 2 seed (192 ep): 0,15 m: R8 16 (8,3%), R9 20 (10,4%). 0,18 m: R8 34 (17,7%), R9 104 (54,2%).
- Kesimpulan: kerapuhan R9 pada 0,18 m konsisten antar seed; pada 0,15 m keduanya mirip. Hipotesis (height scan di luar rentang training) belum diuji.
- Keputusan: evaluasi dianggap cukup; lanjut ke video demo, laporan, README, GitHub. Opsional Run 10 (perceptive pada tangga lebih tinggi) bila waktu sisa.

### Koreksi keputusan (29 Okt, 22:35)
- "Evaluasi cukup" hanya berlaku untuk tangga. Deliverable mencakup policy yang berjalan di medan kasar dan lereng; bukti selain tangga baru visual, belum angka.
- Rencana: evaluasi per jenis medan (konfigurasi medan kasar) untuk Run 7, 8, 9 (Run 7/8 di task Rough-Blind, Run 9 di task Rough perceptive), mencari jenis medan yang jatuh atau tidak stabil. Lalu video demo (termasuk kegagalan), laporan, README, GitHub. Run 10 opsional.
- Dibutuhkan: isi konfigurasi medan kasar untuk opsi --terrain-type di eval_policy.py.

### Konfigurasi medan dan rencana uji per jenis medan (29 Okt, 22:50)
- ROUGH_TERRAINS_CFG (training Run 7): flat 0,2; pyramid_stairs 0,2 (0-0,10 m); pyramid_stairs_inv 0,2 (0-0,10 m); hf_pyramid_slope 0,1 (slope_range 0-1,0); hf_pyramid_slope_inv 0,1; random_rough 0,1 (noise 0,02-0,10); wave_terrain 0,1 (amplitudo 0-0,2). Grid 10 baris x 20 kolom, tile 8 m, border 20 m.
- STAIRS_TERRAINS_CFG (training Run 8 dan 9): flat 0,25 + tiga tingkat pyramid_stairs. Tidak ada lereng, random_rough, wave, atau tangga terbalik.
- Run 8 dan 9 dilatih lanjut dari bobot Run 7 hanya di medan tangga: risiko melupakan kemampuan di medan lain (belum diuji). Keunggulan Run 8/9 pada tangga tidak boleh digeneralisasi ke "medan kasar dan lereng".
- Preset lain tersedia tetapi tidak dipakai di training: discrete_obstacles, perlin_noise, box_random_grid, random_spread_boxes, open_stairs, random_stairs, stepping_stones, narrow_beams, nested_rings, tilted_grid.
- eval_policy.py ditambah --terrain-type dan --level. Rencana: 7 jenis medan x 3 run, 0,5 m/s, seed 0 (Run 7/8 di task Rough-Blind, Run 9 di task Rough perceptive); hasil ke eval_t/.

### Evaluasi per jenis medan, 0,5 m/s, seed 0, rentang kesulitan penuh (29 Okt, 23:10)
- Setup: --terrain-type, 32 env x 3 ep = 96 ep/sel, 20 s. Run 7/8 di task Rough-Blind, Run 9 di Rough perceptive. Jatuh di tepi medan = 0 di semua sel.
- Jatuh / jarak(m) / sway. flat: R7 0/9,41/0,126; R8 0/9,62/0,130; R9 0/8,65/0,104. hf_pyramid_slope: R7 26/6,73/0,297; R8 35/6,29/0,351; R9 33/6,40/0,258. hf_pyramid_slope_inv: R7 32/3,89/0,263; R8 17/3,05/0,207; R9 30/2,56/0,240. pyramid_stairs: R7 1/8,75/0,176; R8 0/8,78/0,174; R9 0/8,69/0,138. pyramid_stairs_inv: R7 0/7,43/0,195; R8 0/6,08/0,192; R9 0/8,20/0,141. random_rough: R7 13/4,32/0,376; R8 10/2,96/0,310; R9 13/6,72/0,303. wave_terrain: R7 15/5,78/0,350; R8 11/4,58/0,372; R9 6/6,62/0,245.
- vel_err: flat 0,080/0,076/0,095; slope 0,273/0,333/0,243; slope_inv 0,321/0,365/0,374; stairs 0,128/0,141/0,121; stairs_inv 0,177/0,250/0,129; random_rough 0,383/0,440/0,291; wave 0,324/0,379/0,308.
- Temuan: lereng (naik dan terbalik) adalah medan tersulit untuk semua policy (17-36% jatuh); tangga justru yang paling mudah. Pada random_rough dan gelombang perceptive (R9) jelas lebih jauh/lebih sedikit jatuh. R8 (blind, hanya tangga) terburuk di random_rough (3,0 m) konsisten dengan dugaan lupa setelah training tangga saja. R8/R9 sedikit lebih buruk di lereng naik daripada R7 (35/33 vs 26), tetapi selisih masih dalam noise.
- Catatan metode: rentang kesulitan penuh mencakup kemiringan ekstrem; angka jatuh adalah batas, bukan kemampuan pada lereng landai. Satuan slope_range belum dikonfirmasi.
- Run 8 vs 9 bukan perbandingan blind vs perceptive yang adil untuk seluruh medan (keduanya hanya tangga). Perbandingan adil: Run 7 (blind, campuran) vs Run 10 (perceptive, campuran sama); resep Run 9 pada task Rough perceptive, perlu cek batas kecepatan.
- Berikutnya: cek satuan slope, sapuan level lereng 0,2-0,8, keputusan Run 10.

### Penyapuan kemiringan lereng naik (hf_pyramid_slope), 0,5 m/s, seed 0 (29 Okt, 23:20)
- slope_range adalah gradien (rise/run); karena rentang mulai 0, level L = gradien L: 0,2=11 derajat, 0,4=22, 0,6=31, 0,8=39 (perkiraan).
- Jatuh/96 | sway | jarak(m): L0,2: R7 3 | 0,206 | 8,33; R8 3 | 0,182 | 8,55; R9 0 | 0,147 | 8,91. L0,4: R7 5 | 0,246 | 7,42; R8 3 | 0,210 | 7,31; R9 9 | 0,210 | 7,92. L0,6: R7 32 | 0,346 | 6,15; R8 24 | 0,314 | 6,52; R9 40 | 0,324 | 5,81. L0,8: R7 63 | 0,435 | 4,79; R8 52 | 0,420 | 5,19; R9 66 | 0,384 | 4,49.
- vel_err: L0,2 0,209/0,224/0,158; L0,4 0,278/0,321/0,224; L0,6 0,313/0,345/0,278; L0,8 0,335/0,373/0,291.
- Temuan: batas kemampuan K1 pada lereng sekitar 22-31 derajat (jatuh <10% sampai 22 derajat, 25-42% pada 31 derajat, >50% pada 39 derajat).
- Hipotesis "lupa setelah training tangga saja" TIDAK didukung: pada level tetap R8 paling sedikit jatuh di L0,6 dan L0,8; selisih 26 vs 35 di uji rentang penuh kemungkinan noise campuran kesulitan.
- Perceptive (R9) paling halus dan sempurna pada 11 derajat tetapi lebih banyak jatuh daripada R8 pada 22-39 derajat (9 vs 3, 40 vs 24, 66 vs 52); selisih L0,6 sekitar 2,4 SE: indikasi, satu seed. Dugaan belum diuji: kemiringan terasa lewat proprioception; R9 tidak pernah dilatih di lereng.
- Bahan video kasus gagal: R9 pada lereng 39 derajat dan tangga 0,18 m.
- Berikutnya: keputusan Run 10 (perceptive pada campuran medan kasar), video, laporan, README.

### Rancangan Run 10: perceptive pada campuran medan kasar (30 Okt, 23:15)
- Tujuan: perbandingan blind vs perceptive yang adil di seluruh jenis medan. Run 8 vs 9 hanya tangga (keduanya dilatih di STAIRS_TERRAINS_CFG), sedangkan Run 7 dilatih di ROUGH_TERRAINS_CFG.
- Rancangan terkontrol: Run 10 = titik awal sama dengan Run 7 (flat Run 5, model_4999, perluasan 187 kolom height scan bernilai nol), medan ROUGH_TERRAINS_CFG sama, 5000 iterasi sama. Satu-satunya beda: ada height scan. (Memulai dari bobot Run 7 ditolak: paparan medan kasar jadi dua kali lipat sehingga membaurkan hasil.)
- Task baru: Mjlab-Velocity-Rough-Perceptive-Booster-K1 (booster_k1_rough_env_cfg + batas kecepatan stage 1 seperti Run 9). Skrip perluasan: scripts/expand_to_perceptive_from_flat.py (SRC Run 5 model_4999, DST 2026-10-30_perceptive-init-from-flat).
- Backup 28 dan 29 Okt sudah ada di drive Windows (terrain-walker-2026-10-28-night, terrain-walker-2026-10-29).

## Run 10: K1 rough perceptive, warm start dari Run 5 (bobot diperluas)
- Mulai: 2026-10-30 23:18 WIB | Task: Mjlab-Velocity-Rough-Perceptive-Booster-K1 | 768 robot | 5000 iterasi (nomor sekitar 5000 sampai 10.000) | save-interval 200
- Resume dari: k1_velocity/2026-10-30_perceptive-init-from-flat model_9998.pt (asal Run 5 model_4999) | Folder run: logs/rsl_rl/k1_velocity/2026-10-30_23-17-57
- Medan: ROUGH_TERRAINS_CFG (sama dengan Run 7), curriculum terrain | Perceptive (height scan 187 titik) | kecepatan terkunci tahap 1
- Pembanding: Run 7 (blind, titik awal, medan, dan iterasi identik). Hasil: (diisi setelah selesai)
- Uji asap 20 iterasi: lolos tanpa size mismatch; 29.604 steps/s, 0,62 s/iter; iterasi 5018: reward 16,40 | episode length 290,73 | fell_over 1,4762 (jumlah env per reset, bukan persen) | time_out 0,7619 | level terrain 2,30 (maks 7) | error_vel_xy 0,2582.
- Catatan: ada terminasi out_of_terrain_bounds di training; terminasi tepi medan pada evaluasi sebelumnya adalah jenis ini, bukan jatuh fisik. Kolom fell di CSV evaluasi = terminasi selain time-out.

## Run 10 selesai (2026-10-31 00:10)
- Task: Mjlab-Velocity-Rough-Perceptive-Booster-K1, init dari 2026-10-30_perceptive-init-from-flat (model_9998.pt)
- Folder: /home/arya/projects/mjlab/logs/rsl_rl/k1_velocity/2026-10-30_23-17-57/
- 768 env, 5000 iterasi tambahan, selesai di iterasi 9998/9999, waktu 0:49:55, 92.160.000 langkah
- Snapshot iterasi terakhir (BUKAN kesimpulan, satu titik data): reward 35.36, ep length 855.6, fell_over 0.278, time_out 1.389, out_of_bounds 0
- terrain_levels mean 5.41 (max 9); hf_pyramid_slope_inv hanya 2.02, lainnya 5.26-5.98
- error_vel_xy 0.77, error_vel_yaw 0.92
- Berikutnya: summarize_run.py, evaluasi terkontrol Run 10 vs Run 7 (jenis medan, tangga, lereng), backup

## Evaluasi Run 10 vs Run 7/8/9 per jenis medan (2026-10-31)
- Protokol: 0,5 m/s, seed 0, 32 env x 3 episode (n=96 per sel), out-dir eval_t, script compare_terrain.py; keluar tepi = 0 di semua sel
- Jatuh asli %, Run7 / Run8 / Run9 / Run10:
  flat 0/0/0/0; pyramid_stairs 1,0/0/0/0; pyramid_stairs_inv 0/0/0/0
  hf_pyramid_slope 27,1/36,5/34,4/5,2; hf_pyramid_slope_inv 33,3/17,7/31,2/19,8
  random_rough 13,5/10,4/13,5/11,5; wave_terrain 15,6/11,5/6,2/19,8
- Run 10 vs Run 7: lereng naik jauh lebih baik (5,2 vs 27,1); lereng turun lebih baik; random_rough selisih kecil; wave lebih buruk (19,8 vs 15,6)
- Run 10 lebih lambat: jarak flat 7,4 vs 9,4 m; pyramid_stairs 5,4 vs 8,8 m (penyebab belum diselidiki)
- Koreksi: klaim "height scan membantu di random_rough dan wave" tidak bertahan (Run 9 terbaik di wave 6,2 tapi Run 10 terburuk 19,8)
- Catatan: satu run per resep -> efek height scan tidak terpisah dari variasi pelatihan
- Berikutnya: sapuan lereng L0.2-0.8 dan tinggi tangga untuk Run 10, selidiki kecepatan lebih rendah

## Sapuan lereng Run 10 (2026-10-31)
- Jatuh asli % / jarak m, Run10: L0.2 5,2/7,2; L0.4 8,3/5,8; L0.6 10,4/2,1; L0.8 6,2/1,6
- Run7: L0.2 3,1/8,3; L0.4 5,2/7,4; L0.6 33,3/6,1; L0.8 65,6/4,8
- Temuan: Run 10 jarang jatuh di lereng curam tapi hampir tidak maju (macet), BUKAN lebih mampu menanjak; persentase jatuh harus dibaca bersama jarak
- Koreksi: klaim "Run 10 jatuh lebih sedikit di lereng" dikoreksi di laporan (Bab IV 4.5, 4.6, abstrak, kesimpulan)
- Rencana: evaluasi seed 1 (Run 10 dan Run 7), evaluasi checkpoint Run 10 awal, ulang pelatihan seed lain, selidiki penyebab macet

## Evaluasi seed 1 dan gabungan 2 seed (2026-10-31)
- Run 7 dan Run 10 dievaluasi seed 0 + seed 1 (n=192/sel); Run 8/9 hanya seed 0 (n=96)
- Jatuh asli % / jarak m, Run7 vs Run10 (gabungan): flat 0/9,4 vs 0/7,4; pyramid_stairs 1,0/8,7 vs 0/5,5; stairs_inv 0/7,1 vs 0/7,1
  slope 35,4/6,3 vs 9,9/4,5; slope_inv 25,0/3,2 vs 16,1/4,7; random_rough 14,1/4,2 vs 12,0/5,9; wave 16,1/4,8 vs 15,1/6,6
- Seed 1 saja: slope Run7 43,8 vs Run10 14,6; slope_inv 16,7 vs 12,4; wave 16,7 vs 10,4
- Koreksi: "Run 10 lebih buruk di wave" tidak bertahan (seed 0 19,8 vs 15,6, seed 1 10,4 vs 16,7); variasi antar-seed sebesar selisih antar-run
- Bertahan: Run 10 lebih jarang jatuh di lereng naik di kedua seed, TAPI jarak tempuh lebih pendek (L0.8: 1,6 vs 4,8 m) -> sebagian karena macet/lebih lambat
- Terbuka: Run 10 lebih lambat di flat/stairs; kecepatan efektif belum dikontrol; satu run pelatihan per resep

## Kecepatan efektif Run 7 vs Run 10 (2 seed, 2026-10-31)
- Kecepatan rerata (jarak/lama) m/s, Run7 vs Run10: flat 0,47 vs 0,37; stairs 0,43 vs 0,27; slope L0.2 0,44 vs 0,37; L0.4 0,39 vs 0,30; L0.6 0,47 vs 0,11; L0.8 0,57 vs 0,09
  slope_inv 0,21 vs 0,25; random_rough 0,25 vs 0,32; wave 0,33 vs 0,42; stairs_inv 0,36 vs 0,35
- vel_err flat: 0,079 (Run7) vs 0,148 (Run10)
- Kesimpulan: rendahnya jatuh Run 10 di lereng curam sebagian besar karena hampir berhenti (bukan mendaki lebih baik); di random_rough dan wave Run 10 lebih cepat dengan jatuh setara
- Catatan: jarak = perpindahan, jatuh menuruni lereng bisa menaikkan angka Run 7
- Berikutnya: cek argumen seed train; ulang pelatihan Run 10 dan Run 7 dengan seed lain; selidiki kenapa Run 10 lebih lambat di flat/stairs

## run10_seed1 selesai (2026-10-31 01:56)
- Task: Mjlab-Velocity-Rough-Perceptive-Booster-K1, init dari 2026-10-30_perceptive-init-from-flat/model_9998.pt, agent.seed 1, env.seed 1, 768 env, 5000 iterasi tambahan
- Folder: logs/rsl_rl/k1_velocity/2026-10-31_01-05-44/
- Log penuh: /home/arya/projects/terrain-walker/train_logs/run10_seed1.log
- Tujuan: sampel pelatihan kedua untuk memisahkan efek height scan dari variasi pelatihan

## run7_seed1 selesai (2026-10-31 01:57)
- Task: Mjlab-Velocity-Rough-Blind-Booster-K1, init dari 2026-10-28_08-32-06/model_4999.pt, agent.seed 1, env.seed 1, 768 env, 5000 iterasi tambahan
- Folder: logs/rsl_rl/k1_velocity/2026-10-31_01-56-55/
- Log penuh: /home/arya/projects/terrain-walker/train_logs/run7_seed1.log
- Tujuan: sampel pelatihan kedua untuk memisahkan efek height scan dari variasi pelatihan

## run10_seed1 selesai (2026-10-31 02:49)
- Task: Mjlab-Velocity-Rough-Perceptive-Booster-K1, init dari 2026-10-30_perceptive-init-from-flat/model_9998.pt, agent.seed 1, env.seed 1, 768 env, 5000 iterasi tambahan
- Folder: logs/rsl_rl/k1_velocity/2026-10-31_01-58-35/
- Log penuh: /home/arya/projects/terrain-walker/train_logs/run10_seed1.log
- Tujuan: sampel pelatihan kedua untuk memisahkan efek height scan dari variasi pelatihan

## run7_seed1 selesai (2026-10-31 03:36)
- Task: Mjlab-Velocity-Rough-Blind-Booster-K1, init dari 2026-10-28_08-32-06/model_4999.pt, agent.seed 1, env.seed 1, 768 env, 5000 iterasi tambahan
- Folder: logs/rsl_rl/k1_velocity/2026-10-31_02-49-31/
- Log penuh: /home/arya/projects/terrain-walker/train_logs/run7_seed1.log
- Tujuan: sampel pelatihan kedua untuk memisahkan efek height scan dari variasi pelatihan

## Evaluasi 4 kebijakan: Run7/Run10 x seed latih 42 dan 1 (2026-11-02)
- Eval: 7 medan, 0,5 m/s, seed eval 0 dan 1 (n=192/sel); run7s1 = folder 2026-10-31_02-49-31, run10s1 = 2026-10-31_01-58-35
- Jatuh asli % / jarak m, urutan Run7(42), Run7(1), Run10(42), Run10(1):
  flat 0/9,4, 0/9,2, 0/7,4, 0/8,5; pyramid_stairs 1,0/8,7, 1,0/8,8, 0/5,5, 0/8,0; stairs_inv 0/7,1, 2,6/7,9, 0/7,1, 0,5/8,5
  slope 35,4/6,3, 21,4/7,0, 9,9/4,5, 7,3/4,7; slope_inv 25,0/3,2, 26,6/2,5, 16,1/4,7, 25,0/4,6
  random_rough 14,1/4,2, 11,5/3,8, 12,0/5,9, 15,6/6,6; wave 16,1/4,8, 18,8/4,3, 15,1/6,6, 16,7/7,2
- Konsisten di dua seed latih: slope naik Run10 jatuh jauh lebih sedikit (tapi maju lebih lambat); random_rough dan wave jatuh setara tapi Run10 40-70% lebih jauh
- Hanya variasi pelatihan: "Run10 lambat di stairs" (5,5 vs 8,0 m); slope_inv tumpang tindih
- Variasi Run7 antar seed latih di slope: 35,4 vs 21,4 -> satu seed tidak cukup
- Kesimpulan masih indikatif (2 seed latih per resep)
- Catatan ops: setelah reboot drive Windows harus di-mount ulang (udisksctl mount -b /dev/nvme0n1p3) karena logs adalah symlink ke /media/arya/Windows/UbuntuProject/rl_data/logs

## Percobaan penggabungan bobot blind+perceptive (2026-11-03)
- Ide: interpolasi aktor (1-a)*Run7 + a*Run10 (induk seed latih 42, sama-sama dari model datar Run 5); script scripts/merge_actors.py; checkpoint logs/rsl_rl/k1_velocity/2026-11-03_merge-a{0.0,0.25,0.5,0.75}
- Lapisan pertama Run7 ditulis ulang ke ruang normalisasi Run10 (asumsi EPS 1e-2), kolom height scan = 0
- Uji kewarasan a=0: flat 0% / 9,40 m (= Run7 9,4); slope 32,3% / 6,08 m (Run7 seed0 27,1% / 6,7; dalam derau)
- Kriteria sebelum evaluasi: a=0,5 berhasil bila (a) jatuh slope ~8-10%, (b) jarak flat ~9 m, (c) random_rough dan wave tidak lebih buruk dari kedua induk
- Hasil a=0,5 (n=192, jatuh%/jarak m): flat 0/7,9; slope 22,4/6,6; random_rough 18,8/4,0; wave 13,0/4,5
  Induk Run7: flat 0/9,4; slope 35,4/6,3; random 14,1/4,2; wave 16,1/4,8. Run10: flat 0/7,4; slope 9,9/4,5; random 12,0/5,9; wave 15,1/6,6
- Kesimpulan: kriteria (a)(b) gagal, (c) sebagian; tidak ada sinergi, perilaku di antara induk atau mengikuti Run7. a lain tidak diuji
- Ide lanjutan (bila ada waktu): latih satu kebijakan dengan dropout pada height scan

## Klip demo terkontrol (2026-11-03)
- Klip dari play (record_clips.sh): robot muncul di platform datar dengan perintah acak, banyak keluar peta, tidak mewakili medan sulit -> hanya cocok sebagai klip pembuka
- Dibuat scripts/record_policy.py (salinan tambalan eval_policy.py + VideoRecorder, opsi via env REC_DIR/REC_LEN/REC_ENV/REC_W/REC_H) dan scripts/record_failures.sh
- Klip di videos/clips/<nama>/rl-video-step-0.mp4 (8 robot, 12 detik, perintah beku 0,5 m/s)
- Isi (jatuh/8, jarak m): run10 random_rough 0/8 4,06; run10 slope L0.8 0/8 1,19 (hampir tidak maju); run7 slope L0.8 3/8 5,20; run9 slope L0.8 5/8 4,06; run9 stairs 0,18 1/8 4,79; run7 stairs 0,18 3/8 4,76
- Catatan: n=8 per klip hanya untuk memilih bahan video, bukan statistik

## 2026-11-03 - Klip demo terkontrol (kamera + rekam sampai jatuh)
- Klip lama dari play.py tidak representatif (perintah acak, robot keluar peta). Diganti scripts/record_policy.py (perintah maju 0,5 m/s, 8 robot, episode 12 s).
- Kamera: elevasi harus NEGATIF di MuJoCo agar kamera di atas (positif = dari bawah tanah). Dipakai REC_ELEV=-35, REC_AZ=90 (samping), REC_DIST=5; kamera bawaan terhalang anak tangga.
- Klip hanya merekam satu robot (REC_ENV). Karena GPU tidak deterministik, scripts/record_falls.sh mengulang REC_ENV 0-7 dan menyimpan klip hanya jika robot itu tercatat jatuh (fell=1, length_steps>=150) di CSV run yang sama. Dapat: run7 tangga env1, run9 tangga env1, run7 lereng env1, run9 lereng env2.
- Run 7 di tangga 0,18 m: menuruni beberapa anak tangga dengan baik, lalu jatuh menabrak anak tangga di depannya (contoh keterbatasan blind).
- Keterangan klip tidak memakai angka dari run perekaman; angka evaluasi hanya di laporan. Draft video: videos/demo_draft.mp4 (9,5 MB, 79 s, 960x540).

## run10_seed2 selesai (2026-11-11 23:22)
- Task: Mjlab-Velocity-Rough-Perceptive-Booster-K1, init dari 2026-10-30_perceptive-init-from-flat/model_9998.pt, agent.seed 2, env.seed 2, 768 env, 5000 iterasi tambahan
- Folder: logs/rsl_rl/k1_velocity/2026-11-11_22-31-19/
- Log penuh: /home/arya/projects/terrain-walker/train_logs/run10_seed2.log
- Tujuan: sampel pelatihan ketiga (seed 2) untuk menguatkan perbandingan blind vs perceptive

## run7_seed2 selesai (2026-11-12 00:10)
- Task: Mjlab-Velocity-Rough-Blind-Booster-K1, init dari 2026-10-28_08-32-06/model_4999.pt, agent.seed 2, env.seed 2, 768 env, 5000 iterasi tambahan
- Folder: logs/rsl_rl/k1_velocity/2026-11-11_23-22-31/
- Log penuh: /home/arya/projects/terrain-walker/train_logs/run7_seed2.log
- Tujuan: sampel pelatihan ketiga (seed 2) untuk menguatkan perbandingan blind vs perceptive
