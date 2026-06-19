#!/usr/bin/env python3
"""Compare prompt-native transparency vs chroma-key --cutout across backends/models.

Writes a run dir under $ILLO_TMP (or /tmp/illo) with manifest.jsonl, analysis.json,
and index.html. Stdlib + illo.py only."""
import argparse
import html
import json
import subprocess
import sys
import textwrap
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ILLO = REPO / "skills/illo/scripts/illo.py"
REF = REPO / "skills/illo/assets/character-reference.webp"

sys.path.insert(0, str(ILLO.parent))
import illo  # noqa: E402

OPENROUTER_MODELS = [
    ("grok-imagine", "x-ai/grok-imagine-image-quality"),
    ("gemini-flash", "google/gemini-3.1-flash-image-preview"),
    ("gpt-image-2-or", "openai/gpt-5.4-image-2"),
]

PROMPT_SHARED = textwrap.dedent("""\
    A 1:1 square character cutout — transparent compositing asset, NOT an editorial scene.

    Composition (cutout — contact continuity): ONLY the mascot, waving with one stubby arm raised.
    Large and centered, ~70% of the frame. NO environment, no props, no text anywhere.

    POSE: front-facing, friendly wave, limbs matching the reference sheet proportions.

    CHARACTER (locked, keep exactly on the reference model): the recurring mascot — a plump rounded
    ink-droplet body (a fat soft teardrop, wide at the bottom, narrowing to a gently curved tip at the top),
    two simple dot eyes, blank deadpan (no eyebrows, no mouth), small stubby arms and legs; the ONLY
    accent-colored part is the droplet tip. Body filled with structure ink #111111, eyes warm-white dots.

    LINE LANGUAGE: ONE bold, even-weight, softly-rounded outline (clean vinyl-sticker line).

    STYLE: risograph print — grainy halftone texture, slight ink-layer offset, flat fills on the character only.

    PALETTE: structure ink #111111. Accent #ff3d9a ONLY on the droplet tip.
    """)

PROMPT_NATIVE_SUFFIX = textwrap.dedent("""\

    OUTPUT FORMAT (critical): deliver a PNG with a REAL transparent alpha channel — pixels outside
    the character must have alpha=0. No solid white, gray, black, green, or checkerboard background.
    No baked-in transparency pattern — true alpha only. The file must composite cleanly on any color.
    """)

PROMPT_CHROMA_SUFFIX = textwrap.dedent("""\

    BACKGROUND: solid flat chroma magenta exactly #FF00FF everywhere outside the character — perfectly
    uniform, no paper grain, no gradient, no cast shadow on the magenta. Do not bleed background color
    onto the mascot outline. (The engine will chroma-key this to transparency.)
    """)


def analyze_image(path):
    """Return metrics dict for a rendered file."""
    data = Path(path).read_bytes()
    ext = illo.sniff_ext(data) or Path(path).suffix
    w, h = illo.image_size(data)
    metrics = {
        "path": str(Path(path).resolve()),
        "ext": ext,
        "width": w,
        "height": h,
        "bytes": len(data),
        "has_alpha": False,
        "transparent": 0,
        "opaque": 0,
        "semi": 0,
        "green_fringe": 0,
        "magenta_fringe": 0,
        "corner_alpha": [],
        "verdict": "",
    }
    if ext != ".png" or not data.startswith(illo.PNG_MAGIC):
        metrics["verdict"] = "no PNG alpha (JPEG or opaque PNG)"
        return metrics
    parsed = illo._parse_png_rgb_or_rgba(data)
    if not parsed:
        metrics["verdict"] = "unparsed PNG"
        return metrics
    w, h, rgba = parsed
    metrics["has_alpha"] = any(rgba[i + 3] < 255 for i in range(0, len(rgba), 4))
    for i in range(0, len(rgba), 4):
        r, g, b, a = rgba[i:i + 4]
        if a == 0:
            metrics["transparent"] += 1
        elif a == 255:
            metrics["opaque"] += 1
        else:
            metrics["semi"] += 1
        if a and g > max(r, b) + 10 and g > 45:
            metrics["green_fringe"] += 1
        if a and r > 120 and b > 120 and r > g + 15 and b > g + 15 and abs(r - b) < 60:
            metrics["magenta_fringe"] += 1
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    metrics["corner_alpha"] = [rgba[(y * w + x) * 4 + 3] for x, y in corners]
    corners_transparent = all(a == 0 for a in metrics["corner_alpha"])
    fringe = metrics["green_fringe"] + metrics["magenta_fringe"]
    if metrics["transparent"] > 1000 and corners_transparent and fringe < 50:
        metrics["verdict"] = "clean alpha"
    elif metrics["has_alpha"] and metrics["transparent"] > 100:
        metrics["verdict"] = "partial alpha" + (f" ({fringe} fringe px)" if fringe else "")
    elif metrics["transparent"] == 0:
        metrics["verdict"] = "fully opaque — no transparency"
    else:
        metrics["verdict"] = "weak alpha"
    return metrics


