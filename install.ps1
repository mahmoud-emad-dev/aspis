# ASPIS one-command installer — Windows (PowerShell 5+).
#
# Verifies prerequisites, installs `uv` if missing, installs the global `aspis`
# CLI, and runs `aspis doctor --verbose` to confirm and show where things live.
# Works two ways:
#
#   irm https://raw.githubusercontent.com/mahmoud-emad-dev/aspis/main/install.ps1 | iex
#   .\install.ps1           # from a clone (installs from the working tree)
$ErrorActionPreference = 'Stop'

function Say($m)  { Write-Host "[aspis] $m" -ForegroundColor Cyan }
function Fail($m) { Write-Host "[aspis] error: $m" -ForegroundColor Red; exit 1 }

# 1. Python 3.11+
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Fail "Python 3.11+ is required - https://python.org/downloads" }
$pv = & python -c 'import sys;print("%d.%d"%sys.version_info[:2])'
& python -c 'import sys;raise SystemExit(0 if sys.version_info[:2]>=(3,11) else 1)'
if ($LASTEXITCODE -ne 0) { Fail "Python >= 3.11 required (found $pv)" }
Say "Python $pv"

# 2. Git (recommended, not required)
if (Get-Command git -ErrorAction SilentlyContinue) { Say "git $((git --version).Split(' ')[2])" } else { Say "git not found (optional)" }

# 3. uv (install if missing)
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Say "installing uv ..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { Fail "uv install failed - see https://docs.astral.sh/uv" }
Say "uv $((uv --version).Split(' ')[1])"

# 4. Install the aspis CLI (from this clone if present, else from GitHub)
if ((Test-Path pyproject.toml) -and (Select-String -Path pyproject.toml -Pattern '^name = "aspis"' -Quiet)) {
    Say "installing aspis from this clone ..."
    uv tool install --reinstall .
} else {
    Say "installing aspis from GitHub ..."
    uv tool install --reinstall "git+https://github.com/mahmoud-emad-dev/aspis.git"
}

# 5. Ensure the shim is on PATH for this session
if (-not (Get-Command aspis -ErrorAction SilentlyContinue)) { $env:Path = "$env:USERPROFILE\.local\bin;$env:Path" }

# 6. Verify + show where everything lives (doctor warns, never fails, outside a project)
Say "verifying ..."
if (-not (Get-Command aspis -ErrorAction SilentlyContinue)) { Fail "aspis not on PATH - add %USERPROFILE%\.local\bin to PATH and re-open PowerShell" }
aspis --version
try { aspis doctor --verbose } catch { }

Write-Host ""
Say "installed. Next, in your project:"
Write-Host "  cd <your-project>"
Write-Host "  aspis init --write          # scaffold the ASPIS brain + runtime"
Write-Host "  aspis bootstrap --write     # make it live"
Write-Host "  aspis models --sync         # assign a model to each agent"
Write-Host "Run ``aspis doctor --verbose`` anytime to see install paths + detected runtimes."
