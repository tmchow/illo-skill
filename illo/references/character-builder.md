# Character builder

Design a user's own recurring mascot and install it as the active character
pack. Read `references/character.md` first — the guardrails there are the
acceptance criteria for everything below. The whole flow costs a few renders
(~6–25¢ each); say the projected cost before generating.

## 1. Interview (one short round, ≤4 questions)

Ask only what changes the design:

- **What is it?** An object or creature from the user's domain, product, or
  brand (a teapot, a terminal cursor, a fox). Push toward things with one
  simple silhouette.
- **Where is the accent?** One small part that will carry the palette accent
  in every image (a tip, a fold, a tail, a topknot).
- **A name?** Optional — the best names read off the design. Offer one if the
  user doesn't have one.
- **Any must/never elements?** (e.g. "no corporate logo shapes").

Skip questions already answered by context. If the user **already has art** —
an existing mascot drawing, logo, or sketch — use it: pass it as `--ref` in
step 4 so the candidates stay close to the original while the prompt
translates it into the house line language.

## 2. Pressure-test the concept before rendering

Work through the anti-complexity guardrails in `character.md` one by one and
push back early:

- A concept that needs text, patterns, clothing, or multiple distinctive
  parts to read as itself will drift off-model across renders — simplify it
  or pick a different object.
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

## Locked design

- **Body**: {the one silhouette, in concrete geometric language}.
- **Face**: two simple dot eyes, blank deadpan — no eyebrows, no mouth, ever.
- **Accent carrier**: {the one accent part} — the only accent-colored part.
- Small stubby arms and legs.

## Prompt spec (drop into the CHARACTER slot)

> the recurring mascot — {body description}, two simple dot eyes, blank
> deadpan (no eyebrows, no mouth), small stubby arms and legs; the ONLY
> accent-colored part is {the accent part}. It MUST perform the move, not
> decorate. {value rule, from the next section}

## Value rules

- **Dark/bold palettes**: {how the body reads — dark fill or light with ink
  outline; what color the eyes are}.
- **Light palettes**: {how the body reads — per the value-follows-palette
  rule in character.md}.

## Personality

{Default: an earnest, low-key operator doing something slightly absurd with a
straight face. Adjust wording, never the deadpan.}
```

## 4. Generate model-sheet candidates

Render each concept as a clean reference sheet — no scene, no labels. Use the
prompt template below per concept, `--count 2`, aspect `1:1`, into a fresh
`newrun` dir; build a `gallery` and let the user pick (or iterate). No `--ref`
on the first round — there is nothing to lock to yet.

```text
A 1:1 square character reference sheet (model sheet) for a recurring
editorial mascot, on a plain empty paper background — no scene, no props, no
labels, no text anywhere.

CHARACTER — "{name}", {what it is}: {the prompt spec paragraph from step 3}.
Cuteness comes from proportion and roundness only — no extra parts, no
accessories, no face details beyond the two dot eyes.

POSE: one large clean front-facing full-body view, centered, occupying about
60% of the frame, standing neutral with arms relaxed at the sides.

LINE LANGUAGE: ONE bold, even-weight, softly-rounded outline (a clean
vinyl-sticker line), nothing thin or scratchy.

STYLE: risograph print — grainy halftone texture, slight ink-layer offset,
faint paper grain, flat fills, no gradients, no soft shadows.

PALETTE: paper warm white #fffef7. Structure ink near-black #111111. Accent
fluoro pink #ff3d9a ONLY on {the accent part}.
```

(Use the user's own palette hexes instead if they already have one — the
reference conditions the character's *shape*; palette stays per-image.)

QA each candidate against the guardrails in `character.md`: deadpan (no
mouth/brows), no extra parts, one accent part only, silhouette reads at small
size. Reject before showing, and tell the user why a concept was re-rolled.
Iterate at most ~2 rounds; if a concept keeps drifting, that is the concept's
fault — return to step 2.

## 5. Install the pack

Pick a pack name — usually the character's name, lowercase kebab-case. With a
winner chosen:

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
so the user sees it on-model in action.

Packs are folders: remove one to retire it, copy it to another machine to
install the character there. If the user wants to share it with everyone,
offer to publish it to the community repo — `references/pack-sharing.md`.

## Styled reference sheets (far styles)

A reference's own rendering leaks into styles far from it (worst: pixel). To
use a character in such a style, derive a styled instance of its model sheet
once: re-run the step-4 sheet prompt with the style file's STYLE / LINE
LANGUAGE blocks and character treatment substituted in, passing the canonical
`reference.png` as `--ref`; QA against the style's deltas plus the character
guardrails; save the winner as `reference-<style>.png` beside the canonical
sheet. Scenes in that style then use it as the `--ref` (SKILL.md step 5).
Near styles (riso ↔ woodcut ↔ blueprint) don't need this — the canonical
sheet carries identity cleanly.
