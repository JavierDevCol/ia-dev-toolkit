import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from next_version import classify_commits
from update_changelog import insert_release, render_body


class RenderBodyTest(unittest.TestCase):
    def test_render_body_sections_order(self):
        body = render_body(
            {
                "Fixed": ["fix: w"],
                "Changed": ["chore: z"],
                "Added": ["feat: y"],
                "Breaking": ["feat(api)!: x"],
            }
        )
        self.assertLess(body.index("### Breaking"), body.index("### Added"))
        self.assertLess(body.index("### Added"), body.index("### Changed"))
        self.assertLess(body.index("### Changed"), body.index("### Fixed"))
        self.assertIn("- feat(api)!: x", body)

    def test_merge_commits_excluded_from_notes(self):
        self.assertEqual(render_body(classify_commits(["Merge pull request #4"])), "")

    def test_skips_empty_sections(self):
        body = render_body({"Added": ["feat: y"], "Fixed": []})
        self.assertIn("### Added", body)
        self.assertNotIn("### Fixed", body)


class InsertReleaseTest(unittest.TestCase):
    def test_inserts_after_unreleased(self):
        text = (
            "# Changelog\n\n## [Unreleased]\n\n"
            "## [1.0.1] - 2026-10-01\n\n### Fixed\n- fix: old\n"
        )
        result = insert_release(
            text, "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        self.assertLess(
            result.index("## [Unreleased]"), result.index("## [1.0.2] - 2026-10-20")
        )
        self.assertLess(
            result.index("## [1.0.2] - 2026-10-20"), result.index("## [1.0.1]")
        )

    def test_creates_changelog_from_scratch(self):
        result = insert_release(
            "", "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        self.assertTrue(result.startswith("# Changelog\n\n## [Unreleased]\n\n"))
        self.assertIn("## [1.0.2] - 2026-10-20", result)
        self.assertIn("- feat: new", result)

    def test_preserves_existing_content(self):
        text = (
            "# Changelog\n\n## [Unreleased]\n\n"
            "## [1.0.1] - 2026-10-01\n\n### Fixed\n- fix: legacy bug\n"
        )
        result = insert_release(
            text, "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        self.assertIn("## [1.0.1] - 2026-10-01", result)
        self.assertIn("### Fixed\n- fix: legacy bug", result)

    def test_inserts_after_title_when_no_unreleased(self):
        text = "# Changelog\n\n## [1.0.1] - 2026-10-01\n\n### Fixed\n- fix: old\n"
        result = insert_release(
            text, "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        self.assertLess(result.index("# Changelog"), result.index("## [1.0.2]"))
        self.assertLess(result.index("## [1.0.2]"), result.index("## [1.0.1]"))
        self.assertIn("- fix: old", result)

    def test_appends_when_no_anchor(self):
        text = "## [1.0.1] - 2026-10-01\n\n### Fixed\n- fix: old\n"
        result = insert_release(
            text, "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        self.assertLess(result.index("## [1.0.1]"), result.index("## [1.0.2]"))
        self.assertIn("- fix: old", result)

    def test_reinsert_same_version_is_idempotent(self):
        first = insert_release(
            "", "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        second = insert_release(
            first, "1.0.2", "2026-10-20", "### Fixed\n- fix: later", None
        )
        self.assertEqual(second.count("## [1.0.2]"), 1)
        self.assertIn("- fix: later", second)
        self.assertNotIn("- feat: new", second)

    def test_compare_url_included_in_section(self):
        url = "https://example.com/compare/v1.0.1...v1.0.2"
        result = insert_release("", "1.0.2", "2026-10-20", "### Added\n- feat: new", url)
        self.assertIn(f"**Full Changelog**: {url}", result)

    def test_no_compare_link_when_absent(self):
        result = insert_release(
            "", "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        self.assertNotIn("Full Changelog", result)

    def test_unreleased_anchor_must_be_at_line_start(self):
        text = (
            "Mencionar ## [Unreleased] en mitad de frase.\n\n"
            "# Changelog\n\n"
            "## [1.0.1] - 2026-10-01\n\n### Fixed\n- fix: old\n"
        )
        result = insert_release(
            text, "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        # la mención en mitad de línea no parte el texto
        self.assertEqual(
            result.splitlines()[0], "Mencionar ## [Unreleased] en mitad de frase."
        )
        # el ancla real es el título de línea completa
        self.assertLess(result.index("# Changelog"), result.index("## [1.0.2]"))
        self.assertLess(result.index("## [1.0.2]"), result.index("## [1.0.1]"))

    def test_title_anchor_must_be_at_line_start(self):
        text = "Intro con # Changelog incrustado.\n\n## [1.0.1] - 2026-10-01\n"
        result = insert_release(
            text, "1.0.2", "2026-10-20", "### Added\n- feat: new", None
        )
        self.assertEqual(result.splitlines()[0], "Intro con # Changelog incrustado.")
        # sin ancla de línea se añade al final, sin partir la introducción
        self.assertLess(result.index("## [1.0.1]"), result.index("## [1.0.2]"))


class CliTest(unittest.TestCase):
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
        (repo / "README.md").write_text("hola\n")
        self._git(repo, "add", "README.md")
        self._git(repo, "commit", "--quiet", "-m", "chore: init")
        self._git(repo, "tag", "v1.0.1")
        (repo / "README.md").write_text("hola mundo\n")
        self._git(repo, "add", "README.md")
        self._git(repo, "commit", "--quiet", "-m", "feat: nueva cosa")
        return repo

    def _run_main(self, argv):
        from update_changelog import main

        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_cli_writes_changelog_and_prints_body(self):
        repo = self._init_repo()
        code, out, err = self._run_main(
            [
                "--version",
                "1.0.2",
                "--since",
                "v1.0.1",
                "--repo",
                str(repo),
                "--date",
                "2026-10-20",
            ]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out, "### Added\n- feat: nueva cosa\n")
        changelog = (repo / "CHANGELOG.md").read_text()
        self.assertTrue(changelog.startswith("# Changelog\n\n## [Unreleased]\n\n"))
        self.assertIn("## [1.0.2] - 2026-10-20", changelog)
        self.assertIn("changelog actualizado", err)

    def test_cli_dry_run_writes_nothing(self):
        repo = self._init_repo()
        original = "# Changelog\n\n## [Unreleased]\n\n## [1.0.1] - 2026-10-01\n"
        (repo / "CHANGELOG.md").write_text(original)
        code, out, err = self._run_main(
            [
                "--version",
                "1.0.2",
                "--since",
                "v1.0.1",
                "--repo",
                str(repo),
                "--date",
                "2026-10-20",
                "--dry-run",
            ]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out, "### Added\n- feat: nueva cosa\n")
        self.assertEqual((repo / "CHANGELOG.md").read_text(), original)
        self.assertTrue(err.startswith("# Changelog\n\n## [Unreleased]\n\n"))
        self.assertIn("## [1.0.2] - 2026-10-20", err)

    def test_cli_rerun_is_idempotent(self):
        repo = self._init_repo()
        argv = [
            "--version",
            "1.0.2",
            "--since",
            "v1.0.1",
            "--repo",
            str(repo),
            "--date",
            "2026-10-20",
        ]
        code1, _, _ = self._run_main(argv)
        code2, _, _ = self._run_main(argv)
        self.assertEqual((code1, code2), (0, 0))
        changelog = (repo / "CHANGELOG.md").read_text()
        self.assertEqual(changelog.count("## [1.0.2]"), 1)
        self.assertIn("- feat: nueva cosa", changelog)

    def test_cli_compare_url_in_notes(self):
        repo = self._init_repo()
        url = "https://example.com/compare/v1.0.1...v1.0.2"
        code, out, _ = self._run_main(
            [
                "--version",
                "1.0.2",
                "--since",
                "v1.0.1",
                "--repo",
                str(repo),
                "--date",
                "2026-10-20",
                "--compare-url",
                url,
            ]
        )
        self.assertEqual(code, 0)
        self.assertIn(f"**Full Changelog**: {url}", out)

    def test_cli_missing_since_tag_fails(self):
        repo = self._init_repo()
        code, out, err = self._run_main(
            ["--version", "1.0.2", "--since", "v9.9.9", "--repo", str(repo)]
        )
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("error:", err)


if __name__ == "__main__":
    unittest.main()
