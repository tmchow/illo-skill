#!/usr/bin/env python3
"""Validate commit subjects that Release Please can read from a pull request."""

import argparse
import re
import subprocess
import sys


CONVENTIONAL_SUBJECT = re.compile(
    r"^(feat|fix|perf|revert|docs|style|refactor|test|build|ci|chore)"
    r"(\([a-z0-9._/-]+\))?!?:\s+\S.*$"
)
RELEASE_SUBJECT = re.compile(
    r"^(feat|fix|perf|revert)(\([a-z0-9._/-]+\))?!?:\s+\S.*$"
)
INSTALLED_SKILL_PREFIX = "skills/illo/"


def validate(commits, changed_paths):
    """Return validation errors for (sha, subject, is_merge) commit tuples."""
    errors = []
    non_merge_commits = [commit for commit in commits if not commit[2]]

    if not non_merge_commits:
        errors.append("Pull request has no non-merge commits to validate.")
        return errors

    for sha, subject, _is_merge in non_merge_commits:
        if not CONVENTIONAL_SUBJECT.fullmatch(subject):
            errors.append(
                f"Commit {sha[:12]} has a non-conventional subject: {subject!r}"
            )

    changes_installed_skill = any(
        path == INSTALLED_SKILL_PREFIX.rstrip("/")
        or path.startswith(INSTALLED_SKILL_PREFIX)
        for path in changed_paths
    )
    if changes_installed_skill and not any(
        RELEASE_SUBJECT.fullmatch(subject)
        for _sha, subject, _is_merge in non_merge_commits
    ):
        errors.append(
            "Changes under skills/illo/** require at least one non-merge "
            "feat:, fix:, perf:, or revert: commit."
        )

    return errors


def git(*args):
    return subprocess.check_output(
        ["git", *args], text=True, stderr=subprocess.STDOUT
    ).strip()


def load_pull_request(base_sha, head_sha):
    merge_base = git("merge-base", base_sha, head_sha)
    revision_range = f"{merge_base}..{head_sha}"
    commits = []

    for line in git("rev-list", "--reverse", "--parents", revision_range).splitlines():
        fields = line.split()
        sha = fields[0]
        subject = git("show", "-s", "--format=%s", sha)
        commits.append((sha, subject, len(fields) > 2))

    changed_output = git("diff", "--name-only", revision_range)
    changed_paths = changed_output.splitlines() if changed_output else []
    return commits, changed_paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="pull request base SHA")
    parser.add_argument("--head", required=True, help="pull request head SHA")
    args = parser.parse_args()

    commits, changed_paths = load_pull_request(args.base, args.head)
    errors = validate(commits, changed_paths)
    if errors:
        for error in errors:
            print(f"::error::{error}")
        print(
            "Use Conventional Commit subjects such as "
            "'fix: correct rendering guidance'."
        )
        return 1

    print(f"Validated {len(commits)} pull request commit(s).")
    if any(
        path == INSTALLED_SKILL_PREFIX.rstrip("/")
        or path.startswith(INSTALLED_SKILL_PREFIX)
        for path in changed_paths
    ):
        print("Installed-skill change includes a release-triggering commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
