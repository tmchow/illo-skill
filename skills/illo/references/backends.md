# Backends — the dual image engine

illo renders through one of two backends. Both produce the same kind of
file; they differ only in where the image is made and who is billed.

- **Codex** — drives the user's already-installed, already-logged-in **Codex
  CLI** (`codex exec`) to reach its built-in `image_generation` tool
  (gpt-image-2). Free for Codex subscribers (no per-image charge); it draws
  on the user's Codex usage quota.
- **OpenRouter** — calls OpenRouter's image API directly. Pay-per-image
  through the user's OpenRouter account. The **universal fallback** and the
  only backend a host without Codex can use.

`--backend` (and config `backend:`) selects one explicitly; otherwise the
engine resolves the right one by host capability. Resolution and readiness
are reported by `doctor`.

## Resolution and default (capability-aware)

The backend is resolved per run, never a static flip:

```
--backend  >  config backend:  >  capability-aware default
```

The **capability-aware default** is, in order:

1. a **usable Codex CLI** is present → `codex`;
2. else an **OpenRouter key** is configured → `openrouter`;
3. else neither → onboarding (the engine names both fixes).

This never silently breaks an existing OpenRouter-only install on upgrade: a
host with a key but no Codex CLI still resolves to `openrouter`, so `doctor`
stays exit 0. An explicit `--backend`/`backend:` choice is honored as-is;
readiness is judged separately, so `doctor` can flag a
chosen-but-unusable backend.

## Codex backend

### The Codex-CLI requirement (detection)

Eligibility is a property of the **execution host**, detected — never
assumed. A Claude Code, Cursor, Gemini, Hermes, or OpenClaw run on a
CLI-equipped host all qualify equally; a Codex-harness run on a bare host
does not. The host is "usable Codex" only when **all three** hold:

1. `codex` is on `PATH`;
2. `codex login status` reports logged in;
3. `codex features list` reports the `image_generation` feature available.

Any non-zero exit, timeout, or unparseable output → not usable, and the
engine soft-falls to OpenRouter. Detection runs once per process and reads
**no** credential file and **no** secret-shaped env var. `doctor` reports
the stage that failed (`codex login` needed, feature unavailable, etc.).

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
asks the agent to save the result to the run-dir path. illo handles **no
token**: it runs no OAuth, reads no `~/.codex/auth.json`, hits no endpoint —
the only privileged action is the subprocess call to the user's own CLI
(the one sanctioned exception to the stdlib-over-subprocess rule; see
`AGENTS.md`). The adapter verifies the file landed, otherwise fetches the
freshest image the tool dropped under `$CODEX_HOME/generated_images/`
(`$CODEX_HOME` resolved at run time — relocatable, never hardcoded).

### Windows/WSL is unsupported → OpenRouter

`codex exec` image generation is broken on Windows/WSL (openai/codex#19133).
illo treats that as a backend failure and falls over to OpenRouter when a key
is configured.

### Fallback behavior

When the Codex backend is unavailable or fails for **any** non-fatal reason —
no usable CLI, `codex exec` errored or timed out, unsupported platform, or no
retrievable image — illo:

- falls back to **OpenRouter** when a key is configured (the manifest record
  is tagged `backend: openrouter`); or
- exits with a clear, actionable error naming both fixes (install +
  `codex login`, or run `init` to set an OpenRouter key) when no key is set.

A Codex-served record carries `cost: null` and no model id, and the engine
never queries OpenRouter for its cost.

## OpenRouter backend

The pay-per-image path, billed to the user's OpenRouter account. It is
**model-selectable** (`--model`; see `references/models.md` for the lineup,
the friendly-name → id map, the aspect caveat, and 404/fallback handling) and
is the universal fallback for any host where Codex is unavailable. Its wire
behavior is unchanged from a single-backend install — the dual-backend work
is purely additive.
