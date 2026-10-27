# Paso 1 — Entregar release desde DEVELOP (Opción 1)

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado.

**Referencias:** `references/checklist-entrega.txt`

**Inputs (pedir/validar antes de empezar):**
- Versión de la entrega `vX.Y.Z` — sugerirla con `@auto-versioning` (Regla 2) y validar formato semver. Si `vX.Y.Z` ya existe como tag → ver paso 5.
- `nombre_repo` del repositorio que se entrega.

**Outputs** (en `{documentacion_sac_path}/entrega_release/{nombre_repo}/{version}/`):
- `release-notes.md`, `checklist-entrega_vX.Y.Z.txt`, `resumen-entrega_release_vX.Y.Z.txt`
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
   mkdir -p "{documentacion_sac_path}/entrega_release/{nombre_repo}/{version}"
   git log vPREV..HEAD --oneline --no-merges > "{documentacion_sac_path}/entrega_release/{nombre_repo}/{version}/release-notes.md"
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
   b. **Marcar los ítems a medida que se ejecuten esas skills**, aplicando la INSTRUCCIÓN DE USO del propio checklist sobre la copia de entrega (nunca sobre la plantilla). Guardar la copia marcada en `{documentacion_sac_path}/entrega_release/{nombre_repo}/{version}/checklist-entrega_vX.Y.Z.txt`; debe reflejar el estado real al cierre.

   Al sugerir cada skill, mostrar su comando exacto listo para copiar (con la versión real ya sustituida):
   ```
   @env-config-audit sobre el diff origin/des..release/vX.Y.Z
   @ado-pipeline-analyzer build latest del pipeline <nombre_pipeline> en rama release/vX.Y.Z
   @analizar-seguridad scope=commits sobre release/vX.Y.Z
   @sac-analizar-calidad-codigo scope=commits sobre release/vX.Y.Z
   ```

8. **Resumen final y notificación:** rellenar la **variante RELEASE** de `references/resumen-entrega.txt` (sustituir todos los placeholders, nunca dejar literales), mostrarla y guardarla como `resumen-entrega_release_vX.Y.Z.txt` en `{documentacion_sac_path}/entrega_release/{nombre_repo}/{version}/`. La notificación al banco cierra el resumen — el PR a `des` lo crea el banco (Regla 6).
