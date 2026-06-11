---
name: illo
description: >-
  Creates original editorial illustrations in which a recurring deadpan
  mascot performs the idea (default mascot: Blot, an ink-drop) — article
  illustration sets, single-concept images, and 2–4 panel mini-comics, in one
  of ten bundled looks (riso, blueprint, woodcut, pixel, clay, manila, chalk,
  phosphor, enamel, gouache) or a custom style. This skill should be used ONLY
  when the request invokes it by name ("illo this post", "use illo on this
  article", "illo: draw blip hauling a crate") or uses its unmistakable
  vocabulary: "riso" / "risograph", or "character pack" (install, update,
  publish, switch, or build one). Also covers shot lists, named/derived/custom
  palettes, variation and model-comparison galleries, the character builder,
  style variant packs, and community pack install/publish. Do NOT trigger on
  requests that don't say illo/riso/character pack — not "illustrate this
  post", "make an image", "draw a cartoon", "make me a mascot", not
  photorealism, UI mockups, charts, or stock art.
version: 0.7.0
author: Trevin Chow
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [illustration, riso, image-generation, blog, editorial, mascot]
    category: creative
    requires_toolsets: [terminal]
  openclaw:
    emoji: "🎨"
    homepage: https://illo-skill.com
    os: [macos, linux]
    requires:
      bins: [python3]
    envVars:
      - name: OPENROUTER_API_KEY
        required: true
        description: >-
          OpenRouter API key used by scripts/illo.py to call the image model
          (default Grok Imagine; any OpenRouter image model via --model).
          May instead be stored in the user config via `illo.py init`.
---

# Illo

Make original, distinctive editorial illustrations for written content. One
image explains one idea: a key judgment, a flow, a before/after, a trap, a
loop. A **recurring mascot** is the one performing the idea in every scene —
the subject, never decoration. When one idea advances through stages, it can
be a **mini-comic**: 2–4 panels inside a single image.

This is a configurable house style, not a generic image generator. The
**methodology is the constant**; the **character pack and palette are the
parameters** — and a character pack carries its **style** with it: one look
per pack, chosen from the bundled look library (riso — grainy halftone,
ink-layer offset, paper grain, one bold softly-rounded outline — plus
blueprint, woodcut, pixel, clay, manila, chalk, phosphor, enamel, and
gouache) or a custom style file. The default mascot is
**Blot**, a deadpan ink-drop in riso. The same character in a different look
is a deliberate **style variant pack**, never a runtime swap. Palettes come
from presets, the user's own palette file, or one derived color. Whatever the
parameters, it is intentionally not a photo, not a logo, not a corporate
infographic, not a flowchart, not a UI mockup.

## Use cases — route the request

| The user wants | The path |
|---|---|
| **Illustrate an article / post / newsletter** | Steps 0–7: pull the load-bearing moments, shot list, one image per anchor, interleave by placement. |
| **One image for a single concept** | Step 1 concept branch (up to ~3 quick questions if the idea is thin), then a single image. |
| **A sequence — process, before→after, fail→fix** | One **mini-comic** when the progression sits in one place (routing in `references/composition.md`). Best shape for social. |
| **Social-ready art** | 16:9 (or 1:1), bold `ink-punch`, watermark with the `x` handle if configured or asked. |
| **Blog / brand / site-matched art** | A named or custom palette, or derive the palette from one dominant color (`references/palettes.md`). |
| **Their own mascot** — "make me a character", "use our mascot", "replace Blot" | The character builder: read `references/character-builder.md` in full and follow it end to end. |
| **Community characters** — "what characters are available", "install blip", "update mole", "publish my character" | `references/pack-sharing.md` — engine `packs list/show/install/update`, publish via a GitHub PR. |
| **A different look** — "in blueprint", "woodcut style", "pixel version of blip" | Styles travel with character packs: build a **style variant pack** via `references/character-builder.md`, "Style variants". |
| **Options to pick from, or "which model is best"** | Step 5b: `--count` variations or a model loop → `gallery` with a recommendation. |
| **Fix an existing image** (stray title, recolor, mascot too decorative) | Edit prompts in `references/prompt-recipe.md`, passing the image back as `--ref`. |

## Prerequisites

- **An OpenRouter API key.** Generation goes straight to OpenRouter's image API
  via `scripts/illo.py` (stdlib Python, no installs). The key resolves as
  `--api-key` > `$OPENROUTER_API_KEY` > the user config file. The env var is
  preferred (runtime-native); the config file is an optional convenience.
- **`python3`** and network access. Nothing else to install.
- The engine is **model-selectable** (`--model`); the default renders English
  labels reliably and honors a reference image for character consistency.

### Setup is the user's job (never enter the key yourself)

Entering an API key is something the **user** does. Do not type, paste, or write
the user's key — direct them to bootstrap it:

- **Bootstrap (user runs it):** `python3 "$SKILL_DIR/scripts/illo.py" init` —
  prompts for the key at a hidden prompt (never echoed) and writes the optional
  YAML config `${XDG_CONFIG_HOME:-~/.config}/illo/config.yaml` (mode 600). It
  can also store non-secret defaults: `--model`, `--palette`, `--aspect`,
  `--character`, `--watermark`. Use `--no-key` to set only preferences and
  leave the key to the env var. (The config file is read via
  PyYAML; without it the file is ignored and the tool runs from env var + flags,
  so generation stays install-free.)
- **You may seed non-secret prefs** for the user with the same command and
  `--no-key`, but the key itself is theirs to enter.

## Read these references as needed

Do not load everything at once. Pull the file that matches the step:

- `references/visual-style.md` — riso, the house default look: the risograph technique, line language, paper/ink, hard do/don'ts.
- `references/styles/<name>.md` — the rest of the look library (`blueprint`, `woodcut`, `pixel`, `clay`, `manila`, `chalk`, `phosphor`, `enamel`, `gouache`), consumed by character packs. Read the active character's style file in full before generating.
- `references/character.md` — the character rules (the load-bearing test, anti-complexity guardrails, value-follows-palette), the default character **Blot**, and the custom-pack format. Read before any character work.
- `references/character-builder.md` — the guided flow for designing and installing a user's own mascot. Read in full before building or replacing a character.
- `references/pack-sharing.md` — installing characters from the community repo and publishing a pack via PR. Read before any install/publish request.
- `references/palettes.md` — named presets, default resolution, custom palettes, **and the derive-a-palette-from-one-color algorithm**. Read in full before choosing or deriving any palette.
- `references/composition.md` — stagings, turning an idea into a move, the no-recycled-composition rule, and the shot-list format.
- `references/prompt-recipe.md` — the generation prompt template and the edit/recolor prompts.
- `references/quality-bar.md` — the post-generation checklist and iteration rules. Read before delivering.

`assets/character-reference.png` is the default character's canonical model
sheet — the consistency anchor (used by the engine, below); a custom pack
brings its own. `assets/examples/` are style-calibration samples only: study
line density, negative space, and accent restraint. **Never copy their
compositions** — invent a fresh metaphor for the current piece.

## Workflow

### 0. Preflight

Before generating, confirm the engine is ready:

```bash
python3 "$SKILL_DIR/scripts/illo.py" doctor
```

It reports python, the config path, the resolved model/palette defaults,
whether a **custom character pack** or **custom palettes file** exists, and
whether a key is found (without revealing it); exit 0 = ready. If the key is
**missing**, stop and ask the user to run
`python3 "$SKILL_DIR/scripts/illo.py" init` themselves (or to export
`OPENROUTER_API_KEY`) — do not enter the key for them.

### 1. Read the input — and clarify a thin concept (briefly)

Two kinds of input, handled differently:

- **An article / paste / doc** carries its own context. Read it and pull the
  **load-bearing moments** — the few places that turn on a judgment, a loop, an
  input→output, a before/after, or a trap. Don't illustrate every paragraph, and
  don't interrogate the user; the text already says what it's about.
- **A bare concept or one-liner** (e.g. "illustrate 'you are the bottleneck'")
  usually underspecifies the picture. Ask **up to ~3 quick questions — only the
  ones that change the output — then build.** Draw from:
  - the single takeaway (what should the reader conclude?),
  - where it's headed (blog / X / deck → sets palette, aspect, watermark),
  - the shape: one image, a **mini-comic** (2–4 panels in one image — right
    when the idea advances through stages, and best for social), or several
    separate images — plus any must-include element or constraint.

  Keep it to **one short round**, then proceed. **Skip the questions entirely**
  if the user already gave enough, said "just make it" / "single shot" /
  "surprise me", or the answer is obvious from context. Never block a clear
  request by asking.

### 2. Resolve the character

Character packs are named folders under
`${XDG_CONFIG_HOME:-~/.config}/illo/characters/<name>/`, each holding
`character.md` (the spec) + `reference.png` (the model sheet); the pack name
is the folder name, and `doctor` lists what's installed. A user can keep
several and pick per run. First match wins:

1. **Explicit request** — "use <pack name>", "as <name>": that pack (or the
   shipped default when asked for by name, `blot`).
2. **Config default** — `defaultCharacter` from the user config, if set.
3. **Shipped default** — **Blot** (spec in `references/character.md`, model
   sheet `assets/character-reference.png`).

Once resolved, read the pack's `character.md` and use its prompt spec, value
rules, and `reference.png` everywhere the default's would be used.

If the user wants a *new* character, that is the character builder
(`references/character-builder.md`); if they want someone else's, packs
install from the community repo (`references/pack-sharing.md`). Either way,
install first, then continue here.

### 3. Plan (shot list) — when asked to plan, or for anything multi-image

If the user wants planning ("where should this be illustrated", "shot list"),
output a shot list before generating. Per image: placement, the one idea,
the staging, **what the mascot is doing**, the palette, and the 1–3 short
English labels. Let the anchor count drive how many (bands and the never-pad
rule are in `references/composition.md`). When a stretch of the piece advances
through stages **in one place**, plan a single mini-comic image there instead
of several — the mini-comic-vs-separate routing is in
`references/composition.md`.

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

Build a full prompt per image from `references/prompt-recipe.md` (scene +
structure + style + the active character's spec + resolved palette hexes +
≤3 labels), write it to a file, and render it. **Pass the active character's
model sheet as `--ref` every time** — that reference conditioning is what
keeps the mascot on-model; style and palette come from the prompt, so both
stays swappable. A pack's sheet is born in its own style, so sheet and style
always match — no cross-style reference juggling.

```bash
SKILL_DIR="<path to this skill>"           # contains scripts/illo.py + assets/
REF="$SKILL_DIR/assets/character-reference.png"   # or the active pack's reference.png

python3 "$SKILL_DIR/scripts/illo.py" generate \
  --prompt-file /tmp/shot-01.txt \
  --ref "$REF" \
  --aspect 16:9 \
  --out "assets/<slug>-illustrations/01-topic.png"
  # --model <id> to override the config/default model for this image
```

`illo.py generate` prints a **JSON line per image** (`{path, model, id, cost,
width, height, label, prompt}`) and appends the same record to
`<out-dir>/manifest.jsonl`.
Read `.path` — it may differ from `--out`: the engine names the file by the
actual encoding (some models return JPEG bytes, so a requested `.png` lands
as `.jpg`). Use `.width/.height` to catch a square when you asked for 16:9
(re-roll).
Generate each image **separately** — never combine ideas into one canvas. Default
aspect is 16:9; use `1:1` for social, `9:16`/`4:5` for vertical. To lock style as
well as the character, add a finished example as a second `--ref`. Pass `--label`
for a caption that shows in the gallery.

**Model choice.** Resolution is `--model` > config `model` > built-in default.
`illo.py` takes a full OpenRouter id only — the friendly-name translation is
yours: when the user names a model in plain language, map it to the id and pass
it as `--model`. Don't make the user remember the formal ids.

| When the user says (any of) | Pass to `--model` | Traits |
|---|---|---|
| "Grok Imagine", "Grok image", "xAI image", "Grok", or says nothing | `x-ai/grok-imagine-image-quality` | **default**; bold riso, strong character lock, cheapest, 16:9 |
| "Nano Banana 2", "nano banana", "banana", "nb2" | `google/gemini-3.1-flash-image-preview` | safe catalogued fallback; fast, reliable text; 16:9 |
| "Nano Banana Pro", "banana pro", "nb pro", "the pro one" | `google/gemini-3-pro-image-preview` | richest detail; honors 16:9 |
| "GPT Image 2", "GPT image", "GPT-5.4 Image", "GPT-5.4 Image 2", "OpenAI image" | `openai/gpt-5.4-image-2` | strong instructions; pricey; tends square |
| "Microsoft AI Image", "MAI Image", "Microsoft image", "MAI 2.5" | `microsoft/mai-image-2.5` | clean, lighter grain; honors 16:9 |

Translating:

- An exact OpenRouter id (contains `/`) passes through verbatim.
- Reason over **traits**, not just names: "best quality / richest" → Nano Banana
  Pro; "default / boldest riso" → Grok Imagine; "safe catalogued option / most
  reliable text" → Nano Banana 2.
- If a name is genuinely ambiguous, or names a model not in this table, ask
  rather than guess — and confirm it's an **image-output** model on OpenRouter.
- **Aspect ratio** is only a prompt-text hint, so some models (e.g. GPT) ignore
  it and return square; the others honor 16:9. Crop in post if needed.
- Some models are image-only output — `illo.py` retries with image-only
  modality automatically. A 404 on *modalities* even after that retry means the
  id isn't an image model on OpenRouter (e.g. MiniMax M3) — drop it. Ids drift;
  if one 404s, this table is what to update.
- **Default note:** the default `x-ai/grok-imagine-image-quality` is best+cheapest
  in testing but is **not in OpenRouter's public `/models` list** — it works for
  accounts with access. If a generation 404s "no endpoints found", that account
  can't reach it; fall back to `google/gemini-3.1-flash-image-preview` (catalogued).

**Watermark / attribution (optional, off by default).** The skill ships with
**no** default watermark — the text comes only from the user's `watermark`
config map (read from the config file) or an explicit request, so installers
never inherit someone else's handle. The resolution order, the prompt line to
append, and the two-render caveat are in `references/prompt-recipe.md`.

### 5b. Batches & comparison (only when it helps)

**Default to ONE image.** Fan out only when the user asks for options/comparison
or the piece is important enough to be worth it — and **say the projected cost
first** (each image ≈ 6–25¢ depending on model). Keep N small (2–4). You
orchestrate the
loop; the skill gives you the primitives:

```bash
RUN=$(python3 "$SKILL_DIR/scripts/illo.py" newrun)      # -> /tmp/illo/<runid>
# (a) VARIATIONS — same prompt+model, pick-the-best:
python3 .../illo.py generate --prompt-file p.txt --ref <ref> --count 4 --label "draft→ship" --out "$RUN/v.png"
# (b) MODEL COMPARISON — loop the SAME prompt over models you choose:
for m in x-ai/grok-imagine-image-quality google/gemini-3-pro-image-preview; do
  python3 .../illo.py generate --prompt-file p.txt --ref <ref> --model "$m" --label "$m" --out "$RUN/$(basename $m).png"; done
# (c) CONCEPT VARIATIONS — different prompts (different stagings) for one idea:
python3 .../illo.py generate --prompt-file staging-A.txt --ref <ref> --label "as a funnel" --out "$RUN/a.png"
python3 .../illo.py generate --prompt-file staging-B.txt --ref <ref> --label "as a crossing" --out "$RUN/b.png"

python3 "$SKILL_DIR/scripts/illo.py" gallery "$RUN" --open    # build + open index.html
# add --embed for a single portable file (images inlined)
```

Every `generate` self-records to `$RUN/manifest.jsonl`; `gallery` assembles them
into one page with each image's **label, model, dimensions, cost, and a
collapsible prompt** — the prompt toggle is what makes concept-variation
comparison readable (the prompt is the variable). Always present the gallery
**with a recommendation**, not a raw dump. Multi-model failures are per-image
(an unavailable model errors that one render only); keep the rest.

### 6. QA and iterate

Check every image against `references/quality-bar.md`. Re-roll or edit when the
mascot is decorative or off its locked spec, the body is wrong-value for the
palette, label text sits on a colored fill, the accent has spread past the
character's accent part + 1–2 elements, an unwanted title bar appears, the
composition copies an example, or text is misspelled. Subject scale varies
run-to-run — re-roll if the subject is tiny (check `.width/.height` in the
JSON: a square back when you asked 16:9 → re-roll).

### 7. Deliver

Copy finals next to the user's work when appropriate
(`assets/<slug>-illustrations/01-topic.png`, `02-topic.png`, …); never
overwrite existing assets without being asked. Then report: how many images,
each one's purpose, the palette used, save paths, and which are strongest vs
optional.

## Output discipline

Pre-generation planning is short and concrete. Post-generation, let the images
speak — report what was made and where, not style theory. Keep labels few and
short; the fewer words baked into an image, the more reliably it renders.
