# Character cutout register

A **cutout** is a reference-locked, transparent PNG of the mascot alone —
one compositing unit for downstream overlay (slides, docs, another agent,
a human editor). It is **not** an editorial illustration and **not** a model
sheet.

Read this file in full before generating any cutout.

## When to route here

Route to cutout when the user asks for things like:

- "character cutout", "transparent PNG", "just the mascot", "sticker",
  "overlay asset", "no background", "PNG I can paste on something else"

**Do not** route here when the ask needs to **explain an idea** — a thesis,
labels, a contraption-as-metaphor, a traceable structure, or a mini-comic.
Those stay editorial or explainer (`references/composition.md`).

Cutout wins when the deliverable is **who + how they're posed**, not **what
idea the picture lands**.

## What a cutout is

| Dimension | Editorial / explainer | Cutout |
|---|---|---|
| Purpose | Explain one idea | Supply a reusable character instance |
| Background | Paper / style ground | **Transparent** (chroma key on Codex and most OpenRouter; native alpha only on backends that expose it; else honest opaque fallback) |
| Text | Labels / callouts allowed | **None** — no labels, captions, watermarks |
| Environment | Scene, machines, diagrams | **No environment** — see contact continuity |
| Expressiveness | Move + metaphor + staging | **Pose + orientation + body language** |
| Aspect | 16:9, 1:1 social, etc. | **1:1** square, character large (~60–80% of frame) |
| QA | Thesis + load-bearing test | On-model + contact continuity + clean alpha |

