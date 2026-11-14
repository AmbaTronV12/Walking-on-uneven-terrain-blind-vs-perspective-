import csv, os, glob

BASE = os.path.expanduser("~/projects/terrain-walker/eval_h")

def is_fall(r):
    if int(float(r["fell"])) != 1:
        return False
    if r.get("end_x") not in (None, ""):
        if abs(float(r["end_x"])) >= 29.5 or abs(float(r["end_y"])) >= 29.5:
            return False
    return True

def load(key, h):
    rows, seeds = [], []
    for sd in (0, 1):
        p = os.path.join(BASE, f"{key}_speed0.5_seed{sd}_h{h}.csv")
        if os.path.exists(p):
            with open(p, newline="") as f:
                rows += list(csv.DictReader(f))
            seeds.append(sd)
    return rows, seeds

def c(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")

HEIGHTS = ["0.1", "0.12", "0.14", "0.15", "0.16", "0.17", "0.18"]
KEYS = [("Run 8 (blind)", "run8_stairs-blind"), ("Run 9 (perceptive)", "run9_stairs-perceptive")]

print("TABEL 4.3c  Sapuan tinggi tangga, jatuh asli % / jarak rerata m (seed evaluasi digabung)")
print("| Tinggi tangga (m) | Run 8 jatuh (%) | Run 8 jarak (m) | Run 9 jatuh (%) | Run 9 jarak (m) | n per sel | seed eval |")
print("| --- | --- | --- | --- | --- | --- | --- |")
for h in HEIGHTS:
    cells, ns, ss = [], [], []
    for _, key in KEYS:
        rows, seeds = load(key, h)
        if not rows:
            cells += ["-", "-"]
            continue
        n = len(rows)
        f = 100.0 * sum(is_fall(r) for r in rows) / n
        d = sum(float(r["distance_m"]) for r in rows) / n
        cells += [c(f), c(d)]
        ns.append(n); ss.append(seeds)
    nn = "/".join(str(x) for x in ns) if ns else "-"
    s = "+".join(str(x) for x in ss[0]) if ss else "-"
    print(f"| {c(float(h),2)} | " + " | ".join(cells) + f" | {nn} | {s} |")

print()
print("Per seed (untuk memeriksa konsistensi):")
for h in ["0.14", "0.15", "0.16", "0.17", "0.18"]:
    for name, key in KEYS:
        out = []
        for sd in (0, 1):
            p = os.path.join(BASE, f"{key}_speed0.5_seed{sd}_h{h}.csv")
            if os.path.exists(p):
                with open(p, newline="") as f:
                    rows = list(csv.DictReader(f))
                out.append(f"seed{sd}={c(100.0*sum(is_fall(r) for r in rows)/len(rows))}%")
        print(f"  h={h} {name}: " + "  ".join(out))
