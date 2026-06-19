#!/usr/bin/env python3
"""Probe OpenRouter cutout/transparency API shapes. Stdlib + illo config key."""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "skills/illo/scripts"))
import illo  # noqa: E402

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
REF = REPO / "skills/illo/assets/character-reference.webp"
MODEL = "openai/gpt-5.4-image-2"
PROMPT = (
    "Character cutout only: the plump ink-droplet mascot from the reference, waving one arm. "
    "No text, no scene, no background objects. 1:1 square."
)


def call(key, body):
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:800]}"


def analyze(data):
    if not data:
        return {"error": "no bytes"}
    ext = illo.sniff_ext(data)
    w, h = illo.image_size(data)
    out = {"ext": ext, "width": w, "height": h, "bytes": len(data)}
    if ext != ".png":
        out["verdict"] = "not png"
        return out
    parsed = illo._parse_png_rgb_or_rgba(data)
    if not parsed:
        out["verdict"] = "unparsed png"
        return out
    _, _, rgba = parsed
    trans = sum(1 for i in range(3, len(rgba), 4) if rgba[i] == 0)
    corners = [rgba[i] for i in (3, (w - 1) * 4 + 3, (w * (h - 1)) * 4 + 3, (w * h - 1) * 4 + 3)]
    out.update({"transparent": trans, "corners_alpha": corners,
                "has_alpha": trans > 0,
                "verdict": "clean alpha" if trans > 1000 and all(a == 0 for a in corners) else "opaque or partial"})
    return out


def extract_img(payload):
    msg = (payload.get("choices") or [{}])[0].get("message") or {}
    return illo.extract_image(msg)


def main():
    key = illo.resolve_key(illo.load_config())
    content = [{"type": "text", "text": PROMPT},
               {"type": "image_url", "image_url": {"url": illo.data_url(REF)}}]
    tests = [
        ("modalities_only", {
            "model": MODEL, "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"],
        }),
        ("modalities+image_config", {
            "model": MODEL, "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": "1:1"},
        }),
        ("modalities+transparent_prompt", {
            "model": MODEL,
            "messages": [{"role": "user", "content": content + [
                {"type": "text", "text": "\nOUTPUT: PNG with real transparent alpha channel; alpha=0 outside character."}
            ]}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": "1:1"},
        }),
        ("image_gen_tool", {
            "model": MODEL,
            "messages": [{"role": "user", "content": PROMPT}],
            "tools": [{"type": "openrouter:image_generation",
                       "parameters": {"model": MODEL, "background": "transparent",
                                      "output_format": "png", "aspect_ratio": "1:1"}}],
        }),
        ("image_gen_tool+ref", {
            "model": MODEL,
            "messages": [{"role": "user", "content": content}],
            "tools": [{"type": "openrouter:image_generation",
                       "parameters": {"model": MODEL, "background": "transparent",
                                      "output_format": "png", "aspect_ratio": "1:1"}}],
        }),
    ]
    results = []
    for name, body in tests:
        print(f"=== {name} ===", flush=True)
        payload, err = call(key, body)
        if err:
            print(err)
            results.append({"name": name, "error": err})
            continue
        img = extract_img(payload)
        if not img:
            keys = list(((payload.get("choices") or [{}])[0].get("message") or {}).keys())
            results.append({"name": name, "error": f"no image in message keys={keys}"})
            print("no image", keys)
            continue
        info = analyze(img)
        out = Path(f"/tmp/illo/probe-{name}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        if info.get("ext") == ".png":
            out.write_bytes(img)
        results.append({"name": name, **info, "path": str(out)})
        print(json.dumps(info, indent=2))
    Path("/tmp/illo/openrouter-cutout-probe.json").write_text(json.dumps(results, indent=2))
    print("wrote /tmp/illo/openrouter-cutout-probe.json")


if __name__ == "__main__":
    main()
