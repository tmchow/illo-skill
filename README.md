# illo

Generate original print-style **editorial illustrations** for articles and
blogs, starring a recurring mascot that performs each idea. Each character
pack carries one of ten bundled looks (riso, blueprint, woodcut, pixel, clay,
manila, chalk, phosphor, enamel, gouache) or a custom style — default
**Blot** (a deadpan ink-drop), or design your own with the built-in character
builder. One-metaphor-per-image scenes with named + custom + derived palettes
and reference-image character consistency. Calls OpenRouter's image API
directly (model-selectable: Grok Imagine, Nano Banana 2/Pro, GPT-5.4
Image 2, …).

> **🌐 [illo-skill.com](https://illo-skill.com)** — live examples, the
> character gallery, and copy-paste installs.

The skill itself lives in [`illo/`](illo/) — its
[README](illo/README.md) is the full developer reference (prerequisites,
API-key setup, models & cost, everything below in detail).

## Install

Any agent ([skills CLI](https://skills.sh) — Claude Code, Cursor, Codex, …):

```bash
npx skills add tmchow/illo-skill --skill illo
```

Hermes:

```bash
hermes skills install tmchow/illo-skill/illo
```

OpenClaw:

```bash
openclaw skills install illo
```

## Repo layout

The skill deliberately sits in the `illo/` subdirectory rather than at the
repo root: installers copy the entire skill directory verbatim, so the skill
dir holds only what every install should ship. Docs-only images live in
`_assets/illo/` (linked by raw URL), and repo meta stays at the root.

## Companion repos

- [tmchow/illo-characters](https://github.com/tmchow/illo-characters) —
  community character packs ("install the blip character").

## Provenance

illo started life inside
[tmchow/agent-skills](https://github.com/tmchow/agent-skills); it moved here
with full git history. The old location keeps a frozen copy so existing
installs don't break, but this repo is the canonical home — new versions
ship only from here.

## License

MIT © Trevin Chow — see [`LICENSE`](LICENSE) and
[`illo/NOTICE`](illo/NOTICE) for attribution of the Blot character and
bundled artwork.
