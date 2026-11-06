# Opción 1 · Paso 6 — Esperar y analizar el pipeline de release

6. **Esperar el pipeline de release y analizarlo** — gate bloqueante:

   > Mientras el pipeline no finalice, no hacer nada más (ver **Siguiente**).

   a. **Consultar el estado cada 30 s hasta que finalice.** API REST de ADO con el mismo `PAT` del paso 5 (nunca imprimirlo). Si el agente ejecuta el bucle en segundo plano (p. ej. por límite de tiempo de la herramienta), es solo para no cortar la consulta: **queda esperando su resultado** y no hace nada más mientras tanto.
      ```bash
      URL="{ado_base}/_apis/build/builds?branchName=refs/heads/release/vX.Y.Z&queryOrder=queueTimeDescending&\$top=1&api-version=7.1"
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
      | `failed`, `canceled` o `partiallySucceeded` | **Detener y reportar**; no crear PR. La versión queda quemada (Regla 8). |
      | Stages omitidos, `sourceVersion` ≠ `<sha>`, tag inexistente o tag ≠ `<sha>` | **Detener y reportar**; no crear PR. |

   Guardar `runId` y los resultados de pruebas, cobertura y SonarQube para el checklist (`[⚠]`, no bloqueantes).

---

**Siguiente:** solo con la decisión **d = Continuar** → cargar `paso_siete.md`. Mientras el pipeline no finalice, esperar sin cargar nada. Cualquier otro resultado → detener; no cargar ningún paso más.
