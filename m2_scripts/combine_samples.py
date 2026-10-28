"""Combine per-repo mined parts into data/sample<S>_raw.csv and rebuild
data/pool_ids.csv (all mined records; the P29 selection is written by make_raw_clean.py to data/sample_ids.csv). Rows are listed in comment creation order (pool order only; NOT the P29 selection order)."""
import csv, glob, os, sys
from datetime import datetime, timezone
csv.field_size_limit(sys.maxsize)
out = sys.argv[1] if len(sys.argv) > 1 else "../data"
ids = []
for sample in sorted({os.path.basename(p).split("__")[0][6:] for p in glob.glob(f"{out}/parts/sample*__*.csv")}):
    rows = []
    for p in sorted(glob.glob(f"{out}/parts/sample{sample}__*.csv")):
        with open(p, newline="") as f:
            rows += list(csv.DictReader(f))
    rows.sort(key=lambda r: (r["created_at"], int(r["comment_id"])))
    with open(f"{out}/sample{sample}_raw.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    mtime = {}
    for i, r in enumerate(rows, 1):
        ids.append([sample, i, r["repo"], r["comment_id"], r["pull_number"], r["filename"], r["created_at"], r["html_url"]])
    print(f"sample {sample}: {len(rows)} records")
with open(f"{out}/pool_ids.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sample", "pool_order", "repo", "comment_id", "pull_number", "filename", "created_at", "html_url"])
    w.writerows(ids)
