import importlib.util
import tempfile
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


class FakeCompletedProcess:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class CodexBackendTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()
        self.illo.codex_available = lambda: True
        self.original_run = self.illo.subprocess.run

    def tearDown(self):
        self.illo.subprocess.run = self.original_run

    def test_codex_exec_passes_refs_and_does_not_enable_removed_feature(self):
        captured = {}

        def fake_run(cmd, input, capture_output, text, timeout):
            captured["cmd"] = cmd
            captured["input"] = input
            captured["capture_output"] = capture_output
            captured["text"] = text
            captured["timeout"] = timeout
            out_path.write_bytes(b"not a real png, just a non-empty artifact")
            return FakeCompletedProcess(returncode=0)

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            out_path = run_dir / "render.png"
            refs = [run_dir / "ref-one.png", run_dir / "ref-two.png"]
            for ref in refs:
                ref.write_bytes(b"ref")

            self.illo.subprocess.run = fake_run
            produced, meta = self.illo.codex_exec_generate(
                "draw the mascot", [str(r) for r in refs], out_path
            )

        self.assertEqual(produced, out_path.resolve())
        self.assertEqual(meta, {"model": None, "id": None})
        cmd = captured["cmd"]
        # imagegenext was removed in Codex 0.144 (folded into stable
        # image_generation); illo must no longer enable it.
        self.assertNotIn("--enable", cmd)
        self.assertNotIn("imagegenext", cmd)
        self.assertEqual(cmd.count("-i"), 2)
        self.assertIn(str(refs[0]), cmd)
        self.assertIn(str(refs[1]), cmd)
        self.assertEqual(cmd[-1], "-")
        self.assertIn("draw the mascot", captured["input"])
        self.assertIn(str(out_path), captured["input"])
        self.assertTrue(captured["capture_output"])
        self.assertTrue(captured["text"])
        self.assertEqual(captured["timeout"], self.illo.CODEX_EXEC_TIMEOUT)

    def test_detect_codex_accepts_image_generation_alone(self):
        self.illo.shutil.which = lambda name: "/usr/local/bin/codex" if name == "codex" else None

        def fake_codex_run(args):
            if args == ["login", "status"]:
                return 0, "Logged in using ChatGPT"
            if args == ["features", "list"]:
                return 0, "image_generation stable true\n"
            raise AssertionError(args)

        self.illo._codex_run = fake_codex_run
        self.assertTrue(self.illo._detect_codex())

    def test_detect_codex_rejects_when_image_generation_absent(self):
        self.illo.shutil.which = lambda name: "/usr/local/bin/codex" if name == "codex" else None

        def fake_codex_run(args):
            if args == ["login", "status"]:
                return 0, "Logged in using ChatGPT"
            if args == ["features", "list"]:
                return 0, "apps stable true\nbrowser_use stable true\n"
            raise AssertionError(args)

        self.illo._codex_run = fake_codex_run
        self.assertFalse(self.illo._detect_codex())

    def test_generic_codex_error_includes_redacted_combined_output(self):
        fake_secret = "sk-" + "secretvalue123"

        def fake_run(cmd, input, capture_output, text, timeout):
            return FakeCompletedProcess(
                returncode=2,
                stdout=f"stdout says {fake_secret} should redact",
                stderr=" stderr details",
            )

        with tempfile.TemporaryDirectory() as td:
            self.illo.subprocess.run = fake_run
            with self.assertRaises(self.illo.BackendUnavailable) as ctx:
                self.illo.codex_exec_generate("prompt", [], Path(td) / "out.png")

        msg = str(ctx.exception)
        self.assertIn("codex exec exited 2", msg)
        self.assertIn("<redacted>", msg)
        self.assertNotIn(fake_secret, msg)
        self.assertIn("stderr details", msg)


if __name__ == "__main__":
    unittest.main()
