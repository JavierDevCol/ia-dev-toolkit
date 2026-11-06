# Opción 2b · Paso 7 — Crear los 4 PR en borrador

7. **Crear los 4 PR en BORRADOR** (✋ OK del usuario), uno por ambiente:
   ```
   @ado-pr-creator crear PR en borrador (isDraft=true) de hotfix/vX.Y.Z hacia des con título exacto "Hotfix vX.Y.Z → DES"
   @ado-pr-creator crear PR en borrador (isDraft=true) de hotfix/vX.Y.Z hacia pru con título exacto "Hotfix vX.Y.Z → PRU"
   @ado-pr-creator crear PR en borrador (isDraft=true) de hotfix/vX.Y.Z hacia prepro con título exacto "Hotfix vX.Y.Z → PRE"
   @ado-pr-creator crear PR en borrador (isDraft=true) de hotfix/vX.Y.Z hacia main con título exacto "Hotfix vX.Y.Z → PRO"
   ```
   ("título exacto": no reescribirlo a Conventional Commits). Descripción de cada PR: versión, base `vBASE`, bug/WI, tag `vX.Y.Z`, imagen `{nombre_ms}:X.Y.Z`, enlace a `release-notes.md` y la instrucción "**Completar con merge commit (sin squash), en orden DES → PRU → PRE → PRO**". Guardar los 4 ID y URL.

   **Aviso de ambiente que baja de versión** (con la tabla del paso 1): por cada ambiente cuya versión actual sea **mayor** que `vX.Y.Z`, agregar a la descripción de su PR y al resumen: "Este PR revierte en `<rama>` lo entregado después de `vBASE` (`<versiones>`); el control de árbol lo permite y la siguiente versión desde develop lo vuelve a llevar."

   **Los PR quedan en borrador: CEIBA no los publica.** El banco los publica; si el hotfix es urgente, puede completarlos de forma consecutiva.

---

**Siguiente:** solo con los 4 PR creados en borrador y sus ID/URL guardados → cargar `paso_ocho.md`. Si falla la creación de alguno → detener y reportar cuáles se crearon; no cargar ningún paso más.
