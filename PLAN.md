# CS4928 Project P29 – M1 Reproduction Plan

**Group:** [GROUP ID]
**Plan written:** 11 Oct 2026 (before any execution)
**Frozen:** [DATE] – git tag `M1_PLAN`, once the coordinator marks M1 as READY
**Coordinator M1 status:** [READY / NOT YET / BLOCKED]
**Group lead:** Antony Thomas

| Student ID | Name |
| --- | --- |
| 23375175 | Antony Thomas |
| 23381272 | Oisin Minogue |
| 23367687 | Padraig Shannon |
| 23365757 | Tadgh Austin |
| 23355573 | Shaun Purcell |

---

## 0. Assigned study and artefact

| Item | Value |
| --- | --- |
| Paper | Pirouzkhah et al., "The price of precision: the cost of preprocessing for automated code revision in code review", *Empirical Software Engineering* (2026). https://link.springer.com/article/10.1007/s10664-025-10781-4 |
| Authors' repository | https://github.com/shirinpirouzkhaah/Price-of-Precision |
| Data (per README) | Zenodo https://doi.org/10.5281/zenodo.17227729 (record v1, 29 Sep 2025) |
| Project pack | P29 – Automated Code Revision and Data Preprocessing |
| Model studied | T5-small (the paper's S2 setting, from Tufano et al. 2022) |

---

## 1. Research questions, source anchors and target results

### Context: what the original study claims
Automated code revision (ACR) models take a piece of code plus a reviewer's comment and try to produce the revised code a developer would write. Before training and testing these models, earlier studies "clean" the data with a chain of preprocessing steps. The paper asks whether that cleaning helps or hurts. Its headline claims are:
- small models need heavy preprocessing;
- mid-sized models (T5, CodeReviewer) benefit from light filtering;
- large models (CodeLLaMA-7B, GPT-3.5) are largely insensitive to preprocessing;
- differences between project-level and time-level data splits are sometimes statistically significant but have small, practically negligible effect sizes.

Our project tests a bounded part of these claims for T5-small, using the authors' own artefact.

---

### RQ1 (assigned, copied exactly)
> How does preprocessing change automated revision success on the bounded dataset?

**Key terms, as we use them**

| Term | Meaning in this project |
| --- | --- |
| Preprocessing | The authors' cumulative pipeline for T5-small's setting (S2), applied in order: P1 method extraction, P2 comment pruning, P3 unchanged-method removal, P4 comment cleaning, P5 long method + comment removal (512-token limit). Each step either transforms records or removes them. |
| Automated revision success | Exact match (EXM): the model's predicted revision is identical to the developer's actual revision. EXM is the paper's primary metric. |
| Bounded dataset | The project-level test split from the authors' artefact, with a fixed 12-record sample for manual tracing (section 2). |

**Sub-questions**
- **RQ1a – Does the pipeline behave as reported?** Running `Preprocessing_Pipeline.py` unchanged on the project-level test split, is the number of records remaining after each step the same as the paper reports?
- **RQ1b – Does preprocessing change success as reported?** Running the authors' statistics script on the published per-record results for T5-small, do we get the same conclusion about whether EXM differs between preprocessing steps (verdict at α = 0.05 and direction of the effect)?

**Why both parts:** RQ1a checks the *input side* of the claim (the data the model actually sees after preprocessing). RQ1b checks the *outcome side* (whether success changes). Reproducing only one would not show whether the paper's conclusion follows from its pipeline.

| Item | Value |
| --- | --- |
| Source anchor | Paper Section 5 ("The Impact of Preprocessing"): Table [X] (records per preprocessing step) and Table [X] (EXM per step for T5-small). Artefact: `Preprocessing/Cumulative_code/Preprocessing_Pipeline.py` (T5 setting outputs `*_Paper2_*`); `Results/StatisticalTests/stats_EXM_all_steps.py` (Cochran's Q + pairwise McNemar, Holm correction). |
| Target result | (a) The per-step record counts for the project-level test split. (b) The paper's verdict and direction for T5-small: T5 benefits from light filtering, so at least one light-filtering step should give significantly higher EXM than the raw or heavily filtered setting. |
| Evidence that answers it | `results/step_counts_projectlevel.csv`; `results/trace_audit.md` (12 records traced step by step); `results/stats_rq1/` (script output). |
| Form of the answer | "For T5-small on the project-level split, preprocessing [did / did not] change EXM in the way the paper reports: [verdict], [direction]; record counts [matched / differed at step X]." |

---

### RQ2 (assigned, copied exactly)
> How much does project-level separation change the result?

**Key terms, as we use them**

| Term | Meaning in this project |
| --- | --- |
| Project-level separation | A data split where each software project appears only in training *or* testing, never both. This prevents the model from "remembering" a project's code style or identifiers. |
| Comparison split | The time-level split: within each project, the earliest 80% of reviews go to training and the latest 20% to testing, so the same projects appear on both sides. |
| "The result" | EXM success for T5-small at each preprocessing step (the RQ1 outcome). |
| "How much" | Both statistical significance (does the split matter?) and effect size (does it matter *enough* to change a practical conclusion?). |

**Sub-questions**
- **RQ2a – Is there a difference?** For T5-small, does EXM differ significantly between the project-level and time-level splits at each preprocessing step (two-proportion test, α = 0.05)?
- **RQ2b – Is the difference large enough to matter?** Is the effect size small or negligible, as the paper reports, or large enough that the RQ1 conclusion would change depending on the split?

**Why it matters:** if project-level separation changed results substantially, conclusions drawn from time-level splits (common in earlier ACR work) could be inflated by data leakage between projects. The paper claims this effect exists but is small; we test that claim for one model.

| Item | Value |
| --- | --- |
| Source anchor | Paper Section 5, split-type comparison: Table [X]. Artefact: `Results/StatisticalTests/stats_EXM_Time_vs_project.py` (two-proportion test with Wilson CIs) and `stats_Time_vs_project.py` (Kruskal–Wallis with bootstrap CI). |
| Target result | Some split differences may be statistically significant, but effect sizes are small or negligible, so the RQ1 conclusion is the same on both splits. |
| Evidence that answers it | `results/stats_rq2/` (script outputs: p-values, CIs, effect sizes per step). |
| Form of the answer | "For T5-small, project-level separation changed EXM by [amount, CI] across steps; [n] of [m] differences were significant and effect sizes were [negligible / not negligible], so the RQ1 conclusion [holds / does not hold] across split types." |

---

### Out of scope at M1
- Retraining or fine-tuning any model; we use the authors' published per-record results.
- Models other than T5-small; ChatGPT results; the paper's own RQ1 (literature review) and RQ3 (model size).
- CodeBLEU and Levenshtein as decision metrics (EXM is primary; others may be reported for context only).
- `NewGitHubData` and any held-out or Change Event material.
- Design / refactoring work. Candidate for M4 (Week 9): the near-duplicate code in `Cumulative_code` and `Isolated_code` (see section 7). Not analysed at M1.

---

## 2. Bounded sample

| Element | Frozen value |
| --- | --- |
| Unit of analysis | One code-review record: code before the change, reviewer comment, code after the change. |
| Source / version | Repo commit `d1e9692`; Zenodo record 10.5281/zenodo.17227729 v1; input file `SplittedData/ProjectLevel/Gerrit_ProjectSplited_Test_NoLeakage.csv`; time-level test file [NAME, once available]; per-record results for T5-small (`*_common_test_predictions_with_codeBLEU_10_{TimeLevel,ProjectLevel}.csv`). |
| Size / range | **12 records** for the bounded reproduction and manual audit. Supporting counts and statistics use the authors' full test split and full per-record results (see note). |
| Selection rule | First 12 eligible records in stable order: case ID, then file path, then chronological ID. Not chosen by outcome. Eligible = row has non-empty code-before, comment and code-after fields. Excluded rows are listed with their reason. If fewer than 12 are eligible, all are used and this is recorded. IDs saved to `data/sample_ids.csv` before any analysis. |
| Note on scope | Per-step counts are a property of the whole split, and a statistical test on 12 records has no power, so the paper's claims can only be compared at full-split level. These runs reuse the authors' scripts and published outputs, with no new infrastructure. The 12 records are traced by hand through each step and their per-step EXM outcomes recorded as the bounded, inspectable evidence. |

---

## 3. Method: inputs → procedure → output

| Inputs | Procedure | Output / comparison |
| --- | --- | --- |
| Project-level test CSV; `Preprocessing/Cumulative_code/*.py` at commit `d1e9692`; `utils/idioms.csv`; Python [VERSION] and libraries pinned in `requirements.txt`. | Set `input_csv_path`; run `Preprocessing_Pipeline.py` unchanged; log records remaining after each T5-setting step (`*_Paper2_*` outputs) to `results/step_counts_projectlevel.csv`; trace the 12 sample records through each step in `results/trace_audit.md`. | Per-step counts vs paper Table [X] → **RQ1a**. |
| Per-record results for T5-small, project-level, all preprocessing steps. | Run `stats_EXM_all_steps.py` unchanged (Cochran's Q + pairwise McNemar, Holm correction, α = 0.05); save console output and CSVs to `results/stats_rq1/`. Record EXM for the 12 sample records per step. | Verdict + direction vs paper → **RQ1b**. |
| Per-record results for T5-small, project-level and time-level. | Run `stats_EXM_Time_vs_project.py` and `stats_Time_vs_project.py` unchanged; save outputs to `results/stats_rq2/`. | Significance + effect size vs paper → **RQ2**. |

**Bounded decisions** (where the paper does not specify):
- One model only: T5-small (the paper's S2 setting, Tufano et al. 2022), chosen because (1) the paper reports a clear preprocessing effect for it (benefits from light filtering), giving a testable claim; (2) the authors' pipeline produces dedicated outputs for this setting (`*_Paper2_*` files); (3) its checkpoints are included in the repository; (4) unlike OpenNMT and GPT-3.5, it needs no training from scratch and was evaluated on both split types.
- α = 0.05, as used in the authors' scripts.
- Scripts are run unchanged. Any edit needed just to make them run (e.g. a file path) is committed separately and listed in section 8.
- Library versions that differ from the authors' are recorded, not hidden.

---

## 4. Expected result (written before execution)

- **RQ1a:** Step counts match the paper exactly, because the pipeline is deterministic.
- **RQ1b:** Same verdict and direction as the paper for T5-small: EXM differs significantly between at least some preprocessing steps, with light filtering performing best.
- **RQ2:** Project-level vs time-level makes a small or negligible difference for T5-small, matching the paper.

---

## 5. Decision rule

| RQ | REPRODUCED | NOT REPRODUCED | INCONCLUSIVE / BLOCKED |
| --- | --- | --- | --- |
| RQ1a | Every step count matches the paper exactly. | A valid completed run gives any step count that differs. | Pipeline cannot run, input data unavailable, or the paper does not report the counts needed to compare. |
| RQ1b | Same significant / not-significant verdict (α = 0.05) and same direction of effect as the paper. | A valid completed run gives a different verdict or direction. | Statistics script or per-record results unavailable or unrunnable. |
| RQ2 | Same significance verdict and a small / negligible effect size, as in the paper. | A valid completed run gives a non-negligible effect size or a different verdict. | Time-level or project-level results unavailable. |

A NOT REPRODUCED result is reported as observed, with its likely cause analysed (library versions, encoding, data version). Results are never adjusted to match the paper. A failed build or missing data is BLOCKED, not NOT REPRODUCED.

---

## 6. Feasibility check (11 Oct 2026)

| Check | Status | Evidence |
| --- | --- | --- |
| Paper accessible | OK | Springer link above |
| Repo cloned at a recorded commit | OK | `git log -1` → `d1e9692`, 29 Sep 2025 |
| Pipeline and statistics code present | OK | `Preprocessing/Cumulative_code/` (4 files); `Results/StatisticalTests/` (4 scripts) |
| Data folders in repo | BLOCKED | `Preprocessing/SplittedData/` and `Preprocessing/NewGitHubData/` are empty; `Results/csvResults/` contains no data. README says to download them from Zenodo. |
| Zenodo record contents | BLOCKED | Record 10.5281/zenodo.17227729 v1 lists one file only: `FinalRatios.zip` (45.5 kB). No split CSVs or per-record results. [Confirm whether other versions or records exist.] |
| Pipeline helper file | BLOCKED | `Preprocessing_Pipeline.py` line 136 reads `./utils/idioms.csv`; not in repo. |
| Statistics inputs | BLOCKED | All four scripts read `*_predictions_with_codeBLEU_10_*.csv`; not in repo or on Zenodo. |
| Actions taken | – | Authors emailed [DATE] asking for the missing data. Raised with coordinator at Lab 3 for the contingency route. |

**Current status: BLOCKED (data availability).** The plan above is complete and executable once the input data is available. Candidate fallback routes, to be agreed with the coordinator and **not** chosen by us after seeing any results:
1. Reproduce the aggregated results using `FinalRatios.zip` (the only data published).
2. Run the pipeline on the original public Tufano et al. dataset, recreating the project-level split as documented.
3. Wait for the data from the authors and keep the plan unchanged.

---



## 7. Known deviations from the paper

- One model only (T5-small); no retraining.
- Bounded 12-record audit alongside the full-split counts and statistics.
- [Any fallback route agreed with the coordinator.]

---

## Change log

Any change after the M1 freeze is recorded here with the date, what changed, why, and how it affects interpretation of later evidence. Earlier wording is kept, not rewritten.

| Date | Change | Reason | Effect on interpretation |
| --- | --- | --- | --- |
| | | | |