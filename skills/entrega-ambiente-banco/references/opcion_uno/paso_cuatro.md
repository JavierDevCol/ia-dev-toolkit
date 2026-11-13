# Opción 1 · Paso 4 — Prechequeos

4. **Prechequeos (bloqueantes):** ninguno de estos debe existir en `origin`:
   ```bash
   git ls-remote --tags origin "refs/tags/vX.Y.Z"
   git ls-remote --heads origin "release/vX.Y.Z"
   ```
   Cualquiera retorna algo → **detener**: la versión ya se publicó (o se intentó) y **no se reutiliza** — volver a calcular la siguiente con la Regla 2. Nunca borrar, mover ni sobrescribir un tag o una rama `release/`.

---

**Siguiente:** solo si **ninguna** de las dos consultas retorna algo → cargar `paso_cinco.md`. Si alguna retorna algo → detener; no cargar ningún paso más.
