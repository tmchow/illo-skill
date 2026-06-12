# Chalk — style pack

White chalk on a deep slate board: dusty, confident hand-drawn strokes with a
ghost smudge or two. A look for **character packs** (the pack's `Style:`
line) suited to teaching and explainers, plans and schedules, countdowns,
retros — anywhere "let me walk you through it at the board" is the right
voice.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: draw EVERYTHING — mascot, objects, arrows — as confident HAND-CHALKED strokes: bold, dry-edged lines with visible chalk texture, drawn with a sure teacher's hand — never wispy, scratchy, or sketchy.

STYLE: CHALKBOARD — chalk drawing on a deep matte slate ground that fills the frame edge to edge, faint chalk dust and one or two ghost smudges of erased marks, completely flat, no gradients, no photorealism, no wooden frame, no classroom.
```

## Palette mapping

Chalk inverts the riso grammar: dark ground, light line.

- **Slate** ← the structure ink's hue, deepened to board depth (L ≈ 14–18%).
  Neutral/black structure → deep green-gray slate `#26302c`.
- **Chalk** ← the paper color, lifted to chalk white (e.g. `#f2efe4`).
- **Accent** ← the palette accent as a stick of colored chalk — lifted and
  dusted until it reads clearly on the dark board (a dark accent rotates
  toward a warm pastel).

Classic default (no palette given): slate `#26302c`, chalk `#f2efe4`, accent
chalk orange `#f5a24b`.

PALETTE line: `matte slate board {ground hex}, edge to edge. All chalk lines
{chalk hex}. Accent chalk {accent hex} used sparingly — the character's
accent part + 1–2 elements.`

## Character treatment

Every character renders as a chalk drawing — no fills, dark-body rules
collapse to line-on-board. Eyes are solid chalk dots; the accent part is
shaded in with the side of the accent chalk. State in the CHARACTER block:
"drawn in the same confident chalk stroke as everything else, eyes as solid
chalk dots, the {accent part} shaded in accent chalk."

## Labels

Hand-chalked capitals in the chalk color directly on the slate. A single
hand-drawn underline is allowed; never boxed.

## QA deltas (replace the riso grain checks)

- The board fills the frame: **no wooden frame, no chalk tray, no classroom
  wall** — the chalkboard cliché. Edit out or re-roll.
- Strokes bold and dry; dust faint; ≤2 ghost smudges.
- One stroke weight everywhere; no wispy sketch lines.
- Accent appears only on the character's accent part + 1–2 elements.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/chalk-timebox.png — study it
for line/texture and restraint; never copy its composition.

Variant note: when deriving a chalk pack from a riso character, the original
sheet works directly as the `--ref` — the style prompt overrides its
rendering.
