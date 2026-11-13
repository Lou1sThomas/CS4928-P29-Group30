# P29 Event B — Hidden dependencies in a neighbouring module

**Group:** 30 / P29  
**Operator:** Tadhg Austin  
**Report prepared:** 12 November 2026  
**Status:** Prediction, case selection, evaluation and response completed. Tracker columns Q–R filled.

## 1. What we were trying to find out

Event B's pressure is that the next pull request contains a change whose correctness depends on a neighbouring module not present in the minimal diff. We had to determine whether our preprocessing and context policy hides or preserves that dependency, and to revise our design only if justified.

Our pre-Event-B state is the Week 9 decision frozen at the `PRE_EVENT_B` tag. In Event A flattening code before removing `//` comments could delete the rest of a reference method. We kept the original results and added a separate complete-reference check, which scores raw and cleaned predictions against the same verified reference. Our pipeline follows the authors' T5/S2 setting: P1 method extraction gives the model only the method containing the review comment, so Event B tests whether this is adequate when a revision relies on code outside that method.

## 2. Our prediction

We predict the new pressure will mainly affect model-input preparation rather than our Week 9 complete-reference check. Our pipeline gives the model only the method containing the review comment, so code the change depends on elsewhere is left out. Raw and cleaned both use the same method extraction, so we expect the dependency to be hidden in both conditions. Our Week 9 check controls how answers are scored, so we expect it to keep raw and cleaned scoring consistent. However, it also works at method level, so it cannot show whether the neighbouring change was needed. We therefore expect the Week 9 decision to be only partly supported: correct for scoring, but not covering hidden dependencies. This prediction would be challenged if the dependency turned out to be visible in the extracted method, or if the complete-reference check gave different results for raw and cleaned on this case.

## 3. Data and case selection

We mined 30 review comments on Java files in merged pull requests from `apache/commons-lang`, one of the two M2 projects, using the same script as M2 and Event A:

```bash
python3 m2_scripts/mine_github_reviews.py --sample EventB --start 2022-05-15 --end 2023-12-31 \
    --repos apache/commons-lang --per-repo 30 --out data/event_b
```

The window starts after the M2 cases so no pull request appears in both samples. We ran the authors' preprocessing pipeline and built raw and cleaned versions as in M2. Of the 30 comments, 22 produced no method-level record in P1 and 2 exceeded the 512-word limit, leaving 6 eligible cases, all test methods from pull requests #892 and #904. With fewer than 12 eligible, all 6 were used under the P29 rule.

