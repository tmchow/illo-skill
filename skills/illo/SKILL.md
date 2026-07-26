---
name: illo
description: >-
  Creates original editorial illustrations where a recurring mascot
  character performs the idea — one caught scene by default, a hand-built
  explainer diagram (a flow, fan-out, timeline, loop, or stack) when the
  structure itself is the point, or a transparent character cutout
  (pose-only compositing asset, no scene or text) — in one of seventeen bundled
  looks (sixteen print, plus a photoreal toy-brick set). Also handles
  "surprise me" / "random" (optionally scoped to a focus or character): rolls
  provenance, builds three saying candidates, picks via interactive choice or
  auto-pick-best (`--autopick`), and renders one image. Triggers only when
  the skill is directly invoked or "illo" is requested; never on generic
  illustrate / draw / make-an-image requests.
# x-release-please-start-version
version: 0.32.0
# x-release-please-end
argument-hint: "[idea or article URL] | build a character | install <character> | surprise me [focus] [--autopick] [using character]"
author: Trevin Chow
license: MIT
metadata:
  hermes:
    tags: [illustration, riso, image-generation, editorial, mascot, codex, grok, openrouter]
    category: creative
    requires_toolsets: [terminal]
  openclaw:
    emoji: "🎨"
    homepage: https://illo-skill.com
    os: [macos, linux]
    requires:
      bins: [python3]
---

# Illo

Make original, distinctive editorial illustrations for written content. One
image explains one idea: a key judgment, a flow, a before/after, a trap, a
loop. A **recurring mascot** is the one performing the idea in every scene —
the subject, never decoration. When one idea advances through stages, it can
be a **mini-comic**: 2–4 panels inside a single image. And when the idea is
itself a traceable structure — a pipeline, a fan-out, a timeline, a loop —
it can be an **explainer**: the same mascot and look drawing the structure
as a hand-built sketch-diagram with arrows and callouts
(`references/composition.md`, "Two registers"; editorial scene is always
the default). Or a **character cutout**: the mascot alone on a transparent
PNG for downstream overlay — pose and contact continuity only, no idea, no
text, no environment (`references/cutout.md`).

This is a configurable house style, not a generic image generator. The
**methodology is the constant**; the **character pack and palette are the
parameters** — and a character pack carries its **style** with it: one look
per pack, chosen from the bundled look library (riso — grainy halftone,
ink-layer offset, paper grain, one bold softly-rounded outline — plus
blueprint, woodcut, pixel, clay, manila, chalk, phosphor, enamel,
gouache, felt, diorama, sketchbook, bricks, fizz, bloom, and snes) or a custom style file. The default mascot is
**Blot**, a deadpan ink-drop in riso. Palettes come
from presets, the user's own palette file, or one derived color. Whatever the
parameters, it is intentionally not a photo — with one deliberate exception, the
`bricks` look, a toy-brick photography style — not a logo, not a corporate
infographic, not a formal flowchart, not a UI mockup.

## Use cases — route the request

