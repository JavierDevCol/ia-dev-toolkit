# Opción 1 · Paso 2 — Versión anterior y versión de la entrega

2. **Versión anterior (`vPREV`) y versión de la entrega (`vX.Y.Z`):**

   a. **`vPREV`** = último tag de versión en `origin`, descartando los tags de despliegue `-DES/-PRU/-PRE/-PRO` (mismo comando que la Regla 2 de `SKILL.md`). Lo usa el paso 3:
      ```bash
      git ls-remote --tags origin | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
      ```
      Sin resultado → no hay `vPREV`: primer release.

   b. **Estado de promoción de `vPREV` (informativo — nunca bloquea):** `git ls-remote --tags origin 'refs/tags/vPREV-*'`. Mostrar cuáles existen y cuáles faltan entre `vPREV-DES`, `vPREV-PRU`, `vPREV-PRE`, `vPREV-PRO` — el ritmo de promoción del banco no frena esta entrega (ver Common Mistakes en `SKILL.md`).

   c. **Proponer `vX.Y.Z`** con la Regla 2: siguiente MINOR de `vPREV` (`vA.B.C` → `vA.(B+1).0`); MAJOR solo si el usuario indica ruptura de compatibilidad; primer release → `v1.0.0`. Si el usuario ya trae la versión, solo validar el formato semver y que sea mayor que `vPREV`.

   d. ✋ **Confirmar `vX.Y.Z` con el usuario.** Desde aquí `{version}` = `vX.Y.Z` en todas las rutas y comandos.

---

**Siguiente:** solo con `vX.Y.Z` confirmada por el usuario → cargar `paso_tres.md`. Pregunta ✋ abierta → esperar la respuesta sin cargar nada.
