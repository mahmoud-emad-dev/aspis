# F-016 Research — System agent pattern: how agentic systems manage their own infrastructure

> **Feature:** F-016 — agent system architecture
> **Mode:** production · **Phase:** plan
> **Compiled:** 2026-06-25 · **Sources verified through:** 2026-06-25
> **Scope:** patterns for an agent that safely edits the system that runs it — its own
> agents, skills, tools, hooks, templates, workflows, config, plugins, and profiles.

This is a **distilled reference**, not a research dump. Each section ends with
**"Implication for ASPIS"** so the plan/builder can read it without re-deriving
the lesson.

---

## TL;DR — Top 5 patterns for system self-management

1. **Filesystem-based skills with progressive disclosure** (Anthropic Agent Skills,
   CrewAI Skills). Each skill is a directory rooted at a `SKILL.md` with YAML
   frontmatter; metadata (~100 tokens) loads at startup, body loads when triggered,
   bundled scripts/resources load on demand. The "system agent" reads the file
   with bash, never injects the whole library into the prompt.

2. **MCP as the tool/plugin contract** (Model Context Protocol, 2025-06-18 spec).
   A JSON-RPC 2.0 client-server protocol with three server primitives — `tools`
   (model-controlled actions), `resources` (application-controlled context),
   `prompts` (user-controlled templates) — plus `notifications/tools/list_changed`
   for hot-reload, `elicitation` for the server to ask the user, and `sampling`
   for the server to ask the client LLM. Now the de-facto standard: Claude, VS
   Code, Cursor, ChatGPT, Spring AI all ship MCP clients.

3. **Sandboxed code execution with explicit approval hooks** (AutoGen
   `DockerCommandLineCodeExecutor`, AutoGen `DefaultInterventionHandler`).
   Never run LLM-generated code on the host. AutoGen's two patterns compose:
   execute in a Docker container **and** intercept every tool call to prompt
   the user with `DefaultInterventionHandler.on_send` before allowing it. The
   handler can raise `ToolException` to block the call.

4. **Manifest + contribution-point plugin model** (VS Code extensions,
   GitHub Actions). A `package.json`/`action.yml` manifest declares what the
   extension contributes (commands, tools, languages, grammars, settings,
   activation events, dependencies). The host loads the manifest, runs the
   extension in a separate process (`Extension Host`), and refuses DOM access.
   Combines well with extension *packs* (`extensionPack`/`uses:`) to bundle
   related capabilities.

5. **Durable, replayable workflow engines** (Temporal, Prefect, GitHub
   Actions). Workflow code is pure, side-effects are *activities* whose results
   are recorded; the engine can crash and replay the workflow from event
   history. For an agent system, this means plan→build→review cycles are
   versioned, restartable, and auditable — and the engine itself can be the
   "system agent" that decides what to do next based on the recorded history.

For ASPIS specifically: ASPIS already has a file-first brain (`.aspis/`).
Pattern 1 (filesystem skills) and Pattern 4 (manifest + contributions) fit
without inventing new machinery. Pattern 3 (intervention handler) is the right
shape for the human-gate rule. Pattern 5 (Temporal-style durability) maps to
the existing `CORE_LOOP.md` plan→build→review design.

---

## 1. Self-modifying agent systems — safety patterns

### 1.1 The threat model is concrete

The most common failure mode is **prompt-induced tool misuse**: an LLM is fed
external content (a fetched URL, a tool description from a third-party MCP
server, a user-uploaded skill) and the new content tells it to call a
high-impact tool (write a file, run a command, call an API with credentials).
MCP's spec section 4 ("Security and Trust & Safety") and Anthropic's
"Security considerations" page on Skills both call this out as the dominant
risk.

### 1.2 Defense layers (what real systems do)

