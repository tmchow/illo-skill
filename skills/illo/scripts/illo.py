#!/usr/bin/env python3
"""Illo — editorial illustration engine + setup. OpenRouter, stdlib only.

Subcommands:
  generate   Render image(s) from a prompt (+ refs); prints a JSON line per image
             and appends to <out-dir>/manifest.jsonl. --count N for variations.
             --cutout best-effort transparent PNG for character cutouts (native
             alpha, chroma key, or opaque fallback; see cutout_alpha in JSON).
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
import argparse, base64, getpass, json, mimetypes, os, pathlib, re, shutil, struct, subprocess, sys, time
import urllib.error, urllib.request

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_PACKS_REPO = "https://raw.githubusercontent.com/tmchow/illo-characters/main"
PACK_NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
ALIASES_RE = re.compile(r"^Aliases:\s*(.+)$", re.M)
CUTOUT_CHROMA_RE = re.compile(r"^Cutout chroma:\s*\*?\*?(green|magenta)\*?\*?\s*$", re.M | re.I)
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
# Chroma key for --cutout: flat screen outside the character cluster; removed
# in post with spill suppression. Default magenta; green for forged/wrought-metal
# silhouettes (Wick). Registration-locked cutout prompts keep riso grain inside
# fills — misregistration halos read as fringe at QA.
CHROMA_MAGENTA = (255, 0, 255)
CHROMA_GREEN = (0, 255, 0)
CHROMA_KEY = CHROMA_MAGENTA
CHROMA_TOLERANCE = 40
CHROMA_SOFT = 20
CHROMA_SPILL_MIN = 18   # channel dominance over the other two → spill candidate
CHROMA_SPILL_FLOOR = 45 # ignore tiny channel noise on very dark pixels
CHROMA_SPILL_STRONG = 30  # dominance this high keys even when G is below floor
# Cutout QA hints on a clean-alpha output (warnings, never gate cutout_alpha):
CUTOUT_FRINGE_WARN = 20   # fringe px below the clean-alpha gate but worth a QA look
CUTOUT_EDGE_FRAC = 0.02   # opaque px along the bottom row over this frac of width →
                          # character likely touches/crops the frame (no foot margin)
# Grok Imagine: best riso quality + cheapest in testing. Note: it is reachable via
# the API but not in OpenRouter's public /models list, so an account without access
# 404s — fall back to a catalogued model like google/gemini-3.1-flash-image-preview.
DEFAULT_MODEL = "x-ai/grok-imagine-image-quality"
# OpenRouter cutouts: Grok returns JPEG (no alpha/chroma); GPT Image 2 + chroma works.
CUTOUT_OPENROUTER_MODEL = "openai/gpt-5.4-image-2"
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
# Codex CLI 0.141 exposes generated image artifacts to `codex exec` only when
# the newer imagegen extension is explicitly enabled. Without this flag, the
# text agent may see images and even claim it generated one, but no
# $CODEX_HOME/generated_images/call_*.png artifact appears; the agent may then
# satisfy the requested output path with local drawing/code, which is not an
# illo render. Keep this centralized so the flag can be removed when Codex makes
# the extension default or replaces it with a stable equivalent.
CODEX_IMAGEGEN_EXT_FEATURE = "imagegenext"
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
    the built-in image_generation feature plus the imagegenext exec-artifact
    extension available. Eligibility is a property of the execution host,
    detected — never assumed. Soft-fails to False on any non-zero exit, timeout,
    or unparseable output (→ OpenRouter); reads NO credential file and NO
    secret-shaped env var. Cached per process."""
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
    # Built-in image tool reachable, and the exec image-artifact extension
    # supported? Both show up as rows in `codex features list`.
    rc, out = _codex_run(["features", "list"])
    low = out.lower()
    if (rc != 0
            or CODEX_IMAGE_FEATURE not in low
            or CODEX_IMAGEGEN_EXT_FEATURE not in low):
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


