# CS4928 P29 – Group 30 – M1 Deviation 02: alternative code-review dataset

**Recorded:** 28 Oct 2026, before any mining, sampling or model run for M2.
**Approved route:** email from Abdul (coordinator), 22 Oct 2026.
**Original M1 record:** kept unchanged (git tag `M1_PLAN`, and the earlier change-log entry of 21 Oct 2026). This note adds to it; it does not replace it.
**Git tag for this note:** `M1_DEVIATION_2` (applied to the commit that adds this file and the `m2_altdata/` folder: `config.json`, `prompt_template.txt`, `scripts/`, `utils/`).

> **We are using alternative data.** The cases below are not the authors' dataset, so we do not expect, and will not claim, to reproduce the paper's exact numbers. We test whether the paper's *direction of effect* holds on new, traceable data.

---

## 1. The missing data (why we changed)

The paper's README says the input data is on Zenodo (10.5281/zenodo.17227729). The record (v1, 29 Sep 2025) contains only `FinalRatios.zip` (45.5 kB, md5 `b1947a3cab816a130a5fe3c329723b18`), which holds aggregate result tables. The repository (commit `d1e96929`) has empty `SplittedData/`, `NewGitHubData/`, `csvResults/` and no `utils/` folder. So the original code-review inputs, the new GitHub test set and the per-record predictions are not available. Evidence: `results/week6/blocker_evidence.txt` (20 Oct 2026) and the feasibility table in `PLAN.md` section 5. Abdul checked the repository and Zenodo record and confirmed the problem on 22 Oct 2026.

## 2. The change in approach

Following Abdul's instructions, we keep P29 and both RQs, and replace the input data with **real, traceable code-review cases mined from GitHub pull requests in more than one Java project**. This follows the same route the authors used to build their own "new GitHub test set" (mined PR reviews), at a bounded scale.

For every case we keep:

| Needed (Abdul) | What we store |
| --- | --- |
| Original code | The reviewed method, extracted with `lizard` from the full source file at the comment's `original_commit_id` |
| Requested revision | The reviewer's inline comment: text, ID, URL, author, timestamp, commented line |
| Revised code | The same method at the first later commit in the same PR that changed it |
| Relevant source files | Both full `.java` files (before and after), their SHA-256, the repo, PR number and both commit SHAs |
| Raw evidence | Every GitHub API response saved as JSON under `m2_altdata/data/github_raw/`, with fetch time |

### Projects (frozen)

| Role | Project | Why |
| --- | --- | --- |
| Main | `apache/commons-lang` | Maven, JUnit tests, active inline PR review |
| Main | `google/gson` | Maven, JUnit tests, small and self-contained |
| Main | `checkstyle/checkstyle` | Maven, very large test suite, heavy inline review |
| Reserve | `apache/commons-io` | Used only to fill a shortfall, in stable order |