| Layer | Mechanism | Source |
|---|---|---|
| **Sandbox the executor** | Run LLM-generated code in Docker, not on the host. | AutoGen `DockerCommandLineCodeExecutor` (AutoGen docs: code-execution-groupchat). Local execution "is not recommended due to the risk of running LLM generated code in your local environment." |
| **Intercept every tool call** | A handler runs in the message pipeline; it can show a confirmation prompt, modify the call, or drop the message entirely. | AutoGen `DefaultInterventionHandler.on_send` — when the user denies a call, the handler raises `ToolException` and the runtime propagates it. |
| **Treat external descriptions as untrusted** | Don't trust what a tool's `description` says it does, unless the tool comes from a trusted server. | MCP spec § "Tool Safety": "descriptions of tool behavior such as annotations should be considered untrusted, unless obtained from a trusted server." |
| **Require explicit user consent for any tool invocation** | UI-level: dialog before tool call, with "Always Allow" as an opt-in shortcut, not a default. | VS Code Language Model Tool API — `prepareInvocation` returns a `confirmationMessages` block; "A generic confirmation dialog will always be shown for tools from extensions." |
| **Make descriptions decide usage, not action** | Tools declare *what* and *when*; the model decides *if*; the user decides *now*. | MCP primitives: tools are "model-controlled", resources are "application-controlled", prompts are "user-controlled". |
| **Deny DOM/UI access to extensions** | Extensions run in a separate process (the *Extension Host*); they cannot inject CSS or HTML into the host's UI. | VS Code Extension Host: "we run extensions in an Extension Host process and prevent direct access to the DOM." |

### 1.3 Self-modification in the MCP world

MCP servers can **proactively push updates** to clients: when a server
declares `"listChanged": true` in its `tools` capability at initialization,
it can send `notifications/tools/list_changed` at runtime. The client then
re-issues `tools/list` to refresh its registry. This is the protocol's
escape hatch for *dynamic tool sets* without a restart.

```json
// MCP initialize response (server side)
{
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": { "tools": { "listChanged": true }, "resources": {} },
    "serverInfo": { "name": "filesystem", "version": "1.0.0" }
  }
}
```

This is the cleanest published pattern for an agent system that *evolves its
own tool surface at runtime* without reloading the host.

### 1.4 Implication for ASPIS

ASPIS agents write to `.aspis/`. The same risk applies — a fetched file, a
copy-pasted prompt, or a new skill could instruct an agent to overwrite
governance files. ASPIS's existing protection engine (F-015) is the
*executor-side* of this defense. The remaining gap is the *handler-side*:
AutoGen-style intervention, where every write that touches `RULES`/`DECISIONS`/
`ARCHITECTURE` pauses for an explicit human confirmation rather than a
diff/approve later. Pair the two and you have defense in depth.

---

## 2. System administration agents — managing config, templates, hooks, scripts

### 2.1 Three patterns for "the agent that manages the system"

| Pattern | Example | How the system is administered |
|---|---|---|
| **Manifest + contribution points** | VS Code extension (`package.json` with `contributes`, `activationEvents`, `commands`, `configuration`, `menus`, `keybindings`, `snippets`, `languages`, `grammars`) | A static JSON manifest declares *what* the system will add. The host (VS Code) reads the manifest and acts on it. |
| **Shell-script hooks over a contract file** | GitHub Actions (`on:`, `jobs.<id>.steps[]`, `uses: owner/repo@version`, custom `actions/`) | A YAML file declares triggers and steps; each step is either a shell command or a reusable action reference. |
| **Server capabilities over JSON-RPC** | MCP (`initialize` → `tools/list`, `resources/list`, `prompts/list`; subscribe to `notifications/*`) | A server's tool/resource/prompt set is queried dynamically; the host treats the manifest as the source of truth. |

All three have the same shape: a **declarative description** of the system's
shape, with the host doing the work. None of them let the extension run
arbitrary code at *host start* — that is the shared safety property.

### 2.2 Hooks — when the system runs YOUR code

- **VS Code**: `activationEvents` (e.g. `onLanguage:python`, `onCommand:foo`,
  `*` for "run on startup if installed") determine when the extension host
  spins up the extension. There is also an **uninstall hook**:
  `"scripts": { "vscode:uninstall": "node ./out/src/lifecycle" }` runs on
  full uninstall.