The user may prompt casually ("cutout of Blot waving", "yoke sitting on a
sofa holding a wrench"). The agent interprets pose and contact objects; the
register restricts **what kind of pixels** may appear.

## Contact continuity (the prop rule)

Every opaque pixel must belong to **one sticker cluster** — the character plus
whatever is in **direct contact** with them. Transparency means everything in
the alpha travels together when pasted elsewhere.

**Allowed** — contact, not proximity:

- **Held** — wrench, mug, flag (grip = contact).
- **Sat on** — sofa seat, stool, boulder (support = contact).
- **Stood on** — foot patch, top of stool (minimal surface under feet only).
- **Leaned on / touched** — table edge, wall fragment (**show only the
  contacted fragment**, not a whole room).
- **Agent-inferred** — when the verb implies contact ("sitting", "leaning",
  "at the desk", "fixing something" → wrench in hand), add the **minimal**
  contact object or surface that makes the pose legible.

**Forbidden** — spatial staging, not pose anchors:

- Objects **nearby but not touching** (character here, rock over there).
- **Scene furniture** — wide floor, horizon, full table with legs extending
  into empty space, living-room sets, machines as separate actors.
- **Diagram machinery** — arrows, stations, callouts, multi-object metaphors.
- **Text anywhere** — labels, captions, signatures, numbers.
- **Second characters.**

When ambiguous, prefer **pose-only** (no extra pixels) over inventing contact
objects. When the verb implies contact, the contact surface is fair game even
if unnamed.

### QA tests

1. **Contact trace** — from every non-body blob, can you draw touch/support/grip
   back to the body?
2. **Orphan test** — cover the character; do leftover opaque pixels read as a
   separate scene object rather than a contacted fragment?
3. **Sticker test** — one peel-and-stick unit, not a cropped illustration corner.
4. **Alpha test** — no magenta/green screen bleed at the silhouette edge; engine
   `--cutout` despills screen-color halos (re-roll if a bright green/magenta
   outline remains).

## Pose vocabulary

Cutouts express **pose**, not **idea**. Reach for:

- **Neutral** — standing, limbs relaxed, front or slight 3/4.
- **Gesture** — wave, point, shrug, hands on hips.
- **Direction** — facing left / right / toward camera (say so in the POSE line).
- **Attitude** — slump, lean, bounce — via body tilt; the locked face carries
  little expression unless the pack spec names a mouth/brows.

No mini-comics, no multi-panel, no "performing the move on a built metaphor"
in illo's editorial sense — if that is what the ask needs, reroute to editorial.

## Relationship to the model sheet

| | Model sheet | Cutout |
|---|---|---|
| Role | Identity lock for all future renders | One compositing asset |
| Pose | Fixed neutral front-facing | User- or agent-chosen within vocabulary |
| Background | Plain paper (intentional) | Transparent |
| Text | None | None |

Do **not** replace a pack's `reference.png` with a cutout. Cutouts are
ephemeral outputs, not catalog artifacts.

## Generate

Build the prompt from `references/prompt-recipe.md`, "Cutout variant". Default
aspect **1:1**. Pass the active character's model sheet as `--ref`. Always pass
**`--cutout`** and **`--aspect 1:1`**.

### Backend and model routing

| Backend | Model | Prompt shape | Transparency path |
|---|---|---|---|
| **Codex** | gpt-image-2 (automatic) | Chroma `BACKGROUND:` in prompt (engine auto-appends if omitted) | Chroma key via `--cutout` — **no native alpha** from `codex exec` |
| **OpenRouter** | **`openai/gpt-5.4-image-2`** (engine default when `--cutout` and no `--model`) | Chroma `BACKGROUND:` + `--image-config` | Chroma key via `--cutout` |
| **OpenRouter** (other `--model`) | User override only | Chroma prompt; may fail on JPEG models | Best-effort; read `cutout_alpha` |

Editorial OpenRouter renders keep the global default (`x-ai/grok-imagine-image-quality`).
**Do not use Grok for cutouts** — it returns JPEG with no chroma path. Gemini and
other models are unreliable for cutout alpha; prefer **Codex + chroma** or
**OpenRouter GPT Image 2 + chroma**.

**Codex backend** — always use a flat chroma `BACKGROUND:` line (included in
the Cutout template). gpt-image-2 via `codex exec` returns **opaque PNG only**;
transparency comes from illo's chroma post-process, not from the model. Do **not**
rely on prompt-native "real alpha channel" requests on Codex.

**OpenRouter backend** — keep the chroma `BACKGROUND:` line in the prompt.
Unless the user names another model with `--model`, the engine selects
**`openai/gpt-5.4-image-2`**. Pass model-specific keys through
**`--image-config`** (JSON object merged with `--aspect`), not prompt prose alone —
the engine forwards this to OpenRouter's `image_config`:

```bash
python3 "$SKILL_DIR/scripts/illo.py" generate \
  --prompt-file /tmp/cutout.txt \
  --ref "$REF" \
  --aspect 1:1 \
  --cutout \
  --image-config '{"aspect_ratio":"1:1"}' \
  --out /tmp/illo-cutout-blot-wave.png
```

### Chroma screen color

Each character pack declares **`Cutout chroma: green`** or **`Cutout chroma:
magenta`** in its `character.md` (Blot: magenta in `references/character.md`).
That is the pack author's one-time decision — agents read it when building the
cutout prompt; the engine reads it from the active `--ref` pack (or the
configured default character when `--ref` is omitted). **`--chroma`** on
`generate` overrides for re-rolls; omit it for normal cutouts.

Pick a screen color **absent from the character palette**. The engine keys that
color to alpha in post; anti-aliased edges inherit screen tint — wrong color =
visible fringe.

| Use | Screen | When |
|---|---|---|
| **Green** | `#00FF00` | Pack line `Cutout chroma: green` — forged-metal / wrought-iron silhouettes (e.g. **Wick**); re-roll when magenta fringe persists on fine metal edges |
| **Magenta** | `#FF00FF` | Pack line `Cutout chroma: magenta` or omitted (default) — including pink-accent riso characters with a **registration-locked silhouette** |

The Cutout template's `BACKGROUND:` line must match the pack's **`Cutout
chroma:`** value. When the line is absent from an old pack, default **magenta**;
the engine still falls back to forged/wrought-metal heuristics, then magenta.
The manifest records `cutout_chroma`.

### Registration-locked silhouette

Cutouts are compositing assets — editorial **ink-layer offset / misregistration**
reads as a bright accent halo after chroma key and fails QA. Every cutout prompt
must include the **SILHOUETTE** block from `references/prompt-recipe.md`
(registration-locked single-plate contour; riso grain stays **inside** fills).
Do not copy the editorial STYLE line verbatim.

Examples of `--image-config` keys (when the model's docs support them):

- `aspect_ratio` — usually covered by `--aspect 1:1` (also mapped automatically).

After generate, read the JSON line's **`cutout_alpha`**, **`cutout_method`**, and
**`cutout_note`**. When `cutout_alpha` is false, the image is **not** compositing-ready
(JPEG, opaque PNG, weak alpha, or chroma extraction failed) — say so honestly; do not claim
transparency. Re-roll, switch backend/model, or disclose before delivering as a sticker.
Even when `cutout_alpha` is true, `cutout_note` may carry a QA warning — a likely
foot-crop (character touching the bottom frame edge) or residual edge fringe — so read it
and treat those as re-roll signals against `references/quality-bar.md`.

No watermark on cutouts. No style-anchor `--ref` from editorial sets — the
character sheet alone.

Check against the cutout section of `references/quality-bar.md` before
delivering. Re-roll on orphans, scene bleed, green fringing, cropped feet/limbs,
or off-model drift.
