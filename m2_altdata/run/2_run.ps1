# Step 2: mine -> freeze sample (local commit + tag) -> preprocess -> pilot -> full run -> score (local commit).
# Nothing is pushed. Everything printed is saved to run\2_run.log.
$ErrorActionPreference = "Continue"
$m2   = Split-Path $PSScriptRoot -Parent
$repo = Split-Path $m2 -Parent
Start-Transcript -Path (Join-Path $PSScriptRoot "2_run.log") -Force | Out-Null
Set-Location $m2
function Stop-Run($msg) { Write-Host "STOPPED: $msg"; Stop-Transcript | Out-Null; exit 1 }
$trailer = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`nClaude-Session: https://claude.ai/code/session_01HCDZi33bnK87yQMvwpoJeG"
Write-Host "=== $(Get-Date -Format o)  m2 folder: $m2"

# ---- GitHub token from m2_altdata\.env (git ignores .env files)
$envFile = Join-Path $m2 ".env"
if (-not (Test-Path $envFile)) { Stop-Run "m2_altdata\.env not found. Put one line in it: GITHUB_TOKEN=ghp_..." }
$line = Get-Content $envFile | Where-Object { $_ -match '^\s*GITHUB_TOKEN\s*=' } | Select-Object -First 1
$env:GITHUB_TOKEN = ($line -split '=', 2)[1].Trim().Trim('"')
if (-not $env:GITHUB_TOKEN) { Stop-Run "GITHUB_TOKEN line in .env is empty" }

# ---- 1. mine + freeze (skipped if the sample is already frozen)
if (-not (Test-Path "data\sample_freeze.json")) {
    Write-Host "=== mining (this can take 10-30 minutes)"
    python scripts\mine_cases.py
    if ($LASTEXITCODE -ne 0) { Stop-Run "mining failed" }
    Write-Host "=== freezing sample"
    python scripts\freeze_sample.py
    if ($LASTEXITCODE -ne 0) { Stop-Run "freeze failed" }
    Set-Location $repo
    git add m2_altdata/data
    git commit -q -m "M2: freeze bounded sample (P29 stable order, 4 eligible cases per project)" -m "Sample frozen before any model run." -m $trailer
    git tag -a SAMPLE_FROZEN -m "Bounded sample frozen before any model run"
    git log -1 --format="%H %ci %s"
    Set-Location $m2
} else { Write-Host "=== sample already frozen - not re-mining" }

# ---- 2. authors' Analyzer2.py (commit d1e96929)
$a2 = "C:\Users\louis\Desktop\CS4928\authors-repo\Preprocessing\Cumulative_code\Analyzer2.py"
if (-not (Test-Path $a2)) {
    $clone = Join-Path (Split-Path $repo -Parent) "authors-repo-d1e9692"
    if (-not (Test-Path $clone)) {
        git clone -q https://github.com/shirinpirouzkhaah/Price-of-Precision.git $clone
        git -C $clone checkout -q d1e96929d2e78a20e65f78422676761411c8b18c
    }
    $a2 = Join-Path $clone "Preprocessing\Cumulative_code\Analyzer2.py"
}
Write-Host "authors' Analyzer2.py: $a2"
Write-Host "authors' repo commit: $(git -C (Split-Path (Split-Path (Split-Path $a2 -Parent) -Parent) -Parent) rev-parse HEAD)"

Write-Host "=== preprocessing (raw / A / B)"
python scripts\preprocess.py --analyzer2 $a2
if ($LASTEXITCODE -ne 0) { Stop-Run "preprocessing failed" }

# ---- 3. model server
try { Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 5 | Out-Null }
catch {
    $ollama = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    Start-Process $ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 8
}
$tags = Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 10
if (-not ($tags.models | Where-Object { $_.name -eq "qwen2.5-coder:7b" })) { Stop-Run "model qwen2.5-coder:7b not downloaded yet - run 1_SETUP.bat first" }

Write-Host "=== PILOT: first case, all 3 conditions"
python scripts\run_model.py --pilot
if ($LASTEXITCODE -ne 0) { Stop-Run "pilot failed" }
Write-Host "=== FULL RUN: all cases x 3 conditions"
python scripts\run_model.py
if ($LASTEXITCODE -ne 0) { Stop-Run "full run failed (re-run this file; saved outputs are kept and skipped)" }

Write-Host "=== scoring"
python scripts\score.py
if ($LASTEXITCODE -ne 0) { Stop-Run "scoring failed" }

Set-Location $repo
git add m2_altdata/data m2_altdata/results m2_altdata/run/1_setup.log
git commit -q -m "M2: run 12 cases x 3 conditions (raw, A, B) and score with the frozen rule" -m $trailer
git log -1 --format="%H %ci %s"
Write-Host "=== RUN FINISHED $(Get-Date -Format o) (nothing pushed)"
Stop-Transcript | Out-Null
