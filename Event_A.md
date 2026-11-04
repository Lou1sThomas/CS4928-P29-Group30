# P29 Event A — Testing the M2 setup on Checkstyle

**Group:** 30 / P29  
**Operator:** Shaun Purcell  
**Report prepared:** 3 November 2026  
**Status:** Runs and scoring checks completed. Commit references, saved diagnostic scripts and tracker links still need to be added.

## 1. What we were trying to find out

Event A asked us to repeat the automated code-revision evaluation using a project-level split. This means keeping whole projects out of training and testing on them afterwards. The aim was to see whether the performance observed in M2 depended on familiarity with a project's code, or possibly on overlap between training and test data. We were also asked to keep the evaluation measure unchanged and run the existing M2 method before making any improvements.

Our M2 had already needed an alternative approach. We could not recover the original input datasets and required model assets from the replication package we inspected. Abdul allowed us to proceed with real, traceable Java review examples instead of reproducing the paper's exact numbers. Our group used Apache Commons IO and Commons Lang examples, the authors' preprocessing code, and an available Tufano T5 checkpoint and tokenizer. The earlier JUnit/Gson pilot was not used in the final M2 experiment.

For Event A, we used Checkstyle as an additional project and kept the adapted M2 model setup. Checkstyle is a Java code-checking tool, but we used reviews of changes to its own source code as our data. We did not run Checkstyle to grade the model's predictions.

There is an important limit to this approach: we did not retrain the model with a project-level split, and we have not established whether Checkstyle was in the replacement checkpoint's training data. This is therefore an evaluation on an additional project, rather than a verified project-level train/test split. It only partially addresses the original Event A requirement. Abdul's email approved alternative data for M2; acceptance of this particular Event A adaptation still needs to be confirmed with the TA.

## 2. Our prediction and what we kept unchanged

Before execution, we predicted that T5-small would perform worse on different projects because their coding styles and structures could make revisions harder to predict. We also predicted that preprocessing would still help, although its effect might differ between projects.

An equal or higher score on the additional project would challenge our predicted performance drop. A cleaned score equal to or below the raw score would challenge our prediction that preprocessing would help.

Our original prediction called M2 a "time-level split". In our adapted experiment, however, we evaluated an already-trained replacement checkpoint. We did not verify its training split or training-project overlap, so that description should not be treated as a claim that we implemented a controlled time-based training/test split ourselves.

Before evaluating Checkstyle, we reran M2's saved evaluation inputs using the recovered setup. We obtained the reported totals of 6/12 raw and 5/12 cleaned. We then used that same model, tokenizer, evaluation script and settings for Event A. This supports consistency with M2, but matching totals alone do not prove that every file and dependency was identical to the original run.

We kept the first results. The later scoring investigation is reported separately and does not replace the frozen M2 record or the initial Event A run.

## 3. Where the Checkstyle data came from

