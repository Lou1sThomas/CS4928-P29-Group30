# CS4928 P29 – Reproduction Log (Group 30)

This log has two parts:

- **Part A – Week 6 (Lab 4):** the contingency check on the authors' published results. Kept as written; only broken characters and one wrong folder name were fixed on 28 Oct.
- **Part B – M2:** the reproduction on alternative GitHub data that the group is now using (Padraig's route, chosen 28 Oct 2026).

---

# Part A – Week 6 (Lab 4): check of the authors' published results

## Step 1 – Re-open the frozen M1 contract

### What M1 froze, and whether it can run as frozen

| M1 item | What M1 froze (PLAN.md section) | Can it run as frozen? |
| --- | --- | --- |
| **RQ + target** | **RQ1:** does the authors' code and data on the project-level test split give the same per-step record counts as Table 4 and the same statistical conclusion for T5-small ("only a weak dependence on cumulative preprocessing")? **RQ2:** does the pipeline behave the same on the authors' new GitHub data, and is restructuring its duplicated code worth doing? | **RQ1 PARTLY:** the record counts and significance tests cannot run (data not published), but the per-step summary results for T5-small are published in `FinalRatios.zip`. **RQ2 PARTLY:** the transfer part is BLOCKED (new data not published); the design part needs only the code, which is available. |
| **Bounded sample** | Unit: one code-review record (RQ1, RQ2 transfer); one source-file pair (RQ2 design). Source: authors' repo (29 Sep 2025) + Zenodo v1. Size: 12 records per test file; 4 file pairs. Rule: first 12 eligible in stable file order; exclusions listed in `data/excluded_rows.csv` (§2) | **PARTLY.** No record-level file exists to sample from for RQ1 or the RQ2 transfer part. The 4 file pairs are available. |
| **Method** | Run the authors' pipeline and statistics scripts unchanged on the published data; measure duplication and complexity of the 4 file pairs (§3) | **PARTLY.** Scripts are present and compile but have no input data. The design measurement can run. |
| **Metric / result** | Per-step record counts (RQ1); EXM@10 with Cochran's Q + McNemar, α = 0.05 (RQ1); removal % per step (RQ2 transfer); duplicated lines, cyclomatic complexity, output hashes (RQ2 design) (§3–4) | **PARTLY.** Counts, tests and removal % need missing data. Per-step EXM10, sizes, precision, recall and F1 are available as published summaries. Design metrics can be measured. |
| **Decision rule** | RQ1: exact counts and same verdict + direction. RQ2: within 10 points per step; restructure only if ≥50% duplication removed, identical output, ≤10% complexity rise. Missing data = BLOCKED (§4.2–4.3) | **YES, unchanged.** An extra rule is needed for the FinalRatios check; it goes in the Change log before any run. |
| **Held-out boundary** | No Event / held-out material | **YES.** Only the authors' public repository and Zenodo files are used. |

## Step 2 – Prepare one traceable run
See `REPRODUCTION.md`, Step 2.

## Step 3 – Pilot on one file
The pilot used the published T5-small project-level summary file `FinalRatios/csvResultsS2T5/final_results/ProjectLevel_test.csv`, extracted from the authors' Zenodo archive.

PowerShell `Import-Csv` was used to select the S2_P1 configuration and read its Size and EXM10 columns.

**Pilot result**
Configuration: S2_P1
Size: 61,562
EXM10: 14.799714109353173

The pilot extracted the expected summary row without errors.
**Evidence:** `results/week6/pilot_output.txt`
**Limitation:** This is an extraction of published aggregate results, not an independent execution of the authors' preprocessing pipeline or statistical tests.

## Step 4 – Full bounded run
We couldn't run the original preprocessing experiment because some of the files needed were missing from the authors' repository and Zenodo.

Instead, we used the `FinalRatios.zip` file from Zenodo, which contains the authors' published results. We extracted the file and used PowerShell to get the T5-small results from `ProjectLevel_test.csv`.

All the results were saved into `results/week6/t5_small_summary.csv` (folder name corrected from "week7" on 28 Oct). We checked the file to make sure the results were saved correctly.

**Evidence:** `results/week6/t5_small_summary.csv` and screenshots showing the results in PowerShell and VS Code.
**Limitation:** We only extracted the authors' existing results. We didn't run their original preprocessing code or statistical tests because the required files were missing.

## Step 5 – Evidence chain (one value traced back)
We checked one of the T5-small results to show where it came from: the S2_P1 configuration in the authors' `ProjectLevel_test.csv`, from `FinalRatios.zip` on Zenodo. We checked the value again in our saved `t5_small_summary.csv` using PowerShell.

Step: S2_P1
Size: 61,562
EXM10: 14.799714109353173

The value matched the one extracted earlier, so it had been saved correctly.

**Evidence:** `results/week6/t5_small_summary.csv` and `results/week6/step5-evidence_chain.png`.
**Limitation:** This checks a published summary value. It doesn't trace an individual prediction through the preprocessing pipeline.

## Step 6 – Comparison with the original study
See `REPRODUCTION.md`, Step 6.

## Step 7 – Current status
See `REPRODUCTION.md`, Step 7 (Week 6 status: INCONCLUSIVE – published numbers only).

## Step 8 – Next action before M2
Done: the coordinator approved an alternative dataset on 22 Oct 2026. See Part B.

---

# Part B – M2: reproduction on alternative GitHub data

> **We are using alternative data.** The authors never published their input data, so these are real code reviews we mined ourselves. We do not expect to match the paper's exact numbers; we check whether the paper's direction of effect holds.

## B0. Why the route changed, and which route we use

- **Missing data:** the authors' input data, their new GitHub test set and their per-record results were never published (Zenodo only has `FinalRatios.zip`; the data folders in their repo are empty). Evidence: `results/week6/blocker_evidence.txt`.
- **Approval:** Abdul (coordinator) checked this and approved a small alternative dataset by email on **22 Oct 2026**. He asked for real, traceable code reviews from more than one Java project, the P29 sampling rule, one or two of the authors' preprocessing steps, and raw vs cleaned compared with the same model and evaluation.
- **Two routes were prepared in parallel on 28 Oct.** TWe chose (`m2_scripts/`, `m2_data/`, `m2_run/`). It runs the authors' own preprocessing pipeline and the same kind of model the paper used (T5-small). Our cases were mined and committed at 15:11, before the other route was frozen at 15:28.
- **The other route** (`m2_altdata/`, `docs/DEVIATION_02_alternative_dataset.md`, tag `M1_DEVIATION_2`; qwen2.5-coder on 3 projects) is **kept but was not run**. It is not used for M2 results.
- The original M1 plan (`PLAN.md`, tag `M1_PLAN`) is unchanged. All changes are recorded in the `PLAN.md` change log.

## B1. Step 1 – M1 contract as applied to the new data

| M1 item | What we run in M2 |
| --- | --- |
| **RQ1** | Does cleaning the input change T5-small's revision success? Compare **raw** vs **cleaned** on the same 12 cases. Paper's claim: T5-small shows only a weak dependence on preprocessing. |
| **RQ2 (transfer)** | Does the authors' pipeline remove a similar share of records at each step on new GitHub data as in Table 4? |
| **RQ2 (design)** | Unchanged; done later on the authors' code. |
| **Sample** | Unit: one GitHub review comment on a `.java` file in a merged PR. P29 rule: first 12 eligible items in stable order (case ID, then file path, then time). |
| **Method** | Authors' `Cumulative_code` pipeline, run on our mined data with only the input path and data type changed. |
| **Metric** | EXM@1/3/5/10 and Levenshtein (authors' evaluation code); exact McNemar test on EXM@10. RQ2: % removed per step. |
| **Decision rule** | M1 rule, unchanged. RQ1: same verdict and direction as the paper (McNemar, α = 0.05). RQ2 transfer: each step within 10 points of Table 4. |
| **Held-out** | No Event / held-out material used. |

## B2. Step 2 – One traceable run

### Input identity
- **Projects:** `apache/commons-io` and `apache/commons-lang` (both Maven Java projects with JUnit tests).
- **Pool:** 60 review comments, 30 per project, from merged PRs, `.java` files only, in creation order. The earliest is dated 4 Sep 2021 and the latest 14 May 2022. Listed in `m2_data/data/pool_ids.csv`.
- **Raw mined data:** `m2_data/data/sampleM2_raw.csv`, plus one file per project in `m2_data/data/parts/`. Each row has the comment, its GitHub URL, author, line, the commit it was made on, and the full source file at three points: the PR base, the commit the comment was made on, and the PR's final commit (the revised code).
- **Integrity:** SHA-256 hashes in `m2_data/data/m2/SHA256SUMS.txt`. All 6 files were checked on 28 Oct 2026 and match.
- **Earlier sample, not used:** a first sample of 50 comments (Sep 2020 – Aug 2021) left only 2 records after the pipeline. It is kept in `m2_data/data/superseded_sampleA_2020-21/` and not used for results.

### Environment
- **Pipeline:** Python 3.10–3.12 with `m2_scripts/requirements-pinned.txt` (pandas 2.3.3, numpy 2.2.6, lizard 1.24.3, langdetect, textblob, langid, regex, tqdm).
- **Model:** `m2_scripts/requirements-model.txt` (torch 2.14.1, transformers 5.21.0, sentencepiece 0.2.2, python-Levenshtein 0.27.5).
- **Model files:** Tufano et al. 2022 T5 checkpoint "pre-trained, new large dataset, code&comment-to-code" and its tokenizer, from Zenodo 10.5281/zenodo.5387856. MD5s are recorded in `models/SOURCE.txt`. The model files are not committed because of their size. No fine-tuning or retraining.

### Execution route
Everything re-runs from the repository root with one script:

```bash
bash m2_scripts/reproduce_m2.sh
```

It does three things:
1. builds the two Python environments;
2. runs the authors' pipeline on the frozen 60-comment pool (`setup_run.sh` → `run_pipeline_fork.py` → `make_raw_clean.py`) and checks the outputs are identical to the frozen files in `m2_data/data/m2/`;
3. runs T5-small on raw and cleaned (`run_t5_eval.py`) and compares them (`compare_raw_clean.py`).

Mining is done once, separately: `m2_scripts/mine_github_reviews.py`, then `combine_samples.py`.

### Changes needed to run the authors' code (no change to the method)
- Two configuration lines only: input file → our CSV, and `data_type` `'Gerrit'` → `'GitHub'`. See `m2_run/REPRO_M2/config_changes.diff`.
- `idioms.csv` and `stop-words-english.txt` are copied from elsewhere in the authors' own repo (`Training_and_Testing/...`) into the `utils/` folder the pipeline expects.
- `pycld3` will not install, so it is replaced by a stub (`m2_scripts/cld3_stub.py`). The authors' `is_english()` returns True on every path, so this cannot change the output.
- Two empty files the pipeline copies (`pipeline.py`, `run_pipeline.sh`) are created.
- The pipeline is started with the "fork" method (`run_pipeline_fork.py`), as on the authors' Linux setup.
- The abstraction tool `src2abs` jar is not in the authors' repo, so the abstraction steps (used by the other models, not T5) produce no records. **This does not affect the T5 (S2) route.**

## B3. Step 3 – Pilot
- **First attempt failed:** the pipeline stopped because `./utils/stop-words-english.txt` was missing (`m2_run/_failed_attempt1_SampleA_first12/Cumulative_code/error_log.txt`). This was an ordinary file-path fault. It was fixed by copying the authors' own stop-word file, and the failed attempt is kept.
- **Pilot after the fix:** `m2_run/GitHub_SampleA_first12/` ran end to end and produced the expected output files.

## B4. Step 4 – Full bounded run

**Pipeline run on the 60-comment pool:** `m2_run/GitHub_M2_pool60/run_stdout.log`. **Independent re-run:** `m2_run/REPRO_M2/run_stdout.log`. Both give the same record counts at every step for T5 (S2):

| Step | Records before | Records after |
| --- | --- | --- |
| P1 Method extraction | 60 | 23 |
| P2 Comment pruning | 23 | 10 |
| P3 Unchanged-method removal | 10 | 8 |
| P4 Comment cleaning | 8 | 8 |

**Building the evaluation set** (`m2_scripts/make_raw_clean.py`):
- **Raw** = the authors' P1 output: the method with the commented lines marked, the reviewer's comment as written, and the revised method.
- **Cleaned** = the same records passed through the authors' own P4 comment cleaning (`Analyzer2.analyze_wo_abs` and `info_for_cleaning_paper2`, called the same way the pipeline calls them).
- **Eligible** = present in both raw and cleaned with non-empty code, comment and target: **21** (13 commons-lang, 8 commons-io).
- **Excluded:** 39, each with a reason in `m2_data/data/m2/excluded_rows.csv`. 37 had no method-level record at P1, and 2 had a comment judged irrelevant at P4.
- **P29 rule:** sort eligible items by review comment ID, then file path, then time, and take the first 12. The result is `m2_data/data/m2/sample_ids.csv`: **8 commons-io, 4 commons-lang**.
- **Model inputs:** `m2_data/data/m2/eval_raw.csv` and `eval_cleaned.csv` (12 rows each, same cases).

**T5-small on raw and cleaned:** `run_t5_eval.py` uses beam search with 10 beams and the authors' own scoring functions, loaded unchanged from their `FineTuning_and_Testing.py`.

> **Not yet committed:** the T5 outputs (`predictions_raw.csv`, `predictions_cleaned.csv`, `per_case_comparison.csv`, `summary.csv`). `reproduce_m2.sh` expects them in `Results/m2_raw_vs_clean/`, but that folder is not in the repository yet.

## B5. Step 5 – Evidence chain (case #1)

| Link | Where |
| --- | --- |
| GitHub review | https://github.com/apache/commons-io/pull/278#discussion_r717135976 – "use final where you can." on `BrokenInputStreamTest.java` |
| Mined record | `m2_data/data/sampleM2_raw.csv`, comment ID 717135976 (Record_id 5) |
| Pipeline run | `m2_run/REPRO_M2/run_stdout.log` and the `Chunk_0000` outputs |
| Selection | `m2_data/data/m2/sample_ids.csv`, P29 rank 1 |
| Raw input | `eval_raw.csv`, rank 1: comment "use final where you can." |
| Cleaned input | `eval_cleaned.csv`, rank 1: comment "final" |
| Model output and score | `predictions_raw.csv` / `predictions_cleaned.csv`, rank 1 → `summary.csv` (**to add once the T5 outputs are committed**) |

## B6. Step 6 – Comparison with the original study

**RQ2 transfer (removal % per step).** Computed with `m2_scripts/compare_removal_rates.py` from `m2_run/REPRO_M2/run_stdout.log`, against Table 4 (S2, project-level test):

| Step | Ours (% removed) | Paper (% removed) | Difference | Within 10 points? |
| --- | --- | --- | --- | --- |
| P2 | 56.5 | 69.3 | −12.7 | No |
| P3 | 20.0 | 28.2 | −8.2 | Yes |
| P4 | 0.0 | 7.7 | −7.7 | Yes |

P1 has no baseline, because Table 4 reports counts after P1. Under the M1 rule, P2 falls outside 10 points, so the transfer is **not reproduced at P2** on our data. The counts are very small (23 → 10 records), so this is a descriptive result, not a strong one.

**RQ1 (raw vs cleaned, T5-small).** Waiting for the T5 outputs. The M1 rule will be applied to `summary.csv` once they are committed.

**Observation from the inputs.** The authors' comment cleaning removes stop-words, including "not". In two of the 12 cases this reverses the reviewer's meaning:
- case 5: "the `out` variable is **not** needed imo" → "the out variable is needed imo"
- case 9: "this one is **not** really necessary" → "this is necessary ?"


## B7. Step 7 – Current status

| RQ | Status | Why |
| --- | --- | --- |
| RQ1 raw vs cleaned | **IN PROGRESS** | Data, preprocessing and model inputs are done, frozen and hashed. The T5 outputs are not committed yet, so the decision rule cannot be applied. |
| RQ2 transfer | **NOT REPRODUCED at P2** (P3, P4 consistent) | M1 rule applied to the pipeline log. Bounded, alternative data, very small counts. |
| RQ2 design | Not started for M2 | Unaffected by the data change; planned for later. |

**Main threats**
- Only 12 cases, so one case moves EXM by about 8 points.
- The projects are uneven: 8 cases from commons-io and 4 from commons-lang.
- 3 of the 12 cases are on test files (ranks 1, 6 and 7).
- The reviews are from 2021–22 and may overlap the T5 checkpoint's training data.
- Different data from the paper, so only the direction of the effect is comparable.

## B8. Step 8 – Next actions
1. Our commits the T5 outputs to `Results/m2_raw_vs_clean/` (`predictions_raw.csv`, `predictions_cleaned.csv`, `per_case_comparison.csv`, `summary.csv`).
2. Apply the M1 rule to `summary.csv` and update B5–B7.
3. `requirements.txt` refers to an `M2_NOTES.md` that is not in the repo. Add it, or change the reference to this file.
4. Add the change-log row to `PLAN.md` recording that Padraig's route was chosen.
5. Push `main` and the tags.
