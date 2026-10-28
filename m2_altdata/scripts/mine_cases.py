"""
Step 1 - Mine candidate code-review cases from GitHub pull requests.

For each project in config.json this script:
  1. lists merged PRs in the frozen date window, oldest PR number first;
  2. downloads each PR, its inline review comments and its commits (raw JSON saved);
  3. for every review comment, applies the frozen eligibility rules in order and
     records the FIRST rule that fails (or "ELIGIBLE");
  4. for eligible comments, saves the full source file before the comment and the
     full source file at the first later commit that changed the commented method.

It stops scanning a project once it has finished the PR in which the target number of
eligible cases was reached, so no lower-numbered PR is ever skipped.
Everything downloaded is cached under data/github_raw/, so re-running costs no extra API calls.

Usage (from the p29_m2 folder):
    set GITHUB_TOKEN=ghp_xxx          (Windows cmd)   |   $env:GITHUB_TOKEN="ghp_xxx" (PowerShell)
    python scripts/mine_cases.py
Output: data/candidates.csv  (every comment examined, with its eligibility result)
"""
import csv
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import lizard

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
RAW = os.path.join(ROOT, "data", "github_raw")
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()


# --------------------------------------------------------------------------- GitHub access
def _request(url, accept):
    headers = {"Accept": accept, "User-Agent": "CS4928-P29-group30",
               "X-GitHub-Api-Version": "2022-11-28"}
    if TOKEN and url.startswith(API):
        headers["Authorization"] = f"Bearer {TOKEN}"
    while True:
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            hdrs = dict(e.headers)
            if e.code in (403, 429) and (hdrs.get("X-RateLimit-Remaining") == "0" or "Retry-After" in hdrs):
                reset = int(hdrs.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(int(hdrs.get("Retry-After", 0)), reset - int(time.time())) + 2
                print(f"  rate limit reached, waiting {wait}s ...", flush=True)
                time.sleep(wait)
                continue
            return e.code, e.read(), hdrs


def cache_path(*parts):
    p = os.path.join(RAW, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def get_json(url, cache_file, paginate=False):
    """GET JSON (all pages if paginate), saving the raw responses to cache_file."""
    if os.path.exists(cache_file):
        return json.load(open(cache_file, encoding="utf-8"))
    out, pages, next_url = [], [], url
    while next_url:
        status, body, hdrs = _request(next_url, "application/vnd.github+json")
        if status != 200:
            raise RuntimeError(f"GitHub API {status} for {next_url}: {body[:300]!r}")
        data = json.loads(body)
        pages.append({"url": next_url, "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "body": data})
        if not paginate:
            out = data
            break
        out.extend(data["items"] if isinstance(data, dict) and "items" in data else data)
        next_url = None
        for part in hdrs.get("Link", "").split(","):
            if 'rel="next"' in part:
                next_url = part[part.find("<") + 1: part.find(">")]
    json.dump({"pages": pages, "data": out}, open(cache_file, "w", encoding="utf-8"), indent=1)
    return {"pages": pages, "data": out}


def get_file(repo, path, sha):
    """Full source file at a commit, from raw.githubusercontent.com. Returns (text or None, local_path)."""
    safe = path.replace("/", "__")
    local = cache_path(repo.replace("/", "__"), "files", sha[:12], safe)
    missing_marker = local + ".MISSING"
    if os.path.exists(local):
        return open(local, encoding="utf-8", errors="replace").read(), local
    if os.path.exists(missing_marker):
        return None, local
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/{urllib.parse.quote(path)}"
    status, body, _ = _request(url, "text/plain")
    if status != 200:
        open(missing_marker, "w").write(str(status))
        return None, local
    open(local, "wb").write(body)
    return body.decode("utf-8", errors="replace"), local


# --------------------------------------------------------------------------- method helpers (P1)
def functions(code, path):
    return lizard.analyze_file.analyze_source_code(os.path.basename(path), code).function_list


def method_at_line(code, path, line):
    """Innermost method containing the line (authors' P1 uses lizard in the same way)."""
    hits = [f for f in functions(code, path) if f.start_line <= line <= f.end_line]
    return min(hits, key=lambda f: f.end_line - f.start_line) if hits else None


def method_text(code, f):
    return "\n".join(code.splitlines()[f.start_line - 1: f.end_line])


def norm(s):
    return " ".join(s.split())


def find_same_method(code, path, before_f):
    fs = functions(code, path)
    same = [f for f in fs if f.long_name == before_f.long_name]
    if len(same) == 1:
        return same[0]
    by_name = [f for f in fs if f.name == before_f.name]
    return by_name[0] if len(by_name) == 1 else None


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- eligibility
def is_test_path(path):
    p = "/" + path.lower()
    return "/src/test/" in p or "/test/" in p or p.endswith("test.java") or p.endswith("tests.java")


def evaluate_comment(repo, pr, c, all_comments, commits):
    """Apply frozen rules R1-R10 in order. Returns (reason, case_dict_or_None)."""
    author = pr["user"]["login"]
    u = c.get("user") or {}
    if c.get("in_reply_to_id"):
        return "R1_reply_not_top_level", None
    if not c["path"].endswith(".java"):
        return "R2_not_java_file", None
    if is_test_path(c["path"]):
        return "R3_test_file", None
    if u.get("type") == "Bot" or u.get("login", "").endswith("[bot]"):
        return "R4_bot_comment", None
    if u.get("login") == author:
        return "R5_comment_by_pr_author", None
    if c.get("side") == "LEFT" or c.get("original_line") is None:
        return "R6_not_on_submitted_code_line", None

    line = c["original_line"]
    before_code, before_file = get_file(repo, c["path"], c["original_commit_id"])
    if before_code is None:
        return "R7_source_file_unavailable", None
    bf = method_at_line(before_code, c["path"], line)
    if bf is None:
        return "R8_comment_not_inside_a_method", None

    others = [o for o in all_comments
              if o["id"] != c["id"] and not o.get("in_reply_to_id") and o["path"] == c["path"]
              and o.get("original_commit_id") == c["original_commit_id"]
              and o.get("original_line") is not None and bf.start_line <= o["original_line"] <= bf.end_line]
    if others:
        return "R9_more_than_one_comment_on_method", None

    before_m = method_text(before_code, bf)
    later = [k for k in commits if k["commit"]["committer"]["date"] > c["created_at"]]
    revised = None
    for k in later[: CFG["max_later_commits_checked"]]:
        code, fpath = get_file(repo, c["path"], k["sha"])
        if code is None:
            continue
        af = find_same_method(code, c["path"], bf)
        if af is not None and norm(method_text(code, af)) != norm(before_m):
            revised = (k, code, fpath, af)
            break
    if revised is None:
        return "R10_method_not_revised_later_in_pr", None

    k, after_code, after_file, af = revised
    if bf.token_count > CFG["max_method_tokens"] or af.token_count > CFG["max_method_tokens"]:
        return "R11_method_over_token_limit", None

    after_m = method_text(after_code, af)
    line_text = before_code.splitlines()[line - 1] if line - 1 < len(before_code.splitlines()) else ""
    case = {
        "case_id": f"{repo}#{pr['number']}-{c['id']}",
        "project": repo,
        "pr_number": pr["number"],
        "pr_url": pr["html_url"],
        "pr_author": author,
        "comment_id": c["id"],
        "comment_url": c["html_url"],
        "comment_author": u.get("login"),
        "comment_created_at": c["created_at"],
        "file_path": c["path"],
        "commented_line": line,
        "commented_line_text": line_text.strip(),
        "original_commit": c["original_commit_id"],
        "revised_commit": k["sha"],
        "method_long_name_before": bf.long_name,
        "method_lines_before": f"{bf.start_line}-{bf.end_line}",
        "method_lines_after": f"{af.start_line}-{af.end_line}",
        "method_tokens_before": bf.token_count,
        "method_tokens_after": af.token_count,
        "source_file_before": os.path.relpath(before_file, ROOT),
        "source_file_after": os.path.relpath(after_file, ROOT),
        "source_file_before_sha256": sha256_text(before_code),
        "source_file_after_sha256": sha256_text(after_code),
        "original_code": before_m,
        "review_comment": c["body"],
        "revised_code": after_m,
    }
    return "ELIGIBLE", case


# --------------------------------------------------------------------------- main
def mine_project(repo, writer, cases_out):
    # List closed PRs newest first and keep those merged inside the window.
    base_dir = repo.replace("/", "__")
    listing = cache_path(base_dir, "closed_prs_listing.json")
    if os.path.exists(listing):
        prs = json.load(open(listing, encoding="utf-8"))["data"]
    else:
        prs, pages, page = [], [], 1
        stop_before = (dt.date.fromisoformat(CFG["window_start"]) - dt.timedelta(days=365)).isoformat()
        while True:
            url = f"{API}/repos/{repo}/pulls?state=closed&sort=created&direction=desc&per_page=100&page={page}"
            status, body, _ = _request(url, "application/vnd.github+json")
            if status != 200:
                raise RuntimeError(f"GitHub API {status} for {url}: {body[:300]!r}")
            data = json.loads(body)
            pages.append({"url": url, "fetched_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "body": data})
            prs.extend(data)
            if not data or data[-1]["created_at"][:10] < stop_before:
                break
            page += 1
        json.dump({"pages": pages, "data": prs}, open(listing, "w", encoding="utf-8"), indent=1)
    in_window = {p["number"]: p for p in prs
                 if p.get("merged_at") and CFG["window_start"] <= p["merged_at"][:10] <= CFG["window_end"]}
    numbers = sorted(in_window)
    print(f"{repo}: {len(numbers)} merged PRs in window", flush=True)
    target = CFG["cases_per_project"] + CFG["extra_eligible_to_collect"]
    n_eligible, scanned = 0, 0
    for n in numbers:
        base = repo.replace("/", "__")
        pr = in_window[n]
        comments = get_json(f"{API}/repos/{repo}/pulls/{n}/comments?per_page=100",
                            cache_path(base, "prs", f"{n}_review_comments.json"), paginate=True)["data"]
        commits = get_json(f"{API}/repos/{repo}/pulls/{n}/commits?per_page=100",
                           cache_path(base, "prs", f"{n}_commits.json"), paginate=True)["data"]
        scanned += 1
        for c in sorted(comments, key=lambda x: (x["path"], x["created_at"], x["id"])):
            reason, case = evaluate_comment(repo, pr, c, comments, commits)
            writer.writerow({"project": repo, "pr_number": n, "file_path": c["path"],
                             "comment_created_at": c["created_at"], "comment_id": c["id"],
                             "comment_url": c.get("html_url"), "result": reason})
            if case:
                n_eligible += 1
                cases_out.write(json.dumps(case) + "\n")
        print(f"  PR #{n}: {len(comments)} review comments, eligible so far {n_eligible}", flush=True)
        if n_eligible >= target:
            break
    print(f"{repo}: scanned {scanned} PRs (up to #{n}), {n_eligible} eligible", flush=True)
    return {"project": repo, "prs_in_window": len(numbers), "prs_scanned": scanned,
            "last_pr_scanned": n if numbers else None, "eligible": n_eligible}


def main():
    if not TOKEN and not os.environ.get("GITHUB_AUTH_VIA_PROXY"):
        sys.exit("Set GITHUB_TOKEN first (a classic or fine-grained token with public read access is enough).")
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    log = {"started_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "config": CFG,
           "lizard_version": getattr(lizard, "version", "?"),
           "config_sha256": hashlib.sha256(open(os.path.join(ROOT, "config.json"), "rb").read()).hexdigest(),
           "script_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
           "projects": []}
    with open(os.path.join(ROOT, "data", "candidates.csv"), "w", newline="", encoding="utf-8") as f, \
         open(os.path.join(ROOT, "data", "eligible_cases.jsonl"), "w", encoding="utf-8") as cases_out:
        w = csv.DictWriter(f, fieldnames=["project", "pr_number", "file_path", "comment_created_at",
                                          "comment_id", "comment_url", "result"])
        w.writeheader()
        for repo in CFG["projects"] + CFG["reserve_projects"]:
            log["projects"].append(mine_project(repo, w, cases_out))
    log["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    json.dump(log, open(os.path.join(ROOT, "data", "mining_log.json"), "w"), indent=2)
    print("Done. See data/candidates.csv and data/mining_log.json")


if __name__ == "__main__":
    main()
