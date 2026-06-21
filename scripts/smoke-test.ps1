# ASPIS end-to-end smoke test — Windows (PowerShell 5+).
#
# Proves a *fresh install* of ASPIS works on this machine, with zero effect on
# your global tools or this repo: it builds a throwaway venv in a temp dir,
# installs ASPIS into it from this checkout (exactly as a real user would), then
# drives the whole pipeline and asserts each step.
#
#   install -> version -> doctor -> init -> status -> models (+sync/+available)
#   -> per-agent pin -> bootstrap
#
# Usage (from the repo root):
#   .\scripts\smoke-test.ps1           # run, then clean up the sandbox
#   .\scripts\smoke-test.ps1 -Keep     # keep the sandbox for inspection
#
# Exit code 0 = every step passed. Non-zero = at least one failure.
param([switch]$Keep)
$ErrorActionPreference = 'Stop'

$Repo = (Resolve-Path "$PSScriptRoot\..").Path
$script:Pass = 0
$script:Fail = 0
function Say($m)  { Write-Host "[smoke] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "  PASS $m" -ForegroundColor Green; $script:Pass++ }
function Bad($m)  { Write-Host "  FAIL $m" -ForegroundColor Red;   $script:Fail++ }
function Check($label, $needle, $out) {
  if ($out -match [regex]::Escape($needle)) { Ok $label }
  else { Bad "$label  (expected to find: '$needle')"; Write-Host "       got: $(($out -split "`n")[0..2] -join '|')" -ForegroundColor DarkGray }
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { Bad "uv is not installed — see https://docs.astral.sh/uv/"; exit 1 }

$Sandbox = Join-Path ([System.IO.Path]::GetTempPath()) ("aspis-smoke-" + [guid]::NewGuid().ToString("N").Substring(0,8))
$Proj = Join-Path $Sandbox "demo-proj"
New-Item -ItemType Directory -Force -Path $Sandbox | Out-Null
try {
  Say "sandbox: $Sandbox"
  Say "1/10  create an isolated venv + install ASPIS from $Repo"
  uv venv "$Sandbox\.venv" *> $null
  uv pip install --python "$Sandbox\.venv" "$Repo" *> $null
  if ($LASTEXITCODE -ne 0) { Bad "install failed"; exit 1 }
  Ok "fresh install"

  $Aspis = Join-Path $Sandbox ".venv\Scripts\aspis.exe"
  $Py    = Join-Path $Sandbox ".venv\Scripts\python.exe"
  if (-not (Test-Path $Aspis)) { Bad "aspis entry point not found in venv"; exit 1 }

  Say "2/10  aspis --version";           Check "version reports a build"       "aspis 0."             (& $Aspis --version 2>&1 | Out-String)
  Push-Location $Sandbox  # a non-project dir, so doctor reports the pre-init state
  Say "3/10  doctor (outside a project)"; Check "doctor runs pre-init"          "not an ASPIS project" (& $Aspis doctor 2>&1 | Out-String)
  Pop-Location

  New-Item -ItemType Directory -Force -Path $Proj | Out-Null
  Say "4/10  init --write";              Check "init writes the brain"          ".aspis"               (& $Aspis init "$Proj" --write 2>&1 | Out-String)
  if (Test-Path "$Proj\.aspis") { Ok "init created .aspis/" } else { Bad "init created .aspis/" }

  Push-Location $Proj
  Say "5/10  status";                    Check "status detects the project"     "ASPIS project detected" (& $Aspis status 2>&1 | Out-String)
  Say "6/10  doctor (inside project)";   Check "doctor passes inside"           "All checks passed"      (& $Aspis doctor 2>&1 | Out-String)
  Say "7/10  models (detect + route)";   Check "models shows a runtime"         "detected:"              (& $Aspis models 2>&1 | Out-String)
  Say "8/10  models --sync";             Check "sync writes agent-models.yaml"  "agent-models.yaml"      (& $Aspis models --sync 2>&1 | Out-String)
  if (Test-Path "$Proj\.aspis\config\agent-models.yaml") { Ok "agent-models.yaml exists" } else { Bad "agent-models.yaml exists" }
  Say "      models --available";        Check "available lists the menu"       "available"              (& $Aspis models --available 2>&1 | Out-String)

  # prove a per-agent pin actually takes effect (uncomment the first reviewer line)
  $amf = "$Proj\.aspis\config\agent-models.yaml"
  $txt = Get-Content -Raw -Encoding UTF8 $amf
  $txt = [regex]::Replace($txt, "#\s*reviewer:\s*\S+", "reviewer: opus", 1)
  Set-Content -Encoding UTF8 -Path $amf -Value $txt
  Say "9/10  per-agent pin takes effect"; Check "reviewer pin resolves"         "pin reviewer"           (& $Aspis models 2>&1 | Out-String)

  Say "10/10 bootstrap -y --write";      Check "bootstrap completes"            "BOOTSTRAPPED"           (& $Aspis bootstrap -y --write 2>&1 | Out-String)
                                         Check "bootstrap recorded"             "bootstrapped:"          (& $Aspis bootstrap --check 2>&1 | Out-String)
  Pop-Location
}
finally {
  if ($Keep) { Say "sandbox kept at: $Sandbox" } else { Remove-Item -Recurse -Force $Sandbox -ErrorAction SilentlyContinue }
}

Write-Host ""
if ($script:Fail -eq 0) { Write-Host "[smoke] ALL $($script:Pass) CHECKS PASSED — fresh install works end-to-end." -ForegroundColor Green; exit 0 }
else { Write-Host "[smoke] $($script:Pass) passed, $($script:Fail) FAILED" -ForegroundColor Red; exit 1 }
