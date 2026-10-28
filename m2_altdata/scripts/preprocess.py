"""
Step 3 - Build the three representations of every frozen case.

  raw : original method + review comment + revised method, exactly as mined
  A   : authors' Analyzer2.removeComments applied to the original AND revised method
        (code-comment removal, as the authors apply it to both 'before' and 'after')
  B   : authors' Analyzer2.clean_comment_without_abstraction applied to the review comment
        (review-comment cleaning); code left as mined

Only text is transformed. No case is dropped: if cleaning empties a comment the case is
kept and flagged, so all three conditions are scored on the same fixed 12 cases.

Usage: python scripts/preprocess.py --analyzer2 "C:/path/to/authors-repo/Preprocessing/Cumulative_code/Analyzer2.py"
Output: data/conditions.jsonl, data/preprocess_log.json
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from authors_steps import load_authors_analyzer2, EXPECTED_COMMIT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyzer2", required=True, help="path to authors' Cumulative_code/Analyzer2.py")
    args = ap.parse_args()
    A2, a2_hash = load_authors_analyzer2(os.path.abspath(args.analyzer2))

    os.chdir(ROOT)  # authors' code opens ./utils/stop-words-english.txt relative to the working folder
    idioms = os.path.join("utils", "idioms.csv")
    cases = [json.loads(l) for l in open(os.path.join("data", "cases.jsonl"), encoding="utf-8")]

    rows, flags = [], []
    for c in cases:
        base = {"case_id": c["case_id"], "project": c["project"],
                "commented_line_text": c["commented_line_text"]}
        rows.append({**base, "condition": "raw", "input_code": c["original_code"],
                     "input_comment": c["review_comment"], "target_code": c["revised_code"]})
        rows.append({**base, "condition": "A_code_comment_removal",
                     "input_code": A2.removeComments(c["original_code"]),
                     "input_comment": c["review_comment"],
                     "target_code": A2.removeComments(c["revised_code"])})
        cleaned = A2.clean_comment_without_abstraction(c["review_comment"], idioms)
        if not cleaned.strip():
            flags.append(f"{c['case_id']}: review comment empty after cleaning (case kept)")
        rows.append({**base, "condition": "B_review_comment_cleaning", "input_code": c["original_code"],
                     "input_comment": cleaned, "target_code": c["revised_code"]})

    with open(os.path.join("data", "conditions.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    json.dump({"run_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
               "authors_commit_expected": EXPECTED_COMMIT,
               "analyzer2_path": os.path.abspath(args.analyzer2), "analyzer2_sha256": a2_hash,
               "n_cases": len(cases), "n_rows": len(rows), "flags": flags},
              open(os.path.join("data", "preprocess_log.json"), "w"), indent=2)
    print(f"{len(cases)} cases x 3 conditions = {len(rows)} rows -> data/conditions.jsonl")
    for fl in flags:
        print("FLAG:", fl)


if __name__ == "__main__":
    main()
