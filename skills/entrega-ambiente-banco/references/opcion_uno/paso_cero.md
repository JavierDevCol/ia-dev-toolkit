# Opción 1 · Paso 0 — Validación de estado de ambientes (2 sub-agentes en paralelo)

0. **Validar el estado de ambientes del `nombre_repo` antes de preparar la entrega** — diagnóstico de solo lectura que responde dos cosas sobre lo que se está solicitando: ¿hace falta una nueva entrega/corte de release? y ¿hay desvíos?

   a. **Lanzar DOS sub-agentes EN PARALELO** (sus salidas no cargan el hilo principal) y **esperar a que ambos terminen** antes de continuar:

      | Sub-agente | Encargo |
      |---|---|
      | **A — ¿Nueva entrega/corte?** | `@estado-ambientes <nombre_repo> -t des` |
      | **B — ¿Desvíos?** | `@estado-ambientes <nombre_repo> -d` |

      Cada sub-agente debe devolver **solo**: las señales detectadas (`CREAR_RELEASE`, `CON DESVIOS`, `DES CON CONTENIDO PROPIO`, `TAG_SIN_CONTENIDO`, `INCONSISTENTE`, `PR_PENDIENTE`, `SALTO`, …), el dato concreto que las respalda (n commits sin entregar, archivos con desvío, tags faltantes) y su veredicto (`BLOQUEA` / `INFORMATIVO` / `OK`). Nunca la salida cruda del script.

   b. **Consolidar ambos resultados y presentarlos al usuario con una recomendación explícita:**

      | Hallazgo | Recomendación |
      |---|---|
      | `CREAR_RELEASE: SI (n)` sin desvíos | **Continuar con el corte**: hay n commits en develop sin entregar |
      | `CREAR_RELEASE: NO` | **No cortar**: DES ya contiene el cambio solicitado; confirmar si aún quiere proceder |
      | `CON DESVIOS (n)` / `DES CON CONTENIDO PROPIO` / `X` en PRO | **No promover** hasta devolver el cambio a develop (PR a develop); decidir archivo por archivo con `EN_DEVELOP` |
      | `TAG_SIN_CONTENIDO` / `INCONSISTENTE` | **Bloquea la entrega** (según `estado-ambientes`): escalar antes de continuar |
      | Tags de promoción faltantes / `PR_PENDIENTE` / `SALTO` | **Informativo, nunca gate**: el ritmo del banco no frena la entrega |

   c. ✋ **El usuario decide sobre la recomendación** (continuar con el corte · detenerse · resolver desvíos primero). La skill no aborta por sí sola ni promueve nada: `estado-ambientes` es solo lectura y sus comandos de escritura nunca se ejecutan.

---

**Siguiente:** solo con la decisión ✋ del usuario de **continuar** → cargar `paso_uno.md`. Decisión de detenerse o resolver desvíos primero → no cargar ningún paso más. Pregunta ✋ abierta → esperar la respuesta sin cargar nada.
