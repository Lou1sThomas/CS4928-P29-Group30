"""Event B: does a PR's commented method depend on code changed in a neighbouring file?

For one merged PR it lists every changed .java file, collects the declarations
(classes, methods, fields/constants) added or changed in each OTHER file's diff,
and checks which of those names the commented method uses.
A name match is a heuristic flag, not proof of a semantic dependency: confirm by hand.

Usage:
  python3 check_pr_dependencies.py --repo apache/commons-io --pr 296 \
      --file src/main/java/org/apache/commons/io/output/FileWriterWithEncoding.java \
      --method FileWriterWithEncoding --out results/event_b/dependency_check_pr296.json
Set GITHUB_TOKEN to raise the API limit (60 calls/hour without it).
"""
import argparse, json, os, re, ssl, urllib.request

API = "https://api.github.com"
# python.org builds on macOS ship without CA certificates; fall back to the system bundle
CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem") if os.path.exists("/etc/ssl/cert.pem") else None
DECL = re.compile(
    r"^[+-]\s*(?:@\w+\s+)*(?:(?:public|protected|private|static|final|abstract|synchronized|default)\s+)*"
    r"(?:(?:class|interface|enum|record)\s+(\w+)"            # type declaration
    r"|[\w<>\[\],.? ]+?\s+(\w+)\s*\("                         # method declaration
    r"|[\w<>\[\],.? ]+?\s+([A-Za-z_]\w*)\s*(?:=|;))",         # field / constant
    re.M)
KEYWORDS = {"return", "new", "if", "for", "while", "switch", "catch", "throw", "else", "try",
            "finally", "do", "case", "this", "super", "assert"}

def get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "cs4928-event-b"})
    if not raw:
        req.add_header("Accept", "application/vnd.github+json")
        if os.environ.get("GITHUB_TOKEN"):
            req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        data = r.read().decode("utf-8", errors="replace")
    return data if raw else json.loads(data)

def method_body(src, name):
    """Return the text of the first method/constructor called `name` (brace matching)."""
    # a declaration starts its line: optional modifiers, optional return type, then the name
    m = re.search(r"^[ \t]*(?:(?:public|protected|private|static|final|abstract|synchronized|native|default)\s+)*"
                  r"(?:<[^>]+>\s+)?(?:[\w<>\[\],.?]+\s+)?" + re.escape(name) +
                  r"\s*\([^;{]*\)\s*(?:throws[^{;]*)?\{", src, re.M)
    if not m:
        return None
    depth, i = 0, m.end() - 1
    for j in range(i, len(src)):
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        if depth == 0:
            return src[m.start():j + 1]
    return src[m.start():]

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--repo", required=True); a.add_argument("--pr", type=int, required=True)
    a.add_argument("--file", required=True, help="path of the commented .java file")
    a.add_argument("--method", required=True, help="name of the commented method")
    a.add_argument("--out", required=True)
    x = a.parse_args()

    pr = get(f"{API}/repos/{x.repo}/pulls/{x.pr}")
    files = get(f"{API}/repos/{x.repo}/pulls/{x.pr}/files?per_page=100")
    java = [f for f in files if f["filename"].endswith(".java")]
    head = pr["head"]["sha"]
    # fetch from the base repo: it keeps every PR commit even when the contributor's fork is deleted
    src = get(f"https://raw.githubusercontent.com/{x.repo}/{head}/{x.file}", raw=True)
    body = method_body(src, x.method)
    if body is None:
        raise SystemExit(f"method {x.method} not found in {x.file} at {head}")
    used = set(re.findall(r"\b[A-Za-z_]\w*\b", body))
    # names the commented file declares itself (locals, its own methods/fields) are not neighbour dependencies
    own = {n for t in DECL.findall("\n".join("+" + l for l in src.splitlines())) for n in t if n}
    used -= own

    neighbours = []
    for f in java:
        if f["filename"] == x.file:
            continue
        names = set()
        for t, mth, fld in DECL.findall(f.get("patch", "")):
            names.update(n for n in (t, mth, fld) if n and n not in KEYWORDS)
        cls = os.path.splitext(os.path.basename(f["filename"]))[0]
        hits = sorted((names | {cls}) & used)
        neighbours.append({"file": f["filename"], "status": f["status"],
                           "changed_declarations": sorted(names), "used_by_method": hits})

    result = {"repo": x.repo, "pr": x.pr, "head_sha": head, "commented_file": x.file,
              "method": x.method, "java_files_changed": len(java),
              "dependency_flag": any(n["used_by_method"] for n in neighbours),
              "neighbours": neighbours}
    os.makedirs(os.path.dirname(x.out) or ".", exist_ok=True)
    json.dump(result, open(x.out, "w"), indent=2)
    print(f"{x.repo}#{x.pr}: {len(java)} Java files changed; method {x.method}; "
          f"dependency_flag={result['dependency_flag']}")
    for n in neighbours:
        print(f"  {n['file']} ({n['status']}): uses {n['used_by_method'] or 'nothing changed here'}")

if __name__ == "__main__":
    main()
