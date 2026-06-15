# Felt — style pack

Layered felt-craft: matte wool-felt cutouts stacked in shallow layers on a
felt ground, soft fuzzy nap on every surface, gentle drop shadows between
layers. A warm, tactile, characterful look — storybook explainers, food and
lifestyle, anything cozy and handmade. Unlike the minimalist house looks,
felt **owns a richer character profile** (see "Character treatment"):
multi-color layered bodies and a fuller locked face are the point, not a
violation.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: build EVERYTHING — mascot, objects, props — from layered hand-cut FELT pieces with soft rounded edges and a visible fuzzy nap; NO drawn outlines — shapes separate by flat felt color, by the soft drop shadow where one felt layer sits on another, and by occasional simple stitch dashes; the mascot's body itself reads as stacked felt layers (rows of feathers, quills, petals, or tufts), built exactly like every other felt piece in the scene.

STYLE: LAYERED FELT-CRAFT diorama — matte wool-felt cutouts stacked in shallow layers on a felt ground, soft fuzzy fiber texture on every surface, gentle soft drop shadows between stacked layers, slightly imperfect hand-cut edges and small handmade misalignment; NOT glossy, NOT a 3D render, no plastic sheen, no photorealistic depth-of-field, no gradients within a piece (one flat felt color per shape).
```

## Palette mapping

This look is **multi-color by nature** — bodies and scenes are built from a
small family of felt colors, not a single structure ink:

- **Felt ground** ← the palette paper, a soft felt backdrop and floor.
- **Craft color set** ← a small family of 4–6 muted felt hues (the palette's
  secondary colors, or a soft woodland family) — the layers of the character
  and the scene props are cut from these.
- **Structure ink** ← the structure-ink hue, used ONLY for the small face
  details (dot eyes, nose, mouth) and any fine line — never to outline whole
  shapes.
- **Accent** ← the palette accent, matte; the **one focal accent part** of the
  character + at most 1–2 small scene elements.

Classic default (no palette given): felt ground `#e7e2d2`, structure ink
`#3a352e`, craft set warm-brown `#9a7b5a` / sage `#8fa682` / dusty-blue
`#8fa6b0` / oat `#c9bfa6` / clay `#c08a6e`, accent vermilion `#d9482e`.

PALETTE line: `a soft felt ground {paper hex} breathing through. Layered felt
in a small craft color set {list 4–6 craft hexes by role}; structure-ink
{structure hex} only for the eyes, nose, mouth and fine detail. Accent
{accent hex} used sparingly — the character's one focal accent part + at most
1–2 elements. One flat felt color per shape; soft drop shadows only between
stacked layers.`

## Character treatment (a richer, style-owned profile)

The mascot is built from the same layered wool felt as the rest of the scene
— **never a flat drawing or sticker placed in.** Append to the CHARACTER
block: "the mascot is itself built of stacked hand-cut felt layers exactly
like every other felt piece in the scene." This look deliberately loosens the
house minimalism (`references/character.md`, "A style may own a richer
profile"):

- **Body = locked layer build, judged in aggregate.** The pack names the
  layer logic ("five staggered quill rows", "scalloped feather tiers"); every
  render must read as that layered build at a glance, but individual cut
  pieces may vary run to run the way hatching does. Lock the *read*, not each
  scrap.
- **Multi-color body, ONE focal accent.** The body may use several flat craft
  colors (that is the medium). Exactly one small part is the focal accent in
  the accent hue — name it and force its hue; the accent never spreads across
  the body.
- **Locked cute face.** Cute is welcome and must be pinned exactly: round dot
  eyes, optionally a small flat or stitched mouth and small oval rosy felt
  cheeks — identical every render ("a small stitched mouth", not "a happy
  smile").
- **One clean silhouette.** Richness comes from layers and fuzz, never from
  loose extra parts; the outline must still read at any size.

Value mapping: the body keeps its muted felt tones; the structure-ink details
(eyes, mouth, stitching) use the structure ink, never pure black; the focal
accent stays the accent hue in every palette.

## Labels

≤2 short hand-lettered English capitals in the structure-ink color directly
on the bare felt ground — slightly irregular, stitched/painted look. Never
tiny detailed lettering (it mangles), never on a colored fill.

## QA deltas (replace the riso grain checks)

- **The mascot is layered felt.** A flat/drawn mascot on a felt set = re-roll.
- Fuzzy fiber texture on every surface; soft drop shadows ONLY between stacked
  layers — no gradients within a piece, no gloss, no 3D-render sheen, no
  depth-of-field blur.
- Face matches the locked spec exactly (eyes/nose/mouth/cheeks as written).
- Multi-color body is fine, but exactly ONE focal accent part carries the
  accent hue — force the hue in words next to the hex; the accent never
  spreads across the whole body.
- Silhouette reads as one clean shape at small size; layer count stays in the
  locked band (no detail creep into loose parts).

Calibration example: none bundled yet — study the community felt packs in
[`illo-characters`](https://github.com/tmchow/illo-characters) (`quill`,
`plume`, `posy`, `pleat`) for line/texture and accent restraint; never copy
their compositions.
