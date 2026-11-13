"""Complete-reference check (the Week 9 / M4 design decision, re-implemented for Event B).

Re-scores SAVED T5 predictions for the raw and cleaned conditions against ONE shared,
complete reference per case. No new predictions are generated; the original scorer and
its results are left untouched.

Reference : the case's multiline `after` method from the authors' P1 output (before any
            flattening). Java comments are removed while line breaks still exist
            (// to end of line, /* ... */), skipping anything inside string or char literals.
            Whitespace is then collapsed to single spaces. The reference is NOT tokenized
            or truncated.
Predictions: the saved `raw_predictions` (model output before the authors' cleaning helper),
            whitespace collapsed only. Comments in predictions are kept.
Match     : EXM@1 / EXM@10 = first / any of the ten candidates equals the reference.
Source check (optional, --pool): the flattened multiline reference must appear inside the
            flattened `file_content_after` of the same review comment in the mined pool.

Usage (build targets from a pipeline run):
  python complete_reference_check.py --chunk <Chunk_0000 dir> --eval <eval_raw.csv> \
      --pred-raw <predictions_raw.csv> --pred-cleaned <predictions_cleaned.csv> \
      --out <out dir> [--pool <sample*_raw.csv>]
Usage (reuse an existing multiline_targets.csv, e.g. to verify against Event A / M2):
  python complete_reference_check.py --targets <multiline_targets.csv> \
      --pred-raw ... --pred-cleaned ... --out <out dir>
"""
import argparse, ast, csv, json, os, sys

csv.field_size_limit(sys.maxsize)
P1_FILE = "Step1.1_Paper2_Gerrit_ProjectLevel_MethodLevel_SizeFiltered.csv"


def strip_java_comments(src):
    """Remove // and /* */ comments outside string/char literals; keep line breaks."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'":                              # string or char literal: copy verbatim
            q = c; out.append(c); i += 1
            while i < n:
                out.append(src[i])
                if src[i] == "\\" and i + 1 < n:
                    out.append(src[i + 1]); i += 2; continue
                if src[i] == q or src[i] == "\n":
                    i += 1; break
                i += 1
        elif src.startswith("//", i):               # line comment: drop to end of line
            j = src.find("\n", i)
            i = n if j == -1 else j
        elif src.startswith("/*", i):               # block comment: replace with a space
            j = src.find("*/", i + 2)
            i = n if j == -1 else j + 2
            out.append(" ")
        else:
            out.append(c); i += 1
    return "".join(out)


def flat(s):
    return " ".join(str(s).split())


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def build_targets(chunk, eval_csv):
    p1 = {r["Record_id"]: r for r in read(os.path.join(chunk, P1_FILE))}
    rows = []
    for e in read(eval_csv):
        m = p1.get(e["Record_id"])
        if m is None:
            sys.exit(f"Record_id {e['Record_id']} (rank {e['p29_rank']}) not found in {P1_FILE}")
        keep = ["p29_rank", "Record_id", "repo", "comment_id", "pull_number", "filename", "created_at", "html_url"]
        rows.append({**{k: e.get(k, "") for k in keep}, "after": m["after"]})
    return rows


def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk"); ap.add_argument("--eval"); ap.add_argument("--targets")
    ap.add_argument("--pred-raw", required=True); ap.add_argument("--pred-cleaned", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--pool")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    if a.targets:
        targets = read(a.targets)
    elif a.chunk and a.eval:
        targets = build_targets(a.chunk, a.eval)
        write(os.path.join(a.out, "multiline_targets.csv"), targets)
    else:
        sys.exit("give --targets, or --chunk and --eval")

    refs = []
    for t in targets:
        refs.append({**t, "complete_reference": flat(strip_java_comments(t["after"]))})
    write(os.path.join(a.out, "complete_references.csv"), refs)
    ref_by_rank = {r["p29_rank"]: r for r in refs}

    if a.pool:                                       # target/source check
        pool = {r["comment_id"]: r for r in read(a.pool)}
        checks = []
        for r in refs:
            p = pool.get(r["comment_id"])
            ok = bool(p) and flat(r["after"]) in flat(p.get("file_content_after", ""))
            checks.append({"p29_rank": r["p29_rank"], "comment_id": r["comment_id"], "method_found_in_saved_source": ok})
        write(os.path.join(a.out, "target_source_checks.csv"), checks)
        print("source check:", sum(c["method_found_in_saved_source"] for c in checks), "/", len(checks), "found in saved final files")

    scores, totals = [], {}
    for cond, path in (("raw", a.pred_raw), ("cleaned", a.pred_cleaned)):
        hits1 = hits10 = 0
        for p in read(path):
            ref = ref_by_rank[p["p29_rank"]]["complete_reference"]
            preds = [flat(x) for x in ast.literal_eval(p["raw_predictions"])]
            first = next((i + 1 for i, x in enumerate(preds) if x == ref), None)
            e1, e10 = first == 1, first is not None and first <= 10
            hits1 += e1; hits10 += e10
            scores.append({"condition": cond, "p29_rank": p["p29_rank"], "comment_id": p["comment_id"],
                           "complete_reference_EXM1": e1, "complete_reference_EXM10": e10,
                           "first_matching_rank": first or "", "reference": ref,
                           "normalized_predictions": json.dumps(preds)})
        totals[cond] = (hits1, hits10, len(read(path)))
    write(os.path.join(a.out, "complete_reference_scores.csv"), scores)

    for cond, (h1, h10, n) in totals.items():
        matched = [s["p29_rank"] + "@" + str(s["first_matching_rank"]) for s in scores
                   if s["condition"] == cond and s["complete_reference_EXM10"]]
        print(f"{cond:8s} EXM@1 {h1}/{n}  EXM@10 {h10}/{n}  matches (rank@candidate): {', '.join(matched) or '-'}")


if __name__ == "__main__":
    main()
