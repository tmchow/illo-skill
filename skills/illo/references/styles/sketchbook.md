# Sketchbook — style pack

Loose vintage pencil-and-ink editorial-cartoon sketch on aged paper: confident
but sketchy hand-drawn linework with construction lines and searching strokes
left un-erased, all shading built from dense graphite cross-hatching, rendered
in a **monochromatic warm sepia** "ink" (warm brown-black, never true black) on
a cream-to-tan, coffee-stained / sun-faded sketchbook page. The mood sits
between a New Yorker spot drawing and a children's-book technical doodle — warm,
hand-made, never slick. Suited to characterful editorial vignettes, retro-tech
worlds, and storybook explainers. Unlike the minimalist house looks, sketchbook
**owns a richer character profile** (see "Character treatment"): a fuller
emotive face and big-head cute figures — including humans — are the point, not a
violation.

The defining restraint: the whole image is warm sepia **except** a few tiny,
sparing **cool** color pops (a teal screen glow, a pale-blue teardrop). Those
rare cool accents against the warm neutral ground do all the color work.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: draw EVERYTHING — mascot, props, environment — as loose hand-drawn pencil-and-ink sketch lines; confident but sketchy warm brown-black outlines with visible construction lines, searching/doubled strokes and un-erased guide marks left in; ALL shading built from dense cross-hatching and parallel-line hatching (on bodies, clothing, furniture, cast shadows), never flat fills and never smooth digital gradients; the mascot is drawn in the same hatched pencil technique as the rest of the scene.

STYLE: VINTAGE PENCIL-AND-INK EDITORIAL-CARTOON SKETCH on an aged cream-to-tan paper page with visible grain, faint coffee-stain blooms and a sun-faded warm tint; monochromatic warm sepia throughout — the "ink" reads warm brown-black, NOT true black, NOT cold grey; hand-drawn sketchbook quality, like a New Yorker spot drawing crossed with a children's-book technical doodle; NOT clean vector, NOT flat color, NOT a 3D render, NOT glossy, no photorealism.
```

## Palette mapping

This look is **monochrome by nature** — one warm sepia ink on warm paper — with
the accent reserved for a few tiny COOL pops:

- **Paper ground** ← the palette paper, an aged cream-to-tan page with grain and
  faint coffee/sun staining.
- **Sepia ink** ← the structure-ink hue, shifted **warm** (brown-black): every
  line and every cross-hatch on every surface, the mascot included.
- **Accent** ← the palette accent, used as a **rare COOL pop** only — the
  character's one focal accent part + at most 1–2 tiny scene elements (a glowing
  screen, a teardrop). Everything else stays warm sepia.

Classic default (no palette given): paper ground `#ece0c8`, sepia ink `#4a3a2a`,
accent cool teal `#3f9f9a` (with a pale sky-blue `#9cc3d6` permitted for a
teardrop/water pop).

PALETTE line: `an aged cream-to-tan paper ground {paper hex} with visible grain
and faint coffee/sun staining; one warm sepia ink {structure hex, brown-black}
for ALL lines and cross-hatching on every surface; the only color is a rare COOL
pop of accent {accent hex} — the character's one focal accent part plus at most
1–2 tiny scene elements. Everything else stays monochrome warm sepia.`

## Character treatment (a richer, style-owned profile)

The mascot is drawn in the same hatched pencil-and-ink as the rest of the scene
— **never a clean flat sticker dropped onto a sketched set.** Append to the
CHARACTER block: "the mascot is drawn in the same loose cross-hatched sepia
pencil-and-ink as every other element in the scene." This look deliberately
loosens the house minimalism (`references/character.md`, "A style may own a
richer profile"):

- **Form via hatching, judged in aggregate.** Volume comes from cross-hatching
  following each surface; the exact strokes may vary run to run the way real
  hatching does — lock the *read*, not each stroke.
- **Monochrome body, ONE cool accent.** The whole mascot is warm sepia. Exactly
  one small part is the focal accent — the only element carrying the cool accent
  color, and it stays tiny. Name it and force its hue; it never spreads.
- **Expressive but locked face.** This look permits a fuller, emotive cartoon
  face (large round eyes with pupils, a simple mouth). Pin it exactly in the
  pack and keep its construction identical every render; emotion is shown by
  brow/mouth *shape* only, never by changing the face's parts.
- **Cute by proportion (chibi) — the default for figures.** Figures (human or
  animal) use a **chibi build**: about **2 heads tall**, an oversized round head
  on a small soft body, short stubby limbs, simple mitten hands, little rounded
  shoes. Keep the **face line clean** (hatching lives on clothing/props/scene),
  and give every figure a **clearly visible hairstyle — never bald**. Realistic
  adult proportions or a detailed lifelike face read "serious editorial," not
  cute, and are a re-roll. Lock cuteness in *words* (proportions + hair +
  costume + prop); do NOT anchor a new figure on another character's model sheet
  to borrow the style — it bleeds that character's features.
- **One clean silhouette.** Even with loose linework, the outline must read as
  one clear shape at small size.

Value mapping: the body stays light cream with warm sepia ink and hatched
recesses; the deepest values are hatched shadows, never a flat black fill; the
focal accent stays the cool accent hue in every palette.

## Labels

Short hand-lettered English words in the sepia ink, drawn ON props (a sign, a
sheet of paper, a CRT screen) the way a cartoonist letters a caption — loose and
slightly irregular, matching the sketch. Keep to a few words; never tiny
detailed paragraphs (they mangle), never on a colored fill.

## QA deltas (replace the riso grain checks)

- **The mascot is hatched pencil-and-ink.** A clean flat/vector mascot on a
  sketched set = re-roll.
- Visible construction lines + cross-hatching on every surface; warm sepia "ink"
  (brown-black, not true black, not cold grey); aged paper grain and faint
  staining present. No flat fills, no smooth gradients, no gloss, no 3D-render
  sheen, no photorealism.
- Figures are cute by proportion: ~2-head chibi build, clean simple face, a
  visible hairstyle (never bald). Lifelike adult proportions = re-roll.
- Face matches the locked spec exactly; emotion via brow + mouth shape only.
- Monochrome sepia throughout, with ONLY the rare cool accent pops — force the
  accent hue in words next to the hex; color never spreads into the warm field.
- Silhouette reads as one clean shape at small size.

Calibration example: none bundled yet — study the community sketchbook packs in
[`illo-characters`](https://github.com/tmchow/illo-characters) (`coil`, `relay`,
`marshal`, `cook`) for line/hatching, chibi proportions and accent restraint;
never copy their compositions.
