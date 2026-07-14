import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from typing import Any, cast
from unittest import mock


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


def write_png_artifact(path):
    """Write enough PNG structure for illo's artifact validation tests."""
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\x0dIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
    )


def generated_session(codex_home, generated_subdir):
    session = Path(codex_home) / generated_subdir / "session-id"
    session.mkdir(parents=True)
    return session


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
            write_png_artifact(out_path)
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

    def test_nonzero_exit_with_requested_output_succeeds(self):
        def fake_run(cmd, input, capture_output, text, timeout):
            write_png_artifact(out_path)
            return FakeCompletedProcess(returncode=1, stderr="empty final response")

        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "requested.png"
            self.illo.subprocess.run = fake_run
            produced, meta = self.illo.codex_exec_generate(
                "draw the mascot", [], out_path
            )

        self.assertEqual(produced, out_path.resolve())
        self.assertEqual(meta, {"model": None, "id": None})

    def test_nonzero_exit_with_fresh_nested_generated_artifact_succeeds(self):
        with tempfile.TemporaryDirectory() as codex_home, tempfile.TemporaryDirectory() as td:
            artifact = generated_session(
                codex_home, self.illo.CODEX_GENERATED_SUBDIR
            ) / "render.png"

            def fake_run(cmd, input, capture_output, text, timeout):
                write_png_artifact(artifact)
                return FakeCompletedProcess(returncode=1, stderr="empty final response")

            self.illo.subprocess.run = fake_run
            with mock.patch.dict(os.environ, {"CODEX_HOME": codex_home}):
                produced, meta = self.illo.codex_exec_generate(
                    "draw the mascot", [], Path(td) / "requested.png"
                )

        self.assertEqual(produced, artifact)
        self.assertEqual(meta, {"model": None, "id": None})

    def test_timeout_with_fresh_nested_generated_artifact_succeeds(self):
        with tempfile.TemporaryDirectory() as codex_home, tempfile.TemporaryDirectory() as td:
            artifact = generated_session(
                codex_home, self.illo.CODEX_GENERATED_SUBDIR
            ) / "render.png"

            def fake_run(cmd, input, capture_output, text, timeout):
                write_png_artifact(artifact)
                raise self.illo.subprocess.TimeoutExpired(cmd, timeout)

            self.illo.subprocess.run = fake_run
            with mock.patch.dict(os.environ, {"CODEX_HOME": codex_home}):
                produced, meta = self.illo.codex_exec_generate(
                    "draw the mascot", [], Path(td) / "requested.png"
                )

        self.assertEqual(produced, artifact)
        self.assertEqual(meta, {"model": None, "id": None})

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

    def test_nonzero_exit_with_invalid_fresh_nested_artifact_fails(self):
        with tempfile.TemporaryDirectory() as codex_home, tempfile.TemporaryDirectory() as td:
            artifact = generated_session(
                codex_home, self.illo.CODEX_GENERATED_SUBDIR
            ) / "partial.png"

            def fake_run(cmd, input, capture_output, text, timeout):
                artifact.write_bytes(b"not an image")
                return FakeCompletedProcess(returncode=1, stderr="empty final response")

            self.illo.subprocess.run = fake_run
            with mock.patch.dict(os.environ, {"CODEX_HOME": codex_home}):
                with self.assertRaises(self.illo.BackendUnavailable):
                    self.illo.codex_exec_generate(
                        "draw the mascot", [], Path(td) / "requested.png"
                    )

    def test_nonzero_exit_with_stale_nested_artifact_fails(self):
        with tempfile.TemporaryDirectory() as codex_home, tempfile.TemporaryDirectory() as td:
            artifact = generated_session(
                codex_home, self.illo.CODEX_GENERATED_SUBDIR
            ) / "stale.png"

            def fake_run(cmd, input, capture_output, text, timeout):
                write_png_artifact(artifact)
                os.utime(artifact, (0, 0))
                return FakeCompletedProcess(returncode=1, stderr="empty final response")

            self.illo.subprocess.run = fake_run
            with mock.patch.dict(os.environ, {"CODEX_HOME": codex_home}):
                with self.assertRaises(self.illo.BackendUnavailable) as ctx:
                    self.illo.codex_exec_generate(
                        "draw the mascot", [], Path(td) / "requested.png"
                    )

        self.assertIn("codex exec exited 1", str(ctx.exception))

    def test_nonzero_exit_with_no_artifact_fails(self):
        def fake_run(cmd, input, capture_output, text, timeout):
            return FakeCompletedProcess(returncode=1, stderr="empty final response")

        with tempfile.TemporaryDirectory() as codex_home, tempfile.TemporaryDirectory() as td:
            self.illo.subprocess.run = fake_run
            with mock.patch.dict(os.environ, {"CODEX_HOME": codex_home}):
                with self.assertRaises(self.illo.BackendUnavailable) as ctx:
                    self.illo.codex_exec_generate(
                        "draw the mascot", [], Path(td) / "requested.png"
                    )

        self.assertIn("codex exec exited 1", str(ctx.exception))

    def test_count_batch_prior_artifact_not_reused(self):
        """A prior --count iteration's artifact in generated_images must not
        be silently returned when the current Codex exec fails to produce any
        new artifact. Without the pre-exec snapshot exclusion, the prior
        artifact's fresh mtime (within CODEX_MTIME_SKEW of start) would let
        it pass the freshness floor. With exclusion it must be blocked."""
        def fake_run(cmd, input, capture_output, text, timeout):
            return FakeCompletedProcess(returncode=1, stderr="empty final response")

        with tempfile.TemporaryDirectory() as codex_home, tempfile.TemporaryDirectory() as td:
            # Simulate a prior iteration's nested artifact in generated_images.
            # Its mtime will be recent enough to pass the freshness floor, so
            # only the pre-exec snapshot exclusion prevents its reuse.
            prior = generated_session(
                codex_home, self.illo.CODEX_GENERATED_SUBDIR
            ) / "previous-iteration.png"
            write_png_artifact(prior)

            self.illo.subprocess.run = fake_run
            with mock.patch.dict(os.environ, {"CODEX_HOME": codex_home}):
                with self.assertRaises(self.illo.BackendUnavailable) as ctx:
                    self.illo.codex_exec_generate(
                        "draw the mascot", [], Path(td) / "requested.png"
                    )

        self.assertIn("codex exec exited 1", str(ctx.exception))

    def test_count_batch_fresh_artifact_still_detected_alongside_prior(self):
        """When Codex creates a genuinely new nested artifact alongside a prior
        iteration's artifact, the exclusion of pre-existing files must not
        accidentally exclude the new one."""
        with tempfile.TemporaryDirectory() as codex_home, tempfile.TemporaryDirectory() as td:
            # Prior iteration's artifact — recent mtime, same layout.
            prior = generated_session(
                codex_home, self.illo.CODEX_GENERATED_SUBDIR
            ) / "previous-iteration.png"
            write_png_artifact(prior)

            # Fresh artifact produced by THIS exec — different session dir so
            # it's a different path from the excluded prior.
            fresh_session = (
                Path(codex_home) / self.illo.CODEX_GENERATED_SUBDIR / "other-session"
            )
            fresh_session.mkdir(parents=True)
            fresh = fresh_session / "fresh-this-run.png"

            def fake_run(cmd, input, capture_output, text, timeout):
                write_png_artifact(fresh)
                return FakeCompletedProcess(returncode=1, stderr="empty final response")

            self.illo.subprocess.run = fake_run
            with mock.patch.dict(os.environ, {"CODEX_HOME": codex_home}):
                produced, meta = self.illo.codex_exec_generate(
                    "draw the mascot", [], Path(td) / "requested.png"
                )

        self.assertEqual(produced, fresh)
        self.assertEqual(meta, {"model": None, "id": None})


class PaidFallbackTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()

        def fail_codex(*args, **kwargs):
            raise self.illo.BackendUnavailable("wrapper failed")

        self.illo.codex_exec_generate = fail_codex

    def test_default_cli_failure_never_calls_openrouter_with_configured_key(self):
        def unexpected_openrouter(*args, **kwargs):
            self.fail("OpenRouter must not be called without explicit paid fallback")

        self.illo._openrouter_record = unexpected_openrouter
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(SystemExit) as ctx:
                self.illo._render_one(
                    "codex", {"apiKey": "configured"}, "prompt", "model",
                    ["ref.png"], False, Path(td) / "out.png"
                )

        self.assertIn("--allow-paid-fallback", str(ctx.exception))

    def test_explicit_paid_fallback_records_openrouter_backend(self):
        self.illo._openrouter_record = lambda *args, **kwargs: {"backend": "openrouter"}
        with tempfile.TemporaryDirectory() as td:
            rec = self.illo._render_one(
                "codex", {"apiKey": "configured"}, "prompt", "model",
                ["ref.png"], False, Path(td) / "out.png", allow_paid_fallback=True
            )

        self.assertEqual(rec["backend"], "openrouter")

    def test_direct_openrouter_does_not_require_paid_fallback_flag(self):
        self.illo._openrouter_record = lambda *args, **kwargs: {"backend": "openrouter"}
        with tempfile.TemporaryDirectory() as td:
            rec = self.illo._render_one(
                "openrouter", {"apiKey": "configured"}, "prompt", "model",
                ["ref.png"], False, Path(td) / "out.png"
            )

        self.assertEqual(rec["backend"], "openrouter")


if __name__ == "__main__":
    unittest.main()
