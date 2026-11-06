# Opción 1 · Paso 9 — Checklist de entrega

9. **Checklist de entrega** (`references/checklist-entrega.txt`):
   a. Mostrarlo **sustituyendo `vX.Y.Z` por la versión real** en todas las líneas antes de mostrarlo — nunca dejar el placeholder literal.
   b. **Marcar de inmediato los ítems que ya tienen resultado**, sin volver a ejecutar nada: los ítems de flujo (`[ ]`) de los pasos 3 a 8; **DAST** con lo guardado en el paso 1; **pruebas, cobertura y SonarQube** con lo guardado en el paso 6.
   c. **Marcar los ítems restantes a medida que se ejecuten sus skills**, aplicando la INSTRUCCIÓN DE USO del propio checklist sobre la copia de entrega (nunca sobre la plantilla). Guardar la copia marcada en `{output_documentacion}/entrega_release/{nombre_repo}/{version}/checklist-entrega_vX.Y.Z.txt`; debe reflejar el estado real al cierre.

   Solo quedan por ejecutar estas skills; mostrar su comando exacto listo para copiar (con la versión real ya sustituida). `@env-config-audit` va **una vez por ambiente**: cada PR muestra lo que entra a ese ambiente.
   ```
   @env-config-audit sobre el diff origin/des..vX.Y.Z
   @env-config-audit sobre el diff origin/pru..vX.Y.Z
   @env-config-audit sobre el diff origin/prepro..vX.Y.Z
   @env-config-audit sobre el diff origin/main..vX.Y.Z
   @sac-analizar-seguridad scope=commits sobre release/vX.Y.Z
   @sac-analizar-calidad-codigo scope=commits sobre release/vX.Y.Z
   ```

---

**Siguiente:** con la copia del checklist guardada con el estado real (✋ cierre del usuario) → cargar `paso_diez.md`.
