#!/usr/bin/env python3
"""Sync plugin-manifest versions from the skill's SKILL.md frontmatter.

skills/illo/SKILL.md `version:` is the single source of truth. This script
copies it into every plugin manifest that carries a version field:

  .claude-plugin/plugin.json   (Claude Code)
  .codex-plugin/plugin.json    (Codex)
  .cursor-plugin/plugin.json   (Cursor)
  .grok-plugin/plugin.json     (Grok)
  gemini-extension.json        (Gemini CLI)

plus the illo entry in each marketplace catalog
(.claude-plugin/marketplace.json, .grok-plugin/marketplace.json), whose
clients show and update against the marketplace entry's version.

Run with --check to verify everything is in lockstep (exit 1 if not).
The publish workflow tags releases v<version>, which is what Copilot's
`gh skill` and Gemini's release-based update detection resolve against —
so a version mismatch here would ship inconsistent metadata.
"""
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
SKILL_MD = REPO / "skills" / "illo" / "SKILL.md"
MANIFESTS = [
    REPO / ".claude-plugin" / "plugin.json",
    REPO / ".codex-plugin" / "plugin.json",
    REPO / ".cursor-plugin" / "plugin.json",
    REPO / ".grok-plugin" / "plugin.json",
    REPO / "gemini-extension.json",
]


def skill_version():
    text = SKILL_MD.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        sys.exit(f"ERROR: no frontmatter in {SKILL_MD}")
    for line in fm.group(1).splitlines():
        if re.match(r"^version\s*:", line):
            return line.split(":", 1)[1].strip().strip("\"'")
    sys.exit(f"ERROR: no version: in {SKILL_MD} frontmatter")


MARKETPLACES = [
    REPO / ".claude-plugin" / "marketplace.json",
    REPO / ".grok-plugin" / "marketplace.json",
]


def main():
    version = skill_version()
    check = "--check" in sys.argv
    stale = []
    for path in MANIFESTS + MARKETPLACES:
        data = json.loads(path.read_text(encoding="utf-8"))
        if path in MARKETPLACES:
            target = next(p for p in data["plugins"] if p["name"] == "illo")
        else:
            target = data
        if target.get("version") == version:
            continue
        stale.append(path.relative_to(REPO).as_posix())
        if not check:
            target["version"] = version
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    if check and stale:
        sys.stderr.write(
            f"Manifest versions out of sync with SKILL.md ({version}): "
            f"{', '.join(stale)}\nRun .github/scripts/sync_plugin_versions.py\n")
        sys.exit(1)
    if stale and not check:
        print(f"synced {len(stale)} manifest(s) to {version}: {', '.join(stale)}")
    else:
        print(f"all manifests at {version}")


if __name__ == "__main__":
    main()
