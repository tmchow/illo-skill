#!/usr/bin/env python3
"""Registration-locked cutout gallery — Codex sanity batch + HTML report."""
import base64
import html
import json
import os
import re
import subprocess
import sys
import textwrap
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ILLO = REPO / "skills/illo/scripts/illo.py"
BLOT_REF = REPO / "skills/illo/assets/character-reference.webp"
CHAR_BASE = "https://raw.githubusercontent.com/tmchow/illo-characters/main/packs"
RUN = Path("/tmp/illo/cutout-registration/gallery")

sys.path.insert(0, str(ILLO.parent))
import illo  # noqa: E402

SILHOUETTE = textwrap.dedent("""\
    SILHOUETTE (cutout — registration-locked): ONE locked outer contour only. All inks aligned on the
    same edge — NO ink-layer offset, NO misregistration, NO ghost plate, NO second copy of the body
    outline, NO accent-colored halo or fringe tracing the silhouette. Accent ink ONLY on the designated
    accent part, never bleeding along the outer edge.""")

STYLE_LINES = {
    "riso": "STYLE: risograph print — grainy halftone texture on fills, registration-locked single-plate silhouette, flat fills on the character only — NOT on the background.",
    "blueprint": "STYLE: engineering blueprint — white construction lines on a deep blueprint ground; registration-locked single-plate silhouette; accent fill ONLY on the designated accent part — NOT on the background.",
    "woodcut": "STYLE: woodcut print — bold carved black ink, registration-locked single-plate silhouette, flat fills on the character only — NOT on the background.",
    "pixel": "STYLE: pixel art — crisp pixel clusters, registration-locked single-plate silhouette, flat fills on the character only — NOT on the background.",
    "diorama": "STYLE: miniature diorama — matte felt-and-paper craft texture on forms, registration-locked single-plate silhouette — NOT on the background.",
    "clay": "STYLE: clay stop-motion — matte clay texture, registration-locked single-plate silhouette — NOT on the background.",
    "enamel": "STYLE: enamel pin — glossy flat fills, registration-locked single-plate silhouette — NOT on the background.",
    "gouache": "STYLE: gouache illustration — flat opaque fills, registration-locked single-plate silhouette — NOT on the background.",
    "phosphor": "STYLE: CRT phosphor — glowing lines on dark ground, registration-locked single-plate silhouette — NOT on the background.",
    "chalk": "STYLE: chalkboard — chalk lines on dark ground, registration-locked single-plate silhouette — NOT on the background.",
    "manila": "STYLE: manila folder — flat cut-paper shapes, registration-locked single-plate silhouette — NOT on the background.",
}

