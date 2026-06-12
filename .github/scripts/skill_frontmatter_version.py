#!/usr/bin/env python3
"""Print the semver `version:` from a skill's SKILL.md frontmatter.

Usage: skill_frontmatter_version.py <skill-dir>
Exits non-zero with a ::error:: annotation when missing or invalid.
"""
import re
import sys
from pathlib import Path

SEMVER = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$'


def main() -> int:
    skill = sys.argv[1]
    text = (Path(skill) / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not match:
        print(f'::error::{skill}/SKILL.md must start with YAML frontmatter containing version:', file=sys.stderr)
        return 1

    version = None
    for line in match.group(1).splitlines():
        if re.match(r'^version\s*:', line):
            version = line.split(':', 1)[1].strip().strip('"\'')
            break

    if not version:
        print(f'::error::{skill}/SKILL.md needs a frontmatter field: version: x.y.z', file=sys.stderr)
        return 1
    if not re.match(SEMVER, version):
        print(f'::error::Invalid semver in {skill}/SKILL.md: {version}', file=sys.stderr)
        return 1

    print(version)
    return 0


if __name__ == '__main__':
    sys.exit(main())
