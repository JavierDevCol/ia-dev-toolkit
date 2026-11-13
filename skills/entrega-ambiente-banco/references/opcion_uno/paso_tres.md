# Opción 1 · Paso 3 — Release notes

3. **Release notes:** con `vPREV` del paso 2, escribir el resultado directamente en el artefacto (crear la carpeta antes):
   ```bash
   mkdir -p "{output_documentacion}/entrega_release/{nombre_repo}/{version}"
   git log vPREV..<sha> --oneline --no-merges > "{output_documentacion}/entrega_release/{nombre_repo}/{version}/release-notes.md"
   ```
   Primer release (sin `vPREV`): `git log <sha> --oneline --no-merges` y advertir "primer release". Se generan **desde cero** en cada versión (Regla 5).

---

**Siguiente:** con `release-notes.md` escrito → cargar `paso_cuatro.md`.
