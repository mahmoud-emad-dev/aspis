#!/usr/bin/env bash
# ASPIS end-to-end smoke test — Linux / macOS / WSL / Git-Bash.
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
#   ./scripts/smoke-test.sh            # run, then clean up the sandbox
#   ./scripts/smoke-test.sh --keep     # keep the sandbox for inspection
#
# Exit code 0 = every step passed. Non-zero = the first failure (printed in red).
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1

PASS=0
FAIL=0
say()  { printf '\033[1;36m[smoke]\033[0m %s\n' "$1"; }
ok()   { printf '\033[1;32m  PASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '\033[1;31m  FAIL\033[0m %s\n' "$1" >&2; FAIL=$((FAIL+1)); }

# check <label> <expected-substring> -- reads the command's stdout+stderr on fd 3
check() {
  local label="$1" needle="$2"
  if printf '%s' "$OUT" | grep -qiF "$needle"; then ok "$label"; else
    bad "$label  (expected to find: '$needle')"
    printf '       got: %s\n' "$(printf '%s' "$OUT" | head -3 | tr '\n' '|')" >&2
  fi
}

command -v uv >/dev/null 2>&1 || { bad "uv is not installed — see https://docs.astral.sh/uv/"; exit 1; }

SANDBOX="$(mktemp -d 2>/dev/null || mktemp -d -t aspis-smoke)"
PROJ="$SANDBOX/demo-proj"
cleanup() { [ "$KEEP" = 1 ] && say "sandbox kept at: $SANDBOX" || rm -rf "$SANDBOX"; }
trap cleanup EXIT

say "sandbox: $SANDBOX"
say "1/10  create an isolated venv + install ASPIS from $REPO"
uv venv "$SANDBOX/.venv" >/dev/null 2>&1 || { bad "uv venv failed"; exit 1; }
uv pip install --python "$SANDBOX/.venv" "$REPO" >/dev/null 2>&1 || { bad "install failed"; exit 1; }
ok "fresh install"

# locate the venv's aspis (Scripts on Windows, bin elsewhere)
if [ -x "$SANDBOX/.venv/Scripts/aspis.exe" ]; then ASPIS="$SANDBOX/.venv/Scripts/aspis.exe"
elif [ -x "$SANDBOX/.venv/Scripts/aspis" ];   then ASPIS="$SANDBOX/.venv/Scripts/aspis"
else ASPIS="$SANDBOX/.venv/bin/aspis"; fi
[ -e "$ASPIS" ] || { bad "aspis entry point not found in venv"; exit 1; }
PY="$(dirname "$ASPIS")/python"; [ -e "$PY" ] || PY="$(dirname "$ASPIS")/python.exe"

say "2/10  aspis --version";          OUT="$("$ASPIS" --version 2>&1)";                 check "version reports a build"      "aspis 0."
cd "$SANDBOX"  # a non-project dir, so doctor reports the pre-init state
say "3/10  doctor (outside a project)"; OUT="$("$ASPIS" doctor 2>&1)";                  check "doctor runs pre-init"         "not an ASPIS project"

mkdir -p "$PROJ"
say "4/10  init --write";             OUT="$("$ASPIS" init "$PROJ" --write 2>&1)";      check "init writes the brain"        ".aspis"
[ -d "$PROJ/.aspis" ] && ok "init created .aspis/" || bad "init created .aspis/"

cd "$PROJ"
say "5/10  status";                   OUT="$("$ASPIS" status 2>&1)";                    check "status detects the project"   "ASPIS project detected"
say "6/10  doctor (inside project)";  OUT="$("$ASPIS" doctor 2>&1)";                    check "doctor passes inside"         "All checks passed"
say "7/10  models (detect + route)";  OUT="$("$ASPIS" models 2>&1)";                    check "models shows a runtime"       "detected:"
say "8/10  models --sync";            OUT="$("$ASPIS" models --sync 2>&1)";             check "sync writes agent-models.yaml" "agent-models.yaml"
[ -f "$PROJ/.aspis/config/agent-models.yaml" ] && ok "agent-models.yaml exists" || bad "agent-models.yaml exists"
say "      models --available";       OUT="$("$ASPIS" models --available 2>&1)";        check "available lists the menu"     "available"

# prove a per-agent pin actually takes effect (uncomment the first reviewer line)
"$PY" - "$PROJ/.aspis/config/agent-models.yaml" <<'PY' 2>/dev/null
import io,sys,re
p=sys.argv[1]; s=io.open(p,encoding="utf-8").read()
s=re.sub(r"#\s*reviewer:\s*\S+", "reviewer: opus", s, count=1)
io.open(p,"w",encoding="utf-8").write(s)
PY
say "9/10  per-agent pin takes effect"; OUT="$("$ASPIS" models 2>&1)";                  check "reviewer pin resolves"        "pin reviewer"

say "10/10 bootstrap -y --write";     OUT="$("$ASPIS" bootstrap -y --write 2>&1)";      check "bootstrap completes"          "BOOTSTRAPPED"
                                      OUT="$("$ASPIS" bootstrap --check 2>&1)";          check "bootstrap recorded"           "bootstrapped:"

echo
if [ "$FAIL" -eq 0 ]; then printf '\033[1;32m[smoke] ALL %d CHECKS PASSED\033[0m — fresh install works end-to-end.\n' "$PASS"; exit 0
else printf '\033[1;31m[smoke] %d passed, %d FAILED\033[0m\n' "$PASS" "$FAIL"; exit 1; fi
