# Phosphor — style pack

Luminous CRT trace: crisp glowing vector strokes on near-black glass, faint
scanlines, a touch of bloom. A look for **character packs** (the pack's
`Style:` line) suited to observability and monitoring, terminals and ops,
incidents and on-call, radar/sonar metaphors — anywhere "watching the signal"
is the right voice.

## Prompt blocks (replace the template's LINE LANGUAGE and STYLE lines)

```text
LINE LANGUAGE: draw EVERYTHING — mascot, objects, arrows — as crisp PHOSPHOR vector strokes of one even weight, glowing softly against the dark screen like an oscilloscope trace; the glow is a tight halo, the line itself stays sharp.

STYLE: CRT PHOSPHOR DISPLAY — luminous trace lines on a near-black screen, very faint horizontal scanlines, subtle bloom around bright strokes, a slight corner vignette, otherwise completely flat; no monitor bezel, no desk, no glass reflections, no photorealism.
```

## Palette mapping

Phosphor inverts the riso grammar: dark ground, luminous line.

- **Screen** ← the structure ink's hue, deepened to near-black (L ≈ 5–9%).
  Neutral/black structure → green-black `#0b100d`.
- **Trace** ← the paper color reimagined as the phosphor: lifted to high
  luminance and saturated toward green — neutral/cream paper → classic P1
  phosphor green `#3fe88e`.
- **Accent** ← the palette accent, brightened until it glows on the dark
  screen (warm accents → amber phosphor reads best).

Classic default (no palette given): screen `#0b100d`, trace `#3fe88e`, accent
amber `#ffb648`.

PALETTE line: `near-black screen {ground hex} with very faint scanlines. All
trace lines {trace hex}, softly glowing. Accent {accent hex} used sparingly —
the character's accent part + 1–2 elements.`

## Character treatment

Every character renders as the same glowing trace — no fills, dark-body rules
collapse to line-on-screen. Eyes are solid glowing dots in the trace color;
the accent part glows in the accent color. State in the CHARACTER block:
"drawn in the same crisp glowing trace as everything else, eyes as solid
trace-color dots, the {accent part} glowing in the accent color — never a
solid filled sprite."

## Labels

Blocky readout capitals in the trace color, hand-traced rather than typeset,
directly on the screen. Never boxed.

## QA deltas (replace the riso grain checks)

- **No bezel, no monitor frame, no desk, no reflections** — the CRT cliché
  the model loves to add. Edit out or re-roll.
- **No dashboard clutter**: no grids of fake numbers, no gauges, no UI
  windows.
- Lines crisp with a tight halo — bloom never washes out a stroke; scanlines
  faint.
- One line weight; accent only on the accent part + 1–2 elements.

Calibration example (not bundled — fetch the URL): https://raw.githubusercontent.com/tmchow/illo-skill/main/_assets/illo/styles/phosphor-spike.png — study it
for line/texture and restraint; never copy its composition.

Variant note: when deriving a phosphor pack from a riso character, the
original sheet works directly as the `--ref` — the style prompt overrides its
rendering.