def post_chat(model, content, key, modalities, image_config=None):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "modalities": modalities,
    }
    if image_config:
        body["image_config"] = image_config
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(body).encode(), method="POST",
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


def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _png_crc(chunk_type, chunk_data):
    import binascii
    return binascii.crc32(chunk_type + chunk_data) & 0xFFFFFFFF


def _unfilter_png(raw, width, height, bpp):
    """Reverse PNG scanline filters → contiguous pixel bytes (no filter bytes)."""
    stride = width * bpp
    out = bytearray(height * stride)
    prev = bytearray(stride)
    pos = 0
    for _y in range(height):
        ftype = raw[pos]
        pos += 1
        row = bytearray(raw[pos:pos + stride])
        pos += stride
        if ftype == 1:  # Sub
            for i in range(stride):
                left = row[i - bpp] if i >= bpp else 0
                row[i] = (row[i] + left) & 0xFF
        elif ftype == 2:  # Up
            for i in range(stride):
                row[i] = (row[i] + prev[i]) & 0xFF
        elif ftype == 3:  # Average
            for i in range(stride):
                left = row[i - bpp] if i >= bpp else 0
                row[i] = (row[i] + ((left + prev[i]) // 2)) & 0xFF
        elif ftype == 4:  # Paeth
            for i in range(stride):
                left = row[i - bpp] if i >= bpp else 0
                up = prev[i]
                up_left = prev[i - bpp] if i >= bpp else 0
                row[i] = (row[i] + _paeth(left, up, up_left)) & 0xFF
        out[_y * stride:(_y + 1) * stride] = row
        prev = row
    return bytes(out)


def _parse_png_rgb_or_rgba(data):
    """Return (width, height, rgba_bytes) from a PNG, or None if unsupported."""
    import zlib
    if data[:8] != PNG_MAGIC:
        return None
    pos = 8
    width = height = None
    color_type = None
    idat = []
    while pos + 12 <= len(data):
        length = int.from_bytes(data[pos:pos + 4], "big")
        ctype = data[pos + 4:pos + 8]
        cdata = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            width = int.from_bytes(cdata[0:4], "big")
            height = int.from_bytes(cdata[4:8], "big")
            color_type = cdata[9]
        elif ctype == b"IDAT":
            idat.append(cdata)
        elif ctype == b"IEND":
            break
    if not width or not height or color_type not in (2, 6):
        return None
    bpp = 4 if color_type == 6 else 3
    raw = zlib.decompress(b"".join(idat))
    pixels = _unfilter_png(raw, width, height, bpp)
    rgba = bytearray(width * height * 4)
    if color_type == 6:
        rgba[:] = pixels
    else:
        for i in range(width * height):
            rgba[i * 4:(i + 1) * 4] = pixels[i * 3:(i + 1) * 3] + b"\xff"
    return width, height, bytes(rgba)


def _spill_dominance(r, g, b):
    """How much one channel exceeds the other two — screen-color halo on edges."""
    return max(g - max(r, b), r - max(g, b), b - max(r, g))


def _is_green_screen(r, g, b):
    """Flat green-screen background (even when the prompt asked for magenta)."""
    return g > 150 and r < 90 and b < 90 and g - max(r, b) > 35


def _is_spill_halo(r, g, b):
    """Screen-color anti-aliasing halo on silhouette edges — not normal palette fills."""
    gb = g - max(r, b)
    # Green-screen bleed — including dark halos like (17,63,17) on black ink.
    if gb >= CHROMA_SPILL_MIN and (g > CHROMA_SPILL_FLOOR or gb >= CHROMA_SPILL_STRONG):
        return True
    # Magenta-screen bleed: R and B both high, G suppressed, similar R/B.
    if (r > g + CHROMA_SPILL_MIN and b > g + CHROMA_SPILL_MIN
            and min(r, b) > 120 and abs(r - b) < 60):
        return True
    return False


def _is_accent_halo(r, g, b, a):
    """Riso misregistration / accent ink tracing the outer silhouette."""
    if a == 0:
        return False
    return r > 150 and g < 110 and b > 80 and r > g + 35


def _despill_rgb(r, g, b, a):
    """Pull excess screen-channel tint off pixels we keep opaque."""
    if a == 0:
        return r, g, b
    gb = g - max(r, b)
    if gb >= CHROMA_SPILL_MIN and (g > CHROMA_SPILL_FLOOR or gb >= CHROMA_SPILL_STRONG):
        g = max(r, b)
    if (r > g + CHROMA_SPILL_MIN and b > g + CHROMA_SPILL_MIN
            and min(r, b) > 120 and abs(r - b) < 60):
        cap = max(g, (r + b) // 4)
        r = min(r, cap + max(g, b) + CHROMA_SPILL_MIN)
        b = min(b, cap + max(g, r) + CHROMA_SPILL_MIN)
    return r, g, b


def _chroma_alpha(r, g, b, key=CHROMA_KEY, tolerance=CHROMA_TOLERANCE, soft=CHROMA_SOFT):
    d = max(abs(r - key[0]), abs(g - key[1]), abs(b - key[2]))
    if d <= tolerance:
        return 0
    if _is_green_screen(r, g, b):
        return 0
    if _is_spill_halo(r, g, b):
        return 0
    if d >= tolerance + soft:
        return 255
    return min(255, max(0, int(255 * (d - tolerance) / soft)))


def chroma_key_to_png(data, key=CHROMA_KEY):
    """Replace chroma background + screen spill with transparency; return PNG bytes."""
    import zlib
    parsed = _parse_png_rgb_or_rgba(data)
    if not parsed:
        return None
    width, height, rgba = parsed
    out = bytearray(len(rgba))
    for i in range(0, len(rgba), 4):
        r, g, b = rgba[i], rgba[i + 1], rgba[i + 2]
        a = _chroma_alpha(r, g, b, key)
        if a:
            r, g, b = _despill_rgb(r, g, b, a)
        out[i:i + 3] = bytes((r, g, b))
        out[i + 3] = a
    # Encode RGBA PNG (filter type 0 per scanline).
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw_rows = bytearray()
    row_len = width * 4
    for y in range(height):
        raw_rows.append(0)
        start = y * row_len
        raw_rows.extend(out[start:start + row_len])
    compressed = zlib.compress(bytes(raw_rows), 9)

    def _chunk(ctype, cdata):
        return (struct.pack(">I", len(cdata)) + ctype + cdata
                + struct.pack(">I", _png_crc(ctype, cdata)))

    return (PNG_MAGIC + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", compressed)
            + _chunk(b"IEND", b""))


def analyze_cutout_alpha(img_bytes):
    """Return transparency metrics for cutout QA and routing."""
    ext = sniff_ext(img_bytes)
    w, h = image_size(img_bytes)
    out = {"ext": ext, "width": w, "height": h, "transparent": 0, "opaque": 0,
           "semi": 0, "green_fringe": 0, "magenta_fringe": 0, "accent_halo": 0,
           "fringe": 0, "bottom_edge_opaque": 0, "corner_alpha": [],
           "has_alpha": False, "clean_alpha": False}
    if ext != ".png" or not img_bytes.startswith(PNG_MAGIC):
        return out
    parsed = _parse_png_rgb_or_rgba(img_bytes)
    if not parsed:
        return out
    w, h, rgba = parsed
    for i in range(0, len(rgba), 4):
        r, g, b, a = rgba[i:i + 4]
        if a == 0:
            out["transparent"] += 1
        elif a == 255:
            out["opaque"] += 1
        else:
            out["semi"] += 1
        if a and g > max(r, b) + 10 and g > 45:
            out["green_fringe"] += 1
        if a and r > 120 and b > 120 and r > g + 15 and b > g + 15 and abs(r - b) < 60:
            out["magenta_fringe"] += 1
        if a and _is_accent_halo(r, g, b, a):
            out["accent_halo"] += 1
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    out["corner_alpha"] = [rgba[(y * w + x) * 4 + 3] for x, y in corners]
    bottom = (h - 1) * w
    out["bottom_edge_opaque"] = sum(1 for x in range(w) if rgba[(bottom + x) * 4 + 3])
    out["has_alpha"] = out["transparent"] > 0 or out["semi"] > 0
    out["fringe"] = out["green_fringe"] + out["magenta_fringe"] + out["accent_halo"]
    out["clean_alpha"] = (out["transparent"] > 1000 and all(a == 0 for a in out["corner_alpha"])
                          and out["fringe"] < 50)
    return out


def aspect_to_image_config(aspect):
    """Map illo --aspect hints to OpenRouter image_config.aspect_ratio."""
    if not aspect:
        return {}
    a = aspect.lower().replace(" horizontal", "").replace(" vertical", "").strip()
    allowed = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9",
               "1:4", "4:1", "1:8", "8:1"}
    return {"aspect_ratio": a} if a in allowed else {}


def merge_image_config(aspect, image_config_json):
    """Merge --aspect and optional --image-config JSON for OpenRouter."""
    cfg = aspect_to_image_config(aspect)
    if image_config_json:
        try:
            extra = json.loads(image_config_json)
        except json.JSONDecodeError as e:
            sys.exit(f"--image-config is not valid JSON: {e}")
        if not isinstance(extra, dict):
            sys.exit("--image-config must be a JSON object.")
        cfg.update(extra)
    return cfg or None


def resolve_generate_model(cfg, args_model, backend, cutout):
    """Resolve the OpenRouter model id for this render.

    Explicit --model wins. Cutouts on OpenRouter default to CUTOUT_OPENROUTER_MODEL
    (Grok/JPEG cannot produce compositing-ready cutouts). Editorial and Codex keep
    config/default resolution."""
    if args_model:
        return args_model
    if cutout and backend == "openrouter":
        return CUTOUT_OPENROUTER_MODEL
    return cfg.get("model") or DEFAULT_MODEL


def _prompt_non_prohibition_lines(prompt):
    for line in prompt.splitlines():
        low = line.lower()
        if "do not" in low or "never " in low:
            continue
        yield line


def _prompt_background_line(prompt):
    for line in prompt.splitlines():
        if line.strip().upper().startswith("BACKGROUND:"):
            return line
    return ""


def _prompt_suggests_green_screen(prompt):
    body = "\n".join(_prompt_non_prohibition_lines(prompt)).lower()
    return any(t in body for t in ("forged-metal", "forged metal", "wrought-iron",
                                   "wrought iron"))


def parse_cutout_chroma(spec_text):
    """Return 'green'|'magenta' from a character.md Cutout chroma: line, or None."""
    m = CUTOUT_CHROMA_RE.search(spec_text or "")
    return m.group(1).lower() if m else None


def pack_dir_for_ref(ref_path):
    """Pack directory when ref_path is a pack's reference image, else None."""
    rp = pathlib.Path(ref_path).expanduser().resolve()
    if not rp.name.lower().startswith("reference"):
        return None
    pack = rp.parent
    return pack if (pack / "character.md").is_file() else None


def bundled_blot_ref_paths():
    assets = SKILL_DIR / "assets"
    return {p.resolve() for p in assets.glob("character-reference*") if p.is_file()}


def shipped_blot_cutout_chroma():
    spec = SKILL_DIR / "references" / "character.md"
    if spec.is_file():
        return parse_cutout_chroma(spec.read_text(encoding="utf-8", errors="replace"))
    return None


def resolve_cutout_chroma_from_context(refs, cfg):
    """Pack-declared cutout chroma from --ref or the configured default character."""
    for ref in refs or []:
        pack = pack_dir_for_ref(ref)
        if pack:
            chroma = parse_cutout_chroma((pack / "character.md").read_text(
                encoding="utf-8", errors="replace"))
            if chroma:
                return chroma
    for ref in refs or []:
        if pathlib.Path(ref).expanduser().resolve() in bundled_blot_ref_paths():
            return shipped_blot_cutout_chroma() or "magenta"
    default_char = (cfg or {}).get("defaultCharacter")
    if default_char and not refs:
        pack = config_dir() / "characters" / default_char
        spec = pack / "character.md"
        if spec.is_file():
            chroma = parse_cutout_chroma(spec.read_text(encoding="utf-8", errors="replace"))
            if chroma:
                return chroma
    return None


def resolve_chroma_key(prompt, override=None, pack_chroma=None):
    """Pick the chroma screen color for this cutout prompt."""
    if override == "green":
        return CHROMA_GREEN
    if override == "magenta":
        return CHROMA_MAGENTA
    if pack_chroma == "green":
        return CHROMA_GREEN
    if pack_chroma == "magenta":
        return CHROMA_MAGENTA
    bg = _prompt_background_line(prompt).upper()
    if "#00FF00" in bg:
        return CHROMA_GREEN
    if "#FF00FF" in bg:
        return CHROMA_MAGENTA
    if _prompt_suggests_green_screen(prompt):
        return CHROMA_GREEN
    return CHROMA_MAGENTA


def chroma_background_line(key):
    if key == CHROMA_GREEN:
        return ("BACKGROUND: solid flat chroma green exactly #00FF00 everywhere outside "
                "the character and its contact cluster — perfectly uniform, no paper grain, "
                "no gradient, no cast shadow on the green, no vignette. The green exists only "
                "for transparency extraction; it must not bleed onto the mascot outline.")
    return ("BACKGROUND: solid flat chroma magenta exactly #FF00FF everywhere outside "
            "the character and its contact cluster — perfectly uniform, no paper grain, "
            "no gradient, no cast shadow on the magenta, no vignette. The magenta exists only "
            "for transparency extraction; it must not bleed onto the mascot outline.")


def _prompt_has_chroma_background(prompt):
    return bool(_prompt_background_line(prompt))


def apply_cutout_postprocess(img_bytes, out_path, key=CHROMA_MAGENTA):
    """Chroma-key to transparent PNG; return (bytes, resolved_path) or None."""
    keyed = chroma_key_to_png(img_bytes, key=key)
    if keyed is None:
        return None
    out = pathlib.Path(out_path).with_suffix(".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(keyed)
    return keyed, out.resolve()


def _place_opaque(img_bytes, out_path):
    """Write image bytes without cutout processing."""
    out = pathlib.Path(out_path)
    actual = sniff_ext(img_bytes) or out.suffix
    if actual != out.suffix:
        out = out.with_suffix(actual)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img_bytes)
    w, h = image_size(img_bytes)
    return out.resolve(), w, h


def _cutout_quality_note(analysis):
    """QA warnings for a clean-alpha cutout. These never gate cutout_alpha —
    transparency is real; the agent re-rolls on framing/fringe at QA."""
    notes = []
    w = analysis.get("width") or 0
    if w and analysis.get("bottom_edge_opaque", 0) > max(4, int(w * CUTOUT_EDGE_FRAC)):
        notes.append("character touches the bottom frame edge — verify feet aren't "
                     "cropped and a transparent margin sits below them")
    fringe = analysis.get("fringe", 0)
    if fringe >= CUTOUT_FRINGE_WARN:
        if analysis.get("accent_halo", 0) >= CUTOUT_FRINGE_WARN:
            notes.append("accent-colored halo on the silhouette — use registration-locked "
                         "STYLE (no ink-layer offset) and re-roll")
        else:
            notes.append("residual screen-color fringe near the silhouette — check edges "
                         "or try the other chroma screen")
    return ("QA: " + "; ".join(notes) + ".") if notes else None


def place_cutout_image(img_bytes, out_path, chroma_key=CHROMA_MAGENTA):
    """Best-effort cutout placement: native alpha → chroma → opaque fallback."""
    meta = {"cutout": True, "cutout_alpha": False, "cutout_method": None,
            "cutout_note": None,
            "cutout_chroma": "green" if chroma_key == CHROMA_GREEN else "magenta"}
    analysis = analyze_cutout_alpha(img_bytes)
    if analysis["clean_alpha"]:
        out = pathlib.Path(out_path).with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(img_bytes)
        w, h = image_size(img_bytes)
        meta.update({"cutout_alpha": True, "cutout_method": "native",
                     "cutout_note": _cutout_quality_note(analysis)})
        return out.resolve(), w, h, meta
    keyed = apply_cutout_postprocess(img_bytes, out_path, key=chroma_key)
    if keyed:
        keyed_bytes, out = keyed
        post = analyze_cutout_alpha(keyed_bytes)
        if post["clean_alpha"]:
            w, h = image_size(keyed_bytes)
            meta.update({"cutout_alpha": True, "cutout_method": "chroma",
                         "cutout_note": _cutout_quality_note(post)})
            return out, w, h, meta
        if post["has_alpha"]:
            meta["cutout_note"] = ("Chroma key produced weak alpha (corners or "
                                   "background not fully transparent).")
    sys.stderr.write("note: cutout transparency unavailable — delivering opaque image "
                     "(see cutout_alpha in JSON).\n")
    path, w, h = _place_opaque(img_bytes, out_path)
    meta["cutout_method"] = "opaque_fallback"
    if analysis["ext"] == ".jpg":
        meta["cutout_note"] = "Model returned JPEG; chroma key skipped."
    elif analysis["ext"] == ".png" and not analysis["has_alpha"]:
        meta["cutout_note"] = ("Model returned opaque PNG; chroma key failed "
                               "(background may be missing or not a flat chroma screen).")
    else:
        meta["cutout_note"] = "Could not extract transparency from this output."
    return path, w, h, meta


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


def openrouter_generate(model, content, key, image_config=None):
    """OpenRouter backend (the dispatch seam). Returns (img_bytes, partial_record) for
    cmd_generate to place; the wire payload is byte-identical to the pre-refactor
    path. Hard caller errors (no usable response, fatal HTTP) stay `sys.exit`; a
    "no image after retry" outcome raises BackendUnavailable so it can fall
    through to another backend instead of killing the run."""
    try:
        payload = post_chat(model, content, key, ["image", "text"], image_config)
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        # Some models are image-only and 404 on ["image","text"] — retry image-only.
        if e.code == 404 and "modalit" in detail.lower():
            try:
                payload = post_chat(model, content, key, ["image"], image_config)
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
                                 "or image_generation/imagegenext unavailable).")
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
           "--sandbox", "workspace-write", "--skip-git-repo-check",
           "--enable", CODEX_IMAGEGEN_EXT_FEATURE]
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
        combined = redact((proc.stdout or "") + (proc.stderr or ""))
        low = combined.lower()
        if ("tools.namespace" in low and "image_gen" in low and "collid" in low):
            raise BackendUnavailable(
                "codex exec imagegenext namespace collision; this Codex CLI build "
                "cannot use the Codex image backend reliably. Upgrade Codex "
                "or use the OpenRouter backend.")
        raise BackendUnavailable(
            f"codex exec exited {proc.returncode}: {combined[:300]}")
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