# Representative cross-section of the ecosystem (not all 37 — each ~2 min on Codex).
CHARACTERS = [
    {"name": "blot", "ref_local": str(BLOT_REF), "style": "riso", "cutout_chroma": "magenta",
     "spec": "the recurring mascot — a plump rounded ink-droplet body (fat soft teardrop, wide bottom, curved tip top), two simple dot eyes, blank deadpan, small stubby arms and legs; ONLY accent on droplet tip. Body #111111, eyes warm-white dots.",
     "palette": "structure ink #111111. Accent #ff3d9a ONLY on the droplet tip.",
     "pose": "front-facing friendly wave"},
    {"name": "wick", "style": "diorama", "cutout_chroma": "green",
     "spec": "a tall, thin, spindly creature built like delicate wrought-iron garden furniture, long fine dark forged-metal legs, narrow dark-metal torso and thin metal arms, two tiny dark dot eyes, blank deadpan, small glass lantern in chest with ONE small flame; flame is ONLY accent.",
     "palette": "structure ink #2a2520 for metal. Accent #e8a030 ONLY on chest flame.",
     "pose": "front-facing, torch raised in one thin metal hand"},
    {"name": "blip", "style": "riso",
     "spec": "a rounded-cube body, one rounded-rectangle screen face with two dot eyes, blank deadpan, one short antenna with accent-colored ball tip, stubby arms and legs.",
     "palette": "structure ink #111111 for outline and screen. Accent on antenna ball ONLY.",
     "pose": "front-facing friendly wave"},
    {"name": "pip", "style": "riso",
     "spec": "a small round bird mascot from the reference — dot eyes, blank deadpan, stubby body matching the sheet.",
     "palette": "structure ink #111111. Accent ONLY on the designated accent part from the reference.",
     "pose": "front-facing friendly wave"},
    {"name": "anvil", "style": "woodcut",
     "spec": "a classic anvil silhouette (flat top, one tapered horn, narrow waist, wide base) carved as solid ink, two dot eyes as uncarved paper, blank deadpan, stubby arms and legs; horn is ONLY accent.",
     "palette": "structure ink #111111. Accent ONLY on the horn.",
     "pose": "front-facing, standing"},
    {"name": "lumen", "style": "blueprint",
     "spec": "a little light-bulb mascot from the reference — dot eyes, blank deadpan, matching the sheet proportions.",
     "palette": "white construction lines on deep blueprint ground. Accent ONLY on the designated accent part.",
     "pose": "front-facing friendly wave"},
    {"name": "yoke", "style": "blueprint",
     "spec": "a placid zebu ox — one massive rounded boulder body with bold shoulder hump, tiny stubby horns, four stubby legs, two dot eyes, blank deadpan; shoulder hump is ONLY accent.",
     "palette": "white construction lines on deep blueprint ground. Accent ONLY on shoulder hump.",
     "pose": "front-facing, standing"},
    {"name": "volt", "style": "pixel",
     "spec": "a battery mascot from the reference — dot eyes, blank deadpan, matching pixel proportions on the sheet.",
     "palette": "structure ink #111111. Accent ONLY on the designated accent part.",
     "pose": "front-facing friendly wave"},
    {"name": "sprout", "style": "riso",
     "spec": "a just-sprouted seed mascot from the reference — dot eyes, blank deadpan, matching the sheet.",
     "palette": "structure ink #111111. Accent ONLY on the designated accent part.",
     "pose": "front-facing friendly wave"},
    {"name": "cone", "style": "riso",
     "spec": "a traffic-cone mascot from the reference — dot eyes, blank deadpan, matching the sheet.",
     "palette": "structure ink #111111. Accent ONLY on the designated accent part.",
     "pose": "front-facing friendly wave"},
]


def fetch_ref(name, dest):
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    url = f"{CHAR_BASE}/{name}/reference.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as resp:
        dest.write_bytes(resp.read())
    return dest


def build_prompt(ch):
    style = ch.get("style") or "riso"
    style_line = STYLE_LINES.get(style, STYLE_LINES["riso"])
    return textwrap.dedent(f"""\
        A 1:1 square character cutout — transparent compositing asset, NOT an editorial scene.

        Composition (cutout — contact continuity): ONLY the mascot, {ch["pose"]}.
        Large and centered, ~70% of the frame height, full body visible with feet uncropped and
        transparent margin below. NO environment, no props, no text anywhere.

        POSE: {ch["pose"]}, proportions matching the reference sheet.

        CHARACTER (locked, keep exactly on the reference model): {ch["spec"]}

        LINE LANGUAGE: ONE bold, even-weight, softly-rounded outline (clean vinyl-sticker line).

        {SILHOUETTE}

        {style_line}

        PALETTE: {ch["palette"]} Do not use chroma screen colors anywhere on the character or props.
        """)


def chroma_for(ch):
    if ch.get("cutout_chroma") in ("green", "magenta"):
        return ch["cutout_chroma"]
    spec = (ch.get("spec") or "").lower()
    if ch["name"] == "wick" or "wrought-iron" in spec or "forged-metal" in spec:
        return "green"
    return "magenta"