- **GitHub Actions**: `on:` triggers fire workflows; within a step, you can
  run `run:` (shell) or `uses:` (action). Actions themselves have a
  `action.yml` describing `inputs`, `outputs`, `runs.using`, `runs.main`.
- **MCP**: there are no host-side hooks, only protocol-level events
  (`notifications/tools/list_changed`, `notifications/resources/updated`,
  `notifications/cancelled`). The server decides when to push them.

### 2.3 Implication for ASPIS

ASPIS's "system agent" is the thing that edits `.aspis/`. The cleanest
fit is the **VS Code manifest model**: keep `.aspis/AGENTS.md` and
`active_feature.json` as declarative manifests, and add a thin
`contributes:` block per skill/agent that declares what it adds to the
system. Hooks map to the existing `RECENT_CHANGES.md` (every change
already flows through git). No new transport needed — files + git are the
manifest and the audit log.

---

## 3. Tool / skill authoring

### 3.1 Tool authoring — three idioms

| Idiom | Framework | Notes |
|---|---|---|
| **Subclass a base class with a typed input schema** | CrewAI `BaseTool` with `args_schema: Type[BaseModel]` (Pydantic) | Strong typing, error handling, caching, and async support all come for free. |
| **Decorator over a plain function** | CrewAI `@tool("name")` over a function with a docstring | Docstring becomes the model-visible description; the schema is auto-derived. |
| **Register a JSON-schema-described function on a server** | MCP `@mcp.tool()` / `server.registerTool()` over a function with a typed signature and docstring | Same idea, but the tool lives in a separate process and is discoverable over JSON-RPC. |

All three share the contract: **a function with a name, a description, a typed
input schema, and a return value** — and the LLM is the caller. The framing
in MCP's spec is the cleanest: a tool is a "schema-defined interface that
LLMs can invoke" with `tools/list` for discovery and `tools/call` for
execution.

### 3.2 Skill authoring — filesystem-based, progressive disclosure

The "Skill" pattern (Anthropic Agent Skills, CrewAI Skills — same file format)
is distinct from the "Tool" pattern:

- **Tools** are *callable functions*. The model calls them.
- **Skills** are *instructions* (markdown). The model reads them, internalizes
  the guidance, and acts accordingly.

A skill is a directory:

```
pdf-skill/
├── SKILL.md                 # required: YAML frontmatter + body
├── FORMS.md                 # optional: loaded only if SKILL.md links to it
├── REFERENCE.md             # optional: API reference
└── scripts/
    ├── analyze_form.py      # optional: executed by the agent, not loaded
    └── fill_form.py
```

The YAML frontmatter requires `name` and `description`:

```yaml
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and
  merges documents. Use when working with PDF files or when the user
  mentions PDFs, forms, or document extraction.
---
```

`name`: ≤64 chars, lowercase + digits + hyphens, no `anthropic`/`claude` in
the name. `description`: ≤1024 chars, **third person**, must include both
*what* it does and *when* to use it.

**Progressive disclosure** is the load model:

| Level | When loaded | Token cost | Content |
|---|---|---|---|
| 1 — metadata | always (startup) | ~100 tokens | `name` + `description` |
| 2 — body | when triggered | < 5k tokens | SKILL.md body |
| 3 — resources | as needed | effectively unlimited | bundled files, executed scripts |

Scripts are *executed*, not loaded — their code never enters the context;
only the output does. This is what makes Skills a real alternative to
monolithic prompts.

### 3.3 CrewAI tool conventions worth stealing

- **Async variants are first-class.** A tool can be `async def _run(...)` and
  the framework auto-handles it; no separate `async_tool` registration.
- **`cache_function(args, result) -> bool`** lets the tool author decide
  *per-call* what to cache, rather than relying on framework defaults.
- **Tool name is the LLM's primary key** — `verb_noun` style, with a clear
  description; naming conventions are *load-bearing for tool selection*.

### 3.4 Implication for ASPIS

