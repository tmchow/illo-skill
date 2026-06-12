#!/usr/bin/env bash
# Hermes-only preflight: verify and repair the skill's binary assets.
#
# Some Hermes versions corrupt binary files when installing multi-file skills
# from GitHub (binaries decoded as text before writing). This script verifies
# every bundled binary against assets/checksums.txt — a generated manifest of
# known-good SHA256 hashes and per-asset pin commits — and re-downloads only
# mismatched or missing files from the immutable raw URL each pin implies.
#
# Safe to run anywhere: it changes nothing when checksums already match.
# Other runtimes (Claude Code, Codex, OpenClaw) install faithfully and never
# need this. Remove once Hermes ships its installer fix.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$SKILL_DIR/assets/checksums.txt"
RAW_BASE="https://raw.githubusercontent.com/tmchow/illo-skill"

[[ -f "$MANIFEST" ]] || { echo "ERROR: $MANIFEST missing — reinstall the skill." >&2; exit 1; }

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

status=0
while read -r expected pin rel || [[ -n "${expected:-}" ]]; do
  [[ -z "$expected" || "$expected" == \#* ]] && continue
  dest="$SKILL_DIR/$rel"
  if [[ -f "$dest" ]] && [[ "$(sha256_file "$dest")" == "$expected" ]]; then
    echo "OK: $rel"
    continue
  fi
  if [[ -f "$dest" ]]; then
    echo "Checksum mismatch — repairing: $rel"
  else
    echo "Missing — downloading: $rel"
  fi
  url="$RAW_BASE/$pin/skills/illo/$rel"
  tmp="$(mktemp)"
  if ! curl -fsSL "$url" -o "$tmp"; then
    echo "ERROR: download failed: $url" >&2
    rm -f "$tmp"
    status=1
    continue
  fi
  actual="$(sha256_file "$tmp")"
  if [[ "$actual" != "$expected" ]]; then
    echo "ERROR: downloaded $rel does not match its known-good hash" >&2
    echo "  expected: $expected" >&2
    echo "  actual:   $actual" >&2
    echo "  url:      $url" >&2
    rm -f "$tmp"
    status=1
    continue
  fi
  mkdir -p "$(dirname "$dest")"
  mv "$tmp" "$dest"
  echo "Repaired: $rel"
done < "$MANIFEST"

exit "$status"
