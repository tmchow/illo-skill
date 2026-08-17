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
| **Grok CLI** | — | — | **Unsupported** — engine auto-redirects (see below) |
| **Grok Bot native** | — | — | **Unsupported** — route to a cutout-capable engine backend |
| **OpenRouter** | **`openai/gpt-5.4-image-2`** (engine default when `--cutout` and no `--model`) | Chroma `BACKGROUND:` + `--image-config` | Chroma key via `--cutout` |
| **OpenRouter** (other `--model`) | User override only | Chroma prompt; may fail on JPEG models | Best-effort; read `cutout_alpha` |

Editorial OpenRouter renders keep the global default (`x-ai/grok-imagine-image-quality`).
**Grok cannot make cutouts** — Grok CLI and Grok Bot native return JPEG with no
alpha, and "solid background" renders come back as gradients with the subject
drifting toward the key color, so chroma-keying fails. A `--cutout` render whose
engine backend resolves to `grok` **auto-redirects**: to **Codex** if usable,
else **OpenRouter GPT Image 2** if a key is set; with neither the engine exits
naming both fixes. On Grok Bot native, do not call the native image tool for a
cutout; route to a cutout-capable engine backend or stop for configuration. No
action needed from the caller for the CLI redirect — the note and the manifest
record the backend that ran.
Gemini and other models are unreliable for cutout alpha; prefer **Codex +
chroma** or **OpenRouter GPT Image 2 + chroma**.

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
SKILL_DIR="<path to this skill>";
python3 "$SKILL_DIR/scripts/illo.py" generate --prompt-file /tmp/cutout.txt --ref "$REF" --aspect 1:1 --cutout --image-config '{"aspect_ratio":"1:1"}' --out /tmp/illo-cutout-blot-wave.png
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

## Idle loop / bot avatar

Route animated idle loops and bot-avatar GIFs through this same **cutout**
register: 1:1, `--cutout`, active character sheet as `--ref`. Do not route to
editorial.

Generate **one** on-model cutout and animate that PNG. Do **not** generate 3-4
poses and morph them — separate renders drift and the loop flickers. Keep the
pack constraints programmatic: no mouth/brows means do not draw them; blink by
squashing the locked eye dots; no fingers means no grasping wave; a deadpan face
stays deadpan.

Pick the move from the figure. Read the pack's locked design, accent carrier,
and limbs; choose one or more motions that figure can do without breaking locks.
Head bob is optional: allowed when the silhouette has a distinct head that can
nod **down into the body** without tearing. Use about 8-12 px on a 512 canvas,
down-only, with a feathered join and the body planted. It can stack with another
move (blink, antenna sway, flame flicker) or be the only move. It is not
required.

Other pack-legal examples (illustrative, not exhaustive):

- Soft blob / droplet (Blot) — jelly squash of the body; tip rides the squash;
  feet planted.
- Rigid cube + antenna (Blip) — antenna sway; cube planted.
- Accent flame / lantern (Wick) — flame flicker only; iron planted.
- Accordion / spring limbs (Coil) — limb compress-and-rebound; head/torso/feet
  planted.
- Blink — squash locked eye dots only, on any pack that has them. Combine freely.

Trust `cutout_alpha` after the engine runs. If a keyed PNG is discarded even
though the corners are transparent and the background is gone, that is an engine
bug — do not "fix" it by switching to Grok Bot native, which has no alpha.

Encode transparent GIFs with ffmpeg palette preservation:

```bash
ffmpeg -i frames/%03d.png -vf "palettegen=reserve_transparent=1" palette.png
ffmpeg -i frames/%03d.png -i palette.png -lavfi "paletteuse=dither=none" -loop 0 avatar.gif
```

Do **not** use Pillow `save(..., optimize=True, disposal=2)` for this path; it
can drop alpha on blink frames and flash a black background. Deliver 1:1, loop
forever, keep the character about 60-80% of the frame, and stay under 5 MB for
Grok Bot avatars.

Before delivery, inspect the source cutout, at least three exported frames
(rest, peak motion, blink if present; otherwise another changed frame), and the
final GIF. Do not ship from the script succeeding.

### Must pass

- **Look at the pixels** — open the cutout and GIF; tight-crop thin parts
  (antenna, stems, outlines) instead of trusting generate JSON or ffmpeg exit
  status.
- **Transparency on every frame** — corners stay transparent; no frame has
  nearly zero transparent pixels.
- **Thin-part geometry** — antenna / accent stem stays straight and centered on
  its ball or tip.
- **Blink stays on-model** — the pack face lock still holds; blink by squashing
  the locked eye dots only, with no invented mouth/brows.
- **Motion is pack-legal, visible, and planted** — the chosen move comes from
  the silhouette, accent carrier, or locked limbs. If using a head bob on a 512
  canvas, rest vs peak head-top Y moves about 8-12 px (~1.5-2.5% of the canvas),
  down-only. Body/feet/contact stay planted.
- **One cutout** — every frame comes from the same still PNG, not morphed
  separately generated poses.
- **Watch the loop once** — if the personality is not noticeable, or a tear is
  noticeable, it is not ready.

### Fail signals → fix

- A frame has nearly zero transparent pixels, or the GIF flashes black →
  re-encode with the ffmpeg palettegen path above; never use Pillow
  `optimize=True` for this path.
- Antenna / accent stem drifts 1-2 px down the shaft, bends, or misses the
  ball/tip center → straighten in post or re-roll the still.
- Whole sticker rotates, hops, or bounces → keep contact planted; animate only
  pack-legal silhouette parts.
- Head bob under ~4 px on a 512 canvas → increase it or choose a better
  pack-legal move; the motion will disappear at delivery size.
- Head lifts off the torso, leaves a gap, sliced chin, double contour, or
  leftover chin slab → if using a bob, move **down into the body only**, feather
  the join, and keep enough overlap.
- Blink frame invents facial features or changes expression → rebuild it as
  locked eye-dot squash only.
- Every avatar in a multi-bot set uses the same generic head bob when a
  pack-legal alternative exists → choose distinct moves from each figure.
