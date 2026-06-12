# Enamel — style pack

Hard-enamel pin: flat glossy color cells separated by one continuous raised
metal line, floating on plain paper. A look for **character packs** (the
pack's `Style:` line) suited to milestones and achievements, badges and
security, launches, merch-adjacent pieces — anywhere "collectible" is the
right voice.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: draw EVERYTHING — mascot, objects, arrows — as ENAMEL PIN cells: every shape bounded by one continuous raised METAL outline of even width, each cell filled with exactly one flat glossy enamel color; no open or unbounded strokes anywhere.

STYLE: HARD-ENAMEL PIN — the scene rendered like an oversized die-struck enamel lapel pin lying flat on plain paper: flat color cells, raised polished metal lines, one subtle uniform sheen across the enamel, a hint of edge thickness; no pin-back hardware, no backing card, no photorealistic depth.
```

## Palette mapping

- **Ground** ← the palette paper (bare and matte — the artwork floats on it).
- **Metal** ← the structure ink reinterpreted as the pin's metal: near-black
  structure → black-nickel `#2c2c30`; warm structure → antique gold
  `#b8923f`.
- **Enamel cells** ← large flat fills; the character's body cell follows its
  value rule using a deep enamel of the structure hue or a pale enamel of the
  paper hue.
- **Accent enamel** ← the palette accent — the single brightest cell.

Classic default (no palette given): ground `#f2ead8`, metal antique gold
`#b8923f`, body enamel `#2e2b33`, accent enamel `#e0356f`.

PALETTE line: `bare paper ground {paper hex}. All outlines are raised
polished metal {metal hex}, one even width. Flat enamel fills only; accent
enamel {accent hex} used sparingly — the character's accent part + 1–2
cells.`

## Character treatment

The mascot is built from a few large enamel cells — countable on one hand.
Dark-capable characters → deep enamel body with pale enamel eyes;
light-bodied characters → pale enamel body with deep enamel eyes. Either way
every cell, eyes included, is bounded by the metal line; the accent part is
the accent enamel cell.

## Labels

Short capitals rendered as the metal itself — stamped-metal lettering in the
metal color directly on the paper ground, ≤2 labels.

## Staging fit (read before choosing the shot)

Enamel discretizes: continuous structure — a winding path, a flowing curve, a
long connector — breaks into separate chunky cells (a path becomes floating
stepping-stones). That is the look working, not failing, so stage for it:
emblematic single-moment scenes and discrete-station diagrams (steps, gates,
before/after) render beautifully; continuous-flow metaphors (graphs with
edges, tangled-vs-straight, one unbroken journey line) belong in a different
look. Keep busy shots to roughly a dozen cells beyond the character or the
scene drifts toward a board-game product shot.

## QA deltas (replace the riso grain checks)

- Every shape is a closed metal-bounded cell — an open stroke or un-outlined
  fill = re-roll.
- **Force the accent contrast in the prompt** ("vivid magenta-pink #e0356f —
  must NOT be the body color"): stated plainly, the model drops the accent
  cell into the body enamel. Accent-less render = re-roll.
- One metal color only; sheen subtle and uniform — no rainbow speculars, no
  3D bevel drama.
- **No pin-back, no butterfly clutch, no backing card, no hand holding it** —
  the product-shot cliché.
- Cells few and large; accent enamel only on the accent part + 1–2 cells.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/enamel-deflect.png — study it
for line/texture and restraint; never copy its composition.

Variant note: when deriving an enamel pack from a riso character, the
original sheet works directly as the `--ref` — the style prompt overrides its
rendering.
