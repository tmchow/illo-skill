# Composition

One picture, one idea — turned into a single physical thing the mascot is
caught doing, in a small slightly-wrong machine-world, with quiet space around
it.

## Two registers

Every image is made in one of two registers. The methodology — thesis lock,
shot list, load-bearing mascot, QA loop — is identical in both, and the look
and palette stay whatever the character pack and `palettes.md` resolve; the
register only sets which image grammar is allowed.

- **Editorial** (the default) — one caught scene: a physical move on one or
  two built objects, meaning implied, no diagram machinery. Everything in
  "Turn the idea into a move" and the stagings below.
- **Explainer** — a hand-built sketch-diagram: stations, one flow direction,
  callouts — for when the reader must be able to *trace* the structure, not
  just feel it. Rules in "The explainer register" below.

Before choosing the register, infer the **artifact job**: what the requested
image is supposed to do for its audience in the place it will be seen. This is
not a keyword match; read the user's intent, destination, and source context.
Some images are meant to explain a mechanism, but others are meant to introduce,
promote, frame, or make a new offering legible as a standalone hero/poster. A
standalone introduction or announcement heroes the role, capability, or
step-change being claimed; mechanisms from the source become props, secondary
actions, or small supporting labels. Do not route such an image to explainer
just because the source contains a traceable process.

Editorial wins every tie. Route an image to explainer only when:

- **(a) the user asks for it** — "show the flow", "diagram the pipeline",
  "map the steps", "make it traceable", "as an explainer", or names /
  describes / alludes to a diagram type ("as labeled stages", "like that
  factory diagram"; specified flowchart / labeled-workflow /
  process-diagram intention locks labeled stages; full precedence in
  "Pick the diagram type"); or
- **(b) the unit's locked thesis IS a traceable structure** — its point
  lives in the stations and their connections (a named pipeline or
  labeled stages, a fan-out, a timeline, a loop, a layered stack), and one
  caught moment would force the reader to take the structure on faith.

A process that is merely *evidence* for a different lock stays editorial —
the lock is the arbiter, exactly as in Source routing step 2. Genres that
most often qualify: how-to / process and systems / architecture pieces.
Opinions, quotes, launches, and anecdotes stay editorial: their theses are
claims, not structures. Like the mini-comic, the explainer is a deliberate
choice, never a fallback — and a set may mix registers (an editorial hero
over explainer anchors is a natural article shape). Labeled stages is a
structure type *inside* this register, not a third register and not a
new look.

## Turn the idea into a move

Start from the one sentence the picture has to land, then find the **physical
move** that embodies it — something the mascot can be mid-action on. Push the
abstract into the concrete: "we ship too slowly" → the mascot cranking a press
that drips a single parcel; "we're buried in inputs" → the mascot bailing a
bucket that keeps overflowing. The move *is* the picture; until the move has
a name, there is no image yet.

Give the move a **built thing to happen on or in** — a low-tech, faintly-broken
machine, container, or rig that the move implies. Invent it for this idea rather
than pulling from a stock set, and keep it to one or two objects, never a
cluttered bench.

Then put **the mascot in the move** — wedged in it, cranking it, plugging it,
hauling across it — never posed politely beside it (see the load-bearing test
in `character.md`). Locked silhouette and body proportions are
non-negotiable in every register, not only X Article banners. Dramatize
scale by changing the **world** — a too-small door, a tiny hatch, an
oversized pile — never by stretching, squashing, or flattening the mascot
to fill architecture or the frame. "Subject large and confident ~50–70%"
is occupancy in the frame, not a license to distort the body.

## Anatomy-action feasibility gate

Before locking the move, map every required contact to a part the active
character actually has — its interaction model (`character.md`). Write the
map as one line per contact:

```text
character part -> object part -> contact location -> resulting motion
```

including a support line (what bears the weight) and where every inactive
limb rests. Example — the move "drive the press":

```text
right foot -> pedal  -> below body -> drives the press
left foot  -> ground -> below body -> supports weight
both arms  -> no contact -> low at the sides, outside the machine
```

