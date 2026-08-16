# Backends and transports

illo has **three engine backends** plus one named **agent-side transport**. All
produce the same kind of file; they differ in where the image is made, how the
agent reaches it, and who is billed.

- **Codex** — drives the user's already-installed, already-logged-in **Codex
  CLI** (`codex exec`) to reach its built-in `image_generation` tool
  (gpt-image-2). Free for Codex subscribers (no per-image charge); it draws
  on the user's Codex usage quota.
- **Grok CLI** — drives the user's **Grok (xAI) CLI** (`grok -p`, its headless
  single-turn mode) to reach its built-in `image_gen`/`image_edit` tools. Free
  for Grok subscribers; draws on the user's Grok usage quota. Same env-free,
  token-free subprocess design as Codex. **Cannot produce transparent cutouts**
  (Grok returns JPEG with no alpha) — cutout renders redirect to a
  cutout-capable backend.
- **Grok Bot native** — when the agent is **Grok Bot** (Cursor's Grok Bot /
  the Grok desktop assistant), the agent calls Grok Bot's built-in Grok image
  tool directly with illo's prompt and reference image. This is the same Grok
  image-model class as the CLI backend, but a different harness: no Grok CLI,
  no `--backend grok-bot`, no OpenRouter key. It is not a generic "any host
  image API" escape hatch.
- **OpenRouter** — calls OpenRouter's image API directly. Pay-per-image
  through the user's OpenRouter account. The direct paid backend and the only
  engine backend a host without a subscription CLI can use. A failed CLI render
  reaches it only when `--allow-paid-fallback` is explicitly supplied;
  intentional cutout routing is unchanged.

`--backend` (and config `backend:`) selects only an engine backend; otherwise
the engine resolves the right one by host capability. Resolution and readiness
are reported by `doctor`. Grok Bot native is selected by the agent-side routing
rules in `SKILL.md` before `illo.py generate` is called.

## Engine resolution and default (capability-aware)

The backend is resolved per run, never a static flip:

```
--backend  >  config backend:  >  capability-aware default
```

The **capability-aware default** is, in order:

1. a **usable Codex CLI** is present → `codex`;
2. else a **usable Grok CLI** is present → `grok`;
3. else an **OpenRouter key** is configured → `openrouter`;
4. else none → onboarding (the engine names the fixes).

This never silently breaks an existing OpenRouter-only install on upgrade: a
host with a key but no subscription CLI still resolves to `openrouter`, so
`doctor` stays exit 0. An explicit `--backend`/`backend:` choice is honored
as-is; readiness is judged separately, so `doctor` can flag a
chosen-but-unusable backend.

### The self-identify rule (agent-driven, not engine-driven)

The precedence above reads **host** capability — the engine can't tell which
agent invoked it, so on a host with both Codex and Grok usable it defaults to
Codex. But the **agent** knows which agent it is. So the actionable rule lives
in `SKILL.md`:

- A subscription-CLI agent whose own CLI is usable here adds its own
  `--backend` flag for non-cutout renders (the **Grok CLI agent** →
  `--backend grok`, the **Codex agent** → `--backend codex`). That keeps
  "running in Grok, generate with Grok" true even when Codex is also installed.
- **Grok Bot** does not add a flag. When backend is unset/auto, it does not call
  `illo.py generate` at all; it builds the same illo prompt and calls Grok
  Bot's built-in Grok image tool with the active character sheet as a reference.

Both rules avoid engine runtime sniffing (no process-tree guessing, no reading
a secret-shaped `GROK_AUTH*`/`*_TOKEN` env var — both of which the skill's
scanner-safe posture forbids). A user's explicit config `backend:` still
overrides everything; cutouts ignore Grok paths and redirect off Grok
regardless.

### Migration: existing configs choose once for engine generation

The config carries a `configVersion` stamp (current: `2`, the version that
introduced the backend choice). A config written by an **older install** lacks
it — that user has never been offered a subscription CLI vs OpenRouter, and
silently picking one (flipping them to a CLI, or quietly keeping OpenRouter so
they never learn the CLI backends exist) is the wrong call. So an out-of-date
config is **not auto-resolved**:

- `generate` **hard-stops** with a message to choose a backend (an agent reusing
  an old playbook learns its config is stale rather than rendering on a guess).
- `doctor` reports `backend: NEEDS CHOICE` and exits non-zero.

The choice is surfaced **interactively** (the agent asks Codex vs Grok vs
OpenRouter; see SKILL.md "Config migration") and persisted with
`init --backend <codex|grok|openrouter> --no-key`, which stamps `configVersion`
and keeps any existing key. A brand-new install (no config) is ordinary onboarding,
not a migration — it resolves capability-aware as above. The stamp, not the
`backend` key's absence, is the signal: a current-version user who chose "auto"
also has no `backend` key but is not re-prompted.

## Codex backend

### The Codex-CLI requirement (detection)

Eligibility is a property of the **execution host**, detected — never
assumed. A Claude Code, Cursor, Gemini, Hermes, or OpenClaw run on a
CLI-equipped host all qualify equally; a Codex-harness run on a bare host
does not. The host is "usable Codex" only when **all three** hold:

