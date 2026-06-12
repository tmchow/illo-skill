#!/usr/bin/env python3
"""Print 'exists' or 'new' for $VERSION against a `clawhub inspect --json` dump.

Usage: VERSION=x.y.z clawhub_version_state.py <inspect-json-path>
clawhub may print progress lines before the JSON payload; they are stripped.
"""
import json
import os
import sys
from pathlib import Path


def main() -> int:
    target = os.environ['VERSION']
    raw = Path(sys.argv[1]).read_text(encoding='utf-8')

    starts = [idx for idx in (raw.find('{'), raw.find('[')) if idx != -1]
    if not starts:
        print('::error::clawhub inspect did not return JSON', file=sys.stderr)
        print(raw, file=sys.stderr)
        return 1

    try:
        data = json.loads(raw[min(starts):])
    except json.JSONDecodeError as exc:
        print(f'::error::Could not parse clawhub inspect JSON: {exc}', file=sys.stderr)
        return 1

    if isinstance(data, dict):
        items = data.get('versions') or []
    elif isinstance(data, list):
        items = data
    else:
        print(f'::error::Unexpected clawhub inspect JSON root: {type(data).__name__}', file=sys.stderr)
        return 1

    versions = [i.get('version') for i in items if isinstance(i, dict)]
    print('exists' if target in versions else 'new')
    return 0


if __name__ == '__main__':
    sys.exit(main())
