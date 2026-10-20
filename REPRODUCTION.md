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

**Limitation:** I was able to check that the result in my CSV matched the authors' published result. However, I couldn't check how they originally calculated it because the dataset and other files needed to run their preprocessing code were missing.


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