The gate applies in **both registers**: an explainer's mascot move — its
station, jam, sorter, or hauler role — maps its contacts the same way
before the structure locks. Labeled stages pack-solves to **one** operator
stage first ("Labeled stages — skeleton, then pack-solve"), then this gate
runs on that one contact map. Confirm each active part is a declared contact
surface, can plausibly reach the contact without changing its locked
silhouette or body proportions, and that no object or route must cross a
protected region or fuse with the body. A move that only reads if the
body fills a door, hatch, or frame is a failed map — shrink or enlarge
the world object; do not squash the mascot. **Re-stage — a
different verb, object, orientation, or contact method — instead of
prompting harder** when the map fails: a required surface the pack doesn't
declare (undeclared fingers, hands, joints), a contact beyond the reach
class, more simultaneous contacts than the character has surfaces, a route
through the face, ambiguous stroke ownership near the face or torso, a
move that only works by fusing the object into the body, or a pose that
only works by stretching or flattening the locked body. A load-bearing
move must be both conceptually necessary and physically drawable by this
character.

The validated map becomes the prompt's INTERACTION GEOMETRY block
(`prompt-recipe.md`) and is the standard QA judges topology against
(`quality-bar.md`).

## Stagings that tend to land

Reach for whichever fits; these are starting angles, not a taxonomy to label on
the image:

- **A contraption** — one absurd machine that performs the idea: small input, one output.
- **A change** — the same scene in two states (jumbled → settled, by-hand → automatic).
- **A throughput** — something travels left-to-right and is transformed on the way.
- **A snag** — the whole thing jams at a single point, and the mascot is usually the jam.
- **A build-up / drain** — it stacks, fills, leaks, or empties over time.
- **A crossing** — a gap, gate, ramp, or threshold the mascot moves something over.
- **A mini-comic** — 2–4 small panels inside ONE image, read left to right, one
  action per panel; the mascot and the key object carry through every panel so
  it reads as the same moment advancing (stuck → small slice → shipped).

Blend sparingly; one clear staging beats two muddled ones. Across a set, vary
the stagings — two adjacent images shouldn't lean on the same staging or
metaphor family.

## Pick the diagram type

Once the thesis is locked, pick the diagram type from that lock. The user
can override. An allusion is enough. After the type locks, do not rotate
it for variety.

Specified intention locks the type even when the thesis would have stayed
editorial. If the user names, describes, or alludes to a flowchart, a
labeled workflow, or a process diagram, lock labeled stages. That is
intention — not a closed synonym list, and not a keyword scan of "flow"
or "workflow". After the type locks, do not rotate it. The ban on
boxes-and-diamonds / Visio / title-legend-grid formality is a **look**
constraint: produce labeled stages in the pack's look; do not refuse the
word flowchart.

Override precedence (highest wins):

1. The user **names** a type — "as labeled stages", "label the steps",
   "walk the stages", "timeline", "loop", "fan-out", "stack",
   "as an explainer", "mini-comic", "just the scene".
2. The user **describes** a type — "swim the stages", "one machine with
   windows". Specified intention includes (examples, not a closed list)
   "as a flowchart", "labeled workflow".
3. The user **alludes** to a type — "like that factory diagram".
4. The agent default from the thesis map below.

A named or alluded type locks both the register (when the type is a
diagram) and the type. "As an explainer" locks the register only — then
the map (or a more specific name) picks the structure. "Mini-comic" and
"just the scene" lock those editorial shapes and skip the diagram.

Default only when the user did not steer. Labeled stages is BEST when
the thesis IS a named pipeline, recipe, or staged process — nameable
stations in order, one connected system. Do not force labeled stages on
every explainer, and do not force explainer on a process that is merely
evidence for a different lock.

- A named pipeline, recipe, or staged process → **labeled stages** (inside
  explainer): named phases in order, one connected system, in through
  named stops then out, optional reject and/or return. The world is
  invented from the thesis and the pack.
- A split or sort → **fan-out**
- Order or history → **timeline**
- A cycle or feedback as the point → **loop**
- Layers / a capability stack → **layer stack**
- A few connected parts, no single direction → **system slice**
- A story beat (fail→fix, before→after) → **mini-comic**, not a diagram
  (the existing editorial shape)
- A claim you can feel in one move → **editorial**, not a diagram
- NEVER labeled stages unless the user specified that type: a claim you
  can feel in one move; opinions, quotes, launches, anecdotes; a story
  beat that is fail→fix / before→after (mini-comic); a split/sort
  (fan-out); a cycle as the point (loop); layers (stack). Editorial
  still wins every tie.
