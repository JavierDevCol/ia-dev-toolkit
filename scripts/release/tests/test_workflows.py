"""Contrato de los workflows de release — checks con ``re`` sobre el YAML.

Sin dependencias: solo stdlib. El "parser" es lectura de texto + regex, tal y
como pide el plan (no se valida el YAML completo, solo el contrato que nos
importa: pinning por SHA, token de escritura, tag ``-TEST`` móvil, sin releases).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
RELEASE_TEST = WORKFLOWS_DIR / "release-test.yml"

# Literal que el workflow usa para validar el tag antes de moverlo (R1).
TAG_GUARD = "^v[0-9]+\\.[0-9]+\\.[0-9]+-TEST$"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ReleaseTestWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yaml = read(RELEASE_TEST)

    def test_release_test_workflow_pins_checkout_by_sha(self):
        self.assertRegex(self.yaml, r"actions/checkout@[0-9a-f]{40}")

    def test_release_test_never_creates_releases(self):
        self.assertNotIn("gh release", self.yaml)

    def test_workflows_use_release_token(self):
        paths = sorted(WORKFLOWS_DIR.glob("release-*.yml"))
        self.assertTrue(paths, "no hay workflows de release")
        for path in paths:
            with self.subTest(path.name):
                text = read(path)
                self.assertIn("secrets.RELEASE_TOKEN", text)
                self.assertNotIn("permissions: contents: write", text)

    def test_release_test_permissions_are_read_only(self):
        self.assertRegex(self.yaml, r"(?m)^permissions:\n  contents: read$")

    def test_release_test_triggers_on_develop_and_manual_dry_run(self):
        self.assertIn("branches: [develop]", self.yaml)
        self.assertIn("workflow_dispatch", self.yaml)
        self.assertRegex(self.yaml, r"dry_run:[\s\S]{0,200}?type: boolean")

    def test_release_test_has_anti_loop_guard(self):
        self.assertIn("if: github.actor != 'github-actions[bot]'", self.yaml)

    def test_release_test_uses_locked_concurrency(self):
        self.assertRegex(
            self.yaml,
            r"(?m)^concurrency:\n  group: release-test\n  cancel-in-progress: false$",
        )

    def test_release_test_only_moves_test_tags(self):
        self.assertIn(TAG_GUARD, self.yaml)
        self.assertNotIn("--force", self.yaml)

    def test_release_test_exit_3_ends_with_notice(self):
        self.assertIn("-eq 3", self.yaml)
        self.assertIn("::notice::", self.yaml)

    def test_release_test_step_order(self):
        markers = [
            "actions/checkout@",
            "next_version.py --channel test --json",
            "::notice::",
            "Would move",
            'git push origin ":refs/tags/',
            "git tag -a",
            'git push origin "refs/tags/',
        ]
        positions = [self.yaml.index(marker) for marker in markers]
        self.assertEqual(
            positions,
            sorted(positions),
            "el orden de pasos no es checkout -> CLI -> notice -> dry_run -> "
            "borrar tag remoto -> tag anotado -> push del tag",
        )

    def test_release_test_move_step_skips_on_dry_run(self):
        self.assertIn("inputs.dry_run == true", self.yaml)
        self.assertIn("inputs.dry_run != true", self.yaml)

    def test_release_test_run_blocks_are_well_formed(self):
        # Un bloque `run: |` termina en cuanto aparece una línea con sangría
        # menor o igual que sea YAML (clave, item o comentario). Una línea de
        # shell a sangría menor cortaría el bloque y rompería el archivo.
        block_indent = None
        yaml_line = re.compile(r"^\s*(?:(?:- )?[A-Za-z_][\w.-]*:|#)")
        for lineno, line in enumerate(self.yaml.splitlines(), start=1):
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip())
            if block_indent is not None:
                if indent > block_indent:
                    continue
                self.assertRegex(
                    line,
                    yaml_line,
                    f"línea {lineno} cierra el bloque run: | y no es YAML: {line!r}",
                )
                block_indent = None
            match = re.match(r"^( +)run: \|$", line)
            if match:
                block_indent = len(match.group(1))


if __name__ == "__main__":
    unittest.main()
