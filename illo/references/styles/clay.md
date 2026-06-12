# Clay — style pack

Stop-motion plasticine: matte hand-modeled clay forms on a paper-craft set,
soft studio light, small contact shadows. A look for **character packs** (the
pack's `Style:` line) — the library's only dimensional look — suited to
product stories, warm explainers, team/culture pieces, anything that wants
handmade charm instead of print edge.

**Known failure mode (why this file is strict):** flat source art fights the
modeled look — the set renders in clay but the mascot stays a flat drawing
pasted in. A clay pack's model sheet must itself be clay-built (born that way
in the builder, or derived as a variant — `references/character-builder.md`,
"Style variants"). The CHARACTER forcing line below is mandatory in every
prompt; a flat mascot is an automatic re-roll.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: build EVERYTHING — mascot, objects, props — as smooth hand-modeled CLAY forms with softly rounded edges and a few subtle fingerprint dents; NO drawn outlines anywhere — shapes separate by color and soft light, like a stop-motion set.

STYLE: STOP-MOTION CLAYMATION diorama — matte plasticine figures on a clean paper-craft set, soft even studio lighting, small soft contact shadows, handmade and slightly imperfect; NOT a glossy 3D render — no plastic sheen, no photorealism, no depth-of-field blur.
```

## Palette mapping

- **Set** ← the palette paper, as a seamless paper-craft backdrop and floor.
- **Main clay** ← the structure ink, lifted from line-ink to a clay material
  color (keep its temperature; near-black structure → warm charcoal clay).
- **Accent clay** ← the palette accent, matte.

Secondary props stay in muted tints of the set color so the character owns
the frame.

Classic default (no palette given): set `#ece4d4`, main clay `#36322c`,
accent clay `#e8543f`.

PALETTE line: `a seamless paper-craft set in {paper hex}. Main clay
{structure hex} for the character (per its value rule) and key objects;
secondary props in muted tints of the set color. Accent clay {accent hex}
only on the character's accent part + 1–2 elements.`

## Character treatment

The reference supplies proportions and identity only — the rendering is
re-modeled in clay. Append to the CHARACTER block: "the mascot itself is a
hand-modeled matte clay figure exactly like every other object in the set —
never a flat drawing or sticker placed into the scene." Value rules map to
material color: dark-capable characters → main-clay body with light clay-bead
eyes; light-bodied characters → set-toned clay body with main-clay bead eyes.
The accent part is modeled in the accent clay.

## Labels

≤2 short hand-lettered capitals painted flat in the main-clay color directly
on the set backdrop — never modeled as clay letters (sculpted type mangles).

## QA deltas (replace the riso grain checks)

- **The mascot is clay.** A flat/drawn mascot on a clay set = re-roll (the #1
  failure).
- **Force the accent hue in words next to the hex** ("coral red #e8543f —
  NOT yellow, NOT brown"): material renders drift accent color toward toy
  defaults. Wrong-hue accent = re-roll.
- Matte everywhere: no glossy highlights, no plastic or 3D-render sheen.
- Small soft contact shadows only — no dramatic lighting, no depth-of-field
  blur.
- No drawn outlines; fingerprint texture subtle, never sculpted detail creep.
- Accent clay appears only on the accent part + 1–2 elements.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/clay-rootcause.png — study it
for line/texture and restraint; never copy its composition.
