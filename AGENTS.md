# illo-skill

The canonical home of **illo**, a cross-platform AI agent skill (`SKILL.md`
format) installable through runtime-specific lanes: the generic skills CLI
(`npx skills add tmchow/illo-skill --skill illo`, works across Claude
Code/Cursor/Codex and other Agent-Skills runtimes), Hermes (GitHub directory
identifier: `hermes skills install tmchow/illo-skill/illo` or
`/skills install tmchow/illo-skill/illo`; raw `SKILL.md` URLs are valid only
for single-file fallback installs — never for illo, which is multi-file), and
OpenClaw (ClawHub via `openclaw skills install illo`). Document lanes side by
side; never present one as the only path.

This guide is for anyone (human or agent) editing the repo. Keep it accurate
when conventions change.

illo was extracted from [tmchow/agent-skills](https://github.com/tmchow/agent-skills)
(June 2026, full history preserved). That repo keeps a frozen copy and must
keep serving its `_assets/illo/` raw URLs — they are baked into
already-installed copies — but all development and publishing happen here.

## Repo layout

**The skill lives in `skills/illo/`, deliberately not at the repo root.**
The top-level `skills/` folder matches the layout convention of the
canonical skill repos (anthropics/skills, openai/skills,
vercel-labs/agent-skills) and keeps a future Claude Code plugin lane
possible (`.claude-plugin/` + `skills/`). Installers copy the entire skill
directory verbatim, so the skill dir must contain only what every install
should ship; promoting `SKILL.md` to the root would make `_assets/` and
repo meta ship with every install and blow the size budget. Note the
install identifiers do **not** carry the `skills/` segment — skills.sh
indexes by skill name (`tmchow/illo-skill/illo`), the same way
`openai/skills/skill-creator` hides its `skills/` folder.

- `skills/illo/SKILL.md` — required. The agent-facing instructions.
- `skills/illo/README.md` — required. The human-facing landing page
  (below).
- `skills/illo/references/` — deep material loaded on demand, including
  the ten look definitions in `references/styles/`.
- `skills/illo/scripts/` — the engine (`illo.py`) and the Hermes
  asset-repair preflight.
- `skills/illo/assets/` — bundled binary assets plus `checksums.txt`, a
  generated manifest (never edit by hand; see Binary assets below).
- `_assets/illo/` — docs-only images linked by raw URL (calibration
  examples, README embeds). They live outside the skill directory so they
  never ship with installs.
- `.github/` — the ClawHub publish and asset-checksum workflows and their
  scripts.
- Root `README.md` — the repo landing page; root `LICENSE` — MIT.

## SKILL.md frontmatter

Required: `name`, `description`, `version`.

- `name` — `illo`, matching the directory.
- `description` — third person, ≤1024 characters, with **specific** trigger
  phrases and an explicit do-not-trigger clause (illo must not hijack
  generic illustrate/draw requests). It states only the look *count* ("ten
  bundled print looks") — bump the number when adding a look, never
  enumerate names there.
- `version` — semver; **Release Please owns this in normal development**.
  Do not bump it in ordinary feature/fix PRs unless the user explicitly asks
  for a release PR or emergency publish. Meaningful shipped-content changes
  are discovered from Conventional Commits and batched into the Release Please
  PR. "Meaningful shipped content" includes **any edit to installed skill
  content** — `SKILL.md`, `references/**`, `scripts/**`, `assets/**` —
  because those install onto the user's machine and change how the skill
  behaves. Editing a reference doc is *not* a docs-only change: only repo-meta
  files (`README.md`, `AGENTS.md`, `CONTRIBUTING`, `.github/**`) are docs-only.
  Use Conventional Commit titles/messages so Release Please can choose the
  right bump: `fix:` for corrected behavior/docs that should ship, `feat:` for
  new user-visible capability, `chore:`/`docs:` for repo-only changes that do
  not need a skill release.

Per-runtime metadata (`metadata.hermes`, `metadata.openclaw`) is optional
and additive — unknown fields are ignored by other runtimes. **Verify every
runtime-specific field against that runtime's own docs before adding it; do
not fabricate frontmatter schemas.** The same goes for any CLI/command
syntax quoted in the skill: confirm against the tool's `--help`, don't
guess.

## SKILL.md body

- Imperative/infinitive voice ("Run X", "Confirm Y"), not second person.
- Progressive disclosure: keep the body focused; move long schemas, advanced
  patterns, and edge cases to `references/`.
- **No duplication across files.** A fact lives in `SKILL.md` *or* a
  reference, never both — duplicated content drifts.
- When a reference is mandatory before acting, gate it explicitly in the
  body (a capsule summary + a "read `references/X.md` in full before …"
  stop).

## Per-skill README.md

`skills/illo/README.md` is the human-facing landing page — what a person reads to
decide whether to install. It is **not** the agent instructions. It covers
purpose, prerequisites (the OpenRouter key setup), install commands for all
three lanes, capability bullets, and the explicit "SKILL.md is the
agent-facing instructions" line. **Do not** restate workflow, schema, or
step-by-step procedure from `SKILL.md` — that duplicates the agent doc and
drifts. Keep the README to slow-changing metadata.

## Scanner-safe rules (security and size budgets)

The skill installs from a community source, so security scanners judge it at
its most hostile reading — Hermes's `skills_guard` hard-blocks an install
(no `--force` override) on patterns that merely *look* like exfiltration.
These rules come from getting illo from a DANGEROUS verdict to SAFE; keep to
them:

- **Never read secrets from the environment.** A community skill that reads
  a secret-shaped env var (`*_API_KEY`, `*_TOKEN`, …) scans as a critical
  exfiltration primitive regardless of what the code does with the value —
  Hermes flags the read even when the variable is declared in frontmatter.
  When a scanner flags a pattern, fix it by **removal, not renaming** —
  dodging the regex is scanner evasion, and scanners say so.
- **Don't take secrets as CLI flags either.** Command-line arguments leak
  into process listings, shell history, and agent transcripts. The one
  scan-clean credential channel is the config file written by the
  **user-run** `init` (hidden `getpass` prompt, file mode 600).
- **Ephemeral cloud workspaces bridge via the platform's secrets, in the
  setup hook** (Codex setup script, devcontainer `postCreateCommand`, a CI
  step) — a one-liner materializing the config file from the workspace
  secret, documented in prose in the README ("Cloud & CI"). The skill's
  *code* stays env-free. A platform-provisioned workspace secret is
  deliberate consent; an ambient env var on a personal machine is not —
  never copy it.
- **Keep credentials out of frontmatter.** Credential setup belongs in body
  text as something the user runs themselves. Agents must not enter, paste,
  print, or store a user's key.
- **Budget the installed bundle: ≤ 1 MB total, no file over 256 KB.**
  Docs-only assets stay in `_assets/illo/`, outside the skill directory.
- **Re-verify any compressed asset that is a functional input — by running
  it, on every backend.** Format support differs per provider (Azure
  rejects WebP reference images; Google and xAI accept them). Prefer
  JPEG/PNG for images sent to third-party APIs, and after recompressing,
  make the real call against each supported provider and inspect the
  output.
- **Prefer stdlib over subprocess** (`webbrowser.open`, not shelling out to
  `open`/`xdg-open`). **One sanctioned exception: the Codex image backend
  shells out to the user's own `codex` CLI** — `codex login status` /
  `codex features list` for detection and `codex exec` for generation. This is
  a benign call to a known CLI, not a credential read: illo never sees the
  token the CLI holds, reads no `~/.codex/auth.json`, runs no OAuth, and hits
  no endpoint. Do **not** "fix" these subprocess calls back to env-free purity
  or replace them with a credential/network path — the subprocess *is* the
  scanner-clean design. (Detection still reads no secret-shaped env var;
  `$CODEX_HOME` is a path, not a secret, so resolving it is allowed.)
- **Pin every install command** quoted in docs or code
  (`pip install 'PyYAML==6.0.2'`, `npx -y tool@1.2.3`).

## Binary assets (Hermes repair preflight)

Some Hermes versions corrupt binary files when installing multi-file skills
from GitHub (binaries decoded as text). The defense, all in this repo:

- `skills/illo/assets/checksums.txt` — generated manifest
  (`<sha256>  <pin-commit>  <relpath>`), written by
  `.github/scripts/regen_asset_checksums.py` and kept current by the
  `asset-checksums` workflow (PRs touching assets get the regenerated
  manifest committed back to their branch; pushes to main verify).
- `skills/illo/scripts/repair-hermes-assets.sh` — generic, never edited per-asset:
  verifies each asset and re-downloads mismatches from the immutable
  `raw.githubusercontent.com/tmchow/illo-skill/<pin-commit>/…` URL.
  Checksum-gated, so it's harmless on faithful runtimes.
- A magic-byte check in the engine's `doctor` preflight so every runtime
  detects corruption.

**Remove the repair preflight once Hermes ships its installer fix** — the
detection in `doctor` can stay.

## Character packs

The companion content repo is
[tmchow/illo-characters](https://github.com/tmchow/illo-characters). When
creating or editing character packs anywhere (that repo, a user's local
`~/.config/illo/characters/`, or skill docs/examples): **every character
pack name is globally unique** — names are the selection keys agents use
("use anvil"), and illo-characters' `index.json` is the ecosystem registry.
Check it before naming a character. Reserved names: `blot` (ships with the
skill), `illo`, and the look names (`riso`, `blueprint`, `woodcut`, `pixel`,
`clay`, `manila`, `chalk`, `phosphor`, `enamel`, `gouache`, `felt`, `diorama`,
`sketchbook`, `bricks`, `fizz`, `bloom`, `snes`).

## Looks (style definitions)

Styles split deliberately across the two repos: a character pack carries
only a style **name** (its `Style:` line); the style **definition** — the
~3 KB prompt-block file in `skills/illo/references/styles/<name>.md` — lives here,
because style files are engine interface (their sections slot into
`references/prompt-recipe.md` and must evolve with it) and shared
infrastructure (one fix improves every pack that references the look). The
consequences:

- **Adding a character** never touches this repo — packs reference looks by
  name and ship entirely through illo-characters.
- **Adding a look** is a PR here: a new `references/styles/<name>.md` in the
  established format (prompt blocks, palette mapping, character treatment,
  labels, QA deltas), plus updating every enumeration of the look library
  (SKILL.md body + references list, `character-builder.md` interview +
  reserved names, the illo README "Looks" table, and the reserved names
  above). Bump the count in the SKILL.md description. New look names must
  not collide with any character pack name in illo-characters'
  `index.json` — they become reserved both ways.
- **No PR needed to experiment**: a custom style file at
  `~/.config/illo/styles/<name>.md` works immediately for that user;
  promote it here once it proves out.

## Plugin manifests and version lockstep

The repo doubles as a native plugin/extension for the major runtimes. One
skill, six manifests, one version:

- `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` — Claude
  Code. The repo is its own single-plugin marketplace (`illo@illo-skill`);
  skills are auto-discovered from `skills/`.
- `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json` — Codex.
  Codex prefers `.agents/plugins/marketplace.json` (it can also read the
  Claude marketplace for compat, but a Claude-style `"source": "./"` entry
  is invalid there — Codex local sources must be `./<subdir>`, so a
  repo-root plugin is only expressible as a git `"source": "url"` entry
  with no `path`, which is exactly what the native file uses).
- `.cursor-plugin/plugin.json` — Cursor. Native managed installs come only
  through the review-gated Cursor Marketplace
  (cursor.com/marketplace/publish); until the listing is approved, Cursor
  users install via the generic skills CLI.
- `.grok-plugin/plugin.json` + `.grok-plugin/marketplace.json` — Grok (xAI).
  Grok reads the `.claude-plugin/*` manifests for compat, so illo installs
  today without these; the native pair makes it a first-class Grok plugin —
  same rationale as the Codex native file. The marketplace catalog uses a
  local source (`{"type": "local", "path": "."}`), and its brand-scoped
  `keywords`/`domains` feed Grok's plugin CTA (kept tight so illo does not
  mis-fire on generic illustrate requests). This same pair is what the
  xAI-official-marketplace submission points at (see below).
- `gemini-extension.json` — Gemini CLI extension; skills auto-discovered
  from `skills/`. (Google is migrating free-tier Gemini CLI users to
  Antigravity CLI, which imports extensions as plugins — the manifest
  remains the right artifact.)
- Copilot needs **no manifest**: `gh skill` discovers `skills/*/SKILL.md`
  directly, and the repo carries the `agent-skills` topic so
  `gh skill search` finds it.

**Every PR title must use Conventional Commit format** because squash merges
make the PR title the commit that Release Please reads. The
`.github/workflows/pr-title.yml` check enforces this for all PRs, including
forks. Allowed types are `feat`, `fix`, `perf`, `revert`, `docs`, `style`,
`refactor`, `test`, `build`, `ci`, and `chore`. Use
`feat: add a new print look` or `fix: correct rendering guidance` for
installed skill changes; use `docs:`, `chore:`, or `ci:` as appropriate for
repo-only changes that should not trigger a skill release.

**Release Please is the release authority.** Ordinary feature/fix PRs should
not edit version fields. On pushes to `main`,
`.github/workflows/release-please.yml` maintains a release PR that bumps
`version.txt`, `skills/illo/SKILL.md`, every plugin manifest, and
`CHANGELOG.md` together. `skills/illo/SKILL.md` remains the runtime-facing
version source for publish/install tools, and `.github/scripts/sync_plugin_versions.py`
still verifies manifest lockstep on `main`. When the Release Please PR is
merged, Release Please creates the `v<version>` git tag and GitHub release:
that tag is what Copilot's `gh skill` resolves versions against and what
Gemini CLI's release-based update detection watches. Never hand-create version
tags. The workflow uses `secrets.RELEASE_PLEASE_TOKEN` when present and falls
back to `github.token`; add a PAT secret only if branch protection requires CI
to run on Release Please-created PRs.

**One-time repo setup for the release PR.** Release Please opens its release
PR, so with the `github.token` fallback the repo must allow Actions to do that:
Settings → Actions → General → "Allow GitHub Actions to create and approve pull
requests" must be **on** (API: `can_approve_pull_request_reviews: true`).
Without it the release job fails at PR creation with "GitHub Actions is not
permitted to create or approve pull requests" — the workflow itself is fine.
The scoped alternative, which keeps that toggle off, is to set the
`RELEASE_PLEASE_TOKEN` PAT secret (contents + pull-requests write); the workflow
prefers it automatically.

Before merging layout or manifest changes, validate with the real tools:
`claude plugin validate .`, `gemini extensions validate .`,
`grok plugin validate .`, and `gh skill publish --dry-run`.

## Submitting to the xAI plugin marketplace

Getting illo into xAI's official catalog (`xai-org/plugin-marketplace`) is an
outbound PR to *their* repo — an index that only points at our source, so
nothing of illo is vendored there. Do this **after** the change you want to
ship has merged to `main`: the entry pins a commit that must already exist.

1. Fork `xai-org/plugin-marketplace` and branch from `main`.
2. Get the commit to pin — a full 40-char lowercase SHA; a branch, tag, or
   short SHA is rejected by their validator:
   ```bash
   git ls-remote https://github.com/tmchow/illo-skill.git HEAD
   ```
3. Add one entry to their `.grok-plugin/marketplace.json` under `plugins[]`, a
   remote source pinned to that SHA:
   ```json
   {
     "name": "illo",
     "description": "Original editorial illustrations where a recurring mascot performs the idea.",
     "category": "creative",
     "source": {
       "source": "url",
       "url": "https://github.com/tmchow/illo-skill.git",
       "sha": "<full-40-char-sha-from-step-2>"
     },
     "homepage": "https://illo-skill.com",
     "keywords": ["illo", "illo skill", "editorial illustration"],
     "domains": ["illo-skill.com"]
   }
   ```
4. Regenerate their component index (never hand-edit it) and validate exactly
   as their CI does:
   ```bash
   python3 scripts/generate-plugin-index.py
   python3 scripts/validate-catalog.py
   python3 scripts/generate-plugin-index.py --check
   ```
5. Open the PR, fill in their template, and wait for code-owner review.

To roll out a later illo update in their catalog, bump the pinned `sha` in the
existing entry — never open a second, parallel entry.

Do not confuse this with our own `.grok-plugin/marketplace.json`: that file
makes this repo directly addable as a Grok marketplace
(`grok plugin marketplace add tmchow/illo-skill`) and uses a **local** source;
the xAI entry above lives in *their* repo and uses a **remote** source pinned
to a SHA.

## Publishing to ClawHub

Single-skill repo, so publishing is driven by the Release Please release.
There is no opt-in registry (that was an agent-skills mechanism).

- **On Release Please release**, `.github/workflows/release-please.yml` calls
  `.github/workflows/publish-clawhub.yml`, which publishes `illo` when its
  `SKILL.md` `version:` is **new** on ClawHub. An already-published version is
  skipped in the release flow so reruns stay safe.
- **Manual dispatch** is strict: an already-published version fails loudly.
  Input: `changelog` (optional, defaults to a sha-stamped message).
- Auth comes from the `CLAW_TOKEN` repository secret (a ClawHub API token).
- The ClawHub slug is `illo` — it predates this repo (first published from
  agent-skills), so OpenClaw users were unaffected by the move.

## License guidance

The repo license is MIT and the skill's frontmatter says `license: MIT`.
`skills/illo/NOTICE` carries attribution for the Blot character and bundled
artwork — keep it shipping inside the skill directory.

## Validate before committing

- Frontmatter parses as valid YAML.
- `name` == directory name (`illo`), lowercase kebab-case.
- `description` ≤ 1024 characters.
- Any install/command syntax in `README.md` or `SKILL.md` is real — checked
  against the tool's `--help`, not guessed. Installer syntax is
  runtime-specific: skills CLI against `npx -y skills --help`, Hermes
  against `hermes skills --help` and `/skills`, OpenClaw against
  `openclaw skills --help` and ClawHub publish/install output.
- If assets changed: `python3 .github/scripts/regen_asset_checksums.py`
  (CI also regenerates on the PR branch).
