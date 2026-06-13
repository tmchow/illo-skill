#!/usr/bin/env python3
"""Illo — editorial illustration engine + setup. OpenRouter, stdlib only.

Subcommands:
  generate   Render image(s) from a prompt (+ refs); prints a JSON line per image
             and appends to <out-dir>/manifest.jsonl. --count N for variations.
  newrun     Make + print a fresh batch dir: $ILLO_TMP (or /tmp/illo) / <runid>.
  gallery    Build a self-contained index.html from a run dir's manifest.jsonl.
  init       Create/update the user config (run by the user; prompts for the key).
  doctor     Preflight: report whether the skill is ready to generate.
  packs      Community character packs: list / show <name> / install <name>.

Resolution (generate):
  api key : config "apiKey" only — written by `init` (user-run, mode 600)
  model   : --model    >  config "model"        >  built-in default
  aspect  : --aspect   >  config "aspect"

The config file is an OPTIONAL user-level YAML file at
${XDG_CONFIG_HOME:-~/.config}/illo/config.yaml — never commit it. Reading it
needs PyYAML; if PyYAML is absent, a minimal stdlib parser still reads the
flat string keys (apiKey, model, …), so generation stays install-free.
The engine never reads secrets from the environment.
The agent must NOT enter the key: `init` is run by the user.
"""
import argparse, base64, getpass, json, mimetypes, os, pathlib, re, shutil, subprocess, sys, time
import urllib.error, urllib.request

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_PACKS_REPO = "https://raw.githubusercontent.com/tmchow/illo-characters/main"
PACK_NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
# Grok Imagine: best riso quality + cheapest in testing. Note: it is reachable via
# the API but not in OpenRouter's public /models list, so an account without access
# 404s — fall back to a catalogued model like google/gemini-3.1-flash-image-preview.
DEFAULT_MODEL = "x-ai/grok-imagine-image-quality"
PROG = pathlib.Path(__file__).name
SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent

# Codex backend: illo drives the user's already-installed,
# already-logged-in Codex CLI via `codex exec` to reach its built-in
# image_generation tool (gpt-image-2, billed to the user's Codex subscription,
# no API key). illo handles NO token: it runs no OAuth, reads no ~/.codex/auth.json,
# and hits no endpoint — the only privileged action is a subprocess call to the
# user's own CLI. Subprocess to `codex` is the ONE sanctioned exception to the
# stdlib-over-subprocess rule — a benign call to a known CLI, not a credential read.
BACKENDS = ("codex", "openrouter")
# Config schema version. 2 is the first version that has the Codex/OpenRouter
# backend choice. A config without this key (or below) predates the choice, so
# the user has never been offered Codex vs OpenRouter — `generate` hard-stops and
# tells them to re-run `init` to choose (see _config_is_stale); `init` re-stamps it.
CONFIG_VERSION = 2
# Where the built-in tool drops images when it ignores the requested path. The
# spike found Orca relocates CODEX_HOME under Library/Application Support, so the
# adapter resolves $CODEX_HOME at run time and NEVER hardcodes ~/.codex.
CODEX_GENERATED_SUBDIR = "generated_images"
# Detection commands are short; generation is an agent turn that fires an image
# tool, so it needs a generous ceiling (seconds).
CODEX_DETECT_TIMEOUT = 20
CODEX_EXEC_TIMEOUT = 600
# Slack on the "file must postdate this exec" floor, for filesystem mtime
# granularity / clock skew between the wall clock and the file's mtime source.
CODEX_MTIME_SKEW = 2.0
# `codex features list` row that means the built-in image tool is reachable.
CODEX_IMAGE_FEATURE = "image_generation"
# Secret-shaped tokens we strip from any captured subprocess output before it
# could reach a terminal (redact, never print raw stdout/stderr).
SECRET_RE = re.compile(r"\b(sk-[A-Za-z0-9_-]{8,}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_.-]+)")


class BackendUnavailable(Exception):
    """A backend could not produce an image for a non-fatal reason (Codex CLI
    missing/logged-out, `codex exec` errored or timed out, unsupported platform,
    or OpenRouter returned no image after a retry). cmd_generate catches this and
    falls back to another configured backend; it is NOT a hard caller error
    (those stay `sys.exit`)."""


def redact(text):
    """Mask secret-shaped substrings in captured subprocess output. Codex output
    should never carry a token, but redact defensively so a stray bearer/key in a
    diagnostic line cannot be echoed to the terminal or a transcript."""
    return SECRET_RE.sub("<redacted>", text or "")


def _codex_run(args):
    """Run a short `codex` subcommand and return (rc, combined-output). Any
    failure mode — missing binary, non-zero exit, timeout — collapses to a
    non-zero rc so callers can treat detection failures as soft (return False),
    never crash. Output is captured (text) for parsing; callers redact before
    printing. Reads no env var and no credential file."""
    try:
        proc = subprocess.run(
            ["codex"] + args, capture_output=True, text=True,
            timeout=CODEX_DETECT_TIMEOUT)
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return 1, ""
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


_CODEX_AVAILABLE = None  # per-process cache so detection's subprocesses run once


def codex_available():
    """True iff the host has a USABLE Codex CLI: `codex` on PATH, logged in, and
    the built-in image_generation feature available. Eligibility is a
    property of the execution host, detected — never assumed. Soft-fails to False
    on any non-zero exit, timeout, or unparseable output (→ OpenRouter); reads NO
    credential file and NO secret-shaped env var. Cached per process."""
    global _CODEX_AVAILABLE
    if _CODEX_AVAILABLE is not None:
        return _CODEX_AVAILABLE
    _CODEX_AVAILABLE = _detect_codex()
    return _CODEX_AVAILABLE


def _detect_codex():
    if not shutil.which("codex"):
        return False
    # Logged in? `codex login status` exits 0 and says so when authenticated.
    rc, out = _codex_run(["login", "status"])
    if rc != 0 or "logged in" not in out.lower():
        return False
    # Built-in image tool reachable? It shows up as a row in `codex features list`.
    rc, out = _codex_run(["features", "list"])
    if rc != 0 or CODEX_IMAGE_FEATURE not in out.lower():
        return False
    return True


