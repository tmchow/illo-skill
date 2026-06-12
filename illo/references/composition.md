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

Editorial wins every tie. Route an image to explainer only when:

- **(a) the user asks for it** — "show the flow", "diagram the pipeline",
  "map the steps", "make it traceable", "as an explainer"; or
- **(b) the unit's locked thesis IS a traceable structure** — its point
  lives in the stations and their connections (a pipeline with named
  stages, a fan-out, a timeline, a loop, a layered stack), and one caught
  moment would force the reader to take the structure on faith.

A process that is merely *evidence* for a different lock stays editorial —
the lock is the arbiter, exactly as in Source routing step 2. Genres that
most often qualify: how-to / process and systems / architecture pieces.
Opinions, quotes, launches, and anecdotes stay editorial: their theses are
claims, not structures. Like the mini-comic, the explainer is a deliberate
choice, never a fallback — and a set may mix registers (an editorial hero
over explainer anchors is a natural article shape).

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
in `character.md`).

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

## The explainer register

One structure, drawn as a hand-built sketch the mascot is working inside —
never a presenter beside a chart. The grammar editorial forbids (arrows,
stations, a path) is the working material here; what stays forbidden is the
*formal* version of it: no title, no border, no grid, no legend, no
boxes-and-diamonds flowchart formality. The result must still read as one
artist's hand-built drawing in the active look.

Structure types — pick ONE (these are the explainer's stagings; an explainer
shot-list row names one of these in its staging slot):

- **A flow** — 3–5 stations left to right on one flow line; the
  transformation is visible station to station.
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
- **Callouts ≤6**, 1–4 short words each, hand-lettered directly on the bare
  paper/ground near what they name — semantic ink roles per `palettes.md`,
  never on a colored fill. Stations may be named; don't also caption them.
- **The mascot is a working part** of the structure — a station, the jam,
  the sorter, the hauler between stops — and passes the same load-bearing
  test (`character.md`).
- Negative space floor stays (≥ ~35%); the structure may spread wider than
  an editorial subject (~40–70% of the frame) but keeps one calm region.
- The fresh-metaphor rule applies unchanged: reinvent the structure's
  objects per piece; never recycle a previous diagram.

Sequence routing changes inside this register: a progression that would be a
mini-comic in editorial is drawn as the flow itself here. Panels are
editorial machinery — never mix panels and flow arrows in one image.

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
aspect, palette, and watermark only. Default to a **single scene**: it is
bolder at every size, and most ideas land in one caught moment.

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

- One idea, one staging; ≤3 short labels; leave a calm empty region.
  (Explainer images swap these numbers for that register's budget, above —
  everything else here applies to both registers.)
- A few accent touches — never a colored-in scene.
- Don't write the staging's name or any diagram-style title on the image.

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
- **Register** — editorial unless the row passes the explainer gate ("Two
  registers"); say which, so the reader can challenge the call.
- **Staging** — which angle above (editorial), or which structure type
  (explainer)
- **The mascot's move** — the physical action
- **Object(s)** — the one or two built things
- **Palette** — preset name or derived dominant
- **Labels** — the 1–3 short strings

Pick the moments that carry the piece — a pivotal claim, a loop, a turn, a trap,
a handoff — not even coverage across every paragraph. A moment is
load-bearing when the argument *turns* on it (remove it and the conclusion
stops following), when the prose goes most abstract and a concrete picture
re-grounds the reader, or when it is the one beat a reader should carry away.
Help the reader; don't turn the whole article into a picture book.
