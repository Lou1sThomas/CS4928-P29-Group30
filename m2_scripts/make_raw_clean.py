"""Build the fixed M2 evaluation set in two representations and apply the P29 rule.

RAW     = the authors' P1 output for the T5/S2 setting
          (Step1.1_Paper2_..._SizeFiltered.csv: method extraction + 512-word size filter).
          Model input fields: before_marked_flat (code), comment, after_flat (target).
CLEANED = the same P1 records passed through the authors' own S2 P4 (comment cleaning)
          code, called exactly as Preprocessing_Pipeline.py lines 451-475 call it:
          Analyzer2.analyze_wo_abs() + info_for_cleaning_paper2(), keep rows with a
          non-empty, relevant cleaned comment, re-flatten code, then the 512-word filter.
          Model input fields: before_marked_flat, cleaned_comment_wo_abs, after_flat.
          (P4 applied directly after P1, i.e. the paper's isolated P1+P4 configuration,
          but with the cleaned text fed to the model so the representation differs.)

ELIGIBLE = present in both RAW and CLEANED with non-empty code, comment and target,
           so the evaluation set is identical for both representations.
P29 RULE = sort eligible items by case ID (GitHub review comment id), then file path,
           then chronological ID (comment created_at); take the first 12.

Run from inside the run folder's Cumulative_code/ directory (needs ./utils/):
  python make_raw_clean.py <pipeline input csv> <chunk output dir> <out dir>
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.getcwd())
from Analyzer2 import Analyzer2

def token_limit_filter(df, limit, cols):  # identical logic to Preprocessing_Pipeline.token_limit_filter (paper 2 => 512)
    def ok(row):
        return all(len((str(row[c]) if pd.notnull(row[c]) else "").split()) <= limit for c in cols)
    mask = df.apply(ok, axis=1) if len(df) else pd.Series(dtype=bool)
    return df[mask].reset_index(drop=True)

def nonempty(s):
    return s.notna() & (s.astype(str).str.strip() != "") & (s.astype(str).str.lower() != "nan")

inp, chunk, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
raw_in = pd.read_csv(inp, low_memory=False)              # pipeline assigns Record_id = row index of this file
p1 = pd.read_csv(os.path.join(chunk, "Step1.1_Paper2_Gerrit_ProjectLevel_MethodLevel_SizeFiltered.csv"))
p1_full = pd.read_csv(os.path.join(chunk, "Step1.1_Paper1-2_Gerrit_ProjectLevel_MethodLevel_Preprocessed.csv"))

# ---- CLEANED: authors' P4 code applied to the P1 records ----
a = Analyzer2(p1.copy(), "./utils/idioms.csv")
a.data = a.analyze_wo_abs()
a.info_for_cleaning_paper2()
flags = a.data.copy()
kept = flags[(flags["clean_comment_wo_abs_empty"] == False) & (flags["wo_abs_comment_is_relevant"] == True)].reset_index(drop=True)
m = Analyzer2.apply_cleaning_to_column_safely(kept, "before_marked", "before_marked_clean")
m = Analyzer2.normalize_start_end_tokens(m, "before_marked_clean", "before_marked_tags")
m = Analyzer2.flatten_to_single_line(m, "before_marked_tags", "before_marked_flat")
m = Analyzer2.apply_cleaning_to_column_safely(m, "after", "after_clean")
m = Analyzer2.flatten_to_single_line(m, "after_clean", "after_flat")
clean = token_limit_filter(m, 512, ["before_marked_flat", "after_flat"])

# ---- attach traceable identifiers ----
meta = raw_in.reset_index().rename(columns={"index": "Record_id"})[
    ["Record_id", "repo", "comment_id", "pull_number", "filename", "created_at", "html_url"]]
def ids(df):
    return df.merge(meta, on="Record_id", how="left")

raw_v = ids(p1)[["Record_id", "repo", "comment_id", "pull_number", "filename", "created_at", "html_url",
                 "before_marked_flat", "comment", "after_flat"]].rename(
    columns={"before_marked_flat": "source_code", "comment": "review_comment", "after_flat": "target_code"})
clean_v = ids(clean)[["Record_id", "repo", "comment_id", "pull_number", "filename", "created_at", "html_url",
                      "before_marked_flat", "cleaned_comment_wo_abs", "after_flat"]].rename(
    columns={"before_marked_flat": "source_code", "cleaned_comment_wo_abs": "review_comment", "after_flat": "target_code"})

# ---- eligibility + exclusion reasons ----
ok_raw = raw_v[nonempty(raw_v.source_code) & nonempty(raw_v.review_comment) & nonempty(raw_v.target_code)]
ok_clean = clean_v[nonempty(clean_v.source_code) & nonempty(clean_v.review_comment) & nonempty(clean_v.target_code)]
elig_ids = set(ok_raw.Record_id) & set(ok_clean.Record_id)

excl = []
p1_ids, p1_full_ids = set(p1.Record_id), set(p1_full.Record_id)
flag_by = flags.set_index("Record_id")
for rid, r in meta.iterrows():
    rid = r.Record_id
    if rid in elig_ids:
        continue
    if rid not in p1_full_ids:
        why = "P1: no method-level record extracted (left-side comment, comment outside a method, or NaN/duplicate removal)"
    elif rid not in p1_ids:
        why = "P1: method + comment over the 512-word size filter"
    elif rid not in set(ok_raw.Record_id):
        why = "raw: empty code, comment or target after P1"
    elif rid in flag_by.index and bool(flag_by.loc[rid, "clean_comment_wo_abs_empty"]):
        why = "P4: cleaned comment is empty"
    elif rid in flag_by.index and not bool(flag_by.loc[rid, "wo_abs_comment_is_relevant"]):
        why = "P4: comment judged irrelevant (isCommentRelevant = False)"
    elif rid not in set(clean.Record_id):
        why = "P4: over the 512-word size filter after cleaning, or row skipped by analyze_wo_abs"
    else:
        why = "cleaned: empty code, comment or target"
    excl.append({**r.to_dict(), "reason": why})

# ---- P29 ordering and selection ----
order = ["comment_id", "filename", "created_at"]
elig = ok_raw[ok_raw.Record_id.isin(elig_ids)].sort_values(order, kind="mergesort").reset_index(drop=True)
elig.insert(0, "p29_rank", range(1, len(elig) + 1))
sel = elig.head(12)
note = "" if len(elig) >= 12 else f"ONLY {len(elig)} ELIGIBLE ITEMS - ALL USED (P29 rule)"

sel[["p29_rank", "Record_id", "repo", "comment_id", "pull_number", "filename", "created_at", "html_url"]].to_csv(os.path.join(out, "sample_ids.csv"), index=False)
elig[["p29_rank", "Record_id", "repo", "comment_id", "pull_number", "filename", "created_at", "html_url"]].to_csv(os.path.join(out, "eligible_all.csv"), index=False)
pd.DataFrame(excl).to_csv(os.path.join(out, "excluded_rows.csv"), index=False)
for name, v in (("raw", raw_v), ("cleaned", clean_v)):
    v.set_index("Record_id").loc[sel.Record_id].reset_index().assign(p29_rank=sel.p29_rank.values) \
     .to_csv(os.path.join(out, f"eval_{name}.csv"), index=False)
print(f"mined={len(meta)} P1(raw)={len(raw_v)} cleaned={len(clean_v)} eligible={len(elig)} selected={len(sel)} excluded={len(excl)} {note}")
print(sel[["p29_rank", "repo", "comment_id", "filename"]].to_string(index=False))
