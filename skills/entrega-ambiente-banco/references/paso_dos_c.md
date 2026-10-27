# Paso 2c — ajuste RC post-entrega en DES (Opción 2c)

**Cuándo:** El banco pidió ajustes sobre un release activo en DES (ciclo RC).

**Referencias:** `references/flujo-rc.sh` (flujo bash completo)

**Inputs (pedir/validar antes de empezar):**
- Versión activa `vX.Y.Z`, descripción del ajuste.
- Número de RCs existentes → `git ls-remote --tags origin 'refs/tags/vX.Y.Z-rc.*'` → `N = máximo(rc) + 1`.

**Outputs** (en `{documentacion_sac_path}/entrega_release/{nombre_repo}/vX.Y.Z/`): `resumen-entrega_rc_vX.Y.Z-rc.N.txt` + rama `release/vX.Y.Z-rc.N` publicada para el PR del banco. **No** se regeneran release notes (Regla 5).

**Confirmaciones del usuario:** ✋ versión y descripción antes del paso 2 · ✋ OK para publicar la rama RC · ✋ validación del fix en DEVELOP antes del back-merge.

1. **Validar la rama base:**
   ```bash
   git fetch origin
   git branch -a | grep release/vX.Y.Z
   ```
   Vacío → **detener**: `release/vX.Y.Z` no existe, este no es el flujo 2c (reevaluar Opción 1 u 2b). `release/vX.Y.Z-rc.N` ya existe (local o en `origin`) → incrementar N o eliminar la efímera previa, previa confirmación del usuario.

2. **Aplicar el fix sobre `release/vX.Y.Z`** (la rama base sigue viva durante todo el ciclo):
   ```bash
   git checkout release/vX.Y.Z && git pull origin release/vX.Y.Z
   git add <archivos> && git commit -m "fix: <descripción del ajuste>"
   git push origin release/vX.Y.Z
   ```

3. **env-config-audit:** `@env-config-audit sobre el diff origin/des..release/vX.Y.Z` (diff de esta fase — `SKILL.md` → Skills sugeridas), antes del back-merge. Al completarla, marcar `config-entorno` según la INSTRUCCIÓN DE USO de `references/checklist-entrega.txt`.

4. **Crear y publicar la rama RC efímera:**
   ```bash
   git checkout -b release/vX.Y.Z-rc.N release/vX.Y.Z
   git push origin release/vX.Y.Z-rc.N
   ```

5. **Gate — validar el fix en DEVELOP:** el pipeline despliega la RC en DEVELOP; validar que el fix funciona correctamente (salvo fixes triviales: typo/config que no afectan lógica de negocio). **Sin validación no hay back-merge**.

6. **Back-merge mediante PR** `release/vX.Y.Z → develop` (develop está protegida: PR con ≥1 approval, sin push directo), con descripción del fix y link al WI/bug original. **Conflictos → detener y reportar**, nunca forzar.

7. **Resumen:** rellenar la **variante RC** de `references/resumen-entrega.txt` (sustituir todos los placeholders), mostrarla y guardarla como `resumen-entrega_rc_vX.Y.Z-rc.N.txt` en `{documentacion_sac_path}/entrega_release/{nombre_repo}/vX.Y.Z/`.

8. **Post-entrega (tras el merge del banco):** cuando el banco confirme que mergeó el PR de la RC a `des`, eliminar la rama efímera — `git push origin --delete release/vX.Y.Z-rc.N` y `git branch -d release/vX.Y.Z-rc.N`. La rama base `release/vX.Y.Z` **sigue viva** hasta la aprobación final del banco (tag `vX.Y.Z` y back-merge final a develop).

**Release notes:** no se regeneran en un RC — ver Regla 5 de `SKILL.md`. El ajuste se documenta en el `resumen-entrega_rc`.