We collected Java review comments from merged pull requests in the [Checkstyle repository](https://github.com/checkstyle/checkstyle). The mining command was:

```bash
python -X utf8 m2_scripts/mine_github_reviews.py \
  --sample EventA --start 2020-09-01 --end 2021-08-31 \
  --repos checkstyle/checkstyle --per-repo 35 --out data/event_a
```
The dates were not chosen to guarantee that these examples were absent from the model's training data as even a later date than the study could have old versions of scripts potentially used in training.

Each mined record includes the review URL, comment ID, file path, commit identifiers, review text and source snapshots. The revised source is taken from the final PR head. This makes the code traceable, but the final revision may include other changes beyond the one requested in a particular comment.

### Correcting the saved review locations

The original saved pool had `original_line = 1` for all 35 comments. We checked individual GitHub comment responses and found that many of the actual review locations were different. We verified the comment ID, file path and original commit, then saved corrected line and side metadata in a separate CSV. We preserved the original pool and the downloaded responses.

We have not established why the incorrect values appeared in the initial saved pool. The correction repaired review locations, it did not invent replacements for missing source files.

### Selecting the evaluation cases

| Stage | Records |
|---|---:|
| Mined pool | 35 |
| Removed for missing required values | 11 |
| Method-level records extracted | 22 |
| T5/S2 P1 records after size filtering | 21 |
| Cleaned records | 20 |
| Eligible in both versions | 20 |
| Selected for evaluation | 12 |

After removing the 11 records with missing values, two of the remaining 24 did not yield a containing before-method. Our selection script then required non-empty code, review text and targets in both raw and cleaned versions. It sorted eligible cases by comment ID, file path and creation time and took the first 12.

The selected cases came from PRs [8783](https://github.com/checkstyle/checkstyle/pull/8783) and [8786](https://github.com/checkstyle/checkstyle/pull/8786). All concern:

```text
src/test/java/com/puppycrawl/tools/checkstyle/internal/AllTestsTest.java
```

These are 12 review comments covering only **two distinct target methods**. They should not be described as 12 independent method changes. The results also describe cases that survived both preparation routes, rather than every review in the mined pool.

## 4. How we ran the evaluation

The raw version uses the authors' T5/S2 P1 output, including method extraction and size filtering. The cleaned version uses the group's isolated P1+P4 preparation. This calls the authors' comment-cleaning functions and also prepares code and target fields. We later confirmed that the code inputs and targets could change too, so the experiment does not isolate review-comment cleaning alone.

We used the Tufano checkpoint `T5_pre-trained_new_large_dataset_code&comment-to-code` from [Zenodo record 5387856](https://zenodo.org/records/5387856), with its SentencePiece tokenizer. The group's conversion script exported 131 non-optimizer variables and mapped them into the Hugging Face model. We did not fine-tune or retrain it locally.

For each case, the model received the code and review comment in this format:

```text
<code>original code</code><technical_language>review comment</technical_language>
```

We used ten beams, ten returned candidates, a maximum generation length of 512, length penalty 1.0 and early stopping. EXM@10 counts a case as a match if any of the ten candidates equals the reference after the scoring procedure.

The group evaluation script loads four helpers from the authors' `FineTuning_and_Testing.py`: `format_content`, `cleaning_model_output`, `to_single_line` and `is_exact_match`. We recovered this file from the downloaded authors' ZIP and recorded its provenance. We have not verified that it is byte-for-byte identical to the file used for the original M2 run, although rerunning M2 recovered its reported totals.

## 5. Results from the original scoring procedure

| Dataset and version | EXM@10 | Mean best Levenshtein similarity |
|---|---:|---:|
| M2 verification — raw | 6/12 (50.0%) | 0.900 |
| M2 verification — cleaned | 5/12 (41.7%) | 0.954 |
| Event A — raw | 2/12 (16.7%) | 0.817 |
| Event A — cleaned | 0/12 (0.0%) | 0.770 |

Levenshtein similarity here is the average of each case's best similarity score among its ten candidates. It measures text similarity, not whether the code compiles or behaves correctly.

For Event A, the raw matches were ranks 7 and 12, both at candidate 10. Neither version matched within its first five candidates. Initially this looked like a raw-versus-cleaned performance difference. Inspection showed that the two raw matches were against incomplete references, so we could not interpret them as successful complete revisions.

## 6. The scoring problem we found

The raw targets for ranks 7 and 12 had already been flattened into one line in the evaluation CSV, but still contained `//` comments. They were 225 tokens long before the limit, so the missing code was not caused by the target token limit.

The authors' scoring helper removes line comments using:

```python
re.sub(r'//[^\n]*', '', text)
```

This removes everything from `//` to the next newline. In these flattened targets there was no next newline, so it removed the comment and the rest of the method. The inspected raw target went from 870 to 307 characters before final trimming and ended at the opening of a loop. The cleaned target retained the full method because its comments had been removed earlier.

This explains why the raw and cleaned scores were not directly comparable as measures of complete-revision accuracy. The problem occurred when our prepared data passed through the authors' scoring helper. It does not establish that the authors' original experiments were affected in the same way.

The review text at rank 7 stayed as `changed`, so its difference was not caused by a change to the review words. At rank 12, cleaning removed `never` from the review, which could change its meaning. However, the code inputs and reference handling changed as well, so we cannot identify review-text cleaning as the sole cause.

## 7. Our separate complete-reference check

We kept the original results and checked the saved predictions again using complete references. We did not generate new predictions.

First, we recovered the multiline `after` methods from the preprocessing outputs. We checked the case identities and confirmed that all 12 targets in each dataset appeared in their saved final source files. This verified their source, but not that every change in the final method was caused by the associated review comment.

We then removed the known comments before flattening the reference. The Checkstyle targets contained standalone comment lines. M2 rank 12 contained three known comments, including inline comments, which we removed explicitly with checks. This was a limited diagnostic for the inspected examples, not a general Java comment parser.

For each case, both raw and cleaned predictions were compared against the same complete reference. We used saved `raw_predictions` and normalized whitespace, without applying the original comment-removal helper to predictions. We also avoided tokenizing or truncating the complete reference.

| Dataset | Original raw | Original cleaned | Complete-reference raw | Complete-reference cleaned |
|---|---:|---:|---:|---:|
| M2 | 6/12 | 5/12 | 5/12 | 5/12 |
| Event A | 2/12 | 0/12 | 2/12 | 0/12 |

For Event A, the two raw matches were now **ranks 9 and 10**, at candidates 1 and 3. The original matches at ranks 7 and 12 disappeared. The total stayed the same, but the cases counted as successful changed.

For M2, both versions matched **ranks 1, 2, 5, 9 and 10**. The original raw match at rank 6 disappeared even though its reference had no comment markers. We cannot attribute that change to the `//` issue without further inspection: this diagnostic also changes reference handling and normalization. M2's 12 cases contain eight distinct target methods.

This check is supplementary. It retains comments in predictions, cannot restore information already lost during decoding, and uses whitespace normalization rather than checking Java behaviour. It should not be presented as an exact rerun of the original metric or as proof of functional correctness.

## 8. What the results tell us

Under the complete-reference check, raw matches fell from 5/12 in M2 to 2/12 on Checkstyle, and cleaned matches fell from 5/12 to 0/12. This is consistent with our prediction of lower performance on an additional project. Our prediction that preprocessing would help was not supported on this Checkstyle sample.

We cannot conclude that project differences alone caused the drop. The time period changed too, the sample is small, and many comments share the same target method. We also do not know whether the model encountered Checkstyle during training. This experiment cannot prove or rule out training-data leakage.

The clearest additional finding is that aggregate scores can hide problems with individual examples. The original and diagnostic Event A scores were both 2/12 raw and 0/12 cleaned, yet the raw matching cases were different. Looking at the actual references and predictions was necessary to understand what those totals meant.

The main limitations are:

- We tested a fixed replacement checkpoint on an additional project; we did not implement a verified project-level training/test split.
- Checkstyle's presence in the checkpoint's training data is unknown.
- M2 and Event A use different time periods as well as different projects.
- The 12 Checkstyle reviews cover only two distinct target methods in one file.
- Only cases eligible in both preparation routes were evaluated.
- Final PR code may include changes unrelated to an individual review comment.
- Code representations changed alongside review text, preventing a comment-only causal comparison.
- Matching M2 totals do not prove that the recovered setup is identical in every detail.
- The complete-reference check was designed after inspecting the first results and is reported separately for that reason.

## 9. Design problem and decision

The design problem is that input preparation and reference scoring are too closely connected. Flattening code can remove information that a later comment-removal step needs. As a result, changing a preprocessing option can also change how much of the expected answer is scored.

We considered leaving the scorer unchanged and reporting the limitation, modifying the existing scorer, or keeping the frozen results and adding a separate check. We chose the third option. It let us investigate the issue without rewriting the M2 record or hiding the first Event A result.

Our recommended design change is to separate reference preparation from model-input preprocessing. Preserve the original multiline source, create one verified reference per case, and reuse it across conditions. Comment handling should understand Java syntax and happen before line boundaries are discarded. Validation should check that the reference remains complete and that paired conditions use the intended shared reference.

This is a separation-of-responsibilities improvement. We have implemented the scoped diagnostic, not a general-purpose replacement scorer. A future implementation should not treat the explicit comment substitutions used here as a complete Java-cleaning solution.

## 10. Evidence

### Data and preparation

- [Verified Checkstyle pool](data/event_a/sampleEventA_verified_raw.csv)
- [Review metadata corrections](data/event_a/metadata_verification.csv)
- [Saved GitHub comment responses](data/event_a/comment_metadata/)
- [Selected case IDs](data/event_a/evaluation/sample_ids.csv)
- [Raw inputs](data/event_a/evaluation/eval_raw.csv)
- [Cleaned inputs](data/event_a/evaluation/eval_cleaned.csv)
- [All eligible cases](data/event_a/evaluation/eligible_all.csv)
- [Excluded cases](data/event_a/evaluation/excluded_rows.csv)
- [Selection log](results/event_a/selection_log.txt)
- [Verified preprocessing run log](results/event_a/pipeline_verified_log.txt)

### Scripts, model and original results

- [Mining script](m2_scripts/mine_github_reviews.py)
- [Raw/cleaned preparation and selection](m2_scripts/make_raw_clean.py)
- [T5 evaluation script](m2_scripts/run_t5_eval.py)
- [Checkpoint conversion script](m2_scripts/convert_tufano_t5.py)
- [Recovered authors' scoring file](authors_reference/FineTuning_and_Testing.py)
- [Scoring-file provenance](results/event_a/scorer_provenance.txt)
- [Model source information](models/SOURCE.txt)
- [Model conversion log](results/event_a/model_conversion_log.txt)
- [Model environment versions](results/event_a/model_env_versions.txt)
- [M2 verification predictions and logs](results/event_a/m2_verification/)
- [Event A raw predictions](results/event_a/t5/predictions_raw.csv)
- [Event A cleaned predictions](results/event_a/t5/predictions_cleaned.csv)
- [Inspection of ranks 7 and 12](results/event_a/t5/ranks_7_12_inspection.txt)
- [Trace showing how the reference was shortened](results/event_a/t5/scoring_diagnostic.txt)

### Complete-reference checks

- [Event A target/source checks](results/event_a/scoring_audit/target_source_checks.csv)
- [Event A multiline targets](results/event_a/scoring_audit/multiline_targets.csv)
- [Event A complete references](results/event_a/scoring_audit/complete_references.csv)
- [Event A diagnostic scores](results/event_a/scoring_audit/complete_reference_scores.csv)
- [M2 multiline targets](results/event_a/m2_scoring_audit/multiline_targets.csv)
- [M2 complete references](results/event_a/m2_scoring_audit/complete_references.csv)
- [M2 diagnostic scores](results/event_a/m2_scoring_audit/complete_reference_scores.csv)
