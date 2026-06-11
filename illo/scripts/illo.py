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
import argparse, base64, getpass, json, mimetypes, os, pathlib, re, sys, time
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
        f"apiKey: {val(cfg['apiKey'])}" if cfg.get("apiKey")
        else "# apiKey: sk-or-...           # set via: illo.py init",
        f"model: {val(cfg['model'])}" if cfg.get("model")
        else f"# model: {DEFAULT_MODEL}   # any OpenRouter image model id",
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


def do_generate(model, content, key, out_path, want_cost):
    """Render one image to out_path; return a manifest record."""
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
        sys.exit(f"No image in response. message keys: {list(message.keys())}; "
                 f"text: {message.get('content', '')[:300]}")
    out = pathlib.Path(out_path)
    # Models return whichever encoding they like; name the file by what the
    # bytes actually are (callers read .path from the JSON line).
    actual = sniff_ext(img) or out.suffix
    if actual != out.suffix:
        out = out.with_suffix(actual)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img)
    w, h = image_size(img)
    gid = payload.get("id")
    # Absolute: IDE agents get a clickable path; chat gateways (e.g. Hermes)
    # auto-detect bare absolute media paths and deliver the file natively.
    return {"path": str(out.resolve()), "model": model, "id": gid,
            "cost": (fetch_cost(gid, key) if want_cost else None), "width": w, "height": h}


def cmd_generate(args):
    cfg = load_config()
    prompt = args.prompt or (pathlib.Path(args.prompt_file).read_text() if args.prompt_file else None)
    if not prompt:
        sys.exit("Provide --prompt or --prompt-file.")
    aspect = args.aspect or cfg.get("aspect")
    if aspect:
        prompt = f"{prompt}\n\nAspect ratio: {aspect}."

    content = [{"type": "text", "text": prompt}]
    for r in args.ref:
        content.append({"type": "image_url", "image_url": {"url": data_url(r)}})

    model = args.model or cfg.get("model") or DEFAULT_MODEL
    key = resolve_key(cfg)

    out = pathlib.Path(args.out)
    n = max(1, args.count)
    paths = [out] if n == 1 else [out.with_name(f"{out.stem}-{k + 1}{out.suffix}") for k in range(n)]
    manifest = out.parent / "manifest.jsonl"  # parent dir is created by do_generate
    # Serial renders: a partial batch still leaves a valid manifest behind.
    for p in paths:
        rec = do_generate(model, content, key, p, args.cost)
        rec["label"] = args.label or ""
        rec["prompt"] = prompt
        with manifest.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec))


def cmd_init(args):
    """Bootstrap the user config. Run by the user — prompts for the key, never echoes it."""
    p = config_path()
    if p.exists():
        try:
            import yaml  # noqa: F401 — needed to read the existing file before merging
        except ImportError:
            sys.exit(f"{p} already exists but PyYAML isn't installed, so it can't be read "
                     f"safely to merge. Install PyYAML first (python -m pip install 'PyYAML==6.0.2') or delete the file.")
    cfg = load_config()
    if args.model:
        cfg["model"] = args.model
    if args.palette:
        cfg["defaultPalette"] = args.palette
    if args.character:
        cfg["defaultCharacter"] = args.character
    if args.aspect:
        cfg["aspect"] = args.aspect
    for pair in args.watermark:
        if "=" in pair:
            dest, text = pair.split("=", 1)
            cfg.setdefault("watermark", {})[dest.strip()] = text.strip()
    if not args.no_key:
        entered = getpass.getpass("OpenRouter API key (blank to skip): ").strip()
        if entered:
            cfg["apiKey"] = entered
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(dump_config_yaml(cfg))
    os.chmod(p, 0o600)
    print(f"wrote {p} (key: {'set' if cfg.get('apiKey') else 'not set — run init again to set it'}; "
          f"model: {cfg.get('model', DEFAULT_MODEL)})")


def character_packs(cdir):
    """{name: pack-dir} for each characters/<name>/ holding a character.md."""
    return {d.name: d for d in sorted((cdir / "characters").glob("*"))
            if (d / "character.md").is_file()}


def cmd_doctor(args):
    """Preflight. Reports readiness without revealing the key; exits non-zero if not ready."""
    cfg = load_config()
    cdir = config_dir()
    p = cdir / "config.yaml"
    key_src = "config" if cfg.get("apiKey") else None
    lines = [
        f"python:  {sys.version.split()[0]}",
        f"config:  {p} ({'present' if p.exists() else 'absent'})",
        f"model:   {cfg.get('model') or DEFAULT_MODEL}",
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
    if key_src:
        lines.append(f"api key: found ({key_src})")
    else:
        lines.append(f"api key: MISSING — run: {PROG} init")
    print("\n".join(lines))
    sys.exit(0 if key_src else 1)


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
    g.add_argument("--model", help="OpenRouter image model id (overrides config/default)")
    g.add_argument("--ref", action="append", default=[], help="reference image path (repeatable)")
    g.add_argument("--aspect", help="aspect ratio hint, e.g. 16:9")
    g.add_argument("--label", help="short caption recorded in the manifest / gallery")
    g.add_argument("--count", type=int, default=1, help="render N variations (out-1, out-2, …)")
    g.add_argument("--cost", action="store_true", help="fetch each render's cost inline (adds latency)")
    g.set_defaults(func=cmd_generate)

    i = sub.add_parser("init", help="create/update user config (run this yourself)")
    i.add_argument("--model", help="default model id")
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