1. `codex` is on `PATH`;
2. `codex login status` reports logged in;
3. `codex features list` reports the `image_generation` row. Codex 0.144 folded
   generated-image artifact handling into this stable feature, so its presence is
   the whole capability signal. (Codex 0.141 also required an experimental
   `imagegenext` extension to make `codex exec` emit the artifact; that extension
   was removed once the behavior went stable, so illo no longer gates on it.)

Any non-zero detection exit, timeout, or unparseable output means Codex is not
usable. The capability-aware default can then select Grok or direct OpenRouter.
Once Codex is selected for a render, generation fails closed by default;
OpenRouter retry requires `--allow-paid-fallback`. Detection runs once per
process and reads **no** credential file and **no** secret-shaped env var.
`doctor` reports the stage that failed (`codex login` needed, feature
unavailable, etc.).

If the user needs to enable it: install the official Codex CLI and run
`codex login` — that is the entire setup. illo never touches the token.

### gpt-image-2 is automatic — no model selection

The free built-in tool exposes **no model selector**; it renders with
Codex's current default, **gpt-image-2**. So on the Codex backend the
`--model` flag and config `model:` **do not apply** — they are an
OpenRouter-only axis. (Pinning a model would require the *billed*
`image_gen.py --model` CLI, which needs an API key and defeats "free for
subscribers" — out of scope.)

Aspect has no size argument on the free tool either; illo states the aspect
in the prompt text, which gpt-image-2 honors. As always, check
`.width/.height` in the JSON line and re-roll a stray wrong-dimension result.

### Quota, not a per-image charge

"Free" means there is no per-image dollar charge — it **draws on the user's
Codex usage quota**, and image turns consume that allowance faster than text
turns. The questionnaire (run by the user during `init`) states this before
enabling Codex.

### Transport and character lock

illo invokes `codex exec` against the built-in tool, attaching the active
character's reference sheet (`-i <sheet>`) so the mascot stays on-model, and
asks the agent to save the result to the run-dir path. As of Codex CLI 0.144
the stable `image_generation` feature drops the generated artifact under
`$CODEX_HOME/generated_images/<session-id>/<image>.png` on its own — illo
verifies the requested path first and otherwise fetches the freshest valid image
artifact at that fixed depth that postdates the exec. (On Codex 0.141 this
required an extra `--enable imagegenext` flag, since
the stable feature did not emit the artifact reliably; the extension was removed
once the behavior went stable, so illo no longer passes the flag.) Artifact
presence takes precedence over wrapper status: Codex can complete
`image_generation` and persist the PNG, then exit 1 because its final assistant
text is empty. A valid requested or fresh generated artifact is still a Codex
success, including after a timeout; only a run with no valid fresh artifact
fails.

With no `--ref` and no
default character there is nothing to lock to, so illo renders ref-less (a
one-line note marks it) — matching OpenRouter, and exactly what bootstrapping a
brand-new character's first model sheet needs (`references/character-builder.md`
step 4). illo handles **no token**: it runs no OAuth, reads no
`~/.codex/auth.json`, hits no endpoint —
the only privileged action is the subprocess call to the user's own CLI
(the one sanctioned exception to the stdlib-over-subprocess rule — a benign
call to a known CLI, not a credential read). The adapter verifies the file
landed, otherwise fetches the
freshest image the tool dropped under
`$CODEX_HOME/generated_images/<session-id>/`
(`$CODEX_HOME` resolved at run time — relocatable, never hardcoded).

### Windows/WSL is unsupported