def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return pathlib.Path(base) / "illo"


def config_path():
    return config_dir() / "config.yaml"


def parse_flat_yaml(text):
    """Stdlib fallback for the config `init` writes: top-level `key: value`
    string pairs only (nested maps like `watermark` need PyYAML). Unquoted
    values containing ':' or ' #' would be misread — `init` always quotes
    those, so quote them in hand edits too."""
    cfg = {}
    for line in text.splitlines():
        if not line or line.startswith((" ", "\t", "#")) or ":" not in line:
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        if v[:1] in ("'", '"'):
            v = v.strip("'\"")
        else:
            v = v.split(" #")[0].strip()
        if k.strip() and v:
            cfg[k.strip()] = v
    return cfg


def needs_pyyaml(text):
    """True when the config holds content the flat fallback parser can't
    round-trip — indented lines or block-map intros like `watermark:`.
    Rewriting such a file from a flat parse would silently drop that data."""
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in (" ", "\t"):
            return True
        if line.split(" #")[0].rstrip().endswith(":"):
            return True
    return False


def load_config():
    """Read the optional YAML config. Graceful: returns {} (with a note) if the
    file is absent or unparseable. Without PyYAML, falls back to a flat parse
    of the string keys (apiKey, model, …) so generation needs no installs."""
    p = config_path()
    if not p.exists():
        return {}
    try:
        import yaml
    except ImportError:
        sys.stderr.write(f"note: PyYAML not installed — reading only {p}'s flat keys "
                         f"(nested keys like watermark need: python -m pip install 'PyYAML==6.0.2').\n")
        return parse_flat_yaml(p.read_text())
    try:
        return yaml.safe_load(p.read_text()) or {}
    except Exception as e:
        sys.stderr.write(f"note: could not parse {p}: {e}\n")
        return {}


def dump_config_yaml(cfg):
    """Serialize our small, fixed config to commented YAML (no PyYAML needed to write)."""
    def val(v):
        s = str(v)
        return f'"{s}"' if (not s or s[0] in "@#&*!|>%`\"'" or ":" in s) else s
    out = [
        "# ~/.config/illo/config.yaml — Illo settings. All keys optional.",
        "# Set the API key once with: illo.py init (stored here, file mode 600).",
        "",
        f"configVersion: {CONFIG_VERSION}   # schema marker; set by init — do not edit",
        "",
        f"apiKey: {val(cfg['apiKey'])}" if cfg.get("apiKey")
        else "# apiKey: sk-or-...           # set via: illo.py init",
        f"model: {val(cfg['model'])}" if cfg.get("model")
        else f"# model: {DEFAULT_MODEL}   # any OpenRouter image model id (codex backend ignores it)",
        f"backend: {val(cfg['backend'])}" if cfg.get("backend")
        else "# backend: codex            # codex (your Codex subscription) or openrouter; default: auto",
        f"defaultPalette: {val(cfg['defaultPalette'])}" if cfg.get("defaultPalette")
        else "# defaultPalette: signal     # preset or custom palette name; default: ink-punch",
        f"defaultCharacter: {val(cfg['defaultCharacter'])}" if cfg.get("defaultCharacter")
        else "# defaultCharacter: my-bot    # a pack in characters/<name>/; default: the shipped character",
        f"packsRepo: {val(cfg['packsRepo'])}" if cfg.get("packsRepo")
        else f"# packsRepo: {DEFAULT_PACKS_REPO}   # raw base URL of a character-packs repo",
        f"aspect: {val(cfg['aspect'])}" if cfg.get("aspect")
        else "# aspect: 16:9               # default aspect ratio",
        "",
        "# Watermark text per destination (your handles). Omit for no watermark.",
    ]
    wm = cfg.get("watermark") or {}
    if wm:
        out.append("watermark:")
        out += [f"  {k}: {val(v)}" for k, v in wm.items()]
    else:
        out += ["# watermark:", "#   blog: yoursite.com", '#   x: "@yourhandle"']
    return "\n".join(out) + "\n"


def resolve_key(cfg):
    key = cfg.get("apiKey")
    if not key:
        sys.exit(f"No OpenRouter key. Run: {PROG} init")
    return key


def _config_is_stale(cfg):
    """True for a config written before the backend choice existed: it has real
    content but predates CONFIG_VERSION, so the user has never picked Codex vs
    OpenRouter. An empty/absent config is NOT stale (that is first-run onboarding,
    not a migration). Keyed on the version stamp, not the backend key's absence —
    a new user who chose 'auto' also has no backend key but a current version."""
    if not cfg:
        return False
    try:
        ver = int(cfg.get("configVersion", 1))
    except (TypeError, ValueError):
        ver = 1
    return ver < CONFIG_VERSION


def migration_message():
    """Shown when an existing pre-backends config is used: hard-stop the run and
    tell the user (and any agent reusing an old playbook) to choose a backend.
    The Codex branch needs no key; OpenRouter keeps an existing key via --no-key."""
    return (
        "illo config is out of date — it predates the image-backend choice, so "
        "no backend is selected.\n"
        "illo now has two image backends. Pick one, then re-run:\n"
        f"  Codex      — free, uses your Codex subscription (draws on your Codex "
        f"quota):\n      {PROG} init --backend codex --no-key\n"
        f"  OpenRouter — pick the model (Grok Imagine, Nano Banana, GPT Image, …):\n"
        f"      {PROG} init --backend openrouter --no-key\n"
        "Agents: surface this as an interactive Codex-vs-OpenRouter choice to the "
        "user, then run the matching init.")


