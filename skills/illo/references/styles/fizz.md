# Fizz — style pack

A high-energy psychedelic soda-pop screenprint: 1990s/early-2000s skate
stickers, underground comics, cereal-box mascots, punk flyers and psychedelic
beverage packaging. Thick, hand-inked **dark-blue or purple** outlines (never
black), flat screen-printed fills in loud high-contrast color, and comic energy
everywhere — bubbles, drips, starbursts, speed lines. Playful, weird, slightly
chaotic, handmade; the deliberate opposite of clean corporate vector. A look
for **character packs** (the pack's `Style:` line), suited to launches, hype,
energy, motion and anything loud and fun.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: outline EVERYTHING — mascot, objects, arrows, labels — in THICK, hand-inked DARK BLUE or PURPLE lines, NEVER black. Lines are wobbly and hand-drawn with rounded, imperfect curves and uneven, lively line weight; bold and confident, like a screen-printed skate sticker, not a clean vector.

STYLE: 1990s/early-2000s SKATE-STICKER + UNDERGROUND-COMIC + CEREAL-BOX-MASCOT + PSYCHEDELIC-BEVERAGE screenprint. FLAT fills, minimal-to-no shading, bold high-contrast color blocks. Slight screen-printed/sticker roughness and faint misregistration; exaggerated, expressive, goofy-surreal shapes with oversized features. Pack the energy in: motion splashes, starbursts, bubbles, liquid drips, speed lines, comic impact marks. NOT glossy, NOT 3D, NOT photoreal, NOT minimal SaaS-vector — handmade and a little chaotic.
```

## Palette mapping

The loud palette maps onto flat screenprint inks, not washes:

- **Paper / ground** ← the palette paper, default warm **cream** (`#f6ecd2`),
  visible as the breathing background.
- **Structure ink** ← the outline color, a **deep blue or purple near-black**
  (default cobalt-purple `#2b2b6b`) — every outline and all the lettering.
  True black is wrong for this look.
- **Fills** ← the loud set, one flat tone per shape, 3–5 colors per image:
  bright orange `#ff7a1a`, lemon yellow `#ffd21e`, cobalt blue `#1f5fff`, neon
  green `#3fd23f`, hot pink `#ff5fa2`, red `#ef2d2d`, plus cream.
- **Accent** ← the palette accent, for the character's accent part + 1–2 energy
  marks.

Classic default (no palette given): cream paper `#f6ecd2`, cobalt-purple ink
`#2b2b6b`, fills from orange / yellow / cobalt / neon-green, accent neon green
`#3fd23f`.

PALETTE line: `cream paper {paper hex}, every outline + lettering in deep
blue-purple ink {structure hex}, never black. Flat blocks of {2-3 loud fill
hexes}, one flat tone per shape. Accent {accent hex} on the character's accent
part and 1-2 energy marks. No gradients.`

## Character treatment

The mascot is outlined in the same thick wobbly blue-purple ink as everything
else and filled with flat blocks of the loud palette. It still follows the
house character rules in `references/character.md`: one clean silhouette, a
locked, exactly-specified face, and exactly ONE accent-carrying part. This look
runs HOT, so the face is usually expressive rather than deadpan — big eyes, a
grin, motion — but the parts stay locked; emotion comes from their shape. Eyes
are cream with dark blue-purple pupils. The accent part is one clean
accent-color shape. Energy marks (bubbles, drips, speed lines) belong to the
*scene*, not the character — keep any baked into a cutout physically connected
to the body.

## Labels

Chunky hand-drawn display lettering in the blue-purple ink — optionally filled
with one loud color and outlined — warped, stretched, slightly irregular, part
of the illustration, never a clean typeset UI label. ≤2 labels; keep them short
and bold.

## Staging fit (read before choosing the shot)

Fizz is built for momentum: launches, releases, hype, energy, motion,
before/after bursts, "ship it" beats and loud announcements. The energy marks
(splashes, starbursts, speed lines, fizz) are the medium doing its job, so
action scenes shine. Quiet, sober, minimal or corporate-clean subjects fight
the look — if a scene wants restraint and white space above all, reach for a
calmer look instead.

## QA deltas (replace the riso grain checks)

- Every outline is **deep blue or purple, never black** — if lines read black,
  re-roll.
- Flat fills, one tone per shape — **no gradients, no soft shading, no gloss,
  no 3D, no photoreal.**
- At least a few **comic energy marks** present (bubbles / drips / starbursts /
  speed lines) — if the image is calm and sterile, it has drifted toward clean
  vector; re-roll.
- Lines are **wobbly and hand-drawn**, not crisp geometric vector.
- The mascot face matches the locked spec exactly; exactly ONE accent part
  carries the accent hue (force the hue next to the hex; it never spreads).
- One clean silhouette that still reads at small size.

Calibration example: none bundled in-skill — study the community fizz packs in
[`illo-characters`](https://github.com/tmchow/illo-characters) (`kick`, `pop`,
`boom`) for the line weight, flat loud fills and energy-mark restraint; never
copy their compositions.

Variant note: a flat riso/illustrated sheet can be reused as `--ref` for a fizz
pack — the style prompt re-renders it in the fizz look. As always, lock the
model sheet first, then derive every scene from it.