def place_image(img_bytes, out_path, cutout=False, chroma_key=CHROMA_MAGENTA):
    """Write image bytes to out_path, renaming by the real encoding (callers read
    .path from the JSON line), and return (resolved_path, width, height, cutout_meta)."""
    if cutout:
        return place_cutout_image(img_bytes, out_path, chroma_key=chroma_key)
    path, w, h = _place_opaque(img_bytes, out_path)
    return path, w, h, {}


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

    backend = resolve_backend(cfg, args.backend)
    if backend is None:
        # Neither backend configured — name both fixes.
        sys.exit(f"No image backend ready. Either install + `codex login` to use "
                 f"your Codex subscription, or run `{PROG} init` to set an "
                 f"OpenRouter key.")

    model = resolve_generate_model(cfg, args.model, backend, args.cutout)
    aspect = args.aspect or cfg.get("aspect")
    if args.cutout and not args.aspect:
        aspect = "1:1"
    image_config = merge_image_config(aspect if backend == "openrouter" else None,
                                      getattr(args, "image_config", None))
    pack_chroma = resolve_cutout_chroma_from_context(args.ref, cfg) if args.cutout else None
    chroma_key = resolve_chroma_key(prompt, getattr(args, "chroma", None),
                                    pack_chroma=pack_chroma) if args.cutout else None
    if aspect:
        prompt = f"{prompt}\n\nAspect ratio: {aspect}."
    if args.cutout and not _prompt_has_chroma_background(prompt):
        prompt = f"{prompt}\n\n{chroma_background_line(chroma_key)}"

    out = pathlib.Path(args.out)
    n = max(1, args.count)
    paths = [out] if n == 1 else [out.with_name(f"{out.stem}-{k + 1}{out.suffix}") for k in range(n)]
    manifest = out.parent / "manifest.jsonl"  # parent dir is created by place_image
    # Serial renders: a partial batch still leaves a valid manifest behind.
    for p in paths:
        rec = _render_one(backend, cfg, prompt, model, args.ref, args.cost, p,
                          cutout=args.cutout, image_config=image_config,
                          chroma_key=chroma_key)
        rec["label"] = args.label or ""
        rec["prompt"] = prompt
        with manifest.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec))