| The user wants | The path |
|---|---|
| **Illustrate an article / post / newsletter / URL** | Steps 0–7: route the source first (thesis → coverage: hero / hero+set / set / mini-comic — `references/composition.md`, "Source routing"), then shot list (hero row + anchors), one image per anchor, interleave by placement. |
| **One image for a single concept** | Step 1 concept branch (up to ~3 quick questions if the idea is thin), then a single image. |
| **Surprise / random** — "surprise me", "random", "surprise me with art quote using bray", "surprise me --autopick" | Read `references/surprise.md` in full: Step 0 first, then character + provenance (ignore `defaultCharacter`; `* quote` forces a cited quote; else ~1/3 roll), build **three** safe candidates, interactive picker or auto-pick-best (`--autopick` preferred for schedulers), then register from the locked saying, then Steps 3–7 as one image. Deliver saying + image. Poster titles default off; mini-comics still get per-panel labels. |
| **A sequence — process, before→after, fail→fix** | One **mini-comic** when the progression sits in one place (shape routing in `references/composition.md` — the idea picks the shape, the destination never does). |
| **A traceable structure** — "show the flow", "diagram the pipeline", "map the steps", "as an explainer" | The **explainer register** (`references/composition.md`, "The explainer register"): a hand-built flow / fan-out / timeline / loop / stack / system slice in the active look, the mascot a working part of it. Also reachable without the phrases when a unit's thesis IS the structure (the register gate). |
| **Social-ready art for X posts / article body images** | 16:9 (or 1:1 when square is explicitly useful), bold `ink-punch`, watermark with the `x` handle if configured or asked. |
| **X Article banner / hero image** | Use the unique banner format: **1536 × 640 px** when the user asks for an X Article hero/banner. Prompt and render through the normal `illo.py generate` image pipeline, with normal, undistorted character/object proportions and crop-safe breathing room. Do not satisfy this by manually compositing or rebuilding crops from another image unless the user explicitly asks for post-processing. |
| **Blog / brand / site-matched art** | A named or custom palette, or derive the palette from one dominant color (`references/palettes.md`). |
| **Their own mascot** — "make me a character", "use our mascot", "replace Blot" | The character builder: read `references/character-builder.md` in full and follow it end to end. |
| **Community characters** — "what characters are available", "install blip", "update mole", "publish my character" | `references/pack-sharing.md` — engine `packs list/show/install/update`, publish via a GitHub PR. |
| **A different look** — "in blueprint", "woodcut style", "pixel version of blip" | Styles travel with character packs: build a **style variant pack** via `references/character-builder.md`, "Style variants". |
| **Options to pick from, or "which model is best"** | Step 5b: `--count` variations or a model loop → `gallery` with a recommendation. |
| **Fix an existing image** (stray title, recolor, mascot too decorative) | Edit prompts in `references/prompt-recipe.md`, passing the image back as `--ref`. |
| **Character cutout / transparent PNG / overlay sticker** — "just the mascot", "no background", "paste on something else" | The **cutout register** (`references/cutout.md`): read in full, prompt from `references/prompt-recipe.md` "Cutout variant", generate with `--cutout` and `--aspect 1:1`. OpenRouter cutouts default to GPT Image 2 (not Grok). Not for explaining an idea — reroute to editorial if the ask needs a scene. |

## Prerequisites

The engine (`scripts/illo.py`, stdlib Python, no installs) renders through one
of **three backends**; `python3` and network access are the only hard
requirements.

**Running the engine — set `$SKILL_DIR` inline in each block.** Every engine
command below is `python3 "$SKILL_DIR/scripts/illo.py" …`. Set `SKILL_DIR` to the
absolute path of the directory this `SKILL.md` was loaded from (it contains
`scripts/illo.py` and `assets/`) **in the same command block that uses it** — shell
state does not persist between separate command runs, so a value set in an earlier
block is gone by the next. If the harness does not expose that path, find the
installed `scripts/illo.py` and use its parent; if neither resolves, stop rather
than guessing the working directory. The engine self-locates its own bundled
assets, so `$SKILL_DIR` only has to be right enough to launch `illo.py` and to
point `--ref` at the bundled character sheet.

