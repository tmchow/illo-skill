<p align="center">
  <img src="_assets/illo/logo/illo-logo.png" alt="illo logo — a small screen-faced robot with a pink antenna" width="170" />
</p>

# illo skill

Original print-style illustrations for agents — a recurring mascot performs the idea.

**[illo-skill.com](https://illo-skill.com)** — live examples, character packs, and copy-paste installs.

![Using Blip, make a flowchart of how a newsletter issue ships](docs/examples/eval-blip-newsletter.png)

`Using Blip, make a flowchart of how a newsletter issue ships`

<table>
  <tr>
    <td><img src="_assets/illo/05-bridgeswap-ink-punch.png" alt="Editorial: we replatform with zero downtime" /></td>
    <td><img src="_assets/illo/styles/woodcut-minicomic.png" alt="Mini-comic: stuck, slice, shipped" /></td>
  </tr>
  <tr>
    <td align="center"><code>/illo we replatform with zero downtime</code></td>
    <td align="center"><code>/illo stuck → slice → shipped as a mini-comic</code></td>
  </tr>
  <tr>
    <td colspan="2"><img src="docs/examples/eval-blip-fanout.png" alt="Fan-out: sort incoming mail into keep, later, and trash" /></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><code>/illo Sort incoming mail into keep, later, and trash as a fan-out, using Blip</code></td>
  </tr>
</table>

## Ask it like this

```text
/illo we replatform with zero downtime
/illo how a book gets published explainer diagram
/illo using Blip, make a flowchart of how a newsletter issue ships
/illo stuck → slice → shipped as a mini-comic
/illo blot cutout waving
/illo surprise me
```

## Install

Use your runtime's native plugin or skill manager.

| Platform | Install | Update |
| --- | --- | --- |
| **Claude Code** | `/plugin marketplace add tmchow/illo-skill` then `/plugin install illo@illo-skill` | `claude plugin update illo`, or enable marketplace auto-update |
| **Codex** | `codex plugin marketplace add tmchow/illo-skill` then `codex plugin add illo@illo-skill` | `codex plugin marketplace upgrade` |
| **Grok CLI** | `grok plugin marketplace add tmchow/illo-skill` then `grok plugin install tmchow/illo-skill --trust` | `grok plugin update illo` |
| **Grok Bot** | paste the prompt below into Grok Bot. | paste the prompt again after updates |
| **Gemini CLI** | `gemini extensions install https://github.com/tmchow/illo-skill` | `gemini extensions update illo` |
| **Copilot / GitHub CLI** | `gh skill install tmchow/illo-skill illo` (cross-agent via `--agent`) | `gh skill update illo` |
| **Hermes** | `hermes skills install tmchow/illo-skill/illo` | `hermes skills update illo` |
| **OpenClaw** | `openclaw skills install illo` | reinstall with the same command |
| **Cursor** | `npx skills add tmchow/illo-skill --skill illo` (Cursor Marketplace listing pending review) | re-run the installer |
| **Other agents / last resort** | `npx skills add tmchow/illo-skill --skill illo` | `npx skills update` |

### Grok Bot

Paste this into Grok Bot; it is not a terminal command for you to run yourself.

```text
Install the illo skill and all community characters.

npx skills add tmchow/illo-skill --skill illo -g -y
```

Engines, models, cost, and API keys: [`skills/illo/README.md`](skills/illo/README.md).

MIT © Trevin Chow — [`LICENSE`](LICENSE), [`skills/illo/NOTICE`](skills/illo/NOTICE). Companion characters: [tmchow/illo-characters](https://github.com/tmchow/illo-characters).
