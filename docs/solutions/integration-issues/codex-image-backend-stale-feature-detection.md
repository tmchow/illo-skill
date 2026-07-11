---
title: Codex image backend silently disabled after upstream removed an experimental feature flag
date: 2026-07-11
category: integration-issues
module: illo-codex-backend
problem_type: integration_issue
component: tooling
symptoms:
  - "illo silently stopped using the free Codex image backend; every render fell back to OpenRouter/Grok"
  - "`illo doctor` reported `codex cli: present but not usable` despite a working, logged-in `codex` CLI"
  - "`codex features list` no longer contained an `imagegenext` row"
root_cause: wrong_api
resolution_type: code_fix
severity: high
tags: [codex, capability-detection, feature-detection, cli-integration, image-backend, upstream-drift]
---

# Codex image backend silently disabled after upstream removed an experimental feature flag

## Problem
illo detects whether the free Codex image backend is usable by parsing `codex features list`. It required **two** rows — the stable `image_generation` feature **and** an experimental `imagegenext` extension. Codex CLI 0.144 removed `imagegenext` (folding its behavior into stable `image_generation`), so detection declared a fully-working, logged-in Codex CLI unusable and every render fell back to OpenRouter (needs an API key) or Grok.

## Symptoms
- Codex subscribers lost the free image backend with no error — renders quietly used a fallback backend.
- `illo doctor` printed `codex cli: present but not usable — run codex login, or this host lacks image_generation/imagegenext support` even when logged in.
- `codex features list` on 0.144 showed `image_generation  stable  true` but no `imagegenext` row at all.

## What Didn't Work
- **Assuming a bug where `imagegenext` was "missing".** The instinct was that Codex had broken something. It hadn't — `imagegenext` was an experimental extension that got *promoted*: upstream `openai/codex` now ships native artifact handling on the stable feature (`image_generation_artifact_path()`, `ImageGenerationItem.saved_path`), and the experimental flag was deleted once the behavior stabilized. The stable `image_generation` row **was** the replacement, not a peer that lost its partner.

## Solution
Gate detection on the stable feature alone, and drop the now-dead experimental flag from the generation path.

```python
# skills/illo/scripts/illo.py — _detect_codex()

# Before: required both rows; the experimental one had just been removed upstream
low = out.lower()
if (rc != 0
        or CODEX_IMAGE_FEATURE not in low
        or CODEX_IMAGEGEN_EXT_FEATURE not in low):   # <- always True on 0.144
    return False

# After: the stable feature is the whole capability signal
if rc != 0 or CODEX_IMAGE_FEATURE not in out.lower():
    return False
```

Also removed from `codex_exec_generate()`: the `--enable imagegenext` flag (verified a harmless no-op on 0.144 — `codex -c features.imagegenext=true` exits 0 — but dead), the `CODEX_IMAGEGEN_EXT_FEATURE` constant, and the obsolete `imagegenext` namespace-collision error branch. Updated `doctor` output and `skills/illo/references/backends.md` to match.

## Why This Works
The artifact-emission behavior `imagegenext` used to force is now intrinsic to the stable `image_generation` feature, so its presence alone proves capability. Verified end-to-end on Codex CLI 0.144.0: `illo doctor` reports `codex cli: usable (logged in, image_generation available)`, and a real `illo generate --backend codex` render produced a genuine gpt-image-2 artifact (`"backend": "codex"`, 1254×1254 PNG) with no flag passed.

## Prevention
- **Gate capability detection on an upstream tool's STABLE surface, never an experimental / under-development feature flag.** Experimental flags exist to be removed — when the behavior stabilizes, the flag disappears and any check that requires it flips to "unavailable" silently. `codex features list` even labels each row (`stable`, `under development`, `removed`); treat anything but `stable` as ephemeral for gating purposes.
- **When an experimental flag is added as a workaround, record its removal trigger.** The original code comment said "remove when Codex makes the extension default or replaces it with a stable equivalent" — that condition silently came true. A workaround tied to an upstream state should be re-checked on each upstream version bump, not left indefinitely.
- **Re-verify third-party-CLI integrations against each new upstream version — detection AND generation, on the real CLI.** A mocked unit test passes forever against a contract the upstream tool has already changed. The test that encoded this bug (`test_detect_codex_requires_imagegenext_row`) faithfully asserted the wrong contract; only a live `features list` + real render caught the drift.
- **Prefer a live capability probe over a hardcoded feature-name allowlist** when the upstream tool exposes one and the probe is cheap. The narrower the set of exact strings detection depends on, the more brittle it is to upstream renames/removals.

## Related Issues
- PR: tmchow/illo-skill#32 (the fix)
- The experimental flag was introduced in an earlier fix ("Fix Codex image artifact generation", commit 51cdbd5) for Codex CLI 0.141 — a workaround that outlived its upstream cause.
