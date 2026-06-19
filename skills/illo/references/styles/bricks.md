# Bricks — style pack

A photograph of a little world built entirely from interlocking toy building
bricks — the mascot and everything around it assembled from flat, studded
plastic bricks and shot like a real toy set. This is the skill's **one
deliberately photographic look** (every other look is illustration/print);
reach for it when the toy-brick, buildable, "snap it together" voice is the
point — build sequences, step-by-step explainers, playful product-y scenes,
launches and missions. A look for **character packs** (the pack's `Style:`
line).

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: there are NO drawn outlines — every form is CONSTRUCTED from interlocking toy building-bricks and read by its real molded edges. The ENTIRE scene is brick-built: the ground is a flat STUDDED baseplate, and all terrain, structures, props, even effects (water, smoke, stars) are ASSEMBLED from stacked rectangular bricks, plates and tiles with flat faces, crisp square corners, visible round studs and real seams. Only a few special pieces are smooth and rounded (a molded character head or helmet, a round pearl/dome, a translucent round stud); everything else is blocky.

STYLE: PHOTOREAL TOY-BRICK SET — a real physical brick build PHOTOGRAPHED in studio macro: glossy molded ABS plastic with true reflections, fine surface scuffs and mold seams, realistic soft key light, gentle shadows and a shallow depth of field, on a clean seamless gradient backdrop. It deliberately IS a photograph of a toy. No drawn lines, no flat illustration, no painterly washes, no neon; the brick grid and stud pattern stay legible everywhere.
```

## Palette mapping

Toy bricks are solid molded colors — the palette maps onto brick colors, not
inks or washes:

- **Ground** ← a flat studded baseplate in a neutral brick color (the palette
  paper reinterpreted as plastic: warm sand, stone grey, or deep blue for
  water).
- **Body bricks** ← the mascot's bricks follow its value rule using a solid
  molded color of the structure hue (dark-capable) or a pale plastic
  (light-bodied).
- **Structure "ink"** ← the deep recesses, seams and the **printed dot eyes** on
  the smooth head tile — the darkest value, never pure black.
- **Accent brick** ← the palette accent as one vivid molded piece: the
  character's single accent part, plus at most 1–2 small scene bricks.
- **Translucent pieces** ← trans-clear/trans-blue/trans-amber bricks for water,
  glass, light and bubbles — the brick way to render an effect.

Classic default (no palette given): sand baseplate `#d8c79a`, body cream
`#e9e2d0` / navy `#33415c`, structure recess `#2b2b30`, accent warm brass
`#c89a3c`.

PALETTE line: `the whole build is solid molded plastic bricks on a studded
{ground hex} baseplate; body bricks {body hexes by role}; deepest seams and
printed dot eyes {structure hex}, never pure black; exactly one vivid accent
brick {accent hex} on the character's accent part (+1–2 small bricks at most);
effects rendered as translucent bricks.`

## Character treatment

The mascot is a small brick minifigure-style toy, **actually built from
bricks** — stubby brick limbs, simple curved mitten hands, a blocky stud-topped
torso — never a flat sticker dropped into a photo. It still follows the house
character rules in `references/character.md`: one clean silhouette, a locked,
exactly-specified face (house default: two printed dot eyes on a smooth molded
head, blank deadpan), and exactly ONE accent-carrying part — the single vivid
brick in an otherwise restrained build. The head or helmet is the main smooth,
rounded exception to the blocky world.

Value mapping: the body bricks and brick terrain hold their molded values; the
seam shadows and printed dot eyes are the deepest value (never pure black); the
one accent brick stays the accent hue in every palette.

> **IP guardrail:** evoke generic toy-brick construction — do not replicate a
> specific trademarked minifigure's exact proportions or trade dress, and never
> show real-brand logos on studs. Generic blocky build only.

## Labels

Short capitals printed on small brick **tiles or signs** (a 1x2 printed tile, a
little brick signpost), ≤2 labels — the toy-set captioning convention. Crisp
printed lettering reads well here; keep it short and never tiny.

## Staging fit (read before choosing the shot)

Bricks discretize: continuous things become stepped, chunky brick versions of
themselves (a stream of water becomes an arc of trans-blue studs, smoke becomes
stacked grey bricks, a curve becomes a staircase of plates). That is the look
working, not failing — so it shines for **build sequences, step/station
explainers, before/after, and snap-together stories** (and photo-comic strips,
since a toy set photographs naturally in panels). Continuous-flow metaphors (a
single smooth unbroken line, organic blobby growth) fight the medium. Above all
the WHOLE frame must be brick-built; a brick character standing in a painterly
or photographic real-world environment is the signature failure.

## QA deltas (replace the riso grain checks)

- **The entire world is brick-built, not just the mascot.** Organic/painterly
  terrain, real sand, real water, a real chain, a smooth real-world floor =
  re-roll. Ground must be a studded baseplate; props must be stacked bricks.
- **It reads as a real photographed toy.** Flat illustration, drawn outlines,
  painterly washes, or a cartoon render = re-roll (this is the one photographic
  look — studio macro, true ABS gloss, shallow depth of field).
- Smooth pieces are limited to molded heads/helmets, round domes/pearls, and
  translucent studs; everything structural stays flat-faced and studded.
- The mascot face matches the locked spec exactly — two printed dot eyes on a
  smooth head; exactly ONE accent brick carries the accent hue (force the hue
  next to the hex; it never spreads to a second piece).
- One clean silhouette that still reads at small size.
- Generic brick construction — no trademarked minifig trade dress, no real-brand
  logos on the studs.

Calibration example: none bundled in-skill — study the community bricks packs in
[`illo-characters`](https://github.com/tmchow/illo-characters) (`fathom`,
`orbit`, `klaxon`) for the brick-built world, accent restraint and toy-photo
lighting; never copy their compositions.

Variant note: a bricks pack can't reuse a flat illustrated sheet as `--ref` —
the character must be re-built as a brick minifig and the model sheet shot as a
studio photo on a plain baseplate; derive every scene from that sheet.
