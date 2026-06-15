# The character

Every Illo image stars one recurring mascot — the subject of every scene,
never decoration. The rules in the first half of this file apply to **any**
character (the shipped default or a custom one); the second half is the
shipped default, **Blot**, and the custom-pack format that replaces it.

## Rules for any character

### Anti-complexity guardrails

The fastest way to ruin a recurring character is detail creep. A character is
a small set of **locked** choices, and nothing else:

- **One simple silhouette** — one body shape that reads at any size (the
  house default favors a single soft geometric form; cuteness comes from
  proportion and roundness, never from added parts). Bipedal is the default,
  not a rule — a quadruped or other body plan is fine if the outline stays
  simple and the character can still perform a move.
- **A locked face** — the face is the pack author's choice, but it must be
  **exactly specified** and identical in every render. The house default —
  two dot eyes, blank deadpan, no eyebrows, no mouth — is the most
  drift-resistant face there is; a mouth, brows, or another simple face is
  fine when the locked design pins it down in render-checkable terms ("a
  thin flat structure-ink mouth", not "a friendly smile"). Faces are where
  renders drift first: every extra feature is a consistency cost.
- **Simple limbs** — enough to perform a move (house default: small stubby
  arms and legs, no hands or detail).
- **ONE accent carrier** — a single small part that takes the palette's accent
  color (a tip, a fold, an antenna ball). Everything else is structure ink or
  paper. Unlike the face and limbs, this is **not a per-pack choice** — the
  palette system and the accent-discipline QA check depend on exactly one.

**Nothing unlocked appears.** Panels, seams, bolts, gauges, UI, text on the
body, hats, clothing, accessories, extra appendages — allowed only when the
locked design names them explicitly, and then they must appear in every
render. If a render adds a part the spec doesn't have, re-roll; if renders
keep dropping or mutating a locked part, the design has too many parts —
simplify. A concept that *needs* many parts or text to read as itself will
not survive generation.

A body **material** (built from paperclips, bricks, yarn) is a *treatment*,
not a part: lock the material and how it reads ("a donkey built of
interlocking oversized paperclips"), then judge consistency **in aggregate**
— every render must read as that material at a glance, but individual units
may shift run to run the way hatching does. Locked parts are checked
one-by-one; locked treatments are checked as a whole.

### A style may own a richer profile

The guardrails above are the house defaults, tuned for the minimalist bundled
looks. A **style/look file may deliberately loosen them** for its medium, as
long as the structural invariants still hold: one readable silhouette, exactly
ONE focal accent, a load-bearing performance, and an exactly-locked,
reproducible design. A layered-craft look like `felt`, for example, builds the
body from many stacked felt pieces in several colors and pins a fuller cute
face (dot eyes + a small stitched mouth + cheeks) — the richness lives in a
**locked layer treatment judged in aggregate** plus a **multi-color body with
one focal accent**, never in loose extra parts. When a pack's `Style:` names
such a look, that look file's "Character treatment" section governs: read it,
and judge the pack by the structural invariants plus the look's own QA deltas,
not by the house minimalism.

### Value-follows-palette (critical)

The character is built with the same value logic as the rest of the scene, so
it never becomes a foreign blob:

- **Dark/bold palettes** (e.g. `ink-punch`): the body may read dark — its
  darkest feature is the deepest value in the scene.
- **Light/warm palettes**: the body is **light/cream with the structure-ink
  outline** (built like the props), and any dark feature uses the **structure
  ink, not pure black**.

When in doubt in a light palette: light body, charcoal (not black) features.

### The character must be load-bearing

The mascot performs the idea's one move — wedged in the neck, cranking the
press, holding the gate, hauling the load. Quick check: mentally **paint the
character out of the sketch.** If the picture still explains itself, it was a
sticker — rebuild the scene so the move can't happen without the character in
it.

### Personality

The house default: an earnest, low-key operator doing something slightly
absurd with a straight face — calm, deadpan, competent, never zany or
cute-for-cute's-sake. A pack may define its own personality; whatever it is,
keep it consistent, and remember the idea is carried by the **move**, not the
face — expression is seasoning, never the message.

### Naming

In generation prompts, describe the character by its **design**, not its name —
image models render the description, not the proper noun. Use the name in
human-facing copy, captions, and shot lists. A good name reads off the design
(an ink drop is a *blot*).

When a name *doesn't* read literally off the subject (an ox named `yoke`, a
mole named `mole` is fine but a robot named `blip` is not), give the pack an
optional **`Aliases:` line** so users can summon it by what it is — "use ox"
→ `yoke`. List the subject and common synonyms, comma-separated:

```markdown
Aliases: ox, zebu, oxen
```

Aliases are selection keys like the name, so the same global-uniqueness rule
applies: an alias must not collide with another pack's name or alias, the
shipped `blot`, or any look name. Absent line = name-only selection (the
agent can still match on the subject prose, just less reliably).

## Blot — the shipped default

**Blot** is the default mascot: a small ink drop. Style: riso. The model
sheet is `assets/character-reference.webp` — the engine conditions on it (see
SKILL.md). (`assets/character-reference-pixel.png` is the sheet behind the
pixel look's calibration example — a ready-made base for a `blot-pixel`
variant pack.)

### Locked design

- **Body**: a plump rounded ink-droplet — a fat, soft teardrop, wide at the
  bottom, narrowing to a gently curved tip at the top.
- **Face**: two simple dot eyes directly on the body, blank deadpan.
- **Accent carrier**: the **droplet tip** — the only accent-colored part.
- Small stubby arms and legs.

### Blot's value rule

- **Dark/bold palettes**: the body is filled solid with the structure ink (a
  literal drop of ink); the eyes are paper/warm-white dots.
- **Light palettes**: the body is light/cream with the structure-ink outline;
  the eyes are structure-ink dots. The accent tip stays accent in both.

### Prompt spec (drop into the CHARACTER slot of the recipe)

> the recurring mascot — a plump rounded ink-droplet body (a fat soft
> teardrop, wide at the bottom, narrowing to a gently curved tip at the top),
> two simple dot eyes, blank deadpan (no eyebrows, no mouth), small stubby
> arms and legs; the ONLY accent-colored part is the droplet tip. It MUST
> perform the move, not decorate. {value rule: in a dark palette the body is
> filled with the structure ink and the eyes are warm-white; in a light
> palette the body is LIGHT with a structure-ink outline and structure-ink
> eyes}

## Custom character packs

A character pack is a self-contained folder
`${XDG_CONFIG_HOME:-~/.config}/illo/characters/<name>/` — the folder name is
the pack name, and the `doctor` subcommand lists what's installed:

- `character.md` — the written spec: name, locked design, a **prompt spec**
  paragraph for the CHARACTER slot, value rules, a `Style: <name>` line (the
  pack's one look — a bundled or custom style; absent = riso), an optional
  `Aliases:` line (subject synonyms for "use ox"-style selection; see
  Naming above), and (optionally) personality notes. Everything in "Rules
  for any character" above still applies.
- `reference.png` — the character's model sheet, passed as `--ref` in place
  of the default's. It is rendered **in the pack's style**, so sheet and
  scenes always match.

One pack, one look. The same character in a different style is a sibling
**style variant pack** (`<name>-<style>`, e.g. `blot-woodcut`) — built
deliberately via `references/character-builder.md`, "Style variants", with
its own sheet and preview.

A user can keep several packs and pick one per run by name; which character
wins is SKILL.md step 2. Packs are portable — copying the folder to another
machine (or sharing it) installs the character. To design and install one
interactively, follow `references/character-builder.md`.
