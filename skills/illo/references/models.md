# Models — friendly names, ids, traits

**This table is the OpenRouter backend only.** `--model` (and config `model:`)
is an **OpenRouter-only axis** — it is orthogonal to `--backend`, and **Codex,
Grok CLI, Grok Bot native, and Muse native ignore it entirely**: there the image model is
automatic (Codex → gpt-image-2; Grok → its built-in image tool; Muse → its native
image tool) with no selector
(`references/backends.md`). So only translate model names / honor `--model` when
the OpenRouter backend is in play.

`illo.py` takes a full OpenRouter id only — do the friendly-name translation:
when the user names a model in plain language, map it to the id and pass it
as `--model`. Don't make the user remember the formal ids. Resolution is
`--model` > config `model` > built-in default.

| When the user says (any of) | Pass to `--model` | Traits |
|---|---|---|
| "Grok Imagine", "Grok image", "xAI image", "Grok", or says nothing | `x-ai/grok-imagine-image-quality` | **default**; bold riso, strong character lock, cheapest, 16:9 |
| "Nano Banana 2", "nano banana", "banana", "nb2" | `google/gemini-3.1-flash-image-preview` | safe catalogued fallback; fast, reliable text; 16:9 |
| "Nano Banana Pro", "banana pro", "nb pro", "the pro one" | `google/gemini-3-pro-image-preview` | richest detail; honors 16:9 |
| "Flare", "GPT Image 2.5", "GPT Image 2.5 Flare" | `openai/gpt-image-2.5-flare` | Images API; speed-oriented generation and reference edits; see Flare below |
| "GPT Image 2", "GPT image", "GPT-5.4 Image", "GPT-5.4 Image 2", "OpenAI image" | `openai/gpt-5.4-image-2` | strong instructions; pricey; tends square |

> **Don't confuse the OpenRouter "OpenAI image" model with the Codex
> backend.** The row above is the *billed* `openai/gpt-5.4-image-2` model on
> **OpenRouter**, selected with `--model`. The **Codex backend** renders with
> **gpt-image-2 on the user's Codex subscription** (free, automatic, no
> `--model`) — a different thing reached by `--backend codex`, not by a model
> id. If the user wants free OpenAI-family generation, that's the Codex
> backend (`references/backends.md`), not this row.

Translating:

- An exact OpenRouter id (contains `/`) passes through verbatim.
- Reason over **traits**, not just names: "best quality / richest" → Nano Banana
  Pro; "default / boldest riso" → Grok Imagine; "safe catalogued option / most
  reliable text" → Nano Banana 2.
- If a name is genuinely ambiguous, or names a model not in this table, ask
  rather than guess — and confirm it's an **image-output** model on OpenRouter.
- **Aspect ratio:** the engine sends recognized `--aspect` ratios as image
  options as well as prompt text. Verify actual output dimensions.
- Some chat-completions models are image-only output — `illo.py` retries with image-only
  modality automatically. A 404 on *modalities* even after that retry means the
  id isn't an image model on OpenRouter (e.g. MiniMax M3) — drop it. Ids drift;
  if one 404s, this table is what to update.
- **Reference-image format:** the bundled model sheet is **WebP**, accepted by
  every model in the table. Some providers take only JPEG/PNG references —
  Azure's image API (e.g. Microsoft MAI) rejects WebP, which is why MAI is not
  in the lineup. If an off-table model errors with "Unsupported image file
  type", that provider can't take the bundled sheet; tell the user rather
  than converting the reference.
- **Default note:** the default `x-ai/grok-imagine-image-quality` is best+cheapest
  in testing but is **not in OpenRouter's public `/models` list** — it works for
  accounts with access. If a generation 404s "no endpoints found", that account
  can't reach it; fall back to `google/gemini-3.1-flash-image-preview` (catalogued).

Cost (OpenRouter backend): generation bills the user's OpenRouter account per
image — typically under ten cents on the default model, varying by model;
prices are OpenRouter's and drift. The Codex backend has no per-image charge
(it draws on the Codex quota) — see `references/backends.md`.

**Cutouts:** `--cutout` without `--model` on OpenRouter selects
`openai/gpt-5.4-image-2` (Grok/JPEG cannot produce compositing-ready cutouts).
**Codex cutouts** request native PNG alpha by default. The engine keeps chroma
keying as an explicit Codex compatibility path (`--chroma`) and as the default
OpenRouter path. Chroma reliability is not universal across all characters or
models; a pack's optional **`Cutout chroma:`** line sets its fallback screen
color (default magenta; green for forged-metal characters like Wick). Re-roll
on screen bleed, accent halos, noisy backgrounds, or malformed native alpha.
See `references/cutout.md`.

## Flare through OpenRouter

Select `--backend openrouter --model openai/gpt-image-2.5-flare`. Keep the
existing editorial and cutout defaults unless the user selects Flare.
The engine routes this model through OpenRouter's dedicated `/api/v1/images`
endpoint; other models keep their existing chat-completions transport.
Every reference is sent through `input_references`, including the character
sheet and any style anchor. No new credential setup is needed.

Pass image options with `--image-config`, for example
`'{"quality":"low"}'` for a draft or `'{"quality":"high"}'` for comparison.
For Flare these become top-level Images API fields. PNG is the default;
JPEG is also supported. Use `--count` for batches; do not put `n`, `stream`,
`model`, `prompt`, or `input_references` in the image options. With `--cost`,
the engine records the response's inline usage cost; unavailable cost or
generation ID remains null.

Verify dimensions before delivery: a reference-guided 16:9 request in the
2026-09-09 probe returned 1536×1024 (3:2). Do not promise an exact aspect ratio.

**Transparent cutouts remain chroma-based on this route.** On 2026-09-09,
OpenRouter rejected Flare's `background: "transparent"` before generation;
`background: "auto"` with an explicit native-alpha prompt returned an opaque
PNG. Use `--cutout` to request a chroma screen and inspect `cutout_alpha` and
`cutout_method`. Do not pass `background: "transparent"` expecting native
alpha through OpenRouter yet. The engine preserves clean native alpha if
the provider returns it.

OpenAI documents native transparency for Flare, but the OpenRouter route must
support it too. Before enabling native-alpha prompting, re-check the
[Flare endpoint capabilities](https://openrouter.ai/api/v1/images/models/openai/gpt-image-2.5-flare/endpoints)
and verify a real render. Request and response details are in the
[OpenRouter Images API guide](https://openrouter.ai/docs/guides/overview/multimodal/image-generation).