`codex exec` image generation is broken on Windows/WSL (openai/codex#19133).
illo treats that as a backend failure. Select OpenRouter directly, or explicitly
permit the paid retry with `--allow-paid-fallback` when a key is configured.

### Fallback behavior

When the Codex backend is unavailable or produces no valid fresh artifact, illo
**fails closed by default**, even when an OpenRouter key is configured. It falls
back to OpenRouter only when the caller explicitly supplies
`--allow-paid-fallback`; that paid record is tagged `backend: openrouter`.
Direct `--backend openrouter` generation is not a fallback and does not need the
flag.

A Codex-served record carries `cost: null` and no model id, and the engine
never queries OpenRouter for its cost.

## Grok Bot native transport

Grok Bot native is an **agent-side transport**, not an engine backend. Use it
only when the agent is **Grok Bot**: Cursor's Grok Bot / the Grok desktop
assistant with a built-in Grok image generation tool. Other agents that happen
to expose some image API must not take this path; they use Codex, Grok CLI, or
OpenRouter through the engine.

### Routing and readiness

Run `doctor` first for the non-transport checks: Python can launch the engine,
the skill path is correct, bundled assets are intact, custom packs are readable,
and palette/config files parse. On Grok Bot native, a `doctor` failure whose
only blocker is "no backend ready", missing OpenRouter key, or
`backend: NEEDS CHOICE` is not a stop and is not a reason to run `init` for an
OpenRouter key. The agent will not call `illo.py generate`.

An explicit user/backend choice still wins. If config or the request says
`backend: openrouter`, `backend: codex`, or `backend: grok`, honor that engine
backend and handle its readiness/failure normally instead of silently switching
to Grok Bot native.

### Tool use and model behavior

Build the prompt exactly as `references/prompt-recipe.md` specifies, including
the active character spec, style file, palette mapping, composition register,
text budget, and QA constraints. Attach the active character's model sheet as a
reference image (`assets/character-reference.webp` for Blot, or the pack's
`reference.png`); for image sets, attach the accepted style anchor as a second
reference on later images. Ask Grok Bot's built-in Grok image tool for the
target aspect ratio and saved output file.

This is the same Grok image-model class as the Grok CLI backend: no model
selector, no OpenRouter billing, and no alpha channel. The returned/saved file
path is the `.path` equivalent for QA and delivery. There is intentionally no
`--backend grok-bot` flag and no manifest record from the engine unless a
separate engine render is run.

### No transparent cutouts

Grok Bot's native image tool returns opaque Grok images, like the Grok CLI path.
Do not use it for transparent cutouts. Route cutouts to a cutout-capable engine
backend (Codex if usable, otherwise OpenRouter GPT Image 2 when configured) or
stop and ask for that backend to be configured.

## Grok CLI backend

The Grok CLI backend is the Codex backend's twin: it drives the user's own Grok
CLI to reach a built-in image tool, handling no token itself.

### Detection

The host is "usable Grok" when **both** hold:

1. `grok` is on `PATH`;
2. a login credential is present — the credential file (`$GROK_HOME/auth.json`,
   `$GROK_HOME` default `~/.grok`) **exists**.

Detection reads the credential file's **existence only, never its contents**
(scanner-clean: no secret read, no secret-shaped env var — `$GROK_HOME` is a
path, not a secret). The image tools' reachability can't be probed without a
billed call, so a logged-out or image-ineligible account fails at generation
time rather than detection. The capability-aware default can choose the next
available backend when Grok CLI is not detectable; once a Grok CLI render
starts, paid OpenRouter retry is opt-in. Detection runs once per process.
`doctor` reports whether the CLI is usable, present-but-logged-out, or absent.
Setup is the entire story: install the Grok CLI and run `grok login`.

### The image tool is automatic — no model selection

`grok -p` fires Grok's built-in `image_gen`/`image_edit` tools; the image model
is not the chat model and exposes no selector, so **`--model` and config
`model:` do not apply on the Grok CLI backend** (an OpenRouter-only axis, exactly
like Codex). Aspect is honored: illo states it in the prompt and Grok's tool
maps it (`1:1`, `16:9`, and non-enum ratios like `3:2` render at the right
dimensions). As always, check `.width/.height` and re-roll a stray result.

### No transparent cutouts (JPEG, no alpha)

The Grok CLI image tool returns **JPEG with no alpha channel**, and its "solid
background" renders come back as gradients with the subject drifting toward the
key color — so chroma-keying fails (opaque corners, heavy fringe). illo does
**not** attempt cutouts on Grok: a `--cutout` render whose backend resolves to
`grok` **redirects** to a cutout-capable backend — Codex if usable, else
OpenRouter GPT Image 2 if a key is set — and prints a note; with neither it
exits naming both fixes. This pre-render capability redirect is intentional and
does not require `--allow-paid-fallback`. The manifest records the backend that
actually ran.

### Quota, transport, and character lock

"Free" means no per-image dollar charge — it **draws on the user's Grok usage
quota**, faster for image turns than text. The `init` questionnaire states this
before enabling Grok. illo invokes `grok -p` with `--always-approve --cwd
<run-dir>`, instructing the agent to fire the image tool (not construct the
image in code) and save to the run-dir path; with a reference sheet it steers
`image_edit` (reference read by filesystem path — Grok has no `-i` flag) for
character lock, else `image_gen` for a ref-less bootstrap render. It handles
**no token**: no OAuth, no read of `~/.grok/auth.json`, no endpoint — the only
privileged action is the subprocess to the user's own CLI (the same sanctioned
exception to the stdlib-over-subprocess rule as Codex). The adapter verifies the
file landed, else fetches the freshest image the tool dropped under
`$GROK_HOME/sessions/**/images/`.

### Fallback behavior

When the Grok CLI backend is unavailable or produces no retrievable image, illo
**fails closed by default**, even with a configured OpenRouter key. It retries
through OpenRouter only when `--allow-paid-fallback` is explicitly supplied
(record tagged `backend: openrouter`). A Grok-served record carries `cost: null`
and no model id.

## OpenRouter backend

The pay-per-image path, billed to the user's OpenRouter account. It is
**model-selectable** (`--model`; see `references/models.md` for the lineup,
the friendly-name → id map, the aspect caveat, and 404/fallback handling).
Use it directly with `--backend openrouter` without any fallback flag. It is also
the capability-aware default on a host with a configured key and no usable
subscription CLI, the explicit paid retry target after a failed CLI render, and
the intentional redirect target for Grok cutouts. Its wire behavior is unchanged
from a single-backend install.
