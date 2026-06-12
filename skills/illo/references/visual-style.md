# Visual style

This file defines **riso**, the house default look. A character pack carries
exactly one style (its `Style:` line — SKILL.md step 4); the other bundled
looks live in `references/styles/`, custom ones in
`${XDG_CONFIG_HOME:-~/.config}/illo/styles/`.

## One line

A risograph print of a small absurd machine-world: grainy, flat, bold-lined,
generous with empty space — a clever idea drawn as one clean scene, not a
diagram.

## The risograph signature (this is the ownable part)

The identity is the **print technique**, independent of color:

- **Halftone grain** — fills are flat ink with a visible dot screen, not smooth.
- **Ink-layer offset** — a slight misregistration between inks (a thin colored
  edge alongside the line). Subtle, not glitchy.
- **Paper grain** — a faint stock texture under everything; never glossy.
- **Flat fills** — no gradients, no soft drop shadows, no photographic light.

Because the signature is the technique, the palette is a free parameter — see
`palettes.md`.

## Line language (unify the whole drawing)

Everything — the mascot, the props, arrows, labels' underlines — shares ONE
line treatment:

- **Bold and even-weight**, confident, not thin/scratchy/wobbly.
- **Softly rounded** corners and terminals (a clean vinyl-sticker line).
- Props are simple geometric-but-soft forms that match the mascot's
  construction. The mascot must never look like a different artist drew it.

This is the key quality lever: if the props look loose/sketchy while the mascot
is crisp, the image fails. Redraw everything in the mascot's line.

## Paper and fills

- **Paper**: a light stock (warm cream by default; the exact tint comes from the
  palette). Never pure-white glossy, never dark.
- **Negative space**: keep ≥ ~35% of the canvas quiet; the subject occupies
  roughly 50–70%. One calm empty region is good.
- **Subject scale**: large and confident, centered or rule-of-thirds. (The model
  drifts small sometimes — re-roll tiny subjects.)

## Color grammar (constant across every palette)

- **Structure ink** (the darker ink): all linework, forms, the mascot's dark
  features, and label text.
- **Accent ink** (the brighter ink): the live, attention-pulling color — the
  character's accent part and the one or two things that most matter in the
  scene. Sparing.
- Optional **secondary accent**: one extra hue, only when an idea genuinely has
  two parts worth separating, and only in the richer palettes. Keep it subordinate.

## Hard don'ts

- No photorealism, no 3D render, no glossy vector, no corporate flat-illustration.
- No PowerPoint/infographic/flowchart look; no formal diagram grids. (An
  **explainer-register** image may use hand-drawn arrows and stations —
  `composition.md`, "The explainer register" — but never the formal look:
  no titles, borders, grids, legends, or vector boxes in any register.)
- No cute-cartoon-poster, children's-book, sticker-pack, or emoji vibe.
- No complex backgrounds, gradients, drop shadows, paper-fold/3D-paper effects.
- No title bar or type label ("Workflow", "System Diagram", etc.) anywhere on
  the image. Let the scene speak.
- No dense explanation: one core idea per image, ≤3 short labels
  (explainer register: that register's callout budget instead).

## Aesthetic target

Strange but clean; clear but not instructional; smart, dry, a little deadpan.
A reader should feel "huh, that's a bit odd" and then get the point within a
second.
