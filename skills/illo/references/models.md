# Models — friendly names, ids, traits

**This table is the OpenRouter backend only.** `--model` (and config `model:`)
is an **OpenRouter-only axis** — it is orthogonal to `--backend`, and the
**Codex backend ignores it entirely**: there the model is automatic
(gpt-image-2) with no selector (`references/backends.md`). So only translate
model names / honor `--model` when the OpenRouter backend is in play.

`illo.py` takes a full OpenRouter id only — do the friendly-name translation:
when the user names a model in plain language, map it to the id and pass it
as `--model`. Don't make the user remember the formal ids. Resolution is
`--model` > config `model` > built-in default.

| When the user says (any of) | Pass to `--model` | Traits |
|---|---|---|
| "Grok Imagine", "Grok image", "xAI image", "Grok", or says nothing | `x-ai/grok-imagine-image-quality` | **default**; bold riso, strong character lock, cheapest, 16:9 |
| "Nano Banana 2", "nano banana", "banana", "nb2" | `google/gemini-3.1-flash-image-preview` | safe catalogued fallback; fast, reliable text; 16:9 |
| "Nano Banana Pro", "banana pro", "nb pro", "the pro one" | `google/gemini-3-pro-image-preview` | richest detail; honors 16:9 |
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
- **Aspect ratio** is only a prompt-text hint, so some models (e.g. GPT) ignore
  it and return square; the others honor 16:9. Crop in post if needed.
- Some models are image-only output — `illo.py` retries with image-only
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
