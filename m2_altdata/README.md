# P29 M2 – raw vs cleaned code-review cases (Group 30)

Bounded reproduction on alternative data, as agreed with Abdul on 22 Oct 2026.
The plan, sampling rule and decision rule are in `docs/DEVIATION_02_alternative_dataset.md`.

## Run order (Windows PowerShell, from this folder)

Each step saves its own evidence. Commit after every step marked **commit**.

**0. Freeze the rules – before anything is mined**
```powershell
git add docs config.json prompt_template.txt scripts utils README.md
git commit -m "M1 deviation 2: alternative GitHub code-review data (approved by Abdul 22 Oct)"
git tag -a M1_DEVIATION_2 -m "Rules, projects, model, prompt and decision rule frozen before mining"
git push; git push origin M1_DEVIATION_2
```

**1. Install**
```powershell
pip install lizard regex rapidfuzz
```

**2. Mine candidate cases** – needs a GitHub token (Settings → Developer settings → Personal access tokens; public read access is enough)
```powershell
$env:GITHUB_TOKEN = "ghp_..."
python scripts/mine_cases.py
```
Writes `data/candidates.csv` (every comment checked + the rule it failed), `data/eligible_cases.jsonl`, `data/mining_log.json` and all raw API JSON and source files under `data/github_raw/`. Re-running uses the saved files.

**3. Freeze the 12 cases** – **commit + tag `SAMPLE_FROZEN`**, and copy the IDs into the workbook
```powershell
python scripts/freeze_sample.py
git add data; git commit -m "Freeze 12 cases (P29 rule, 4 per project)"; git tag -a SAMPLE_FROZEN -m "Sample frozen before model runs"
```

**4. Build raw / A / B** – point at your clone of the authors' repo
```powershell
python scripts/preprocess.py --analyzer2 "C:\Users\louis\Desktop\CS4928\authors-repo\Preprocessing\Cumulative_code\Analyzer2.py"
```

**5. Run the model** – install Ollama (ollama.com), then:
```powershell
ollama pull qwen2.5-coder:7b
python scripts/run_model.py --pilot     # Lab 4 pipeline check: case 1 only
python scripts/run_model.py             # all 12 cases x 3 conditions
```
**commit** `results/raw_outputs` and `results/model_info.json`.

**6. Score and decide** – **commit**
```powershell
python scripts/score.py
```
Writes `results/per_case.csv`, `summary_by_condition.csv`, `summary_by_project.csv` and `decision.md` (the RQ1/RQ2 status from the frozen rule).

## Tracing one number back (for the lab assistant)

`results/decision.md` → `results/summary_by_condition.csv` → the row in `results/per_case.csv` → its `raw_output_file` → the input in `data/conditions.jsonl` → the case in `data/cases.jsonl` → `comment_url`, `original_commit`, `revised_commit` and the two saved source files in `data/github_raw/`.

## If something goes wrong

- **A project has fewer than 4 eligible cases:** nothing to do; `freeze_sample.py` uses all of them, fills from the reserve and records it.
- **Fewer than 12 cases overall:** all are used and recorded (the P29 rule allows this). If very few, raise it with Abdul as he offered.
- **Ollama too slow or won't run:** changing the model is a methodological change. Record it as a deviation *before* running, then edit `config.json` → `model`.
