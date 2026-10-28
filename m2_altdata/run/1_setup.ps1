# Step 1: freeze the rules in git (local commit + tag only, nothing pushed), install Python libs, install Ollama and download the model.
$ErrorActionPreference = "Continue"
$repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$log  = Join-Path $PSScriptRoot "1_setup.log"
Start-Transcript -Path $log -Force | Out-Null
Set-Location $repo
Write-Host "=== $(Get-Date -Format o) repo: $repo"

Write-Host "=== git: commit and tag M1_DEVIATION_2 (before any mining)"
git add PLAN.md docs m2_altdata/README.md m2_altdata/config.json m2_altdata/prompt_template.txt m2_altdata/scripts m2_altdata/utils m2_altdata/run
git commit -m "M1 deviation 2: alternative GitHub code-review data (approved by Abdul 22 Oct)" -m "Projects, eligibility rules, sampling rule, preprocessing steps, model, prompt and decision rule frozen before mining." -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`nClaude-Session: https://claude.ai/code/session_01HCDZi33bnK87yQMvwpoJeG"
git tag -a M1_DEVIATION_2 -m "Rules frozen before mining, 28 Oct 2026"
# (no push - the group pushes later)
git log -1 --format="%H %ci %s"

Write-Host "=== python libraries"
python --version
python -m pip install --quiet lizard regex rapidfuzz
python -c "import lizard, regex, rapidfuzz; print('python libs OK')"

Write-Host "=== Ollama"
$ollama = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
if (-not (Test-Path $ollama)) {
    winget install --id Ollama.Ollama -e --silent --accept-package-agreements --accept-source-agreements
}
if (-not (Test-Path $ollama)) { $c = Get-Command ollama -ErrorAction SilentlyContinue; if ($c) { $ollama = $c.Source } }
Write-Host "ollama exe: $ollama  exists: $(Test-Path $ollama)"
try { Invoke-RestMethod http://localhost:11434/api/tags -TimeoutSec 5 | Out-Null; Write-Host "server already running" }
catch { Start-Process $ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 8 }
& $ollama --version
& $ollama pull qwen2.5-coder:7b
& $ollama list
Write-Host "=== SETUP FINISHED $(Get-Date -Format o)"
Stop-Transcript | Out-Null
