"""M2: compare RAW vs CLEANED predictions on the fixed 12-case evaluation set.

Copy case (rule fixed before results, 2026-10-28): the gold target equals the model input
code once <START>/<END> markers are removed and both are passed through the authors'
cleaning_model_output + to_single_line (loaded verbatim from their T5 script).
Paired test on EXM@10: exact McNemar (binomial on discordant pairs), two-sided.

Usage: python compare_raw_clean.py <authors FineTuning_and_Testing.py> <results dir>
"""
import ast, re, sys, json, unicodedata, unidecode
from math import comb
import pandas as pd

script, rdir = sys.argv[1:3]
ns = {"re": re, "unicodedata": unicodedata, "unidecode": unidecode}
for node in ast.parse(open(script, encoding="utf-8").read()).body:
    if isinstance(node, ast.FunctionDef) and node.name in {"format_content", "cleaning_model_output", "to_single_line"}:
        exec(compile(ast.Module([node], []), script, "exec"), ns)
norm = lambda s: ns["to_single_line"](ns["cleaning_model_output"](re.sub(r"<START>|<END>", " ", str(s))))

raw = pd.read_csv(f"{rdir}/predictions_raw.csv")
cln = pd.read_csv(f"{rdir}/predictions_cleaned.csv")
assert list(raw.comment_id) == list(cln.comment_id), "evaluation sets differ"

def code_in(model_input):
    return model_input.split("<code>", 1)[1].rsplit("</code>", 1)[0]

per = pd.DataFrame({
    "p29_rank": raw.p29_rank, "repo": raw.repo, "comment_id": raw.comment_id,
    "copy_case": [norm(code_in(i)) == g for i, g in zip(raw.model_input, raw.gold)],
    "raw_EXM1": raw.EXM1, "clean_EXM1": cln.EXM1, "raw_EXM10": raw.EXM10, "clean_EXM10": cln.EXM10,
    "raw_LevRatio": raw.Lev_Ratio.round(3), "clean_LevRatio": cln.Lev_Ratio.round(3),
    "raw_input_tokens": raw.input_tokens, "clean_input_tokens": cln.input_tokens,
    "raw_truncated": raw.input_truncated, "clean_truncated": cln.input_truncated,
    "raw_top1_is_copy": [json.loads(p)[0] == norm(code_in(i)) for p, i in zip(raw.predictions, raw.model_input)],
    "clean_top1_is_copy": [json.loads(p)[0] == norm(code_in(i)) for p, i in zip(cln.predictions, cln.model_input)],
})
per.to_csv(f"{rdir}/per_case_comparison.csv", index=False)

def mcnemar(a, b):
    b01 = int(((~a) & b).sum()); b10 = int((a & (~b)).sum()); n = b01 + b10
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(0, min(b01, b10) + 1)) / 2 ** n)
    return b10, b01, p

rows = []
for subset, d in (("all 12", per), ("non-copy cases", per[~per.copy_case]), ("copy cases", per[per.copy_case])):
    raw_only, clean_only, p = mcnemar(d.raw_EXM10, d.clean_EXM10)
    rows.append({"subset": subset, "n": len(d),
                 "raw_EXM@1_%": round(100 * d.raw_EXM1.mean(), 1), "clean_EXM@1_%": round(100 * d.clean_EXM1.mean(), 1),
                 "raw_EXM@10_%": round(100 * d.raw_EXM10.mean(), 1), "clean_EXM@10_%": round(100 * d.clean_EXM10.mean(), 1),
                 "raw_LevRatio": round(d.raw_LevRatio.mean(), 3), "clean_LevRatio": round(d.clean_LevRatio.mean(), 3),
                 "EXM@10 only raw": raw_only, "EXM@10 only cleaned": clean_only, "McNemar_exact_p": round(p, 3)})
summary = pd.DataFrame(rows)
summary.to_csv(f"{rdir}/summary.csv", index=False)
print(summary.to_string(index=False)); print()
print(per[["p29_rank", "repo", "copy_case", "raw_EXM10", "clean_EXM10", "raw_LevRatio", "clean_LevRatio", "raw_truncated", "clean_truncated", "raw_top1_is_copy", "clean_top1_is_copy"]].to_string(index=False))