- If two types fit, pick the one that makes the stations nameable
- If none fit, do not force a diagram — editorial wins the tie, as in
  "Two registers"

The register gate still applies: user asks, or the thesis IS a
traceable structure. Do not invent a look to "read as a diagram" —
the pack's existing style draws whatever type locks.

## The explainer register

One structure, drawn as a hand-built sketch the mascot is working inside —
never a presenter beside a chart. The grammar editorial forbids (arrows,
stations, a path) is the working material here; what stays forbidden is the
*formal* version of it: no title, no border, no grid, no legend, no
boxes-and-diamonds flowchart formality. That formality ban is a look
constraint — not a refusal of the word flowchart. A specified flowchart
intention still draws labeled stages in the pack's look. The result must
still read as one artist's hand-built drawing in the active look.

Structure types — pick ONE (these are the explainer's stagings; an explainer
shot-list row names one of these in its staging slot). Labeled stages is
the staged, labeled form of a workflow; the other types stay as they are.

- **Labeled stages** — a staged, labeled workflow: named phases in
  order, one connected system, in through named stops then out,
  optional reject and/or return. Lock the skeleton and run the
  pack-solve below before drawing. The world is invented from the
  thesis and the pack — a factory only when the thesis is a factory.
- **A flow** — 3–5 stations left to right on one flow line; the
  transformation is visible station to station. Use labeled stages when
  the stages are a named pipeline or recipe, or when the user specified
  a flowchart / labeled-workflow / process-diagram intention. Do not
  treat that ask as this looser unlabeled flow.
- **A fan-out / sort** — one source, the mascot routing, 2–4 labeled
  destinations.
- **A timeline** — one axis, 3–5 beats with short callouts; the order or
  the spacing is the message.
- **A loop / route** — a path with a few stops that visibly returns or
  arrives; the return leg is drawn, not implied.
- **A layer stack** — 3–4 informally stacked layers (hand-piled, never a
  formal pyramid), the mascot building, carrying, or wedged under one.
- **A system slice** — 3–5 connected parts of a system, the mascot
  operating the one that matters.

Budget (replaces the Restraint section's editorial numbers for this image):

- **Stations ≤5**, each with a job a reader can name — a station that
  explains nothing is clutter, and each is an invented physical thing in
  the scene's world (a drawer cabinet, a press, a well — never a generic
  rectangle).
- **One main flow direction**, drawn as simple hand-drawn arrows in the
  flow ink (semantic roles: `palettes.md`); at most one return or
  exception leg.
- **Callouts ≤6**, 1–4 short words each, two jobs: **station names**
  (short, on the stations — where you are) and **arrow notes** (a verb
  or condition ON the arrow — what happens between). Hand-lettered
  directly on the bare paper/ground or on/along the arrow in the flow
  ink — semantic ink roles per `palettes.md`, never on a colored fill.
  Don't caption a station twice. Suggested split when the type is
  labeled stages: ~3 station names + up to 2 arrow notes.
- **The mascot is a working part** of the structure — a station, the jam,
  the sorter, the hauler between stops — and passes the same load-bearing
  test (`character.md`) and the anatomy-action feasibility gate (above).
- Negative space floor stays (≥ ~35%); the structure may spread wider than
  an editorial subject (~40–70% of the frame) but keeps one calm region.
- The fresh-metaphor rule applies unchanged: reinvent the structure's
  objects per piece; never recycle a previous diagram.

Sequence routing changes inside this register: a progression that would be a
mini-comic in editorial is drawn as the flow itself here. Panels are
editorial machinery — never mix panels and flow arrows in one image.

**Labeled stages — skeleton, then pack-solve.** One connected system —
not five editorial islands, not a formal boxes-and-diamonds flowchart
look, not a title / legend / grid. The look stays the pack's: draw the system
in riso, woodcut, clay, or whichever style the character already wears.
Do not switch to a white doodle or whiteboard look to "read as a
diagram." Do not default the world to a plant, a belt, or a hopper —
invent it from the thesis and the pack. A factory is a metaphor only
when the thesis is a factory.

Lock this skeleton (content, style-agnostic) **before** drawing:

