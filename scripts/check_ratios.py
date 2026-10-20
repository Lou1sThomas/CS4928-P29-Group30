"""
P29 Week 6 - consistency check on the authors' published FinalRatios tables.

For every results CSV under a folder, recompute Precision, Recall and F1
from the Size and EXM10 columns and compare them with the values the
authors published. Writes one row per table row to an output CSV.

How the recomputation works (derived from the published columns):
  correct   = EXM10 / 100 * Size
  Precision = EXM10 / 100
  Recall    = correct / baseline_size   (baseline = Size of the *_P1 row,
                                         i.e. the least-filtered test set;
                                         first row if no *_P1 row exists)
  F1        = 2 * P * R / (P + R)
A value "matches" if it is within 0.0005 of the published value
(the authors round to 3 decimal places).

Usage (from your project folder):
  python check_ratios.py "path\\to\\unzipped\\FinalRatios" results\\week6\\ratio_check.csv
"""
import csv
import os
import sys

TOL = 0.0005
NEEDED = {"Step", "Size", "EXM10", "Precision", "Recall", "F1"}


def f1(p, r):
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


# Two published files (*_common_new_test.csv) have NO header row and a
# different column order. Inferred from their values (recorded as an
# assumption in REPRODUCTION.md): Step, EXM10, Lev ratio, CodeBLEU, Size,
# Precision, Recall, F1.
HEADERLESS = ["Step", "EXM10", "Lev ratio", "CodeBLEU", "Size", "Precision", "Recall", "F1"]


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        raw = list(csv.reader(fh))
    if not raw:
        return [], "empty"
    if raw[0] and raw[0][0].strip() == "Step":
        header, body, layout = raw[0], raw[1:], "header"
    elif len(raw[0]) == len(HEADERLESS):
        header, body, layout = HEADERLESS, raw, "no header (inferred columns)"
    else:
        return [], "unrecognised"
    return [dict(zip(header, r)) for r in body if r], layout


def check_file(path):
    rows, layout = read_rows(path)
    if not rows or not NEEDED.issubset(rows[0].keys()):
        return None  # not a ratio table; reported as skipped
    base_row = next((r for r in rows if r["Step"].strip().endswith("_P1")), rows[0])
    base = float(base_row["Size"])
    out = []
    for r in rows:
        size, exm = float(r["Size"]), float(r["EXM10"])
        p = exm / 100
        rec = (exm / 100 * size) / base
        calc = {"Precision": p, "Recall": rec, "F1": f1(p, rec)}
        pub = {k: float(r[k]) for k in calc}
        ok = all(abs(calc[k] - pub[k]) <= TOL for k in calc)
        out.append({
            "file": path,
            "layout": layout,
            "step": r["Step"],
            "size": int(size),
            "baseline_size": int(base),
            "exm10": exm,
            **{f"{k}_published": pub[k] for k in calc},
            **{f"{k}_recomputed": round(calc[k], 4) for k in calc},
            "match": "YES" if ok else "NO",
        })
    return out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    root, out_path = sys.argv[1], sys.argv[2]
    results, skipped = [], []
    for dirpath, _, files in os.walk(root):
        for name in sorted(files):
            if name.lower().endswith(".csv"):
                path = os.path.join(dirpath, name)
                res = check_file(path)
                (skipped.append(path) if res is None else results.extend(res))
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if results:
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(results[0].keys()))
            w.writeheader()
            w.writerows(results)
    n_ok = sum(r["match"] == "YES" for r in results)
    n_files = len({r["file"] for r in results})
    print(f"Tables checked: {n_files}   Rows: {len(results)}   Matching: {n_ok}   Not matching: {len(results) - n_ok}")
    print(f"Skipped (not ratio tables): {len(skipped)}")
    for s in skipped:
        print("  skipped:", s)
    print(f"Row-level results written to: {out_path}")


if __name__ == "__main__":
    main()