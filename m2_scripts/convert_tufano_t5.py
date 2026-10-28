"""Convert Tufano et al. (2022) Mesh-TensorFlow T5-small checkpoint to a PyTorch
(Hugging Face T5ForConditionalGeneration) model, without changing any weight.

Source: Zenodo 10.5281/zenodo.5387856, models.zip ->
        models/T5_pre-trained_new_large_dataset_code&comment-to-code/model.ckpt (global_step 500000)
Architecture read from the checkpoint: T5 v1.0 small (6+6 layers, d_model 512, d_ff 2048,
8 heads, ReLU feed-forward, relative attention bias in block 0 only, 32128-row shared
embedding tied to the output layer).

Usage (two stages, because TensorFlow and PyTorch segfault in one process):
  python convert_tufano_t5.py export <tf checkpoint prefix> <weights.npz>
  python convert_tufano_t5.py build  <weights.npz> <out dir>
Check: every non-optimizer variable in the checkpoint is used exactly once, and every
HF parameter is filled (script stops otherwise).
"""
import sys
import numpy as np

mode, src, out = sys.argv[1:4]
if mode == "export":
    import tensorflow as tf
    reader = tf.train.load_checkpoint(src)
    names = [k for k in reader.get_variable_to_shape_map() if "slot" not in k and k != "global_step"]
    np.savez(out, **{k.replace("/", "|"): reader.get_tensor(k).astype(np.float32) for k in names})
    print(f"exported {len(names)} variables (optimizer slots skipped) to {out}")
    sys.exit(0)

import torch
from transformers import T5Config, T5ForConditionalGeneration
weights = {k.replace("|", "/"): v for k, v in np.load(src).items()}
tf_vars = set(weights)

cfg = T5Config(vocab_size=32128, d_model=512, d_kv=64, d_ff=2048, num_layers=6,
               num_decoder_layers=6, num_heads=8, relative_attention_num_buckets=32,
               dropout_rate=0.0, feed_forward_proj="relu", tie_word_embeddings=True,
               pad_token_id=0, eos_token_id=1, decoder_start_token_id=0)
model = T5ForConditionalGeneration(cfg)
sd = model.state_dict()

def tf_to_hf(name):
    p = name.split("/")
    if p[0] == "shared":
        return "shared.weight", False
    stack = p[0]
    if p[1] == "final_layer_norm":
        return f"{stack}.final_layer_norm.weight", False
    b = int(p[1].split("_")[1]); l = int(p[2].split("_")[1])
    base = f"{stack}.block.{b}.layer.{l}"
    if p[3] == "layer_norm":
        return f"{base}.layer_norm.weight", False
    if p[3] in ("SelfAttention", "EncDecAttention"):
        if p[4] == "relative_attention_bias":
            return f"{base}.{p[3]}.relative_attention_bias.weight", True   # TF [heads, buckets] -> HF [buckets, heads]
        return f"{base}.{p[3]}.{p[4]}.weight", True                          # TF [in, out] -> HF [out, in]
    if p[3] == "DenseReluDense":
        return f"{base}.DenseReluDense.{p[4]}.weight", True
    raise KeyError(name)

filled, used = set(), set()
for name in sorted(tf_vars):
    key, transpose = tf_to_hf(name)
    arr = weights[name]
    if transpose:
        arr = arr.T
    if tuple(sd[key].shape) != arr.shape:
        sys.exit(f"shape mismatch {name} {arr.shape} -> {key} {tuple(sd[key].shape)}")
    sd[key] = torch.from_numpy(np.ascontiguousarray(arr))
    filled.add(key); used.add(name)

tied = {"lm_head.weight", "encoder.embed_tokens.weight", "decoder.embed_tokens.weight"}
missing = set(sd) - filled - tied
if missing or used != tf_vars:
    sys.exit(f"unfilled HF params: {sorted(missing)[:10]} / unused TF vars: {sorted(tf_vars - used)[:10]}")
model.load_state_dict(sd, strict=False)
model.tie_weights()
assert torch.equal(model.lm_head.weight, model.shared.weight)
model.save_pretrained(out)
print(f"converted {len(used)} TF variables -> {len(filled)} HF parameters; saved to {out}")