- Input
- 3–5 named stages (the thesis)
- Output(s)
- Optional reject and/or return

Stations are invented physical objects in the scene's world — never
generic rectangles. One main flow direction. Callout budget stays the
explainer budget above (≤5 stations, ≤6 callouts, 1–4 words).

**Arrow notes.** A second text job, not more plaques. Station names sit
on the stations (where you are). Arrow notes sit ON the arrow (what
happens between): the main flow arrow gets one verb; the return/reject
arrow gets one condition. Suggested split: ~3 station names + up to 2
arrow notes — still ≤6 total, each 1–4 words. Hand-letter arrow notes
on or along the arrow in the flow ink. Never a legend, a title bar, or
captioning every station twice. Mute arrows (all plaques, no notes) and
paragraph arrows both fail.

**Pack-solve (required before the prompt).** Each character pack is
different. Reason from this body; do not template one factory. Write a
short internal scratch — stage list → operator stage → contact map →
bind — then the image prompt:

1. Read the active pack's `## Interaction model` (or derive
   conservatively from the locked design per `character.md`): contact
   surfaces, reach, grip, protected regions.
2. Pick ONE stage this body can actually operate. Examples: Blot
   (stubby, pressure/contact, no fingers) → a pedal, a press, a jam. A
   long-armed pack → haul between stations. A no-limb / body-contact
   pack → *be* the jam or the vessel. Prefer body-weight, pressing,
   carrying, leaning over invented dexterity.
3. Every other stage is a world object that MUST NOT require that
   character's hands or undeclared contacts.
4. Bind the stages into one connected system — not a row of
   disconnected props. Invent the bind from the thesis and the pack.
5. Run the anatomy-action feasibility gate (above) on the ONE contact
   map. If it fails, restage the verb or which stage the mascot works —
   not the thesis, not the stage names.
6. Draw the system in the pack's existing look and palette.

Then write the explainer prompt (`prompt-recipe.md`) from that scratch.

## Source routing (URLs, articles, threads, long posts) — before any prompt

For any URL, pasted article, newsletter, thread, or long post, never
generate from the first vivid detail — that produces an image of a
*subclaim* while the piece's actual point goes unillustrated. Route in
three steps, before writing any prompt:

**1. Classify the source — shape *and* genre** (internally — no need to show
the user). Shape sizes the coverage: single-claim short post · multi-claim
short post · long article / newsletter · procedural sequence or thread.
Genre sets the hero logic: launch / announcement · failure report /
postmortem · quote · how-to / process · benchmark / comparison · personal
anecdote · opinion / argument. Genre matters because each one heroes a
different thing (the **Genre guardrails** below) — the same vivid detail
that's the headline in one genre is a supporting prop in another.
Also classify the requested artifact's job: is this image meant to introduce
the whole thing as a standalone opener/social card, support a section inside a
piece, explain a mechanism, or provide a reusable visual asset? Let that job
shape the hero and the text hierarchy. A launch source can contain a process,
but if the requested artifact is a hero/announcement, the process is evidence
unless the source's actual promise is the process itself.

**2. Lock the thesis — per coverage unit, not once per piece.** Write one
sentence before any prompt: *"This image must communicate: \<thesis>."*
The thesis is scoped to the unit you are about to draw, and every image
gets its own:

- A **single image / hero** locks the *whole piece's* thesis. A launch
  post listing six improvements is about the step-change they add up to
  ("runs farther with less steering"), not about whichever list item
  stages best.
- A **set member** locks *its own section's* thesis — what that section
  turns on — analyzed fresh, never sliced off the piece summary. Four
  sections with four different angles must produce four different images;
  if they all restate the headline, the per-section locks weren't done.

**A hero locks the source's *job*, not its loudest evidence.** Separate
three things the source contains and do not confuse them: the **rhetorical
job** (what the author wants the reader to believe or feel), the **primary
claim** (the one sentence that job reduces to — this is the hero thesis),
and the **supporting mechanisms** (the concrete anecdotes/details that
*prove* the claim). A load-bearing moment is usually a *supporting
mechanism* — load-bearing for the argument, but evidence, not headline. It
earns a spot as a **prop or secondary action** in the hero, or its own
anchor in a set — never the hero itself, unless the source's job genuinely
*is* that mechanism (a post whose whole point is "measure, log, verify"
heroes measure/verify; a launch post that merely *mentions* careful
debugging does not). The classic miss: heroing the most drawable mechanism
while the source's actual job — a role shift, a verdict, a warning — goes
unillustrated.

