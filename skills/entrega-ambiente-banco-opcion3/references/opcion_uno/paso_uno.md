# Opción 1 · Paso 1 — Verificar develop y fijar <sha>

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

---

**Siguiente:** solo con la decisión **c = Continuar** (`<sha>` fijado) → cargar `paso_dos.md`. Pregunta ✋ abierta → esperar la respuesta del usuario sin cargar nada. Detener → no cargar ningún paso más.
