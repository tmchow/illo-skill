# Character builder

Design a user's own recurring mascot and install it as the active character
pack. Read `references/character.md` first — the guardrails there are the
acceptance criteria for everything below. The whole flow costs a few paid
renders (typically under ten cents each); say the projected cost before
generating.

## 1. Interview (one short round, ≤4 questions)

Ask only what changes the design:

- **What is it?** An object or creature from the user's domain, product, or
  brand (a teapot, a terminal cursor, a fox). Push toward things with one
  simple silhouette.
- **What look?** The pack's one style: riso (house default) or another from
  the look library — blueprint, woodcut, pixel, clay, manila, chalk,
  phosphor, enamel, gouache — or a custom style file. The model sheet and
  every scene render in this style.
- **Where is the accent?** One small part that will carry the palette accent
  in every image (a tip, a fold, a tail, a topknot).
- **A name?** Optional — the best names read off the design. Offer one if the
  user doesn't have one. If the chosen name *doesn't* read off the subject
  (an ox named `yoke`), ask for **aliases** — the words people would summon
  it by ("ox", "zebu") — and record them in the spec's `Aliases:` line so
  "use ox" resolves to the pack.
- **Any must/never elements?** (e.g. "no corporate logo shapes").

Skip questions already answered by context. If the user **already has art** —
an existing mascot drawing, logo, or sketch — use it: pass it as `--ref` in
step 4 so the candidates stay close to the original while the prompt
translates it into the house line language.

**The face is deliberately not an interview question.** The house face — two
dot eyes, blank deadpan, no mouth, no brows — is the catalog's family look
and the most render-stable choice: apply it by default without asking. But
it is a default, not a rule. If the user asks for something else (a mouth,
brows, a different body plan, a body built from a material), accommodate
them — `character.md`'s locked-face and locked-treatment rules say how:
exact render-checkable terms, never moods — and say the trade-offs out loud:
more facial detail means more drift and harder QA, and designs that diverge
from the house family face a higher review bar if published to the
community catalog.

## 2. Pressure-test the concept before rendering

Work through the anti-complexity guardrails in `character.md` one by one and
push back early:

- A concept that needs text or many distinctive parts to read as itself will
  drift off-model across renders — simplify it or pick a different object.
  Accessories (a hat, a tool, a pattern) are allowed but each must be locked
  in the spec and survive every render; every part is a drift liability.
- A face beyond the deadpan default must be specified in render-checkable
  terms — exact shapes, not moods. "Smiling warmly" drifts; "a thin flat
  structure-ink mouth" locks.
- Does the silhouette stay readable at thumbnail size?
- Is it distinct from a visual cliché the reader already knows (a generic
  file icon, an emoji, a famous mascot)? Collisions read as borrowed IP.

Rewrite the concept with the user until it passes; this step saves more
renders than any prompt tweak.

## 3. Draft the locked spec

Fill this template (it becomes `character.md` in the pack):

```markdown
# {Name} — custom character

{One sentence: what it is, and why the name reads off the design.}

Style: **{look name — riso if unset}**
Aliases: {subject + synonyms, comma-separated — omit this line if the name already reads off the subject}

## Locked design

- **Body**: {the one silhouette, in concrete geometric language}.
- **Face**: {the locked face — house default: two simple dot eyes, blank
  deadpan, no eyebrows, no mouth}.
- **Accent carrier**: {the one accent part} — the only accent-colored part.
- {limbs — house default: small stubby arms and legs}.

## Prompt spec (drop into the CHARACTER slot)

> the recurring mascot — {body description}, {the locked face spec},
> {limbs}; the ONLY accent-colored part is {the accent part}. It MUST
> perform the move, not decorate. {value rule, from the next section}

## Value rules

- **Dark/bold palettes**: {how the body reads — dark fill or light with ink
  outline; what color the eyes are}.
- **Light palettes**: {how the body reads — per the value-follows-palette
  rule in character.md}.

## Personality

{Default: an earnest, low-key operator doing something slightly absurd with a
straight face. Adjust freely — keep it consistent with the locked face, and
let the move, not the expression, carry the idea.}
```

## 4. Generate model-sheet candidates

Render each concept as a clean reference sheet — no scene, no labels. Use the
prompt template below per concept, `--count 2`, aspect `1:1`, into a fresh
`newrun` dir; build a `gallery` and let the user pick (or iterate). No `--ref`
on the first round — there is nothing to lock to yet (both backends render this
first sheet ref-less; once it exists, every later scene render passes it as
`--ref`).

