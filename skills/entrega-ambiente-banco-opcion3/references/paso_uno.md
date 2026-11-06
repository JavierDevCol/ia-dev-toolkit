# Paso 1 — Entregar versión desde DEVELOP (Opción 1)

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado.

**Referencias:** `references/checklist-entrega.txt`

**Inputs (pedir/validar antes de empezar):**
- Versión de la entrega `vX.Y.Z` — calcularla con la Regla 2 (siguiente MINOR del último tag de versión; MAJOR solo si el usuario indica ruptura de compatibilidad) y validar formato semver.
- `nombre_repo` del repositorio que se entrega.

**Outputs** (en `{output_documentacion}/entrega_release/{nombre_repo}/{version}/`):
- `release-notes.md`, `checklist-entrega_vX.Y.Z.txt`, `resumen-entrega_release_vX.Y.Z.txt`
- Rama `release/vX.Y.Z` en `origin`, creada una sola vez sobre el commit validado. La skill la bloquea (`isLocked = true`) al crearla. El tag `vX.Y.Z` y la imagen `{nombre_ms}:X.Y.Z` los crea el **pipeline de release** — CEIBA nunca crea tags.
- 4 PR `release/vX.Y.Z → des, pru, prepro, main` **en borrador** en ADO, creados tras el pipeline de release OK. Los publica el banco.

**Confirmaciones del usuario:** ✋ versión antes del paso 4 · ✋ OK para crear y bloquear la rama · ✋ OK para crear los 4 PR en borrador · ✋ cierre del checklist como estado real.

1. **Verificar develop y fijar el commit de entrega (`<sha>`)** — gate bloqueante:

   a. **Punta actual de develop:**
      ```bash
      git fetch origin --tags
      git log origin/develop -1 --format='%H %s'
      ```

   b. **Validar el pipeline en un sub-agente** (su salida no carga el hilo principal). Encargo:
      ```
      @ado-pipeline-analyzer build latest del pipeline <nombre_pipeline> en rama develop
      ```
      El sub-agente debe devolver **solo**: `runId` y URL, estado (`completed`/`inProgress`), resultado (`succeeded`/`failed`/…), `sourceVersion` (SHA compilado), stages ejecutados vs omitidos y el resultado de **DAST** (High/Critical).

   c. **Decidir:**

      | Resultado del sub-agente | Acción |
      |---|---|
      | `failed`, `canceled`, stages omitidos o no verificable | **Detener y reportar.** Nunca asumir OK. |
      | `inProgress` | Esperar a que termine y repetir **b**. |
      | `succeeded` y `sourceVersion` = punta de develop | `<sha>` = `sourceVersion`. Continuar. |
      | `succeeded` pero `sourceVersion` ≠ punta de develop | Hay commits en develop sin validar. ✋ Mostrar cuáles (`git log <sourceVersion>..origin/develop --oneline`) y preguntar: entregar `<sourceVersion>` (esos commits quedan fuera) o esperar el pipeline de la punta. |

   `<sha>` es **siempre el `sourceVersion` del build validado**, nunca `HEAD` ni `origin/develop`: develop puede avanzar mientras se prepara la entrega y lo que se entrega es exactamente lo que pasó el pipeline. Los pasos 3, 5 y 6 lo usan.

   Guardar `runId` y el resultado de DAST para el checklist: el ítem **DAST** sale de esta corrida porque el pipeline de release no despliega y no lo ejecuta (`[⚠]`, no bloqueante).

2. **Estado de promoción de la versión anterior (informativo — nunca bloquea):** hallar el último tag de versión (`vPREV`, lo reutilizan los pasos 3 y 4), descartando los tags de despliegue `-DES/-PRU/-PRE/-PRO`:
   ```bash
   git tag -l 'v*' | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -1
   ```
   y listar su promoción con `git ls-remote --tags origin 'refs/tags/vPREV-*'`. Mostrar cuáles existen y cuáles faltan entre `vPREV-DES`, `vPREV-PRU`, `vPREV-PRE`, `vPREV-PRO`, y continuar siempre — el ritmo de promoción del banco no frena esta entrega (ver Common Mistakes en `SKILL.md`).

3. **Release notes:** con `vPREV` del paso 2, escribir el resultado directamente en el artefacto (crear la carpeta antes):
   ```bash
   mkdir -p "{output_documentacion}/entrega_release/{nombre_repo}/{version}"
   git log vPREV..<sha> --oneline --no-merges > "{output_documentacion}/entrega_release/{nombre_repo}/{version}/release-notes.md"
   ```
   Primer release (sin `vPREV`): `git log <sha> --oneline --no-merges` y advertir "primer release". Se generan **desde cero** en cada versión (Regla 5).

