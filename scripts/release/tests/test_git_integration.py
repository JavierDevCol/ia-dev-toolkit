import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from next_version import git_messages_since, git_test_tag_ancestors

RELEASE_SCRIPT = Path(__file__).resolve().parents[1] / "next_version.py"


class GitIntegrationTest(unittest.TestCase):
    def _git(self, repo, *args):
        result = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def _init_repo(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name) / "repo"
        repo.mkdir()
        self._git(repo, "init", "--quiet")
        self._git(repo, "config", "user.email", "release-test@example.com")
        self._git(repo, "config", "user.name", "Release Test")
        self._git(repo, "config", "commit.gpgsign", "false")
        self._git(repo, "config", "tag.gpgsign", "false")
        self._git(repo, "checkout", "--quiet", "-b", "main")
        return repo

    def _commit(self, repo, message, filename):
        (repo / filename).write_text(message + "\n", encoding="utf-8")
        self._git(repo, "add", filename)
        self._git(repo, "commit", "--quiet", "-m", message)

    def _run_cli(self, repo, channel, *extra):
        return subprocess.run(
            [sys.executable, str(RELEASE_SCRIPT), "--channel", channel, "--repo", str(repo), *extra],
            capture_output=True,
            text=True,
        )

    def test_adopts_test_tag_behind_merge_commit(self):
        repo = self._init_repo()
        self._commit(repo, "chore: init", "a.txt")
        self._git(repo, "tag", "v1.0.1")
        self._git(repo, "checkout", "--quiet", "-b", "develop")
        self._commit(repo, "feat: x", "d.txt")
        self._git(repo, "tag", "v1.0.2-TEST")
        self._git(repo, "checkout", "--quiet", "main")
        self._git(repo, "merge", "--no-ff", "--quiet", "-m", "Merge branch 'develop'", "develop")

        self.assertEqual(git_messages_since(repo, "v1.0.1"), ["feat: x"])
        self.assertEqual(
            git_test_tag_ancestors(repo, ["v1.0.1", "v1.0.2-TEST"]), ["v1.0.2-TEST"]
        )

        result = self._run_cli(repo, "stable")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "v1.0.2\n")

        result = self._run_cli(repo, "stable", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "tag": "v1.0.2",
                "version": "1.0.2",
                "source": "test-tag",
                "warnings": [],
                "resume": False,
            },
        )

    def test_cli_resumes_half_finished_release(self):
        repo = self._init_repo()
        self._commit(repo, "chore: init", "a.txt")
        self._git(repo, "tag", "-a", "v1.0.1", "-m", "Release v1.0.1")

        result = self._run_cli(repo, "stable", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["tag"], "v1.0.1")
        self.assertEqual(plan["version"], "1.0.1")
        self.assertEqual(plan["source"], "resume")
        self.assertTrue(plan["resume"])

    def test_cli_exit_3_when_nothing(self):
        repo = self._init_repo()
        self._commit(repo, "chore: init", "a.txt")
        self._git(repo, "tag", "v1.0.1")

        result = self._run_cli(repo, "test")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_cli_exit_3_when_only_merges_since_tag(self):
        repo = self._init_repo()
        self._commit(repo, "chore: init", "a.txt")
        root = self._git(repo, "rev-parse", "HEAD").strip()
        self._commit(repo, "fix: x", "b.txt")
        self._git(repo, "tag", "v1.0.1")
        # HEAD avanza solo con un merge real (padres el tag y su ancestro): sin
        # commits convencionales nuevos no hay nada que publicar y el tag ya no
        # está en HEAD, así que tampoco hay reanudación.
        tree = self._git(repo, "rev-parse", "HEAD^{tree}").strip()
        merge = self._git(
            repo,
            "commit-tree",
            tree,
            "-p",
            "v1.0.1",
            "-p",
            root,
            "-m",
            "Merge branch 'x'",
        ).strip()
        self._git(repo, "reset", "--hard", "--quiet", merge)

        result = self._run_cli(repo, "stable")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_cli_exit_1_on_error(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        not_a_repo = Path(tmp.name)

        result = self._run_cli(not_a_repo, "stable")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
