# ASPIS manual test plan — install → init → bootstrap → git

Four ordered tests. Run each on **WSL and Windows**, record **P/F** per case, and
send any failure's output. Do not advance to the next test until the current one
is fully green. (Test 1 — installation — is the runbook already delivered; its
matrix is summarized at the bottom.)

Legend: ✅ pass · ⚠️ warn-but-ok · ❌ fix before moving on.

---

# TEST 2 — `aspis init` (scaffold + export)

**What init does** (lifecycle: `pre-init hooks → init_core → post-init hooks`):
1. export the profile — render agents, copy skills/templates/hooks/scripts;
2. scaffold the brain dirs (`.gitkeep` only while empty);
3. ship helper scripts (`context/`, `planning/`, `hooks/`, `git/`);
4. write root files (`AGENTS.md`, `CLAUDE.md`, `.gitignore`);
5. `git init`; 6. arm the git hooks (`.git/hooks`).

### 2.1 Dry-run shows, writes nothing
```bash
mkdir -p /tmp/t2-empty && cd /tmp/t2-empty
aspis init                 # dry-run
ls -A                      # PASS: still EMPTY (nothing written)
aspis init                 # PASS: every line prefixed DRY-RUN; ends "Re-run with --write"
```

### 2.2 `--write` on an empty folder (the happy path)
```bash
aspis init --write
```
Inspect (PASS criteria in comments):
```bash
ls -A .aspis                       # context/ config/ index/ scripts/ features/ … + manifest later
ls -A .opencode/agents             # 11 agents rendered
ls -A .opencode/skills             # 33 skills copied
test -f AGENTS.md && echo ok       # root entry file
test -f .gitignore && echo ok      # root gitignore
test -d .git && echo ok            # git initialized
ls .git/hooks | grep -vE 'sample'  # commit-msg, pre-commit, post-commit armed
ls -A .aspis/scripts/context .aspis/scripts/hooks .aspis/scripts/git   # helper scripts shipped
```
- ✅ next-step "Next:" block printed (bootstrap/models/AGENTS/runtime).
- ✅ `.gitkeep` only in dirs that are genuinely empty (none in populated ones).

### 2.3 Runtime selection
```bash
mkdir -p /tmp/t2-claude && cd /tmp/t2-claude
aspis init --write --runtime claude
ls .claude/agents                  # PASS: Claude assets rendered, no .opencode
aspis init --write --runtime claude --runtime opencode /tmp/t2-both   # PASS: both
```

### 2.4 Existing folder — real code present (must not clobber)
```bash
mkdir -p /tmp/t2-code/src && cd /tmp/t2-code
printf 'print("hi")\n' > src/app.py ; printf '# My App\n' > README.md ; git init -q
aspis init --write
cat src/app.py ; cat README.md     # PASS: UNCHANGED (init never overwrites product files)
test -d .aspis && echo "brain added ok"
```
- ✅ existing `.git` reused, not re-init destructively.
- Re-run `aspis init --write` → PASS: idempotent or clear "exists" message; `--force` needed to overwrite.

### 2.5 Existing folder — a *stale/bad* runtime dir present
```bash
mkdir -p /tmp/t2-stale/.opencode/agents && cd /tmp/t2-stale
echo "garbage" > .opencode/agents/old.md ; git init -q
aspis init --write          # without --force
aspis init --write --force  # with --force
ls .opencode/agents         # PASS: --force re-renders clean; note whether old.md is reaped
```
*(Record: does init warn about pre-existing runtime files? Should it reconcile or refuse without --force?)*

### 2.6 Stack detection at init/bootstrap time
```bash
cd /tmp/t2-code           # has src/app.py (python)
aspis status              # PASS: project detected
# stack is detected at bootstrap (Test 3); note here what detect sees for a python repo
```

### 2.7 Catalog ↔ exported parity (the dogfood invariant)
```bash
# In the ASPIS repo itself:
cd /path/to/aspis-clone
uv run pytest -q -k "transform or export or parity"   # PASS: exported runtime == catalog
```
- Record: any profile in `src/aspis/data/profiles/` **not** wired to init? (compare profile list vs what init can export).
- Record: rendered agent frontmatter has a valid `model:` (tier resolved), correct `mode:`, tools.

**TEST 2 exit:** every case ✅, product files never clobbered, parity green.

---

# TEST 3 — `aspis bootstrap` (make the project live)

**What bootstrap does** (`pre hooks → bootstrap_core → post hooks`, two commits):
collect details (`detect.detect_stack`) → fill `AGENTS.md`/`CLAUDE.md` slots →
write `project.yaml` (mode) → write `manifest.json` (bootstrapped flag) →
promote leads to primary → brain fill (runs `.aspis/scripts/context/update.py`)
→ commit init scaffolding, then commit bootstrap.

### 3.1 Dry-run writes nothing
```bash
cd /tmp/t2-code
aspis bootstrap            # PASS: DRY-RUN, "Nothing was written", shows --write
git log --oneline | head   # PASS: unchanged
```

### 3.2 `--write -y` (non-interactive happy path)
```bash
aspis bootstrap --write -y
```
Inspect:
```bash
grep -v '<!-- ' AGENTS.md | head        # PASS: definition + Stack slots FILLED (no leftover placeholders)
cat .aspis/config/project.yaml          # PASS: mode set (production)
cat .aspis/manifest.json                # PASS: bootstrapped: true, name/goal/stack
aspis bootstrap --check                 # PASS: "bootstrapped: <path>"
```
- ✅ "promote leads to primary: system-lead, planning-lead, build-lead, reviewer".
- ✅ two commits exist (init scaffolding + bootstrap), messages convention-clean.