4. **Prechequeos (bloqueantes):** ninguno de estos debe existir en `origin`:
   ```bash
   git ls-remote --tags origin "refs/tags/vX.Y.Z"
   git ls-remote --heads origin "release/vX.Y.Z"
   ```
   Cualquiera retorna algo → **detener**: la versión ya se publicó (o se intentó) y **no se reutiliza** — volver a calcular la siguiente con la Regla 2. Nunca borrar, mover ni sobrescribir un tag o una rama `release/`.

5. **Crear `release/vX.Y.Z` y bloquearla** (✋ OK del usuario) — una sola vez, directamente sobre `<sha>`, y con `isLocked = true` inmediatamente después:
   ```bash
   git push origin <sha>:refs/heads/release/vX.Y.Z
   ```
   Bloquear por API REST de ADO (`az` CLI no está disponible). PAT en `.env` de la raíz del proyecto, clave `pat_ado`, con permiso de escritura sobre Code — **nunca imprimirlo** (Regla 7):
   ```bash
   PAT=$(grep -m1 '^pat_ado=' .env | cut -d= -f2-)
   URL="https://dev.azure.com/GestionRequerimientos/BancaPorWhatsappCICD/_apis/git/repositories/{nombre_repo}/refs?filter=heads/release/vX.Y.Z&api-version=7.1"
   curl -s -u ":$PAT" -H "Content-Type: application/json" -X PATCH "$URL" -d '{"isLocked":true}'
   curl -s -u ":$PAT" "$URL" | grep -o '"isLocked":[a-z]*'   # debe ser "isLocked":true
   ```
   El bloqueo impide cualquier commit posterior: lo que se compila es exactamente `<sha>`. **Sin PAT, HTTP distinto de 200 o `isLocked` distinto de `true` → detener y reportar**; no continuar con una rama abierta.
   El push dispara el pipeline de release. La rama no se actualiza ni se desbloquea nunca: si después hace falta un cambio, es una versión nueva (Regla 3).

6. **Esperar el pipeline de release y analizarlo** — gate bloqueante:

   > **Espera exclusiva:** mientras el pipeline no finalice y el paso 6 no termine OK, **no se avanza a ningún paso siguiente** ni se adelanta trabajo de ellos (PR, listado de PR anteriores, checklist, resumen o correo). Solo con la decisión **6d = continuar** se pasa al paso 7.

   a. **Consultar el estado cada 30 s hasta que finalice.** API REST de ADO con el mismo `PAT` del paso 5 (nunca imprimirlo). Si el agente ejecuta el bucle en segundo plano (p. ej. por límite de tiempo de la herramienta), es solo para no cortar la consulta: **queda esperando su resultado** y no hace nada más mientras tanto.
      ```bash
      URL="https://dev.azure.com/GestionRequerimientos/BancaPorWhatsappCICD/_apis/build/builds?branchName=refs/heads/release/vX.Y.Z&queryOrder=queueTimeDescending&\$top=1&api-version=7.1"
      for i in $(seq 1 120); do                      # 120 × 30 s = 60 min máximo
        B=$(curl -s -u ":$PAT" "$URL" | jq -r '.value[0] | "\(.id) \(.status) \(.result) \(.sourceVersion)"')
        echo "$(date +%T) $B"
        case "$B" in *" completed "*) break ;; esac
        sleep 30
      done
      ```
      Cada línea muestra `runId status result sourceVersion`. Mientras no exista corrida (`null`, el push aún no se encola) o el estado sea `notStarted`/`inProgress`, seguir esperando. **Se agotan los 60 min sin `completed` → detener y reportar** con el `runId` y la URL para revisarlo a mano.

   b. **Al finalizar (`completed`), analizar la corrida en un sub-agente:**
      ```
      @ado-pipeline-analyzer build <runId> del pipeline <nombre_pipeline> en rama release/vX.Y.Z
      ```
      El sub-agente devuelve **solo**: `runId` y URL, resultado, `sourceVersion`, stages ejecutados vs omitidos y los resultados de **pruebas, cobertura y SonarQube**.

   c. **Confirmar el tag** sobre el commit de entrega:
      ```bash
      git fetch origin --tags
      git rev-list -n 1 vX.Y.Z   # debe ser igual a <sha>
      ```

   d. **Decidir:**

      | Resultado | Acción |
      |---|---|
      | `succeeded`, `sourceVersion` = `<sha>`, sin stages omitidos y tag `vX.Y.Z` = `<sha>` | Continuar al paso 7. |
      | `failed`, `canceled` o `partiallySucceeded` | **Detener y reportar**; no crear PR. La versión queda quemada (Regla 3). |
      | Stages omitidos, `sourceVersion` ≠ `<sha>`, tag inexistente o tag ≠ `<sha>` | **Detener y reportar**; no crear PR. |

   Guardar `runId` y los resultados de pruebas, cobertura y SonarQube para el checklist (`[⚠]`, no bloqueantes).

