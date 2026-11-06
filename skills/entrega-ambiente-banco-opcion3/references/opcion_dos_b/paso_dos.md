# Opción 2b · Paso 2 — Versión del hotfix y prechequeos

2. **Versión del hotfix (`vX.Y.Z`) y prechequeos** — gate bloqueante:

   a. `vX.Y.Z` = PATCH+1 de `vBASE` (Regla 2): `vA.B.C` → `vA.B.(C+1)`.

   b. Ninguno de estos debe existir en `origin`:
      ```bash
      git ls-remote --tags origin "refs/tags/vX.Y.Z"
      git ls-remote --heads origin "hotfix/vX.Y.Z"
      ```
      Cualquiera retorna algo → **detener y reportar**: hay otro hotfix en curso o ya publicado sobre `vBASE`. El usuario decide (p. ej. tomar ese hotfix como nueva base). Nunca borrar, mover ni sobrescribir un tag o una rama `hotfix/`.

---

**Siguiente:** solo si **ninguna** consulta retorna algo → cargar `paso_tres.md`. Si alguna retorna algo → detener; no cargar ningún paso más.
