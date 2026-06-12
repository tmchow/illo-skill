# Manila — style pack

Vintage office paperwork: flat rubber-stamped ink on a manila-folder ground,
dry edges, slight misalignment. A look for **character packs** (the pack's
`Style:` line) suited to approvals and sign-off, process and checklist
pieces, compliance and audit content, bureaucracy humor — anywhere "it went
through the office" is the right voice.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: draw EVERYTHING — mascot, objects, arrows — as flat RUBBER-STAMPED impressions: one chunky stamp-cut line with dry, unevenly inked edges, pressed by hand so elements sit at slightly different angles; one or two small ink blotches are welcome.

STYLE: VINTAGE OFFICE PAPERWORK — stamped ink on a manila folder ground, dry-ink texture with faint paper fiber, each element slightly rotated or misaligned like separate hand stampings, completely flat, no gradients, no photorealism, no typed or printed documents.
```

## Palette mapping

- **Ground** ← the palette paper, warmed and deepened to manila buff.
- **Stamp ink** ← the structure ink, deepened toward office blue-black while
  keeping its temperature.
- **Accent ink** ← the palette accent as the "second stamp" — classic stamp
  red — pressed slightly off-angle.

Classic default (no palette given): manila `#e6c992`, stamp ink `#23303d`,
accent red `#c8372d`.

PALETTE line: `manila paper ground {paper hex}. Stamp ink {structure hex} for
all linework, forms, and label text. Accent ink {accent hex} used sparingly,
stamped slightly off-angle — the character's accent part + 1–2 elements.`

## Character treatment

Manila maps the riso value rules natively:

- Dark-capable characters → body stamped solid ink, eyes left as bare manila.
- Light-bodied characters → manila body with a chunky stamped outline, ink
  eyes.

The accent part reads as a second stamping in the accent ink, allowed to sit
a few degrees off-angle.

## Labels

Stamped capitals in the ink color directly on the manila — uneven baseline
and slightly patchy inking, like an office stamp, never typeset.

## QA deltas (replace the riso grain checks)

- Dry stamped edges, faint paper fiber — **no halftone dots, no smooth
  digital curves, no gray midtones.**
- Slight rotation/misalignment of stamped elements is correct — don't "fix"
  it.
- **No typed text, no printed forms, no ruled lines or checkbox grids, no
  barcodes, no date stamps with digits** — the office clichés the model
  loves.
- **Stamps attract type**: the model stamps stray words — even hex codes from
  the PALETTE line — onto any paper sheet in the scene, and migrates labels
  onto the sheets. State that in-scene papers stay blank (marks are plain
  filled shapes, nothing inside) and float labels in empty manila, well clear
  of the sheets. Stray writing = re-roll.
- ≤2 accent elements beyond the character's accent part.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/manila-queue.png — study it
for line/texture and restraint; never copy its composition.

Variant note: when deriving a manila pack from a riso character, the original
sheet works directly as the `--ref` — the style prompt overrides its
rendering.
