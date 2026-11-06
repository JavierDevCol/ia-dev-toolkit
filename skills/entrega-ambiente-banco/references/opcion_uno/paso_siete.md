# Opción 1 · Paso 7 — Crear los 4 PR en borrador

7. **Crear los 4 PR en BORRADOR** (✋ OK del usuario), uno por ambiente, con el comando listo para copiar:
   ```
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia des con título exacto "Release vX.Y.Z → DES"
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia pru con título exacto "Release vX.Y.Z → PRU"
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia prepro con título exacto "Release vX.Y.Z → PRE"
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia main con título exacto "Release vX.Y.Z → PRO"
   ```
   ("título exacto": no reescribirlo a Conventional Commits). Descripción de cada PR: versión, tag `vX.Y.Z`, imagen `{nombre_ms}:X.Y.Z`, enlace a `release-notes.md` y la instrucción "**Completar con merge commit (sin squash), en orden DES → PRU → PRE → PRO**". Guardar los 4 ID y URL para el resumen.
   **Los PR quedan en borrador: CEIBA no los publica.** El banco los publica y les da el manejo que requiera (revisores, orden, aprobación). Es esperado que, al publicarlos, los PR hacia `pru`, `prepro` y `main` muestren la validación de orden en rojo hasta que exista el tag `vX.Y.Z-{AMB}` del ambiente anterior — no es un error de la entrega.

---

**Siguiente:** solo con los 4 PR creados en borrador y sus ID/URL guardados → cargar `paso_ocho.md`. Si falla la creación de alguno → detener y reportar cuáles se crearon; no cargar ningún paso más.
