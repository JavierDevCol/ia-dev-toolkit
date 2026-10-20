import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from next_version import classify_commits, find_last_stable, next_version, parse_bump, plan_release


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


class FindLastStableTest(unittest.TestCase):
    def test_picks_highest_stable_by_numeric_order(self):
        self.assertEqual(
            find_last_stable(["v1.0.9", "v1.0.10", "v1.0.10-TEST", "v0.9.9"]),
            "v1.0.10",
        )

    def test_returns_none_without_stable_tags(self):
        self.assertIsNone(find_last_stable([]))
        self.assertIsNone(find_last_stable(["v1.2.3-TEST", "not-a-tag"]))


class PlanReleaseTest(unittest.TestCase):
    def test_test_channel_appends_suffix(self):
        result = plan_release("test", ["v1.0.1"], ["fix: x"], [])
        self.assertEqual(result["tag"], "v1.0.2-TEST")
        self.assertEqual(result["version"], "1.0.2")
        self.assertEqual(result["source"], "recalculated")
        self.assertEqual(result["warnings"], [])

    def test_adopts_test_tag_for_stable(self):
        result = plan_release("stable", ["v1.0.1", "v1.0.2-TEST"], [], ["v1.0.2-TEST"])
        self.assertEqual(result["tag"], "v1.0.2")
        self.assertEqual(result["version"], "1.0.2")
        self.assertEqual(result["source"], "test-tag")
        self.assertEqual(result["warnings"], [])

    def test_recalculates_when_no_test_tag(self):
        result = plan_release("stable", ["v1.0.1"], ["feat: x"], [])
        self.assertEqual(result["source"], "recalculated")
        self.assertEqual(result["tag"], "v1.1.0")

    def test_existing_tag_is_reported_not_forced(self):
        tags = ["v1.0.1", "v1.0.2", "v1.0.2-TEST"]
        result = plan_release("stable", tags, ["fix: x"], ["v1.0.2-TEST"])
        self.assertEqual(result["source"], "recalculated")
        self.assertEqual(result["tag"], "v1.0.3")
        self.assertTrue(any("v1.0.2" in warning for warning in result["warnings"]))
        self.assertNotIn(result["tag"], tags)

    def test_nothing_to_release_returns_none(self):
        self.assertIsNone(plan_release("stable", ["v1.0.1"], [], []))
        self.assertIsNone(plan_release("test", ["v1.0.1"], [], []))

    def test_highest_test_tag_wins(self):
        tags = ["v1.0.1", "v1.0.2-TEST", "v1.0.3-TEST"]
        result = plan_release("stable", tags, [], ["v1.0.2-TEST", "v1.0.3-TEST"])
        self.assertEqual(result["tag"], "v1.0.3")
        self.assertEqual(result["version"], "1.0.3")
        self.assertEqual(result["source"], "test-tag")

    def test_never_adopts_below_last_stable(self):
        tags = ["v1.0.1"]
        result = plan_release("stable", tags, ["fix: x"], ["v1.0.0-TEST"])
        self.assertEqual(result["source"], "recalculated")
        self.assertEqual(result["tag"], "v1.0.2")
        self.assertNotIn(result["tag"], tags)
        self.assertIsNone(plan_release("stable", tags, [], ["v1.0.0-TEST"]))

    def test_first_release_without_tags(self):
        result = plan_release("stable", [], ["feat: x"], [])
        self.assertEqual(result["tag"], "v0.1.0")
        self.assertEqual(result["source"], "recalculated")

    def test_invalid_channel_raises(self):
        with self.assertRaises(ValueError):
            plan_release("hotfix", [], ["fix: x"], [])


if __name__ == "__main__":
    unittest.main()
