# Walking on Uneven Terrain: Blind vs Perceptive (Booster K1, mjlab)

Proyek akhir magang di tim riset ICHIRO (ITS). Kami melatih policy berjalan untuk robot humanoid **Booster K1** di simulasi **mjlab** (MuJoCo Warp) dengan **PPO** (rsl_rl), lalu membandingkan dua jenis policy di medan tidak rata:

- **Blind**: hanya mengandalkan propriosepsi (sensor sendi dan IMU).
- **Perceptive**: ditambah *height scan* (187 titik ketinggian medan di sekitar robot).

> Semua hasil berasal dari simulasi. Run 7 dan Run 10 punya **tiga seed latih**; Run 8, Run 9, dan versi tangga tingginya hanya **satu**. Jadi kesimpulannya masih **gambaran awal**, bukan klaim umum.

## Demo

Video demo (termasuk kegagalan): _tautan GitHub Release: ISI SETELAH DIUNGGAH_

## Temuan utama

- Keunggulan perceptive konsisten hanya pada **jarak tempuh** di medan random rough dan gelombang (sekitar 40-70 persen lebih jauh, jumlah jatuh setara).
- Di slope curam, Run 10 (perceptive) jarang jatuh karena **hampir berhenti** (kecepatan efektif 0,09 vs 0,57 m/s di gradien 0,8), bukan karena mendaki lebih baik.
- Tangga pada grid bawaan (tinggi sampai 0,10 m) dan medan datar: setara. Cekungan: hasil tumpang tindih.
- Penggabungan bobot blind dan perceptive (interpolasi aktor, a = 0,5): **tidak ada sinergi**.
- Di tangga 0,18 m, Run 9 (perceptive) jatuh 54,2 persen, jauh di atas Run 8 (blind, 17,7 persen). Penyebabnya tinggi tangga latih yang hanya sampai 0,10 m: setelah Run 8 dan Run 9 dilatih ulang dengan tangga sampai 0,20 m (Run 8-tinggi dan Run 9-tinggi), jatuh di 0,18 m turun menjadi 6,2 persen untuk keduanya. Di 0,20 m: 8,9 persen (perceptive) vs 16,1 persen (blind), satu seed latih.
- Menolkan atau mengacak height scan Run 9 di tangga 0,15 m menaikkan jatuh dari 10,4 ke 66,1 persen, jadi policy-nya memang memakai scan.

Tabel lengkap dan daftar klaim yang kami tarik kembali ada di [`EXPERIMENTS.md`](EXPERIMENTS.md).

## Run yang dilatih

| Run | Task | Titik awal | Medan latih |
|---|---|---|---|
| 5 | Flat-Booster-K1 | dari nol | datar |
| 6 | Rough-Booster-K1 (perceptive) | dari nol | rough campuran (gagal: robot diam) |
| 7 | Rough-Blind-Booster-K1 | Run 5 | rough campuran |
| 8 | Stairs-Blind-Booster-K1 | Run 7 | tangga |
| 9 | Stairs-Perceptive-Booster-K1 | Run 7 + kolom height scan bernilai nol | tangga |
| 10 | Rough-Perceptive-Booster-K1 | Run 5 + kolom height scan bernilai nol | rough campuran |
| 8-tinggi | StairsTall-Blind-Booster-K1 | Run 7 | tangga sampai 0,20 m |
| 9-tinggi | StairsTall-Perceptive-Booster-K1 | Run 7 + kolom height scan bernilai nol | tangga sampai 0,20 m |

Run 10 sengaja memakai titik awal, medan, dan jumlah iterasi yang sama dengan Run 7 sehingga hanya height scan yang berbeda.

## Protokol evaluasi