def resolve_backend(cfg, override=None):
    """Capability-aware backend resolution, the single source of truth for
    `generate` and `doctor`. Precedence:

      --backend  >  config `backend:`  >  capability-aware default

    The default never silently breaks an existing OpenRouter-only install on
    upgrade: a usable Codex CLI picks codex; otherwise a configured OpenRouter key
    picks openrouter; otherwise the host has neither and onboarding is needed
    (returned as None so doctor/generate can route to the right setup). An
    explicit choice is honored as-is — readiness is judged separately so doctor
    can flag a chosen-but-unusable backend without re-resolving."""
    choice = override or cfg.get("backend")
    if choice in BACKENDS:
        return choice
    if codex_available():
        return "codex"
    if cfg.get("apiKey"):
        return "openrouter"
    return None  # neither configured → caller routes to onboarding


def data_url(path):
    p = pathlib.Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"


def extract_image(message):
    """First generated image as bytes, or None.

    OpenRouter returns generated images on message.images as
    [{"type":"image_url","image_url":{"url":"data:image/...;base64,..."}}].
    """
    for img in message.get("images") or []:
        url = (img.get("image_url") or {}).get("url") if isinstance(img, dict) else None
        if url and url.startswith("data:") and ";base64," in url:
            return base64.b64decode(url.split(";base64,", 1)[1])
    return None


def post_chat(model, content, key, modalities):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "modalities": modalities,
    }).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def sniff_ext(b):
    """'.png' or '.jpg' from magic bytes, else None."""
    if b[:8] == PNG_MAGIC:
        return ".png"
    if b[:2] == b"\xff\xd8":
        return ".jpg"
    return None


def image_size(b):
    """(width, height) from PNG or JPEG bytes, or (None, None). Stdlib only."""
    try:
        # PNG: 8-byte signature, then the IHDR chunk (4-byte length, "IHDR" type,
        # then width/height as big-endian uint32 at offsets 16 and 20).
        if b[:8] == PNG_MAGIC and b[12:16] == b"IHDR":
            return int.from_bytes(b[16:20], "big"), int.from_bytes(b[20:24], "big")
        if b[:2] == b"\xff\xd8":  # JPEG: scan to a start-of-frame marker
            i = 2
            while i + 9 < len(b):
                if b[i] != 0xFF:
                    i += 1; continue
                m = b[i + 1]
                if 0xC0 <= m <= 0xCF and m not in (0xC4, 0xC8, 0xCC):
                    return int.from_bytes(b[i + 7:i + 9], "big"), int.from_bytes(b[i + 5:i + 7], "big")
                seg = int.from_bytes(b[i + 2:i + 4], "big")
                i += 2 + (seg or 1)
    except Exception:
        pass
    return None, None


def fetch_cost(gen_id, key, tries=3, delay=1.5):
    """Best-effort total_cost (USD) for a generation id; None if not ready/unknown."""
    if not gen_id or not key:
        return None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                f"https://openrouter.ai/api/v1/generation?id={gen_id}",
                headers={"Authorization": f"Bearer {key}"})
            d = json.loads(urllib.request.urlopen(req, timeout=60).read()).get("data") or {}
            if d.get("total_cost") is not None:
                return float(d["total_cost"])
        except Exception:
            pass
        if attempt < tries - 1:  # don't sleep after the final attempt
            time.sleep(delay)
    return None


def run_base():
    return pathlib.Path(os.environ.get("ILLO_TMP") or "/tmp/illo")


def openrouter_generate(model, content, key):
    """OpenRouter backend (the dispatch seam). Returns (img_bytes, partial_record) for
    cmd_generate to place; the wire payload is byte-identical to the pre-refactor
    path. Hard caller errors (no usable response, fatal HTTP) stay `sys.exit`; a
    "no image after retry" outcome raises BackendUnavailable so it can fall
    through to another backend instead of killing the run."""
    try:
        payload = post_chat(model, content, key, ["image", "text"])
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        # Some models are image-only and 404 on ["image","text"] — retry image-only.
        if e.code == 404 and "modalit" in detail.lower():
            try:
                payload = post_chat(model, content, key, ["image"])
            except urllib.error.HTTPError as e2:
                sys.exit(f"OpenRouter HTTP {e2.code}: {e2.read().decode()[:600]}")
        else:
            sys.exit(f"OpenRouter HTTP {e.code}: {detail[:600]}")
    choices = payload.get("choices") or []
    if not choices:
        sys.exit(f"No choices in response: {json.dumps(payload)[:600]}")
    message = choices[0].get("message") or {}
    img = extract_image(message)
    if not img:
        # Fallable: the model answered but produced no image — let the caller try
        # another backend rather than ending the run here.
        raise BackendUnavailable(
            f"OpenRouter returned no image. message keys: {list(message.keys())}; "
            f"text: {message.get('content', '')[:300]}")
    gid = payload.get("id")
    return img, {"model": model, "id": gid}


def _freshest_generated_image(since):
    """Newest file under $CODEX_HOME/generated_images/ that postdates `since`
    (a wall-clock float captured just before this exec ran), or None. The
    recency floor is mandatory: the dir is shared across renders and across
    concurrent codex sessions, so without it the agent failing to produce a new
    image (a non-deterministic miss) would silently return a leftover from
    a previous render or a foreign session — a duplicate in a --count batch, or
    the wrong illustration tagged success. A small CODEX_MTIME_SKEW slack
    tolerates mtime granularity / clock skew. Resolves CODEX_HOME (env, default
    ~/.codex) at run time and NEVER hardcodes ~/.codex — the spike found Orca
    relocates it. CODEX_HOME is a path, not secret-shaped, so reading it
    is allowed."""
    home = os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")
    gen = pathlib.Path(home) / CODEX_GENERATED_SUBDIR
    if not gen.is_dir():
        return None
    floor = since - CODEX_MTIME_SKEW
    recent = [(f.stat().st_mtime, f) for f in gen.iterdir() if f.is_file()]
    recent = [(m, f) for m, f in recent if m >= floor]
    if not recent:
        return None
    return max(recent, key=lambda mf: mf[0])[1]


