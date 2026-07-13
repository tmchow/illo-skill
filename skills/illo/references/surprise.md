# Surprise mode

Invent or fetch a **safe** seed idea, lock one thesis, and render **one**
image through the normal workflow — with **no clarifying questions**. Built
for both casual "surprise me" prompts and scheduled / headless agents that
call the skill on a timer and need a caption-ready deliverable back.

Read this file in full before acting on any surprise / random request.

## When to route here

Route here when the ask is essentially **unscoped invent-and-render**:

- "surprise me", "surprise", "illo surprise"
- "random", "random illo", "give me something random"
- scoped variants: "surprise me with art quote", "random using blot",
  "surprise me with space using bray"

**Do not** route here when the user already supplied a concrete thesis
("illustrate 'you are the bottleneck'", "draw the bridge under live
traffic"). Those stay the Step 1 concept branch — "just make it" / "single
shot" only skips questions; they are not surprise mode.

## Headless contract

Surprise mode is always headless:

- **Never** ask clarifying questions (focus, destination, shape, palette).
- **Never** fan out into option batches (`--count`, model loops) unless the
  user explicitly asked for options.
- Always **one** image.
- Resolve palette via normal Step 4 defaults (no destination interrogation).
- Still run Step 0 preflight. If `doctor` reports `backend: NEEDS CHOICE`,
  surface that choice — it is a hard blocker, not a taste question.

## Parse scopes

Strip the trigger words, then split what remains into **character** and
**focus**:

1. **Character** — phrases like `using blot`, `with bray`, `as blip`.
   Resolve with Step 2 rules (pack name → aliases → catalog). On one clear
   match, use it; on several, pick the closest name match without asking; on
   none, say the name was unknown and fall through to random.
2. **Focus** — everything else that scopes subject matter: `art quote`,
   `productivity`, `space`, `cooking`, `design`, etc. Unscoped = any safe
   domain.

### Character when unnamed

Ignore config `defaultCharacter` in this mode (surprise means variety;
explicit names still win). Build the pool from `doctor`'s installed
character list, then **add shipped `blot`** if it is not already present.
Pick **uniformly at random** (e.g. a one-liner over the name list). Name
the chosen pack in the delivery text.

## Seed discovery — three layers

There is **no** canned topic bank. Build three related pieces, then render:

| Layer | Role | Lives where |
|---|---|---|
| **Saying** | The shareable caption — the line a person posts *with* the image | Delivery text (always) |
| **Provenance** | Citation only when sourced and multi-source verified; omit when original or unverified | Delivery text when citing |
| **Thesis** | One sentence naming what the picture must communicate | Internal lock before the prompt |
| **Title** (optional) | A short on-image label that helps the scene read at a glance | Pixels, only when useful |

The saying is the load-bearing deliverable for scheduled / share use. The
thesis turns that saying into a physical move. Cite only when there is a
real source — silence means original. The title is never a substitute for
the saying.

### Saying bar (reject thin stubs)

Ask: *Would this line still earn a pause if the image were covered?* If not,
re-roll the saying before locking a thesis.

A good saying is a **complete thought** with impact — roughly one to three
sentences, or one dense sentence with a turn — that is at least one of:

- **inspirational** — warmth, courage, patience, quiet pride
- **educational** — a real insight you could teach in a breath
- **interesting** — a vivid observation, gentle wit, or wonder (topical
  science and craft count)

Hard reject as a saying (these may still be *titles*):

- Two-to-four-word stubs: "The spike settles", "Roll again", "First light"
- Jargon shorthand with no human stake: "check once", "steep", "provision"
- Vague mood without a claim: "be kind", "keep going", "stay curious"

Thin → rich (shape only — invent fresh lines every run; do not reuse these):

- ✗ "The spike settles." → ✓ "Rough patches peak. Hold steady and the bolt
  gets smaller — the storm was never meant to be the whole sky."
- ✗ "First light." → ✓ "After years of building the ruler, the instrument
  finally saw Earth — first light is the moment craft becomes witness."
- ✗ "Steep." → ✓ "A pause is part of the work: what ships well was allowed
  to steep."

Famous / recalled quotes still work when they already clear the bar; invent
original sayings when the focus is unscoped or topical — then run the
**sense bar** below before locking. Cite only when sourced (next section).
Never imply a line is a famous quote when it is not.

### Sense bar (critical evaluation — especially originals)

Fluent is not the same as true or useful. Models often emit lines that
*sound* wise and mean little, contradict themselves, or invent fake
profundity. Before locking any **original** saying (and before locking an
inspired-by paraphrase of a topical hook), run this judgment out loud in
planning — reject and rewrite on any fail:

1. **Plain-sense test** — Restate the claim in plain words with no metaphor.
   If you cannot, or the restatement is empty ("be mindful of journeys"),
   reject.
2. **Stake test** — Name who benefits and what changes if the claim is
   taken seriously. If nobody would act differently, reject.
3. **Non-contradiction** — The line must not undo itself or stack opposing
   advice without a clear turn. Reject vibes that cancel out.
4. **Specificity** — Prefer a concrete domain (craft, rest, learning,
   noticing, repair) over cosmic filler. Reject abstract fog sold as depth.
5. **Honest originality** — Do not smuggle a half-remembered famous quote
   as an "original." If it might be someone else's line, verify or rewrite
   until it is clearly yours.
6. **Share test** — Would you post this under the image without cringing or
   needing a footnote to explain what you meant? If not, reject.

Attributed quotes that already passed verification skip this bar (their
authors own the claim). Still reject a verified quote that fails the
ordinary saying bar (too thin, unsafe, undrawable).

### Provenance (cite when sourced)

Every saying is either **sourced** or **original**. Cite only when sourced —
do not add an `— original` marker; omission of a citation is enough.

1. **Attributed quote** — a real line from a real person / work. Prefer this
   when the focus is quote-shaped (`art quote`, `design quote`, …) or when a
   well-known safe line already clears the saying bar. Delivery form:
   `"{saying}" — Name` (add work/year only when it helps).
   **Verification gate (required before citing):**
   - Do **not** trust model memory alone — LLMs commonly invent or
     misattribute quotes.
   - Do **not** cite from a single blog, quote-aggregator, or social post.
   - Confirm with **at least two independent reputable sources**, and prefer
     a primary or near-primary one when available (the person's published
     work, a scholarly edition, a museum/archive transcript, a
     well-regarded quotation reference that cites the original). Quote-
     investigator sites (e.g. Quote Investigator) count as one strong
     check when they document the trail.
   - The wording must match closely enough to be honest — do not "improve"
     a quote and keep the name.
   - If sources disagree, the trail is murky, or only viral lists agree:
     **do not attribute**. Deliver as an original (no citation) or pick a
     different, verifiable line.
2. **Attributed idea / topical hook** — not a verbatim quote, but grounded
   in a real event, discovery, or named practice (e.g. a science first-light,
   a craft tradition). Delivery form: the saying, then a short credit line
   such as `Inspired by …` / `After …` naming the source. Confirm the event
   against a reputable report (agency release, major news, paper) — not a
   single unverified post. Keep the credit factual and celebratory (safety
   filter still applies).
3. **Original** — invented for this run. Fair game, and common for unscoped
   surprise — **only after the sense bar passes**. Deliver the saying alone
   — **no** fake author, **no** `— original` tag. Lack of citation is the
   signal.

**Never** invent a fake author, misattribute a line, or dress an original as
a classic. Prefer (1) or (2) when share-credibility matters **and** the
verification gate passes; use (3) freely when inventing is the honest path
or verification fails.

### How to find the saying

1. Prefer a **fresh, drawable moment** with a human stake — then either find
   a **verifiable** sourced line that fits it, or write an **original**
   saying that passes the sense bar (no citation).
2. **May fetch** (web search, news, pop culture) when the focus invites
   topicality, or when the run is unscoped and a safe current hook is
   available — a successful rocket launch, a science discovery, a sports
   celebration, a museum opening, a harmless meme shape. Historical
   knowledge and famous quotes remain fair game **only after verification**.
   Compress the hook into a saying that teaches or wonders, not a headline
   stub; run the sense bar on any paraphrase; cite only when the provenance
   gate passes.
3. **May invent or recall** when fetch is unavailable, empty, or every
   topical candidate fails the safety filter — originals must clear the
   sense bar and carry no citation; a recalled quote still must pass
   verification before any name is attached.
4. For **quote-shaped** focuses (`art quote`, `design quote`, …): prefer a
   **verified attributed** line that clears the saying bar. If verification
   fails, invent an original quote-shaped line that clears the **sense bar**
   with **no** citation — do not fake a famous voice. Illustrate the *idea*,
   not a wall of text on the canvas.
5. Reject sayings that cannot become a **physical move the mascot performs**
   (`references/composition.md`, "Turn the idea into a move"). Abstract
   vibes without a move → invent a concrete staging, then rewrite the
   saying so it still names the stake.

Re-roll until the saying clears the saying bar, the sense bar (for
originals / paraphrases), the safety filter, **and** has a named physical
move (plus a verified citation whenever a name is attached). Never "tone
down" a banned topic into the picture.

## Safety filter

Apply **before** locking the thesis.

**Allow:** warmth, quiet joy, curiosity, craft / making, gentle absurdity,
playful point-of-view disagreement that stays kind, celebration of safe
achievements, nature, learning, collaboration.

**Hard reject:**

- Politics, elections, parties, policy fights, wars, geopolitics
- Race, ethnicity, religion-as-conflict, identity attacks
- Tragedy, disaster aftermath, crime, medical trauma, death
- Sexual content, cruelty, humiliation, "roast" / cutting humor
- Culture-war bait, conspiracy, harassment

**Borderline current events:** keep only the **celebratory or wondrous**
face (the launch succeeded; the discovery landed) — never the controversy
around it. If unsure whether a seed is safe, invent something else.

## Register variety (pick before locking the move)

Surprise runs must **not** collapse into the same picture shape every time
(one mascot + one prop + a big title). Pick the **register first**, then
shape the saying and thesis to earn it — do not invent a single-beat claim
and then default to editorial every run.

Choose among these with deliberate variety across runs (and within a
scheduled series). A simple rotation works: editorial → mini-comic →
explainer → editorial… unless the user's focus forces a shape (e.g. "as a
comic", "show the flow"):

- **Editorial** — one caught scene. Still the most common, but not automatic.
- **Mini-comic** — 2–4 panels in one image when the saying is a short
  progression (stuck → try → land; closed → open → light). Invent the saying
  so it *has* beats — do not demote a progression into a single freeze-frame.
  Panel lettering follows the house mini-comic rules below (not silence).
- **Explainer** — a hand-built flow / fan-out / timeline / loop / stack when
  the saying teaches a structure (how care compounds, how a craft works, how
  an archive becomes a discovery). Invent the saying so the structure *is*
  the point — then follow `references/composition.md`, "The explainer
  register", including short station callouts.
- **Never cutout** — cutouts carry no idea.

If the chosen register and a candidate saying fight each other, rewrite the
saying or pick a different register — do not silently fall back to
editorial+title.

## Thesis lock

With register and saying locked, write one composition sentence before any
prompt:

> This image must communicate: \<thesis>.

The thesis is the *move* (or panel beats / structure type) compressed from
the saying — not a shorter substitute for the saying. Example: saying = a
rough-patch paragraph; mini-comic thesis = "panel 1 bolt wild → panel 2
mascot steadies it → panel 3 bolt small and calm."

## On-image text — no poster title; comics still letter

In surprise mode the **saying already lives in delivery**, so a big
floating **primary title** is usually redundant and makes every run look
like the same poster. That ban is about *poster titles*, not about all
lettering.

- **Default across registers: no PRIMARY TITLE.** Do not put STEEP / ONE STEP
  / FIRST LIGHT style headlines on the canvas.
- **Editorial** — usually `TEXT: no hand-lettered text`, or at most 1–2 tiny
  supporting labels if a prop must be named. Never a poster title.
- **Mini-comic** — **letter the panels by default.** Follow
  `references/composition.md` / `prompt-recipe.md`: at most **one short
  label per panel** (a beat word, a whisper of dialogue, a caption, or a
  sound) on bare paper/ground inside or beside that panel. Compress the
  saying into those beats — do not dump the full saying as a title above
  the strip. A fully wordless comic is allowed only when the silent
  progression is clearer than any label; it is the exception, not the
  habit.
- **Explainer** — short station/callout labels as the explainer budget
  requires (`composition.md`); still no poster title above the diagram.
- Never hand-letter the full saying onto the image.

Then continue with Steps 2–7 as a **single** image (character already
resolved above; Step 2 is confirmation, not re-asking). Explainer and
mini-comic rows still follow those registers' shot-list / structure rules.

## Delivery

Always report, next to the image (path or chat media per Step 7):

- the **saying** first — full shareable caption
- a **citation** only when sourced **and verified** — `— Name` for quotes
  (after the multi-source gate), or `Inspired by …` / `After …` for topical
  hooks confirmed against a reputable report. Omit any credit line when the
  saying is original or attribution is unverified.
- the **character** used
- palette / look only as briefly as a normal single-image delivery

Do not deliver only the on-image title or a thesis stub. Scheduled callers
need caption text without OCR — the saying (and citation when sourced) is
part of the deliverable, not optional commentary.
