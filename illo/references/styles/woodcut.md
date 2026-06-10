# Woodcut — style pack

Hand-carved relief print: heavy black ink on warm cream with one accent ink
slightly off-register. The most print-heritage voice — use for opinionated
essays, manifestos, "old truth" pieces, anything that wants weight.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: thick, confident CARVED strokes — bold black shapes and outlines with slightly rough, chipped ink edges; texture comes from visible carve marks and coarse parallel gouge lines in the large fills, never from halftone dots.

STYLE: WOODCUT / linocut relief print — hand-carved look, heavy ink on warm cream paper, slightly uneven ink coverage, one accent ink printed slightly off-register, completely flat, no gradients, no digital smoothness.
```

## Palette mapping

- **Paper** ← the palette paper, warmed toward cream (e.g. `#f6efe0`).
- **Carving ink** ← the structure ink, deepened to near-black while keeping
  its temperature (warm structure → warm black `#161311`).
- **Accent ink** ← the palette accent, printed off-register. Vermilion
  `#d8401f` is the classic default.

No midtones: every area is paper, ink, or accent.

PALETTE line: `paper {paper hex}. Carving ink {ink hex}. Accent ink
{accent hex} used sparingly, slightly off-register — the character's accent
part + 1–2 elements.`

## Character treatment

Woodcut maps the riso value rules natively:

- Dark-capable characters (e.g. Blot in bold palettes) → body carved solid
  ink, eyes left as uncarved paper.
- Light-bodied characters → paper body with a thick carved outline, ink eyes.

The accent part is printed in the accent ink in both cases.

## Labels

Short carved-letter capitals in the ink color on bare paper — they should
look cut, not typeset.

## QA deltas (replace the riso grain checks)

- Edges rough and chipped; gouge marks in big fills. **No halftone dots, no
  smooth digital curves, no gray midtones.**
- Slight off-register accent is correct — don't "fix" it.
- ≤2 accent elements beyond the character's accent part.

Calibration example: `assets/examples/styles/woodcut-minicomic.png` — study it for line/texture
and restraint; never copy its composition.
