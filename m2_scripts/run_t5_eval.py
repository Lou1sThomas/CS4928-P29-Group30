"""M2: run the same T5-small model on the RAW and CLEANED representations of the frozen
12-case evaluation set and score them with the authors' evaluation method.

Model     : Tufano et al. (2022) T5 'pre-trained, new large dataset, code&comment-to-code'
            checkpoint, converted by convert_tufano_t5.py (no fine-tuning, no retraining).
Tokenizer : Tufano et al. SentencePiece model (tokenizer.zip, TokenizerModel.model).
Input     : "<code>{source_code}</code><technical_language>{review_comment}</technical_language>"
            (format of the authors' T5Dataset; the six tags are special symbols in the vocabulary).
Decoding  : as the authors' run_test_and_evaluate(): beam search, 10 beams, 10 returned
            sequences, max_length 512, length_penalty 1.0, early_stopping=True.
Scoring   : authors' functions loaded verbatim from Training_and_Testing/T5/Code/FineTuning_and_Testing.py
            (format_content, cleaning_model_output, to_single_line, is_exact_match):
            predictions and gold are decoded, cleaned and flattened the same way;
            EXM@k = any of the top-k predictions equals the gold; Levenshtein = best of the 10.

Usage: python run_t5_eval.py <authors FineTuning_and_Testing.py> <hf model dir> <spm model> \
                             <eval csv> <label> <out dir> [--limit N]
"""
import ast, re, sys, time, json, argparse
import unicodedata, unidecode
import pandas as pd
import torch, Levenshtein
import sentencepiece as spm
from transformers import T5ForConditionalGeneration

ap = argparse.ArgumentParser()
for a in ["authors_script", "model_dir", "spm_model", "eval_csv", "label", "out_dir"]:
    ap.add_argument(a)
ap.add_argument("--limit", type=int, default=None)
args = ap.parse_args()

# ---- load the authors' evaluation helpers verbatim (no re-typing) ----
src = open(args.authors_script, encoding="utf-8").read()
wanted = {"format_content", "cleaning_model_output", "to_single_line", "is_exact_match"}
ns = {"re": re, "unicodedata": unicodedata, "unidecode": unidecode}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in wanted:
        exec(compile(ast.Module([node], []), args.authors_script, "exec"), ns)
assert wanted <= set(ns), f"missing authors' helpers: {wanted - set(ns)}"
cleaning_model_output, to_single_line, is_exact_match = ns["cleaning_model_output"], ns["to_single_line"], ns["is_exact_match"]

torch.manual_seed(0)
torch.set_num_threads(max(1, torch.get_num_threads()))
sp = spm.SentencePieceProcessor(model_file=args.spm_model)
model = T5ForConditionalGeneration.from_pretrained(args.model_dir).eval()
EOS, PAD, MAXLEN, BEAMS = 1, 0, 512, 10

def encode(text):
    ids = sp.encode(str(text))[: MAXLEN - 1] + [EOS]          # truncation to 512 as in the authors' T5Dataset
    return ids

def decode(ids):
    ids = [int(i) for i in ids if int(i) not in (PAD, EOS) and int(i) < sp.get_piece_size()]
    return sp.decode(ids)

df = pd.read_csv(args.eval_csv)
if args.limit:
    df = df.head(args.limit)
rows = []
for i, r in df.iterrows():
    src_text = f"<code>{r.source_code}</code><technical_language>{r.review_comment}</technical_language>"
    ids = torch.tensor([encode(src_text)])
    t0 = time.time()
    with torch.no_grad():
        out = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=True,
                             max_length=MAXLEN, num_beams=BEAMS, num_return_sequences=BEAMS,
                             length_penalty=1.0, early_stopping=True, decoder_start_token_id=PAD)
    raw_preds = [re.sub(r"<extra_id_\d+>", "", decode(g)).strip() for g in out]
    preds = [to_single_line(cleaning_model_output(p)) for p in raw_preds]
    gold = to_single_line(cleaning_model_output(decode(encode(r.target_code))))   # gold goes through the tokenizer, as in the authors' code
    exm = {k: any(is_exact_match(p, gold) for p in preds[:k]) for k in (1, 3, 5, 10)}
    rows.append({"p29_rank": r.p29_rank, "repo": r.repo, "comment_id": r.comment_id, "representation": args.label,
                 "input_tokens": int(ids.shape[1]), "input_truncated": len(sp.encode(src_text)) > MAXLEN - 1,
                 "EXM1": exm[1], "EXM3": exm[3], "EXM5": exm[5], "EXM10": exm[10],
                 "Lev_Dist": min(Levenshtein.distance(p, gold) for p in preds),
                 "Lev_Ratio": max(Levenshtein.ratio(p, gold) for p in preds),
                 "gold": gold, "predictions": json.dumps(preds), "raw_predictions": json.dumps(raw_preds),
                 "model_input": src_text, "seconds": round(time.time() - t0, 1)})
    print(f"[{args.label}] rank {r.p29_rank} EXM@10={exm[10]} Lev_Ratio={rows[-1]['Lev_Ratio']:.3f} ({rows[-1]['seconds']}s)", flush=True)

res = pd.DataFrame(rows)
res.to_csv(f"{args.out_dir}/predictions_{args.label}.csv", index=False)
summary = {"representation": args.label, "n": len(res), **{f"EXM@{k}": round(100 * res[f'EXM{k}'].mean(), 1) for k in (1, 3, 5, 10)},
           "mean_Lev_Ratio": round(res.Lev_Ratio.mean(), 3), "mean_Lev_Dist": round(res.Lev_Dist.mean(), 1)}
print(json.dumps(summary))