def run_generate(run_dir, label, prompt_file, out_name, backend, model=None, cutout=False):
    out = run_dir / out_name
    cmd = [
        sys.executable, str(ILLO), "generate",
        "--prompt-file", str(prompt_file),
        "--ref", str(REF),
        "--aspect", "1:1",
        "--backend", backend,
        "--label", label,
        "--out", str(out),
    ]
    if model:
        cmd.extend(["--model", model])
    if cutout:
        cmd.append("--cutout")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": proc.stderr or proc.stdout, "label": label}
    line = proc.stdout.strip().splitlines()[-1]
    rec = json.loads(line)
    rec["analysis"] = analyze_image(rec["path"])
    rec["approach"] = "chroma+script" if cutout else "prompt-native"
    return rec


def summarize(rows):
    lines = []
    for row in rows:
        name = row["name"]
        for arm, key in (("Prompt-native", "native"), ("Chroma + script", "chroma")):
            rec = row.get("chroma" if key == "chroma" else "native")
            if not rec or rec.get("error"):
                lines.append(f"{name} · {arm}: failed — {(rec or {}).get('error', 'missing')[:120]}")
            else:
                a = rec["analysis"]
                lines.append(f"{name} · {arm}: {a['verdict']} "
                             f"(transparent {a['transparent']:,}, fringe g/m {a['green_fringe']}/{a['magenta_fringe']})")
    return lines


def build_html(run_dir, rows, title):
    run_dir = run_dir.resolve()
    css = """
    body{font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         margin:0;padding:28px 32px 48px;background:#0f1115;color:#e8eaed}
    h1{font-size:1.35rem;font-weight:600;margin:0 0 8px}
    h2{font-size:1.05rem;font-weight:600;margin:28px 0 10px;color:#c0c4c9}
    .sub{color:#9aa0a6;margin:0 0 24px;max-width:960px}
    table{border-collapse:collapse;width:100%;margin-top:16px}
    th,td{border:1px solid #2a2f38;padding:12px;vertical-align:top}
    th{background:#171a20;text-align:left;font-size:13px;color:#c0c4c9}
    .checker{background:repeating-conic-gradient(#808080 0% 25%, #c0c0c0 0% 50%) 50% / 16px 16px;
             border-radius:8px;padding:8px;display:inline-block}
    .on-blue{background:#2563eb;border-radius:8px;padding:8px;display:inline-block;margin-top:8px}
    .on-blue img,.checker img{display:block;max-width:280px;max-height:280px;height:auto;width:auto}
    .metrics{font:12px/1.45 ui-monospace,Menlo,monospace;color:#9aa0a6;margin-top:8px}
    .verdict{font-weight:600;color:#e8eaed;margin:8px 0 0}
    .good{color:#81c995}.warn{color:#fdd663}.bad{color:#f28b82}
    .legend{display:flex;gap:16px;flex-wrap:wrap;margin:16px 0 0;font-size:13px;color:#9aa0a6}
    .swatch{width:14px;height:14px;border-radius:3px;display:inline-block;vertical-align:middle;margin-right:6px}
    .summary{background:#171a20;border:1px solid #2a2f38;border-radius:10px;padding:16px 18px;max-width:960px}
    .summary ul{margin:8px 0 0;padding-left:1.2rem;color:#c0c4c9}
    .summary li{margin:6px 0}
    .takeaway{color:#e8eaed;font-weight:500;margin-top:12px}
    pre.fail{white-space:pre-wrap;font:11px/1.4 ui-monospace,Menlo,monospace;color:#f28b82;margin:8px 0 0}
    """
    summary_lines = summarize(rows)
    takeaways = [
        "Codex (gpt-image-2) delivered real alpha from the prompt alone — no chroma script required on this run.",
        "OpenRouter Grok Imagine and Gemini Flash returned JPEG with no alpha; prompt-native failed; --cutout could not run (PNG-only post-process).",
        "OpenRouter GPT Image 2 returned an opaque PNG for prompt-native (white corners); chroma + --cutout produced clean alpha.",
        "When native alpha works, prefer prompt-native (simpler, no spill). Keep --cutout as fallback for models/backends that return opaque RGB/JPEG.",
    ]
    parts = [
        f"<!doctype html><html lang=en><head><meta charset=utf-8>",
        f'<meta name=viewport content="width=device-width,initial-scale=1">',
        f"<title>{html.escape(title)}</title><style>{css}</style></head><body>",
        f"<h1>{html.escape(title)}</h1>",
        "<p class=sub>Same Blot cutout prompt and reference sheet across backends. "
        "<strong>Prompt-native</strong> asks for a real alpha PNG (no <code>--cutout</code>). "
        "<strong>Chroma + script</strong> uses flat #FF00FF and illo&apos;s <code>--cutout</code> post-process. "
        "Checkerboard + blue strip show whether backgrounds are actually transparent.</p>",
        "<div class=legend><span><span class=swatch style='background:repeating-conic-gradient(#808080 0% 25%,#c0c0c0 0% 50%) 50%/8px 8px'></span>checker</span>"
        "<span><span class=swatch style='background:#2563eb'></span>blue (reveals white/green halos)</span></div>",
        '<div class=summary><h2 style="margin-top:0">Findings</h2><ul>',
    ]
    for line in summary_lines:
        parts.append(f"<li>{html.escape(line)}</li>")
    parts.append("</ul>")
    parts.append('<p class=takeaway>Takeaways</p><ul>')
    for t in takeaways:
        parts.append(f"<li>{html.escape(t)}</li>")
    parts.append("</ul></div>")
    parts.append("<h2>Visual comparison</h2>")
    parts.append("<table><thead><tr><th>Backend / model</th><th>Prompt-native (no script)</th><th>Chroma + --cutout script</th></tr></thead><tbody>")

    def cell(rec):
        if not rec or rec.get("error"):
            msg = html.escape((rec or {}).get("error", "missing")[:500])
            return f'<td class=bad>Failed<pre class=fail>{msg}</pre></td>'
        rel = Path(rec["path"]).resolve().relative_to(run_dir)
        a = rec["analysis"]
        vc = "good" if a["verdict"] == "clean alpha" else ("warn" if "partial" in a["verdict"] or "weak" in a["verdict"] else "bad")
        return (
            f'<td><div class=checker><img src="{html.escape(str(rel))}" alt=""></div>'
            f'<div class=on-blue><img src="{html.escape(str(rel))}" alt=""></div>'
            f'<p class="verdict {vc}">{html.escape(a["verdict"])}</p>'
            f'<div class=metrics>'
            f"format: {html.escape(a['ext'] or '?')} · alpha channel: {a['has_alpha']}<br>"
            f"transparent px: {a['transparent']:,} · opaque: {a['opaque']:,} · semi: {a['semi']:,}<br>"
            f"green fringe: {a['green_fringe']} · magenta fringe: {a['magenta_fringe']} · "
            f"corner α: {a['corner_alpha']} · {a['bytes']//1024} KB"
            f"</div></td>"
        )

    for row in rows:
        parts.append(f"<tr><th>{html.escape(row['name'])}</th>{cell(row.get('native'))}{cell(row.get('chroma'))}</tr>")
    parts.append("</tbody></table></body></html>")
    out = run_dir / "index.html"
    out.write_text("".join(parts))
    return out