def codex_exec_generate(prompt, refs, out_path):
    """Codex backend: drive the user's `codex exec` against
    its built-in image_generation tool (gpt-image-2, no API key, no per-image
    charge). Returns (produced_file_path, partial_record). Sends NO model id —
    gpt-image-2 is automatic on the free built-in tool, so --model never
    applies here. Every failure (CLI unusable, exec non-zero, timeout, no image)
    raises BackendUnavailable for fallback. illo handles no token; the only
    privileged action is this subprocess to the user's own CLI."""
    if not codex_available():
        raise BackendUnavailable("Codex CLI not usable (not installed, logged out, "
                                 "or image_generation feature unavailable).")
    out = pathlib.Path(out_path).resolve()
    run_dir = out.parent
    run_dir.mkdir(parents=True, exist_ok=True)
    # The free built-in tool takes no size argument, so aspect must live in the
    # prompt text — illo already states it. The spike proved positional prompts
    # break in loops, so feed the FULL prompt via STDIN ('-' mode) and instruct
    # the agent to save to a path inside run_dir.
    stdin_prompt = (f"{prompt}\n\n"
                    f"Use your built-in image generation tool to render this, "
                    f"then save the resulting image to {out} "
                    f"(overwrite if it exists). Do not ask for confirmation.")
    cmd = ["codex", "exec", "--cd", str(run_dir),
           "--sandbox", "workspace-write", "--skip-git-repo-check"]
    # Attach every reference: the active character sheet, plus any finished-look
    # style anchor illo passes for within-set consistency. codex exec -i
    # repeats, so a second --ref is no longer silently dropped.
    for r in refs:
        cmd += ["-i", str(r)]
    cmd.append("-")
    # Clear any prior file at the target so the verify-first branch below cannot
    # accept a stale render (e.g. a re-roll into the same --out) as this run's
    # output — only a file this exec actually creates counts.
    try:
        out.unlink()
    except FileNotFoundError:
        pass
    # Wall-clock floor for the fetch-fallback: any image this exec produced must
    # postdate this moment, so a stale prior render or a concurrent session's
    # file in the shared generated_images dir can't pass as our result.
    started = time.time()
    try:
        proc = subprocess.run(cmd, input=stdin_prompt, capture_output=True,
                              text=True, timeout=CODEX_EXEC_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise BackendUnavailable("codex exec timed out before producing an image.")
    except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
        # Includes the unsupported-platform case (Windows/WSL exec breakage).
        raise BackendUnavailable(f"codex exec could not run: {e}")
    if proc.returncode != 0:
        # Redact before this string can reach a terminal — never echo raw output.
        raise BackendUnavailable(
            f"codex exec exited {proc.returncode}: {redact(proc.stderr)[:300]}")
    # Verify-first (the agent's save-to-path works under workspace-write), then
    # fall back to fetching the freshest file the built-in tool dropped under
    # $CODEX_HOME/generated_images/.
    if out.is_file() and out.stat().st_size > 0:
        produced = out
    else:
        produced = _freshest_generated_image(started)
        if produced is None:
            raise BackendUnavailable("codex exec produced no retrievable image.")
    return produced, {"model": None, "id": None}


def place_image(img_bytes, out_path):
    """Write image bytes to out_path, renaming by the real encoding (callers read
    .path from the JSON line), and return (resolved_path, width, height)."""
    out = pathlib.Path(out_path)
    actual = sniff_ext(img_bytes) or out.suffix
    if actual != out.suffix:
        out = out.with_suffix(actual)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img_bytes)
    w, h = image_size(img_bytes)
    return out.resolve(), w, h


def cmd_generate(args):
    cfg = load_config()
    # An existing pre-backends config has never been offered Codex vs OpenRouter.
    # Hard-stop rather than silently picking a backend, so a user (or an agent
    # reusing an old playbook) is forced to choose once after upgrading.
    if _config_is_stale(cfg):
        sys.exit(migration_message())
    prompt = args.prompt or (pathlib.Path(args.prompt_file).read_text() if args.prompt_file else None)
    if not prompt:
        sys.exit("Provide --prompt or --prompt-file.")
    aspect = args.aspect or cfg.get("aspect")
    if aspect:
        prompt = f"{prompt}\n\nAspect ratio: {aspect}."

    backend = resolve_backend(cfg, args.backend)
    if backend is None:
        # Neither backend configured — name both fixes.
        sys.exit(f"No image backend ready. Either install + `codex login` to use "
                 f"your Codex subscription, or run `{PROG} init` to set an "
                 f"OpenRouter key.")

    model = args.model or cfg.get("model") or DEFAULT_MODEL

    out = pathlib.Path(args.out)
    n = max(1, args.count)
    paths = [out] if n == 1 else [out.with_name(f"{out.stem}-{k + 1}{out.suffix}") for k in range(n)]
    manifest = out.parent / "manifest.jsonl"  # parent dir is created by place_image
    # Serial renders: a partial batch still leaves a valid manifest behind.
    for p in paths:
        rec = _render_one(backend, cfg, prompt, model, args.ref, args.cost, p)
        rec["label"] = args.label or ""
        rec["prompt"] = prompt
        with manifest.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec))


def _render_one(backend, cfg, prompt, model, refs, want_cost, out_path):
    """Render one image through the resolved backend and place it, returning the
    manifest record. Codex failures raise BackendUnavailable and fall back to a
    configured OpenRouter key (record tagged backend=openrouter); a Codex-only
    host with no key exits with both fixes named. The single file placement,
    sniff_ext, and the additive `backend` field live here, never in a backend."""
    if backend == "codex":
        try:
            produced, meta = codex_exec_generate(prompt, _codex_refs(refs, cfg), out_path)
        except BackendUnavailable as e:
            if cfg.get("apiKey"):
                sys.stderr.write(f"note: Codex backend unavailable ({e}); "
                                 f"falling back to OpenRouter.\n")
                return _openrouter_record(cfg, prompt, model, refs, want_cost, out_path)
            sys.exit(f"Codex backend failed and no OpenRouter key is set: {e}\n"
                     f"Fix: ensure Codex CLI is installed + `codex login`, or run "
                     f"`{PROG} init` to set an OpenRouter key.")
        img = produced.read_bytes()
        path, w, h = place_image(img, out_path)
        # gpt-image-2 on the free built-in tool: no model id, no per-image cost,
        # so never fetch_cost a codex-served record.
        return {"path": str(path), "model": meta["model"], "id": meta["id"],
                "backend": "codex", "cost": None, "width": w, "height": h}
    return _openrouter_record(cfg, prompt, model, refs, want_cost, out_path)


