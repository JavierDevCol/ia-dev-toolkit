# Opción 2b · Paso 10 — Checklist de entrega

10. **Checklist de entrega** (`references/checklist-entrega.txt`):
    a. Mostrarlo **sustituyendo `vX.Y.Z` por la versión del hotfix** y `release/vX.Y.Z` por `hotfix/vX.Y.Z` en todas las líneas — nunca dejar el placeholder literal. El primer ítem queda "hotfix/vX.Y.Z creada sobre `<sha>` (fix sobre `vBASE`) y bloqueada".
    b. **Marcar de inmediato lo que ya tiene resultado**, sin volver a ejecutar nada: los ítems de flujo (`[ ]`) de los pasos 4 a 9; **pruebas, cobertura y SonarQube** con lo guardado en el paso 6; **DAST = `[N/A]`** (el hotfix no pasa por el pipeline de develop antes de entregarse).
    c. **Marcar los ítems restantes a medida que se ejecuten sus skills**, aplicando la INSTRUCCIÓN DE USO del propio checklist sobre la copia de entrega (nunca sobre la plantilla). Guardar la copia en `{output_documentacion}/entrega_release/{nombre_repo}/vX.Y.Z/checklist-entrega_vX.Y.Z.txt`.

    Solo quedan por ejecutar estas skills (comandos listos para copiar):
    ```
    @env-config-audit sobre el diff origin/des..vX.Y.Z
    @env-config-audit sobre el diff origin/pru..vX.Y.Z
    @env-config-audit sobre el diff origin/prepro..vX.Y.Z
    @env-config-audit sobre el diff origin/main..vX.Y.Z
    @sac-analizar-seguridad scope=commits sobre hotfix/vX.Y.Z
    @sac-analizar-calidad-codigo scope=commits sobre hotfix/vX.Y.Z
    ```

---

**Siguiente:** con la copia del checklist guardada con el estado real (✋ cierre del usuario) → cargar `paso_once.md`.
