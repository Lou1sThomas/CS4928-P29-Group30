#!/usr/bin/env bash
# Build an isolated run folder for the authors' Cumulative pipeline on one input CSV.
# Authors' code is copied, never edited in place. Only two config lines change:
#   input_csv_path -> our mined sample;  data_type 'Gerrit' -> 'GitHub'.
# Usage: m2_scripts/setup_run.sh <input_csv> <run_name>   (run from repo root)
# AUTHORS = folder holding the authors' repository (default: repo root; e.g. AUTHORS=authors_repo for a submodule)
set -euo pipefail
IN="$1"; NAME="$2"; RUN="m2_run/$NAME"; A="${AUTHORS:-.}"
rm -rf "$RUN" 2>/dev/null || true
mkdir -p "$RUN/SplittedData/ProjectLevel" "$RUN/Cumulative_code/utils"
cp "$A"/Preprocessing/Cumulative_code/*.py "$RUN/Cumulative_code/"
cp "$IN" "$RUN/SplittedData/ProjectLevel/$NAME.csv"
# Missing pieces of the released package (documented deviations):
cp "$A"/Training_and_Testing/OpenNMT/Code/idioms.csv "$RUN/Cumulative_code/utils/idioms.csv"  # idioms file lives in OpenNMT/, pipeline expects utils/
touch "$RUN/Cumulative_code/pipeline.py" "$RUN/Cumulative_code/run_pipeline.sh"            # copy_whole_current_directory() copies these; not in repo
cp "$A"/Training_and_Testing/T5/Code/utils/stop-words-english.txt "$RUN/Cumulative_code/utils/"   # stop-word list lives in T5/Code/utils, pipeline expects utils/
cp m2_scripts/cld3_stub.py "$RUN/Cumulative_code/cld3.py"                                  # pycld3 cannot build; is_english() returns True on every path so cld3 never affects output
P="$RUN/Cumulative_code/Preprocessing_Pipeline.py"
# portable in-place edit (GNU and macOS): python instead of sed -i
python3 - "$P" "$NAME" <<'PY'
import re, sys
p, name = sys.argv[1], sys.argv[2]
s = open(p).read()
s = re.sub(r"^input_csv_path = .*$", f"input_csv_path = os.path.join(Root_dir,'SplittedData/ProjectLevel/{name}.csv')", s, count=1, flags=re.M)
s = re.sub(r"^    data_type = 'Gerrit'$", "    data_type = 'GitHub'", s, count=1, flags=re.M)
open(p, "w").write(s)
PY
diff "$A"/Preprocessing/Cumulative_code/Preprocessing_Pipeline.py "$P" > "$RUN/config_changes.diff" || true
echo "Run folder ready: $RUN"; cat "$RUN/config_changes.diff"