def _openrouter_record(cfg, prompt, model, refs, want_cost, out_path):
    # OpenRouter takes the references inline as base64 data-URLs; build that here
    # so a Codex-only render never pays to encode a sheet codex exec sends via -i.
    content = [{"type": "text", "text": prompt}]
    for r in refs:
        content.append({"type": "image_url", "image_url": {"url": data_url(r)}})
    key = resolve_key(cfg)
    img, meta = openrouter_generate(model, content, key)
    path, w, h = place_image(img, out_path)
    # Absolute: IDE agents get a clickable path; chat delivery (e.g. Hermes
    # MEDIA: attachment tags) needs the absolute path to build the tag.
    return {"path": str(path), "model": meta["model"], "id": meta["id"],
            "backend": "openrouter",
            "cost": (fetch_cost(meta["id"], key) if want_cost else None),
            "width": w, "height": h}


def _codex_refs(refs, cfg):
    """Reference image(s) to attach with `codex exec -i` for character lock. Passes every --ref the caller gives (the active character sheet, plus
    any finished-look style anchor illo adds for set consistency); else falls
    back to a configured default character's reference.png so the mascot still
    locks if --ref was omitted."""
    if refs:
        return list(refs)
    default_char = cfg.get("defaultCharacter")
    if default_char:
        ref = config_dir() / "characters" / default_char / "reference.png"
        if ref.is_file():
            return [str(ref)]
    raise BackendUnavailable("Codex backend needs a character reference image "
                             "(pass --ref <sheet>) for character lock.")


def cmd_init(args):
    """Bootstrap the user config. Run by the user — prompts for the key, never echoes it."""
    p = config_path()
    if p.exists():
        try:
            import yaml  # noqa: F401 — full reader, needed only for nested keys
        except ImportError:
            # Flat keys round-trip through parse_flat_yaml; only nested
            # content (e.g. a watermark block) would be lost on rewrite.
            if needs_pyyaml(p.read_text()):
                sys.exit(f"{p} has nested settings (e.g. watermark) that need PyYAML "
                         f"to preserve when rewriting. Install it "
                         f"(python -m pip install 'PyYAML==6.0.2') "
                         f"or delete the file and re-run init.")
    cfg = load_config()
    if args.model:
        cfg["model"] = args.model
    if args.palette:
        cfg["defaultPalette"] = args.palette
    if args.character:
        cfg["defaultCharacter"] = args.character
    if args.aspect:
        cfg["aspect"] = args.aspect
    if args.backend:
        cfg["backend"] = args.backend
    for pair in args.watermark:
        if "=" in pair:
            dest, text = pair.split("=", 1)
            cfg.setdefault("watermark", {})[dest.strip()] = text.strip()
    # Codex preflight: only when a usable Codex CLI is detected, and
    # only as a user-run, consented choice — the agent never auto-enables Codex.
    # No secret is entered on this branch (the Codex path needs none). If declined
    # or unavailable, fall through to the existing hidden-prompt OpenRouter flow.
    chose_codex = (not args.no_key and not args.backend
                   and _maybe_offer_codex(cfg))
    if not chose_codex and not args.no_key:
        entered = getpass.getpass("OpenRouter API key (blank to skip): ").strip()
        if entered:
            cfg["apiKey"] = entered
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump_config_yaml(cfg))
    os.chmod(p, 0o600)
    backend_note = cfg.get("backend") or "auto"
    print(f"wrote {p} (backend: {backend_note}; "
          f"key: {'set' if cfg.get('apiKey') else 'not set — run init again to set it'}; "
          f"model: {cfg.get('model', DEFAULT_MODEL)})")


def _maybe_offer_codex(cfg):
    """If a usable Codex CLI is present, offer to generate through the user's
    Codex subscription (free, but it draws on their Codex usage quota) and to set
    it as the default. Returns True iff the user opted into Codex (so the caller
    skips the OpenRouter key prompt). Writes `backend: codex` into cfg on accept;
    enables nothing without an explicit yes."""
    if not codex_available():
        return False
    print("Detected a usable Codex CLI (logged in, image_generation available).")
    print("illo can generate images through your Codex subscription — free, but it "
          "draws on your Codex usage quota (image turns consume it faster than text).")
    ans = input("Use your Codex subscription for image generation? [y/N] ").strip().lower()
    if ans not in ("y", "yes"):
        return False
    default = input("Set Codex as the default backend? [Y/n] ").strip().lower()
    if default not in ("n", "no"):
        cfg["backend"] = "codex"
    else:
        # Opted into Codex but not as default — leave resolution capability-aware.
        cfg.pop("backend", None)
    return True


def character_packs(cdir):
    """{name: pack-dir} for each characters/<name>/ holding a character.md."""
    return {d.name: d for d in sorted((cdir / "characters").glob("*"))
            if (d / "character.md").is_file()}


def corrupted_assets():
    """Bundled binary assets that no longer match the known-good hashes in
    assets/checksums.txt — the signature of an installer that decoded
    binaries as text (some Hermes versions do this on GitHub installs)."""
    import hashlib
    manifest = SKILL_DIR / "assets" / "checksums.txt"
    if not manifest.is_file():
        return []
    bad = []
    for line in manifest.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        expected, _pin, rel = line.split(None, 2)
        f = SKILL_DIR / rel
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != expected:
            bad.append(f)
    return bad


