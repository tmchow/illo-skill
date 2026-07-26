# Surprise mode

Invent or fetch a **safe** seed idea, lock one thesis, and render **one**
image through the normal workflow. Built for both casual "surprise me"
prompts and scheduled / headless agents that call the skill on a timer and
need a caption-ready deliverable back.

Read this file in full before acting on any surprise / random request.

## When to route here

Route here when the ask is essentially **unscoped invent-and-render**:

- "surprise me", "surprise", "illo surprise"
- "random", "random illo", "give me something random"
- scoped variants: "surprise me with art quote", "random using blot",
  "surprise me with space using bray",
  "surprise me with art quote --autopick using bray"

**Do not** route here when the user already supplied a concrete thesis
("illustrate 'you are the bottleneck'", "draw the bridge under live
traffic"). Those stay the Step 1 concept branch — "just make it" / "single
shot" only skips questions; they are not surprise mode.

## Headless contract

Surprise mode stays non-interrogative about taste and destination:

- **Never** ask clarifying questions about focus, destination, shape,
  palette, character, or register.
- **Never** fan out into option batches (`--count`, model loops) unless the
  user explicitly asked for options.
- Always **one** image.
- Resolve palette via normal Step 4 defaults (no destination interrogation).

**Exception — saying picker:** in interactive sessions, present the saying
candidates and wait for a choice (or refresh) before any render — unless
the run is on the **auto-pick path** (below). Auto-pick hosts still **must**
build the candidate set and judge the best, then continue through register
and thesis; they only skip the question UI.

Scheduled / timer callers should pass **`--autopick`** so the path is
unambiguous. Do not rely on guessing whether the host can ask questions —
prefer the token for automation; use the no-question fallback only when the
host truly cannot present a choice.

## Procedure order

Execute in this order:

1. Parse scopes → note `--autopick` if present
2. **Step 0 preflight** (`doctor`) — resolve hard blockers (including
   `backend: NEEDS CHOICE`) **before** any saying work or picker. Use the
   installed-character list from this check for character resolution below.
3. Resolve **character** (below)
4. Pick **provenance mode** (below)
5. Build saying candidates for that mode — **three** by default; each already
   cleared the **safety filter**, saying bar, and (when applicable) sense
   bar / verification gate. Fewer than three is allowed **only** on a
   forced `* quote` budget miss (see **Search budget and demotion**).
6. **Saying picker** (interactive) **or** judge-and-lock the best (auto-pick)
7. Pick **register** shaped to the **locked** saying (below) — for
   `attributed_quote`, never rewrite the quote to fit a register
8. Lock the **thesis**, then render via Steps 3–7 (skip Step 0 — already
   done; skip Step 2 — character is already resolved). Auto-pick does **not**
   skip steps 7–8.

## Parse scopes

Strip the trigger words, then split what remains into **character**,
**focus**, and optional **auto-pick**:

1. **`--autopick`** — the **sole** keyword/token match for skipping the
   saying picker. If present, strip it before any other matching; never
   treat it as focus or character. Do **not** keyword-match bare
   `autopick`, `[autopick]`, or phrase lists — those are not tokens.
2. **Character** — phrases like `using blot`, `with bray`, `as blip`.
   Resolve by pack name → aliases → catalog (same matching rules as Step 2;
   do **not** fall through to `defaultCharacter`). On one clear match, use
   it; on several, pick the closest name match without asking; on none, say
   the name was unknown and fall through to random.
3. **Focus** — everything else that scopes subject matter: `art quote`,
   `productivity`, `space`, `cooking`, `design`, etc. Unscoped = any safe
   domain.
   - If the focus **ends with** `quote` (`art quote`, `design quote`, …):
     that **forces** provenance mode `attributed_quote`; the words before
     `quote` are the topic narrower (`art`, `design`, …). If there are no
     words before `quote` (focus is just `quote`), treat the topic as **any
     safe domain**.

### Character when unnamed

Ignore config `defaultCharacter` in this mode (surprise means variety;
explicit names still win). Build the pool from `doctor`'s installed
character list, then **add shipped `blot`** if it is not already present.
Pick **uniformly at random** (e.g. a one-liner over the name list). Name
the chosen pack in the delivery text.

### Auto-pick path (candidates → best, no question UI)

Skip the interactive saying picker — but **still build the candidate set
and lock the strongest** — when **any** of these hold:

1. **`--autopick`** appeared in the prompt (sole token match). Prefer this
   for scheduled / timer prompts.
2. **Intent reasoning** — in an interactive session, the whole prompt
   clearly asks you to choose / not ask / proceed without options. Reason
   over intent; do **not** use a phrase checklist. Ambiguous → keep the
   picker.
3. **No interactive question capability** — the host genuinely cannot
   present a choice → auto-pick without requiring `--autopick`. Treat this
   as a last resort; automation should still send `--autopick`.

On this path: score the keepers (normally three; see forced-quote budget
miss below) on drawability and the share test — saying bar, sense bar, and
**safety already cleared at candidate build**. Lock the strongest, then
**continue the procedure at steps 7–8** (register → thesis → render). Do
**not** jump straight to `generate`. Do **not** invent an extra line to pad
the set. Still report the chosen saying in delivery.

Example scheduled prompt: `surprise me with art quote --autopick using bray`

## Provenance variety (pick before building candidates)

Surprise runs must **not** always invent originals. Pick a **provenance
mode** before building candidates, then build three for that mode only.

Modes:

- **`attributed_quote`** — a real line from a real person / work; cite only
  after the verification gate. Delivery form: `"{saying}" — Name`. Short
  stubs still fail the saying bar — prefer lines with real impact, not
  two-to-four-word catchphrases.
- **`topical_hook`** — not a verbatim quote; grounded in a real event,
  discovery, or named practice. Credit with `Inspired by …` / `After …`.
- **`original`** — invented for this run; sense bar required; **no** citation.

**How to pick the mode:**

1. Focus ends with `quote` → **force** `attributed_quote` (topic = words
   before `quote`, or any safe domain if bare `quote`). Inventing an
   uncited “quote-shaped” original is **forbidden** on this path.
2. Otherwise (unscoped or a non-quote focus such as `productivity`,
   `space`): **roll uniformly** among the three modes (~1 in 3 cited
   quotes). A simple rotation across scheduled runs also works. Constrain
   candidates to the focus domain when one is present.

### Search budget and demotion

When building candidates for a sourced mode, **attempt real fetch and
verification** (web search / primary sources) before giving up — do not
demote from model memory alone.

- **Rolled `attributed_quote`:** after at most **10** candidate attempts
  (fetch → verify → saying bar → safety) still short of three keepers,
  **demote that run to `original`** and build three sense-bar originals
  instead.
- **Forced `* quote` focus:** do **not** demote to invent. Cap at **10**
  candidate attempts; widen slightly within the topic as needed. If fewer
  than three verified keepers land after the cap:
  - **0 keepers** → abort cleanly; say so; do not render; do not invent.
  - **1–2 keepers** → that smaller set **is** the candidate set for this
    run (the only exception to “always three”). Interactive: offer those
    keepers plus **“Three new ones”** (full refresh — see picker below).
    Auto-pick: lock the best of the keepers, then continue steps 7–8.
  - **Never** invent or pad to force a count of three.
- **`topical_hook`:** after at most **10** candidate attempts still short of
  three safe credited hooks, **demote that run to `original`** and build
  three sense-bar originals instead.

## Register variety (pick after the saying is locked)

Surprise runs must **not** collapse into the same picture shape every time
(one mascot + one prop + a big title). Pick the **register after** the
saying is locked, shaped so the locked line earns it — do not invent a
single-beat claim and then default to editorial every run.

Choose among these with deliberate variety across runs (and within a
scheduled series). A simple rotation works: editorial → mini-comic →
explainer → editorial… unless the user's focus forces a shape (e.g. "as a
comic", "show the flow") or the locked saying clearly demands one shape:

- **Editorial** — one caught scene. Still the most common, but not automatic.
- **Mini-comic** — 2–4 panels in one image when the saying is a short
  progression (stuck → try → land; closed → open → light). For originals /
  topical hooks, shape the saying so it *has* beats when this register
  wins. Panel lettering follows the house mini-comic rules below (not
  silence).
- **Explainer** — a hand-built flow / fan-out / timeline / loop / stack when
  the saying teaches a structure. For originals / topical hooks, shape the
  saying so the structure *is* the point — then follow
  `references/composition.md`, "The explainer register", including short
  station callouts.
- **Never cutout** — cutouts carry no idea.

**Register vs saying fights:**

- **`original` / `topical_hook`:** rewrite the saying **or** pick a different
  register — do not silently fall back to editorial+title.
- **`attributed_quote`:** the verified wording is frozen — **never** rewrite,
  “improve,” or compress the quote to fit a register. Change the register
  (or the staging/thesis) instead; if no register fits honestly, drop that
  candidate before offer/auto-pick and find another verified line.

## Seed discovery — three layers

There is **no** canned topic bank. With provenance mode chosen and three
candidates ready (then one locked), build:

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
re-roll that candidate before offering or auto-picking.

A good saying is a **complete thought** with impact — roughly one to three
sentences, or one dense sentence with a turn — that is at least one of:

- **inspirational** — warmth, courage, patience, quiet pride
- **educational** — a real insight you could teach in a breath
- **interesting** — a vivid observation, gentle wit, or wonder (topical
  science and craft count)

Hard reject as a saying (these may still be *titles*) — **including
attributed quotes**:

- Two-to-four-word stubs: "The spike settles", "Roll again", "First light",
  "Stay hungry"
- Jargon shorthand with no human stake: "check once", "steep", "provision"
- Vague mood without a claim: "be kind", "keep going", "stay curious"

Thin → rich (shape only — invent fresh lines every run; do not reuse these):

- ✗ "The spike settles." → ✓ "Rough patches peak. Hold steady and the bolt
  gets smaller — the storm was never meant to be the whole sky."
- ✗ "First light." → ✓ "After years of building the ruler, the instrument
  finally saw Earth — first light is the moment craft becomes witness."
- ✗ "Steep." → ✓ "A pause is part of the work: what ships well was allowed
  to steep."

Famous / recalled quotes work when provenance mode is `attributed_quote`
and they clear the saying bar **and** the verification gate. Short catchphrases
are not rescued by fame. Originals only when mode is `original` (or after a
rolled sourced mode demotes). Never imply a line is a famous quote when it
is not.

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

### Provenance rules (cite when sourced)

Every locked saying is either **sourced** or **original**. Cite only when
sourced — do not add an `— original` marker; omission of a citation is
enough. Mode selects which path to build candidates on:

1. **`attributed_quote`** — real line, real person / work. Delivery:
   `"{saying}" — Name` (add work/year only when it helps).
   **Verification gate (required before citing or offering):**
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
     **do not attribute** that candidate — drop it and count it against the
     search budget; find another verifiable line (forced quote focus) or
     demote per **Search budget and demotion** when mode was only rolled.
2. **`topical_hook`** — not a verbatim quote; grounded in a real event,
   discovery, or named practice. Delivery: the saying, then
   `Inspired by …` / `After …`. Confirm the event against a reputable
   report (agency release, major news, paper) — not a single unverified
   post. Keep the credit factual and celebratory (safety filter still
   applies).
3. **`original`** — invented for this run — **only after the sense bar
   passes**. Deliver the saying alone — **no** fake author, **no**
   `— original` tag.

**Never** invent a fake author, misattribute a line, or dress an original as
a classic.

### How to build saying candidates

Produce **three distinct** candidates for the **provenance mode** already
chosen — except the forced `* quote` budget-miss case above (1–2 verified
keepers, or abort on zero). Never invent a line just to hit three, and never
short-circuit past the picker/auto-pick into render. Apply the **safety
filter** to every candidate **before** it is offered or auto-picked — the
user must never choose a line that then fails safety.

1. Prefer a **fresh, drawable moment** with a human stake that fits the mode.
2. **`attributed_quote`:** fetch/recall candidates in the topic (or any safe
   domain if unscoped / bare `quote`); each must pass the multi-source
   verification gate, the saying bar, and safety before it is offered or
   auto-picked. Illustrate the *idea*, not a wall of text on the canvas.
   Respect the **search budget** above. Wording stays frozen once verified.
3. **`topical_hook`:** may fetch (web search, news, pop culture) for distinct
   safe hooks; compress each into a saying that teaches or wonders (not a
   headline stub); sense bar on paraphrases; credit only when the
   provenance gate passes. Respect the **search budget** above.
4. **`original`:** invent three distinct sense-bar originals; no citation;
   no half-remembered classics smuggled in.
5. Reject any candidate that cannot become a **physical move the mascot
   performs** (`references/composition.md`, "Turn the idea into a move")
   under some honest register. For quotes, drop the candidate rather than
   rewriting the line.

Each keeper must clear the saying bar, the sense bar (for originals /
paraphrases), the safety filter, **and** have a named physical move available
(plus a verified citation whenever a name is attached). Never "tone down" a
banned topic into the picture.

### Parallel candidate verification (optional)

When provenance is **`attributed_quote`** or **`topical_hook`** and the host
can run subagents / parallel workers, **may** fan out verification. Parallel
is only an acceleration of the same keeper rules and search budget as the
serial path — not a shorter checklist.

- The **main agent** still owns scope parse, preflight, character,
  provenance roll, assembling keepers, the picker / auto-pick, register,
  thesis, image generate, QA, and delivery.
- Spawn workers in **waves of up to three** (one candidate line or hook
  each). Each worker runs the **full** keeper gate, same as serial:
  fetch → multi-source verify (or event confirm) → saying bar → sense bar
  when the line is a topical paraphrase → safety → physical-move check
  (can the mascot perform an honest move under some register?) → return
  keeper (saying + citation) or reject reason. Keep search noise in the
  workers.
- **Search budget still applies:** each worker attempt counts toward the
  **10** candidate attempts for this build. Accumulate keepers across
  waves. After each wave: if the **total** keepers for this build is
  already **three** (or more — then keep only the best three), **stop** —
  do not launch another wave. If total keepers are still under three and
  budget remains, launch another wave sized to the **shortfall** (need 2
  more → at most 2 workers) with **fresh** distinct candidates, or finish
  remaining attempts serially. Demote / forced-quote shortfall / abort
  rules are unchanged and only fire after the budget is exhausted with
  fewer than three keepers.
- On **“Three new ones”**, re-roll provenance/topic on the main agent
  first; fan out again only if the new mode is sourced (new 10-attempt
  budget for that build).
- **`original`** mode: invent on the main agent (cheap enough that fan-out
  is usually not worth it).
- If the host has no subagent / parallel support: verify serially on the
  main agent.

### Saying candidates + picker

After the candidate set is ready (three, or 1–2 on a forced-quote budget
miss):

- **Interactive (default)** when the host can ask and the run is not on the
  auto-pick path: present every keeper plus **“Three new ones”** using the
  available interactive question tool (or, in plain chat, ask as a concise
  message and wait). Put **short labels** in the tool options (speaker name,
  a few cue words, or “Option A/B/C”); put the **full saying + citation** in
  the accompanying message so long lines are not truncated. **Do not** call
  `generate` until a saying is locked.
- **“Three new ones” / refresh** — this is a **full re-roll**, not a deeper
  search in the same pocket. Go back to procedure step 4:
  1. **Re-pick provenance mode** unless the user's focus **forces**
     `attributed_quote` (`* quote`). Prefer a *different* mode than the
     set just shown when the roll allows (avoid showing three more
     originals after three originals unless the roll lands there again).
  2. **Change the topic / event / angle** — do not stay on the same subject,
     news hook, or quote cluster. Unscoped: pick a fresh safe domain.
     Focused (e.g. `art`, `productivity`): stay inside the focus, but a
     different corner of it. Forced quote: stay on attributed quotes in
     that topic (or any safe domain if bare `quote`), but different
     speakers/lines — not near-duplicates of what was just offered.
  3. Build a new candidate set (10-attempt cap still applies per build).
  4. Present the picker again. Unlimited refreshes; no image cost.
  Discard the previous set — do not mix old keepers into the new offer.
- **Auto-pick path** (see above): compare the keepers; lock the best; then
  continue at procedure steps 7–8. No question UI.

## Safety filter

Apply to **every candidate before** it is offered or auto-picked (and again
as a final check before thesis lock if anything changed).

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
around it. If unsure whether a seed is safe, drop that candidate (or, on a
forced quote path, pick a different verified line within the search budget).

## Thesis lock

With register and saying locked, write one composition sentence before any
prompt:

> This image must communicate: \<thesis>.

The thesis is the *move* (or panel beats / structure type) compressed from
the saying — not a shorter substitute for the saying. Example: saying = a
rough-patch paragraph; mini-comic thesis = "panel 1 bolt wild → panel 2
mascot steadies it → panel 3 bolt small and calm."

For attributed quotes, the thesis/staging carries the picture; the quote
text in delivery stays verbatim.

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

Then continue with Steps 3–7 as a **single** image (preflight and character
already resolved above — skip Steps 0 and 2 so `defaultCharacter` cannot
override). Explainer and mini-comic rows still follow those registers'
shot-list / structure rules.

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