Dijalankan oleh `scripts/eval_policy.py`: perintah maju dibekukan 0,5 m/s, curriculum dimatikan, 32 robot x 3 episode x 20 detik, dua seed evaluasi. "Jatuh" dihitung hanya jika episode berakhir bukan karena waktu habis dan robot tidak keluar tepi peta (|x| atau |y| >= 29,5 m). Metrik: persen jatuh, jarak, kecepatan efektif, sway, galat kecepatan.

## Isi repo

| Berkas | Fungsi |
|---|---|
| `mjlab_k1_port/` | port Booster K1 ke mjlab: `asset_zoo/robots/booster_k1/` (model robot, mesh, `k1_constants.py`) dan `tasks/velocity/config/k1/` (`env_cfgs.py`, `rl_cfg.py`, registrasi task). `BASE_COMMIT.txt` mencatat commit mjlab dasar. |
| `scripts/eval_policy.py` | evaluasi policy per medan |
| `scripts/eval_seed1.sh` | menjalankan evaluasi untuk model seed latih 1 |
| `scripts/retrain_seed1.sh`, `scripts/retrain_seed2.sh` | melatih ulang Run 7 dan Run 10 dengan seed latih 1 dan 2 |
| `scripts/eval_seed2.sh` | menjalankan evaluasi untuk model seed latih 2 |
| `scripts/eval_stairs_fine.sh` | sapuan tinggi tangga halus (0,14; 0,16; 0,17 m) untuk Run 8 dan 9 |
| `scripts/eval_policy_scan.py`, `scripts/eval_scan.sh` | uji peran height scan Run 9 (scan dinolkan atau diacak saat evaluasi) |
| `scripts/add_stairs_tall.py` | menambah set medan tangga tinggi dan dua task baru ke mjlab (tidak mengubah set lama) |
| `scripts/train_stairs_tall.sh`, `scripts/eval_tall.sh` | melatih dan mengevaluasi Run 8-tinggi dan Run 9-tinggi |
| `scripts/make_tables*.py` | mencetak tabel hasil dari CSV evaluasi |
| `scripts/expand_to_perceptive.py`, `scripts/expand_to_perceptive_from_flat.py` | memperluas bobot blind menjadi perceptive (kolom height scan bernilai nol) |
| `scripts/merge_actors.py` | interpolasi bobot aktor Run 7 dan Run 10 |
| `scripts/summarize_run.py`, `scripts/compare_terrain.py` | merangkum log latih dan membandingkan hasil antar medan |
| `scripts/record_policy.py`, `scripts/record_clips.sh` | merekam klip video dari policy |
| `scripts/record_failures.sh`, `scripts/record_falls.sh` | merekam klip, mengulang sampai robot yang direkam benar-benar jatuh |
| `scripts/fell_check.py` | memeriksa CSV evaluasi apakah robot yang direkam jatuh |
| `scripts/compile_demo.sh` | menyusun klip dan teks menjadi video demo |
| `eval/`, `eval_ep14/`, `eval_h/`, `eval_t/`, `eval_scan/`, `eval_tall/` | CSV hasil evaluasi mentah (`eval/v1/` = putaran evaluasi sebelumnya) |
| `EXPERIMENTS.md` | catatan eksperimen ringkas (keputusan dan hasil akhir) |
| `EXPERIMENTS_FULL.md` | log kronologis lengkap |

## Lingkungan

- Ubuntu (dual-boot), GPU RTX 4050 6 GB; pelatihan memakai 768 robot paralel agar VRAM tetap di bawah sekitar 5 GB.
- mjlab commit dasar `8bb2bc9e187797689ec82c78c35019afd2fd0376`.
- Robot Booster K1, 22 derajat kebebasan.

## Cara mereproduksi

Port K1 dibuat sebagai empat commit di atas mjlab commit `8bb2bc9e187797689ec82c78c35019afd2fd0376` (dicatat di `mjlab_k1_port/BASE_COMMIT.txt`; commit terakhir port: `a78fb2044e38eacd29d37c0e61a1ba00d4a33c1b`). Repo ini menyimpan salinan berkas yang kami tambahkan. Untuk memakainya: clone mjlab, `git checkout 8bb2bc9e187797689ec82c78c35019afd2fd0376`, lalu salin isi `mjlab_k1_port/src/` ke `src/` pada clone tersebut. Contoh melanjutkan Run 7 dari model datar (Run 5) dengan seed latih 1 (dari `scripts/retrain_seed1.sh`):