ASPIS already has a skills concept (`.opencode/skills/*/SKILL.md`). The
Anthropic/CrewAI progressive-disclosure model is the right shape to keep
using. The gap to close: ASPIS skills should be *discoverable from the
agent loop* — a `tools/list`-style entry point that returns each skill's
`name` and `description` so the LLM can pick the right skill before paying
the load cost. The `.opencode/skills/` directory plus the `skill` tool in
the skill is the right primitive to grow.

---

## 4. Template systems for consistent output

### 4.1 Templates live at three layers

| Layer | What | Example |
|---|---|---|
| **Prompt template** | Pre-built instruction template the user invokes explicitly. | MCP `prompts/get` returns a `messages[]` array with parameters filled in. Anthropic pre-built Agent Skills ship as templates (PowerPoint, Excel, Word, PDF). |
| **Skill body** | Markdown the agent reads to learn *how* to do a category of work. | A `code-review` skill with a "Severity Levels" section. |
| **Output template** | Strict or flexible structure the agent must follow in its reply. | Skills best-practices guide: "ALWAYS use this exact template structure…" with a strict-mode example. |

### 4.2 The CrewAI/CrewAI-skills insight

CrewAI now ships **five** distinct capability types per agent: Tools (actions),
MCPs (remote tool servers), Apps (platform integrations), Skills (domain
expertise as instructions), Knowledge (RAG-retrieved facts). Skills ≠ Tools ≠
Knowledge; a careful design picks one based on whether the agent needs a
*process*, a *capability*, or a *fact*:

> "If the agent needs to follow a *process*, use a skill. If the agent needs
> to reference *data*, use knowledge." — CrewAI docs

### 4.3 Template scoping

- **Agent-level** vs **crew-level** skills: an agent's skill overrides the
  crew's same-named skill. Names are unique per scope.
- **MCP prompts** are user-controlled (the user picks one from a list); they
  are *not* auto-triggered.
- **Claude Skills** are model-controlled via description matching — the model
  reads the description and decides whether to load the body.

### 4.4 Implication for ASPIS

The existing ASPIS templates (SPEC.md, PLAN.md, TASKS.md, ACCEPTANCE.md) are
output templates for *human* readers. The Skill pattern is a *prompt*
template for the LLM. The two should share a discipline: frontmatter (or
header) that declares *what kind of document this is* and *when it applies*,
so the agent loop can pick the right template by description alone. This is
the same shape as a Skill — adopt it for ASPIS's own templates.

---

## 5. Workflow engines — durable, replayable, auditable

### 5.1 The four reference patterns

| System | Workflow definition | Durability | Determinism | Best fit |
|---|---|---|---|---|
| **Temporal** | Code-as-workflow (Go/Java/TS/Python); activities are the I/O | Event history replay; crash-safe | Workflow code must be deterministic (no `Date.now()`, no random); activities absorb all side effects | Long-running, multi-step agentic processes that must survive crashes |
| **Prefect** | Python decorators (`@flow`, `@task`); native control flow (if/else, while) | State tracking + resume-from-last-success | Dynamic — work can be created at runtime based on data | Data pipelines with branching |
| **GitHub Actions** | YAML (`on:`, `jobs:`, `steps:`, `uses:`, `run:`) | Runs on ephemeral VMs; state lives in artifacts | Not deterministic per se; each run is a new VM | Event-driven automation on a repo |
| **Airflow** | DAG (Python or YAML); explicit task graph | State in metadata DB; retries/resume | DAG-level only — task code can be anything | Scheduled batch jobs |

For an **agent system** the salient comparison is Temporal vs. Prefect,
because they both support long-running, branching, dynamic workflows.

### 5.2 The Temporal "deterministic replay" trick

A Temporal workflow does not snapshot its state. It *re-runs the code* from
the beginning against a recorded event history — `Started Timer for 5
minutes`, `Scheduled Activity X`, `Activity X completed with result Y`,
`Received Signal Z`. Replay uses the same decisions, so the workflow must
be deterministic. Activities (the I/O) run once and their results are
recorded; replays reuse the recorded result.

