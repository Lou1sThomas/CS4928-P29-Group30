"""Event B: run check_pr_dependencies.py over every case in an evaluation file.

Reads repo, pull_number, filename and the method name (first identifier before
'(' in source_code) for each case, checks each distinct (PR, file, method) once,
and writes one summary row per case.

Usage:
  python3 flag_sample_dependencies.py m2_data/data/m2/eval_raw.csv results/event_b/flags_m2.csv
"""
import csv, json, os, re, subprocess, sys

csv.field_size_limit(sys.maxsize)
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    src, out = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))[:limit]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    cache, summary = {}, []
    for r in rows:
        method = re.search(r"(\w+)\s*\(", r["source_code"]).group(1)
        key = (r["repo"], r["pull_number"], r["filename"], method)
        if key not in cache:
            js = os.path.join(os.path.dirname(out), "json",
                              f"{r['repo'].replace('/', '__')}_{r['pull_number']}_{method}.json")
            subprocess.run([sys.executable, os.path.join(HERE, "check_pr_dependencies.py"),
                            "--repo", r["repo"], "--pr", r["pull_number"], "--file", r["filename"],
                            "--method", method, "--out", js], check=True)
            cache[key] = json.load(open(js))
        d = cache[key]
        summary.append({"Record_id": r["Record_id"], "repo": r["repo"], "pull_number": r["pull_number"],
                        "filename": r["filename"], "method": method,
                        "java_files_changed": d["java_files_changed"],
                        "dependency_flag": d["dependency_flag"],
                        "matched_names": "; ".join(f"{n['file'].split('/')[-1]}: {', '.join(n['used_by_method'])}"
                                                   for n in d["neighbours"] if n["used_by_method"]),
                        "manual_verdict": ""})
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    print(f"{len(summary)} cases, {sum(s['dependency_flag'] for s in summary)} flagged -> {out}")

if __name__ == "__main__":
    main()
