# ASPIS manual test plan — install → init → bootstrap → git

Four ordered tests. Run each on **WSL and Windows**, record **P/F** per case, and
send any failure's output. Do not advance to the next test until the current one is
fully green.

Legend: ✅ pass · ⚠️ warn-but-ok · ❌ fix before moving on.

> Reinstall from the working branch (the v0 work lives on `feat/F-013-install-ux`,
> not `main` yet):
>
> ```bash
> git clone -b feat/F-013-install-ux https://github.com/mahmoud-emad-dev/aspis.git
> cd aspis && ./install.sh        # or  .\install.ps1  on Windows
> ```
>
> `install.sh/.ps1` verify Python ≥ 3.11 + git + uv, install the `aspis` CLI, and
> run `aspis doctor --verbose`. Expect `[aspis] Python X.Y` with no traceback.

---

# TEST 1 — installation

```bash
# clean slate
uv tool uninstall aspis 2>/dev/null || true        # PowerShell: uv tool uninstall aspis 2>$null
aspis uninstall --write                            # removes machine-wide state, keeps project brains

# install from the branch clone
./install.sh                                       # PowerShell: .\install.ps1
aspis --version                                    # PASS: aspis 0.1.0bN
aspis doctor --verbose                             # PASS: paths + runtimes, no FAIL
```
- ✅ `doctor --verbose` prints **Installation** (cli/config/data/cache) and **Runtimes** (claude/opencode/… on PATH).
- ✅ Windows: no `SyntaxError` in the Python-version line (the PS quote-stripping fix).

---

# TEST 2 — `aspis init` (scaffold + export)

**What init does:** export the profile (agents/skills/commands/templates/config/rules/
workflows) → scaffold the **filled** brain dirs → ship helper scripts → write root files
→ `git init` → arm git hooks. Init does **not** commit (bootstrap does).

### 2.1 Dry-run writes nothing
```bash
mkdir -p /tmp/t2 && cd /tmp/t2
aspis init                      # dry-run
ls -A                           # PASS: still EMPTY
```

### 2.2 `--write` on an empty folder
```bash
aspis init --write
```
Inspect (PASS criteria in comments):
```bash
ls .opencode/agents | wc -l          # 12 agents (incl. the transient `bootstrap`)
ls .opencode/skills | wc -l          # 34 skills (incl. `project-onboarding`)
ls .opencode/commands | wc -l        # 5 commands
ls .aspis/workflows | wc -l          # 6 workflows (incl. `bootstrap.md`)
ls .aspis/config | wc -l             # 10 (9 exported config incl. the 4 model files + purposes.json)
ls -A .aspis                         # config context index rules scripts templates workflows + .gitignore
test -f AGENTS.md && echo ok         # root entry file
ls .git/hooks | grep -vE 'sample'    # commit-msg, pre-commit, post-commit armed
git log --oneline 2>&1               # PASS: "no commits yet" — init never commits
```
- ✅ **On-demand dirs are NOT scaffolded empty**: `.aspis/{features,current,research}` do **not** exist yet (no `.gitkeep`-only folders).
- ✅ The 7 scaffold dirs exist: config, context, index, rules, scripts, templates, workflows.
- ✅ Root `.gitignore` carries the universal baseline: `.env`, `.DS_Store`, `*.swp`, `!.env.example`.

### 2.3 Runtime selection
```bash
aspis init --write --runtime claude /tmp/t2-claude   # PASS: .claude/ rendered + CLAUDE.md
```

### 2.4 Existing folder with real code (must not clobber)
```bash
mkdir -p /tmp/t2-code/src && cd /tmp/t2-code
printf 'print("hi")\n' > src/app.py ; printf '# My App\n' > README.md ; git init -q
aspis init --write
cat src/app.py ; cat README.md       # PASS: UNCHANGED
test -d .aspis && echo "brain added"
```
- Re-run `aspis init --write` → PASS: idempotent / clear message; `--force` to overwrite.

### 2.5 Catalog ↔ export parity (in the ASPIS repo)
```bash
uv run pytest -q -k "transform or export or parity or init"   # PASS: export == catalog
```

**TEST 2 exit:** every case ✅, no empty brain folders, product files never clobbered, init left uncommitted.

---

# TEST 3 — `aspis bootstrap` (make the project live)

**What bootstrap does** (two commits, then self-cleans): fill AGENTS.md/CLAUDE.md slots
→ enrich `.gitignore` from the stack → write `project.yaml` + `manifest.json` →
detect runtimes → `models --sync` → promote 4 leads (→ 5 primaries) → brain-fill →
gate (doctor + readiness + validation + structure) → self-clean the onboarding package
→ stamp `bootstrap.done` → git self-test.

### 3.1 First-run gate
```bash
cd /tmp/t2-code
aspis bootstrap --check               # PASS: "NOT bootstrapped" (exit 1)
```
(In a runtime, `project-lead` runs this on the first message and routes to the `bootstrap`
agent before any feature work.)