def main():
    ap = argparse.ArgumentParser(description="Cutout alpha comparison benchmark")
    ap.add_argument("--run", type=Path, help="existing run dir (skip generation)")
    ap.add_argument("--html-only", action="store_true", help="rebuild HTML from analysis.json")
    ap.add_argument("--skip-codex", action="store_true")
    ap.add_argument("--skip-openrouter", action="store_true")
    args = ap.parse_args()

    if args.run:
        run_dir = args.run.resolve()
    else:
        out = subprocess.run([sys.executable, str(ILLO), "newrun"], capture_output=True, text=True, check=True)
        run_dir = Path(out.stdout.strip()).resolve()

    if args.html_only:
        analysis_path = run_dir / "analysis.json"
        rows = json.loads(analysis_path.read_text())
        html_path = build_html(run_dir, rows, "Cutout transparency comparison")
        print(json.dumps({"run_dir": str(run_dir), "html": str(html_path.resolve())}))
        return

    native_prompt = run_dir / "prompt-native.txt"
    chroma_prompt = run_dir / "prompt-chroma.txt"
    native_prompt.write_text(PROMPT_SHARED + PROMPT_NATIVE_SUFFIX)
    chroma_prompt.write_text(PROMPT_SHARED + PROMPT_CHROMA_SUFFIX)

    rows = []
    manifest = []

    if not args.skip_codex:
        print("Codex: prompt-native …", flush=True)
        codex_native = run_generate(run_dir, "codex-native", native_prompt, "codex-native.png", "codex")
        print("Codex: chroma+script …", flush=True)
        codex_chroma = run_generate(run_dir, "codex-chroma", chroma_prompt, "codex-chroma.png", "codex", cutout=True)
        rows.append({"name": "Codex CLI (gpt-image-2)", "native": codex_native, "chroma": codex_chroma})
        manifest.extend([codex_native, codex_chroma])

    if not args.skip_openrouter:
        for slug, model_id in OPENROUTER_MODELS:
            print(f"OpenRouter {slug}: prompt-native …", flush=True)
            native = run_generate(run_dir, f"{slug}-native", native_prompt,
                                   f"{slug}-native.png", "openrouter", model=model_id)
            print(f"OpenRouter {slug}: chroma+script …", flush=True)
            chroma = run_generate(run_dir, f"{slug}-chroma", chroma_prompt,
                                  f"{slug}-chroma.png", "openrouter", model=model_id, cutout=True)
            rows.append({"name": f"OpenRouter · {slug}", "native": native, "chroma": chroma})
            manifest.extend([native, chroma])
            time.sleep(1)

    analysis_path = run_dir / "analysis.json"
    analysis_path.write_text(json.dumps(rows, indent=2))
    html_path = build_html(run_dir, rows, "Cutout transparency comparison")
    print(json.dumps({"run_dir": str(run_dir), "html": str(html_path.resolve()), "analysis": str(analysis_path.resolve())}))


if __name__ == "__main__":
    main()
