import csv, os
T = os.path.expanduser("~/projects/terrain-walker/eval_tall")
H = os.path.expanduser("~/projects/terrain-walker/eval_h")

def is_fall(r):
    if int(float(r["fell"])) != 1:
        return False
    if r.get("end_x") not in (None, ""):
        if abs(float(r["end_x"])) >= 29.5 or abs(float(r["end_y"])) >= 29.5:
            return False
    return True

def load(key, h, seeds=(0, 1)):
    rows = []
    for sd in seeds:
        for base in (T, H):
            p = os.path.join(base, f"{key}_speed0.5_seed{sd}_h{float(h):g}.csv")
            if os.path.exists(p):
                with open(p, newline="") as f:
                    rows += list(csv.DictReader(f))
                break
    return rows

def c(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")

def stat(rows):
    if not rows:
        return "-", "-", 0
    n = len(rows)
    return (c(100.0 * sum(is_fall(r) for r in rows) / n),
            c(sum(float(r["distance_m"]) for r in rows) / n), n)

COLS = [("Run 8 lama", "run8_stairs-blind"), ("Run 8-tinggi", "run8_tall-blind"),
        ("Run 9 lama", "run9_stairs-perceptive"), ("Run 9-tinggi", "run9_tall-perceptive")]
HS = ["0.12", "0.15", "0.18", "0.20"]

print("TABEL 4.3e  Tangga tinggi: jatuh asli (%) dan jarak (m), seed eval digabung")
print("| Tinggi tangga (m) | " + " | ".join(f"{n} jatuh (%)" for n, _ in COLS) + " | " + " | ".join(f"{n} jarak (m)" for n, _ in COLS) + " | n per sel |")
print("| --- | " + " | ".join("---" for _ in range(9)) + " |")
for h in HS:
    fs, ds, ns = [], [], []
    for _, key in COLS:
        f, d, n = stat(load(key, h))
        fs.append(f); ds.append(d); ns.append(str(n))
    print(f"| {c(float(h),2)} | " + " | ".join(fs) + " | " + " | ".join(ds) + " | " + "/".join(ns) + " |")

print()
print("Per seed (jatuh %):")
for h in HS:
    for name, key in COLS:
        out = []
        for sd in (0, 1):
            f, d, n = stat(load(key, h, (sd,)))
            out.append(f"seed{sd}={f}% (n={n})")
        print(f"  h={h} {name}: " + "  ".join(out))
