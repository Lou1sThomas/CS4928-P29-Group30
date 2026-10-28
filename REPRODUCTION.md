# CS4928 P29 – Week 6 Reproduction Log (Lab 4)

## Step 1 – Re-open the frozen M1 contract

### What M1 froze, and whether it can run as frozen

| M1 item | What we froze | Can it run? |
| --- | --- | --- |
| **RQ + target** | **RQ1:** Do the authors' code and data (project-level test split) give the same record counts per step as Table 4, and the same T5-small conclusion (preprocessing has only a weak effect)? **RQ2:** Does the pipeline behave the same on the new GitHub data, and is it worth restructuring the duplicated code? | **RQ1: Partly.** Counts and significance tests can't run (data not published), but T5-small summary results are in `FinalRatios.zip`. **RQ2: Partly.** The new-data part is blocked (not published); the code part can run. |
| **Sample** | One code-review record (RQ1, RQ2 new data) or one source-file pair (RQ2 code). Source: authors' repo (29 Sep 2025) + Zenodo v1. 12 records per test file; 4 file pairs. First 12 eligible in file order; exclusions in `data/excluded_rows.csv`. | **Partly.** No record-level data to sample from. The 4 file pairs are available. |
| **Method** | Run the authors' pipeline and statistics scripts unchanged; measure duplication and complexity of the 4 file pairs. | **Partly.** Scripts are there but have no input data. The code measurements can run. |
| **Metric** | RQ1: record counts per step; EXM@10 with Cochran's Q + McNemar (α = 0.05). RQ2: % removed per step; duplicated lines, complexity, output hashes. | **Partly.** Counts, tests and % removed need the missing data. Published summaries (EXM@10, sizes, precision, recall, F1) and code metrics are available. |
| **Decision rule** | RQ1: exact counts, same verdict and direction. RQ2: within 10 points per step; restructure only if it removes ≥50% duplication, keeps output identical and raises complexity ≤10%. Missing data = BLOCKED. | **Yes.** One extra rule is needed for the FinalRatios check; add it to the Change log before running. |
| **Held-out** | No Event / held-out material. | **Yes.** Only the authors' public repo and Zenodo files are used. |


## Step 2 – Prepare one traceable run
 
### Input identity
 
| Input | Version / identity |
| --- | --- |
| Authors' repository | https://github.com/shirinpirouzkhaah/Price-of-Precision – commit `d1e96929d2e78a20e65f78422676761411c8b18c` (29 Sep 2025). Re-cloned 15 Oct 2026 to `../authors-repo` (outside this repo); same commit as the 5 Oct clone, so no changes since. Code only – the data folders in GitHub are empty. |
| Zenodo record | https://doi.org/10.5281/zenodo.17227729 – v1 (29 Sep 2025), still the only version on 15 Oct 2026. One file: `FinalRatios.zip` (45.5 kB, CC BY 4.0). |
| Input file | `data/FinalRatios.zip` – Zenodo MD5: `b1947a3cab816a130a5fe3c329723b18`; our copy: `b1947a3cab816a130a5fe3c329723b18` → **MATCH** (checked 15 Oct 2026 with `Get-FileHash -Algorithm MD5`, re-checked after rebuilding the unzipped folder). |
| Unzipped copy (never edited) | `data/FinalRatios/` – rebuilt from the verified zip on 15 Oct 2026. |
| Bounded items | All rows of the 10 CSVs in `data/FinalRatios/csvResultsS2T5/final_results/` (T5-small, setting S2): ProjectLevel / TimeLevel × test / new_test × all / common, plus `ProjectLevel_common_new_test.csv` and `TimeLevel_common_new_test.csv`. Pilot (Step 3): `ProjectLevel_test.csv`. |
 
### Environment
 
| Item | Value |
| --- | --- |
| OS | Windows [11 / 10] [version, e.g. 23H2] (from `winver`) |
| Python | 3.11.10 (from `python --version`, 15 Oct 2026) |
| Libraries | Standard library only (`csv`, `os`, `sys`) – nothing installed with pip |
| Hardware | Not material – the script does simple arithmetic on small CSVs; no model is run |
 
### Execution route
 
 
| Item | Value |
| --- | --- |
| Scripts | Authors' repo, commit `d1e9692`: `Preprocessing/Cululative_code/Preprocessing_Pipeline.py` (RQ1a, per-step record counts); `Results/StatisticalTests/stats_EXM_all_steps.py` (RQ1b, statistical verdict); `Results/StatisticalTests/stats_EXM_Time_vs_project.py` and `stats_Time_vs_project.py` (RQ2, project vs time split) |
| Command | `python <script>.py`, run unchanged from `../authors-repo` (input paths are set inside each script) |
| Status | Not run. Inputs they read (`SplittedData/` and per-record model results) are not in the GitHub repo or the Zenodo record (checked 15 Oct 2026). |
 
**Fallback route**
 
| Item | Value |
| --- | --- |
| Script | `scripts/check_ratios.py` (SHA-256: `[PASTE]`) – recomputes Precision, Recall and F1 from each row's Size and EXM10 and compares them with the published values. Drafted with GenAI; checked by hand on one row by [NAME]. |
| Command (run from repo root) | `python scripts\check_ratios.py data\FinalRatios\csvResultsS2T5\final_results results\week6\ratio_check.csv > results\week6\run_log.txt` |
 
### Raw evidence
 
