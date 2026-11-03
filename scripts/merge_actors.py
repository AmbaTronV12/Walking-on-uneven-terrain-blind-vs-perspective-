import os, torch
A = "logs/rsl_rl/k1_velocity/"
ld = lambda p: torch.load(A + p, map_location="cpu", weights_only=False)
ck7 = ld("2026-10-28_12-23-06/model_9998.pt")
ck10 = ld("2026-10-30_23-17-57/model_9998.pt")
init = ld("2026-10-30_perceptive-init-from-flat/model_9998.pt")
EPS = 1e-2
cols = (init["actor_state_dict"]["mlp.0.weight"].abs().sum(0) > 0).nonzero().squeeze(1)
print("kolom blind di 265:", len(cols), "| awal/akhir:", cols[:3].tolist(), cols[-3:].tolist())
assert len(cols) == 78, "jumlah kolom blind bukan 78, berhenti"
a7, a10 = ck7["actor_state_dict"], ck10["actor_state_dict"]
m7, s7 = a7["obs_normalizer._mean"][0], a7["obs_normalizer._std"][0]
m10, s10 = a10["obs_normalizer._mean"][0], a10["obs_normalizer._std"][0]
W7 = a7["mlp.0.weight"]
W7e = torch.zeros(512, 265)
W7e[:, cols] = W7 * ((s10[cols] + EPS) / (s7 + EPS))
b7e = a7["mlp.0.bias"] + W7 @ ((m10[cols] - m7) / (s7 + EPS))
run7_in10 = dict(a7)
run7_in10["mlp.0.weight"], run7_in10["mlp.0.bias"] = W7e, b7e
for alpha in (0.0, 0.25, 0.5, 0.75):
    out = dict(a10)  # normalizer Run 10
    for k in ("mlp.0.weight", "mlp.0.bias", "mlp.2.weight", "mlp.2.bias", "mlp.4.weight",
              "mlp.4.bias", "mlp.6.weight", "mlp.6.bias", "distribution.std_param"):
        out[k] = (1 - alpha) * run7_in10[k] + alpha * a10[k]
    ck = dict(ck10)
    ck["actor_state_dict"] = out
    d = A + f"2026-11-03_merge-a{alpha}"
    os.makedirs(d, exist_ok=True)
    torch.save(ck, d + "/model_9998.pt")
    print("disimpan:", d)
