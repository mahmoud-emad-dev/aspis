# ASPIS — Brand Guidelines

ASPIS is **the shield for agentic software production** — an *Agentic Software
Production & Integration System*. The brand reads the way the software behaves:
deterministic, reliable, engineering-first. Flat, geometric, monochrome-capable.
No gradients, no AI clichés (no brains, robots, or glowing circuits).

---

## The mark

A **shield** with a bold geometric **A** cut into it.

- **Shield** — protection, determinism, a wall the model can't cross. ASPIS guards
  the build with gates, scope, and review.
- **A** — *ASPIS* / *Agentic*. Integrated into the shield, not stamped on top:
  the discipline *is* the system, not a label.
- **Negative space** — the A is a knockout, so the mark works in a single flat color
  and stays legible at 16×16.

The mark is constructed on a 64-unit grid with a symmetric shield and a centered
inverted-V A. It carries one color. It never gets a gradient, a bevel, or a shadow.

---

## Files & when to use each

| File | What it is | Use for |
|---|---|---|
| `logo.svg` | Horizontal lockup (mark + wordmark), `currentColor` | Inline SVG / anywhere the color should inherit |
| `logo-light.svg` | Lockup in **ink** (`#0F172A`) | **Light** backgrounds (GitHub light, docs, slides) |
| `logo-dark.svg` | Lockup in **white** (`#FFFFFF`) | **Dark** backgrounds (dark READMEs, terminals, slides) |
| `icon-only.svg` | The shield mark alone, `currentColor` | App icon, social avatar, square placements |
| `wordmark.svg` | The word **ASPIS** alone | Tight horizontal spaces, footers, nav bars |
| `favicon.svg` | Optimized mark, adapts to light/dark tabs | Browser tab / site favicon |

In GitHub READMEs, pair the two lockups so the logo follows the viewer's theme:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/logo-dark.svg">
  <img alt="ASPIS" src="assets/brand/logo-light.svg" width="220">
</picture>
```

`favicon.svg` adapts on its own via a `prefers-color-scheme` block — ink shield on
light tabs, white shield on dark tabs.

---

## Color

The brand is **monochrome-first**: the logo only ever needs ink *or* white. The
accent exists for UI, links, and diagram highlights — never inside the logo.

| Token | Hex | Role |
|---|---|---|
| **Ink** | `#0F172A` | Primary mark on light backgrounds; body text |
| **Paper** | `#FFFFFF` | Background; the mark on dark backgrounds |
| **ASPIS Indigo** (accent) | `#4F46E5` | Links, active states, diagram highlights |
| **Slate** | `#64748B` | Secondary text, diagram labels, captions |
| **Hairline** | `#E2E8F0` | Borders, dividers, diagram strokes |

Rules: one accent, used sparingly. No gradients anywhere. On a colored background,
use the all-ink or all-white logo — never the accent as the logo fill.

---

## Clear space & minimum size

- **Clear space** — keep padding of at least the width of the shield (the cap height
  of the wordmark) on all sides. Nothing crowds the mark.
- **Minimum size** — icon/favicon down to **16 px**; the full lockup not below
  **120 px** wide (below that, use `icon-only.svg`).

---

## Typography

Geometric, neutral sans. The wordmark is set in a system geometric stack so it
renders everywhere; outline it to paths for print or fixed-pixel assets.

- **Stack:** `Inter, "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif`
- **Wordmark:** weight **800**, letter-spacing ~`0.08em`, all caps.
- **Headings:** 600–700. **Body:** 400. **Code/CLI:** any monospace
  (`ui-monospace, "JetBrains Mono", "SFMono-Regular", Menlo, Consolas, monospace`).

---

## Misuse — don't

- ❌ Add a gradient, glow, bevel, or drop shadow.
- ❌ Recolor the logo into the accent or any non-brand color.
- ❌ Stretch, skew, rotate, or outline-stroke the mark.
- ❌ Place the ink logo on a dark background (use `logo-dark.svg`) or vice-versa.
- ❌ Reconstruct the wordmark in a different typeface, or crowd the clear space.
- ❌ Add a brain / robot / circuit motif. ASPIS is an *engineering* brand.

---

## Source

All assets are flat, hand-authored SVG in `assets/brand/`. Edit the SVG directly;
there is no binary master. The shield path and A geometry are shared verbatim across
every file, so the mark stays identical at all sizes.
