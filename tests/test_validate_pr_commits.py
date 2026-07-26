import importlib.util
import unittest
from pathlib import Path
from typing import Any, cast


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "scripts"
    / "validate_pr_commits.py"
)


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validator_under_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load validator from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(Any, module)


class PullRequestCommitValidationTests(unittest.TestCase):
    def setUp(self):
        self.validator = load_validator_module()

    def commit(self, subject, merge=False):
        return ("a" * 40, subject, merge)

    def test_merge_strategy_validates_release_please_child_commits(self):
        commits = [
            self.commit("feat: add SNES look"),
            self.commit("Merge pull request #46 from tmchow/add-snes-look", merge=True),
        ]

        self.assertEqual(
            self.validator.validate(commits, ["skills/illo/references/styles/snes.md"]),
            [],
        )

        errors = self.validator.validate(
            [self.commit("Add SNES look")],
            ["skills/illo/references/styles/snes.md"],
        )
        self.assertTrue(any("non-conventional" in error for error in errors))

    def test_repo_only_ci_and_docs_commits_are_valid(self):
        for subject in ("ci: tighten checks", "docs: clarify contribution rules"):
            with self.subTest(subject=subject):
                self.assertEqual(
                    self.validator.validate(
                        [self.commit(subject)], [".github/workflows/pr-title.yml"]
                    ),
                    [],
                )

    def test_installed_skill_fix_and_feat_commits_are_valid(self):
        for subject in (
            "fix: correct rendering guidance",
            "feat(illo)!: replace the rendering contract",
        ):
            with self.subTest(subject=subject):
                self.assertEqual(
                    self.validator.validate(
                        [self.commit(subject)], ["skills/illo/SKILL.md"]
                    ),
                    [],
                )

    def test_installed_skill_with_only_ci_or_docs_is_rejected(self):
        commits = [
            self.commit("ci: update checks"),
            self.commit("docs: describe the change"),
        ]

        errors = self.validator.validate(commits, ["skills/illo/SKILL.md"])

        self.assertEqual(len(errors), 1)
        self.assertIn("require at least one", errors[0])

    def test_trusted_generated_release_metadata_is_valid(self):
        errors = self.validator.validate(
            [self.commit("chore(main): release 0.31.6")],
            ["skills/illo/SKILL.md", "version.txt"],
            trusted_release_pr=True,
        )

        self.assertEqual(errors, [])

    def test_fork_like_release_metadata_without_trusted_mode_is_rejected(self):
        errors = self.validator.validate(
            [self.commit("chore(main): release 0.31.6")],
            ["skills/illo/SKILL.md", "version.txt"],
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("require at least one", errors[0])

    def test_trusted_generated_release_still_requires_conventional_subject(self):
        errors = self.validator.validate(
            [self.commit("release 0.31.6")],
            ["skills/illo/SKILL.md", "version.txt"],
            trusted_release_pr=True,
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("non-conventional", errors[0])


if __name__ == "__main__":
    unittest.main()
