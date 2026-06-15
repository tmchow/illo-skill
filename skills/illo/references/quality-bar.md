# Quality bar

Check every generated image before delivering. Re-roll or edit on any failure.
The checks below assume riso; when the active character's style isn't riso,
swap the riso-specific checks (grain, halftone, paper) for the **QA deltas in
its style's file** — everything else here still applies.

## Must pass

- **Thesis test** (do this first): cover the labels and ask what one idea a
  stranger would name. It must be *this image's locked thesis*
  (`composition.md`, Source routing step 2 — for a set member, its own
  section's lock), not a side activity the scene happens to depict. If the
  picture lands a supporting anecdote while the thesis was an abstract claim
  (a quality, a step-change, a role shift), it failed — re-roll toward the
  thesis via a role/scale/relationship move, don't ship the drawable detail.
- **Source-fit test** (for source-derived images, before re-rolling
  anything): was the locked thesis the *right compression of the source*?
  An image can perfectly land its lock and still be wrong if the lock
  itself was a supporting mechanism, not the source's rhetorical job — a
  launch post heroed as one debugging anecdote, a postmortem heroed as one
  incident. Apply the genre guardrails (`composition.md`): does the hero
  match what this genre should hero? If not, **re-route, then re-roll** —
  fix the lock first; do not keep iterating a well-rendered wrong thesis.
- Correct aspect ratio; the style's expected ground (riso: light paper with
  the risograph grain; other styles: per their QA deltas — e.g. blueprint's
  deep ground is correct).
- **The mascot is present and performs the move** (passes the load-bearing
  test in `character.md`) — not standing beside the idea.
- **Mascot is on-model**: matches the active character's locked design (the
  default Blot's in `character.md`, or the custom pack's) — the locked face
  exactly (house default: two dot eyes, blank deadpan, no brow, no mouth),
  every locked part present, locked treatments reading in aggregate, one
  accent carrier, nothing the spec doesn't name.
- **Structural integrity** — a separate axis from "on-model" (a body can be
  perfectly on-model and still be assembled wrong, so the identity check
  above will not catch this; scan for it deliberately). The one rule that
  covers every case: **only the character's own locked design parts touch its
  silhouette** — limbs, the accent carrier, locked accessories, nothing else.
  Everything else is
  either *clearly held in a hand with visible separation from the body* or
  *resting in the scene* (on the table, the ground). Trace the outline and
  check the three ways that breaks:
  - **Occlusion / opacity** — nothing from behind passes *through* the body.
    A ground line, horizon, table edge, belt, shelf, or prop must **stop at
    the silhouette**, not cut across the waist/torso. The mascot (and every
    solid object) is opaque and sits in front of what's behind it. A line
    through the body is the most common miss because the character still
    "looks like itself."
  - **Anatomy / attachment** — trace each limb to where it joins: exactly
    the character's limb count (no extra, floating, doubled, or merged
    arms/legs), each rooted at a sensible point on the body, not emerging
    from mid-torso or an accent band. Limb **proportions** must match the
    character sheet: a stubby arm cannot become a long bar, cable, lever, or
    bridge across the scene. For one-arm / handle characters, the handle is
    never a second hand and the working arm must stay visually short.
  - **No fused props** — a tool/object is held in a hand (separated from the
    torso) or sits in the scene; it is never pressed flat against the body
    or sprouting from it. Watch the case where the mascot is given more
    props than it has hands: the extra one tends to fuse to the torso — keep
    held props to **one per hand** and let any others rest in the world.
  - **In mini-comics, run all three checks on every panel separately** —
    each panel is its own small render and the repeated, smaller mascot
    instances are where these errors drift in most.
- **Value matches the palette**: in light palettes the body is light with
  structure-ink (not pure-black) features — not a heavy dark blob.
- One core idea, one structure. Subject large (~50–70%; explainer images may
  spread ~40–70%), ≥35% negative space.
