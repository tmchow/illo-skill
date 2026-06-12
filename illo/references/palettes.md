# Palettes

The risograph technique is the constant identity; the palette is a swappable
parameter. Every palette obeys the same color grammar from `visual-style.md`:
**structure ink** (darker) + **accent ink** (brighter) on **paper**, with an
optional secondary accent. Whatever the path, finish with concrete hex
values to put in the prompt.

## Default resolution (first match wins)

1. **Explicit request** — "use ink-punch", a custom palette by name, "make it emerald", a brand hex.
2. **Destination cue** — a blog / Substack / personal-site context, or a pasted
   article from one → the user's custom palette tagged for that destination
   (below), if any.
3. **Config default** — `defaultPalette` from the user config, if set.
4. **House default** — `ink-punch`.

## Named presets

| preset | paper | structure ink | accent(s) | mascot body | notes |
|---|---|---|---|---|---|
| **`ink-punch`** (house default) | warm white `#fffef7` | near-black `#111111` | fluoro pink `#ff3d9a` | dark OK | boldest, most distinctive |
| `classic` | cream `#fbf7ee` | blue `#2b6cff` | pink `#ff3d9a` (purple where inks overprint) | dark OK | loud, "very online" |
| `signal` | cream `#fbf7ee` | navy `#1b2a6b` | fluoro orange `#ff6a1a` | dark OK | complementary, confident/pro |
| `full-grammar` | cream `#fbf7ee` | near-black `#111111` | red `#e5342b` + blue `#2b6cff` | dark OK | richest semantic range; keep restrained |
| `mono-heat` | cream `#fbf7ee` | charcoal `#363737` | single orange `#ff6a1a` | light | minimal; one ink |

Mascot body value follows the palette — see `character.md` (light palettes →
light body + structure-ink features).

## Custom palettes (site- and brand-matched)

Users keep their own palettes in
`${XDG_CONFIG_HOME:-~/.config}/illo/palettes.md` (the `doctor` subcommand
reports whether the file exists). Same table schema as the presets, plus an
optional "Destination cues:" line mapping cues (blog, x, deck, …) to palette
names. When the file exists, its names join the preset namespace and its
destination cues drive resolution step 2.

The highest-value custom palette is a **site-matched** one: eyedrop or read
the site's live theme tokens (background → paper, text → structure ink, link/
brand color → accent), record them as a named palette, and new art sits next
to existing content without a hard visual break. If the site rebrands,
re-extract the tokens; nothing else changes.

## Semantic ink roles (explainer register only)

Explainer images (`composition.md`, "The explainer register") give each ink
a job on top of the same color grammar. Resolve the palette normally first,
then map — semantic roles spend the inks the palette already has; they never
add new ones:

- **Structure** — stations, the mascot, station names: the structure ink.
- **Flow** — the main direction's arrows + the one flow note: the accent ink.
- **Warning** — at most ONE trap/failure note: the secondary accent when the
  palette has one; otherwise reuse the accent **and** drop the flow arrows
  to structure ink — one ink never carries two jobs in the same image.
- **Aside** — any remaining secondary note: structure ink.

A style file may remap these in its palette mapping (e.g. blueprint draws
flow in its accent on the deep ground); the restraint rules are unchanged.

## Derive a palette from one dominant color

When the user gives an arbitrary dominant color **C** (a brand color, "make it
emerald", a hex), derive the rest by rule instead of picking a preset.

### Steps

1. **Assign C's role** by its lightness/saturation (user may override):
   - bright & saturated → C is the **accent** (or the lead fill).
   - dark/deep → C is the **structure ink**.
   - very light → C is the **paper**.
2. **Structure ink** (if not C): take C's hue, drop lightness to ~18–22% and
   desaturate toward neutral — a *tinted black* that harmonizes (warm C → warm
   charcoal, cool C → cool charcoal). Never flat `#000`.
3. **Paper** (if not C): near-white, L ≈ 96–98%, faintly tinted toward C's
   temperature (warm → cream like `#fffbeb`; cool → cool off-white).
4. **Secondary accent** (only if range is wanted): **complement** (hue +180°)
   for punch, or **analogous** (hue ±30°) for a calmer tonal look. Default mode:
   **complement.** Use it sparingly.

### Guardrails (so derived ≠ ugly)

- Max **2 inks + paper** by default; 3 inks only when full-grammar range is asked for.
- **Temperature coherence** — paper, structure, and accent share a warm/cool lean.
- **Contrast floor** — structure-on-paper must stay legible (target ≥ ~7:1).
- Accent never becomes label-text background if its contrast is low (labels are
  structure-ink on bare paper — see `quality-bar.md`).
- The two inks must be clearly distinct in hue and value.
- Light paper → light mascot body + structure-ink features (`character.md`).

### Worked examples (complement mode)

- **Dominant emerald `#1e9e6a`** → paper `#f7faf5`, structure `#18241c`
  (green-black), lead fills `#1e9e6a`, complementary accent warm coral `#e0553b`.
- **Dominant royal purple `#6b3fa0`** → paper `#faf8fd`, structure `#211a2e`
  (violet-black), lead fills `#6b3fa0`, complementary accent gold `#d9a521`.

### Caveat

The model approximates hexes (close, not pixel-exact). The QA step eyedrops the
output vs the target and re-rolls if off; for flat riso fills, snapping
colors to exact hex in post also works.
