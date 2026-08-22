# SNES — style pack

16-bit console sprite editorial: a slightly finer pixel grid than NES, soft
checkerboard / diagonal dither for volume, hard square pixels throughout. A
look for **character packs** (the pack's `Style:` line) suited to games-
adjacent posts, adventure metaphors, party-member energy, and anything that
wants richer shade than strict 4-color `pixel` without leaving the console
family.

**Known failure modes (why this file is strict):**

1. **Smooth mascot** — the scene pixelates but the character renders smooth /
   AA'd. The CHARACTER forcing line below is mandatory; a smooth mascot is an
   automatic re-roll. Model sheets for SNES packs must themselves be
   pixel-built.
2. **Dither scale drift** — dither cells grow huge on one prop and tiny on
   another. One shared pixel grid and one dither cell size across the frame.
3. **Color / accent flood** — models sneak a 7th–10th color, or paint every
   prop gold. Cap at **6** including paper; accent only on the character's
   accent part + **one** scene element. Other props use mid-cool / mid-warm /
   deep — never a second accent hue.
4. **CRT / bezel creep** — scanlines, TV frames, and monitor glass are a
   different look (`phosphor` / CRT proposal). SNES is a clean sprite sheet
   on flat paper, not a TV capture.
5. **Cutout edge spoil** — dither or paper color leaks outside the character
   cluster. On cutouts, dither the **character only**; native-alpha pixels
   outside it must be transparent, while a forced chroma screen must stay flat
   and undithered.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: 16-bit PIXEL construction on one shared pixel grid (finer than chunky NES — think a 256-wide sprite sheet scaled with nearest-neighbor); 1-pixel stair-stepped outlines; soft checkerboard and diagonal dither for volume ONLY — never smooth gradients; every shape, INCLUDING THE MASCOT, is hard square pixels.

STYLE: SNES-era console SPRITE ART editorial — hard square pixels, NO anti-aliasing, NO smooth curves, NO photoreal, NO CRT scanlines, NO TV bezel, NO monitor glass. Flat fills plus restrained dither shade. If any edge in the image is smooth, the image is wrong. Feels like an overworld NPC or party-member sprite enlarged for print, not a screenshot of a glowing CRT.
```

## Palette mapping

Quantize the resolved palette to **at most 6 colors**:

1. **Background** ← paper (default lavender-cream `#e8e0f0`).
2. **Ink** ← structure ink for outlines, label text, dark fills
   (default `#2a1f3d`).
3. **Mid-cool** ← secondary shapes / cool fills (default `#6b7db5`).
4. **Mid-warm** ← secondary shapes / warm fills (default `#c4785a`).
5. **Accent** ← the palette accent (default gold `#e8c84a`).
6. **Deep** ← deepest shade / platform undersides (default `#4a3560`).

When the resolved palette has fewer named stops, derive mid-cool / mid-warm /
deep from the structure hue rather than inventing new hues. Character body
colors must map into these stops (e.g. a red apple uses mid-warm pushed toward
true red, still counting as one of the six).

PALETTE line: `at most 6 colors — background {paper hex}, ink {structure hex}
for outlines and labels, mid-cool {mid-cool hex}, mid-warm {mid-warm hex},
deep {deep hex}, accent {accent hex} used sparingly: the character's accent
part + 1 element. Soft checkerboard dither only between neighboring stops —
never a smooth gradient.`

Classic default (no palette given): background `#e8e0f0`, ink `#2a1f3d`,
mid-cool `#6b7db5`, mid-warm `#c4785a`, accent `#e8c84a`, deep `#4a3560`.

## Character treatment

The reference supplies proportions and identity only — the rendering is
re-drawn in pixels. Append to the CHARACTER block: "the mascot itself is
built from visible square pixels with a stair-stepped outline and the same
dither cell size as every other shape — it must NOT be smoother than the rest
of the image."

Accent discipline still holds: exactly ONE accent-carrying part on the
character, plus at most one accent prop in the scene.

## Labels

≤2 short labels in a blocky pixel font, ink color, on the background. Never
boxed UI chrome. Check for duplicated labels — pixel-family looks have
produced the same label twice.

Explainers may use short step words on the structure (e.g. IN / WORK / OUT)
as the label budget — do not add a separate title on top. Mini-comics get
per-panel labels only (e.g. BEFORE / AFTER).

## Cutouts

Same SNES character treatment, but:

- Outside the character cluster is **transparent** on Codex-native output or
  only the engine-selected flat chroma on the compatibility path — no lavender
  paper, no dither, no ground shadow.
- Dither lives on the mascot body only.
- No labels, no environment.

If native alpha fails, re-roll once, then force `--chroma`; if chroma keying
fails, re-roll with "ZERO dither outside the character cluster" before
accepting an opaque deliverable.

## Staging fit

SNES likes readable silhouettes, a little volume via dither, and adventure /
party-member sincerity. It fights photoreal props, dense dashboards, and
CRT nostalgia (use phosphor for that). Prefer one clear move over a busy HUD.

**World vernacular (required for impact):** do not stage on blank paper with a
pixel mascot alone. The scene should read as a 16-bit game world slice —
tiles, bricks, platforms, chests, paths, doorways — so the look is carried by
place and props, not only by dither. Avoid licensed icons (no Mario
question-blocks, no Triforce); use generic 16-bit grammar.

### Three world views (required; every SNES character pack)

Every character with `Style: snes` inherits these three cameras. Prefer
**human / party-member** mascots — they match 16-bit game casts better than
object or produce mascots for this look.

Unless the user names a view, the agent **picks one per image** — either
uniformly at random or by fit to the thesis (journey → top, momentum/gap →
side, unlock/reward/gate → prop-first). Across a multi-image set, rotate so
the series does not collapse into one camera.

1. **Top view (overworld)** — top-down tilemap: grass/dirt/stone tiles, paths,
   bushes, cliffs, caves, town squares. Camera looks down. Best for journeys,
   routes, scope, exploration, getting stuck on the map.
2. **Side view (platformer)** — side-scrolling stage: floating brick/block
   platforms, ladders, coins, gaps, parallax sky hills. Camera looks from the
   side. Best for momentum, gaps, shipping, climbs, one-more-jump.
3. **Prop-first (loot nook)** — item vernacular leads: chest, key, potion,
   coins, pots, torch — usually in a dungeon/treasure alcove. Camera can be
   slight 3/4 but props carry the metaphor. Best for unlocks, rewards, gates,
   triage, “what you carry.”

Name the chosen world view in the shot notes. Keep HUD chrome off (no health
bars, no full inventory screens). World-staging gallery:
https://6882e96a.ht-ml.app/ (password trevin).

## QA deltas (replace the riso grain checks)

- **The mascot is pixelated.** Smooth / AA'd mascot = re-roll (#1 failure).
- Zero anti-aliasing anywhere; one consistent pixel size and dither cell size
  across the image.
- ≤6 colors; no smooth gradients or soft airbrushed shadows.
- No CRT scanlines, TV bezel, monitor glass, or photoreal materials.
- No duplicate labels; ≤2 labels total.
- Accent only on the character's accent part + ≤1 scene element.

## Calibration notes (2026-07-24 pass with Crisp)

What held across editorial / explainer / busy-props / mini-comic:

- Shared pixel grid + soft checkerboard dither reads consistently.
- Funnel/hourglass bottleneck, 3-step flow, triage table, and 2-panel
  before/after all stayed on-look without CRT creep.
- Crisp (red apple + green leaf) stays readable when body maps to a warm
  stop and the leaf keeps the single accent.

What to watch:

- **Accent flood** on busy prop scenes (gold key + gold coin + gold chest).
  Keep non-accent props in mid-cool / mid-warm / deep.
- **Cutouts**: two stacked failure modes for green-accent characters like
  Crisp: (1) engine clean_alpha fringe gate discards keyed output; (2)
  default illo chroma_key_to_png treats green leaf fills as green-screen
  spill (_is_spill_halo) and punches them hollow. Practical fix: key with
  magenta-distance only (no green-spill pass), keep the result even when
  fringe is high, and bake a checkerboard preview for review.


Calibration examples (study for line/texture and restraint; never copy
compositions): https://4e2e44c9.ht-ml.app/ (password trevin).