Then **draw the locked thesis, not the most drawable thing near it.** The
trap: the most *illustratable* moment is usually a supporting anecdote,
not the thesis — a concrete process (measure → log → verify) pictures in
one second while an abstract claim (judgment, taste, a step-change, "now a
partner not a tool") resists. The easy picture is bait. When the thesis is
abstract, do not retreat to whatever concrete activity the piece happens
to describe; turn the abstract claim into a **role / scale / relationship
move** — tool→partner (climb out of the toolbox, pull up a chair),
rung→higher rung, follows-orders→exercises-taste — the same "turn the idea
into a move" discipline applied to a quality claim, with the leftover
mechanisms tucked in as small evidence props.

**"Subclaim" is relative to the unit's own thesis.** Drawing a section's
point is correct for that section's image even though it's a "supporting
detail" of the whole — the subclaim filter rejects only what is smaller
than *this unit's* lock, never a section image for being smaller than the
article. **A process is the subject when it IS the locked thesis** (an
article section "how X deploys", a how-to whose point is the steps →
mini-comic), and bait when it is merely evidence for a different lock (the
debugging anecdote under a "it's a thinking partner now" thesis). The lock
is the arbiter; the shape rules below then carry whatever it named.

For multi-beat sources, pull the 3–7 load-bearing moments (criteria in the
shot-list section below) before locking each.

**Genre guardrails — what each genre heroes** (the rest become props or
set anchors):

- **Launch / announcement** → the new role, capability, or step-change
  being claimed (the product/person/model *crossing into* what it now is).
  Benchmarks, demos, and debugging anecdotes are supporting props.
- **Failure report / postmortem** → the failed premise, the broken loop,
  or the final outcome; individual incidents support it, not replace it.
- **Quote** → the abstract relationship the quote names. Avoid an author
  portrait or literal quote text unless the user asks.
- **How-to / process** → the transformation it produces; a mini-comic only
  when the *sequence itself* is the point (meaning lives between the steps).
- **Benchmark / comparison** → the contrast or threshold crossed, not a
  generic chart (charts are the forbidden register).
- **Personal anecdote** → the felt realization if that's the point; the
  event only if the event is the point.
- **Opinion / argument** → the claim's consequence or the thing it
  overturns, not a neutral depiction of the topic.

Do not bake a product/person/model *name* into the image unless the user
asks for the text — hero the role or claim, not the wordmark.

**3. Decide coverage — and ask once when it's both ambiguous and costly.**
Reason in five coverage shapes (users won't name them; map their words):

- **hero** — one image carrying the whole piece's thesis (the opener /
  og-image job)
- **set** — one image per load-bearing anchor, interleaved by placement
- **hero + set** — the full article job: a thesis-carrying hero up top
  *and* per-section anchor images. The hero is not anchor #1 — anchors
  land their section's idea; the hero lands the piece's. Generate the
  hero first: once it passes the quality bar it doubles as the set's
  **style anchor** (the second `--ref`, step 5 in SKILL.md).
- **mini-comic** — one canvas, 2–4 panels, when the thesis is itself a
  progression
- **shot list** — plan only, render nothing yet

**Sets need placements.** The placement test below gates sets at the
source level too: separate images are justified by separate places in a
piece for them to live. A compact source — a tweet, a launch post, one
concept however complex — has no such places and **never yields a set**;
its multi-beat form is the mini-comic, or a hero that carries the whole
thesis. Only a structured piece (an article or newsletter with real
sections) supports a set.

Routing:

- **Single-claim short post** → hero; no questions.
- **Compact multi-beat source** (multi-claim tweet/launch, complex
  one-liner) → hero if one scene can carry the *full* thesis; mini-comic
  if the thesis is a progression; if genuinely unclear, ask once offering
  exactly those two — never a set.
- **Structured multi-beat piece** (article, newsletter, postmortem with
  sections) → never silently collapse it into one image, and never
  silently render a set either (each render bills the user). Ask **one**
  short question — "One hero image, a hero plus per-section set (~N
  images), or just the section set? (Default: one hero — it won't be full
  coverage.)" — then proceed with the answer or the stated default. Offer
  the mini-comic in that question only when the whole piece is one
  progression. Never ask twice.