All four are Maven projects with test suites, so a revised method can later be dropped into the real source file at `revised_commit` and compiled and tested. This is what keeps the later evaluation and design work possible on the same cases (Abdul's last condition).

Date window: PRs **merged 1 Jan 2025 – 30 Sep 2026**. This is after the chosen model's release (Sep 2024), which limits the chance the model has seen these reviews.

## 3. How the replacement cases are selected

**Eligibility rules, applied in this order** (the first failing rule is recorded for every comment in `data/candidates.csv`):

| Rule | A comment is excluded if… | Mirrors the authors' step |
| --- | --- | --- |
| R1 | it is a reply, not a top-level review comment | comment pruning (S2.P2) |
| R2 | the file is not `.java` | Java-only data |
| R3 | the file is a test file | – |
| R4 | the author is a bot | – |
| R5 | the author is the PR author | `remove_owner_comments` |
| R6 | it is on the old (left) side or has no line | `remove_left_side` |
| R7 | the source file cannot be downloaded | – |
| R8 | the commented line is not inside a method | method extraction (P1) |
| R9 | another top-level comment sits on the same method | `remove_multiple_comments_methodLevel` (P2) |
| R10 | no later commit in the PR changes that method | unchanged-method removal (P3) |
| R11 | the method before or after has more than 512 tokens | long method removal (P5) |

**Sampling (P29 rule, per-project adaptation).** The P29 rule is "first 12 eligible items in stable order (case ID, then file path, then chronological ID)". Applied to one pooled list, all 12 would come from whichever project sorts first, which breaks Abdul's multi-project condition and leaves RQ2 nothing to compare. So we apply the same stable order **within each project** — PR number (case ID), then file path, then comment time and ID — and take the **first 4 eligible cases from each of the 3 projects (12 in total)**. A project with fewer than 4 uses all of its cases, and the shortfall is filled from the reserve in the same order and recorded. Cases are never chosen by looking at the content or at any model output; mining stops only after finishing the PR in which the quota was reached, so no earlier PR is skipped.

The 12 case IDs (`owner/repo#PR-commentID`) are written to `data/sample_ids.csv` by `scripts/freeze_sample.py`, hashed in `data/sample_freeze.json`, copied into the group workbook, and committed and tagged (`SAMPLE_FROZEN`) **before** any model is run.

## 4. Preprocessing: raw vs two of the authors' steps

| Condition | What changes | Authors' code |
| --- | --- | --- |
| `raw` | Nothing – method and comment as mined | – |
| `A_code_comment_removal` | `//` and `/* */` comments removed from the original **and** revised method | `Analyzer2.removeComments` |
| `B_review_comment_cleaning` | Reviewer comment cleaned (emoji/non-ASCII, links, `@mentions`, stop-words, lower-casing, trailing punctuation) | `Analyzer2.clean_comment_without_abstraction` |

Both functions are **executed from the authors' own `Analyzer2.py`** (commit `d1e96929`), not rewritten (`scripts/authors_steps.py`). The steps are applied separately (isolated), so each effect is measured on its own. They only transform text; no case is removed, so all three conditions are scored on the same fixed 12 cases. Two substitutions are needed because the authors did not release `utils/`: a standard English stop-word list (179 words) in place of `utils/stop-words-english.txt`, and an empty `utils/idioms.csv`. The authors' `is_english` is replaced by a function returning `True`, which is exactly what their version always returns.

## 5. Model and evaluation (identical for every condition)

| Item | Frozen value |
| --- | --- |
| Model | `qwen2.5-coder:7b` via local Ollama; exact digest saved in `results/model_info.json` |
| Why not T5-small | The paper's T5 must be fine-tuned on the unavailable training data; the P29 pack allows a current general-purpose LLM |
| Prompt | `prompt_template.txt`, the same for all conditions (as in the paper) |
| Settings | temperature 0, seed 42, max 2,048 tokens, one output per case |
| Primary metric | Exact match (EXM) after whitespace normalisation |
| Secondary metric | Normalised Levenshtein similarity (LEV), 0–1 |
| Raw evidence | One JSON per case and condition in `results/raw_outputs/`, never edited |

## 6. Research questions on the new data

- **RQ1.** How does preprocessing change automated revision success on the bounded dataset? → raw vs A vs B on the 12 fixed cases.
- **RQ2 (transfer part).** Our frozen RQ2 asked whether the pipeline behaves the same on *new GitHub data*. The mined cases are new GitHub data, so the transfer question is now answered on them, together with the pack's project-separation question: does the raw-vs-cleaned effect stay the same when the 12 cases are separated by project (4 per project)?
- **RQ2 (design part, duplicated code).** Unchanged by this deviation. It uses only the authors' code and is not part of the M2 run.
- **Record-count check against Table 4 (frozen RQ1 target).** Still BLOCKED: it needs the authors' original input data. The Week 6 check of the published `FinalRatios.zip` values stays in `REPRODUCTION.md` as it was.

## 7. Expected result and decision rule (frozen now)

**Expected (from the paper):** large general-purpose models (CodeLLaMA, GPT-3.5) are largely insensitive to preprocessing, and split effects are small in practice. We therefore expect little difference between raw and cleaned, and a similar effect in each project.

| | REPRODUCED / consistent | NOT REPRODUCED / project-dependent | INCONCLUSIVE / BLOCKED |
| --- | --- | --- | --- |
| **RQ1** | For **both** A and B: EXM within ±1 case of raw **and** mean LEV within ±0.05 of raw | Either A or B outside either bound | Any output missing or the run invalid |
| **RQ2** | Each project's effect (cleaned − raw mean LEV) within ±0.05 of the pooled effect, for A and B | Any project outside ±0.05 | Any output missing or a project has no cases |

If EXM is 0 in every condition (floor effect), RQ1 rests on LEV and this is reported. `scripts/score.py` applies these thresholds from `config.json` and writes `results/decision.md`. With 4–12 cases these are descriptive checks, not significance tests.

## 8. Main threats

- **Very small sample** (12 cases, 4 per project): a single case moves EXM by 8 points.
- **Different model and data** from the paper, so only the direction of the effect is comparable.
- **Substituted helper files** change step B's stop-word removal slightly.
- **Revised code is the developer's next change to the method,** which may include edits beyond the comment.
