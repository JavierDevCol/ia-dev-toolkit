# Paso 2b — hotfix post-entrega (Opción 2b)

**Cuándo:** Bug detectado en PRU/PREPRO/PRO sobre una versión ya entregada.

**Referencias:** `references/flujo-hotfix.sh` (flujo bash completo)

**Inputs (pedir/validar antes de empezar):**
- Ambiente afectado → sufijo de tag: PRU→`-pru`, PREPRO→`-prepro`, PRO→`-pro`.
- Versión afectada `vX.Y.Z` (semver, Regla 2) y descripción del bug.

**Outputs** (en `{documentacion_sac_path}/entrega_release/{nombre_repo}/vX.Y.Z+1/`): `release-notes.md`, `resumen-entrega_hotfix_vX.Y.Z+1.txt` y rama `release/vX.Y.Z+1` en `origin`. El tag lo crea el banco (Regla 6).

**Confirmaciones del usuario:** ✋ versión y ambiente antes del paso 1 · ✋ OK para crear el PR a develop · ✋ cierre del checklist como estado real.

1. **Validar el tag del ambiente afectado:**
   ```bash
   git fetch origin --tags
   git ls-remote --tags origin 'refs/tags/vX.Y.Z-<sufijo>'
   ```
   Vacío → **detener**: la versión no existe en ese ambiente (¿versión mal reportada? ¿ambiente desactualizado?) y preguntar al usuario.

2. **Estado de promoción de `vX.Y.Z` (informativo — nunca bloquea):** mismo chequeo que Opción 1 paso 2 (`vX.Y.Z`, `-pru`, `-prepro`, `-pro`). Mostrar y continuar (SKILL.md → Common Mistakes).

3. **Crear rama hotfix desde el tag del ambiente afectado y aplicar el fix:**
   ```bash
   git checkout -b hotfix/<nombre> vX.Y.Z-<sufijo>
   git add <archivos> && git commit -m "fix: <descripción del ajuste>"
   ```
   `hotfix/<nombre>` ya existe (local o en `origin`) → **detener** y preguntar (reutilizar el intento previo o elegir otro nombre). Nunca sobrescribir ni usar `checkout -B`. La rama se crea **desde el tag del ambiente afectado**, no desde develop.

4. **Verificar que develop necesita el fix** (precondition del merge limpio): `git log develop --oneline | head -10`. Si develop ya tiene el fix, reportarlo y reevaluar el flujo.

5. **env-config-audit:** `@env-config-audit sobre el diff develop..hotfix/<nombre>` (diff de esta fase — `SKILL.md` → Skills sugeridas), antes del PR. Al completarla, marcar `config-entorno` según la INSTRUCCIÓN DE USO de `references/checklist-entrega.txt`.

6. **Merge a develop PRIMERO, mediante PR** (develop está protegida: PR con ≥1 approval, sin push directo):
   - Crear PR `hotfix/<nombre> → develop` con descripción y link al WI/bug original.
   - **Conflictos en el PR → detener y reportar**; nunca forzar el merge hacia develop.
   - Tras el merge, verificar que develop contiene el fix.

7. **Nuevo release `vX.Y.Z+1`** (incremento de PATCH — fix→PATCH, coherente con `@auto-versioning`):
   ```bash
   git checkout develop && git pull
   git checkout -b release/vX.Y.Z+1
   git push origin release/vX.Y.Z+1
   ```
   **Regla de oro:** `git fetch origin` y luego `git rev-parse origin/develop` vs `git rev-parse origin/release/vX.Y.Z+1` deben coincidir. Si difieren → **detener**, abrir un ajuste RC (Opción 2c).

8. **Release notes desde cero** para `vX.Y.Z+1` (Regla 5):
   ```bash
   mkdir -p "{documentacion_sac_path}/entrega_release/{nombre_repo}/vX.Y.Z+1"
   git log v<X.Y.Z>..HEAD --oneline --no-merges > "{documentacion_sac_path}/entrega_release/{nombre_repo}/vX.Y.Z+1/release-notes.md"
   ```

9. **Limpiar la rama hotfix** (tras el merge del PR): `git branch -d hotfix/<nombre>` y `git push origin --delete hotfix/<nombre>`.

10. **Resumen y notificación:** rellenar la **variante HOTFIX** de `references/resumen-entrega.txt` (sustituir todos los placeholders), mostrarla y guardarla como `resumen-entrega_hotfix_vX.Y.Z+1.txt` en `{documentacion_sac_path}/entrega_release/{nombre_repo}/vX.Y.Z+1/`.
