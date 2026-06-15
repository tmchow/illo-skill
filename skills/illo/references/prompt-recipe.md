# Prompt recipe

Build one prompt per image and generate each separately (reference-locked, per
SKILL.md). Fill the braces; keep the constants. The CHARACTER block comes from
the active character's **prompt spec** (`references/character.md` for the
default Blot, or the custom pack's `character.md`). End with concrete hex
values from `palettes.md`.

The template below is written for **riso**. When the active character's pack
declares a different style (its `Style:` line — SKILL.md step 4), replace the
LINE LANGUAGE and STYLE lines with the blocks from that style's file, build
the PALETTE line from its palette mapping, and apply its character treatment
to the CHARACTER block's value-rule slot.

## Generation template

```text
A {aspect, e.g. 16:9 horizontal} editorial illustration that explains ONE idea: "{the single idea}".

Composition ({staging from composition.md}): {the scene — where the mascot is, the move it performs, the one or two built objects, how things flow}. Generous negative space (keep ~35%+ of the canvas empty); the subject is large and confident, ~50–70% of the frame.

CHARACTER (locked, keep exactly on the reference model): {the active character's prompt spec, with its value rule resolved for this palette}. The mascot is a solid OPAQUE shape in front of the scene — no ground line, table edge, horizon, or prop passes through its body; background lines stop at its silhouette. Its limbs join the body cleanly at sensible points, exactly the count its design specifies (no extra, floating, or mid-body arms/legs). Only the mascot's own parts touch its outline: any tool is HELD in a hand and clearly separated from the torso, or rests in the scene — never pressed flat against the body or sprouting from it. Hold at most one prop per hand; any extra object sits on the table or ground. Preserve the character sheet's limb proportions: a stubby arm stays stubby and nearby, never stretched into a long bar/cable/lever or across the whole scene; handles, horns, tails, ears, or accent carriers are not extra hands unless the character pack explicitly says so.

LINE LANGUAGE: draw EVERYTHING — mascot, objects, arrows — in ONE bold, even-weight, softly-rounded outline (clean vinyl-sticker line), not thin scratchy sketch lines.

STYLE: risograph print — grainy halftone texture, slight ink-layer offset, faint paper grain, flat fills, no gradients, no soft shadows.

PALETTE: paper {paper hex}. Structure ink {structure hex} for all linework, forms, and label text. Accent {accent hex} used sparingly — the character's accent part + 1–2 elements. {optional secondary accent hex for one secondary note}.

LABELS: exactly {1–3} short hand-lettered English labels — {"label one", "label two"} — in the structure-ink color placed directly on the bare paper. Never put label text on a colored fill. No title bar, no type label, no logo.
```

## Mini-comic variant

When the staging is a mini-comic, replace the Composition line with one that
spells out each panel — the model needs the panel structure stated explicitly:

```text
Composition (mini-comic, {2–4} panels in ONE image, read left to right, separated by clear gutters or thin hand-drawn panel borders): Panel 1 — {the mascot's action}. Panel 2 — {the same mascot and the same key object, one step further}. Panel 3 — {the payoff}. The SAME mascot and the SAME key object appear in every panel, identical design and palette, so it reads as one moment advancing. One action per panel; at most one short label per panel.
```

## Explainer variant

When the shot list declared the **explainer register** (`composition.md`,
"The explainer register"), replace the Composition and LABELS lines with the
two below — CHARACTER, LINE LANGUAGE, STYLE, and PALETTE are unchanged, so
the structure is drawn in the active look. Resolve the semantic ink hexes
(flow, warning) from `palettes.md` first.

Hex values live in the PALETTE line ONLY — extend it with the semantic-role
sentence shown below. Never put a hex inside the Composition or CALLOUTS
lines: a hex adjacent to quoted callout text gets hand-lettered into the art
as if it were a label. Refer to inks by role name ("the flow color"), exactly
as the editorial LABELS line refers to "the structure-ink color". When the
structure has a return/exception leg, state its direction twice — where it
leaves and where it rejoins — or the model may flip the arrowhead.

