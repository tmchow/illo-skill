import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from typing import Any, cast


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "skills" / "illo" / "scripts" / "illo.py"

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


def synthetic_soft_alpha_fringe_png():
    width = height = 128
    cx = cy = width // 2
    body_radius = 34
    pixels = [TRANSPARENT] * (width * height)
    for y in range(height):
        for x in range(width):
            dist2 = (x - cx) ** 2 + (y - cy) ** 2
            idx = y * width + x
            if dist2 <= body_radius ** 2:
                pixels[idx] = CREAM + (255,)
            elif dist2 <= (body_radius + 2) ** 2:
                pixels[idx] = GREEN + (255,)
            elif dist2 <= (body_radius + 6) ** 2:
                pixels[idx] = CREAM + (64,)
    return rgba_png(width, height, pixels)


def rgba_at(parsed, x, y):
    width, _, rgba = parsed
    offset = (y * width + x) * 4
    return tuple(rgba[offset:offset + 4])


class CutoutChromaTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()

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

    def test_soft_alpha_screen_fringe_warns_without_discarding_cutout(self):
        source = synthetic_soft_alpha_fringe_png()

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
