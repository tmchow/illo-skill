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

The skill itself lives in [`skills/illo/`](skills/illo/) — its
[README](skills/illo/README.md) is the full developer reference
(prerequisites, API-key setup, models & cost, everything below in detail).

## Install

**Quick install — any agent.** One command for Claude Code, Cursor, Codex,
Copilot, Gemini CLI, and the ~70 other runtimes the
[skills CLI](https://skills.sh) supports (update later with
`npx skills update`):

```bash
npx skills add tmchow/illo-skill --skill illo
```

**Platform-native installs.** The repo also ships a plugin/extension
manifest for each major runtime, so you can install through your platform's
own package manager and get managed updates:

| Platform | Install | Update |
| --- | --- | --- |
| **Claude Code** | `/plugin marketplace add tmchow/illo-skill` then `/plugin install illo@illo-skill` | `claude plugin update illo`, or enable marketplace auto-update |
| **Codex** | `codex plugin marketplace add tmchow/illo-skill` then `codex plugin add illo@illo-skill` | `codex plugin marketplace upgrade` |
| **Gemini CLI** | `gemini extensions install https://github.com/tmchow/illo-skill` | `gemini extensions update illo` |
| **Copilot / GitHub CLI** | `gh skill install tmchow/illo-skill illo` (cross-agent via `--agent`) | `gh skill update illo` |
| **Cursor** | `npx skills add tmchow/illo-skill --skill illo` (Cursor Marketplace listing pending review) | re-run the installer |
| **Hermes** | `hermes skills install tmchow/illo-skill/illo` | `hermes skills update illo` |
| **OpenClaw** | `openclaw skills install illo` | reinstall with the same command |

Every lane installs the same skill; releases are tagged `v<version>` and
the version in every manifest is kept in lockstep with
`skills/illo/SKILL.md` by CI.

## Repo layout

The skill sits in `skills/illo/`, following the layout of the canonical
skill repos (anthropics/skills, openai/skills): a top-level `skills/`
folder, one directory per skill. It is deliberately not at the repo root —
installers copy the entire skill directory verbatim, so the skill dir holds
only what every install should ship. Docs-only images live in
`_assets/illo/` (linked by raw URL), and repo meta stays at the root —
including the plugin manifests (`.claude-plugin/`, `.codex-plugin/`,
`.cursor-plugin/`, `gemini-extension.json`) that make the repo installable
as a native plugin on each platform.

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
[`skills/illo/NOTICE`](skills/illo/NOTICE) for attribution of the Blot character and
bundled artwork.
