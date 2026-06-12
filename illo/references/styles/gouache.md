# Gouache — style pack

Mid-century gouache poster: opaque matte paint, flat hand-painted shapes with
soft dry-brush edges and paper breathing between them. A look for **character
packs** (the pack's `Style:` line) suited to essays and culture pieces, food
and lifestyle, anything human and warm — the painterly voice of the library.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: paint EVERYTHING — mascot, objects, arrows — as flat matte GOUACHE shapes with soft, slightly dry hand-painted edges; NO drawn outlines — shapes separate by value and color, with thin slivers of bare paper showing between neighboring shapes.

STYLE: MID-CENTURY GOUACHE POSTER — opaque matte paint on paper, one flat tone per shape, visible dry-brush texture only in the large fills, slightly chalky surface, imperfect confident edges; no gradients, no blended shading, no digital smoothness, no photorealism.
```

## Palette mapping

- **Paper** ← the palette paper, visible in negative space and the slivers
  between shapes.
- **Paint ink** ← the structure ink softened to a paint near-black that keeps
  its temperature (true black is too harsh in gouache).
- **Mid** ← one muted midtone derived from the structure hue at ~65%
  lightness, for secondary shapes only.
- **Accent** ← the palette accent, shifted slightly matte and desaturated.

Classic default (no palette given): paper `#f4ecdc`, paint ink `#33302a`, mid
`#a89a82`, accent tomato `#d95f3b`.

PALETTE line: `bare paper {paper hex} breathing through. Paint ink
{structure hex} for primary shapes and label lettering, mid {mid hex} for
secondary shapes. Accent {accent hex} used sparingly — the character's
accent part + 1–2 elements. One flat tone per shape.`

## Character treatment

The mascot is painted in flat gouache shapes like everything else.
Dark-capable characters → paint-ink body with bare-paper dot eyes;
light-bodied characters → pale body in a tint of the paper with paint-ink
eyes, separated from the ground by value or a thin painted contour where
contrast fails — that contour is the only line allowed in the image. The
accent part is one clean accent shape.

## Labels

Hand-painted brush capitals in the paint-ink color on bare paper — slightly
irregular, confident, never typeset.

## QA deltas (replace the riso grain checks)

- Matte everywhere; one flat tone per shape — **no blended shading, no
  gradients, no gloss.**
- Brush texture lives in large fills only; edges soft but confident — no
  sloppy bleed, no watercolor washes.
- No outline creep: if the image reads as outlined linework, it has drifted
  toward riso — re-roll.
- Accent appears only on the character's accent part + 1–2 elements.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/gouache-steep.png — study it
for line/texture and restraint; never copy its composition.

Variant note: when deriving a gouache pack from a riso character, the
original sheet works directly as the `--ref` — the style prompt overrides its
rendering.
