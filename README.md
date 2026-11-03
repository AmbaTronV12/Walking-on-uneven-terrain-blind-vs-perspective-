# Walking on Uneven Terrain: Blind vs Perceptive (Booster K1, mjlab)

Proyek akhir magang di tim riset ICHIRO (ITS). Kami melatih kebijakan berjalan untuk robot humanoid **Booster K1** di simulasi **mjlab** (MuJoCo Warp) dengan **PPO** (rsl_rl), lalu membandingkan dua jenis kebijakan di medan tidak rata:

- **Blind**: hanya mengandalkan propriosepsi (sensor sendi dan IMU).
- **Perceptive**: ditambah *height scan* (187 titik ketinggian medan di sekitar robot).

> Semua hasil berasal dari simulasi dan hanya **dua seed latih** per resep, jadi kesimpulannya **indikatif**, bukan klaim umum.

## Demo

Video demo (termasuk kegagalan): _tautan GitHub Release: ISI SETELAH DIUNGGAH_

## Temuan utama

- Keunggulan perceptive konsisten hanya pada **jarak tempuh** di medan kasar acak dan gelombang (sekitar 40-70 persen lebih jauh, jumlah jatuh setara).
- Di lereng curam, Run 10 (perceptive) jarang jatuh karena **hampir berhenti** (kecepatan efektif 0,09 vs 0,57 m/s di gradien 0,8), bukan karena mendaki lebih baik.
- Tangga dan medan datar: setara. Cekungan: hasil tumpang tindih.
- Penggabungan bobot blind dan perceptive (interpolasi aktor, a = 0,5): **tidak ada sinergi**.
- Tangga 0,18 m melampaui tinggi latih (0,10 m); Run 7 (blind) jatuh 61,5 persen, Run 8 (blind, dilatih di tangga) 17,7 persen, Run 9 (perceptive, dilatih di tangga) 54,2 persen.

Tabel lengkap dan daftar klaim yang kami tarik kembali ada di [`EXPERIMENTS.md`](EXPERIMENTS.md).

## Run yang dilatih

| Run | Task | Titik awal | Medan latih |
|---|---|---|---|
| 5 | Flat-Booster-K1 | dari nol | datar |
| 6 | Rough-Booster-K1 (perceptive) | dari nol | kasar campuran (gagal: robot diam) |
| 7 | Rough-Blind-Booster-K1 | Run 5 | kasar campuran |
| 8 | Stairs-Blind-Booster-K1 | Run 7 | tangga |
| 9 | Stairs-Perceptive-Booster-K1 | Run 7 + kolom height scan bernilai nol | tangga |
| 10 | Rough-Perceptive-Booster-K1 | Run 5 + kolom height scan bernilai nol | kasar campuran |

Run 10 sengaja memakai titik awal, medan, dan jumlah iterasi yang sama dengan Run 7 sehingga hanya height scan yang berbeda.

## Protokol evaluasi

Dijalankan oleh `scripts/eval_policy.py`: perintah maju dibekukan 0,5 m/s, kurikulum dimatikan, 32 robot x 3 episode x 20 detik, dua seed evaluasi. "Jatuh" dihitung hanya jika episode berakhir bukan karena waktu habis dan robot tidak keluar tepi peta (|x| atau |y| >= 29,5 m). Metrik: persen jatuh, jarak, kecepatan efektif, sway, galat kecepatan.

## Isi repo

| Berkas | Fungsi |
|---|---|
| `mjlab_k1_port/` | port Booster K1 ke mjlab: `asset_zoo/robots/booster_k1/` (model robot, mesh, `k1_constants.py`) dan `tasks/velocity/config/k1/` (`env_cfgs.py`, `rl_cfg.py`, registrasi task). `BASE_COMMIT.txt` mencatat commit mjlab dasar. |
| `scripts/eval_policy.py` | evaluasi kebijakan per medan |
| `scripts/eval_seed1.sh` | menjalankan evaluasi untuk model seed latih 1 |
| `scripts/retrain_seed1.sh` | melatih ulang Run 7 dan Run 10 dengan seed latih 1 |
| `scripts/expand_to_perceptive.py`, `scripts/expand_to_perceptive_from_flat.py` | memperluas bobot blind menjadi perceptive (kolom height scan bernilai nol) |
| `scripts/merge_actors.py` | interpolasi bobot aktor Run 7 dan Run 10 |
| `scripts/summarize_run.py`, `scripts/compare_terrain.py` | merangkum log latih dan membandingkan hasil antar medan |
| `scripts/record_policy.py`, `scripts/record_clips.sh` | merekam klip video dari kebijakan |
| `scripts/record_failures.sh`, `scripts/record_falls.sh` | merekam klip, mengulang sampai robot yang direkam benar-benar jatuh |
| `scripts/fell_check.py` | memeriksa CSV evaluasi apakah robot yang direkam jatuh |
| `scripts/compile_demo.sh` | menyusun klip dan teks menjadi video demo |
| `eval/`, `eval_ep14/`, `eval_h/` | CSV hasil evaluasi mentah (`eval/v1/` = putaran evaluasi sebelumnya) |
| `EXPERIMENTS.md` | catatan eksperimen ringkas (keputusan dan hasil akhir) |
| `EXPERIMENTS_FULL.md` | log kronologis lengkap |

## Lingkungan

- Ubuntu (dual-boot), GPU RTX 4050 6 GB; pelatihan memakai 768 robot paralel agar VRAM tetap di bawah sekitar 5 GB.
- mjlab commit dasar `8bb2bc9e187797689ec82c78c35019afd2fd0376`.
- Robot Booster K1, 22 derajat kebebasan.

## Cara mereproduksi

Pelatihan dijalankan dari clone mjlab pada commit dasar di `mjlab_k1_port/BASE_COMMIT.txt`, dengan berkas `mjlab_k1_port/src/...` ditempatkan pada path yang sama di dalam clone tersebut. Contoh melanjutkan Run 7 dari model datar (Run 5) dengan seed latih 1 (dari `scripts/retrain_seed1.sh`):

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

- Hanya dua seed latih per resep; selisih kecil dapat berasal dari variasi seed.
- Hanya simulasi; belum diuji di robot nyata.
- Episode dalam satu robot berbagi medan, dan GPU tidak deterministik, sehingga angka dapat bergeser sedikit antar evaluasi.
- Satu seed evaluasi untuk Run 8 dan 9.

## Ide lanjutan

Lebih banyak seed latih, pelatihan dengan *dropout* pada height scan, dan menyelidiki mengapa kebijakan perceptive berhenti di lereng curam.

## Penulis

Arya, magang di tim ICHIRO, Institut Teknologi Sepuluh Nopember (ITS).