- **Labels**: ≤3, short, correctly spelled, structure-ink on bare paper — never
  on a colored fill. (Explainer images use that register's callout budget
  instead — next bullet.)
- **Explainer register** (only when the shot list declared it): exactly one
  structure type; ≤5 stations, each with a nameable job; ONE main flow
  direction plus at most one return/exception leg; ≤6 short callouts,
  correctly spelled, on bare paper in the semantic ink roles
  (`palettes.md`); the mascot is a working part of the structure, not a
  presenter beside it; still hand-built — no title, border, grid, legend,
  or vector-formal boxes.
- **Accent discipline**: accent on the character's accent part + 1–2 elements
  only; the body and background are not colored-in with the accent.
- Unified line language across mascot and props (one artist).
- **Sets read as one artist too**: across a multi-image set, line weight,
  halftone density, and flat-vs-dimensional treatment stay consistent — an
  outlier re-rolls with the set's style anchor (a QA-passed set member) as a
  second `--ref`.
- A fresh metaphor — not a copy of a calibration example's composition.
- **Mini-comics**: 2–4 panels, one action per panel, the same mascot and key
  object in every panel, clear left-to-right reading, ≤1 short label per panel.

## Fail signals → fix

- A title bar / type label ("Workflow", "System Diagram", "Roadmap") anywhere → edit it out.
- Mascot reads as a sticker/cute-cartoon, or shows face details its locked
  design doesn't name (for house-face packs: any mouth/eyebrows/shiny eyes) → re-roll.
- Looks like a slide, infographic, flowchart, or formal diagram → re-roll
  simpler. (In the explainer register the fail is *formality* — vector-clean
  boxes, a legend, a grid, a boxed title — not the presence of arrows and
  stations; redraw hand-built, don't strip the structure.)
- Too many objects/arrows/nodes; text became sentences → editorial: cut to
  one action + ≤3 labels; explainer: cut to ≤5 stations + ≤6 callouts, one
  flow direction.
- An explainer's arrows run in multiple directions, or a station has no
  nameable job → cut legs/stations until the structure traces cleanly.
- A callout appears twice, stray text/numbers/a hex code is lettered into
  the art, or a return leg's arrowhead points the wrong way → edit out if
  small, else re-roll (and check the prompt kept hexes out of the CALLOUTS
  line). The flow arrows must actually wear the flow ink — reference-sheet
  conditioning can drag the accent back to the character sheet's hue;
  off-palette accents re-roll or snap in post.
- Gradients, soft shadows, glossy/3D, photo, real UI → re-roll.
- Subject tiny in a sea of paper → re-roll larger (scale drifts run-to-run).
- A line passes through the mascot's body, a limb roots wrong / is
  doubled/floating, or a prop is fused flat to the torso instead of held →
  re-roll (these resist edits; a fresh render is cleaner). If the re-roll
  keeps fusing a prop, the scene likely has more tools than hands — drop one
  or rest it on the table.
- Accent spread across the body/background, or label text on an accent fill → fix.
- Derived/custom palette colors off-target → eyedrop vs the target hex; re-roll or snap in post.
- Misspelled labels → prefer an edit; if widespread, re-roll with fewer/shorter labels.

## Iteration moves

- Too plain → make the mascot the actor and add one strange-but-valid metaphor.
- Too busy → delete nodes; keep one action and ≤3 labels.
- Too cute → strip face details the locked design doesn't name (the house
  deadpan resists this best), not a sticker.
- Too "diagram" → drop titles/borders/grids; redraw as a hand-built scene.
  If an editorial image keeps wanting arrows back, re-check the register
  gate (`composition.md`, "Two registers") before stripping — the thesis
  may be a structure that belongs in the explainer register.
- Too similar to an example → keep the idea, swap the object and the action.

## Delivery test

A strong image reads "a bit odd" first, then clicks within ~1 second. If it
reads like a tutorial slide instead of a clean, deadpan scene in the active
style, it is not ready.
