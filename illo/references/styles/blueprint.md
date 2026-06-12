# Blueprint — style pack

White draftsman linework on a deep blueprint ground: the scene drawn as a
technical drawing of an absurd little machine. A look for **character packs**
(the pack's `Style:` line) suited to engineering posts, systems/architecture
pieces, "how it works" explainers — anywhere "this is a plan" is the right
voice.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: draw EVERYTHING — mascot, objects, arrows — as clean even-weight WHITE construction linework, like a draftsman's technical drawing; up to two small dimension ticks or measurement arrows allowed.

STYLE: architectural BLUEPRINT — crisp white and pale line drawing on a deep blueprint ground, a very faint drafting grid across the paper, slight print-fade at the edges, completely flat, no shading, no gradients, no photorealism.
```

## Palette mapping

Blueprint inverts the riso grammar: dark ground, light line.

- **Ground** ← the structure ink's *hue*, deepened and saturated to blueprint
  depth (L ≈ 25–30%). Neutral/black structure → classic blueprint blue
  `#193a8c`.
- **Line** ← the paper color, lifted to near-white (e.g. `#f4f8ff`, tinted
  toward the paper's temperature).
- **Accent** ← the palette accent, unchanged — warm accents (orange
  `#ff7a1a`) read best on blue grounds; if the accent is cool and vanishes
  against the ground, warm it by hue rotation toward orange.

Classic default (no palette given): ground `#193a8c`, line `#f4f8ff`, accent
`#ff7a1a`.

PALETTE line: `ground {ground hex} with a faint lighter grid. All linework
{line hex}. Accent {accent hex} used sparingly — the character's accent part
+ 1–2 elements.`

## Character treatment

Every character renders as a white line drawing — no fills, dark-body rules
collapse to line-on-ground. Eyes are solid dots in the line color; the accent
part is filled with the accent. State in the CHARACTER block: "drawn in the
same white construction line as everything else, eyes as solid {line-color}
dots, the {accent part} in the accent color."

## Labels

Hand-lettered draftsman-style capitals in the line color, directly on the
ground. Never boxed.

## QA deltas (replace the riso grain checks)

- Faint grid visible; flat ground — no clouds of shading, no vignette heavier
  than a slight edge fade.
- One line weight everywhere; ≤2 dimension ticks.
- **No title block, no stamp, no border frame** — the blueprint cliché the
  model loves to add. Edit out or re-roll.
- Accent appears only on the character's accent part + 1–2 elements.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/blueprint-crossing.png — study it for line/texture
and restraint; never copy its composition.

Variant note: when deriving a blueprint pack from a riso character, the
original sheet works directly as the `--ref` — the style prompt overrides
its rendering.
