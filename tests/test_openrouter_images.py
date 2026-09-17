import base64
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from test_cutout_chroma import load_illo_module, rgba_png


class OpenRouterImagesTests(unittest.TestCase):
    def setUp(self):
        self.illo = load_illo_module()
        self.png = rgba_png(64, 64, [(0, 0, 0, 0)] * 4096)
        self.content = [{"type": "text", "text": "draw"},
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64,one"}},
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64,two"}}]

    def response(self, **extra):
        return io.BytesIO(json.dumps({
            "data": [{"b64_json": base64.b64encode(self.png).decode()}],
            **extra,
        }).encode())

    def test_flare_request_preserves_all_refs_and_uses_images_response(self):
        options = {"aspect_ratio": "16:9", "quality": "low"}
        with mock.patch.object(self.illo.urllib.request, "urlopen",
                               return_value=self.response(usage={"cost": 0.02})) as post:
            image, meta = self.illo.openrouter_generate(
                self.illo.FLARE_MODEL, self.content, "test-key", options)
        req = post.call_args.args[0]
        self.assertEqual(req.full_url, "https://openrouter.ai/api/v1/images")
        self.assertEqual(json.loads(req.data), {
            "model": self.illo.FLARE_MODEL, "prompt": "draw", "n": 1,
            "input_references": self.content[1:], "output_format": "png", **options,
        })
        self.assertEqual(options, {"aspect_ratio": "16:9", "quality": "low"})
        self.assertEqual(image, self.png)
        self.assertEqual(meta, {"model": self.illo.FLARE_MODEL, "id": None, "cost": 0.02})

    def test_image_options_cannot_override_identity_prompt_or_batch_size(self):
        for field in ("model", "prompt", "input_references", "n", "stream"):
            with self.subTest(field=field), mock.patch.object(
                    self.illo.urllib.request, "urlopen") as post:
                with self.assertRaisesRegex(SystemExit, "Unsupported Images API"):
                    self.illo.openrouter_generate(
                        self.illo.FLARE_MODEL, self.content, "test-key", {field: "override"})
                post.assert_not_called()

    def test_bad_images_are_rejected(self):
        for data in ([], [{"b64_json": "not base64!"}],
                     [{"b64_json": base64.b64encode(b"not an image").decode()}]):
            with self.subTest(data=data), mock.patch.object(
                    self.illo.urllib.request, "urlopen",
                    return_value=io.BytesIO(json.dumps({"data": data}).encode())):
                with self.assertRaises(self.illo.BackendUnavailable):
                    self.illo.openrouter_generate(self.illo.FLARE_MODEL, self.content, "test-key")

    def test_http_error_does_not_retry_paid_generation(self):
        error = urllib.error.HTTPError("url", 400, "bad request", {},
                                       io.BytesIO(b'background: not supported'))
        self.addCleanup(error.close)
        with mock.patch.object(self.illo.urllib.request, "urlopen", side_effect=error) as post:
            with self.assertRaisesRegex(SystemExit, "background: not supported"):
                self.illo.openrouter_generate(self.illo.FLARE_MODEL, self.content, "test-key")
        self.assertEqual(post.call_count, 1)

    def test_other_models_keep_chat_transport(self):
        response = {"id": "chat-id", "choices": [{"message": {"images": [
            {"image_url": {"url": "data:image/png;base64," + base64.b64encode(self.png).decode()}}
        ]}}]}
        with mock.patch.object(self.illo, "post_chat", return_value=response) as post:
            image, meta = self.illo.openrouter_generate("other/model", self.content, "test-key")
        post.assert_called_once_with("other/model", self.content, "test-key", ["image", "text"], None)
        self.assertEqual(image, self.png)
        self.assertEqual(meta, {"model": "other/model", "id": "chat-id"})

    def test_inline_cost_and_native_alpha_survive_placement_without_cost_lookup(self):
        for usage, expected in (({"cost": 0.02}, 0.02), ({"cost": 0}, 0), ({}, None)):
            with self.subTest(usage=usage), tempfile.TemporaryDirectory() as td, \
                    mock.patch.object(self.illo.urllib.request, "urlopen",
                                      return_value=self.response(usage=usage)), \
                    mock.patch.object(self.illo, "fetch_cost") as fetch:
                rec = self.illo._openrouter_record(
                    {"apiKey": "test-key"}, "draw", self.illo.FLARE_MODEL,
                    [], True, Path(td) / "cutout.png", cutout=True)
                self.assertEqual(rec["cost"], expected)
                self.assertEqual(rec["cutout_method"], "native")
                self.assertEqual(Path(rec["path"]).read_bytes(), self.png)
                fetch.assert_not_called()

if __name__ == "__main__":
    unittest.main()