### 3.3 Brain fill / context / indexing / file registry (the "full filling")
```bash
ls -A .aspis/context                    # CURRENT_STATE.md, RECENT_CHANGES.md, … filled (not empty)
ls -A .aspis/index                      # FILE_REGISTRY.yaml, CODE_MAP.md present + populated
test -s .aspis/index/FILE_REGISTRY.yaml && echo "registry filled"
```
- Record: are placeholder templates copied into `.aspis/**` folders, and then **filled** by the context scripts (not left as raw placeholders)?
- Record: did the brain-fill script run (look for "brain fill: .aspis/scripts/context/update.py" in output)?

### 3.4 Interactive path
```bash
cd /tmp/t3-interactive && aspis init --write -q 2>/dev/null; aspis bootstrap --write
# Answer the prompts. PASS: answers land in manifest + AGENTS.md slots.
```

### 3.5 Provider / model detection runs even if the user never ran `models --sync`
```bash
aspis doctor --verbose                  # PASS: runtimes detected; models line present
# Record: does bootstrap (or first doctor) trigger detection so the project is
# usable without a manual `aspis models --sync`? If not, note as a gap.
```

### 3.6 Git validation + hygiene after bootstrap (first commit is clean)
```bash
git status --short                      # PASS: clean tree (bootstrap committed its work)
git log --oneline                       # PASS: 2 conventional commits, no AI attribution
aspis commits --audit                   # PASS: history conforms
git ls-files | grep .gitkeep            # PASS: no stale .gitkeep in populated dirs
```

### 3.7 Live hooks / scripts smoke (everything downstream will work)
```bash
echo "x" > note.md
aspis commit note.md --type docs --title "add a note"   # PASS: hooks run, message composed, commit lands
git log -1 --format=%B                                  # PASS: clean, conventional
```
- Record: any script/hook that errors, warns, or is skipped during init+bootstrap (these are the "downstream will break" risks).

**TEST 3 exit:** project is fully filled (context + index + registry), leads promoted, detection done, git clean & conventional, hooks live — i.e. any agent/script run *after* this works with no missing pieces.

---

# TEST 4 — Git subsystem (the hygiene wall)

**Surface:** `aspis commit` (single writer) · `aspis commits --audit/--fix` (F-012)
· commit-msg hook (style + attribution auto-fix) · pre-commit hook (junk clean,
format/lint-fix, secret scan) · `.gitkeep` reaping · `aspis gitignore` (stack →
ignore, Toptal + offline cache).

### 4.1 Commit message style + attribution auto-fix
```bash
printf 'feat(F-999): do a thing\n\nCo-Authored-By: Some Bot\n' | git commit -F - --allow-empty
git log -1 --format=%B          # PASS: Co-Authored-By auto-stripped, commit still made
git commit --allow-empty -m "bad subject with no type"   # PASS: warns (warn mode), still commits
aspis commits --audit           # PASS: lists any non-conforming historical messages
```

### 4.2 History audit + fix
```bash
aspis commits --audit           # exit 1 + per-commit detail when violations exist
aspis commits --fix             # PASS: backup ref made, auto-fixable messages rewritten, content identical
git branch | grep backup/       # PASS: a backup/commits-fix-* ref exists
```

### 4.3 Junk / garbage auto-clean (pre-commit)
```bash
printf 'junk\n' > '=1.0.0'      # a shell-redirect ghost file
git add -A && git commit -m "chore: test junk reap" --allow-empty
git ls-files | grep '=1.0.0' && echo "LEAK ❌" || echo "reaped ✅"
```

### 4.4 `.gitkeep` auto-removal when no longer needed
```bash
# a brain dir that started empty (had .gitkeep) now has real content:
echo "data" > .aspis/features/keepcheck.txt
git add -A && git commit -m "chore: populate dir"
git ls-files .aspis/features | grep .gitkeep && echo "STALE ❌" || echo "reaped ✅"
```

### 4.5 `aspis gitignore` — stack detection + correct ignores
```bash
cd /tmp/t2-code                 # python project
aspis gitignore
cat .gitignore                  # PASS: python ignores (__pycache__, .venv, *.pyc, …) present + merged, not duplicated
# Record: are the brain's own .gitignore(s) present (.aspis/.gitignore) and correct?
```
- Record: offline templates available (python/node/vscode/…) under the gitignore script's cache?
- Record: online fallback — when offline cache misses a stack, does it fetch from gitignore.io/Toptal and cache it?

### 4.6 Guards / enforcement mode
```bash
grep enforcement .aspis/config/hooks.yaml     # warn by default (never blocks)
# Record: protected_paths (rules/**) — a change there needs ASPIS_ALLOW_PROTECTED=1.
```

### 4.7 Runtime-agent fallback (where a script can't fix deterministically)
- Record (design check, may be a gap): when a hook/script cannot resolve something
  deterministically (e.g. a non-trivial gitignore for an exotic stack, or a malformed
  message it can't auto-fix), is there a path to hand it to an available runtime
  agent? Note whether this exists or is future work.

**TEST 4 exit:** messages conform & self-heal, history auditable/fixable, junk &
stale `.gitkeep` reaped automatically, `.gitignore` correct for the stack from the
first commit — git hygiene holds with no manual effort.

---

# TEST 1 — installation (summary; full runbook delivered separately)

Clean removal → Method A (clone branch + `./install.sh`/`.ps1`) → Method B
(`uv tool install git+…@branch`) → Method C (`uv tool install .`) → verify
(`--version`, `doctor`, `doctor --verbose`) → edge cases (no chmod, uv
auto-install, fresh-shell PATH, reinstall) → uninstall (`aspis uninstall
[--write]`, `uv tool uninstall aspis`) → the true one-command (after merge→main +
repo Public). Automated cross-check: `./scripts/smoke-test.sh`.
