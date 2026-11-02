import os
import torch

SRC = "logs/rsl_rl/k1_velocity/2026-10-28_12-23-06/model_9998.pt"
DST_DIR = "logs/rsl_rl/k1_velocity/2026-10-28_19-30-00_perceptive-init"
N = 187  # height_scan dims
POS = 78  # actor: appended at end; critic: inserted after the 78 base dims


def insert_cols(t, pos, n, fill):
    shape = list(t.shape)
    shape[-1] = n
    new = torch.full(shape, fill, dtype=t.dtype)
    return torch.cat([t[..., :pos], new, t[..., pos:]], dim=-1)


def expand_group(sd):
    out = dict(sd)
    out["mlp.0.weight"] = insert_cols(sd["mlp.0.weight"], POS, N, 0.0)
    out["obs_normalizer._mean"] = insert_cols(sd["obs_normalizer._mean"], POS, N, 0.0)
    out["obs_normalizer._var"] = insert_cols(sd["obs_normalizer._var"], POS, N, 1.0)
    out["obs_normalizer._std"] = insert_cols(sd["obs_normalizer._std"], POS, N, 1.0)
    return out


ck = torch.load(SRC, map_location="cpu", weights_only=False)
assert ck["actor_state_dict"]["mlp.0.weight"].shape == (512, 78)
assert ck["critic_state_dict"]["mlp.0.weight"].shape == (512, 90)
ck["actor_state_dict"] = expand_group(ck["actor_state_dict"])
ck["critic_state_dict"] = expand_group(ck["critic_state_dict"])

n_opt = 0
for st in ck["optimizer_state_dict"]["state"].values():
    for key in ("exp_avg", "exp_avg_sq"):
        t = st.get(key)
        if t is not None and tuple(t.shape) in ((512, 78), (512, 90)):
            st[key] = insert_cols(t, POS, N, 0.0)
            n_opt += 1

os.makedirs(DST_DIR, exist_ok=True)
torch.save(ck, os.path.join(DST_DIR, "model_9998.pt"))
print("actor mlp.0.weight :", tuple(ck["actor_state_dict"]["mlp.0.weight"].shape))
print("critic mlp.0.weight:", tuple(ck["critic_state_dict"]["mlp.0.weight"].shape))
print("tensor optimizer diperluas:", n_opt, "(harus 4)")
print("disimpan di", DST_DIR)
