# Bloom — style pack

A flat cel character staged inside a soft, atmospherically-lit scene: one
diegetic light source, gentle bloom and depth, a painterly ground behind a
crisp graphic character. A look for **character packs** (the pack's `Style:`
line) suited to slice-of-life, focus and quiet-work, mood and place — the
warm, cinematic voice of the library. The signature is **light and
atmosphere**, not any one palette; the cozy warm default below is just a
default.

## The signature (this is the ownable part)

The identity is the **contrast between a crisp flat character and a softly lit,
deep scene**, independent of palette:

- **Flat cel character** — the mascot is a clean flat fill with ONE bold,
  even-weight, softly rounded outline. No rendering, no gradient, no texture on
  the character body itself; it stays graphic in every frame.
- **One diegetic light source** — every scene has exactly one visible light
  (lamp, window, screen, candle, fire, sky) that casts a soft glow with a smooth
  gradient falloff into shadow. This light is the look; it is what riso forbids
  and bloom is built on.
- **Painterly atmosphere on the GROUND only** — soft ambient gradients, gentle
  bloom around the light, light haze and soft focus for depth, a quiet vignette.
  The background is painted and deep; the character stays flat.
- **Calm, lived-in staging** — the character performs an ordinary act with total
  sincerity inside a real place. Quiet, not dramatic.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: draw the MASCOT and key props as flat cel shapes with ONE bold, even-weight, softly rounded outline and flat interior fills — no outline on the painted background; the character reads crisp and graphic against a soft, atmospheric ground.

STYLE: ATMOSPHERIC CEL STILL — a flat cel character staged inside a soft, painterly-lit scene with real depth; exactly ONE diegetic light source with a smooth glow and gradient falloff into shadow, gentle bloom, soft focus and light haze for depth, a quiet vignette; calm lived-in staging; NOT flatly/evenly lit, NOT neon, NOT photoreal, NO texture or shading on the character body.
```

## Palette mapping

Palette is a free parameter — bloom works warm (evening lamp), cool (blue night,
grey rain), or bright (morning window). Map any palette as:

- **Ambient base** ← the palette paper, pushed into the scene's dim/unlit level
  (the shadow tone away from the light, not bright paper).
- **Key glow** ← a glow tone near the light source — derive from the accent, or
  from the palette's warmest/brightest member; brightest at the source, falling
  off smoothly.
- **Character ink** ← the structure ink as the character's flat fill / outline.
- **Accent** ← the palette accent, kept saturated only on the character's accent
  part + the light source itself.

Cozy warm default (no palette given): ambient base `#2a2018`, key glow `#e8a24c`,
character ink `#1a1410`, accent tomato `#d9523b`.

PALETTE line: `dim {ambient base hex} in shadow, lifting to {key glow hex} near
the single light source with smooth falloff. Character flat-filled in
{character ink hex}. Accent {accent hex} only on the character's accent part and
the light itself. Soft bloom, light haze for depth, a quiet vignette.`

## Character treatment

The mascot stays a flat cel shape regardless of the lighting around it.
Dark-bodied characters → solid ink body with pale eyes that catch the light;
light-bodied characters → flat pale body, separated from the dim ground by its
bold outline and by catching more of the key glow. The body never receives
painterly shading — at most ONE soft rim of light along the lit edge, nothing
more. The accent part stays the one saturated note.

## Labels

Soft sans lettering in pale-light or the accent, sitting in the dim ambient
zones away from the light — never typeset-sharp, never neon; reads like a title
card on a quiet scene.

## QA deltas (replace the riso grain checks)

- Exactly ONE diegetic light source, with visible glow and gradient falloff — if
  the scene is evenly/flatly lit, it has drifted toward cel/riso; re-roll.
- The CHARACTER is flat — no painterly shading or texture on the body (one soft
  rim of light at most). If the character looks rendered or 3D, re-roll.
- The BACKGROUND is soft, deep, and atmospheric — gradients, bloom, and soft
  focus are allowed and expected HERE (the one look where they're correct).
- No neon and no photoreal detail; the scene reads painted, not photographed.
- Accent appears only on the character's accent part + the light source.

Calibration example (not bundled — fetch the URL):
https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/bloom-pitz.png
— a flat black-cat loaf at a lamplit desk; study it for the crisp-character /
soft-deep-ground contrast and the single-light rule. Never copy its composition
or assume its warm palette is mandatory (bloom works cool and bright too).

Variant note: when deriving a bloom pack from a riso character, the original
clean sheet works directly as the `--ref` — the style prompt overrides scene
rendering, since the character treatment (flat cel) is compatible.
