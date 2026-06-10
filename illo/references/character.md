# The character

Every Illo image stars one recurring mascot — the subject of every scene,
never decoration. The rules in the first half of this file apply to **any**
character (the shipped default or a custom one); the second half is the
shipped default, **Blot**, and the custom-pack format that replaces it.

## Rules for any character

### Anti-complexity guardrails

The fastest way to ruin a recurring character is detail creep. A character is
exactly four things, and nothing else:

- **One simple silhouette** — a single soft geometric body, readable at any
  size. Cuteness comes from proportion and roundness, never from added parts.
- **Two dot eyes, blank deadpan** — no eyebrows, no mouth, no shiny/anime
  eyes, ever. The straight face is the house personality.
- **Stubby arms and legs** — enough to perform a move, no hands or detail.
- **ONE accent carrier** — a single small part that takes the palette's accent
  color (a tip, a fold, an antenna ball). Everything else is structure ink or
  paper.

Never add: panels, seams, bolts, gauges, UI, text or expressions on the body,
hats, clothing, accessories, extra appendages. If a render adds any of these,
re-roll. Simpler is more on-model and more reproducible — and a concept that
*needs* extra parts or text to read as itself will not survive generation.

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

An earnest, low-key operator doing something slightly absurd with a straight
face. Calm, deadpan, competent, never zany or cute-for-cute's-sake.

### Naming

In generation prompts, describe the character by its **design**, not its name —
image models render the description, not the proper noun. Use the name in
human-facing copy, captions, and shot lists. A good name reads off the design
(an ink drop is a *blot*).

## Blot — the shipped default

**Blot** is the default mascot: a small ink drop. The canonical model sheet is
`assets/character-reference.png` — the engine conditions on it (see SKILL.md).

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
  paragraph for the CHARACTER slot, value rules, and (optionally) personality
  notes. Everything in "Rules for any character" above still applies.
- `reference.png` — the character's canonical model sheet, passed as `--ref`
  in place of the default's.

A user can keep several packs and pick one per run by name; which character
wins is SKILL.md step 2. Packs are portable — copying the folder to another
machine (or sharing it) installs the character. To design and install one
interactively, follow `references/character-builder.md`.