def edge_stats(path):
    data = Path(path).read_bytes()
    a = illo.analyze_cutout_alpha(data)
    parsed = illo._parse_png_rgb_or_rgba(data)
    if not parsed:
        return {**a, "magenta_edge_px": None, "green_edge_px": None}
    w, h, rgba = parsed
    mag_edge = green_edge = 0
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            r, g, b, al = rgba[i:i + 4]
            if al == 0:
                continue
            near = any(
                0 <= x + dx < w and 0 <= y + dy < h and rgba[((y + dy) * w + (x + dx)) * 4 + 3] == 0
                for dy in range(-2, 3) for dx in range(-2, 3)
            )
            if not near:
                continue
            if r > 120 and b > 80 and r > g + 10:
                mag_edge += 1
            if g > max(r, b) + 15 and g > 40:
                green_edge += 1
    return {**a, "magenta_edge_px": mag_edge, "green_edge_px": green_edge}


def run_one(ch, run_dir):
    name = ch["name"]
    ref = Path(ch.get("ref_local") or run_dir / "refs" / f"{name}.png")
    if not ch.get("ref_local"):
        fetch_ref(name, ref)
    prompt_file = run_dir / "prompts" / f"{name}.txt"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(ch)
    prompt_file.write_text(prompt)
    chroma = chroma_for(ch)
    out = run_dir / name
    cmd = [
        sys.executable, str(ILLO), "generate",
        "--backend", "codex",
        "--cutout", "--aspect", "1:1",
        "--chroma", chroma,
        "--ref", str(ref),
        "--prompt-file", str(prompt_file),
        "--label", f"{name}-registration-codex",
        "--out", str(out),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    rec = {"character": name, "style": ch.get("style"), "chroma": chroma, "ref": str(ref),
           "prompt_file": str(prompt_file)}
    if proc.returncode != 0:
        rec["error"] = (proc.stderr or proc.stdout).strip()
        return rec
    rec.update(json.loads(proc.stdout.strip().splitlines()[-1]))
    p = Path(rec["path"])
    if p.exists():
        rec["edge"] = edge_stats(p)
        rec["data_uri"] = "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
    return rec


def build_html(run_dir, results, sanity):
    css = """
    body{font:15px/1.55 -apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:28px 32px 56px;
         background:#0b0d10;color:#e8eaed}
    h1{font-size:1.45rem;margin:0 0 6px} .sub{color:#9aa0a6;margin:0 0 24px;max-width:960px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px}
    .card{background:#141820;border:1px solid #2a3140;border-radius:12px;padding:14px}
    .card h3{margin:0 0 4px;font-size:.95rem}
    .meta{color:#9aa0a6;font-size:12px;margin:0 0 10px;line-height:1.45}
    .checker{background:repeating-conic-gradient(#808080 0% 25%,#c0c0c0 0% 50%) 50%/14px 14px;
             border-radius:8px;padding:6px;display:inline-block}
    .on-blue{background:#2563eb;border-radius:8px;padding:6px;display:inline-block;margin-top:6px}
    img{max-width:100%;height:auto;display:block}
    .good{color:#81c995}.warn{color:#fdd663}.bad{color:#f28b82}
    .pill{display:inline-block;font-size:11px;padding:2px 7px;border-radius:999px;
          background:#1f2937;margin:2px 4px 2px 0}
    .sanity{border:1px solid #3d5a80;border-radius:12px;padding:16px;margin-bottom:28px;background:#101820}
    """
    parts = [f"<!DOCTYPE html><html><head><meta charset=utf-8><title>Cutout registration gallery</title>",
             f"<style>{css}</style></head><body>",
             "<h1>Registration-locked cutouts — Codex</h1>",
             "<p class=sub>Silhouette block forbids ink-layer offset / misregistration on all cutouts. "
             "Chroma auto per character. Compare Blot sanity vs old offset prompt.</p>"]

    if sanity:
        e = sanity.get("edge") or {}
        parts.append('<div class=sanity><h2>Blot sanity (registration-locked)</h2>')
        parts.append(f'<p class=meta>Old offset prompt: ~17,800 magenta edge px. '
                     f'New: {e.get("magenta_edge_px", "?")} magenta edge px · '
                     f'method {html.escape(str(sanity.get("cutout_method")))} · '
                     f'alpha {html.escape(str(sanity.get("cutout_alpha")))}</p>')
        if sanity.get("data_uri"):
            u = sanity["data_uri"]
            parts.append(f'<div class=checker><img src="{u}" alt="blot sanity"></div>')
            parts.append(f'<div class=on-blue><img src="{u}" alt="blot on blue"></div>')
        parts.append("</div>")

    parts.append('<div class=grid>')
    for rec in results:
        name = rec.get("character", "?")
        edge = rec.get("edge") or {}
        mag = edge.get("magenta_edge_px")
        cls = "good" if rec.get("cutout_alpha") and (mag is None or mag < 500) else (
            "warn" if rec.get("cutout_alpha") else "bad")
        parts.append(f'<div class=card><h3>{html.escape(name)} <span class="{cls}">'
                     f'{html.escape(verdict(rec))}</span></h3>')
        parts.append(f'<p class=meta>{html.escape(rec.get("style") or "")} · chroma {html.escape(rec.get("chroma") or "")}<br>'
                     f'method {html.escape(str(rec.get("cutout_method")))} · '
                     f'magenta edge px {mag}<br>{html.escape(rec.get("cutout_note") or "")}</p>')
        if rec.get("error"):
            parts.append(f'<p class=bad>{html.escape(rec["error"][:400])}</p>')
        elif rec.get("data_uri"):
            u = rec["data_uri"]
            parts.append(f'<div class=checker><img loading=lazy src="{u}" alt="{html.escape(name)}"></div>')
            parts.append(f'<div class=on-blue><img loading=lazy src="{u}" alt="{html.escape(name)} blue"></div>')
        parts.append("</div>")
    parts.append("</div></body></html>")
    out = run_dir / "index.html"
    out.write_text("".join(parts))
    return out


def verdict(rec):
    if rec.get("error"):
        return "failed"
    if rec.get("cutout_alpha"):
        mag = (rec.get("edge") or {}).get("magenta_edge_px")
        if mag is not None and mag >= 500:
            return "alpha ok · heavy edge tint"
        return "compositing-ready"
    return "not ready"


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    sanity_path = Path("/tmp/illo/cutout-registration/blot-sanity-codex.png")
    sanity = {"path": str(sanity_path), "cutout_alpha": True, "cutout_method": "native"}
    if sanity_path.exists():
        sanity["edge"] = edge_stats(sanity_path)
        sanity["data_uri"] = "data:image/png;base64," + base64.b64encode(sanity_path.read_bytes()).decode()

    # Clear stale manifest for clean rerun
    manifest = RUN / "manifest.jsonl"
    if manifest.exists():
        manifest.unlink()

    results = []
    for ch in CHARACTERS:
        if ch["name"] == "blot" and sanity_path.exists() and not os.environ.get("RERUN_ALL"):
            rec = {"character": "blot", "style": "riso", "chroma": "magenta",
                   "path": str(sanity_path), "cutout_alpha": True, "cutout_method": "native",
                   "cutout_note": "sanity run (reused)", "edge": sanity.get("edge"),
                   "data_uri": sanity.get("data_uri")}
            results.append(rec)
            print(f"blot: reused sanity", flush=True)
            continue
        print(f"generating {ch['name']}...", flush=True)
        results.append(run_one(ch, RUN))

    (RUN / "results.json").write_text(json.dumps(results, indent=2))
    html_path = build_html(RUN, results, sanity)
    print(f"wrote {html_path}")
    print(f"ready: {sum(1 for r in results if r.get('cutout_alpha'))}/{len(results)}")


if __name__ == "__main__":
    main()
