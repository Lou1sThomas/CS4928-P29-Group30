#!/usr/bin/env bash
# Re-run M2 end to end from the committed, frozen data and check the results match.
# Run from the repository root:   bash m2_scripts/reproduce_m2.sh
# Options (environment variables):
#   PYTHON=python3.11   which Python to build the environments with (3.10-3.12 recommended)
#   STEPS="env pipeline model"   which parts to run (default: all three)
#   AUTHORS=authors_repo   folder with the authors' repository (default: repo root)
#   RESULTS=results/m2_raw_vs_clean   committed results to compare against
# Needs: models/models/T5_pre-trained_new_large_dataset_code&comment-to-code/ and models/tokenizer/
#        (unzip models.zip and tokenizer.zip from Zenodo 10.5281/zenodo.5387856 into models/; see models/SOURCE.txt)
set -euo pipefail
ROOT="$(pwd)"; PY="${PYTHON:-python3}"; STEPS="${STEPS:-env pipeline model}"
OUT="$ROOT/repro_out"; mkdir -p "$OUT/data" "$OUT/results"
PIPE_PY="$ROOT/.venv-pipeline/bin/python"; MODEL_PY="$ROOT/.venv-model/bin/python"
CKPT="$ROOT/models/models/T5_pre-trained_new_large_dataset_code&comment-to-code/model.ckpt"
SPM="$ROOT/models/tokenizer/TokenizerModel.model"
export AUTHORS="${AUTHORS:-.}"; AUTH="$ROOT/$AUTHORS/Training_and_Testing/T5/Code/FineTuning_and_Testing.py"
RES="${RESULTS:-Results/m2_raw_vs_clean}"
say() { printf "\n=== %s ===\n" "$*"; }

if [[ " $STEPS " == *" env "* ]]; then
  say "1/3 Python environments"
  "$PY" -m venv .venv-pipeline && "$PIPE_PY" -m pip install -q -r m2_scripts/requirements-pinned.txt
  "$PY" -m venv .venv-model && "$MODEL_PY" -m pip install -q torch transformers sentencepiece python-Levenshtein unidecode pandas tensorflow
  "$MODEL_PY" -m pip freeze | grep -i -E "^(torch|transformers|sentencepiece|tensorflow|python-levenshtein|unidecode|pandas)==" > "$OUT/model_env_versions.txt"
fi

if [[ " $STEPS " == *" pipeline "* ]]; then
  say "2/3 Authors' preprocessing pipeline on the frozen 60-case pool"
  bash m2_scripts/setup_run.sh data/sampleM2_raw.csv REPRO_M2 > "$OUT/setup_run.log"
  ( cd m2_run/REPRO_M2/Cumulative_code
    "$PIPE_PY" "$ROOT/m2_scripts/run_pipeline_fork.py" > ../run_stdout.log 2>&1
    "$PIPE_PY" "$ROOT/m2_scripts/make_raw_clean.py" ../SplittedData/ProjectLevel/REPRO_M2.csv \
        ../SplittedData/PreprocessedData/REPRO_M2/Chunk_0000 "$OUT/data" 2>/dev/null | grep -A14 "^mined=" )
  for f in sample_ids.csv eval_raw.csv eval_cleaned.csv excluded_rows.csv eligible_all.csv; do
    if cmp -s "$OUT/data/$f" "data/m2/$f"; then echo "  $f: IDENTICAL to frozen data/m2/$f"; else echo "  $f: DIFFERS from frozen data/m2/$f"; fi
  done
fi

if [[ " $STEPS " == *" model "* ]]; then
  say "3/3 T5-small on RAW and CLEANED (frozen data/m2/eval_*.csv)"
  [[ -f "$CKPT.index" && -f "$SPM" ]] || { echo "Model files missing: unzip models.zip and tokenizer.zip into models/ (see models/SOURCE.txt)"; exit 1; }
  if [[ ! -f "$OUT/t5_hf/model.safetensors" ]]; then
    TF_CPP_MIN_LOG_LEVEL=3 "$MODEL_PY" m2_scripts/convert_tufano_t5.py export "$CKPT" "$OUT/tufano_weights.npz"
    "$MODEL_PY" m2_scripts/convert_tufano_t5.py build "$OUT/tufano_weights.npz" "$OUT/t5_hf"
  fi
  for v in raw cleaned; do
    "$MODEL_PY" m2_scripts/run_t5_eval.py "$AUTH" "$OUT/t5_hf" "$SPM" "data/m2/eval_$v.csv" "$v" "$OUT/results" 2>&1 | grep -E "^\[|^\{"
  done
  "$MODEL_PY" m2_scripts/compare_raw_clean.py "$AUTH" "$OUT/results" | head -4
  if cmp -s "$OUT/results/summary.csv" "$RES/summary.csv"; then echo "  summary.csv: IDENTICAL to committed $RES/summary.csv"
  else echo "  summary.csv: DIFFERS from committed results (see diff below)"; diff "$OUT/results/summary.csv" "$RES/summary.csv" || true; fi
fi
say "done - outputs in repro_out/"
