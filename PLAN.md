# CS4928 Project P29 – M1 Reproduction Plan

**Group:** 30


| Student ID | Name |
| --- | --- |
| 23375175 | Antony Thomas |
| 23381272 | Oisin Minogue |
| 23367687 | Padraig Shannon |
| 23365757 | Tadhg Austin |
| 23355573 | Shaun Purcell |

---

## 0. Assigned study and artefact

| Item | Value |
| --- | --- |
| Paper | Pirouzkhah et al., "The price of precision: the cost of preprocessing for automated code revision in code review", *Empirical Software Engineering* (2026). https://link.springer.com/article/10.1007/s10664-025-10781-4 |
| Authors' repository | https://github.com/shirinpirouzkhaah/Price-of-Precision – latest version dated 29 Sep 2025, accessed 11 Oct 2026 |
| Data (per README) | Zenodo https://doi.org/10.5281/zenodo.17227729 (record v1, 29 Sep 2025) |
| Project pack | P29 – Automated Code Revision and Data Preprocessing |
| Model studied | T5-small (the paper's S2 setting, from Tufano et al. 2022) |

---

## 1. Research questions, source anchors and target results

### Context: what the original study claims
Automated code revision (ACR) models take a piece of code plus a reviewer's comment and try to produce the revised code a developer would write. Before training and testing these models, earlier studies "clean" the data with a chain of preprocessing steps. The paper asks whether that cleaning helps or hurts. Its headline claims are:
- small models need heavy preprocessing;
- mid-sized models (T5, CodeReviewer) benefit from light filtering (selective removal of records);
- large models (CodeLLaMA-7B, GPT-3.5) are largely insensitive to preprocessing.

The authors also built a newer GitHub test set (pull requests after September 2021) and released two copies of their preprocessing pipeline (cumulative and isolated). Our project reproduces a bounded part of the study for T5-small, tests whether the pipeline behaves the same on the new data, and evaluates a design decision about the pipeline's duplicated code.

**RQ origin:** our RQs refine the project pack's suggested RQs ("How does preprocessing change automated revision success on the bounded dataset?" and "How much does project-level separation change the result?"), as the pack allows during Lab 3. They were approved by the coordinator on [DATE]. RQ2 follows the module brief: RQ1 addresses the bounded reproduction; RQ2 addresses transfer/extension and the software-design question.

---

### RQ1 – Bounded reproduction
> If we run the authors' own code and data on the project-level test split, do we get the same number of records removed at each preprocessing step, and the same statistical conclusion for one model?

**Key terms, as we use them**

| Term | Meaning in this project |
| --- | --- |
| Authors' own code and data | `Preprocessing/Cumulative_code/` and `Results/StatisticalTests/` from the authors' repository, with the input data and per-record results the README says are on Zenodo. |
| Preprocessing steps | The cumulative pipeline for T5-small's setting (S2), in order: P1 method extraction, P2 comment pruning, P3 unchanged-method removal, P4 comment cleaning, P5 long method + comment removal (512-token limit). |
| Records removed | The drop in record count from one step to the next on the project-level test split. |
| Statistical conclusion | Whether exact match (EXM@10) differs significantly across preprocessing steps (Cochran's Q + pairwise McNemar, α = 0.05) and in which direction. |
| One model | T5-small. |
| EXM@10 | A record counts as correct if any of the model's 10 beam-search predictions is identical to the developer's revision (the authors' `EXM10` column; reported in the paper as Precision (EXM)). |

**Sub-questions**
- **RQ1a – Records removed:** does running `Preprocessing_Pipeline.py` unchanged give the same per-step record counts as the paper?
- **RQ1b – Statistical conclusion:** does running `stats_EXM_all_steps.py` on the published T5-small results give the same verdict and direction as the paper?

| Item | Value |
| --- | --- |
| Source anchor | Paper Section 5 ("The Impact of Preprocessing"): Table 4 (train/test sizes per preprocessing configuration) and Figure 7 (S2/T5 precision per step); statistical test results [location to confirm in Section 5.2]. Artefact: `Preprocessing/Cumulative_code/Preprocessing_Pipeline.py` (T5-setting outputs `*_Paper2_*`); `Results/StatisticalTests/stats_EXM_all_steps.py`. |
| Target result | (a) Per-step record counts for the project-level test split in Table 4. (b) The paper's conclusion for T5-small: "T5's Precision shows only a weak dependence on cumulative preprocessing". |
| Evidence that answers it | `results/step_counts_projectlevel.csv`; `results/trace_audit.md`; `results/stats_rq1/`. |

---

### RQ2 – Transfer and design decision
> Does the preprocessing pipeline behave the same way on new data, and is restructuring its duplicated code worth doing compared with leaving it as it is?

**Key terms, as we use them**

| Term | Meaning in this project |
| --- | --- |
| New data | The authors' newer GitHub test set (`Preprocessing/NewGitHubData/`, pull requests after September 2021, time-level split). |
| Behave the same way | The share of records removed at each preprocessing step on the new data is similar to the share removed on the project-level test split (threshold in section 4.3). |
| Duplicated code | The near-copies of the pipeline in `Preprocessing/Cumulative_code/` and `Preprocessing/Isolated_code/` (section 2). |
| Restructuring | Extracting the shared code into one module used by both pipelines, instead of keeping two copies. |
| Worth doing | Removes substantial duplication **and** produces identical output **and** does not make the code more complex (rule in section 4.3). |

**Sub-questions**
- **RQ2a – Transfer:** run the same pipeline unchanged on the new data. Is the removal rate at each step similar to the project-level split?
- **RQ2b – Design decision:** compare (A) leave the duplicated code as it is, and (B) extract the shared code into one module, and choose using the pre-declared rule. M1 freezes the question, measures and rule; implementation and verification happen at M4 (Week 9).

| Item | Value |
| --- | --- |
| Source anchor | Transfer: the paper's new GitHub test set (Section 5.1) [location to confirm]; artefact `Preprocessing/NewGitHubData/` (per README). Design: artefact `Preprocessing/Cumulative_code/` and `Preprocessing/Isolated_code/`. |
| Target result | (a) Removal rates on new data similar to the project-level split. (b) An evidence-based choice between A and B. |
| Evidence that answers it | `results/step_counts_newdata.csv`; `results/rq2_transfer_comparison.csv`; `results/design/duplication_report.md`; at M4: design branch, equivalence check, `PRE_EVENT_B` tag. |

---

### Out of scope at M1
- Retraining or fine-tuning any model; we use the authors' published per-record results.
- Models other than T5-small; ChatGPT results; the paper's literature review and model-size analysis.
- The project-level vs time-level statistical comparison (the pack's suggested RQ2, replaced by our approved RQ2).
- CodeBLEU and Levenshtein as decision metrics.
- Implementing the refactoring (M4, Week 9) and any Change Event material.

---

## 2. Bounded sample

| Element | Frozen value |
| --- | --- |
| Unit of analysis | RQ1 and RQ2a: one code-review record (code before the change, reviewer comment, code after the change). RQ2b: one source-file pair in `Cumulative_code` vs `Isolated_code`. |
| Source / version | Authors' GitHub repository (latest version dated 29 Sep 2025, accessed 11 Oct 2026); Zenodo record 10.5281/zenodo.17227729 v1. RQ1 input: `SplittedData/ProjectLevel/Gerrit_ProjectSplited_Test_NoLeakage.csv`. RQ1b results: `*_common_test_predictions_with_codeBLEU_10_ProjectLevel.csv` for T5-small. RQ2a input: the new GitHub test file in `NewGitHubData` (exact name to be confirmed once available). RQ2b: the 4 file pairs below. |
| Size / range | RQ1: **12 records** from the project-level test split. RQ2a: **12 records** from the new GitHub test set. RQ2b: **4 file pairs**: `Abstracter.py`, `Analyzer1.py`, `Analyzer2.py`, `Preprocessing_Pipeline.py`. Supporting record counts and statistics use the full splits via the authors' scripts (see note). |
| Selection rule | First 12 eligible records in each test file in stable file order (row index 0, 1, 2, …, as read by the authors' pipeline, which assigns a row-index ID). If the file has a case ID or chronological ID column, we sort by case ID, then file path, then chronological ID instead, and record which rule was used. Not chosen by outcome. **Eligible** = code-before, comment and code-after fields all non-empty. **Excluded** rows are listed in `data/excluded_rows.csv` with their reason. If fewer than 12 are eligible, all are used and this is recorded. Selected IDs are saved to `data/sample_ids.csv` and committed **before** any analysis. RQ2b: all 4 file pairs present in both folders; no selection. |
| Note on scope | Per-step counts are a property of the whole split, and a statistical test on 12 records has no power, so the paper's claims can only be compared at full-split level. These runs reuse the authors' scripts and outputs, with no new infrastructure. The sampled records are traced by hand through each step as the bounded, inspectable evidence. |

---

## 3. Method, metric and evidence route

### 3.1 Summary: inputs → procedure → output / decision

| | INPUTS | PROCEDURE | OUTPUT / DECISION |
| --- | --- | --- | --- |
| **RQ1a** | Project-level test CSV + authors' `Cumulative_code/` scripts + `utils/idioms.csv`. No extra filtering by us. | Run `Preprocessing_Pipeline.py` unchanged; T5-setting steps P1–P5; count records after each step; hand-trace the 12 sample records. | Records remaining/removed per step. **Compared with** paper Table 4. Exact match required. |
| **RQ1b** | Authors' published per-record results for T5-small, project-level split, one file per step. | Run `stats_EXM_all_steps.py` unchanged: Cochran's Q, pairwise McNemar with Holm correction, α = 0.05, EXM@10. | Verdict + direction. **Compared with** paper Figure 7 and reported tests. Same verdict + direction required. |
| **RQ2a** | New GitHub test set (`NewGitHubData`) + the same scripts. | Run `Preprocessing_Pipeline.py` unchanged on the new data; count records after each step; hand-trace 12 sample records. | Removal % per step, new data vs project-level split. Similar if within threshold (4.3). |
| **RQ2b** | The 4 file pairs in `Cumulative_code/` and `Isolated_code/`. | Measure duplication (line diff + clone detection) and complexity (`lizard`, cyclomatic complexity). Compare A (leave as is) vs B (extract shared module). At M4: implement B on a branch; run old and new versions on the same input. | Duplicated lines removed, complexity change, output equivalence. **Decision** by rule in 4.3. |

### 3.2 Detailed steps

**RQ1a – Records removed per step**
1. Run `Preprocessing_Pipeline.py` unchanged, setting only `input_csv_path` to the project-level test CSV.
2. Steps (S2): P1 method extraction → P2 comment pruning → P3 unchanged-method removal → P4 comment cleaning → P5 long method + comment removal (512-token limit).
3. Count records after each step (`*_Paper2_*` outputs) → `results/step_counts_projectlevel.csv`.
4. Trace the 12 sample records through every step by hand → `results/trace_audit.md`.

**RQ1b – Statistical conclusion**
1. Run `Results/StatisticalTests/stats_EXM_all_steps.py` unchanged on the T5-small project-level results.
2. Cochran's Q across steps, pairwise McNemar with Holm correction, α = 0.05; metric EXM@10 (column `EXM10`, line 40).
3. Outputs → `results/stats_rq1/`.

**RQ2a – Transfer to new data**
1. Run the same pipeline unchanged with `input_csv_path` set to the new GitHub test file.
2. Count records after each step → `results/step_counts_newdata.csv`.
3. Compute removal % per step for both datasets → `results/rq2_transfer_comparison.csv`.
4. Trace the 12 new-data sample records by hand.

**RQ2b – Design decision**
1. Measure duplication for each file pair with `diff` and a clone detector (e.g. PMD CPD or jscpd) → `results/design/duplication_report.md`.
2. Measure size and average cyclomatic complexity of both folders with `lizard`.
3. Option A (no change): record the baseline and the maintenance risk (every fix must be made twice).
4. Option B (extract shared module, at M4): move shared code into one module, with any real differences (e.g. the 45 lines in `Analyzer2.py`) kept as a parameter; both pipelines import it.
5. Verify B: run the original and refactored pipelines on the same input and compare output row counts and SHA-256 hashes of every output CSV.
6. Apply the decision rule (4.3) and record the choice.

### 3.3 Bounded decisions

Where the paper or artefact does not specify something, we decide it now so it cannot change after we see results.

| Decision | What we will do | Why |
| --- | --- | --- |
| Model | T5-small only (paper's S2 setting: "a standard encoder-decoder Transformer architecture T5-small", 6 layers, 8 heads, d_model 512, from Tufano et al. 2022) | The paper reports a preprocessing finding for it, and the pipeline has dedicated outputs for it |
| Setup | Cumulative preprocessing only for RQ1 and RQ2a | One bounded preprocessing chain |
| Metric | EXM@10 (any of the top 10 predictions matches) | The paper's text does not say top-1 or top-10; the authors' statistics code uses `EXM10` |
| Retraining | None; we use the authors' published results | T5 checkpoints are not needed (and are not in the repository despite the README) |
| Significance level | α = 0.05 | Matches the authors' scripts |
| Script changes | Run unchanged for RQ1 and RQ2a; any edit needed just to make them run is committed separately and recorded in the change log | Keeps the reproduction faithful and auditable |
| Equivalence input (RQ2b) | The authors' project-level test data if available; otherwise a small constructed input file, recorded as a deviation | Equivalence must be checked on identical input for both versions |
| Environment | Python [VERSION]; library versions recorded in `requirements.txt` | The authors provide no environment file; differences are reported, not hidden |
| Artefact version | Authors' GitHub repository and Zenodo record as accessed on 11 Oct 2026 | If either changes later, we keep using this version and note the change |

---

## 4. Expected result and decision rule

### 4.1 Expected result (written before any execution)

| RQ | Type of claim | What we expect to see |
| --- | --- | --- |
| **RQ1a** | Count (deterministic) | Per-step record counts on the project-level test split are **identical** to paper Table 4. The pipeline has no randomness. |
| **RQ1b** | Statistical difference + direction | The same verdict as the paper. The paper states that "T5's Precision shows only a weak dependence on cumulative preprocessing", so we expect EXM@10 to vary only modestly across steps, with the same step pairs (if any) significant and the same best step(s) as Figure 7. |
| **RQ2a** | Transfer (similarity of removal rates) | Broadly similar removal rates on the new data, since the same deterministic rules are applied. Some steps may differ because GitHub pull requests differ from Gerrit reviews in format. |
| **RQ2b** | Design decision | Option B is worth doing for the shared analysis code (`Abstracter.py` is identical and `Analyzer1.py` differs by one line), with the pipeline scripts kept separate because they genuinely differ. |

### 4.2 Decision rule

| RQ | REPRODUCED / POSITIVE | NOT REPRODUCED / NEGATIVE | INCONCLUSIVE / BLOCKED |
| --- | --- | --- | --- |
| **RQ1a** | Every per-step record count matches Table 4 **exactly**. | A valid completed run gives **any** step count that differs. | Pipeline cannot run, input data or `utils/` files unavailable, or Table 4 lacks comparable counts. |
| **RQ1b** | Same Cochran's Q verdict (α = 0.05) **and** same direction (best step(s), significant pairs) as the paper. | A valid completed run gives a different verdict or direction. | Results files or statistics script unavailable or unrunnable, or the paper does not report comparable results. |
| **RQ2a** | **Same behaviour:** every step's removal % on the new data is within 10 percentage points of the project-level split. | **Different behaviour:** any step differs by more than 10 percentage points; reported per step. | New data unavailable or pipeline cannot run on it. |
| **RQ2b** | **Restructure (B):** removes ≥ 50% of duplicated lines **and** output identical (row counts + file hashes) **and** average cyclomatic complexity does not rise by more than 10%. | **Leave as is (A):** any of those three conditions fails. A no-change decision backed by evidence is a valid outcome. | Equivalence cannot be tested because no input can be run through both versions. |

**Partial results:** if some steps match and others do not, the RQ is recorded as NOT REPRODUCED / different behaviour, and we list exactly which steps differed and by how much. We do not average over steps to make a mismatch disappear.

**Important:** a failed build, missing dependency or inaccessible dataset is **not** NOT REPRODUCED. It is INCONCLUSIVE / BLOCKED until we have a valid result to compare.

### 4.3 Bounded decisions for interpreting results

| Decision | Rule | Why |
| --- | --- | --- |
| Significance level | α = 0.05, with the authors' Holm correction for pairwise tests | Matches the authors' scripts |
| Count match (RQ1a) | Zero tolerance | The pipeline is deterministic; a tolerance would hide real differences |
| "Same behaviour" (RQ2a) | Within 10 percentage points per step | The paper gives no threshold; 10 points allows for natural differences between Gerrit and GitHub data while catching a step that behaves differently |
| "Worth doing" (RQ2b) | ≥ 50% duplicated lines removed, identical output, complexity rise ≤ 10% | Restructuring is only justified if it substantially reduces duplication without changing behaviour or adding complexity |
| No result-fitting | Thresholds, metrics and sample are **not** changed after seeing output; any genuine change goes in the change log with a reason | Lab 3 rule: freeze before results can move the goalposts |

### 4.4 Current status

- **RQ1 and RQ2a: INCONCLUSIVE / BLOCKED (data availability).** The input data, the new GitHub data and the per-record results are not available from the authors' Zenodo record (section 5).
- **RQ2b: feasible.** It needs only the code, which is available and compiles. Output equivalence will use the authors' data if it becomes available, otherwise a constructed input (section 3.3).

---

## 5. Feasibility check (11 Oct 2026)

**Goal (Lab 3 brief):** confirm the released artefact and data can be accessed and that the first essential step of the method is executable, recording any blocker with concrete evidence and what we tried.

**First essential step:** load the project-level test CSV and run `Preprocessing_Pipeline.py` on it (RQ1a).

### 5.1 Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Paper accessible | OK | Springer, open access (link in section 0) |
| Authors' repository accessible | OK | Cloned from GitHub. Latest commit `d1e9692`, 29 Sep 2025 (re-checked 11 Oct 2026: no newer version) |
| Pipeline and statistics code present | OK | `Preprocessing/Cumulative_code/` and `Isolated_code/` (4 scripts each); `Results/StatisticalTests/` (4 scripts) |
| Code compiles | OK | All pipeline and statistics scripts compile under Python 3 (`python -m py_compile`). One harmless warning in `Analyzer2.py` line 1158 (escape sequence) |
| Input data in repository | BLOCKED | `Preprocessing/SplittedData/`, `Preprocessing/NewGitHubData/`, `Results/csvResults/` and `Results/FinalRatios/` contain 0 data files. README says to download their contents from Zenodo |
| Zenodo record contents | BLOCKED | Record 10.5281/zenodo.17227729 (open, CC-BY 4.0, "content of dataset subfolders in replication package"): only version v1, one file, `FinalRatios.zip` (45.5 kB). No split CSVs, no new GitHub data, no per-record results, no other versions or linked records |
| Pipeline input file (RQ1) | BLOCKED | `Preprocessing_Pipeline.py` line 33 expects `SplittedData/ProjectLevel/Gerrit_ProjectSplited_Test_NoLeakage.csv`. Not available anywhere |
| New GitHub data (RQ2a) | BLOCKED | `Preprocessing/NewGitHubData/` is empty and the data is not on Zenodo |
| Helper folder `utils/` | BLOCKED | Not in repository. Code references `utils/idioms.csv` (`Preprocessing_Pipeline.py` line 136), `utils/is_relevant.sh` (`Analyzer2.py`), `utils/abstract.sh` and `utils/src2abs-0.1-jar-with-dependencies.jar` (`Abstracter.py`, Java tool) |
| Statistics inputs (RQ1b) | BLOCKED | All four statistics scripts read `*_predictions_with_codeBLEU_10_*.csv`. Not in repository or on Zenodo |
| Design analysis (RQ2b) | OK | Both code folders present; duplication baseline measured (section 2) |
| Software environment | RISK | No `requirements.txt` or environment file from the authors. Imports include pandas, numpy, scipy, statsmodels, seaborn, lizard, langdetect, langid, cld3, textblob, aeon |

### 5.2 What we tried

1. Cloned the authors' repository and confirmed the latest version (`git log -1`, `git ls-remote`).
2. Checked every data folder named in the README; all are empty.
3. Followed the README's Zenodo link; checked the file list, the Versions section and related records.
4. Searched the repository for the missing input files, `utils/` folder and results files; none found.
5. Compiled all pipeline and statistics scripts to confirm the code itself is intact.
6. Measured the duplication between `Cumulative_code` and `Isolated_code` with `diff`.
7. Emailed the authors on [DATE] asking where the data and `utils/` files are published.
8. Raised the blocker with the lab coordinator to agree a contingency route.

**Evidence files:** `results/feasibility/zenodo_files.png`, `results/feasibility/readme_zenodo_link.png`, `results/feasibility/empty_folders.png`.

### 5.3 Status and next step

**Status: RQ1 and RQ2a BLOCKED (data availability); RQ2b feasible.** Under the Lab 3 brief, missing data is a feasibility problem, not a NOT REPRODUCED result.

Candidate contingency routes for RQ1 and RQ2a, to be agreed with the coordinator and **not** chosen by us after seeing any results:
1. Reproduce the aggregated results using `FinalRatios.zip` (the only data published).
2. Run the pipeline on the original public Tufano et al. dataset, recreating the project-level split as documented in the paper.
3. Wait for the data from the authors and keep this plan unchanged.

---

## 6. Known deviations from the paper

- One model only (T5-small); cumulative setup only; no retraining.
- Bounded 12-record audits alongside full-split counts and statistics.
- RQ2b is our own design analysis of the artefact, not a claim from the paper.
- [Any contingency route agreed with the coordinator.]

---

## 7. AI use

GenAI helped interpret the brief, draft this plan's structure.

---

## Change log

Any change after the M1 freeze is recorded here with the date, what changed, why, and how it affects interpretation of later evidence. Earlier wording is kept, not rewritten.

| Date | Change | Reason | Effect on interpretation |
| --- | --- | --- | --- |
| 20 Oct 2026 (recorded 28 Oct 2026) | Week 6 contingency: checked the authors' published T5-small values in `FinalRatios.zip` against the paper's Figure 7(c) (see `REPRODUCTION.md`, Steps 2–7). | Input data, new GitHub data and per-record results are not published; `FinalRatios.zip` is the only file on Zenodo (`results/week6/blocker_evidence.txt`). | A check of published numbers only, not an independent reproduction. Status: INCONCLUSIVE. Row added late; the original plan text above is unchanged. |
| 28 Oct 2026 | Input replaced with 12 real code-review cases mined from GitHub pull requests in 3 Java projects (4 per project, P29 stable order within each project). Raw is compared with two of the authors' own steps (`removeComments`, `clean_comment_without_abstraction`) using one fixed LLM, prompt and metric. Full details: `docs/DEVIATION_02_alternative_dataset.md`; code: `m2_altdata/`; tag `M1_DEVIATION_2`. | Approved by Abdul (coordinator) by email on 22 Oct 2026 after he confirmed the missing input data. | Alternative data: the paper's exact numbers are not expected; only the direction of the effect is compared. Table 4 record-count check stays BLOCKED. Duplicated-code design part of RQ2 is unaffected. |
