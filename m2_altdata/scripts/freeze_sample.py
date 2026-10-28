"""
Step 2 - Freeze the bounded sample (P29 sampling rule, per-project adaptation).

P29 rule: take the first 12 eligible items in stable order (case ID, then file path,
then chronological ID). Adaptation recorded in DEVIATION_02: the same stable order is
applied WITHIN each project and the first 4 eligible cases are taken from each of the
3 projects, so the 12 cases span more than one Java project (Abdul's condition, and
needed for RQ2). Stable order = PR number, then file path, then comment time, then comment ID.

If a project has fewer than 4 eligible cases, all of them are used, the shortfall is
recorded, and it is filled from the reserve project(s) in the same stable order.

Output: data/sample_ids.csv, data/cases.jsonl, data/sample_freeze.json (with SHA-256 hashes)
Run this BEFORE any model call. Commit and tag the outputs straight away.
"""
import csv
import datetime as dt
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))


def key(c):
    return (c["pr_number"], c["file_path"], c["comment_created_at"], c["comment_id"])


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    eligible = [json.loads(l) for l in open(os.path.join(ROOT, "data", "eligible_cases.jsonl"), encoding="utf-8")]
    quota = CFG["cases_per_project"]
    chosen, notes = [], []
    for repo in CFG["projects"]:
        mine = sorted([c for c in eligible if c["project"] == repo], key=key)[:quota]
        if len(mine) < quota:
            notes.append(f"{repo}: only {len(mine)} eligible cases; shortfall {quota - len(mine)}")
        chosen.extend(mine)
    need = quota * len(CFG["projects"]) - len(chosen)
    for repo in CFG["reserve_projects"]:
        if need <= 0:
            break
        extra = sorted([c for c in eligible if c["project"] == repo], key=key)[:need]
        if extra:
            notes.append(f"reserve {repo}: {len(extra)} cases added to fill shortfall")
        chosen.extend(extra)
        need -= len(extra)
    if need > 0:
        notes.append(f"total sample is {len(chosen)} (< 12); all eligible cases used, as the P29 rule allows")

    with open(os.path.join(ROOT, "data", "cases.jsonl"), "w", encoding="utf-8") as f:
        for c in chosen:
            f.write(json.dumps(c) + "\n")
    cols = ["case_id", "project", "pr_number", "file_path", "comment_created_at", "comment_id",
            "comment_url", "original_commit", "revised_commit", "method_long_name_before"]
    with open(os.path.join(ROOT, "data", "sample_ids.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(chosen)

    freeze = {"frozen_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "n_cases": len(chosen), "notes": notes,
              "sha256": {p: sha256(os.path.join(ROOT, "data", p))
                         for p in ["cases.jsonl", "sample_ids.csv", "candidates.csv"]}}
    json.dump(freeze, open(os.path.join(ROOT, "data", "sample_freeze.json"), "w"), indent=2)
    print(f"Frozen {len(chosen)} cases -> data/sample_ids.csv")
    for n in notes:
        print("NOTE:", n)
    for c in chosen:
        print(f"  {c['case_id']}  {c['file_path']}  {c['method_long_name_before'][:60]}")


if __name__ == "__main__":
    main()
