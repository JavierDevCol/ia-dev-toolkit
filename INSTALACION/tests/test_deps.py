import os, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from diatlib import deps, paths


class ValidateDependenciesC1Test(unittest.TestCase):
    """Batería C1 (B13): subgrafo por seeds, requires vs warnings, mensaje educativo."""

    def setUp(self):
        self._home = os.environ.get("HOME")
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["HOME"] = self._tmp.name
        paths.get_cache_dir().mkdir(parents=True, exist_ok=True)
        paths.get_ref_file().write_text("v2.1.1", encoding="utf-8")   # get_ref() en el error

    def tearDown(self):
        os.environ["HOME"] = self._home
        self._tmp.cleanup()

    def catalog(self, **over):
        cat = {"skills": {"sac-ejecutar-plan", "validar-ca"},
               "workflows": set(), "agents": set(), "plugins": set(),
               "commands": set(), "tools": set()}
        cat.update(over)
        return cat

    def test_requires_ausente_aborta_con_ref_activa_y_bootstrap(self):     # B-07
        with self.assertRaises(deps.DependencyError) as cm:
            deps.validate_dependencies(self.catalog(skills={"sac-ejecutar-plan"}),
                                       seeds=[("skills", "sac-ejecutar-plan")])
        msg = str(cm.exception)
        self.assertIn("skills:validar-ca", msg)
        self.assertIn("ref activa: v2.1.1", msg)
        self.assertIn("re-ejecuta el bootstrap", msg)           # mensaje nuevo

    def test_requires_presente_sin_errores(self):
        warnings = deps.validate_dependencies(self.catalog(),
                                              seeds=[("skills", "sac-ejecutar-plan")])
        self.assertEqual(warnings, [])

    def test_seed_ausente_es_warning_no_error(self):
        warnings = deps.validate_dependencies(self.catalog(),
                                              seeds=[("skills", "no-existe")])
        self.assertTrue(any("no está en esta ref" in w for w in warnings))

    def test_opcional_ausente_es_warning(self):
        graph = {"skills": {"a": {"requires": {},
                                  "optional": {"skills": ["opt-no"]}}}}
        warnings = deps.validate_dependencies({"skills": {"a"}}, seeds=[("skills", "a")],
                                              dependencies=graph)
        self.assertEqual(len(warnings), 1)
        self.assertIn("opcional", warnings[0])

    def test_subgrafo_no_alcanzado_no_bloquea(self):                        # C1 núcleo
        # workflows:definir-vision-producto exige workflow-sac ausente del catálogo,
        # pero NO es alcanzable desde las seeds -> no bloquea.
        warnings = deps.validate_dependencies(self.catalog(),
                                              seeds=[("skills", "sac-ejecutar-plan")],
                                              dependencies=deps.for_platform(".opencode"))
        self.assertEqual(warnings, [])

    def test_sin_seeds_valida_grafo_completo(self):
        with self.assertRaises(deps.DependencyError):
            deps.validate_dependencies(self.catalog(skills={"sac-ejecutar-plan"}), seeds=None,
                                       dependencies=deps.for_platform(".opencode"))

    def test_for_platform_opencode_requiere_plugin_y_command(self):
        _, by = deps.resolve_closure([("workflows", "definir-vision-producto")], deps.for_platform(".opencode"))
        self.assertEqual(by.get("plugins"), ["workflow-sac"]); self.assertEqual(by.get("commands"), ["workflow-sac"])
        self.assertNotIn("skills", by)

    def test_for_platform_claude_requiere_skill(self):
        _, by = deps.resolve_closure([("workflows", "demo-delegacion")], deps.for_platform(".claude"))
        self.assertEqual(by.get("skills"), ["exc-workflow-sac"]); self.assertEqual(by.get("agents"), ["PO"])
        self.assertNotIn("plugins", by)

    def test_for_platform_no_muta_el_grafo_base(self):
        deps.for_platform(".claude")
        self.assertNotIn("skills", deps.COMPONENT_DEPENDENCIES["workflows"]["definir-vision-producto"]["requires"])

    def test_tipo_no_recursivo_ausente_es_warning(self):
        warnings = deps.validate_dependencies(self.catalog(), seeds=[("tools", "tool-x")])
        self.assertTrue(any("no está en esta ref" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
