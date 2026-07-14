import importlib.util
import tempfile
import time
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


class GrokExecTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()
        self.illo.grok_available = lambda: True
        self.original_run = self.illo.subprocess.run

    def tearDown(self):
        self.illo.subprocess.run = self.original_run

    def test_grok_exec_sandboxes_and_uses_image_edit_with_refs(self):
        captured = {}

        def fake_run(cmd, capture_output, text, timeout):
            captured["cmd"] = cmd
            captured["timeout"] = timeout
            out_path.write_bytes(b"not a real png, just a non-empty artifact")
            return FakeCompletedProcess(returncode=0)

        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            out_path = run_dir / "render.png"
            refs = [run_dir / "sheet.png"]
            for ref in refs:
                ref.write_bytes(b"ref")

            self.illo.subprocess.run = fake_run
            produced, meta = self.illo.grok_exec_generate(
                "draw the mascot", [str(r) for r in refs], out_path
            )

        self.assertEqual(produced, out_path.resolve())
        self.assertEqual(meta, {"model": None, "id": None})
        cmd = captured["cmd"]
        # Prompt is passed as the argument after -p, not on stdin.
        self.assertEqual(cmd[cmd.index("-p") + 1].count("draw the mascot"), 1)
        prompt_arg = cmd[cmd.index("-p") + 1]
        # Confinement + auto-approval + run-dir cwd.
        sandbox_index = cmd.index("--sandbox")
        self.assertEqual(cmd[sandbox_index + 1], "workspace")
        self.assertIn("--always-approve", cmd)
        self.assertEqual(cmd[cmd.index("--cwd") + 1], str(out_path.resolve().parent))
        # Reference present -> image_edit with the ref path in the prompt text.
        self.assertIn("image_edit", prompt_arg)
        self.assertIn(str(refs[0].resolve()), prompt_arg)
        self.assertIn(str(out_path.resolve()), prompt_arg)
        self.assertEqual(captured["timeout"], self.illo.GROK_EXEC_TIMEOUT)

    def test_grok_exec_uses_image_gen_without_refs(self):
        def fake_run(cmd, capture_output, text, timeout):
            out_path.write_bytes(b"artifact")
            fake_run.prompt = cmd[cmd.index("-p") + 1]
            return FakeCompletedProcess(returncode=0)

        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "out.png"
            self.illo.subprocess.run = fake_run
            self.illo.grok_exec_generate("ref-less bootstrap", [], out_path)

        self.assertIn("image_gen", fake_run.prompt)
        self.assertNotIn("image_edit", fake_run.prompt)

    def test_grok_exec_falls_back_to_session_cache_when_out_missing(self):
        # Agent generated but never copied to --out: fetch the freshest session
        # image instead of failing.
        with tempfile.TemporaryDirectory() as grok_home, tempfile.TemporaryDirectory() as td:
            images = Path(grok_home) / "sessions" / "enc-cwd" / "uuid" / "images"
            images.mkdir(parents=True)
            artifact = images / "1.jpg"
            artifact.write_bytes(b"generated")
            # Postdate the exec floor so recency check passes.
            future = time.time() + 5
            import os
            os.utime(artifact, (future, future))
            self.illo.grok_home = lambda: Path(grok_home)

            def fake_run(cmd, capture_output, text, timeout):
                return FakeCompletedProcess(returncode=0)  # writes nothing to --out

            self.illo.subprocess.run = fake_run
            produced, _ = self.illo.grok_exec_generate("prompt", [], Path(td) / "out.png")
            self.assertEqual(produced, artifact)

    def test_grok_error_is_redacted_and_backend_unavailable(self):
        fake_secret = "sk-" + "secretvalue123"

        def fake_run(cmd, capture_output, text, timeout):
            return FakeCompletedProcess(returncode=2, stdout=f"boom {fake_secret}", stderr="")

        with tempfile.TemporaryDirectory() as td:
            self.illo.subprocess.run = fake_run
            with self.assertRaises(self.illo.BackendUnavailable) as ctx:
                self.illo.grok_exec_generate("prompt", [], Path(td) / "out.png")

        msg = str(ctx.exception)
        self.assertIn("grok exited 2", msg)
        self.assertIn("<redacted>", msg)
        self.assertNotIn(fake_secret, msg)


class GrokDetectionTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()

    def test_available_requires_binary_and_auth_file(self):
        with tempfile.TemporaryDirectory() as home:
            self.illo.grok_home = lambda: Path(home)
            self.illo.shutil.which = lambda name: "/usr/local/bin/grok" if name == "grok" else None

            self.illo._GROK_AVAILABLE = None
            self.assertFalse(self.illo.grok_available())  # no auth.json yet

            (Path(home) / "auth.json").write_text("{}")
            self.illo._GROK_AVAILABLE = None
            self.assertTrue(self.illo.grok_available())

            self.illo.shutil.which = lambda name: None
            self.illo._GROK_AVAILABLE = None
            self.assertFalse(self.illo.grok_available())  # binary gone


class CutoutModelRoutingTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()

    def test_cutout_always_resolves_gpt_image_regardless_of_backend(self):
        # The bug guarded here: a Codex/Grok cutout that falls back to OpenRouter
        # must still land on GPT Image 2, not the editorial default.
        cfg = {"model": "x-ai/some-editorial-model"}
        for backend in ("codex", "grok", "openrouter"):
            self.assertEqual(
                self.illo.resolve_generate_model(cfg, None, backend, cutout=True),
                self.illo.CUTOUT_OPENROUTER_MODEL,
                backend,
            )
        # Explicit --model still wins for cutouts.
        self.assertEqual(
            self.illo.resolve_generate_model(cfg, "user/model", "grok", cutout=True),
            "user/model",
        )
        # Editorial keeps config/default resolution.
        self.assertEqual(
            self.illo.resolve_generate_model(cfg, None, "grok", cutout=False),
            "x-ai/some-editorial-model",
        )


class RenderRefResolutionTests(unittest.TestCase):
    """A ref-less render with a configured default character must attach that
    sheet on every path — including OpenRouter (direct) and the CLI→OpenRouter
    fallback, not only the CLI backends."""

    def setUp(self):
        self.illo = load_illo_module()

    def _with_default_char(self, cfgdir):
        char_ref = Path(cfgdir) / "characters" / "bot" / "reference.png"
        char_ref.parent.mkdir(parents=True)
        char_ref.write_bytes(b"sheet")
        self.illo.config_dir = lambda: Path(cfgdir)
        return char_ref

    def test_direct_openrouter_gets_default_character_ref(self):
        with tempfile.TemporaryDirectory() as cfgdir:
            char_ref = self._with_default_char(cfgdir)
            captured = {}
            self.illo._openrouter_record = (
                lambda cfg, prompt, model, refs, *a, **k: captured.update(refs=refs) or {}
            )
            cfg = {"apiKey": "k", "defaultCharacter": "bot"}
            self.illo._render_one("openrouter", cfg, "p", "m", [], False, Path(cfgdir) / "o.png")
            self.assertEqual(captured["refs"], [str(char_ref)])

    def test_cli_fallback_to_openrouter_keeps_default_character_ref(self):
        with tempfile.TemporaryDirectory() as cfgdir:
            char_ref = self._with_default_char(cfgdir)
            self.illo.grok_available = lambda: True

            def boom(*a, **k):
                raise self.illo.BackendUnavailable("down")

            self.illo.grok_exec_generate = boom
            captured = {}
            self.illo._openrouter_record = (
                lambda cfg, prompt, model, refs, *a, **k: captured.update(refs=refs) or {}
            )
            cfg = {"apiKey": "k", "defaultCharacter": "bot"}
            self.illo._render_one(
                "grok", cfg, "p", "m", [], False, Path(cfgdir) / "o.png",
                allow_paid_fallback=True,
            )
            self.assertEqual(captured["refs"], [str(char_ref)])


if __name__ == "__main__":
    unittest.main()