def _apply_cutout_meta(rec, cutout_meta):
    """Merge cutout placement metadata into a manifest record."""
    if not cutout_meta:
        return rec
    for key in ("cutout", "cutout_alpha", "cutout_method", "cutout_note", "cutout_chroma"):
        if key in cutout_meta and cutout_meta[key] is not None:
            rec[key] = cutout_meta[key]
    return rec


def _render_one(backend, cfg, prompt, model, refs, want_cost, out_path,
                cutout=False, image_config=None, chroma_key=CHROMA_MAGENTA):
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
                return _openrouter_record(cfg, prompt, model, refs, want_cost, out_path,
                                          cutout=cutout, image_config=image_config,
                                          chroma_key=chroma_key)
            sys.exit(f"Codex backend failed and no OpenRouter key is set: {e}\n"
                     f"Fix: ensure Codex CLI is installed + `codex login`, or run "
                     f"`{PROG} init` to set an OpenRouter key.")
        img = produced.read_bytes()
        path, w, h, cutout_meta = place_image(img, out_path, cutout=cutout,
                                              chroma_key=chroma_key)
        # gpt-image-2 on the free built-in tool: no model id, no per-image cost,
        # so never fetch_cost a codex-served record.
        rec = {"path": str(path), "model": meta["model"], "id": meta["id"],
               "backend": "codex", "cost": None, "width": w, "height": h}
        return _apply_cutout_meta(rec, cutout_meta)
    return _openrouter_record(cfg, prompt, model, refs, want_cost, out_path,
                              cutout=cutout, image_config=image_config,
                              chroma_key=chroma_key)


