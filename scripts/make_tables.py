import csv, os

BASE = os.path.expanduser("~/projects/terrain-walker")

def rows_of(rel):
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        return None
    with open(p, newline="") as f:
        return list(csv.DictReader(f))

def is_fall(r):
    if int(float(r["fell"])) != 1:
        return False
    if r.get("end_x") not in (None, ""):
        if abs(float(r["end_x"])) >= 29.5 or abs(float(r["end_y"])) >= 29.5:
            return False
    return True

def mean(rows, k):
    v = [float(r[k]) for r in rows if r.get(k) not in (None, "")]
    return sum(v) / len(v) if v else float("nan")

def summ(rows):
    n = len(rows)
    falls = sum(is_fall(r) for r in rows)
    return n, 100.0 * falls / n, mean(rows, "distance_m"), mean(rows, "sway"), mean(rows, "vel_err")

def c(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")

print("TABEL 4.2  Grid tangga bawaan, 0,5 m/s, seed 0")
print("| Run | n | Jatuh asli (%) | Jarak rerata (m) | Sway | Galat kecepatan |")
print("| --- | --- | --- | --- | --- | --- |")
for name, rel in [
    ("Run 7 (blind, kasar)", "eval/run7_rough-blind_speed0.5_seed0.csv"),
    ("Run 8 (blind, tangga)", "eval/run8_stairs-blind_speed0.5_seed0.csv"),
    ("Run 9 (perceptive, tangga)", "eval/run9_stairs-perceptive_speed0.5_seed0.csv"),
]:
    rows = rows_of(rel)
    if rows is None:
        print(f"| {name} | - | - | - | - | - |")
        continue
    n, f, d, s, v = summ(rows)
    print(f"| {name} | {n} | {c(f)} | {c(d)} | {c(s,3)} | {c(v,3)} |")

RUNS = [("Run 7 (blind)", "run7_rough-blind"),
        ("Run 8 (blind)", "run8_stairs-blind"),
        ("Run 9 (perceptive)", "run9_stairs-perceptive")]
HEIGHTS = ["0.1", "0.12", "0.15", "0.18"]

print()
print("TABEL 4.3  Jatuh asli (%) menurut tinggi anak tangga, seed 0")
print("| Tinggi tangga (m) | " + " | ".join(n for n, _ in RUNS) + " |")
print("| --- | " + " | ".join("---" for _ in RUNS) + " |")
for h in HEIGHTS:
    cells = []
    for _, key in RUNS:
        rows = rows_of(f"eval_h/{key}_speed0.5_seed0_h{h}.csv")
        if rows is None:
            cells.append("-")
        else:
            n, f, *_ = summ(rows)
            cells.append(f"{c(f)} (n={n})")
    print(f"| {c(float(h),2)} | " + " | ".join(cells) + " |")

print()
print("TABEL 4.3b  Dua seed evaluasi digabung (seed 0 + seed 1)")
print("| Tinggi tangga (m) | Run 8 (blind) | Run 9 (perceptive) |")
print("| --- | --- | --- |")
for h in ["0.15", "0.18"]:
    cells = []
    for key in ["run8_stairs-blind", "run9_stairs-perceptive"]:
        pooled = []
        for sd in (0, 1):
            r = rows_of(f"eval_h/{key}_speed0.5_seed{sd}_h{h}.csv")
            if r:
                pooled += r
        if not pooled:
            cells.append("-")
        else:
            n, f, *_ = summ(pooled)
            cells.append(f"{c(f)} (n={n})")
    print(f"| {c(float(h),2)} | " + " | ".join(cells) + " |")