For an LLM agent: the **model call is an activity**, not a workflow step.
The workflow can crash, restart, replay, and still arrive at the same
state. Activities are where the budget burns (LLM tokens, API calls).

### 5.3 GitHub Actions as a *meta-pattern*

GitHub Actions is interesting not for its durability (ephemeral VMs) but
for its **composability grammar**: `on: push` (trigger) → `jobs:` (parallel
or sequential) → `steps:` → `uses: owner/action@v1` (reuse). Reusable
workflows (`workflow_call`) let one workflow call another — same idea as
a library. This is the right shape for ASPIS's "agent system manages
itself" story: each agent role is a *reusable workflow*, the brain is the
*orchestrator*, and the lifecycle hook is the *trigger*.

### 5.4 Implication for ASPIS

ASPIS's `CORE_LOOP.md` is a workflow definition (plan → build → review) but
lives in markdown. The natural step is to express the same loop as a
declarative manifest (YAML) of phases + agents + transitions, with the
current state (`.aspis/current/active_feature.json`) as the workflow state.
This is a *Prefect*-shaped move (native Python + dynamic), not a
*Temporal*-shaped one — ASPIS's loops are short and human-gated, not
crash-recovering. But the *language* of `trigger → phase → step → tool`
should be lifted from GitHub Actions; it is the most readable grammar for
a non-engineer user.

---

## 6. Configuration management — make config easy to change

### 6.1 Three configurations, three audiences

| Audience | Format | Where it lives | Why |
|---|---|---|---|
| **End user** (toggles, options) | JSON (Claude Desktop `claude_desktop_config.json`, VS Code `settings.json`), YAML (GitHub Actions workflows), or GUI | App config dir (`~/Library/Application Support/Claude/`, `.vscode/settings.json`) | Should be discoverable, hand-editable, and survive app updates |
| **Extension author** | JSON manifest (`package.json` `contributes.configuration` + `configurationDefaults` + a JS registration) | Inside the extension's manifest, exposed under VS Code's Settings UI | Should be discoverable via the host's settings UX |
| **Server author** | JSON-RPC `initialize` capabilities + a `*/list` discovery | In the server's source, with the host caching it | Should be versioned and stable across server releases |

### 6.2 The VS Code pattern in detail

VS Code treats configuration as a first-class extension surface:

- Declare in `package.json`:
  ```json
  "contributes": {
    "configuration": {
      "title": "My Extension",
      "properties": {
        "myExt.enable": {
          "type": "boolean",
          "default": true,
          "description": "Enable the feature"
        }
      }
    }
  }
  ```
- Read in code with `vscode.workspace.getConfiguration('myExt').get('enable')`.
- VS Code surfaces it under Settings UI, validates against the JSON schema,
  and supports per-workspace overrides.

The discipline: **schema-declared, scope-aware, with sensible defaults**.

### 6.3 The MCP server config pattern

MCP clients (e.g. Claude Desktop) read `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "/path/to/weather", "run", "weather.py"]
    }
  }
}
```

The client launches the server as a subprocess (stdio transport) or
connects over HTTP. STDIO requires special care: **never write to stdout**
inside the server — it corrupts the JSON-RPC stream. Use stderr or a
logging library.

### 6.4 Implication for ASPIS

ASPIS already has two config layers: `AGENTS.md` (governance, durably
versioned) and `.aspis/current/active_feature.json` (live state). Add a
third: a *user-tunable* layer under `.aspis/config/` (or similar) with
JSON-schema-declared settings — `default_mode`, `preferred_tests`, etc.
The schema lives in the same file as the settings, so the system can
validate its own config at boot. VS Code's pattern is the cleanest model.

---

## 7. Plugin / extension systems

### 7.1 The two reference architectures