def _openrouter_record(cfg, prompt, model, refs, want_cost, out_path,
                       cutout=False, image_config=None, chroma_key=CHROMA_MAGENTA):
    # OpenRouter takes the references inline as base64 data-URLs; build that here
    # so a Codex-only render never pays to encode a sheet codex exec sends via -i.
    content = [{"type": "text", "text": prompt}]
    for r in refs:
        content.append({"type": "image_url", "image_url": {"url": data_url(r)}})
    key = resolve_key(cfg)
    img, meta = openrouter_generate(model, content, key, image_config)
    path, w, h, cutout_meta = place_image(img, out_path, cutout=cutout,
                                          chroma_key=chroma_key)
    # Absolute: IDE agents get a clickable path; chat delivery (e.g. Hermes
    # MEDIA: attachment tags) needs the absolute path to build the tag.
    rec = {"path": str(path), "model": meta["model"], "id": meta["id"],
           "backend": "openrouter",
           "cost": (fetch_cost(meta["id"], key) if want_cost else None),
           "width": w, "height": h}
    return _apply_cutout_meta(rec, cutout_meta)


def _codex_refs(refs, cfg):
    """Reference image(s) to attach with `codex exec -i` for character lock. Passes every --ref the caller gives (the active character sheet, plus
    any finished-look style anchor illo adds for set consistency); else falls
    back to a configured default character's reference.png so the mascot still
    locks if --ref was omitted.

    With neither a --ref nor a default character there is nothing to lock to —
    a ref-less render, exactly what bootstrapping a brand-new character's first
    model sheet needs (character-builder step 4). gpt-image-2 via `codex exec`
    does text-to-image fine with no -i, and OpenRouter already renders ref-less
    without complaint, so Codex matches it rather than refusing (which had left
    Codex-only users unable to create a character). A one-line note marks the
    lockless render so a genuinely-forgotten --ref on a scene is still visible."""
    if refs:
        return list(refs)
    default_char = cfg.get("defaultCharacter")
    if default_char:
        ref = config_dir() / "characters" / default_char / "reference.png"
        if ref.is_file():
            return [str(ref)]
    sys.stderr.write("note: rendering with no character reference (no --ref, no "
                     "default character) — expected when bootstrapping a new "
                     "character's model sheet.\n")
    return []


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


