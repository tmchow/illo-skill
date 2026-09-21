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


if __name__ == "__main__":
    unittest.main()