| Evidence | Location | Status |
| --- | --- | --- |
| Authors' published results (input, unedited) | `data/FinalRatios/csvResultsS2T5/final_results/` – 10 CSVs | In repo; MD5 of source zip matches Zenodo |
| Blocker evidence – authors' route | `results/week6/blocker_evidence.txt` – listing of `authors-repo/Preprocessing/SplittedData` (incl. hidden files) at commit `d1e9692`: only `.DS_Store` (macOS folder-settings file, 6 kB), 0 CSV files | Saved 20 Oct 2026 |
| Script output – per row | `results/week6/ratio_check.csv` – one row per input row: published vs recomputed Precision, Recall, F1, with a YES/NO match flag | Not yet produced – pending lab attendant approval, then Step 3 pilot / Step 4 full run |
| Script output – summary | `results/week6/run_log.txt` – the script's printed summary | Not yet produced – as above |
 
### Derived result
 
The derived results are the numbers we calculate from the raw output and then compare with the paper. None have been produced yet.
 
**What we will calculate (fallback route):**
- **(A) Do the authors' numbers add up?** For every row in the 10 CSVs, the script recalculates Precision, Recall and F1 from Size and EXM10 and checks they match the published values (within 0.0005). Result: how many rows match out of the total. Comes from `results/week6/ratio_check.csv`.
- **(B) Do the authors' numbers match the paper?** For each preprocessing step, we compare the test Size with the paper's Table 4, and the EXM10 with the paper's T5 results (§5, Figure 7). Saved in `results/week6/paper_comparison.md`.
**What we can't calculate (original route – BLOCKED):**
- RQ1a: the record count after each preprocessing step (needs the authors' pipeline input, which isn't published).
- RQ1b: whether preprocessing makes a statistically significant difference (needs per-record results, which aren't published).
- RQ2: whether project-level and time-level splits give different results (needs the same per-record results).
Evidence for the blocker: `results/week6/blocker_evidence.txt`. The rule for deciding REPRODUCED / NOT REPRODUCED is in the `PLAN.md` Change log, entry dated 15 Oct 2026

## Step 3 – Pilot on one file
The pilot used the published T5-small project-level summary file FinalRatios/csvResultsS2T5/final_results/ProjectLevel_test.csv, extracted from the authors' Zenodo archive

PowerShell Import-CSV was used to select the S2_P1 configuration and read its Size and EXM10 columns.

**Pilot Result**
Configuration: S2_P1
Size: 61,562
EXM10: 14.799714109353173

The pilot successfully extracted the expected summary row without errors.
**Evidence:** results/week6/pilot_output.txt
**Limitation:** This is an extraction of published aggregate results, not an independent execution of the authors preprocessing pipeline or statisical tests.


## Step 4 – Full bounded run
We couldn't run the original preprocessing experiment because some of the files needed were missing from the authors' repository and Zenodo.

Instead, we used the FinalRatios.zip file from Zenodo, which contains the authors' published results. We extracted the file and used PowerShell to get the T5-small results from ProjectLevel_test.csv.

I saved all the results into results/week7/t5_small_summary.csv. We checked the file to ensure the results were saved correctly.

**Evidence:** results/week6/t5_small_summary.csv and screenshots showing the results in PowerShell and VS Code.
**Limitation:** We only extracted the authors existing results. We didn't run their original preprocessing code or statistical tests because the required files were missing.

## Step 5 – Evidence chain (one value traced back)
For this step, we checked one of the T5-small results to show where it came from.

We used the S2_P1 configuration from the authors ProjectLevel_test.csv file, which was included in FinalRatios.zip on Zenodo.

We checked the value again in my saved t5_small_summary.csv file using PowerShell.

The result was:
Step: S2_P1
Size: 61,562
EXM10: 14.799714109353173

The value matched the one I extracted earlier, so I could confirm that it had been saved correctly.

**Evidence:** results/week6/t5_small_summary.csv and results/week6/step5-evidence_chain.png.

**Limitation:** This checks a published summary value. It doesn't trace an individual prediction through the preprocessing pipeline.


## Step 6 – Comparison with the original study

We compared the T5-small results from t5_small_summary.csv with Figure 7(c) in the original paper.

At first, the CSV values for P1, P3 and P4 looked similar to the blue points on the graph. For example, P1 had an EXM10 value of 14.80%, which is close to 0.15 (15%) on the graph.

The P2 value was 20.35% in our CSV, but the graph looked closer to 16%. We then realised we had used ProjectLevel_test.csv instead of ProjectLevel_test_common.csv. After checking th common-test file, P2 was 14.95% which was much closer to the graph.

The other values in the common-test file were also similar to the graph with P1 at 15.05%, P3 at 10.31% and P4 at 21.68%

We couldn't confirm an exact match because the graph only gives approximate values, and we couldn't run the original experiment because some of the required data files were missing.

**Outcome:** Inconclusive

**Evidence:** results/week7/t5_small_summary.csv and Figure 7(c) from the original paper.

**Limitation:** The graph only gives approximate values and we couldn't run the original preprocessing pipeline or statistical tests because the required files were missing.

## Step 7 – Current status
So far we have downloaded the authors FinalRatios.zip file from Zenodo and extract the T5-small results.

We successfully ran a pilot using PowerShell to check one result and then saved all six project level results into results/week6/t5_small_summary.csv.

We also compared these results with Figure 7(c) in the original paper. Some values were similar but we couldn't confirm an exact match for every step.

We couldn't run the original preprocessing pipeline or statistical tests because the required datasets and supporting files were missing.

Current status: Inconclusive

We have evidence of the published results being extracted and checked but we haven't independently reproduced the original experiment.

## Step 8 – Next action before M2
Before submitting we need to make sure all our evidence is uploaded to our GitHub repository, including all images and csv's and our updated REPRODUCTION.md

We also need to get our alternative approach approved. If approved we can use the published results as our contingency evidence. If it is not approved we need to discuss another way of completing the reproduction.

Our current result will remain inconclusive because we havent been able reproduce the original experiment.