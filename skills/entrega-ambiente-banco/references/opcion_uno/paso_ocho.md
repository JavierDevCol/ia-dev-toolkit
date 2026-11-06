# Opción 1 · Paso 8 — PR de versiones anteriores

8. **PR abiertos de versiones anteriores (solo listar):** buscar con el MCP de ADO, `ado_repo_pull_request` (list) sobre `{nombre_repo}`, los PR con estado `active` (incluye los borradores, `isDraft = true`) y `targetRefName` en `refs/heads/des`, `refs/heads/pru`, `refs/heads/prepro` o `refs/heads/main`. Quedarse con los que tengan `sourceRefName` `refs/heads/release/v*` u `refs/heads/hotfix/v*`, **excluyendo** los 4 recién creados de `release/vX.Y.Z`. Mostrar por cada uno: origen → destino, versión, estado y URL, con la indicación de **abandonarlos a mano** (la versión `vX.Y.Z` los reemplaza). La skill **no** los abandona. Sin PR abiertos → continuar.

---

**Siguiente:** este paso nunca bloquea → cargar `paso_nueve.md`.