```text
Composition (explainer — {structure type from composition.md}): a hand-built sketch-diagram of ONE structure: {the 3–5 stations/beats, each an invented physical object — what each is and what happens at it}. One main flow direction, {e.g. left to right}, drawn as simple hand-drawn arrows in the flow color{, plus one return leg: it leaves from {station}, travels {direction}, and rejoins at {station} — the arrowhead points at {station}}. The mascot is a WORKING PART of the structure — {its station/jam/sorter/hauler move} — never a presenter beside it. No title, no border, no grid, no legend, no formal flowchart boxes. The structure spans ~40–70% of the frame; keep ~35%+ of the canvas empty with one calm region.

PALETTE: {the style's PALETTE line as usual, hexes here only}. Semantic roles: the flow arrows and the one flow note use the accent ink; {warning-role sentence per palettes.md when present}; everything else, including all callout text not named above, uses the structure ink.

CALLOUTS: exactly {3–6} short hand-lettered English callouts — {"…", "…"} — each 1–4 words, each appearing EXACTLY ONCE, placed directly on the bare paper near what they name: station names in the structure-ink color, the one main-flow note in the flow color, at most one warning note in the warning color. Hand-letter ONLY these words — no other text, numbers, or color codes anywhere in the image. Never put callout text on a colored fill. No title bar, no type label, no logo.
```

## Notes that keep it on-style

- One idea, one structure. Never combine images.
- Reference conditioning beats the PALETTE line for the character's accent
  part: when the resolved accent differs from the hue on the pack's model
  sheet, say so inside the CHARACTER block — "the {accent part} uses THIS
  palette's accent, even if the reference sheet shows a different hue" —
  or the sheet's color wins. Check it at QA either way.
- Keep labels few and short; long text is where the model misspells.
- Accent discipline: the character's accent part + 1–2 elements; the body is
  never "colored in" with the accent.
- If the user named a dominant color, derive hexes first (`palettes.md`) and put
  the real hexes here.

## Watermark / attribution (optional)

Off by default — **there is no built-in watermark text.** The handle comes only
from the user's `watermark` config map (or an explicit request), so installers
never inherit someone else's site or handle. Resolve in order:

1. explicit text in the request ("watermark it with @foo"),
2. `watermark[<destination>]` from config, by cue — e.g. `blog`, `x`,
3. `watermark.default` from config,
4. otherwise **none** — omit the watermark entirely.

When a handle resolves, append one line (`{handle}` = the resolved text), and
the model hand-letters it in the riso style:

```text
WATERMARK: in the bottom-right corner, hand-letter the tiny signature "{handle}" in the structure-ink color at low opacity — subtle but legible, about 2–3% of the image width. It is a quiet signature, not a label: keep it small and tucked in the corner, never overlapping the subject or labels, with no box or underline.
```

Caveat: the model bakes the watermark into the art, so a blog version and an X
version are two separate renders (the art will differ). For one identical image
with two different handles, generate it once without a watermark and add each
handle in an image editor.

## Edit / fix prompts

Pass the existing image back as a `--ref` to `illo.py generate` (instead of, or
in addition to, the character reference) with one of these instructions as the
prompt:

Remove an unwanted title or stray text:

```text
Edit the provided image. Remove only the text "{text}" and any underline/box around it. Fill the area with the surrounding paper texture and color so it is seamless. Preserve everything else exactly — character, objects, labels, line, palette, grain, and aspect ratio. Add no new text or objects.
```

Recolor to another palette (keep composition):

```text
Edit the provided image. Keep the exact composition, characters, objects, line work, and grain. Recolor it to this palette only: paper {paper hex}, structure ink {structure hex}, accent {accent hex}. Re-apply the character's value rule for this palette: {the rule, e.g. light paper means a light body with structure-ink (not black) features}. Change nothing else.
```

Make the mascot more central to the action:

```text
Regenerate with the same idea and simple layout, but make the mascot clearly PERFORM the move (operating/holding/stuck-in the object), not standing beside it. Keep it clean, sparse, deadpan, and on the reference model.
```