7. **Crear los 4 PR en BORRADOR** (✋ OK del usuario) — **solo después de que el paso 6 pase OK**, uno por ambiente, con el comando listo para copiar:
   ```
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia des con título exacto "Release vX.Y.Z → DES"
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia pru con título exacto "Release vX.Y.Z → PRU"
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia prepro con título exacto "Release vX.Y.Z → PRE"
   @ado-pr-creator crear PR en borrador (isDraft=true) de release/vX.Y.Z hacia main con título exacto "Release vX.Y.Z → PRO"
   ```
   ("título exacto": no reescribirlo a Conventional Commits). Descripción de cada PR: versión, tag `vX.Y.Z`, imagen `{nombre_ms}:X.Y.Z`, enlace a `release-notes.md` y la instrucción "**Completar con merge commit (sin squash), en orden DES → PRU → PRE → PRO**". Guardar los 4 ID y URL para el resumen.
   **Los PR quedan en borrador: CEIBA no los publica.** El banco los publica y les da el manejo que requiera (revisores, orden, aprobación). Es esperado que, al publicarlos, los PR hacia `pru`, `prepro` y `main` muestren la validación de orden en rojo hasta que exista el tag `vX.Y.Z-{AMB}` del ambiente anterior — no es un error de la entrega.

8. **PR abiertos de versiones anteriores (solo listar):** buscar en ADO los PR **activos o en borrador** hacia `des`, `pru`, `prepro` o `main` cuyo origen sea otra `release/v*` u `hotfix/v*`. Mostrar por cada uno: origen → destino, versión, estado y URL, con la indicación de **abandonarlos a mano** (la versión `vX.Y.Z` los reemplaza). La skill **no** los abandona. Sin PR abiertos → continuar.

9. **Checklist de entrega** (`references/checklist-entrega.txt`):
   a. Mostrarlo **sustituyendo `vX.Y.Z` por la versión real** en todas las líneas antes de mostrarlo — nunca dejar el placeholder literal. Los items ⚠️ requieren skills externas (ver tabla "Skills complementarias" en `SKILL.md`).
   b. **Marcar los ítems a medida que se ejecuten esas skills**, aplicando la INSTRUCCIÓN DE USO del propio checklist sobre la copia de entrega (nunca sobre la plantilla). Guardar la copia marcada en `{output_documentacion}/entrega_release/{nombre_repo}/{version}/checklist-entrega_vX.Y.Z.txt`; debe reflejar el estado real al cierre.

   Al sugerir cada skill, mostrar su comando exacto listo para copiar (con la versión real ya sustituida). `@env-config-audit` va **una vez por ambiente**: cada PR muestra lo que entra a ese ambiente.
   ```
   @env-config-audit sobre el diff origin/des..vX.Y.Z
   @env-config-audit sobre el diff origin/pru..vX.Y.Z
   @env-config-audit sobre el diff origin/prepro..vX.Y.Z
   @env-config-audit sobre el diff origin/main..vX.Y.Z
   @sac-analizar-seguridad scope=commits sobre release/vX.Y.Z
   @sac-analizar-calidad-codigo scope=commits sobre release/vX.Y.Z
   ```

10. **Resumen final y notificación:** rellenar la **variante RELEASE** de `references/resumen-entrega.txt` (sustituir todos los placeholders, nunca dejar literales), mostrarla y guardarla como `resumen-entrega_release_vX.Y.Z.txt` en `{output_documentacion}/entrega_release/{nombre_repo}/{version}/`. El correo de entrega al banco lo envía CEIBA; para redactarlo:
    ```
    @email-composer correo laboral de entrega vX.Y.Z de {nombre_repo} al banco con el contenido de resumen-entrega_release_vX.Y.Z.txt
    ```
