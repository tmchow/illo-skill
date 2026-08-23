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
- **Artifact-job test** (especially for standalone heroes/social cards): would
  a stranger understand what this image is introducing or framing without
  nearby prose? If the artifact's job is to introduce, announce, promote, or
  frame a new offering, the primary read must be the role/capability/step-change
  being claimed. A neat picture of the source's internal mechanism is still a
  failure when that mechanism is only evidence for the announcement.
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
  - **Pack-driven face-interior scan:** when the active character pack forbids a
    mouth, muzzle divider, cheek, nostril, or any other interior facial mark,
    inspect a tight face crop at full resolution and judge literal strokes, not
    the intended expression. After accounting for explicitly locked eyes/marks,
    any prohibited line, loop, notch, arc, divider, or construction stroke inside
    the face is a **hard fail**. Do not rationalize it as anatomy, texture, or a
    route/prop line; ambiguous marks fail and must be edited or re-rolled.
- **Structural integrity** — a separate axis from "on-model" (a body can be
  perfectly on-model and still be assembled wrong, so the identity check
  above will not catch this; scan for it deliberately). The one rule that
  covers every case: **only the character's own locked design parts touch its
  silhouette** — limbs, the accent carrier, locked accessories, nothing else.
  Everything else is
  either *clearly connected through a declared contact surface
  (`character.md`, the interaction model) with visible separation from the
  body* or *resting in the scene* (on the table, the ground). Trace the
  outline and check the three ways that breaks:
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
  - **No fused props** — a tool/object connects through a declared contact
    surface (separated from the torso) or sits in the scene; it is never
    pressed flat against the body or sprouting from it. Exception: when the
    character's interaction model declares **body contact as the operating
    mechanism** (a body-press, a load resting against the torso or back),
    judge that contact against the declared surface — deliberate body
    contact is not fusion. Watch the case where
    the mascot is given more props than it has contact surfaces: the extra
    one tends to fuse to the torso — keep operated props to **one per
    contact surface** and let any others rest in the world.
  - **Line topology / collisions** — trace facial strokes and every route-like
    line (wire, arrow, path, ground line, cable) through contacts near the
    character. A stroke must keep one clear owner and readable endpoints. It is a
    hard fail when a facial or route stroke visually fuses into a face, torso, or
    limb, creates apparent extra anatomy, or makes a limb and route read as one
    continuous line. Restore a clear gap/occlusion or re-roll.
  - **In mini-comics, run all four checks on every panel separately** —
    each panel is its own small render and the repeated, smaller mascot
    instances are where these errors drift in most.
- **Value matches the palette**: in light palettes the body is light with
  structure-ink (not pure-black) features — not a heavy dark blob.
- One core idea, one structure. Subject large (~50–70%; explainer images may
  spread ~40–70%), ≥35% negative space.