| System | Plugin shape | Discovery | Loading | Safety |
|---|---|---|---|---|
| **MCP (Model Context Protocol)** | A server process (local stdio or remote HTTP) exposing `tools`, `resources`, `prompts` | `initialize` (capability negotiation) + `tools/list` / `resources/list` / `prompts/list` | Host launches subprocess or opens HTTP connection; capability-based auth (OAuth for HTTP) | User consent before any tool call; tool descriptions untrusted; JSON-RPC schema validation |
| **VS Code extension** | A directory with `package.json` manifest + `out/extension.js` entrypoint | `package.json` `contributes` block + `activationEvents` | Extension Host process; `when` clauses for context-sensitive loading | DOM access denied; uninstall hook; tool confirmation dialogs; "untrustedWorkspaces" capability |

### 7.2 The 2025 winner: MCP

MCP is the dominant new contract. Claude, ChatGPT, VS Code, Cursor, MCPJam,
Spring AI, and the major IDEs all ship MCP clients; the official reference
servers cover filesystem, GitHub, Slack, Sentry, Postgres, etc. The
`2025-06-18` spec version is the current stable; the spec is versioned
in the `initialize` handshake so clients and servers can negotiate a
mutually compatible version.

**When to use MCP for a new capability:**
- The capability is reusable across multiple AI clients.
- The capability needs user-facing controls (tool list, prompt templates,
  resource subscriptions).
- The capability needs to be updated at runtime (the
  `notifications/tools/list_changed` mechanism).
- The capability needs authentication against external services (OAuth).

**When to use a VS Code-style extension instead:**
- The capability needs deep integration with the *host's* API (debugger
  protocol, workbench tree views, file watchers).
- The capability is single-host and you don't need cross-tool reuse.

### 7.3 Extension Packs (VS Code)

VS Code's `extensionPack` is a *meta*-extension that bundles other
extensions: `"extensionPack": ["xdebug.php-debug", "zobo.php-intellisense"]`.
When the user installs the pack, all bundled extensions install with it.
The pack declares `categories: ["Extension Packs"]`. This is the right
shape for "ship a coherent set of agents/skills together" — the
*profile* concept from question 8 maps cleanly to an extension pack.

### 7.4 Implication for ASPIS

The two viable directions are:
- **MCP-shaped** — wrap each ASPIS skill as a *local* MCP server. Pros:
  reuse the existing MCP ecosystem and tooling; interop with Claude/Cursor.
  Cons: most of MCP's value (cross-client reuse) doesn't apply if the
  consumer is just ASPIS itself.
- **VS Code extension pack-shaped** — bundle agents + skills into a pack
  the user installs once. Pros: clean install/upgrade story; users
  recognize the pattern from VS Code. Cons: requires a packaging step.

For ASPIS-as-self-contained-system, the simplest move is the *files +
manifest* pattern from §6 — `.aspis/agents/<name>/` with an `AGENT.md`
manifest declaring what the agent contributes. Adopt MCP only if ASPIS
ever needs to be driven by an external client (Claude/Cursor).

---

## 8. Specialized profiles — domain-specific agents

### 8.1 How each system composes "a specialized agent"

| System | Composition | Profile = ... |
|---|---|---|
| **CrewAI** | `Agent(role, goal, backstory, tools=[...], skills=[...], mcps=[...], apps=[...], knowledge=[...])` | A tuple of: a role string, a domain skill directory, and a tool/MCP/app set. |
| **AutoGen** | `RoutedAgent` subclass + `@message_handler` methods; `register(runtime, "type", factory)` | A registered agent type with a unique string ID and a factory. The runtime creates instances on demand. |
| **Claude Skills + Profiles** | Skill with `allowed-tools: web-search file-read` (experimental) + a curated tools list | A skill that pins a pre-approved tool set, scoped to the skill. |
| **VS Code chat participants** | `contributes.chatParticipants` registers a participant with id, name, fullName, description, commands | A scoped chat agent inside VS Code's chat UI, with its own slash commands. |
| **Anthropic Agent Skills (pre-built)** | PowerPoint/Excel/Word/PDF skills | A bundle of skill + tool + code-execution-tool invocation that turns Claude into a domain specialist. |

### 8.2 The "Skills ≠ Tools ≠ Knowledge" rule (CrewAI)

> "Skills inject *instructions and context* into the agent's prompt. They
> tell the agent *how to think* about a problem. Tools give the agent
> *callable functions* to take action."