Write the block **flatten-safe** — some hosts (Codex observed) collapse a fenced
block to one line, turning a newline into a space. Terminate the assignment with
`;` (`SKILL_DIR="…";` — without it, a flattened `SKILL_DIR="…" python3 "$SKILL_DIR/…"`
becomes an env-prefix whose `$SKILL_DIR` expands to empty **before** the assignment
applies, so the path collapses to `/scripts/illo.py`). Put **no comment on an
assignment or command line** (a flattened `#` comments out the rest of the line and
the command silently vanishes), and keep each invocation on **one line** (a
flattened `\` continuation injects stray arguments). A wrong or unset value makes
`doctor` (Workflow step 0) fail loudly (`can't open file …/scripts/illo.py`) — the
signal to fix the path, not a skill fault.

- **Codex backend (free for Codex subscribers).** When the host has a usable
  **Codex CLI** — installed, `codex login`-ed, with the `image_generation`
  feature — illo can generate through the user's Codex subscription at no
  per-image charge (it draws on their Codex quota). No API key, no token: illo
  only shells out to the user's own CLI. Detected, not assumed; gpt-image-2 is
  automatic; unsupported on Windows/WSL.
- **Grok backend (free for Grok/xAI subscribers).** When the host has a usable
  **Grok CLI** — installed and `grok login`-ed — illo can generate through the
  user's Grok subscription via `grok -p` (headless), drawing on their Grok
  quota. Same env-free, token-free subprocess design as Codex. **Grok returns
  JPEG with no alpha, so it cannot make transparent cutouts** — those auto-fall
  back to a cutout-capable backend. The image tool exposes no model selector.
- **OpenRouter backend (paid, direct or explicit fallback).** Needs an
  **OpenRouter API key** in the user's config file — the **single credential
  channel** — written once by the user-run `init` (mode 600). The engine never
  reads secrets from the environment and never accepts them as command-line
  arguments. A host without a subscription CLI can select this path directly.
  A failed Codex/Grok render does **not** spend money automatically: paid
  fallback requires `--allow-paid-fallback`. It is **model-selectable**
  (`--model`).

Capsule of the backend model (resolution and precedence, the CLI requirements,
the built-in image tool being automatic, quota vs. charge, cutout limits,
Windows/WSL, fallback): **read `references/backends.md` in full before choosing
or explaining a backend** — the mechanics live there, once.

### Setup is the user's job (never enter the key yourself)

Entering an API key is something the **user** does. Do not type, paste, print,
or store the user's key — direct them to bootstrap it:

- **Bootstrap (user runs it):** `python3 "$SKILL_DIR/scripts/illo.py" init` —
  prompts for the key at a hidden prompt (never echoed) and writes the
  YAML config `${XDG_CONFIG_HOME:-~/.config}/illo/config.yaml` (mode 600). It
  can also store non-secret defaults: `--model`, `--palette`, `--aspect`,
  `--character`, `--watermark`. Use `--no-key` to update preferences without
  touching the stored key. (The config is read via PyYAML when installed;
  without it a minimal built-in parser still reads the flat keys — `apiKey`,
  `model`, … — so generation needs no installs. Only nested settings like
  `watermark` need PyYAML: `python -m pip install 'PyYAML==6.0.2'`.)
- **Non-secret prefs may be seeded** for the user with the same command and
  `--no-key`, but the key itself is theirs to enter.

### Hermes Agent only: binary asset repair preflight

Some Hermes versions corrupt binary files (the bundled character sheets) when
installing multi-file skills from GitHub — text files survive, binaries don't,
and a corrupted sheet silently breaks the character lock. **Under Hermes
Agent**, run this once before first use (and whenever `doctor` reports
`assets: CORRUPTED`):

```bash
bash ${HERMES_SKILL_DIR}/scripts/repair-hermes-assets.sh
```

It verifies every bundled binary against known-good SHA256 hashes
(`assets/checksums.txt`) and re-downloads only mismatched files from pinned,
immutable URLs — a no-op when everything checks out. Under Claude Code,
Codex, OpenClaw, or any runtime that installs faithfully: skip this; `doctor`
checks asset integrity everywhere and will say if repair is ever needed.

## Read these references as needed

Do not load everything at once. Pull the file that matches the step:

- `references/visual-style.md` — riso, the house default look: the risograph technique, line language, paper/ink, hard do/don'ts.
- `references/styles/<name>.md` — the rest of the look library (`blueprint`, `woodcut`, `pixel`, `clay`, `manila`, `chalk`, `phosphor`, `enamel`, `gouache`, `felt`, `diorama`, `sketchbook`, `bricks`, `fizz`, `bloom`, `snes`), consumed by character packs. Read the active character's style file in full before generating.
- `references/character.md` — the character rules (the load-bearing test, anti-complexity guardrails, value-follows-palette), the default character **Blot**, and the custom-pack format. Read before any character work.
- `references/character-builder.md` — the guided flow for designing and installing a user's own mascot. Read in full before building or replacing a character.
- `references/pack-sharing.md` — installing characters from the community repo and publishing a pack via PR. Read before any install/publish request.
- `references/palettes.md` — named presets, default resolution, custom palettes, **and the derive-a-palette-from-one-color algorithm**. Read in full before choosing or deriving any palette.
- `references/composition.md` — the two registers (editorial scene / explainer diagram) and the explainer's structure types and budget, stagings, turning an idea into a move, the no-recycled-composition rule, and the shot-list format.
- `references/cutout.md` — the cutout register: transparent compositing assets, contact continuity, pose vocabulary, and generate flags. Read in full before any cutout request.
- `references/surprise.md` — surprise / random mode: preflight-first, scope parse, random character, provenance variety + three saying candidates (optional parallel verify for sourced modes), interactive picker or `--autopick` / auto-pick-best, full re-roll on refresh, register after the locked saying, saying bar + sense bar, multi-source quote verification, safety-before-offer, headless contract. Read in full before any surprise/random request.
- `references/backends.md` — the three-backend image engine: how the backend resolves (precedence Codex > Grok > OpenRouter, and the self-identify rule), the Codex/Grok CLI requirements, artifact-first success, the built-in image tool being automatic (no model selection), quota-vs-charge, Grok's no-cutout limit, Windows/WSL, and opt-in paid fallback. Read before choosing or explaining a backend.
- `references/models.md` — the model lineup (**OpenRouter backend only**): friendly-name → OpenRouter id map, traits, aspect caveats, 404/fallback handling. Read before passing any `--model`.
- `references/prompt-recipe.md` — the generation prompt template and the edit/recolor prompts.
- `references/quality-bar.md` — the post-generation checklist and iteration rules. Read before delivering.

`assets/character-reference.webp` is the default character's canonical model
sheet — the consistency anchor (used by the engine, below); a custom pack
brings its own. Style-calibration examples are **not bundled** — each style
file links its own by URL (fetch when needed): study line density, negative
space, and accent restraint. **Never copy their compositions** — invent a
fresh metaphor for the current piece.

## Workflow

### 0. Preflight

Before generating, confirm the engine is ready:

```bash
SKILL_DIR="<path to this skill>";
python3 "$SKILL_DIR/scripts/illo.py" doctor
```

Run the `illo.py` call standalone — never chained with `&&` — so the displayed exit code is
the readiness signal itself (0 = ready): a chained neighbor's failure paints
a healthy check as an error.

It reports python, the config path, the resolved model/palette defaults,
whether a **custom character pack** or **custom palettes file** exists,
**Codex/Grok CLI detection and the resolved backend/transport**, and whether an
OpenRouter key is found (without revealing it); exit 0 = the resolved backend
is ready. An OpenRouter-only install (no subscription CLI) stays exit 0 —
readiness follows the resolved backend, not a hardwired key check
(`references/backends.md`).

**Config migration — surface the backend choice interactively.** If `doctor`
reports `backend: NEEDS CHOICE` (or `generate` hard-stops saying the config "is
out of date"), this user's config predates the backend choice — they have an
older install and have never been offered a subscription CLI. Do **not** pick
for them silently. Surface an **interactive choice** using the platform's
blocking-question capability (`AskUserQuestion` in Claude Code, the equivalent
elsewhere; where the host has none — e.g. a plain chat session — ask the same one
choice as a concise message and wait for the reply, never picking silently):
"illo now has three image backends — which would you like?" with
three options — **Codex** (free, your Codex subscription), **Grok** (free, your
Grok subscription; no transparent cutouts), and **OpenRouter** (pick the model:
Grok Imagine, Nano Banana, GPT Image, and others). Persist the answer without
touching any existing key:
`python3 "$SKILL_DIR/scripts/illo.py" init --backend <codex|grok|openrouter> --no-key`,
then continue. A brand-new install (no config at all) is ordinary onboarding,
not this migration — it does not fire.

**Prefer your own CLI when you are a subscription-CLI agent.** The engine's
auto-default reads *host* capability (**Codex > Grok > OpenRouter**; it can't
tell which agent invoked it) — but **you know which agent you are**. So when you
are a subscription-CLI agent and your own CLI is usable on this host, add your
own backend flag to `generate` for non-cutout renders: the **Grok agent** adds
`--backend grok`, the **Codex agent** adds `--backend codex`. This keeps "in
Grok, generate with Grok" true even on a host that also has Codex, with no
runtime-sniffing in the engine. Cutouts ignore this (Grok can't make them — they
auto-fall back). A user's config `backend:` overrides everything. Resolution and
precedence mechanics: `references/backends.md`.

Read the printed **config path** before concluding
the key is missing: under Hermes,
multi-profile setups can resolve `HOME`/`XDG_CONFIG_HOME` to *another*
profile's home (e.g. `…/profiles/<name>/home/.config/illo/…`), so a key
that exists looks absent. If the path points at the wrong profile, re-run
with the right `HERMES_HOME`/`HOME`/`XDG_CONFIG_HOME` rather than treating
the key as missing. If the key is genuinely
**missing**, stop and ask the user to run
`python3 "$SKILL_DIR/scripts/illo.py" init` themselves — do not enter the
key for them. In a **chat session** the user can't run commands where they
are, so shrink their host-side step first: run `init --no-key` yourself
(allowed — it scaffolds the config with defaults and a commented `# apiKey:`
placeholder, mode 600, never touching a key), then offer the user two
equivalent one-time options **on the machine the agent runs on** (that host
is theirs — it's where they installed the agent): run
`python3 <resolved absolute $SKILL_DIR>/scripts/illo.py init` (hidden
prompt), or open `~/.config/illo/config.yaml` and fill in the `apiKey:`
line. The key must never transit the chat: never ask for it in a message,
and if the user pastes it anyway, do not use it — tell them to revoke that
key at openrouter.ai and set a fresh one on the host (the pasted key now
lives in chat history and platform servers). Never copy a key from the
environment or any other store into the config yourself — the user is the
only writer of that line — with **one scoped exception**: an ephemeral
cloud workspace (Claude Code web, Codex cloud, CI) where the user
provisioned `OPENROUTER_API_KEY` through the platform's secrets mechanism.
That provisioning is itself the user's deliberate, workspace-scoped
consent, and there is no interactive prompt or persistent home for `init` —
so there, seed the config from the workspace secret once (the "Cloud & CI"
one-liner in README.md). On a personal machine an ambient env var proves
nothing about intent (it may belong to other tools) — the rule stands:
never copy it.

### 1. Read the input — and clarify a thin concept (briefly)

Three kinds of input, handled differently:

- **Surprise / random** ("surprise me", "random", "surprise me with art quote
  using bray", "surprise me --autopick", and close variants) — the ask is
  invent-and-render, not a supplied thesis. **Stop and read
  `references/surprise.md` in full**, run Step 0 first, then resolve character
  and provenance there (ignore `defaultCharacter`; random character when
  unnamed), build three saying candidates and lock one via picker or
  auto-pick-best, pick register from the locked saying, then continue Steps
  3–7 as one image — Steps 0 and 2 are skipped in that render pass because
  preflight and pack are already done. Do not enter the thin-concept Q&A path
  below. A prompt that already names a concrete idea ("illustrate 'you are
  the bottleneck'") is **not** surprise mode even if it also says "surprise
  me".
- **A URL / article / paste / long post** carries its own context — but
  never generate from the first vivid detail. Route it first
  (`references/composition.md`, "Source routing"): classify the source's
  **shape and genre**, infer the **requested artifact's job** (what this
  image must do for its audience), separate that job from the source's most
  drawable mechanism, **lock the main thesis in one sentence** (a hero locks
  the source/artifact job, not its loudest evidence — the genre guardrails
  say what each genre heroes), then pick the coverage — hero, hero +
  per-section set (the full article job), set, mini-comic, or shot list
  first. Sets need placements: compact sources (a tweet, one
  concept) never yield a set — their multi-beat form is the mini-comic. Pull the **load-bearing moments** —
  the few places that turn on a judgment, a loop, an input→output, a
  before/after, or a trap — never one image per paragraph. The text already
  says what it's about, so don't interrogate the user, with **one
  exception**: a materially multi-beat source (long article, postmortem,
  multi-claim launch) gets a single coverage question before any
  multi-image spend — unless the user already named the coverage. A lone
  image from a multi-beat source is a **hero**, delivered saying so — not
  as coverage of the piece.
- **A bare concept or one-liner** (e.g. "illustrate 'you are the bottleneck'")
  usually underspecifies the picture. Ask **up to ~3 quick questions — only the
  ones that change the output — then build.** Draw from:
  - the single takeaway (what should the reader conclude?),
  - where it's headed (blog / deck / X post / X article body / X Article banner → sets palette, aspect, pixel normalization, and watermark),
  - the shape: one image (the default), a **mini-comic** (2–4 panels in one
    image — only when the idea itself advances through stages), or several
    separate images — plus any must-include element or constraint. The shape
    follows the idea, never the destination (`references/composition.md`).

  Keep it to **one short round**, then proceed. **Skip the questions entirely**
  if the user already gave enough, said "just make it" / "single shot", or
  the answer is obvious from context. Never block a clear request by asking.

### 2. Resolve the character

**Surprise / random mode:** skip this step — character was already resolved
in `references/surprise.md` (named pack, or random among installed + Blot;
never `defaultCharacter`). Continue at Step 3+.

Installed packs live under `${XDG_CONFIG_HOME:-~/.config}/illo/characters/`
(format and location details: `references/character.md`); `doctor` lists
what's installed. A user can keep several and pick per run. First match
wins:

1. **Explicit request** — "use <pack name>", "as <name>": that pack (or the
   shipped default when asked for by name, `blot`). When the word matches no
   pack name, resolve by **approximation**: match it against each installed
   pack's `Aliases:` line and subject (the `character.md` opening line and
   Locked design **Body**) — `doctor` prints names + aliases, so this needs
   no file reads in the common case — and against catalog `description`s
   (`packs list`). So "use ox" finds a pack subtitled an ox (e.g. `yoke`).
   On one clear match, use it and name it; on several, ask which; on none,
   say so before falling through.
2. **Config default** — `defaultCharacter` from the user config, if set.
3. **Shipped default** — **Blot** (spec in `references/character.md`, model
   sheet `assets/character-reference.webp`).

Once resolved, read the pack's `character.md` and use its prompt spec, value
rules, **`Cutout chroma:`** (for cutouts), and `reference.png` everywhere the
default's would be used.

When rerouting an article set to a new character — especially after a weak
attempt, or for a technical/platform essay — read
`references/article-set-character-reroute.md` in full before planning or
rendering. Do the legibility preflight there before spending renders.

If the user wants a *new* character, that is the character builder
(`references/character-builder.md`); if they want someone else's, packs
install from the community repo (`references/pack-sharing.md`). Either way,
install first, then continue here.

### 3. Plan (shot list) — when asked to plan, or for anything multi-image

If the user wants planning ("where should this be illustrated", "shot list"),
output a shot list before generating. Per image: placement, the one idea,
the artifact job, the register (editorial unless the row passes the explainer
gate), the staging (or structure type), **what the mascot is doing**, the
palette, and the text hierarchy — primary read/title when the artifact needs
one, plus short supporting labels/callouts within the per-register budgets in
`references/composition.md`. Let the anchor count drive how many (bands and the never-pad
rule are in `references/composition.md`). When a stretch of the piece advances
through stages **in one place**, plan a single mini-comic image there instead
of several — the mini-comic-vs-separate routing is in
`references/composition.md`.

For article-set character reroutes, add the mandatory preflight fields from
`references/article-set-character-reroute.md` before any render: section claim,
visual object/action, and reader mapping. Reject rows that need a private
metaphor glossary or more than one conceptual substitution.

### 4. Resolve the palette (the style is the character's)

**Style** is not separately resolvable: the active character's pack carries
it — the `Style:` line in its `character.md` names a bundled look
(`references/styles/<name>.md`, riso in `visual-style.md`) or a custom one at
`${XDG_CONFIG_HOME:-~/.config}/illo/styles/<name>.md`; absent line = riso.
Blot is riso. For any non-riso style, read its file in full: it supplies the
STYLE and LINE LANGUAGE prompt blocks, the palette mapping, the character
treatment, and extra QA checks. A request for the same character in a
*different* look is a variant-pack build (route table) — never restyle on the
fly.

**Palette**: read `references/palettes.md` in full and resolve there — it
holds the resolution order (explicit request, then destination cue via the
user's palettes file, then config default, then house `ink-punch`), the named
presets, custom palettes, and the derive-a-palette-from-one-color algorithm.
End with **concrete hex values**; when the pack's style isn't riso, run them
through that style's palette mapping.

### 5. Generate — reference-locked, one metaphor per image

**Cutout branch.** When the request routed to the cutout register, read
`references/cutout.md` in full first — it covers prompt shape (chroma
`BACKGROUND:` from the pack's **`Cutout chroma:`** line — green for forged
metal, magenta default), **registration-locked silhouette** (no ink-layer
offset), **`--cutout`** /**`--aspect 1:1`**, OpenRouter **`--image-config`**,
and manifest **`cutout_alpha`** disclosure. Read the active character's
`Cutout chroma:` in `character.md` before building the prompt; pass `--chroma`
only when re-rolling with the other screen. Codex does not emit native alpha —
transparency is chroma-keyed by the engine. Build the prompt from
`references/prompt-recipe.md`, "Cutout variant" — not the editorial template.
Only the character model sheet as `--ref` (no editorial style anchor, no
watermark). QA against the cutout section of `references/quality-bar.md`. Skip
the editorial shot-list / thesis steps.

**Editorial and explainer.** Build a full prompt per image from
`references/prompt-recipe.md` (scene + structure + communication hierarchy +
style + the active character's spec + resolved palette hexes + the
per-register text budget), write it to a file, and render it. **Pass the active character's
model sheet as `--ref` every time** — that reference conditioning is what
keeps the mascot on-model; style and palette come from the prompt, so both
stays swappable. A pack's sheet is born in its own style, so sheet and style
always match — no cross-style reference juggling. (Under Hermes Agent, the
asset-repair preflight above must have run before the first `--ref` use —
a corrupted sheet conditions every render on garbage.)

Set `SKILL_DIR` inline (see Prerequisites), and use the bundled sheet as `REF` — or
the active pack's `reference.png` for a custom character. Add `--model <id>` to
override the config/default model for this image (OpenRouter backend only):

```bash
SKILL_DIR="<path to this skill>";
REF="$SKILL_DIR/assets/character-reference.webp";
python3 "$SKILL_DIR/scripts/illo.py" generate --prompt-file /tmp/shot-01.txt --ref "$REF" --aspect 16:9 --out "assets/<slug>-illustrations/01-topic.png"
```

`illo.py generate` prints a **JSON line per image** (`{path, backend, model,
id, cost, width, height, label, prompt}`; `backend` is `codex`, `grok`, or
`openrouter`, and `model`/`id`/`cost` are OpenRouter-only — they are null on a
CLI-served record (Codex or Grok). `cost` is null unless `--cost` is passed —
`gallery` backfills it) and appends the same record to
`<out-dir>/manifest.jsonl`.
Read `.path` — it may differ from `--out`: the engine names the file by the
actual encoding (some models return JPEG bytes, so a requested `.png` lands
as `.jpg`). Use `.width/.height` to catch a square when 16:9 was requested
(re-roll). A failed Codex/Grok render stops by default even when an OpenRouter
key is configured. Add `--allow-paid-fallback` only when the user has explicitly
approved a pay-per-image retry. Direct `--backend openrouter` renders and the
intentional Grok-cutout redirect remain direct routes and do not need this flag.
Generate each image **separately** — never combine ideas into one canvas. Default
aspect is 16:9; use `1:1` for square social, `9:16`/`4:5` for vertical, and
`1536:640` for an **X Article banner / hero**. For X Article banners, the
platform target is **1536 × 640 px**. Generate through the normal image
pipeline; do not manually composite or rebuild the scene from crops as a
substitute for an illo render. Check `.width/.height`, and only do final
post-processing when it is a non-distorting resize/crop that preserves normal
proportions and all essential information. Never stretch or squash the art to
force exact dimensions. Pass `--label` for a caption that shows in the gallery.

**Sets read as one artist.** For any multi-image set, the first image that
**passes the full quality bar** (and, for a hero in a rerouted article set,
passes the thesis-legibility gate in
`references/article-set-character-reroute.md`; never anchor on an unvetted
render — a failed anchor, e.g. an off-palette ground or illegible metaphor,
would propagate its failure set-wide) becomes the set's **style anchor**: pass
it as a second `--ref` after the character sheet for every later image in the
set and for every re-roll of a set member, so line weight, halftone density,
and flat-vs-dimensional treatment stay consistent throughout. The same trick
locks style for a one-off: add any finished example as a second `--ref`.

**Model choice (OpenRouter backend only).** `--model` and config `model:` are
an **OpenRouter-only** axis — on the Codex backend the model is automatic
(gpt-image-2) and `--model` does not apply (`references/backends.md`). For the
OpenRouter path, read `references/models.md` in full before passing any
`--model` (or whenever the user names a model in plain language or asks for
"best quality" / "cheapest"): it holds the friendly-name → OpenRouter id
map, per-model traits, the aspect-ratio caveat, and the 404/fallback
handling. Resolution is `--model` > config `model` > built-in default.

**Watermark / attribution (optional, off by default).** The skill ships with
**no** default watermark — the text comes only from the user's `watermark`
config map (read from the config file) or an explicit request, so installers
never inherit someone else's handle. The resolution order, the prompt line to
append, and the two-render caveat are in `references/prompt-recipe.md`.

### 5b. Batches & comparison (only when it helps)

**Default to ONE image.** Fan out only when the user asks for options/comparison
or the piece is important enough to be worth it — and **say first what each
image costs**: on the Codex backend it draws on the user's Codex quota (no
per-image charge); on the OpenRouter backend it bills their OpenRouter account
(typically under ten cents per image, varying by model). Keep N small (2–4).
Orchestrate the loop with the engine's primitives:

`newrun` prints a fresh run dir (`/tmp/illo/<runid>`) into `RUN`. Record the user's
VERBATIM request (URL, pasted text, concept) to `request.txt` — the gallery shows
it as provenance so anyone can tell what the run was for. Adapt each `generate`
line below to a real path and run it on its own:

```bash
SKILL_DIR="<path to this skill>";
RUN=$(python3 "$SKILL_DIR/scripts/illo.py" newrun);
printf '%s' "<the verbatim request>" > "$RUN/request.txt"
# (a) VARIATIONS — same prompt+model, pick-the-best:
python3 .../illo.py generate --prompt-file p.txt --ref <ref> --count 4 --label "draft→ship" --out "$RUN/v.png"
# (b) MODEL COMPARISON — loop the SAME prompt over the chosen models
#     (full OpenRouter ids from references/models.md):
for m in <model-id-1> <model-id-2>; do
  python3 .../illo.py generate --prompt-file p.txt --ref <ref> --model "$m" --label "$m" --out "$RUN/$(basename $m).png"; done
# (c) CONCEPT VARIATIONS — different prompts (different stagings) for one idea:
python3 .../illo.py generate --prompt-file staging-A.txt --ref <ref> --label "as a funnel" --out "$RUN/a.png"
python3 .../illo.py generate --prompt-file staging-B.txt --ref <ref> --label "as a crossing" --out "$RUN/b.png"

python3 "$SKILL_DIR/scripts/illo.py" gallery "$RUN" --title "<the piece or request>" --open
# always pass --title so a saved gallery stays identifiable later;
# add --embed for a single portable file (images inlined)
```

Every `generate` self-records to `$RUN/manifest.jsonl`; `gallery` assembles them
into one page with each image's **label, model, dimensions, cost, and a
collapsible prompt** — the prompt toggle is what makes concept-variation
comparison readable (the prompt is the variable). Always present the gallery
**with a recommendation**, not a raw dump — and in a chat session, present
the labeled candidates directly in the chat instead of a gallery (delivery
routing in step 7). Multi-model failures are per-image
(an unavailable model errors that one render only); keep the rest.

### 6. QA and iterate

Check every image against `references/quality-bar.md`. Re-roll or edit when the
mascot is decorative or off its locked spec, the body is wrong-value for the
palette, label text sits on a colored fill, the accent has spread past the
character's accent part + 1–2 elements, an unwanted title bar appears, the
composition copies an example, or text is misspelled. Subject scale varies
run-to-run — re-roll if the subject is tiny (check `.width/.height` in the
JSON: a square back when 16:9 was requested → re-roll). When a re-roll
supersedes a render, rebuild any delivery gallery with
`--exclude <superseded label>` (repeatable) so rejected rolls don't appear in
the review artifact.

### 7. Deliver — match the session's medium

Copy finals next to the user's work when appropriate; never overwrite
existing assets without being asked. **Filenames carry the role** — they
are the only metadata that survives a document attachment, so make them
self-identifying: `00-hero-<slug>.png` for the hero, then
`01-<section-slug>.png`, `02-<section-slug>.png`, … for anchors in piece
order (`assets/<slug>-illustrations/`). Then report: how many images, the
palette used, which are strongest vs optional — and for any multi-image
job, a **placement map**: one line per image naming the file, its role
(hero, or after which section), and the one idea it lands, so the user can
drop each file where it belongs without re-deriving the plan. Deliver the
images themselves the way this session can actually show them:

- **Filesystem sessions** (IDE/terminal agents — Claude Code, Codex,
  Cursor): report each final's **absolute path** (the engine's JSON `.path`
  is already absolute) and present the gallery for multi-image runs. The
  file on disk already *is* the original — never emit `[[as_document]]`
  here: it's a Hermes gateway token, literal noise in any other runtime.
  If the runtime has its own in-chat file delivery, use that.
- **Chat sessions** (the user is on a messaging surface — Hermes over
  Telegram/Discord/WhatsApp, or any chat surface with lossy media delivery —
  and cannot open local files): a path alone is not a complete deliverable;
  the image must land **in the chat**, and a *final* must arrive as the
  **original file**. Platform photo delivery recompresses images — exactly
  what destroys riso grain, halftone texture, ink-layer offset, and fine
  hand-lettering — so **finals are delivered as document attachments**. On
  Hermes, tag each final with an explicit `MEDIA:` attachment tag — the tag
  is `MEDIA:` immediately followed by the absolute path, no space — and the
  literal directive `[[as_document]]` in the same reply. Do **not** rely on
  a bare absolute path for a final: bare paths can pass through to the user
  as literal text instead of being dispatched as an attachment.

  ```text
  MEDIA:/absolute/path/to/final.jpg
  [[as_document]]
  ```

  Candidate/options rounds may use normal inline photo delivery when quick
  glances help — say so ("preview — original file to follow") — but a
  final is never delivered that way. **Skip the HTML
  gallery in chat** — the user has no easy way to open or host it; send the
  labeled finals directly with the recommendation as text, and only build
  `gallery --embed` (one self-contained file) if a portable artifact is
  explicitly requested, delivering it with `[[as_document]]`.

Before the final reply in a chat session, check:

- every final's path came from the engine's JSON `.path`, not the requested
  `--out` (the actual extension may differ);
- every final appears as an explicit `MEDIA:/absolute/path` attachment tag
  in the reply;
- `[[as_document]]` is in the reply unless this is explicitly preview-only;
- rejected/re-rolled candidates are excluded from delivery;
- the text says what was made — character, palette, strongest final, and
  for sets the placement map (which file is the hero, which follows which
  section) — without implementation noise.

## Output discipline

Pre-generation planning is short and concrete. Post-generation, let the images
speak — report what was made and where, not style theory. Keep labels few and
short; the fewer words baked into an image, the more reliably it renders.
