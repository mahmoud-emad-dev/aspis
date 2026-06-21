#!/usr/bin/env bash
# ASPIS one-command installer — Linux / macOS.
#
# Verifies prerequisites, installs `uv` if missing, installs the global `aspis`
# CLI, and runs `aspis doctor --verbose` to confirm and show where things live.
# Works two ways:
#
#   curl -fsSL https://raw.githubusercontent.com/mahmoud-emad-dev/aspis/main/install.sh | bash
#   ./install.sh            # from a clone (installs from the working tree)
set -euo pipefail

REPO_URL="https://github.com/mahmoud-emad-dev/aspis.git"

say()  { printf '\033[1;36m[aspis]\033[0m %s\n' "$1"; }
fail() { printf '\033[1;31m[aspis] error:\033[0m %s\n' "$1" >&2; exit 1; }

# 1. Python 3.11+
command -v python3 >/dev/null 2>&1 || fail "Python 3.11+ is required — https://python.org/downloads"
PYV="$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
python3 -c 'import sys;raise SystemExit(0 if sys.version_info[:2]>=(3,11) else 1)' \
  || fail "Python >= 3.11 required (found $PYV)"
say "Python $PYV"

# 2. Git (recommended, not required)
if command -v git >/dev/null 2>&1; then say "git $(git --version | awk '{print $3}')"; else say "git not found (optional)"; fi

# 3. uv (install if missing)
if ! command -v uv >/dev/null 2>&1; then
  say "installing uv ..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 || fail "uv install failed — see https://docs.astral.sh/uv"
say "uv $(uv --version | awk '{print $2}')"

# 4. Install the aspis CLI (from this clone if present, else from GitHub)
if [ -f pyproject.toml ] && grep -q '^name = "aspis"' pyproject.toml 2>/dev/null; then
  say "installing aspis from this clone ..."
  uv tool install --reinstall .
else
  say "installing aspis from $REPO_URL ..."
  uv tool install --reinstall "git+$REPO_URL"
fi

# 5. Ensure the shim is on PATH for this shell
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) export PATH="$HOME/.local/bin:$PATH"; say "added ~/.local/bin to PATH for this session";; esac

# 6. Verify + show where everything lives (doctor warns, never fails, outside a project)
say "verifying ..."
aspis --version || fail "aspis not on PATH — add ~/.local/bin to PATH and re-open your shell"
aspis doctor --verbose || true

cat <<'DONE'

[aspis] installed. Next, in your project:
  cd <your-project>
  aspis init --write          # scaffold the ASPIS brain + runtime
  aspis bootstrap --write     # make it live
  aspis models --sync         # assign a model to each agent
Run `aspis doctor --verbose` anytime to see install paths + detected runtimes.
DONE
