import csv, sys
path, env = sys.argv[1], int(sys.argv[2])
rows = [r for r in csv.DictReader(open(path)) if int(r["env"]) == env]
print(1 if any(int(r["fell"]) == 1 and int(r["length_steps"]) >= 150 for r in rows) else 0)
