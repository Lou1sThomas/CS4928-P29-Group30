"""RQ1/RQ2a: per-step removal rates for T5 (study S2 = 'Paper 2' in the pipeline log)
from our pipeline runs vs. the authors' Table 4 (S2, project-level test split).
Usage: python3 compare_removal_rates.py <run_log> [<run_log> ...]  > results csv on stdout
Rate for step k = 1 - n_k / n_(k-1), in percentage points. P1 has no Table 4 baseline
(Table 4 reports counts after P1, not the raw input size)."""
import re, sys
TABLE4_S2_PROJECT_TEST = {"P1": 61562, "P2": 18928, "P3": 13589, "P4": 12547}  # Table 4, cumulative, after size filtering

def s2_counts(log):
    t = open(log).read()
    def block(title):
        return t[t.index(title):].split("\n\n")[0]
    def p2_after(b):  # the 'Paper 2 - 512 tokens' size-filter line is followed by its remaining count
        m = re.search(r"Paper 2 - 512 tokens\) removed: \d+\n - Remaining after size filtering: (\d+)", b)
        return int(m.group(1))
    raw = int(re.search(r"Initial raw records: (\d+)", t).group(1))
    c = {"raw": raw,
         "P1": p2_after(block("(Step 1.1 - Paper 1 & 2) P1")),
         "P2": p2_after(block("(Step 1.2 - Paper 1 & 2) ----> P2")),
         "P3": p2_after(block("(Step 1.3 - Paper 1 & 2) ----> P3"))}
    b4 = block("(Step 2.1 - Paper 2)  ----> P4")
    c["P4"] = int(re.findall(r"Remaining after size filtering: (\d+)", b4)[-1])
    return c

def rates(c, keys):
    out = {}
    for prev, k in zip(keys, keys[1:]):
        out[k] = None if not c[prev] else 100 * (1 - c[k] / c[prev])
    return out

paper = rates(TABLE4_S2_PROJECT_TEST, ["P1", "P2", "P3", "P4"])
print("run,step,count_before,count_after,our_removed_pct,paper_removed_pct,diff_pts,within_10pts")
for log in sys.argv[1:]:
    c = s2_counts(log); ours = rates(c, ["raw", "P1", "P2", "P3", "P4"])
    name = log.split("/PreprocessedData/")[1].split("/")[0] if "/PreprocessedData/" in log else log
    keys = ["raw", "P1", "P2", "P3", "P4"]
    for prev, k in zip(keys, keys[1:]):
        o, p = ours[k], paper.get(k)
        d = None if (o is None or p is None) else o - p
        fmt = lambda v: "" if v is None else f"{v:.1f}"
        print(f"{name},{k},{c[prev]},{c[k]},{fmt(o)},{fmt(p)},{fmt(d)},{'' if d is None else abs(d) <= 10}")
