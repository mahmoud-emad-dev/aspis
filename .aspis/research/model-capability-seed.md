# Reference — Model capability/cost SEED (F-010)

**Status: SEED — low trust. Initial estimates only; refine later.** Distilled from a ChatGPT pass
(raw kept in `model-scores.chatgpt-raw.txt`). **Captured 2026-06-21.**

How this gets corrected:
- **Objective facts** (context window, pricing) → pulled at build time from `opencode models --verbose`
  / models.dev (authoritative). The numbers below are placeholders where they disagreed with that source.
- **Capability scores** (the subjective 1–10) → seeds only; **replaced by real usage tracing** (Phase 4/5).
  Treat all `confidence: low` rows as guesses calibrated off model family, not measured.
- Scale anchor: 10 = current frontier best (Claude Opus / GPT-5-class). Dimensions: planning,
  implementation, review, reasoning.

> Reconciliation notes: the raw had 3 overlapping passes that disagreed on context windows and a few
> cost tiers. Below picks one value per model; conflicts are flagged inline. Naming normalized
> (e.g. `qwen3.7-max`).

```yaml
# capability scores + cost tier (SEED — confidence per row)
claude-opus-4-8:   {planning: 10, implementation: 10, review: 10, reasoning: 10, cost_tier: frontier, in: 5.00,  out: 25.00, confidence: medium}
claude-sonnet-4-6: {planning: 9,  implementation: 9,  review: 9,  reasoning: 9,  cost_tier: deep,     in: 3.00,  out: 15.00, confidence: medium}
claude-haiku-4-5:  {planning: 8,  implementation: 9,  review: 8,  reasoning: 8,  cost_tier: standard, in: 1.00,  out: 5.00,  confidence: medium}
gpt-5.5:           {planning: 10, implementation: 10, review: 10, reasoning: 10, cost_tier: frontier, in: 5.00,  out: 30.00, confidence: low}
gpt-5.2:           {planning: 10, implementation: 10, review: 10, reasoning: 10, cost_tier: deep,     in: 1.75,  out: 14.00, confidence: medium}
gpt-5.2-codex:     {planning: 10, implementation: 10, review: 10, reasoning: 9,  cost_tier: deep,     in: 1.75,  out: 14.00, confidence: medium}
gpt-5.3-codex:     {planning: 9,  implementation: 10, review: 10, reasoning: 9,  cost_tier: deep,     in: 1.75,  out: 14.00, confidence: low}   # not in ask; CC added
gpt-5.4-mini:      {planning: 8,  implementation: 8,  review: 7,  reasoning: 8,  cost_tier: standard, in: 0.75,  out: 4.50,  confidence: medium}
gpt-5-nano:        {planning: 6,  implementation: 6,  review: 5,  reasoning: 6,  cost_tier: cheap,    in: 0.05,  out: 0.40,  confidence: low}
gemini-3.1-pro:    {planning: 10, implementation: 10, review: 10, reasoning: 10, cost_tier: deep,     in: 2.00,  out: 12.00, confidence: high}
gemini-3.5-flash:  {planning: 9,  implementation: 9,  review: 8,  reasoning: 9,  cost_tier: deep,     in: 1.50,  out: 9.00,  confidence: medium}
gemini-3-flash:    {planning: 8,  implementation: 8,  review: 7,  reasoning: 8,  cost_tier: standard, in: 0.50,  out: 3.00,  confidence: medium}
minimax-m3:        {planning: 9,  implementation: 9,  review: 8,  reasoning: 8,  cost_tier: cheap,    in: 0.30,  out: 1.20,  confidence: low}
minimax-m2.7:      {planning: 6,  implementation: 6,  review: 5,  reasoning: 6,  cost_tier: cheap,    in: 0.25,  out: 1.00,  confidence: low}
deepseek-v4-pro:   {planning: 9,  implementation: 9,  review: 9,  reasoning: 9,  cost_tier: standard, in: 0.44,  out: 0.87,  confidence: low}   # CONFLICT: cheap pricing, deep capability
deepseek-v4-flash: {planning: 8,  implementation: 8,  review: 7,  reasoning: 8,  cost_tier: cheap,    in: 0.09,  out: 0.18,  confidence: low}
glm-5.2:           {planning: 8,  implementation: 8,  review: 7,  reasoning: 8,  cost_tier: standard, in: 1.40,  out: 4.40,  confidence: low}   # CONFLICT: standard vs deep
glm-5.1:           {planning: 6,  implementation: 6,  review: 5,  reasoning: 6,  cost_tier: standard, in: 1.40,  out: 4.40,  confidence: low}
glm-4.7-flash:     {planning: 4,  implementation: 5,  review: 4,  reasoning: 4,  cost_tier: cheap,    in: 0.07,  out: 0.40,  confidence: low}
qwen3.7-max:       {planning: 9,  implementation: 9,  review: 8,  reasoning: 8,  cost_tier: deep,     in: 1.25,  out: 3.75,  confidence: low}
qwen3.6-plus:      {planning: 8,  implementation: 8,  review: 7,  reasoning: 8,  cost_tier: standard, in: 0.33,  out: 1.95,  confidence: medium}
qwen3-coder-plus:  {planning: 8,  implementation: 9,  review: 7,  reasoning: 7,  cost_tier: standard, in: 0.65,  out: 3.25,  confidence: medium}
qwen3-coder-flash: {planning: 6,  implementation: 8,  review: 6,  reasoning: 6,  cost_tier: cheap,    in: 0.50,  out: 2.50,  confidence: low}
kimi-k2.7-code:    {planning: 8,  implementation: 9,  review: 8,  reasoning: 8,  cost_tier: standard, in: 0.95,  out: 4.00,  confidence: low}
kimi-k2.6:         {planning: 6,  implementation: 6,  review: 6,  reasoning: 6,  cost_tier: standard, in: 0.95,  out: 4.00,  confidence: low}
mimo-v2.5:         {planning: 9,  implementation: 9,  review: 8,  reasoning: 9,  cost_tier: cheap,    in: 0.14,  out: 0.28,  confidence: medium}
grok-build-0.1:    {planning: 7,  implementation: 8,  review: 7,  reasoning: 6,  cost_tier: standard, in: 1.00,  out: 2.00,  confidence: low}
```

```yaml
# free-to-test (for the $0 default so a new user can run end-to-end)
free_recommended:
  cheap:   opencode/north-mini-code-free
  standard: openrouter/qwen/qwen3-coder:free
  deep:    openrouter/openai/gpt-oss-120b:free
  overall_default: openrouter/qwen/qwen3-coder:free
free_caveat: "All 'free' endpoints are rate/quota-limited and terms unverified; treat as try-it defaults."
```

**Do NOT trust the exact numbers.** They exist so F-010 ships with a populated catalog from day one;
every value is overwritten by detection (objective facts) or tracing (scores) later.
