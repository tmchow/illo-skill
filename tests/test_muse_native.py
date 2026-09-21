import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any, cast


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "skills" / "illo" / "scripts" / "illo.py"


def load_illo_module():
    spec = importlib.util.spec_from_file_location("illo_script_under_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load illo script from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(Any, module)


class KeyoutParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.illo = load_illo_module()

    def run_main(self, argv):
        with self.assertRaises(SystemExit) as ctx:
            old = sys.argv
            sys.argv = ["illo.py"] + argv
            try:
                self.illo.main()
            finally:
                sys.argv = old
        return ctx.exception

    def test_keyout_accepts_positional_src(self):
        # Documented form: keyout <screen.png> --chroma magenta --out <final.png>.
        # A missing file must fail with "no such file" (cmd_keyout), not an
        # argparse usage error (exit code 2).
        exc = self.run_main(["keyout", "/nonexistent-screen.png",
                             "--chroma", "magenta", "--out", "/tmp/x.png"])
        self.assertNotEqual(exc.code, 2)
        self.assertIn("no such file", str(exc.code))


class RecordValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.illo = load_illo_module()

    def make_args(self, **kw):
        import types
        base = dict(path="", dir=None, backend="muse-native", label="t",
                    prompt_file=None)
        base.update(kw)
        return types.SimpleNamespace(**base)

    def tiny_png(self, width=4, height=4, rgb=(255, 0, 255)):
        import struct
        import zlib
        raw = bytearray()
        for _ in range(height):
            raw.append(0)
            for _ in range(width):
                raw.extend(rgb)
        ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

        def chunk(kind, data):
            c = struct.pack(">I", len(data)) + kind + data
            return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw)))
                + chunk(b"IEND", b""))

    def test_record_rejects_invalid_image(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.png"
            bad.write_bytes(b"this is not image data")
            with self.assertRaises(SystemExit) as ctx:
                self.illo.cmd_record(self.make_args(path=str(bad), dir=td))
            self.assertIn("not a valid PNG or JPEG image",
                          str(ctx.exception.code))
            self.assertFalse((Path(td) / "manifest.jsonl").exists())

    def test_record_rejects_missing_prompt_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            img = Path(td) / "ok.png"
            img.write_bytes(self.tiny_png())
            with self.assertRaises(SystemExit) as ctx:
                self.illo.cmd_record(self.make_args(
                    path=str(img), dir=td,
                    prompt_file=str(Path(td) / "nope.txt")))
            self.assertIn("no such file", str(ctx.exception.code))

    def test_record_happy_path(self):
        import io
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            img = Path(td) / "ok.png"
            img.write_bytes(self.tiny_png(4, 4))
            pf = Path(td) / "prompt.txt"
            pf.write_text("a test prompt", encoding="utf-8")
            buf = io.StringIO()
            old = sys.stdout
            sys.stdout = buf
            try:
                self.illo.cmd_record(self.make_args(
                    path=str(img), dir=td, prompt_file=str(pf)))
            finally:
                sys.stdout = old
            rec = json.loads(buf.getvalue())
            self.assertEqual((rec["width"], rec["height"]), (4, 4))
            self.assertEqual(rec["prompt"], "a test prompt")
            self.assertEqual(rec["backend"], "muse-native")
            lines = (Path(td) / "manifest.jsonl").read_text().strip().split("\n")
            self.assertEqual(len(lines), 1)


if __name__ == "__main__":
    unittest.main()
