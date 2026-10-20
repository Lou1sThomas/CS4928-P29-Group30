# CS4928 P29 – Week 6 Reproduction Log (Lab 4)

## Step 1 – Re-open the frozen M1 contract

### What M1 froze, and whether it can run as frozen

| M1 item | What M1 froze (PLAN.md section) | Can it run as frozen? |
| --- | --- | --- |
| **RQ + target** | **RQ1:** does the authors' code and data on the project-level test split give the same per-step record counts as Table 4 and the same statistical conclusion for T5-small ("only a weak dependence on cumulative preprocessing")? **RQ2:** does the pipeline behave the same on the authors' new GitHub data, and is restructuring its duplicated code worth doing?  | **RQ1 PARTLY:** the record counts and significance tests cannot run (data not published), but the per-step summary results for T5-small are published in `FinalRatios.zip`. **RQ2 PARTLY:** the transfer part is BLOCKED (new data not published); the design part needs only the code, which is available. |
| **Bounded sample** | Unit: one code-review record (RQ1, RQ2 transfer); one source-file pair (RQ2 design). Source: authors' repo (29 Sep 2025) + Zenodo v1. Size: 12 records per test file; 4 file pairs. Rule: first 12 eligible in stable file order; exclusions listed in `data/excluded_rows.csv` (§2) | **PARTLY.** No record-level file exists to sample from for RQ1 or the RQ2 transfer part. The 4 file pairs are available. |
| **Method** | Run the authors' pipeline and statistics scripts unchanged on the published data; measure duplication and complexity of the 4 file pairs (§3) | **PARTLY.** Scripts are present and compile but have no input data. The design measurement can run. |
| **Metric / result** | Per-step record counts (RQ1); EXM@10 with Cochran's Q + McNemar, α = 0.05 (RQ1); removal % per step (RQ2 transfer); duplicated lines, cyclomatic complexity, output hashes (RQ2 design) (§3–4) | **PARTLY.** Counts, tests and removal % need missing data. Per-step EXM10, sizes, precision, recall and F1 are available as published summaries. Design metrics can be measured. |
| **Decision rule** | RQ1: exact counts and same verdict + direction. RQ2: within 10 points per step; restructure only if ≥50% duplication removed, identical output, ≤10% complexity rise. Missing data = BLOCKED (§4.2–4.3) | **YES, unchanged.** An extra rule is needed for the FinalRatios check; it goes in the Change log before any run. |
| **Held-out boundary** | No Event / held-out material | **YES.** Only the authors' public repository and Zenodo files are used. |


## Step 2 – Prepare one traceable run
### Input identity
### Environment
### Execution route

## Step 3 – Pilot on one file
The pilot used the published T5-small project-level summary file FinalRatios/csvResultsS2T5/final_results/ProjectLevel_test.csv, extracted from the authors' Zenodo archive

PowerShell Import-CSV was used to select the S2_P1 configuration and read its Size and EXM10 columns.

**Pilot Result**
Configuration: S2_P1
Size: 61,562
EXM10: 14.799714109353173

The pilot successfully extracted the expected summary row without errors.
Evidence: results/week7/pilot_output.txt
Limitation: This is an extraction of published aggregate results, not an independent execution of the authors preprocessing pipeline or statisical tests.


## Step 4 – Full bounded run

## Step 5 – Evidence chain (one value traced back)

## Step 6 – Comparison with the original study

## Step 7 – Current status

## Step 8 – Next action before M2