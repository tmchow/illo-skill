# Pixel — style pack

Chunky low-resolution pixel art on a strict 4-color palette. A look for
**character packs** (the pack's `Style:` line) suited to retro-computing
pieces, games-adjacent posts, terminal/CLI content.

**Known failure mode (why this file is strict):** smooth source art fights
pixelation — the scene pixelates but the mascot renders smooth. A pixel
pack's model sheet must itself be pixel-built (born that way in the builder,
or derived as a variant — `references/character-builder.md`, "Style
variants"; a ready example sheet: `assets/character-reference-pixel.png`).
The CHARACTER forcing line below is mandatory in every prompt; a smooth
mascot is an automatic re-roll.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: chunky PIXEL construction — every shape, INCLUDING THE MASCOT, is built from visible square pixels on one shared pixel grid; 1-pixel stair-stepped outlines; sparse checkerboard dithering only where texture is needed.

STYLE: retro PIXEL ART as if a 160x90 image were scaled up with nearest-neighbor — hard square pixels, NO anti-aliasing, NO smooth curves anywhere, NO gradients; flat single-color fills per shape. If any edge in the image is smooth, the image is wrong.
```

## Palette mapping

Quantize the resolved palette to exactly 4 colors:

1. **Background** ← paper.
2. **Ink** ← structure ink (outlines, label text, dark fills).
3. **Mid** ← a single midtone derived from the structure hue at ~60%
   lightness (secondary shapes only).
4. **Accent** ← the palette accent.

Classic default (no palette given): background `#f2ead8`, ink `#1c1a17`, mid
`#a89c88`, accent magenta `#e0359a`.

PALETTE line: `exactly 4 colors — background {paper hex}, ink {structure
hex} for outlines and dark fills, mid {mid hex} for secondary shapes, accent
{accent hex} used sparingly: the character's accent part + 1 element.`

## Character treatment

The reference supplies proportions and identity only — the rendering is
re-drawn in pixels. Append to the CHARACTER block: "the mascot itself is
built from visible square pixels with a stair-stepped outline, exactly like
every other shape — it must NOT be smoother than the rest of the image."

## Labels

≤2 short labels in a blocky pixel font, ink color, on the background. Check
for duplicated labels — this style has produced the same label twice.

## QA deltas (replace the riso grain checks)

- **The mascot is pixelated.** Smooth mascot = re-roll (the #1 failure).
- Zero anti-aliasing anywhere; one consistent pixel size across the image.
- Exactly 4 colors; no gradients or soft shadows.
- No duplicate labels; ≤2 labels total.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/pixel-funnel.png — study it for line/texture
and restraint; never copy its composition.