A "python profile" would be: `skills=["./skills/python-style"]`
(style/checklist) + `tools=[CodeInterpreterTool(), FileReadTool()]`
(actions) + `knowledge=[python_docs]`. A "data science profile" would
swap skills to data-analysis methodology and tools to pandas/exec.

### 8.3 AutoGen's profile-as-runtime

AutoGen's most interesting pattern for "specialized profiles" is the
**runtime as profile registry**. The runtime is a generic container; the
specialization is the `AgentType` string and its factory. A "python" profile
is a different set of registered types; an "ops" profile is a different
set. Switching profiles = registering a different set of types into the
same runtime. The runtime itself is unopinionated.

### 8.4 Implication for ASPIS

ASPIS already has agent *roles* (system-rules, current-state). The
profile concept adds: "what is bundled in by default for a *kind* of
project?". A "python project" profile would pre-load:

- skills: `code-review`, `pytest-patterns`, `python-style`
- tools: `pytest`, `ruff`, `mypy`
- templates: `SPEC.md`, `PLAN.md` with python-specific sections

This is the same shape as the existing `.opencode/skills/` system + a
*selection* layer. A `select_profile` tool that takes a domain name and
returns the bundle (skill paths + tool names + template overrides) is the
right primitive. Profiles are *data* (a YAML/JSON file), not code.

---

## Provenance & version

- **MCP spec version:** 2025-06-18 — current stable, per
  `https://modelcontextprotocol.io/specification/2025-06-18`
- **Anthropic Agent Skills:** docs current 2026-06; API uses beta headers
  `code-execution-2025-08-25`, `skills-2025-10-02`, `files-api-2025-04-14`
- **VS Code Extension API:** docs current; VS Code 1.x; "Yeoman" + `yo code`
  scaffolder; `languageModelTools` contribution point
- **GitHub Actions:** docs current; `workflow_call` reusable workflows
- **Temporal:** docs current; "replay-safe" versions of time/random
- **Prefect 3.0:** "90% runtime improvement" claim; native Python control
  flow (no DAG constraint); events & automations open-sourced
- **CrewAI:** current docs; five agent capability types (tools, MCPs,
  apps, skills, knowledge)
- **AutoGen 0.4+:** Core API + `SingleThreadedAgentRuntime`; Docker-based
  code execution; `DefaultInterventionHandler` for approval
- **Claude Code skills:** docs current; filesystem-based skills in
  `~/.claude/skills/` or `.claude/skills/`

All sources were fetched 2026-06-25 from primary documentation. Where
secondary sources are referenced (Devin), the URL could not be retrieved;
no claims about Devin's internal architecture are made in this document.

---

## Where to read more (pointers, not copies)

- MCP architecture: `https://modelcontextprotocol.io/docs/learn/architecture`
- MCP server concepts: `https://modelcontextprotocol.io/docs/learn/server-concepts`
- Anthropic Agent Skills overview: `https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview`
- Anthropic Skills best practices: `https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices`
- Anthropic tool use: `https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview`
- CrewAI Tools: `https://docs.crewai.com/en/concepts/tools`
- CrewAI Skills: `https://docs.crewai.com/en/concepts/skills`
- VS Code Language Model Tool API: `https://code.visualstudio.com/api/extension-guides/ai/tools`
- VS Code Extension Manifest: `https://code.visualstudio.com/api/references/extension-manifest`
- VS Code Extension Capabilities: `https://code.visualstudio.com/api/extension-capabilities/overview`
- AutoGen code execution: `https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/design-patterns/code-execution-groupchat.html`
- AutoGen intervention handlers: `https://microsoft.github.io/autogen/dev/user-guide/core-user-guide/cookbook/tool-use-with-intervention.html`
- Temporal Workflows: `https://docs.temporal.io/workflows`
- Prefect: `https://docs.prefect.io/v3/concepts/workflows`
- GitHub Actions: `https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions`
- MCP build a server: `https://modelcontextprotocol.io/docs/develop/build-server`
