import contextlib
import importlib.util
import io
import struct
import tempfile
import types
import unittest
import zlib
from pathlib import Path
from typing import Any, cast


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "skills" / "illo" / "scripts" / "illo.py"
EVAL_PATH = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "cutout_eval.py"

MAGENTA = (255, 0, 255)
CREAM = (248, 234, 205)
PINK = (255, 61, 154)
GREEN = (0, 255, 0)
TRANSPARENT = (255, 0, 255, 0)


def load_illo_module():
    spec = importlib.util.spec_from_file_location("illo_script_under_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load illo script from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(Any, module)


def load_eval_module():
    spec = importlib.util.spec_from_file_location("cutout_eval_under_test", EVAL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load eval script from {EVAL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(Any, module)


def rgb_png(width, height, pixels):
    raw_rows = bytearray()
    for y in range(height):
        raw_rows.append(0)
        for x in range(width):
            raw_rows.extend(pixels[y * width + x])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw_rows), 9))
            + chunk(b"IEND", b""))


def rgba_png(width, height, pixels):
    raw_rows = bytearray()
    for y in range(height):
        raw_rows.append(0)
        for x in range(width):
            raw_rows.extend(pixels[y * width + x])
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw_rows), 9))
            + chunk(b"IEND", b""))


def synthetic_cutout_png(accent="interior"):
    width = height = 128
    cx = cy = width // 2
    body_radius = 38
    accent_radius = 10
    pixels = [MAGENTA] * (width * height)
    for y in range(height):
        for x in range(width):
            dist2 = (x - cx) ** 2 + (y - cy) ** 2
            idx = y * width + x
            if accent == "ring" and body_radius ** 2 < dist2 <= (body_radius + 2) ** 2:
                pixels[idx] = PINK
            elif dist2 <= body_radius ** 2:
                pixels[idx] = CREAM
            if accent == "interior" and dist2 <= accent_radius ** 2:
                pixels[idx] = PINK
            if accent == "tip" and (x - cx) ** 2 + (y - 26) ** 2 <= 8 ** 2:
                pixels[idx] = PINK
    return rgb_png(width, height, pixels)


def synthetic_soft_alpha_fringe_png(soft_layers=1):
    width = height = 128
    cx = cy = width // 2
    body_radius = 34
    pixels = [TRANSPARENT] * (width * height)
    for y in range(height):
        for x in range(width):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            idx = y * width + x
            if dist <= body_radius:
                pixels[idx] = CREAM + (255,)
            elif dist <= body_radius + 1:
                pixels[idx] = GREEN + (255,)
            elif dist <= body_radius + 1 + soft_layers:
                pixels[idx] = CREAM + (64,)
    return rgba_png(width, height, pixels)


def synthetic_accent_ring_behind_soft_matte_png(soft_layers=5):
    width = height = 128
    cx = cy = width // 2
    body_radius = 34
    pixels = [TRANSPARENT] * (width * height)
    for y in range(height):
        for x in range(width):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            idx = y * width + x
            if dist <= body_radius:
                pixels[idx] = CREAM + (255,)
            elif dist <= body_radius + 1:
                pixels[idx] = PINK + (255,)
            elif dist <= body_radius + 1 + soft_layers:
                pixels[idx] = CREAM + (64,)
    return rgba_png(width, height, pixels)


def synthetic_interior_soft_patch_png():
    width = height = 128
    cx = cy = width // 2
    body_radius = 40
    pixels = [TRANSPARENT] * (width * height)
    for y in range(height):
        for x in range(width):
            if (x - cx) ** 2 + (y - cy) ** 2 <= body_radius ** 2:
                pixels[y * width + x] = CREAM + (255,)
    pixels[cy * width + cx] = PINK + (64,)
    pixels[cy * width + cx + 1] = CREAM + (64,)
    return rgba_png(width, height, pixels)


def rgba_at(parsed, x, y):
    width, _, rgba = parsed
    offset = (y * width + x) * 4
    return tuple(rgba[offset:offset + 4])


class CutoutChromaTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()

    def test_codex_cutout_prompt_defaults_to_native_alpha(self):
        prompt = self.illo.cutout_prompt_for_backend(
            "Blot carrying a pencil",
            "codex",
            self.illo.CHROMA_MAGENTA,
        )

        self.assertIn("real transparent alpha channel", prompt.lower())
        self.assertNotIn("#FF00FF", prompt)
        self.assertNotIn("#00FF00", prompt)

    def test_codex_explicit_chroma_forces_compatibility_screen(self):
        prompt = self.illo.cutout_prompt_for_backend(
            "Blot carrying a pencil",
            "codex",
            self.illo.CHROMA_GREEN,
            force_chroma=True,
        )

        self.assertIn("BACKGROUND:", prompt)
        self.assertIn("#00FF00", prompt)
        self.assertNotIn("real transparent alpha channel", prompt.lower())

    def test_openrouter_cutout_prompt_stays_on_chroma_path(self):
        prompt = self.illo.cutout_prompt_for_backend(
            "Blot carrying a pencil",
            "openrouter",
            self.illo.CHROMA_MAGENTA,
        )

        self.assertIn("BACKGROUND:", prompt)
        self.assertIn("#FF00FF", prompt)
        self.assertNotIn("real transparent alpha channel", prompt.lower())

    def test_explicit_chroma_background_keeps_codex_on_compatibility_path(self):
        supplied = (
            "Blot carrying a pencil\n\n"
            "BACKGROUND: solid flat chroma green exactly #00FF00."
        )
        prompt = self.illo.cutout_prompt_for_backend(
            supplied,
            "codex",
            self.illo.CHROMA_GREEN,
        )

        self.assertEqual(prompt.count("BACKGROUND:"), 1)
        self.assertIn("#00FF00", prompt)
        self.assertNotIn("real transparent alpha channel", prompt.lower())

    def test_transparent_background_text_is_replaced_by_codex_native_contract(self):
        prompt = self.illo.cutout_prompt_for_backend(
            "Blot carrying a pencil\n\nBACKGROUND: transparent.",
            "codex",
            self.illo.CHROMA_MAGENTA,
        )

        self.assertIn("real transparent alpha channel", prompt.lower())
        self.assertNotIn("BACKGROUND:", prompt)

    def test_explicit_chroma_override_replaces_conflicting_legacy_screen(self):
        prompt = self.illo.cutout_prompt_for_backend(
            "Blot carrying a pencil\n\nBACKGROUND: chroma magenta exactly #FF00FF.",
            "codex",
            self.illo.CHROMA_GREEN,
            force_chroma=True,
        )

        self.assertEqual(prompt.count("BACKGROUND:"), 1)
        self.assertIn("#00FF00", prompt)
        self.assertNotIn("#FF00FF", prompt)

    def test_generate_applies_native_contract_after_codex_routing(self):
        captured = {}

        def fake_render(backend, cfg, prompt, *args, **kwargs):
            captured["backend"] = backend
            captured["prompt"] = prompt
            return {"backend": backend, "path": kwargs.get("out_path", "unused")}

        self.illo.load_config = lambda: {"configVersion": self.illo.CONFIG_VERSION}
        self.illo.resolve_backend = lambda cfg, requested: "codex"
        self.illo._render_one = fake_render
        with tempfile.TemporaryDirectory() as td:
            args = types.SimpleNamespace(
                prompt="Blot carrying a pencil",
                prompt_file=None,
                backend="codex",
                model=None,
                cutout=True,
                aspect=None,
                image_config=None,
                ref=[],
                chroma=None,
                out=str(Path(td) / "cutout.png"),
                count=1,
                cost=False,
                label=None,
                allow_paid_fallback=False,
            )
            with contextlib.redirect_stdout(io.StringIO()):
                self.illo.cmd_generate(args)

        self.assertEqual(captured["backend"], "codex")
        self.assertIn("real transparent alpha channel", captured["prompt"].lower())
        self.assertNotIn("BACKGROUND:", captured["prompt"])

    def test_grok_cutout_redirect_applies_codex_native_contract(self):
        captured = {}

        def fake_render(backend, cfg, prompt, *args, **kwargs):
            captured.update(backend=backend, prompt=prompt)
            return {"backend": backend, "path": kwargs.get("out_path", "unused")}

        self.illo.load_config = lambda: {"configVersion": self.illo.CONFIG_VERSION}
        self.illo.resolve_backend = lambda cfg, requested: "grok"
        self.illo.codex_available = lambda: True
        self.illo._render_one = fake_render
        with tempfile.TemporaryDirectory() as td:
            args = types.SimpleNamespace(
                prompt="Blot carrying a pencil", prompt_file=None, backend="grok",
                model=None, cutout=True, aspect=None, image_config=None, ref=[],
                chroma=None, out=str(Path(td) / "cutout.png"), count=1,
                cost=False, label=None, allow_paid_fallback=False,
            )
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.illo.cmd_generate(args)

        self.assertEqual(captured["backend"], "codex")
        self.assertIn("real transparent alpha channel", captured["prompt"].lower())

    def test_eval_html_supports_legacy_input_prompt_schema(self):
        cutout_eval = load_eval_module()
        results = [{
            "case": {"title": "Legacy result", "subtitle": "old schema"},
            "prompt_text": "legacy prompt text",
            "error": "old run failed",
        }]
        with tempfile.TemporaryDirectory() as td:
            html_text = cutout_eval.build_html(Path(td), results, "Legacy").read_text()

        self.assertIn("Input prompt (no render prompt recorded)", html_text)
        self.assertIn("legacy prompt text", html_text)

    def test_eval_expected_alpha_failure_is_bad(self):
        cutout_eval = load_eval_module()
        rec = {
            "case": {"expect_alpha": True},
            "cutout_alpha": False,
            "cutout_method": "opaque_fallback",
        }

        self.assertEqual(cutout_eval.verdict_class(rec), "bad")
        self.assertIn("expected", cutout_eval.verdict_text(rec))

    def test_interior_pink_accent_does_not_discard_chroma_cutout(self):
        source = synthetic_cutout_png(accent="interior")
        keyed = self.illo.chroma_key_to_png(source, key=self.illo.CHROMA_MAGENTA)
        self.assertIsNotNone(keyed)
        analysis = self.illo.analyze_cutout_alpha(keyed)
        self.assertTrue(analysis["clean_alpha"])
        self.assertEqual(analysis["accent_halo"], 0)

        with tempfile.TemporaryDirectory() as td:
            out, _, _, meta = self.illo.place_cutout_image(
                source, Path(td) / "cutout.png", chroma_key=self.illo.CHROMA_MAGENTA
            )
            parsed = self.illo._parse_png_rgb_or_rgba(out.read_bytes())

        self.assertTrue(meta["cutout_alpha"])
        self.assertEqual(meta["cutout_method"], "chroma")
        self.assertEqual(rgba_at(parsed, 0, 0)[3], 0)
        self.assertEqual(rgba_at(parsed, 127, 0)[3], 0)
        self.assertEqual(rgba_at(parsed, 0, 127)[3], 0)
        self.assertEqual(rgba_at(parsed, 127, 127)[3], 0)
        self.assertEqual(rgba_at(parsed, 64, 64), PINK + (255,))

    def test_pink_silhouette_tip_does_not_warn_as_accent_halo(self):
        source = synthetic_cutout_png(accent="tip")

        with tempfile.TemporaryDirectory() as td:
            out, _, _, meta = self.illo.place_cutout_image(
                source, Path(td) / "cutout.png", chroma_key=self.illo.CHROMA_MAGENTA
            )
            parsed = self.illo._parse_png_rgb_or_rgba(out.read_bytes())

        self.assertTrue(meta["cutout_alpha"])
        self.assertEqual(meta["cutout_method"], "chroma")
        self.assertEqual(rgba_at(parsed, 64, 18), PINK + (255,))
        self.assertIsNone(meta["cutout_note"])

    def test_adjacent_interior_soft_pixels_do_not_self_trigger_fringe(self):
        source = synthetic_interior_soft_patch_png()
        analysis = self.illo.analyze_cutout_alpha(source)

        self.assertTrue(analysis["clean_alpha"])
        self.assertEqual(analysis["green_fringe"], 0)
        self.assertEqual(analysis["magenta_fringe"], 0)
        self.assertEqual(analysis["accent_halo"], 0)
        self.assertEqual(analysis["fringe"], 0)
        self.assertIsNone(self.illo._cutout_quality_note(analysis))

    def test_outer_pink_ring_warns_but_keeps_chroma_cutout(self):
        source = synthetic_cutout_png(accent="ring")

        with tempfile.TemporaryDirectory() as td:
            out, _, _, meta = self.illo.place_cutout_image(
                source, Path(td) / "cutout.png", chroma_key=self.illo.CHROMA_MAGENTA
            )
            parsed = self.illo._parse_png_rgb_or_rgba(out.read_bytes())

        self.assertTrue(meta["cutout_alpha"])
        self.assertEqual(meta["cutout_method"], "chroma")
        self.assertEqual(rgba_at(parsed, 0, 0)[3], 0)
        self.assertEqual(rgba_at(parsed, 127, 127)[3], 0)
        self.assertRegex((meta["cutout_note"] or "").lower(), r"accent|halo|fringe")

    def test_pink_ring_behind_wide_soft_matte_warns_without_discarding_cutout(self):
        source = synthetic_accent_ring_behind_soft_matte_png(soft_layers=5)
        analysis = self.illo.analyze_cutout_alpha(source)

        self.assertTrue(analysis["clean_alpha"])
        self.assertGreaterEqual(analysis["accent_halo"], self.illo.CUTOUT_FRINGE_WARN)

        with tempfile.TemporaryDirectory() as td:
            out, _, _, meta = self.illo.place_cutout_image(
                source, Path(td) / "cutout.png", chroma_key=self.illo.CHROMA_MAGENTA
            )
            parsed = self.illo._parse_png_rgb_or_rgba(out.read_bytes())

        self.assertTrue(meta["cutout_alpha"])
        self.assertEqual(meta["cutout_method"], "native")
        self.assertEqual(rgba_at(parsed, 0, 0)[3], 0)
        self.assertRegex((meta["cutout_note"] or "").lower(), r"accent|halo|fringe")

    def test_soft_alpha_screen_fringe_warns_without_discarding_cutout(self):
        source = synthetic_soft_alpha_fringe_png(soft_layers=1)

        with tempfile.TemporaryDirectory() as td:
            out, _, _, meta = self.illo.place_cutout_image(
                source, Path(td) / "cutout.png", chroma_key=self.illo.CHROMA_MAGENTA
            )
            parsed = self.illo._parse_png_rgb_or_rgba(out.read_bytes())

        self.assertTrue(meta["cutout_alpha"])
        self.assertEqual(meta["cutout_method"], "native")
        self.assertEqual(rgba_at(parsed, 0, 0)[3], 0)
        self.assertRegex((meta["cutout_note"] or "").lower(), r"fringe")

    def test_two_layer_soft_alpha_screen_fringe_warns_without_discarding_cutout(self):
        source = synthetic_soft_alpha_fringe_png(soft_layers=2)

        with tempfile.TemporaryDirectory() as td:
            out, _, _, meta = self.illo.place_cutout_image(
                source, Path(td) / "cutout.png", chroma_key=self.illo.CHROMA_MAGENTA
            )
            parsed = self.illo._parse_png_rgb_or_rgba(out.read_bytes())

        self.assertTrue(meta["cutout_alpha"])
        self.assertEqual(meta["cutout_method"], "native")
        self.assertEqual(rgba_at(parsed, 0, 0)[3], 0)
        self.assertRegex((meta["cutout_note"] or "").lower(), r"fringe")


if __name__ == "__main__":
    unittest.main()
