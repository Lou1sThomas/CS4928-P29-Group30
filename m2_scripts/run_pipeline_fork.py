"""Run the authors' Preprocessing_Pipeline.py unchanged, but with the 'fork' start method.
The script creates a ProcessPoolExecutor at module level without an
`if __name__ == "__main__":` guard; under macOS's default 'spawn' method each worker would
re-import and re-run the whole script. 'fork' (the Linux default the authors used) avoids that.
Run from inside the run folder's Cumulative_code/ directory:  python run_pipeline_fork.py"""
import multiprocessing as mp, runpy, sys, os
sys.path.insert(0, os.getcwd())
mp.set_start_method("fork", force=True)
runpy.run_path("Preprocessing_Pipeline.py", run_name="__main__")
