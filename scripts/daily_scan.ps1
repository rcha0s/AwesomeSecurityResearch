# ---------------------------------------------------------------------------
# daily_scan.ps1 - Unattended daily research scan for AwesomeSecurityResearch.
#
# Ingests fresh candidates (deterministic, no LLM), then runs Claude Code headless
# to analyze/verify/merge/render, and - if anything new was curated - commits on a
# dated branch and opens a PR for review. Never auto-merges; never pushes to main.
#
# Register it to run daily with scripts/install_daily_scan.ps1, or run by hand:
#     powershell -ExecutionPolicy Bypass -File scripts\daily_scan.ps1
# ---------------------------------------------------------------------------
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$stamp   = Get-Date -Format "yyyy-MM-dd"
$logDir  = Join-Path $repo "scripts\logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log     = Join-Path $logDir "daily_scan_$stamp.log"
function Log($m) { $line = "$(Get-Date -Format o)  $m"; $line | Tee-Object -FilePath $log -Append }

Log "=== daily scan $stamp starting in $repo ==="

# 1) Sync main and start a dated scan branch (idempotent per day). ------------
try {
    git fetch origin --quiet
    $branch = "scan/$stamp"
    # NEVER clobber an existing branch. If today's scan branch already exists
    # (locally or on the remote), a scan already ran or someone is working on it —
    # bail rather than delete it. This is the safe default; `git branch -D` here
    # once destroyed in-progress local work.
    git show-ref --verify --quiet "refs/heads/$branch"
    $localExists = ($LASTEXITCODE -eq 0)
    git show-ref --verify --quiet "refs/remotes/origin/$branch"
    $remoteExists = ($LASTEXITCODE -eq 0)
    if ($localExists -or $remoteExists) {
        Log "branch $branch already exists (local=$localExists remote=$remoteExists) - skipping to avoid clobber."
        exit 0
    }
    # Guard against running on top of uncommitted work in the primary tree.
    if (git status --porcelain) { Log "working tree not clean - refusing to run."; exit 1 }
    git checkout main --quiet
    git merge --ff-only origin/main --quiet
    git checkout -b $branch --quiet
    Log "on branch $branch"
} catch { Log "GIT SETUP FAILED: $_"; exit 1 }

# From here on, native tools (python/git/gh/wsl) write progress to stderr, which
# under -ErrorActionPreference Stop PowerShell 5.1 wraps as a terminating error
# (spurious 'Traceback' failures). Switch to Continue; we check outcomes explicitly.
$ErrorActionPreference = "Continue"

# 2) Ingest candidates (best-effort; a failing source never aborts the run). ---
$py = "python"
foreach ($step in @(
    @("aggregate.py", @()),
    @("ingest_github.py", @("--max", "5")),
    @("ingest_ghsa.py",   @("--max", "25")),
    @("ingest_hn.py",     @("--max", "6"))
)) {
    $script = $step[0]; $argv = $step[1]
    try { & $py "scripts\$script" @argv 2>&1 | Tee-Object -FilePath $log -Append; Log "ingest ok: $script" }
    catch { Log "ingest WARN ($script): $_" }
}
# Twitter needs WSL + burner cookies; best-effort, never fatal.
try {
    wsl bash -lc 'source ~/.agent-reach/twitter.env 2>/dev/null; cd /mnt/c/Users/rohan/Desktop/AwesomeSecurityResearch && ~/.venvs/asr/bin/python scripts/ingest_twitter.py --max 15' 2>&1 | Tee-Object -FilePath $log -Append
    Log "ingest ok: twitter (wsl)"
} catch { Log "ingest WARN (twitter/wsl): $_" }

# 3) Headless Claude analysis (analyze -> verify -> merge -> render). ----------
# acceptEdits + an explicit allowlist (NOT --dangerously-skip-permissions).
$prompt = Get-Content (Join-Path $repo "scripts\daily_scan_prompt.md") -Raw
$tools  = "Bash Edit Write Read Grep Glob Skill Task WebFetch"
Log "invoking claude headless..."
$out = & claude -p $prompt --permission-mode acceptEdits --allowedTools $tools 2>&1
$out | Tee-Object -FilePath $log -Append | Out-Null

$result = ($out | Select-String -Pattern "SCAN_RESULT:" | Select-Object -Last 1).ToString()
if (-not $result) { $result = "SCAN_RESULT: (no summary line emitted)" }
Log "claude result: $result"

# 4) Commit + open PR only if the render produced changes. --------------------
git add -A
$dirty = git status --porcelain
if (-not $dirty) {
    Log "no changes produced - nothing curated today; skipping PR."
    git checkout main --quiet
    exit 0
}
if ($result -match "merged=0") {
    Log "SCAN_RESULT merged=0 - discarding empty scan."
    git checkout . --quiet; git checkout main --quiet
    exit 0
}

$body = "Automated daily scan for $stamp.`n`n$result`n`nAnalysis by headless Claude Code; every finding was independently verified and excerpts grounded against the source. Review before merge."
git commit -q -m "content: $stamp automated daily scan" -m $result
try {
    git push -u origin $branch --quiet
    & gh pr create --base main --head $branch --title "content: $stamp daily scan" --body $body 2>&1 | Tee-Object -FilePath $log -Append
    Log "PR opened for $branch."
} catch { Log "PUSH/PR FAILED (branch committed locally): $_"; exit 1 }

git checkout main --quiet
Log "=== daily scan $stamp complete ==="
