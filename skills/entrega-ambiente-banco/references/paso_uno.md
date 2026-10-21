# Paso 1 — Entregar release desde DEVELOP (Opción 1)

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado.

**Referencias:** `references/checklist-entrega.txt`

**Inputs (pedir/validar antes de empezar):**
- Versión de la entrega `vX.Y.Z` — validar formato semver (Regla 2). Si `vX.Y.Z` ya existe como tag → ver paso 5.
- `nombre_repo` del repositorio que se entrega.

**Outputs** (en `{output_folder}/entrega_release/{nombre_repo}/{version}/`):
- `release-notes.md`, `CHECKLIST_ENTREGA_vX.Y.Z.txt`, `RESUMEN_ENTREGA_release ({nombre_repo}).txt`
- Rama `release/vX.Y.Z` publicada en `origin`. El tag `vX.Y.Z` **no** lo creamos en CEIBA — lo genera el banco en DES (Regla 6).

**Confirmaciones del usuario:** ✋ versión antes del paso 5 · ✋ OK para el `push` de la rama · ✋ cierre del checklist como estado real.

1. **Verificar develop:**
   ```bash
   git fetch origin
   git log origin/develop -1 --oneline
   ```
   Verificar que el pipeline de develop está OK, con el comando listo para copiar:
   ```
   @ado-pipeline-analyzer build latest del pipeline <nombre_pipeline> en rama develop
   ```
   (también vale pegar la URL del build de ADO). **Pipeline rojo o no verificable → detener y reportar al usuario antes de continuar** (gate bloqueante; nunca asumir OK). Las métricas de calidad del checklist (cobertura/DAST/Sonar) siguen siendo `[⚠]` no bloqueantes.

2. **Estado de promoción de la versión anterior (informativo — nunca bloquea):** hallar el tag anterior más reciente (`vPREV`, mismo hallazgo que reutiliza el paso 3):
   ```bash
   git tag -l 'v*' | grep -v -- '-rc' | sort -V | tail -1   # excluye tags rc.N del banco
   ```
   y listar su promoción con `git ls-remote --tags origin 'refs/tags/vPREV*'`. Mostrar cuáles existen y cuáles faltan entre `vPREV` (DES), `vPREV-pru`, `vPREV-prepro`, `vPREV-pro`, y continuar siempre — el ritmo de promoción del banco no frena esta entrega (ver Common Mistakes en `SKILL.md`).

3. **Release notes:** `git checkout develop && git pull`. Con `vPREV` del paso 2:
   - Con tag previo: `git log vPREV..HEAD --oneline --no-merges`
   - Primer release (sin tag previo): `git log --oneline --no-merges` (histórico completo) y advertir "primer release"

   Escribir el resultado directamente en el artefacto (crear la carpeta antes):
   ```bash
   mkdir -p "{output_folder}/entrega_release/{nombre_repo}/{version}"
   git log vPREV..HEAD --oneline --no-merges > "{output_folder}/entrega_release/{nombre_repo}/{version}/release-notes.md"
   ```
   Se generan **desde cero** en cada release (Regla 5).

4. **Versión en artefactos:** identificar los artefactos del repo que declaran la versión (p. ej. `pom.xml`, `package.json`, archivos de config) y actualizarlos a `vX.Y.Z`, **respetando el formato que ya usa cada artefacto** (`2.3.1` sin `v` en `pom.xml`/`package.json`, salvo que el artefacto lo lleve). Commitear sobre develop y **publicarlo antes de crear la rama**:
   ```bash
   git add <artefactos de versión>
   git commit -m "chore: versión vX.Y.Z para release"
   git push origin develop
   ```
   El `push` es obligatorio: sin él, `origin/develop` queda detrás y el paso 6 fallaría en falso. Verificar que el commit queda en `origin/develop`; si el repo no declara versión en artefactos, dejar constancia en el resumen.

5. **Crear/actualizar `release/vX.Y.Z`:**
   - **Tag existente:** `git ls-remote --tags origin 'refs/tags/vX.Y.Z'` retorna algo → **detener** y preguntar al usuario (¿versión ya entregada? → bump de MINOR/PATCH o abortar). **Nunca sobrescribir ni mover un tag.**
   - **CASO A — la rama NO existe** (`git branch -a | grep release/vX.Y.Z` vacío) — crearla desde develop:
     ```bash
     git checkout develop && git pull
     git checkout -b release/vX.Y.Z
     git push origin release/vX.Y.Z
     ```
   - **CASO B — la rama YA existe** — actualizarla con fast-forward:
     ```bash
     git checkout release/vX.Y.Z
     git pull origin release/vX.Y.Z
     git merge --ff-only develop
     git push origin release/vX.Y.Z
     ```
   - **`--ff-only` falla → detener**, no forzar el merge, remitir a la Opción 2c (ajuste RC) — Regla 8.

6. **Validar mismo commit (Regla de oro):** `git fetch origin` y luego `git rev-parse origin/develop` vs `git rev-parse origin/release/vX.Y.Z` — deben coincidir. Si difieren: **detener**, no forzar nada, abrir un ajuste RC (Opción 2c) y reportar al usuario.

7. **Checklist de entrega** (`references/checklist-entrega.txt`):
   a. Mostrarlo **sustituyendo `vX.Y.Z` por la versión real** en todas las líneas (incluida la de `env-config-audit`) antes de mostrarlo — nunca dejar el placeholder literal. Los items ⚠️ requieren skills externas (ver tabla "Skills complementarias" en `SKILL.md`).
   b. **Marcar los ítems a medida que se ejecuten esas skills**, aplicando la INSTRUCCIÓN DE USO del propio checklist sobre la copia de entrega (nunca sobre la plantilla). Guardar la copia marcada en `{output_folder}/entrega_release/{nombre_repo}/{version}/CHECKLIST_ENTREGA_vX.Y.Z.txt`; debe reflejar el estado real al cierre.

   Al sugerir cada skill, mostrar su comando exacto listo para copiar (con la versión real ya sustituida):
   ```
   @env-config-audit sobre el diff origin/des..release/vX.Y.Z
   @ado-pipeline-analyzer build latest del pipeline <nombre_pipeline> en rama release/vX.Y.Z
   @analizar-seguridad scope=project sobre release/vX.Y.Z
   @analizar-calidad-codigo scope=project sobre release/vX.Y.Z
   ```

8. **Resumen final y notificación:** mostrar y guardar `RESUMEN_ENTREGA_release ({nombre_repo}).txt` en `{output_folder}/entrega_release/{nombre_repo}/{version}/`. Contenido mínimo: versión `vX.Y.Z`, commit de entrega (`git rev-parse`), release notes generadas, estado del checklist (qué `[⚠]` quedan pendientes y por qué), artefactos entregados y bloque de firma (`SKILL.md` → Configuración global). Avisar al banco que la entrega está lista — el PR a `des` lo crea el banco (Regla 6).