```text
A 1:1 square character reference sheet (model sheet) for a recurring
editorial mascot, on a plain empty paper background — no scene, no props, no
labels, no text anywhere.

CHARACTER — "{name}", {what it is}: {the prompt spec paragraph from step 3}.
Cuteness comes from proportion and roundness only — no parts, accessories,
or face details beyond the locked spec.

POSE: one large clean front-facing full-body view, centered, occupying about
60% of the frame, standing neutral, limbs relaxed.

LINE LANGUAGE: ONE bold, even-weight, softly-rounded outline (a clean
vinyl-sticker line), nothing thin or scratchy.

STYLE: risograph print — grainy halftone texture, slight ink-layer offset,
faint paper grain, flat fills, no gradients, no soft shadows.

PALETTE: paper warm white #fffef7. Structure ink near-black #111111. Accent
fluoro pink #ff3d9a ONLY on {the accent part}.
```

(Use the user's own palette hexes instead if they already have one — the
reference conditions the character's *shape*; palette stays per-image. For a
non-riso look, substitute the style file's LINE LANGUAGE and STYLE blocks and
its classic-default palette into the template above — the sheet must be born
in the pack's style.)

QA each candidate against the guardrails in `character.md`: the locked face
exactly (house default: deadpan, no mouth/brows), no unlocked parts, locked
treatments read in aggregate, one accent part only, silhouette reads at small
size. Reject before showing, and tell the user why a concept was re-rolled.
Iterate at most ~2 rounds; if a concept keeps drifting, that is the concept's
fault — return to step 2.

## 5. Install the pack

Pick a pack name — usually the character's name, lowercase kebab-case.
**Names are globally unique** (they're how agents select characters): check
the community registry with `packs list` before settling, even if the user
isn't publishing, and avoid the reserved names `blot`, `illo`, and the look
names (`riso`, `blueprint`, `woodcut`, `pixel`, `clay`, `manila`, `chalk`,
`phosphor`, `enamel`, `gouache`). With a winner chosen:

```bash
PACK="${XDG_CONFIG_HOME:-$HOME/.config}/illo/characters/<name>"
mkdir -p "$PACK"
cp <chosen-render>.png "$PACK/reference.png"
# write the filled step-3 template to "$PACK/character.md"
```

Confirm with `python3 "$SKILL_DIR/scripts/illo.py" doctor` — it lists the
pack. Then ask whether this should become the **default character**; if yes,
set it (non-secret, so you may run it):

```bash
python3 "$SKILL_DIR/scripts/illo.py" init --no-key --character <name>
```

Per-run selection ("use <name>") beats the default — SKILL.md step 2. Offer a
quick proof render: one simple scene with the new mascot performing a move,
**rendered with the pack's `reference.png` passed as `--ref`**, so the user
sees it on-model in action. The locked sheet is the **single source of
truth**: derive the preview — and every later scene — by conditioning on it,
never from the bare prompt or a sketch/seed alone. A sheet and a scene
generated independently drift into two *different* characters; only
`--ref`-ing the sheet keeps them the same mascot (the same rule SKILL.md
step 5 states for generation — it applies to the very first preview too).

Packs are folders: remove one to retire it, copy it to another machine to
install the character there. If the user wants to share it with everyone,
offer to publish it to the community repo — `references/pack-sharing.md`.

## Style variants

A character's look is part of its pack — the same character in a different
style is a **sibling pack**, built deliberately, never a runtime restyle:

1. Name it `<name>-<style>` (e.g. `blot-woodcut`). Identity is unchanged:
   copy the locked spec and prompt spec verbatim; set the `Style:` line to
   the new look.
2. Regenerate the model sheet in the new style (step 4, substituting the
   style file's blocks), passing the **original pack's** `reference.png` as
   `--ref` so proportions carry over. Far looks fight the original sheet's
   rendering (worst: pixel) — the style file's character treatment and
   forcing language are mandatory; QA against the new style's deltas plus
   the character guardrails, and re-roll until the sheet is fully in-style.
3. Install (and optionally publish) it as its own pack with its own preview.

One look per pack keeps galleries one-image-per-character and makes every
cross-style move a cared-for act instead of a casual transplant.