We selected the case with the rule "the first case in P29 order whose commented method calls a declaration that is changed in another file of the same pull request, confirmed by manual inspection". A helper script (`flag_sample_dependencies.py`) flagged ranks 1 and 2 (PR #892, which changes `DateUtils.java`) and none of ranks 3–6. Therefore rank 1 (PR #892, comment 873211413) is the Event B case.

## 4. Manual dependency check

We checked the case by hand on GitHub (final commit `92b5f8e`) and in our evaluation files:

- **Does the pull request change a neighbouring file the method uses?** Yes. `DateUtils.java` adds `getStandaloneLongMonths(Locale)` (lines 1840–1842), which the test method `testGetStandaloneLongMonthNames` calls.
- **Is that code missing from the model's input?** Yes, in both versions. The raw and cleaned inputs contain only the test method; the call is visible, but not what the method returns, so the model cannot check whether the twelve expected month names are correct.
- **Does acting on the review comment need the hidden code?** No. The comments ask for a local variable to be renamed (rank 1) and for a local variable to be inlined (rank 2). Both are local edits.

PR #904 changes only test files and its comments concern whitespace and local variables, so ranks 3–6 were correct to not be flagged.

## 5. Evaluation and results

We used the same Tufano T5 checkpoint, evaluation script and decoding settings as M2 and Event A. We rebuilt the model from Zenodo record 5387856 and verified it by rerunning M2: 6/12 raw and 5/12 cleaned, with all 24 prediction sets identical to Event A's saved M2 run. The complete-reference check script was not in the repository, so we rebuilt it using Gen AI from Event A's description; it reproduced the committed Event A and M2 results exactly before we used it.

| Dataset and version | Original EXM@10 | Complete-reference EXM@10 |
|---|---:|---:|
| M2 — raw / cleaned | 6/12 / 5/12 | 5/12 / 5/12 |
| Event A — raw / cleaned | 2/12 / 0/12 | 2/12 / 0/12 |
| **Event B — raw / cleaned** | **2/6 / 1/6** | **1/6 / 1/6** |

**The Event B case (rank 1) did not match in either condition under either scorer.** In raw, four of the first five candidates attempted the requested rename, but only on the declaration, leaving the code uncompilable. In cleaned, comment cleaning had split the arrow -> into - > and removed the question mark, and no candidate attempted the rename. All candidates in both conditions also corrupted the string `"August"`, and the merged code never applied the rename, so even a correct rename would have been scored as wrong.

**Rank 5's raw match was false.** Its reference had been cut down to the method's first line by the same `//` problem found in Event A. Against the complete reference, it does not match.

## 6. Conclusion on the Week 9 decision

The Week 9 decision is partly supported as we predicted. The complete-reference check was correct for the problem it was designed for: on Event B it gave consistent raw and cleaned results and removed the false rank 5 match. We keep it unchanged. It cannot reveal the new pressure, however, because it only checks the method being scored. Neither challenge condition in our prediction occurred.

Hidden dependencies were not new. Running the same dependency check on the frozen samples flagged 3 of 12 M2 cases and 0 of 12 Event A cases. In every flagged case, a test method calls main code changed in the same pull request.

## 7. Responses considered and chosen response

| Option | Main trade-off |
|---|---|
| 1. No change: report the limitation | Cheap but hidden dependencies stay invisible in future results |
| 2. Add neighbouring code to the model input | Could expose the dependency, but does not match the checkpoint's training format and risks the 512-token limit|
| 3. Keep the input and results and add a separate dependency audit | Makes the problem visible without changing results, but does not fix it, and adds a step that must be rerun for each sample |

**Option 3 chosen.** In our confirmed case the hidden code was not needed and did not affect the outcome, therefore the evidence does not justify changing the model input. However the problem should be visible. We implemented the audit as two helper scripts with manual verdicts and changed nothing in the pipeline, model input or scorers.

**Accepted trade-off.** Our method-level results cannot show whether a revision is correct across files. Both the model input and the scoring reference contain only the commented method ([Event B inputs](data/event_b/evaluation/eval_raw.csv), [complete references](results/event_b/scoring_audit/complete_references.csv)), and cases where this matters exist in earlier samples too ([M2 flags](results/event_b/flags_m2.csv)). We record which cases are affected ([Event B flags](results/event_b/flags_candidates.csv)) rather than change the input to fix it.

## 8. Pre-Event-B and post-response states

| | Pre-Event-B | After Event B |
|---|---|---|
| Pipeline, model input, original scorer | Authors' code and group scripts | Unchanged |
| Files added | — | `check_pr_dependencies.py`, `flag_sample_dependencies.py`, `complete_reference_check.py` |
| Dependency visibility | Not recorded | Flagged per case: M2 3/12, Event A 0/12, Event B 2/6 |
| M2 results | 6/12 raw, 5/12 cleaned | Identical predictions |

## 9. Limitations

- One Event B case (two comments on one method): it shows the problem can occur, not how often.
- The dependency check matches names in changed lines, so it can miss or wrongly flag dependencies.
- The reference for ranks 1–2 equals the input, so these scores do not measure whether the comment was carried out.
- 24 of 30 mined comments were excluded at P1, and the 6 remaining cases are all test methods.
- The complete-reference check was rebuilt, not recovered, although it reproduced the committed outputs exactly.

## 11. Evidence

- **Data:** [mined pool](data/event_b/sampleEventB_raw.csv), [raw inputs](data/event_b/evaluation/eval_raw.csv), [cleaned inputs](data/event_b/evaluation/eval_cleaned.csv), [excluded cases](data/event_b/evaluation/excluded_rows.csv)
- **Dependency audit:** [check script](m2_scripts/check_pr_dependencies.py), [flagging script](m2_scripts/flag_sample_dependencies.py), [Event B flags](results/event_b/flags_candidates.csv), [M2 flags](results/event_b/flags_m2.csv), [Event A flags](results/event_b/flags_event_a.csv)
- **Model verification:** [environment versions](results/event_b/model_env_versions.txt), [M2 rerun](results/event_b/m2_check/)
- **Evaluation:** [raw predictions](results/event_b/t5/predictions_raw.csv), [cleaned predictions](results/event_b/t5/predictions_cleaned.csv)
- **Complete-reference check:** [script](m2_scripts/complete_reference_check.py), [references](results/event_b/scoring_audit/complete_references.csv), [source checks](results/event_b/scoring_audit/target_source_checks.csv), [scores](results/event_b/scoring_audit/complete_reference_scores.csv)