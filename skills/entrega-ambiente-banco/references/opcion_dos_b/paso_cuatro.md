# Opción 2b · Paso 4 — Confirmar fix completo y release notes

4. **Confirmar que el fix está completo** — gate bloqueante. Después del push no se puede agregar nada: un commit posterior deja el HEAD sin el tag `vX.Y.Z` y la validación de origen rechaza los PR (otro ajuste = `vA.B.(C+2)`).

   a. **Mostrar el alcance** del hotfix:
      ```bash
      git log vBASE..<sha> --oneline --no-merges
      git diff vBASE..<sha> --stat
      ```
      Debe contener **solo** la corrección. Archivos o commits ajenos al bug → **detener y reportar**.

   b. **Release notes** desde cero (Regla 5):
      ```bash
      mkdir -p "{output_documentacion}/entrega_release/{nombre_repo}/vX.Y.Z"
      git log vBASE..<sha> --oneline --no-merges > "{output_documentacion}/entrega_release/{nombre_repo}/vX.Y.Z/release-notes.md"
      ```

   c. ✋ **Preguntar al usuario:** "¿El fix está completo y revisado? Tras el push no se puede agregar nada."

---

**Siguiente:** solo con la confirmación ✋ del usuario → cargar `paso_cinco.md`. Respuesta negativa → detener; el fix se completa fuera de la skill y se retoma desde el paso 3.
