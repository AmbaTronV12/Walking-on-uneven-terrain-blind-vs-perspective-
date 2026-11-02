import sys
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

run_dir = sys.argv[1]
ea = EventAccumulator(run_dir, size_guidance={"scalars": 0})
ea.Reload()
tags = ea.Tags()["scalars"]
keys = ["mean_reward", "mean_episode_length", "terrain_levels/mean",
        "lin_vel_x_max", "error_vel_xy", "fell_over"]
chosen = []
for k in keys:
    chosen += [t for t in tags if k in t][:1]
print("Tag dipakai:", chosen)
series = {t: {e.step: e.value for e in ea.Scalars(t)} for t in chosen}
steps = sorted(series[chosen[0]])
pick = steps[:: max(1, len(steps) // 20)] + [steps[-1]]
print("iter | " + " | ".join(t.split("/")[-1][:14] for t in chosen))
for s in pick:
    row = []
    for t in chosen:
        v = series[t].get(s)
        row.append("   -   " if v is None else f"{v:7.2f}")
    print(f"{s:5d} | " + " | ".join(row))
