# Opción 2b · Paso 3 — Recibir y validar el fix

3. **Recibir y validar el fix** — la skill **no implementa** la corrección; crea `hotfix/vX.Y.Z` **solo en local** (el push es el paso 5):

   | Origen del fix | Qué hacer |
   |---|---|
   | **(a)** Rama `fix/<desc>` | Validar que nace de `vBASE`: `git merge-base <rama_fix> vBASE` (`<rama_fix>` = `fix/<desc>` local u `origin/fix/<desc>`) debe ser igual a `git rev-list -n 1 vBASE`. Si no → **detener**: la rama no nace del tag base. Si sí: `git switch -c hotfix/vX.Y.Z <rama_fix>` (mismo commit, sin copiar nada). |
   | **(b)** Commits ya en develop | `git switch -c hotfix/vX.Y.Z vBASE` y `git cherry-pick -x <sha1> [<sha2> …]`. **Conflicto → `git cherry-pick --abort`, borrar la rama local y detener**: el conflicto se resuelve fuera de la skill (rama `fix/<desc>`, modo **a**). |
   | **(c)** Aún no hay fix | **Detener** y mostrar el comando para empezarlo: `git switch -c fix/<desc> vBASE`. Al volver con el fix revisado, retomar desde este paso. |

   `<sha>` = `git rev-parse HEAD` de `hotfix/vX.Y.Z`. Los pasos 4, 5 y 6 lo usan.

---

**Siguiente:** solo con `hotfix/vX.Y.Z` creada en local y `<sha>` fijado → cargar `paso_cuatro.md`. Detener → no cargar ningún paso más.