- **Text hierarchy / labels**: editorial text stays short, correctly spelled,
  structure-ink on bare paper — never on a colored fill. A primary floating
  title is allowed when the artifact job needs a standalone read; it must be
  visibly larger than secondary labels and readable at thumbnail size. Supporting
  labels must remain visibly secondary and not compete with it. If the title
  and labels flatten into equal-weight callouts, or a title is smaller than or
  visually equal to labels, re-roll or simplify.
  (Explainer images use that register's callout budget instead — next bullet.)
- **Title placement** (when a primary title is present): it sits in an
  intentionally reserved field with visible paper around it, inside the safe
  area, and separated from the mascot, props, and labels by a clear gutter. Keep
  it roughly one title-letter height, or at least ~6-8% of the canvas, from the
  nearest frame edge. If the title feels crammed into a corner, nearly touches
  the subject/frame, or steals the only calm negative-space region, re-roll with
  a named title field and a shifted/scaled subject.
- **Explainer register** (only when the shot list declared it): exactly one
  structure type; ≤5 stations, each with a nameable job; ONE main flow
  direction plus at most one return/exception leg; ≤6 short callouts,
  correctly spelled, on bare paper in the semantic ink roles
  (`palettes.md`); the mascot is a working part of the structure, not a
  presenter beside it; still hand-built — no title, border, grid, legend,
  or vector-formal boxes. **Factory flow** (only when that type locked):
  one connected plant, not five editorial islands or a row of disconnected
  props; stations are invented physical objects, not generic rectangles;
  the mascot operates exactly one stage; no formal flowchart; the look
  stayed the pack's — a whiteboard / white-doodle restyle is a fail.
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

## Cutout register (only when the request was a character cutout)

Read `references/cutout.md` for routing. These checks replace the thesis,
load-bearing, label, and negative-space editorial tests — everything else
(on-model, structural integrity, value-follows-palette, accent discipline,
style QA deltas) still applies to the character cluster.

### Must pass

- **Transparent output** — manifest `cutout_alpha` is true (transparent corners
  and sufficient background removal). No visible magenta/green screen fringing at
  the silhouette edge. Interior accent fill is not a fringe fail; when corners
  are transparent and the background is gone, `cutout_alpha` must stay true. When
  `cutout_alpha` is false, do not deliver as a compositing sticker — re-roll,
  switch backend/model, or disclose honestly (see `cutout_note`).
- **Full body framing** — feet/base fully visible, not cropped by the frame; clear
  margin below the feet (same structural-integrity bar as editorial limbs). The
  engine flags likely crops in `cutout_note` ("character touches the bottom frame
  edge") even when `cutout_alpha` is true — treat that as a re-roll signal.
- **No text** — no labels, captions, watermarks, numbers, or hand-lettering
  anywhere.
- **Contact continuity** — every opaque pixel is the character or in direct
  contact (held, sat on, stood on, leaned on/touched); no orphaned objects at
  a distance; no horizon, wide floor, or full-room furniture.
- **Minimal contact fragments** — table/sofa/wall shows only the touched part,
  not a whole scene prop extending into empty space.
- **On-model** — same locked-design checks as editorial.
- **Structural integrity** — same limb/prop attachment checks, scoped to the
  cutout cluster.
- **One compositing unit** — reads as one sticker, not a cropped illustration.
- **Pose matches the ask** — gesture, facing, and attitude match what was
  requested (or the agent's inferred pose when the prompt was thin).
- **Idle-loop GIFs** — after this cutout QA, run `references/cutout.md`, "Idle
  loop / bot avatar" on the source cutout, rest/peak-motion/blink-or-other
  changed frames, and final GIF.

### Fail signals → fix

- Green or magenta bleed on a chroma-rendered silhouette → re-roll with the
  **other** `--chroma` screen (see `references/cutout.md`); check `--cutout`
  was passed. Do not hand-write a `BACKGROUND:` line — the engine appends it.
- Halo/fringe on a native-alpha Codex result → re-roll once with the
  registration-locked prompt; if it persists, force `--chroma` compatibility
  and inspect the result again.
- Edge-only accent-colored halo tracing the outer contour (riso
  misregistration) → re-roll with the **registration-locked SILHOUETTE** block —
  no ink-layer offset on cutouts (`references/prompt-recipe.md`, "Cutout
  variant"). Interior accent fill and compact locked accent carriers that touch
  air are correct on-model, not halos.
- Feet or base cropped by the frame → re-roll; check the Composition line names
  full body and margin below the feet.
- A separate object sits near but not touching the character → re-roll
  pose-only or rebuild contact.
- Full table, sofa, or floor plane → re-roll with "only the contacted fragment."
- Any text → edit out if tiny; else re-roll.
- Ask clearly needs a scene or idea → not a cutout failure — reroute to editorial.

## Fail signals → fix

- A title bar / type label ("Workflow", "System Diagram", "Roadmap") anywhere → edit it out.
- A standalone announcement/hero image has only mechanism labels and no clear
  primary read for the thing being introduced → re-route as an editorial hero
  with a primary title or stronger role/step-change scene, then re-roll.
- A primary title is technically present but jammed against the edge, clipped,
  tangent to the subject, or crowding the visual action → re-roll with reserved
  title space and fewer/smaller supporting labels.
- Mascot reads as a sticker/cute-cartoon, or shows face details its locked
  design doesn't name → inspect the tight face crop and re-roll. For a pack that
  forbids facial interior marks, any mouth-like loop/line, cheek/muzzle/nostril
  mark, or construction stroke is a hard fail regardless of apparent intent.
- Looks like a slide, infographic, flowchart, or formal diagram → re-roll
  simpler. (In the explainer register the fail is *formality* — vector-clean
  boxes, a legend, a grid, a boxed title — not the presence of arrows and
  stations; redraw hand-built, don't strip the structure.)
- A factory flow that reads as disconnected islands, generic rectangles,
  the character working two stages, a formal flowchart, or a look
  switched to a whiteboard / white doodle → restage the bind or the
  operator stage (`composition.md`, factory flow pack-solve), then
  re-roll. Do not "fix" it by changing the look.
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
  doubled/floating, or a prop is fused flat to the torso instead of
  connected through a declared contact surface (declared body contact is
  not fusion — see the exception above) → re-roll (these resist edits; a
  fresh render is cleaner). If the re-roll
  keeps fusing a prop, the scene likely has more tools than contact
  surfaces — drop one or rest it on the table.
- Accent spread across the body/background, or label text on an accent fill → fix.
- Derived/custom palette colors off-target → eyedrop vs the target hex; re-roll or snap in post.
- Misspelled labels → prefer an edit; if widespread, re-roll with fewer/shorter labels.

## Topology failure response

Not every structural failure is random drift — distinguish the two before
spending the next render. When a failed render's contact geometry was itself
infeasible — a limb stretched past its reach class, undeclared grip anatomy
(invented fingers/hands), a prop or route crossing the body or face
where the interaction model declares no such contact,
ambiguous stroke ownership near the face or torso — the pose is the problem:
re-stage immediately through the feasibility gate (`composition.md`) rather
than re-rolling the same prompt. If one clean re-roll repeats the same
topology failure, changing the physical move is **mandatory**; appending
more negative constraints to the same pose is not an acceptable third
attempt.

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
