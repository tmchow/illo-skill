# Diorama — style pack

Soft hand-drawn children's-book illustration in a slightly elevated isometric
"tabletop diorama" perspective — peeking down into a tiny self-contained world
that sits on a surface. Confident dark ink outlines on the main forms, but
everything filled with loose watercolor-and-gouache washes rather than flat
color, on heavily textured handmade paper with a warm aged vintage tint. The
charm is a tension: hard surfaces (rock, paving) render as faceted, low-poly,
almost crystalline geometric chunks, set against soft organic pillowy foliage.
A storybook-explainer look — cozy, tactile, miniature-world — that almost
always reads as a tiny diorama framed by out-of-focus foreground foliage.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: confident dark ink outlines on the main forms — the mascot,
objects and faceted stones — with every shape filled by loose, layered
watercolor-and-gouache washes rather than flat color (visible brush pooling,
soft granulation, a little bleed past the line); hard surfaces (rock, paving,
crystal) drawn as faceted, low-poly, almost crystalline geometric chunks with
flat planes, while trees, bushes, moss and other foliage stay soft, organic,
pillowy blobs — the angular-stone-against-soft-foliage tension is the point.

STYLE: soft hand-drawn CHILDREN'S-BOOK TABLETOP DIORAMA — a slightly elevated
isometric view peeking down into a tiny self-contained world resting on a
surface, on heavily textured handmade/recycled paper with visible grain and
fiber and a faint warm aged vintage tint baked into the lighting; out-of-focus
foliage in the foreground corners vignettes the scene (a gentle tilt-shift
miniature feel). NOT glossy, NOT a 3D render, no plastic sheen, no photographic
realism, no neon; washes stay muted and earthy.
```

## Palette mapping

This look is **multi-color and painterly** — a small muted earthy family of
washes, not a single structure ink:

- **Paper ground** ← the palette paper: an aged off-white handmade stock, grain
  and fiber breathing through everywhere.
- **Wash family** ← a small set of 4–6 muted, slightly desaturated washes (the
  palette's secondaries, or a soft garden family — sage, olive, warm brown,
  dusty blue, stone grey) for foliage, stone, water and the mascot's body.
- **Structure ink** ← the structure-ink hue: a dark warm brown-black for the
  confident outlines and the small face details (dot eyes) — never pure black.
- **Accent** ← the palette accent, used sparingly: the character's one focal
  accent part + at most 1–2 small scene elements.

Classic default (no palette given): paper `#efe7d4`, structure ink `#3a342b`,
wash family sage `#9caf8f` / olive `#7d8456` / warm-brown `#9a7b57` /
dusty-blue `#8ba0a8` / stone-grey `#c7c2b6`, accent coral `#e06a3b`.

PALETTE line: `an aged off-white handmade-paper ground {paper hex} with grain
and fiber throughout. Loose watercolor-and-gouache washes in a small muted
earthy family {list 4–6 wash hexes by role}; confident structure-ink
{structure hex} outlines and dot eyes, never pure black. Accent {accent hex}
used sparingly — the character's one focal accent part + at most 1–2 elements.
A warm aged vintage tint over the whole frame; faceted stone against soft
foliage.`

## Character treatment

The mascot is rendered in the **same ink-and-wash technique** as the rest of
the diorama — confident dark outline, loose washes inside — and may be built
from the world's own materials (faceted crystalline stone, forged metal and
glass, paper, moss), never a flat sticker dropped onto a painted scene. It
still follows the house character rules in `references/character.md`: one clean
silhouette, a locked, exactly-specified face (house default: two dot eyes,
blank deadpan, no mouth), and exactly ONE accent-carrying part — the only
saturated note in an otherwise muted earthy frame.

Value mapping: the body and stone read in muted earthy washes; the structure-
ink outlines and dot eyes are the deepest value (never pure black); the one
focal accent stays the accent hue in every palette.

## Labels

≤2 short hand-lettered English capitals in the structure-ink color, painted
directly on the bare paper ground or a small wooden signpost — slightly
irregular, storybook hand-painted look. Never tiny detailed lettering (it
mangles), never on a busy painted fill.

## QA deltas (replace the riso grain checks)

- **It reads as a tiny tabletop diorama.** A flat full-bleed scene with no
  sense of a small self-contained world on a surface = re-roll.
- Confident dark ink outlines on the main forms, with loose watercolor/gouache
  washes inside — NOT flat color, NOT gradients-as-render, no gloss, no 3D
  sheen, no photographic depth (the only blur is the soft foreground vignette).
- Hard surfaces are faceted/low-poly crystalline; foliage is soft pillowy
  blobs — both present, the tension visible.
- Visible handmade paper grain and a warm aged vintage tint across the frame.
- The mascot face matches the locked spec exactly; exactly ONE focal accent
  part carries the accent hue — force the hue next to the hex; it never spreads.
- One clean silhouette that still reads at small size.

Calibration example: none bundled in-skill — study the community diorama packs
in [`illo-characters`](https://github.com/tmchow/illo-characters) (`wick`,
`spritz`, `whorl`) for line/wash/texture and accent restraint; never copy their
compositions.