def cmd_doctor(args):
    """Preflight. Reports readiness without revealing the key; exits non-zero if not ready."""
    cfg = load_config()
    cdir = config_dir()
    p = cdir / "config.yaml"
    has_key = bool(cfg.get("apiKey"))
    codex_ok = codex_available()
    backend = resolve_backend(cfg)  # capability-aware; honors config `backend:`
    lines = [
        f"python:  {sys.version.split()[0]}",
        f"config:  {p} ({'present' if p.exists() else 'absent'})",
        f"model:   {cfg.get('model') or DEFAULT_MODEL}"
        + ("  (openrouter only — codex uses gpt-image-2 automatically)" if backend == "codex" else ""),
    ]
    if cfg.get("defaultPalette"):
        lines.append(f"palette: {cfg['defaultPalette']} (default)")
    if cfg.get("aspect"):
        lines.append(f"aspect:  {cfg['aspect']} (default)")
    if cfg.get("watermark"):
        lines.append(f"watermark: {', '.join(sorted(cfg['watermark']))} (configured)")
    packs = character_packs(cdir)
    if packs:
        notes = [n + ("" if (d / "reference.png").is_file() else " (reference.png MISSING)")
                 for n, d in packs.items()]
        lines.append(f"characters: {', '.join(notes)} (packs in {cdir / 'characters'})")
    default_char = cfg.get("defaultCharacter")
    if default_char:
        status = "" if default_char in packs else " — no such pack"
        lines.append(f"character: {default_char} (config default{status})")
    else:
        lines.append("character: shipped default")
    user_styles = sorted(s.stem for s in (cdir / "styles").glob("*.md"))
    if user_styles:
        lines.append(f"styles: {', '.join(user_styles)} (custom looks in {cdir / 'styles'})")
    if (cdir / "palettes.md").exists():
        lines.append(f"palettes: custom file ({cdir / 'palettes.md'})")
    bad = corrupted_assets()
    if bad:
        names = ", ".join(str(f.relative_to(SKILL_DIR)) for f in bad)
        lines.append(f"assets: CORRUPTED ({names}) — reinstall the skill, or run: "
                     f"bash {SKILL_DIR / 'scripts/repair-hermes-assets.sh'}")
    else:
        lines.append("assets: OK")
    # Codex CLI detection — present / logged-in / image_generation, or why not.
    # codex_available() short-circuits at the first failure, so report by stage.
    # Only fall back to a fresh PATH walk when the cached check already said not-usable.
    if codex_ok:
        lines.append("codex cli: usable (logged in, image_generation available)")
    elif shutil.which("codex"):
        lines.append("codex cli: present but not usable — run `codex login`, "
                     "or this host lacks the image_generation feature")
    else:
        lines.append("codex cli: not installed (optional — enables free Codex-subscription images)")
    # OpenRouter key (no value ever printed).
    lines.append("api key: found (config)" if has_key
                 else f"api key: not set — run `{PROG} init` to use OpenRouter")
    # Resolved backend + transport, and whether it is actually ready (the exit
    # predicate). An OpenRouter-only install stays exit 0: doctor reports
    # the resolved backend's readiness, not a hardwired key check.
    if _config_is_stale(cfg):
        # Pre-backends config: not ready until the user makes a one-time choice.
        ready = False
        lines.append("backend: NEEDS CHOICE — this config predates the image "
                     "backend choice. Codex (free, your Codex subscription) or "
                     "OpenRouter (model choice: Grok Imagine, Nano Banana, GPT "
                     f"Image, …)? Run `{PROG} init --backend codex|openrouter "
                     "--no-key`. Agents: ask the user interactively, then run that init.")
    elif backend == "codex":
        ready = codex_ok
        lines.append("backend: codex — transport: `codex exec` (your Codex "
                     "subscription, gpt-image-2; illo stores no token)"
                     if ready else
                     "backend: codex (configured) — NOT ready: Codex CLI unusable; "
                     f"run `codex login` or set backend: openrouter / run `{PROG} init`")
    elif backend == "openrouter":
        ready = has_key
        lines.append("backend: openrouter — transport: OpenRouter API"
                     if ready else
                     f"backend: openrouter (configured) — NOT ready: no key; run `{PROG} init`")
    else:
        ready = False
        lines.append(f"backend: none ready — install + `codex login`, or run `{PROG} init` "
                     f"to set an OpenRouter key")
    # Hermes caveat: the path above is illo's default; a managed runtime may
    # resolve config elsewhere. Preserve this note for that environment.
    lines.append(f"note: config resolved at {p} (a managed runtime e.g. Hermes "
                 f"may use a different path).")
    print("\n".join(lines))
    sys.exit(0 if ready and not bad else 1)


def cmd_newrun(args):
    """Make + print a fresh run dir for a batch: $ILLO_TMP (or /tmp/illo) / <runid>."""
    rid = time.strftime("%Y%m%d-%H%M%S") + "-" + os.urandom(2).hex()
    d = run_base() / rid
    d.mkdir(parents=True, exist_ok=True)
    print(str(d))


def packs_repo(args):
    return (args.repo or load_config().get("packsRepo") or DEFAULT_PACKS_REPO).rstrip("/")


def pack_name(name):
    """Validate a pack name before it goes into a URL or filesystem path."""
    if not PACK_NAME_RE.fullmatch(name or ""):
        sys.exit(f"invalid pack name {name!r} — lowercase kebab-case only")
    return name


