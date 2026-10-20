import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from next_version import classify_commits, next_version, parse_bump


class ParseBumpTest(unittest.TestCase):
    def test_fix_only_is_patch(self):
        self.assertEqual(parse_bump(["fix: x"]), "patch")

    def test_feat_is_minor(self):
        self.assertEqual(parse_bump(["feat: x"]), "minor")
        self.assertEqual(parse_bump(["feat(scope): x", "fix: y"]), "minor")

    def test_breaking_bang_is_major(self):
        self.assertEqual(parse_bump(["feat(api)!: x"]), "major")

    def test_breaking_change_footer_triggers_major(self):
        self.assertEqual(parse_bump(["fix: x\n\nBREAKING CHANGE: rompe"]), "major")

    def test_unconventional_is_patch(self):
        self.assertEqual(parse_bump(["cosas sueltas", "wip"]), "patch")

    def test_no_commits_is_none(self):
        self.assertEqual(parse_bump([]), "none")


class NextVersionTest(unittest.TestCase):
    def test_next_version_bumps(self):
        self.assertEqual(next_version("v1.0.1", "patch"), "1.0.2")
        self.assertEqual(next_version("v1.0.1", "minor"), "1.1.0")
        self.assertEqual(next_version("v1.0.1", "major"), "2.0.0")
        self.assertEqual(next_version(None, "patch"), "0.0.1")
        self.assertEqual(next_version("v1.0.1", "none"), "1.0.1")


class ClassifyCommitsTest(unittest.TestCase):
    def test_merge_commits_excluded_from_notes(self):
        self.assertEqual(
            classify_commits(["Merge pull request #4", "Revert \"feat: x\"", "fix: x"]),
            {"Fixed": ["fix: x"]},
        )

    def test_classify_sections(self):
        self.assertEqual(classify_commits(["feat: x"]), {"Added": ["feat: x"]})
        self.assertEqual(classify_commits(["fix: x"]), {"Fixed": ["fix: x"]})
        self.assertEqual(
            classify_commits(["docs: x", "chore: y", "refactor: z"]),
            {"Changed": ["docs: x", "chore: y", "refactor: z"]},
        )
        self.assertEqual(
            classify_commits(["feat(api)!: x"]),
            {"Breaking": ["feat(api)!: x"]},
        )


if __name__ == "__main__":
    unittest.main()