### 3.2 `--write -y` (non-interactive happy path)
```bash
aspis bootstrap --write -y --goal "a tiny tool" --stack python
```
Inspect:
```bash
grep -c 'filled at bootstrap' AGENTS.md          # 0 — slots filled
cat .aspis/manifest.json                          # bootstrapped:true, bootstrap_engine_version, goal/stack
ls .aspis/config | wc -l                          # 12 (9 + project.yaml + agent-models.yaml + purposes.json)
test -f .aspis/config/agent-models.yaml && echo ok  # models --sync ran
aspis bootstrap --check                            # PASS: "bootstrapped" (exit 0)
```

### 3.3 Canonical structure — every folder filled, none empty/stray
```bash
for d in config context index rules scripts templates workflows; do
  echo "$d: $(find .aspis/$d -type f | wc -l) files"      # PASS: all > 0 (FILLED)
done
test ! -d .aspis/state && echo "no state folder ✅"        # PASS: no stray 'state' dir
ls .aspis/features .aspis/current 2>/dev/null || echo "on-demand, not created yet ✅"
```

### 3.4 Brain fill / index / registry
```bash
test -s .aspis/index/FILE_REGISTRY.yaml && echo "registry filled"
test -s .aspis/index/CODE_MAP.md && echo "code map filled"
test -s .aspis/context/CURRENT_STATE.md && echo "state filled"
```

### 3.5 Five primaries + the onboarding package self-cleaned
```bash
grep -l 'mode: primary' .opencode/agents/*.md | wc -l    # 5 (project-lead + planning/build/reviewer/system)
test ! -f .opencode/agents/bootstrap.md && echo "bootstrap agent removed ✅"
test ! -d .opencode/skills/project-onboarding && echo "onboarding skill removed ✅"
test ! -f .aspis/workflows/bootstrap.md && echo "bootstrap workflow removed ✅"
```

### 3.6 Clean history + git self-test
```bash
git log --oneline                  # PASS: 2 ours-only commits (initialize + bootstrap)
git status --porcelain             # PASS: clean (no dangling .gitkeep; user code untracked = fine)
```
- ✅ In the bootstrap output, look for `git self-test: ok (7 checks passed)` — the probe-commit proof that hooks fire (junk clean, stale `.gitkeep` reap, attribution strip), rolled back so history is untouched.
- ✅ `structure: canonical (no stray folders)` and `validation: all config + agent files parse`.

### 3.7 Re-run is idempotent
```bash
aspis bootstrap --write -y         # PASS: no duplicate commits; package stays gone; "already bootstrapped"
```

**TEST 3 exit:** project is fully filled (no empty folders, no `state`), 5 primaries, agent-models
written, gates green, package self-cleaned, history clean, git subsystem self-test passed.

---

# TEST 4 — Git subsystem (the hygiene wall)

**Surface:** `aspis commit` · `aspis commits --audit/--fix` · commit-msg (style + attribution
auto-fix) · pre-commit (junk clean, format/lint-fix, secret scan, stale-`.gitkeep` reap) ·
`aspis gitignore` (offline-first) · the bootstrap git self-test.

### 4.1 Message style + attribution auto-fix
```bash
printf 'feat(F-999): do a thing\n\nCo-Authored-By: Some Bot\n' | git commit -F - --allow-empty
git log -1 --format=%B           # PASS: Co-Authored-By auto-stripped, commit still made
```

### 4.2 History audit + fix
```bash
aspis commits --audit            # lists non-conforming history (exit 1 if any)
aspis commits --fix              # PASS: backup ref made, messages rewritten, content identical
```

### 4.3 Junk + stale `.gitkeep` auto-clean
```bash
printf 'x\n' > '=1.0.0'          # a shell-redirect ghost
git add -A && git commit -m "chore: probe" --allow-empty
git ls-files | grep '=1.0.0' && echo "LEAK ❌" || echo "reaped ✅"
```

### 4.4 `aspis gitignore` — offline-first, stack-aware
```bash
cd /tmp/t2-code
aspis gitignore python           # PASS: offline cache hit, no network
aspis gitignore go               # PASS: offline (go/rust/java/node/python ship in the cache)
grep -c '__pycache__' .gitignore # PASS: python block present, merged (not duplicated)
```
- Record: an uncached stack (e.g. `elixir`) falls back to the online Toptal API and caches it.

### 4.5 Root vs brain gitignore (nature-based)
```bash
git check-ignore .env .DS_Store                          # PASS: ignored (root baseline)
git check-ignore .aspis/index/CODE_MAP.md                # PASS: ignored (generated)
git check-ignore .aspis/config/.runtime-inventory.json   # PASS: ignored (machine state)
git check-ignore .aspis/config/models.yaml && echo BAD || echo "tracked ✅ (source)"
```

**TEST 4 exit:** messages conform & self-heal, history auditable/fixable, junk & stale
`.gitkeep` reaped, `.gitignore` correct by file nature from the first commit — git hygiene
holds with no manual effort, and bootstrap *proved* it via the self-test.

---

## Automated cross-check (in the ASPIS repo)
```bash
uv run pytest -q                 # full suite
uv run ruff format --check src tests && uv run ruff check src tests
./scripts/smoke-test.sh          # PowerShell: .\scripts\smoke-test.ps1
```
