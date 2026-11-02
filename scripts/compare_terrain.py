import csv, glob, os, re, collections
D = os.path.expanduser("~/projects/terrain-walker/eval_t")
rows = collections.defaultdict(list)
for f in sorted(glob.glob(D + "/*_speed0.5_seed*_*.csv")):
    b = os.path.basename(f)[:-4]
    m = re.match(r"(.+?)_speed0\.5_seed\d+_(.+)$", b)
    if not m: continue
    label, terr = m.groups()
    if label.startswith("smoke"): continue
    for r in csv.DictReader(open(f)):
        rows[(label, terr)].append(r)
labels = sorted({k[0] for k in rows})
terrs = sorted({k[1] for k in rows})
def stat(rs):
    n = len(rs)
    edge = real = 0
    for r in rs:
        if str(r["fell"]).lower() in ("1", "true", "1.0"):
            ex, ey = abs(float(r["end_x"])), abs(float(r["end_y"]))
            if ex >= 29.5 or ey >= 29.5: edge += 1
            else: real += 1
    d = sum(float(r["distance_m"]) for r in rs) / n
    s = sum(float(r["sway"]) for r in rs) / n
    return n, 100 * real / n, edge, d, s
print("jatuh asli % | keluar tepi (jumlah) | jarak m | sway")
print("%-26s" % "medan" + "".join("%-30s" % l for l in labels))
for t in terrs:
    line = "%-26s" % t
    for l in labels:
        rs = rows.get((l, t))
        if not rs: line += "%-30s" % "-"; continue
        n, fr, e, d, s = stat(rs)
        line += "%-30s" % ("%5.1f%% e=%d d=%.1f s=%.2f (n=%d)" % (fr, e, d, s, n))
    print(line)