def fetch(url, optional=False):
    req = urllib.request.Request(url, headers={"User-Agent": "illo-skill"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        if optional:
            return None
        sys.exit(f"HTTP {e.code} fetching {url}")
    except urllib.error.URLError as e:
        if optional:
            return None
        sys.exit(f"network error fetching {url}: {e.reason}")


def repo_index(args, optional=False):
    """{name: index entry} from the packs repo ({} when optional and unavailable/unparsable)."""
    repo = packs_repo(args)
    raw = fetch(f"{repo}/index.json", optional=optional)
    if raw is None:
        return {}
    try:
        idx = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        if optional:
            return {}
        sys.exit(f"could not parse index.json from {repo}: {e}")
    return {p["name"]: p for p in idx.get("packs", []) if p.get("name")}


def installed_version(pack_dir):
    """The repo version a local pack was installed at, or None (pre-stamp installs)."""
    f = pack_dir / ".version"
    return f.read_text().strip() if f.is_file() else None


def stamp_version(dest, entry):
    """Record the index version a pack was installed at; silently a no-op without one."""
    if entry and entry.get("version"):
        (dest / ".version").write_text(entry["version"] + "\n")


def install_pack_files(repo, name, dest):
    base = f"{repo}/packs/{name}"
    # Fetch everything first so a broken remote pack exits before any disk write.
    spec = fetch(f"{base}/character.md")
    ref = fetch(f"{base}/reference.png")
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "character.md").write_bytes(spec)
    (dest / "reference.png").write_bytes(ref)


def cmd_packs_list(args):
    entries = repo_index(args)
    packs = character_packs(config_dir())
    for name, p in entries.items():
        mark = ""
        if name in packs:
            local, remote = installed_version(packs[name]), p.get("version", "")
            if local and remote and local != remote:
                mark = f"  [installed {local} — {remote} available: packs update {name}]"
            else:
                mark = "  [installed]"
        print(f"{name} {p.get('version', '')}  {p.get('author', '')} — "
              f"{p.get('description', '')}{mark}")


def cmd_packs_show(args):
    # write, not print: preserve the spec byte-for-byte (no added newline)
    sys.stdout.write(
        fetch(f"{packs_repo(args)}/packs/{pack_name(args.name)}/character.md").decode("utf-8"))


def cmd_packs_install(args):
    name = pack_name(args.name)
    local = pack_name(args.as_name) if args.as_name else name
    dest = config_dir() / "characters" / local
    if (dest / "character.md").exists() and not args.force:
        sys.exit(f"{dest} already exists — use --force to overwrite or --as <name> to rename")
    repo = packs_repo(args)
    entry = repo_index(args, optional=True).get(name)  # version stamp is best-effort
    install_pack_files(repo, name, dest)
    stamp_version(dest, entry)
    suffix = f" (as {local})" if local != name else ""
    print(f"installed {name} -> {dest}{suffix}")


def cmd_packs_update(args):
    """Re-fetch installed pack(s) from the repo. Overwrites local edits to a pack."""
    repo = packs_repo(args)
    entries = repo_index(args)
    packs = character_packs(config_dir())
    if args.name:
        names = [pack_name(args.name)]
    else:
        names = sorted(set(packs) & set(entries))
        if not names:
            sys.exit("no installed packs found in the repo index — nothing to update")
    for name in names:
        dest = packs.get(name)
        if dest is None:
            sys.exit(f"{name} is not installed — use: packs install {name}")
        entry = entries.get(name)
        if entry is None:
            sys.exit(f"{name} is not in the repo index at {repo} — a local-only "
                     f"character, or installed under a different name (--as)")
        local, remote = installed_version(dest), entry.get("version", "")
        if local and remote and local == remote and not args.force:
            print(f"{name} {local} — already up to date")
            continue
        install_pack_files(repo, name, dest)
        stamp_version(dest, entry)
        was = f"{local} -> " if local else ""
        print(f"updated {name} {was}{remote or '?'} -> {dest}")


GALLERY_CSS = """
:root{color-scheme:light dark}*{box-sizing:border-box}
body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0f1115;color:#e8eaed;padding:28px clamp(16px,4vw,56px)}
h1{font-size:21px;margin:0 0 18px}.tot{color:#9aa0a6;font-weight:400;font-size:15px}
.grid{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(400px,1fr))}
figure{margin:0;background:#171a20;border:1px solid #232830;border-radius:13px;overflow:hidden}
figure img{display:block;width:100%;height:auto;background:#f3efe6}
figcaption{padding:10px 14px 14px}
.lab{font-size:15px;font-weight:650;margin:0 0 2px}.lab:empty{display:none}
.mod{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:#7a8089;margin:0 0 4px}
.meta{color:#9aa0a6;font-size:13px;margin:0}
.pr{margin-top:8px}.pr summary{cursor:pointer;color:#8ab4f8;font-size:12px}
.pr pre{white-space:pre-wrap;font:12px/1.45 ui-monospace,Menlo,monospace;color:#c0c4c9;background:#0f1115;border:1px solid #232830;border-radius:8px;padding:10px;margin:8px 0 0;max-height:240px;overflow:auto}
.req{color:#9aa0a6;font-size:13px;margin:-8px 0 20px;max-width:920px;white-space:pre-wrap}
.req summary{cursor:pointer;list-style:none}.req summary::after{content:" …more";color:#8ab4f8}
.req[open] summary::after{content:""}
.req pre{white-space:pre-wrap;font:12px/1.45 ui-monospace,Menlo,monospace;color:#c0c4c9;background:#171a20;border:1px solid #232830;border-radius:8px;padding:10px;margin:8px 0 0;max-height:320px;overflow:auto}
"""


def build_gallery_html(recs, embed, base, title=None, request=None):
    import html as _html
    heading = _html.escape(title or "Illo gallery")
    req_html = ""
    if request:
        if len(request) > 280:
            req_html = (f'<details class="req"><summary>{_html.escape(request[:280])}</summary>'
                        f'<pre>{_html.escape(request)}</pre></details>')
        else:
            req_html = f'<p class="req">{_html.escape(request)}</p>'
    total = sum(r["cost"] for r in recs if r.get("cost"))
    cards = []
    for r in recs:
        p = pathlib.Path(r["path"])
        if embed and p.exists():
            src = data_url(p)
        else:
            src = _html.escape(os.path.relpath(p, base))
        w, h = r.get("width"), r.get("height")
        ar = ("16:9" if (w and h and abs(w / h - 16 / 9) < 0.05)
              else f"{w}×{h}" if w and h else "")
        cost = f"${r['cost']:.4f}" if r.get("cost") is not None else "—"
        meta = " · ".join(x for x in (ar, cost) if x)
        prompt = (f'<details class="pr"><summary>prompt</summary><pre>'
                  f'{_html.escape(r["prompt"])}</pre></details>') if r.get("prompt") else ""
        cards.append(
            f'<figure><img src="{src}" alt="">'
            f'<figcaption><p class="lab">{_html.escape(r.get("label") or "")}</p>'
            f'<p class="mod">{_html.escape(r.get("model") or "")}</p>'
            f'<p class="meta">{meta}</p>{prompt}</figcaption></figure>')
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8>"
            f'<meta name=viewport content="width=device-width,initial-scale=1">'
            f"<title>{heading}</title><style>{GALLERY_CSS}</style></head>"
            f'<body><h1>{heading} <span class="tot">{len(recs)} images'
            f" · ${total:.4f}</span></h1>{req_html}"
            f'<div class="grid">{"".join(cards)}</div></body></html>')


