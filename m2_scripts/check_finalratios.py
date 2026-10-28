"""RQ1 (statistical part, contingency route): check the authors' only published output
(FinalRatios.zip, Zenodo 10.5281/zenodo.17227729) against the paper for T5 (S2).
  1. Test-set sizes in FinalRatios vs Table 4.
  2. Re-run Table 5's two-proportion z-test (time-level vs project-level EXM, T5),
     pooling the six S2 configurations on the intersection ('_test_common') sets.
  3. Precision ranges quoted in Sec. 5.2 (time 13-18%, project 10-21%).
Usage: python3 check_finalratios.py <path to FinalRatios/csvResultsS2T5/final_results>"""
import sys, os
from math import sqrt, erfc
import pandas as pd
d = sys.argv[1]
r = lambda f: pd.read_csv(os.path.join(d, f))
T4 = {"ProjectLevel_test.csv": [61562, 18928, 13589, 12547, 43294, 55086],
      "TimeLevel_test.csv":    [82217, 26176, 18911, 17352, 58705, 72157],
      "ProjectLevel_new_test.csv": [13189, 4687, 1014, 941, 3244, 11775]}
print("1) Sizes vs Table 4")
for f, exp in T4.items():
    got = r(f)["Size"].tolist(); print(f"   {f}: {'MATCH' if got == exp else 'MISMATCH'} {got}")
print("2) Table 5, T5 EXM time vs project (paper: diff 0.008, p 6.20e-06, CI 0.0045-0.0114)")
t, p = r("TimeLevel_test_common.csv"), r("ProjectLevel_test_common.csv")
nt, npj = t.Size.sum(), p.Size.sum()
xt, xp = (t.EXM10 / 100 * t.Size).sum(), (p.EXM10 / 100 * p.Size).sum()
pt, pp = xt / nt, xp / npj; pool = (xt + xp) / (nt + npj)
zz = (pt - pp) / sqrt(pool * (1 - pool) * (1 / nt + 1 / npj)); pval = erfc(abs(zz) / sqrt(2))
se = sqrt(pt * (1 - pt) / nt + pp * (1 - pp) / npj)
print(f"   ours: diff {pt-pp:.4f}, p {pval:.2e}, CI ({pt-pp-1.96*se:.4f}, {pt-pp+1.96*se:.4f})")
print("3) Precision ranges on intersection sets (paper: time ~13-18%, project ~10-21%)")
print(f"   time {t.EXM10.min():.1f}-{t.EXM10.max():.1f}%, project {p.EXM10.min():.1f}-{p.EXM10.max():.1f}%")
