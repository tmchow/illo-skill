# Quality bar

Check every generated image before delivering. Re-roll or edit on any failure.
The checks below assume the default riso style; when another style is active,
swap the riso-specific checks (grain, halftone, paper) for the **QA deltas in
that style's file** — everything else here still applies.

## Must pass

- Correct aspect ratio; the style's expected ground (riso: light paper with
  the risograph grain; other styles: per their QA deltas — e.g. blueprint's
  deep ground is correct).
- **The mascot is present and performs the move** (passes the load-bearing
  test in `character.md`) — not standing beside the idea.
- **Mascot is on-model**: matches the active character's locked design (the
  default Blot's in `character.md`, or the custom pack's) — two dot eyes,
  blank deadpan (no brow, no mouth), one accent carrier, no added parts.
- **Value matches the palette**: in light palettes the body is light with
  structure-ink (not pure-black) features — not a heavy dark blob.
- One core idea, one structure. Subject large (~50–70%), ≥35% negative space.
- **Labels**: ≤3, short, correctly spelled, structure-ink on bare paper — never
  on a colored fill.
- **Accent discipline**: accent on the character's accent part + 1–2 elements
  only; the body and background are not colored-in with the accent.
- Unified line language across mascot and props (one artist).
- A fresh metaphor — not a copy of an `assets/examples/` composition.
- **Mini-comics**: 2–4 panels, one action per panel, the same mascot and key
  object in every panel, clear left-to-right reading, ≤1 short label per panel.

## Fail signals → fix

- A title bar / type label ("Workflow", "System Diagram", "Roadmap") anywhere → edit it out.
- Mascot reads as a sticker/cute-cartoon, or has a mouth/eyebrows/shiny eyes → re-roll.
- Looks like a slide, infographic, flowchart, or formal diagram → re-roll simpler.
- Too many objects/arrows/nodes; text became sentences → cut to one action + ≤3 labels.
- Gradients, soft shadows, glossy/3D, photo, real UI → re-roll.
- Subject tiny in a sea of paper → re-roll larger (scale drifts run-to-run).
- Accent spread across the body/background, or label text on an accent fill → fix.
- Derived/custom palette colors off-target → eyedrop vs the target hex; re-roll or snap in post.
- Misspelled labels → prefer an edit; if widespread, re-roll with fewer/shorter labels.

## Iteration moves

- Too plain → make the mascot the actor and add one strange-but-valid metaphor.
- Too busy → delete nodes; keep one action and ≤3 labels.
- Too cute → emphasize blank deadpan, no mouth, not a sticker.
- Too "diagram" → drop titles/borders/grids; redraw as a hand-built scene.
- Too similar to an example → keep the idea, swap the object and the action.

## Delivery test

A strong image reads "a bit odd" first, then clicks within ~1 second. If it
reads like a tutorial slide instead of a clean, deadpan scene in the active
style, it is not ready.