def cmd_gallery(args):
    d = pathlib.Path(args.dir)
    man = d / "manifest.jsonl"
    if not man.exists():
        sys.exit(f"No manifest.jsonl in {d}")
    recs = [json.loads(line) for line in man.read_text().splitlines() if line.strip()]
    if args.exclude:
        skip = set(args.exclude)
        recs = [r for r in recs if r.get("label") not in skip]
        if not recs:
            sys.exit("every manifest record excluded — nothing to build")
    key = load_config().get("apiKey")
    for r in recs:  # backfill any costs not captured at generate time (settled by now)
        # Codex-served records are free (no model id, no OpenRouter cost) — never
        # query OpenRouter for them, even if a stray id is ever present.
        if r.get("backend") == "codex":
            continue
        if r.get("cost") is None and r.get("id"):
            r["cost"] = fetch_cost(r["id"], key, tries=8, delay=2)
    req = d / "request.txt"
    request = req.read_text().strip() if req.is_file() else None
    out = d / "index.html"
    out.write_text(build_gallery_html(recs, args.embed, d, title=args.title, request=request))
    print(str(out.resolve()))
    if args.open:
        import webbrowser
        webbrowser.open(out.resolve().as_uri())


def main():
    ap = argparse.ArgumentParser(description="Illo editorial illustration engine.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="render one illustration")
    g.add_argument("--prompt")
    g.add_argument("--prompt-file")
    g.add_argument("--out", required=True)
    g.add_argument("--model", help="OpenRouter image model id (overrides config/default; "
                   "ignored by the codex backend, which uses gpt-image-2 automatically)")
    g.add_argument("--backend", choices=BACKENDS,
                   help="image backend (overrides config/default): codex (your Codex "
                        "subscription) or openrouter; default resolves by host capability")
    g.add_argument("--ref", action="append", default=[], help="reference image path (repeatable)")
    g.add_argument("--aspect", help="aspect ratio hint, e.g. 16:9")
    g.add_argument("--label", help="short caption recorded in the manifest / gallery")
    g.add_argument("--count", type=int, default=1, help="render N variations (out-1, out-2, …)")
    g.add_argument("--cost", action="store_true", help="fetch each render's cost inline (adds latency)")
    g.set_defaults(func=cmd_generate)

    i = sub.add_parser("init", help="create/update user config (run this yourself)")
    i.add_argument("--model", help="default model id")
    i.add_argument("--backend", choices=BACKENDS,
                   help="default image backend: codex or openrouter (skips the Codex questionnaire)")
    i.add_argument("--palette", help="default palette preset name")
    i.add_argument("--character", help="default character pack name (characters/<name>/)")
    i.add_argument("--aspect", help="default aspect ratio")
    i.add_argument("--watermark", action="append", default=[], metavar="DEST=TEXT",
                   help="default watermark text per destination, e.g. blog=yoursite.com (repeatable)")
    i.add_argument("--no-key", action="store_true", help="set prefs only; skip the key prompt")
    i.set_defaults(func=cmd_init)

    d = sub.add_parser("doctor", help="preflight readiness check")
    d.set_defaults(func=cmd_doctor)

    nr = sub.add_parser("newrun", help="make + print a fresh batch dir (/tmp/illo/<runid>)")
    nr.set_defaults(func=cmd_newrun)

    pk = sub.add_parser("packs", help="community character packs (list/show/install/update)")
    pksub = pk.add_subparsers(dest="packs_cmd", required=True)
    pl = pksub.add_parser("list", help="list packs in the community repo")
    pl.set_defaults(func=cmd_packs_list)
    ps = pksub.add_parser("show", help="print a pack's character.md (review before install)")
    ps.add_argument("name")
    ps.set_defaults(func=cmd_packs_show)
    pi = pksub.add_parser("install", help="install a pack into ~/.config/illo/characters/")
    pi.add_argument("name")
    pi.add_argument("--as", dest="as_name", metavar="NAME",
                    help="install under a different local name (collision escape)")
    pi.add_argument("--force", action="store_true", help="overwrite an existing local pack")
    pi.set_defaults(func=cmd_packs_install)
    pu = pksub.add_parser("update", help="re-fetch installed pack(s) at the repo's current version")
    pu.add_argument("name", nargs="?",
                    help="pack to update (default: every installed pack in the repo index)")
    pu.add_argument("--force", action="store_true",
                    help="re-fetch even when already at the index version")
    pu.set_defaults(func=cmd_packs_update)
    for sp in (pl, ps, pi, pu):
        sp.add_argument("--repo", help=f"raw base URL of a packs repo (default: {DEFAULT_PACKS_REPO})")

    gl = sub.add_parser("gallery", help="build a self-contained index.html from a run dir's manifest")
    gl.add_argument("dir", help="run dir containing manifest.jsonl")
    gl.add_argument("--open", action="store_true", help="open the gallery after building")
    gl.add_argument("--embed", action="store_true", help="inline images as data-URIs (single portable file)")
    gl.add_argument("--exclude", action="append", default=[], metavar="LABEL",
                    help="drop records with this exact label (repeatable) — e.g. rolls superseded by a re-roll")
    gl.add_argument("--title", help="gallery heading naming the piece/request this run is for")
    gl.set_defaults(func=cmd_gallery)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
