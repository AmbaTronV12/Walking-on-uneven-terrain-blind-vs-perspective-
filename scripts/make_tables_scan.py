import csv, os
H = os.path.expanduser("~/projects/terrain-walker/eval_h")
S = os.path.expanduser("~/projects/terrain-walker/eval_scan")

def is_fall(r):
    if int(float(r["fell"])) != 1:
        return False
    if r.get("end_x") not in (None, ""):
        if abs(float(r["end_x"])) >= 29.5 or abs(float(r["end_y"])) >= 29.5:
            return False
    return True

def load(base, key, h, seeds=(0, 1)):
    rows = []
    for sd in seeds:
        p = os.path.join(base, f"{key}_speed0.5_seed{sd}_h{h}.csv")
        if os.path.exists(p):
            with open(p, newline="") as f:
                rows += list(csv.DictReader(f))
    return rows

def c(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")

def stat(rows):
    if not rows:
        return "-", "-", 0
    n = len(rows)
    return (c(100.0 * sum(is_fall(r) for r in rows) / n),
            c(sum(float(r["distance_m"]) for r in rows) / n), n)

MODES = [("Scan utuh", H, "run9_stairs-perceptive"),
         ("Scan dinolkan", S, "run9_scan-zero"),
         ("Scan diacak antar robot", S, "run9_scan-shuffle")]

print("TABEL 4.3d  Run 9, scan utuh vs dinolkan vs diacak (jatuh asli % / jarak m, seed eval 0+1)")
print("| Mode scan | 0,15 m jatuh (%) | 0,15 m jarak (m) | 0,18 m jatuh (%) | 0,18 m jarak (m) | n per sel |")
print("| --- | --- | --- | --- | --- | --- |")
for name, base, key in MODES:
    cells, ns = [], []
    for h in ("0.15", "0.18"):
        f, d, n = stat(load(base, key, h))
        cells += [f, d]; ns.append(n)
    print(f"| {name} | " + " | ".join(cells) + f" | {'/'.join(map(str, ns))} |")

print()
print("Per seed:")
for name, base, key in MODES:
    for h in ("0.15", "0.18"):
        out = []
        for sd in (0, 1):
            f, d, n = stat(load(base, key, h, (sd,)))
            out.append(f"seed{sd}={f}% (n={n})")
        print(f"  h={h} {name}: " + "  ".join(out))
