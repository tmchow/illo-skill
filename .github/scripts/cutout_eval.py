#!/usr/bin/env python3
"""Evaluate illo v0.24.0 cutout workflow across backends/models/methods.

Runs generate with --cutout (and optional --image-config), records manifest
cutout_* fields, and writes a self-contained HTML gallery under the run dir.
Stdlib + illo.py only."""
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

PROMPT_BASE = textwrap.dedent("""\
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

PROMPT_NATIVE = PROMPT_BASE + textwrap.dedent("""\

    OUTPUT FORMAT (critical): deliver a PNG with a REAL transparent alpha channel — pixels outside
    the character must have alpha=0. No solid white, gray, black, green, or checkerboard background.
    No baked-in transparency pattern — true alpha only. The file must composite cleanly on any color.
    """)

PROMPT_CHROMA = PROMPT_BASE + textwrap.dedent("""\

    BACKGROUND: solid flat chroma magenta exactly #FF00FF everywhere outside the character — perfectly
    uniform, no paper grain, no gradient, no cast shadow on the magenta. Do not bleed background color
    onto the mascot outline. (The engine will chroma-key this to transparency.)
    """)

CASES = [
    {
        "id": "codex-agent-workflow",
        "title": "Codex · agent workflow",
        "subtitle": "Native prompt (no chroma BACKGROUND) + --cutout",
        "backend": "codex",
        "model": None,
        "prompt": "native",
        "image_config": None,
        "expect_alpha": True,
    },
    {
        "id": "codex-chroma-fallback",
        "title": "Codex · chroma fallback",
        "subtitle": "Chroma #FF00FF prompt + --cutout",
        "backend": "codex",
        "model": None,
        "prompt": "chroma",
        "image_config": None,
        "expect_alpha": True,
    },
    {
        "id": "or-gpt-agent-workflow",
        "title": "OpenRouter · GPT Image 2 · agent workflow",
        "subtitle": "Chroma prompt + --cutout + --image-config aspect_ratio",
        "backend": "openrouter",
        "model": "openai/gpt-5.4-image-2",
        "prompt": "chroma",
        "image_config": '{"aspect_ratio":"1:1"}',
        "expect_alpha": True,
    },
    {
        "id": "or-gpt-native-cutout",
        "title": "OpenRouter · GPT Image 2 · native ask",
        "subtitle": "Transparent prompt + --cutout + --image-config (no chroma line)",
        "backend": "openrouter",
        "model": "openai/gpt-5.4-image-2",
        "prompt": "native",
        "image_config": '{"aspect_ratio":"1:1"}',
        "expect_alpha": False,
    },
    {
        "id": "or-grok-agent-workflow",
        "title": "OpenRouter · Grok Imagine · agent workflow",
        "subtitle": "Chroma prompt + --cutout + --image-config (JPEG → opaque fallback)",
        "backend": "openrouter",
        "model": "x-ai/grok-imagine-image-quality",
        "prompt": "chroma",
        "image_config": '{"aspect_ratio":"1:1"}',
        "expect_alpha": False,
    },
    {
        "id": "or-gemini-agent-workflow",
        "title": "OpenRouter · Gemini Flash · agent workflow",
        "subtitle": "Chroma prompt + --cutout + --image-config (JPEG → opaque fallback)",
        "backend": "openrouter",
        "model": "google/gemini-3.1-flash-image-preview",
        "prompt": "chroma",
        "image_config": '{"aspect_ratio":"1:1"}',
        "expect_alpha": False,
    },
]


def analyze_image(path):
    data = Path(path).read_bytes()
    return illo.analyze_cutout_alpha(data)


def run_case(run_dir, case, prompts):
    out = run_dir / f"{case['id']}.png"
    prompt_key = case["prompt"]
    prompt_file = prompts[prompt_key]
    cmd = [
        sys.executable, str(ILLO), "generate",
        "--prompt-file", str(prompt_file),
        "--ref", str(REF),
        "--aspect", "1:1",
        "--backend", case["backend"],
        "--label", case["id"],
        "--cutout",
        "--out", str(out),
    ]
    if case.get("model"):
        cmd.extend(["--model", case["model"]])
    if case.get("image_config"):
        cmd.extend(["--image-config", case["image_config"]])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    rec = {
        "case": case,
        "command": " ".join(cmd),
        "prompt_file": str(prompt_file),
        "prompt_text": prompt_file.read_text(),
    }
    if proc.returncode != 0:
        rec["error"] = (proc.stderr or proc.stdout).strip()
        return rec
    line = proc.stdout.strip().splitlines()[-1]
    manifest = json.loads(line)
    rec.update(manifest)
    if manifest.get("path"):
        rec["analysis"] = analyze_image(manifest["path"])
    return rec


def verdict_class(rec):
    if rec.get("error"):
        return "bad"
    if rec.get("cutout_alpha"):
        return "good"
    if rec.get("cutout_method") == "opaque_fallback":
        return "warn"
    return "bad"


def verdict_text(rec):
    if rec.get("error"):
        return "generate failed"
    if rec.get("cutout_alpha"):
        method = rec.get("cutout_method") or "?"
        return f"compositing-ready ({method})"
    if rec.get("cutout_method") == "opaque_fallback":
        return "not compositing-ready (opaque fallback)"
    return "not compositing-ready"


def build_html(run_dir, results, title):
    run_dir = run_dir.resolve()
    css = """
    body{font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         margin:0;padding:28px 32px 56px;background:#0b0d10;color:#e8eaed}
    h1{font-size:1.45rem;font-weight:650;margin:0 0 6px;letter-spacing:-.02em}
    h2{font-size:1.05rem;font-weight:600;margin:0 0 10px;color:#c0c4c9}
    .sub{color:#9aa0a6;margin:0 0 28px;max-width:980px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}
    .card{background:#141820;border:1px solid #2a3140;border-radius:12px;padding:16px 16px 18px}
    .card h3{font-size:.98rem;margin:0 0 4px;font-weight:600}
    .card .method{color:#9aa0a6;font-size:13px;margin:0 0 12px;line-height:1.4}
    .checker{background:repeating-conic-gradient(#808080 0% 25%, #c0c0c0 0% 50%) 50% / 16px 16px;
             border-radius:8px;padding:8px;display:inline-block}
    .on-blue{background:#2563eb;border-radius:8px;padding:8px;display:inline-block;margin-top:8px}
    .on-blue img,.checker img{display:block;max-width:100%;max-height:260px;height:auto;width:auto}
    .verdict{font-weight:600;margin:10px 0 6px;font-size:14px}
    .good{color:#81c995}.warn{color:#fdd663}.bad{color:#f28b82}
    .meta{font:12px/1.5 ui-monospace,Menlo,monospace;color:#9aa0a6;margin:6px 0 0}
    .summary{background:#141820;border:1px solid #2a3140;border-radius:12px;padding:18px 20px;max-width:980px;margin-bottom:28px}
    .summary ul{margin:8px 0 0;padding-left:1.2rem;color:#c0c4c9}
    .summary li{margin:6px 0}
    details{margin-top:12px}
    summary{cursor:pointer;color:#c0c4c9;font-size:13px}
    pre.prompt,pre.cmd{white-space:pre-wrap;word-break:break-word;font:11px/1.45 ui-monospace,Menlo,monospace;
         background:#0b0d10;border:1px solid #2a3140;border-radius:8px;padding:10px 12px;color:#c0c4c9;
         margin:8px 0 0;max-height:220px;overflow:auto}
    pre.fail{color:#f28b82}
    .legend{display:flex;gap:16px;flex-wrap:wrap;margin:0 0 20px;font-size:13px;color:#9aa0a6}
    .swatch{width:14px;height:14px;border-radius:3px;display:inline-block;vertical-align:middle;margin-right:6px}
    .pill{display:inline-block;font:11px/1.4 ui-monospace,Menlo,monospace;padding:2px 7px;border-radius:999px;
          background:#1e2430;color:#c0c4c9;margin-right:6px}
    """
    ready = sum(1 for r in results if r.get("cutout_alpha"))
    fallback = sum(1 for r in results if r.get("cutout_method") == "opaque_fallback")
    failed = sum(1 for r in results if r.get("error"))
    summary_items = []
    for rec in results:
        case = rec["case"]
        vt = verdict_text(rec)
        summary_items.append(f"{case['title']}: {vt}")

    parts = [
        "<!doctype html><html lang=en><head><meta charset=utf-8>",
        '<meta name=viewport content="width=device-width,initial-scale=1">',
        f"<title>{html.escape(title)}</title><style>{css}</style></head><body>",
        f"<h1>{html.escape(title)}</h1>",
        "<p class=sub>illo v0.24.0 cutout eval — every case uses <code>--cutout</code>. "
        "OpenRouter cases also pass <code>--image-config</code> (aspect_ratio). "
        "Checkerboard + blue reveal real alpha vs baked backgrounds. "
        "Manifest fields <code>cutout_alpha</code>, <code>cutout_method</code>, "
        "<code>cutout_note</code> drive agent disclosure.</p>",
        '<div class=legend><span><span class=swatch style="background:repeating-conic-gradient(#808080 0% 25%,#c0c0c0 0% 50%) 50%/8px 8px"></span>checker</span>'
        '<span><span class=swatch style="background:#2563eb"></span>blue halo test</span></div>',
        '<div class=summary><h2>Results</h2>',
        f'<p class=meta>{ready} compositing-ready · {fallback} opaque fallback · {failed} hard failures</p><ul>',
    ]
    for item in summary_items:
        parts.append(f"<li>{html.escape(item)}</li>")
    parts.append("</ul></div><div class=grid>")

    for rec in results:
        case = rec["case"]
        vc = verdict_class(rec)
        vt = verdict_text(rec)
        parts.append('<article class=card>')
        parts.append(f"<h3>{html.escape(case['title'])}</h3>")
        parts.append(f"<p class=method>{html.escape(case['subtitle'])}</p>")
        if rec.get("error"):
            parts.append(f'<p class="verdict bad">{html.escape(vt)}</p>')
            parts.append(f'<pre class="fail">{html.escape(rec["error"][:1200])}</pre>')
        else:
            rel = Path(rec["path"]).resolve().relative_to(run_dir)
            parts.append('<div class=checker><img loading=lazy src="{}" alt=""></div>'.format(html.escape(str(rel))))
            parts.append('<div class=on-blue><img loading=lazy src="{}" alt=""></div>'.format(html.escape(str(rel))))
            parts.append(f'<p class="verdict {vc}">{html.escape(vt)}</p>')
            a = rec.get("analysis") or {}
            parts.append(
                f'<div class=meta>'
                f'<span class=pill>backend={html.escape(rec.get("backend","?"))}</span>'
                f'<span class=pill>cutout_alpha={html.escape(str(rec.get("cutout_alpha")))}</span>'
                f'<span class=pill>method={html.escape(str(rec.get("cutout_method")))}</span><br>'
                f"model: {html.escape(str(rec.get('model') or 'gpt-image-2 (codex)'))}<br>"
                f"format: {html.escape(a.get('ext','?'))} · {a.get('width','?')}×{a.get('height','?')} · "
                f"transparent px: {a.get('transparent',0):,} · fringe g/m: "
                f"{a.get('green_fringe',0)}/{a.get('magenta_fringe',0)}<br>"
                f"note: {html.escape(str(rec.get('cutout_note') or '—'))}"
                f"</div>"
            )
        parts.append("<details><summary>Prompt</summary>")
        parts.append(f'<pre class=prompt>{html.escape(rec.get("prompt_text",""))}</pre></details>')
        parts.append("<details><summary>Command</summary>")
        parts.append(f'<pre class=cmd>{html.escape(rec.get("command",""))}</pre></details>')
        parts.append("</article>")

    parts.append("</div></body></html>")
    out = run_dir / "index.html"
    out.write_text("".join(parts))
    return out


def main():
    ap = argparse.ArgumentParser(description="Cutout v0.24.0 eval gallery")
    ap.add_argument("--run", type=Path, help="existing run dir")
    ap.add_argument("--html-only", action="store_true")
    ap.add_argument("--skip-codex", action="store_true")
    ap.add_argument("--skip-openrouter", action="store_true")
    ap.add_argument("--case", action="append", help="run only case id(s)")
    args = ap.parse_args()

    if args.run:
        run_dir = args.run.resolve()
    else:
        out = subprocess.run([sys.executable, str(ILLO), "newrun"], capture_output=True, text=True, check=True)
        run_dir = Path(out.stdout.strip()).resolve()

    cases = CASES
    if args.case:
        wanted = set(args.case)
        cases = [c for c in CASES if c["id"] in wanted]

    if args.skip_codex:
        cases = [c for c in cases if c["backend"] != "codex"]
    if args.skip_openrouter:
        cases = [c for c in cases if c["backend"] != "openrouter"]

    prompts = {
        "native": run_dir / "prompt-native.txt",
        "chroma": run_dir / "prompt-chroma.txt",
    }
    prompts["native"].write_text(PROMPT_NATIVE)
    prompts["chroma"].write_text(PROMPT_CHROMA)

    if args.html_only:
        results = json.loads((run_dir / "results.json").read_text())
        html_path = build_html(run_dir, results, "Cutout eval — illo v0.24.0")
        print(json.dumps({"run_dir": str(run_dir), "html": str(html_path.resolve())}))
        return

    results = []
    for case in cases:
        print(f"Running {case['id']} …", flush=True)
        rec = run_case(run_dir, case, prompts)
        results.append(rec)
        status = verdict_text(rec)
        print(f"  → {status}", flush=True)
        if case["backend"] == "openrouter":
            time.sleep(1)

    (run_dir / "results.json").write_text(json.dumps(results, indent=2))
    html_path = build_html(run_dir, results, "Cutout eval — illo v0.24.2")
    dest = REPO / "_assets/illo/cutout-eval-v0240"
    dest.mkdir(parents=True, exist_ok=True)
    # Copy gallery artifacts for docs hosting
    import shutil
    for p in run_dir.iterdir():
        if p.suffix in {".png", ".jpg", ".html", ".json", ".txt"}:
            shutil.copy2(p, dest / p.name)
    print(json.dumps({
        "run_dir": str(run_dir),
        "html": str(html_path.resolve()),
        "assets_copy": str(dest),
        "ready": sum(1 for r in results if r.get("cutout_alpha")),
        "total": len(results),
    }))


if __name__ == "__main__":
    main()
