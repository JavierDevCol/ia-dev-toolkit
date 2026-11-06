# Opción 2b · Paso 8 — PR hotfix → develop

8. **PR `hotfix/vX.Y.Z → develop`, activo** (✋ OK del usuario) — obligatorio: sin él, la validación de correcciones contenidas en develop bloquea la siguiente versión.
   ```
   @ado-pr-creator crear PR de hotfix/vX.Y.Z hacia develop titulado "fix: hotfix vX.Y.Z — <descripción del bug>"
   ```
   Descripción: bug/WI, base `vBASE`, versión `vX.Y.Z` y enlace a los 4 PR de ambientes. Lo aprueba y completa el equipo CEIBA (develop protegida, ≥1 approval).
   - **Origen (b)**, fix ya en develop: el PR puede quedar sin cambios de código; igual se crea para registrar la integración del tag.
   - **Conflictos** → reportar al usuario, nunca forzar el merge. Se resuelven en el PR.

   Guardar ID y URL para el resumen.

---

**Siguiente:** con el PR creado (o el conflicto reportado) → cargar `paso_nueve.md`. Si falla la creación → detener y reportar; no cargar ningún paso más.