```bash
cd ~/projects/mjlab
uv run train Mjlab-Velocity-Rough-Blind-Booster-K1 \
  --env.scene.num-envs 768 --agent.max-iterations 5000 --agent.save-interval 200 \
  --agent.resume True --agent.load-run <folder-run-datar> --agent.load-checkpoint model_4999.pt \
  --agent.seed 1 --env.seed 1
```

Run perceptive (Run 9 dan 10) dimulai dari bobot blind/datar yang diperluas dengan `scripts/expand_to_perceptive.py` atau `scripts/expand_to_perceptive_from_flat.py`. Evaluasi satu medan:

```bash
uv run python -u ~/projects/terrain-walker/scripts/eval_policy.py \
  --task Mjlab-Velocity-Rough-Blind-Booster-K1 --checkpoint <path/model.pt> \
  --label run7s1 --seed 0 --terrain-type random_rough --out-dir eval_t
```

Jenis medan yang dievaluasi: `flat`, `pyramid_stairs`, `pyramid_stairs_inv`, `hf_pyramid_slope`, `hf_pyramid_slope_inv`, `random_rough`, `wave_terrain`. Skrip `scripts/eval_seed1.sh` menjalankan semuanya untuk dua seed evaluasi. Catatan lengkap tiap run ada di [`EXPERIMENTS_FULL.md`](EXPERIMENTS_FULL.md).

## Keterbatasan

- Seed latih: tiga untuk Run 7 dan Run 10, satu untuk Run 8, Run 9, dan versi tangga tingginya; selisih kecil dapat berasal dari variasi seed.
- Selama evaluasi, dorongan acak, derau, dan randomisasi gesekan tetap aktif.
- Hanya simulasi; belum diuji di robot nyata.
- Episode dalam satu robot berbagi medan, dan GPU tidak deterministik, sehingga angka dapat bergeser sedikit antar evaluasi.
- Satu seed evaluasi untuk Run 8 dan 9.

## Ide lanjutan

Lebih banyak seed latih (terutama untuk tangga tinggi), tangga di atas 0,20 m, pelatihan dengan *dropout* pada height scan, dan menyelidiki mengapa policy perceptive hampir berhenti di slope curam.

## Sumber dan lisensi

- Simulator dan kerangka tugas: [mujocolab/mjlab](https://github.com/mujocolab/mjlab) (lisensi Apache 2.0, salinan di `mjlab_k1_port/LICENSE.mjlab`). Tugas velocity K1 di repo ini adalah modifikasi dari tugas velocity bawaan mjlab; berkas yang kami tambah atau ubah ada di `mjlab_k1_port/`.
- Model robot Booster K1 (`k1.xml` dan mesh STL di `mjlab_k1_port/.../booster_k1/`) berasal dari [BoosterRobotics/booster_assets](https://github.com/BoosterRobotics/booster_assets), hak cipta 2025 BoosterRobotics, lisensi BSD 3-Clause (salinan di `mjlab_k1_port/LICENSE.booster_assets`). Aset robot tetap milik Booster Robotics.
- Kontribusi proyek ini: konfigurasi tugas K1 (`env_cfgs.py`, `rl_cfg.py`), skrip evaluasi, perekaman klip, penggabungan bobot, dan seluruh catatan eksperimen.
- Algoritma PPO dari rsl_rl (bawaan mjlab).

## Penulis

I Putu Rohedi Arya Wijaya Putra dan Claude

## Note

Aku jujur aja mas kalo dibantu AI makanya aku masukin claude ke kontributor