- **The user already named the coverage** ("one hero image", "a 4-image
  set", "hero plus section images", "make it a comic", "shot list
  first") → that wins; no questions.
- A lone image made from a multi-beat source is a **hero for the central
  lesson** — deliver it saying so, never as if it covered the piece.

**One idea per image never means one image per article.** It means a
multi-idea piece needs multiple images, a mini-comic, or an explicit
hero decision. From here, the count and shape rules below take over.

## Picking the shape (single scene vs mini-comic vs separate images)

Shape is an **editorial-register** decision — an explainer image's shape is
its structure type (above). The anchor-count rules here apply to both
registers; each anchor also picks its register by the gate in "Two
registers" before picking a shape.

For anything multi-image, decide in two passes, in order: **count first,
shape second.** The count of images is the count of load-bearing anchors in
the piece (the shot-list section below) — one image per anchor. Then each
anchor's image picks its own shape with the rules here. The passes never
trade: a mini-comic is one image at one anchor, never a way to merge several
anchors into one frame; a multi-stage anchor is one image (possibly a
comic), never sliced into several. The placement test separates them: panels
that would sit at *different* places in the piece, each landing its own
sentence, are separate anchors — separate images.

The idea picks the shape; the destination never does — destination sets
aspect, palette, pixel normalization, and watermark only. Default to a
**single scene**: it is bolder at every size, and most ideas land in one caught
moment. Treat an **X Article banner / hero** as a special destination format,
not generic social art: prompt for the banner target **1536 × 640 px**
(`1536:640`) unless the user gives another concrete size. Keep essential action
inside a crop-safe middle band, leave top/bottom/side breathing room, and avoid
title placement that depends on edge-to-edge filling. The same
silhouette lock as above applies: never stretch, squash, or flatten the
mascot or props to fill the banner. Generate the banner through the normal `illo.py generate` pipeline;
do not manually composite or rebuild the scene from crops unless the user asks
for post-processing. Ordinary X post art and X article body images remain the
normal social formats (`16:9` or sometimes `1:1`).

A mini-comic earns its panels only when **the meaning lives between the
panels** — panels beat one scene when at least one of these holds:

- **Causality is the claim** — the idea says "X leads to Y", and Y only
  reads as a consequence if X is seen first (a fail→fix, a
  before→during→after). One frame can show X and Y; it can't show *because*.
- **Accumulation is the point** — the idea is about steps compounding
  (stuck → small slice → shipped); freezing any single moment loses the
  build.
- **A turn lands it** — setup, then a deadpan reversal in the last panel.
  Only panels have comic timing; if the idea is funny because of the turn,
  the beat structure is the joke.
- **Rhythm carries it** — the same scene repeated with one change per
  panel, where the pattern itself is the message (the retry loop, the
  meeting that never ends).

The negative test: **if the panels could be reordered, or any panel dropped,
without losing the meaning, it is not a sequence** — collapse it to one
scene. In particular, a comparison of two states with no journey between
them is a single "change" staging (one frame holding both states, or one
state caught mid-action that implies the other), not a comic.

Note that almost any sequence *can* be flattened into one frame — with
arrows, numbered stations, a winding path, ghosted before-states. In the
editorial register that machinery is forbidden (the quality bar's
flowchart/infographic fail) — it is the explainer register's working
grammar, but reaching for it does not reroute the image: a sequence whose
point is a story beat (a turn, an accumulation, a felt build) is editorial
business and stays panels-or-scene; only a thesis that is itself a
traceable structure passes the register gate. So within editorial the
question is never "can it be one frame?" but what the flattening costs: one caught moment implies the arc
cleanly → single scene; the flattening would need diagram machinery or a
second instance of the mascot → panels, each panel staying a simple one-move
scene; the sequence needs more than 4 beats even as panels → depict the one
load-bearing beat and let the prose carry the rest.

Borderline cases — an idea that passes the sequence test but where one
caught moment could still imply the whole arc — are a style call, and the
house style calls it for the single scene: panels are a deliberate choice,
never a fallback. An explicit user request ("make it a comic", "single
shot") beats all of the above.

When a sequence IS the right call, pick where it lives:

- The progression sits **in one place** — inside one section or one concept
  → **one mini-comic image**.
- The ideas are **spread across the piece** → **separate interleaved images**,
  one per anchor.
- On a **social destination**, one self-contained mini-comic beats a thread
  of separate images — but a social destination alone never upgrades a
  single-moment idea into panels.

Panel rules: 2–4 panels, never more; one action per panel; same mascot, same
key object, same palette in every panel; clear gutters or thin panel borders;
at most one short label per panel.

## Restraint

- One idea, one staging; usually ≤3 short editorial text items total; leave a calm empty region.
  (Explainer images swap these numbers for that register's budget, above —
  everything else here applies to both registers.)
- A few accent touches — never a colored-in scene.
- Decide the communication hierarchy before writing the prompt: the **primary
  read** (the scene alone, or one short floating thesis title) and the
  **supporting reads** (small labels/callouts that name evidence or parts).
  Standalone heroes, announcement art, social cards, and abstract claims often
  need an inferred primary title so the image can be understood away from the
  surrounding prose. Interior article art often does not.
- When there is a primary title, reserve its space as a **title field** before
  placing the subject — usually the calm upper-left or upper-center region in a
  16:9 hero. For an X Article banner, prefer a far-left or far-right calm field
  and keep the title short enough to read in a 640 px-tall canvas. The title
  must sit inside the safe area, with visible paper around it on all sides:
  roughly one title-letter height, or at least ~6-8% of the canvas, from the
  nearest frame edge. It is never squeezed against the frame or tucked into a
  leftover corner. Keep a clear gutter between title, mascot, props, and
  supporting labels; no tangencies, no crowding, no title touching or visually
  leaning on the subject.
- No boxed title bar or diagram-style header, and don't write the staging's
  name. A short *floating* thesis title — a few words on bare paper, like a
  caption that completes the piece — is fine and counts against the editorial
  text budget; reach for it when it lands the artifact job, skip it when the
  scene already speaks. If a primary title is present, supporting labels stay
  visibly subordinate and do not compete with it. Honor an explicit request
  either way: add a title when the user asks for one, omit it when they say no
  title.

## Reinvent each time

The bundled examples calibrate line weight, grain, and restraint only — never
copy their layout. Same topic next time means a **different move and a different
object**: if a new piece drifts toward an earlier one, change the verb and the
thing. The aim is one fresh, memorable, slightly-absurd picture per idea.

## Shot list (planning requests)

Let the count fall out of the anchors actually found — typically 3–6 per
article, 1–2 for short pieces — and **never pad to hit a number**: a section
with no load-bearing moment gets no image. A full article job
(hero + set) leads the list with a **hero row** — placement "top of
piece", idea = the locked thesis — which sits outside the anchor count
and the never-pad rule. Per image:

- **Placement** — after which section or idea
- **Idea** — the one sentence it lands: *this anchor's* own thesis-lock
  (Source routing step 2), what this section turns on — not a fragment of
  the piece summary. Each row is analyzed on its own terms.
- **Artifact job** — opener/social hero, interior section support, mechanism
  explainer, reusable asset, etc.
- **Register** — editorial unless the row passes the explainer gate ("Two
  registers"); say which, so the reader can challenge the call.
- **Staging** — which angle above (editorial), or which structure type
  (explainer; pick per "Pick the diagram type")
- **The mascot's move** — the physical action (labeled stages: the one
  pack-solved operator stage)
- **Object(s)** — the one or two built things (labeled stages: one
  connected system, not a row of props)
- **Palette** — preset name or derived dominant
- **Text hierarchy** — primary read/title if needed, then supporting labels or
  explainer callouts; keep their visual priority distinct. For a primary title,
  name the reserved title field and the gutter that keeps it clear of the
  subject.

Pick the moments that carry the piece — a pivotal claim, a loop, a turn, a trap,
a handoff — not even coverage across every paragraph. A moment is
load-bearing when the argument *turns* on it (remove it and the conclusion
stops following), when the prose goes most abstract and a concrete picture
re-grounds the reader, or when it is the one beat a reader should carry away.
Help the reader; don't turn the whole article into a picture book.
