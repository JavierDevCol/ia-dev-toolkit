# Opción 2b · Paso 0 — Validación de estado de ambientes (2 sub-agentes en paralelo)

0. **Validar el estado de ambientes del `nombre_repo` antes de preparar el hotfix** — diagnóstico de solo lectura que responde dos cosas sobre lo que se está solicitando: ¿hace falta una nueva entrega/corte? y ¿hay desvíos? (aplica igual en un hotfix: la falla puede ya estar corregida o el ambiente puede tener contenido fuera de develop).

   a. **Lanzar DOS sub-agentes EN PARALELO** (sus salidas no cargan el hilo principal) y **esperar a que ambos terminen** antes de continuar:

      | Sub-agente | Encargo |
      |---|---|
      | **A — ¿Nueva entrega/corte?** | `@estado-ambientes <nombre_repo> -t des` |
      | **B — ¿Desvíos?** | `@estado-ambientes <nombre_repo> -d` |

      Cada sub-agente debe devolver **solo**: las señales detectadas (`CREAR_RELEASE`, `CON DESVIOS`, `DES CON CONTENIDO PROPIO`, `TAG_SIN_CONTENIDO`, `INCONSISTENTE`, `PR_PENDIENTE`, `SALTO`, …), el dato concreto que las respalda (n commits sin entregar, archivos con desvío, tags faltantes) y su veredicto (`BLOQUEA` / `INFORMATIVO` / `OK`). Nunca la salida cruda del script.

      > **Por qué `-t des` aunque la falla sea de otro ambiente:** `CREAR_RELEASE` solo existe con `-t des` en `estado-ambientes`; responde si hace falta un corte nuevo para lo solicitado, con independencia del ambiente donde se detectó la falla.

   b. **Consolidar ambos resultados y presentarlos al usuario con una recomendación explícita:**

      | Hallazgo | Recomendación |
      |---|---|
      | `CREAR_RELEASE: SI (n)` sin desvíos | **Continuar con el corte del hotfix** |
      | `CREAR_RELEASE: NO` | **Revisar si el hotfix sigue siendo necesario**: DES ya contiene el cambio solicitado (puede estar corregido en develop) |
      | `CON DESVIOS (n)` / `DES CON CONTENIDO PROPIO` / `X` en PRO | **No promover** hasta devolver el cambio a develop (PR a develop); decidir archivo por archivo con `EN_DEVELOP` |
      | `TAG_SIN_CONTENIDO` / `INCONSISTENTE` | **Bloquea la entrega** (según `estado-ambientes`): escalar antes de continuar |
      | Tags de promoción faltantes / `PR_PENDIENTE` / `SALTO` | **Informativo, nunca gate**: el ritmo del banco no frena la entrega (un hotfix urgente menos) |

   c. ✋ **El usuario decide sobre la recomendación** (continuar con el corte · detenerse · resolver desvíos primero). En 2b la urgencia puede justificar continuar pese a un hallazgo, pero siempre con decisión explícita. La skill no aborta por sí sola ni promueve nada: `estado-ambientes` es solo lectura y sus comandos de escritura nunca se ejecutan.

---

**Siguiente:** solo con la decisión ✋ del usuario de **continuar** → cargar `paso_uno.md`. Decisión de detenerse o resolver desvíos primero → no cargar ningún paso más. Pregunta ✋ abierta → esperar la respuesta sin cargar nada.