def pack_aliases(pack_dir):
    """The pack's Aliases: line as a list (subject synonyms for "use ox"-style
    selection), or [] when absent — lets the agent resolve a character by what
    it is, not just its pack name."""
    spec = pack_dir / "character.md"
    if not spec.is_file():
        return []
    m = ALIASES_RE.search(spec.read_text(encoding="utf-8", errors="replace"))
    return [a.strip() for a in m.group(1).split(",") if a.strip()] if m else []


def aka_suffix(aliases):
    """Display suffix ' (aka a, b)' for an alias list, '' when empty."""
    return f" (aka {', '.join(aliases)})" if aliases else ""


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
        notes = []
        for n, d in packs.items():
            note = n + aka_suffix(pack_aliases(d))
            notes.append(note + ("" if (d / "reference.png").is_file() else " (reference.png MISSING)"))
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
    # Codex CLI detection — present / logged-in / image_generation + imagegenext,
    # or why not.
    # codex_available() short-circuits at the first failure, so report by stage.
    # Only fall back to a fresh PATH walk when the cached check already said not-usable.
    if codex_ok:
        lines.append("codex cli: usable (logged in, image_generation + imagegenext available)")
    elif shutil.which("codex"):
        lines.append("codex cli: present but not usable — run `codex login`, "
                     "or this host lacks image_generation/imagegenext support")
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
              f"{p.get('description', '')}{aka_suffix(p.get('aliases') or [])}{mark}")


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
    g.add_argument("--image-config",
                   help="OpenRouter image_config JSON object (merged with --aspect); "
                        "e.g. '{\"aspect_ratio\":\"1:1\"}'")
    g.add_argument("--chroma", choices=("magenta", "green"),
                   help="cutout chroma screen color (default: pack Cutout chroma line, "
                        "then prompt BACKGROUND:, then heuristics)")
    g.add_argument("--label", help="short caption recorded in the manifest / gallery")
    g.add_argument("--count", type=int, default=1, help="render N variations (out-1, out-2, …)")
    g.add_argument("--cutout", action="store_true",
                   help="character cutout: best-effort transparent PNG (native alpha, "
                        "chroma key, or opaque fallback with cutout_alpha in JSON)")
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
