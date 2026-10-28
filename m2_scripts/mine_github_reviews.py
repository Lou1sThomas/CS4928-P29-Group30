"""Mine raw GitHub PR review comments in the input schema of the authors'
preprocessing pipeline (Analyzer1, data_type='GitHub').

Contingency route for M2: the authors' raw inputs (SplittedData, NewGitHubData)
were never published, so we rebuild a small raw sample the same way the paper
built its New Test (newly mined GitHub code reviews).

Mining choices (deviations, record them in the M2 notes):
  * Java files only (*.java), merged PRs only.
  * file_content_before = file at the PR base commit
  * file_content_while  = file at the commit the comment was made on (original_commit_id)
  * file_content_after  = file at the PR's final head commit (the revised code)
  * Records are ordered by comment creation time; "first N" = first N rows.

Usage:
  python3 mine_github_reviews.py --sample A --start 2020-09-01 --end 2021-08-31 \
      --repos apache/commons-lang apache/commons-io --per-repo 35 --out ../data
Set GITHUB_TOKEN (read-only token) to raise the API limit from 60 to 5000 calls/hour.
"""
import argparse, csv, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
TOKEN = os.environ.get("GITHUB_TOKEN")
calls = 0

def get(url, raw=False):
    global calls
    req = urllib.request.Request(url, headers={"User-Agent": "cs4928-m2-miner"})
    if not raw:
        req.add_header("Accept", "application/vnd.github+json")
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                if not raw:
                    calls += 1
                    rem = r.headers.get("X-RateLimit-Remaining")
                    if rem is not None and int(rem) == 0:
                        reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
                        wait = max(0, reset - time.time()) + 5
                        print(f"  rate limit reached, sleeping {wait/60:.1f} min", flush=True)
                        time.sleep(wait)
                data = r.read()
                return data.decode("utf-8", errors="replace") if raw else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 403 and not raw:
                reset = int(e.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(0, reset - time.time()) + 5
                print(f"  403 (rate limit), sleeping {wait/60:.1f} min", flush=True)
                time.sleep(wait)
                continue
            raise
        except urllib.error.URLError:
            time.sleep(5)
    return None

def iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def mine_repo(repo, start, end, cap, pr_cache):
    rows, page = [], 1
    while len(rows) < cap:
        url = (f"{API}/repos/{repo}/pulls/comments?sort=created&direction=asc"
               f"&since={start.strftime('%Y-%m-%dT%H:%M:%SZ')}&per_page=100&page={page}")
        batch = get(url)
        if not batch:
            break
        for c in batch:
            created = iso(c["created_at"])
            if created < start:
                continue
            if created > end:
                return rows
            if not c["path"].endswith(".java"):
                continue
            num = int(c["pull_request_url"].rsplit("/", 1)[1])
            if num not in pr_cache:
                pr_cache[num] = get(f"{API}/repos/{repo}/pulls/{num}")
            pr = pr_cache[num]
            if not pr or not pr.get("merged_at"):
                continue
            path = c["path"]
            rows.append({
                "repo": repo,
                "comment_id": c["id"],
                "html_url": c["html_url"],
                "created_at": c["created_at"],
                "updated_at": c["updated_at"],
                "pull_id": pr["id"],
                "pull_number": num,
                "filename": path,
                "message": c["body"],
                "user_id": c["user"]["id"] if c.get("user") else None,
                "owner_id": pr["user"]["id"] if pr.get("user") else None,
                "side": c.get("side"),
                "original_line": c.get("original_line"),
                "original_start_line": c.get("original_start_line"),
                "original_commit_id": c["original_commit_id"],
                "base_sha": pr["base"]["sha"],
                "head_sha": pr["head"]["sha"],
                "diff_hunk": c.get("diff_hunk"),
                "file_content_before": get(f"{RAW}/{repo}/{pr['base']['sha']}/{path}", raw=True),
                "file_content_while": get(f"{RAW}/{repo}/{c['original_commit_id']}/{path}", raw=True),
                "file_content_after": get(f"{RAW}/{repo}/{pr['head']['sha']}/{path}", raw=True),
            })
            print(f"  {repo} #{num} comment {c['id']} ({len(rows)}/{cap}) api_calls={calls}", flush=True)
            if len(rows) >= cap:
                return rows
        page += 1
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--repos", nargs="+", required=True)
    ap.add_argument("--per-repo", type=int, default=35)
    ap.add_argument("--out", default="../data")
    a = ap.parse_args()
    start = datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(a.end).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
    rows = []
    for repo in a.repos:
        print(f"Mining {repo} {a.start}..{a.end}", flush=True)
        rows += mine_repo(repo, start, end, a.per_repo, {})
    os.makedirs(os.path.join(a.out, "parts"), exist_ok=True)
    csv.field_size_limit(sys.maxsize)
    for repo in a.repos:
        part = [r for r in rows if r["repo"] == repo]
        path = os.path.join(a.out, "parts", f"sample{a.sample}__{repo.replace('/', '__')}.csv")
        if part:
            with open(path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(part[0].keys()))
                w.writeheader(); w.writerows(part)
        print(f"Wrote {len(part)} records to {path}; api_calls={calls}")
    print("Run combine_samples.py to build sample<S>_raw.csv and sample_ids.csv")

if __name__ == "__main__":
    main()
