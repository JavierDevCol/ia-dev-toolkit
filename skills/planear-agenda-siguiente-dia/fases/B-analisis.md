# B. Análisis

Entradas: reporte de A1 (fichas), A2 (eventos de hoy), A3 (notas), A4 (bitácoras).

1. **Evidencia por bloque y por trabajo no agendado:** cruza A2 con las fichas de A1 y con A4.
   - Ubica el trabajo en el tiempo con las marcas de ADO (`ActivatedDate`, `CreatedDate`/`ClosedDate` de tasks, `createdDate` de comentarios; en la zona configurada): son más precisas que las bitácoras.
   - Si las horas registradas (`CompletedWork`) superan el tiempo transcurrido entre bloques y cierres, o todas las tasks se crearon y cerraron en lote, señálalo como dato para que el usuario lo revise; no lo califiques. Las fechas de creación en ADO no se pueden editar.
   - Si el WI del bloque está asignado a otra persona, no es trabajo propio: "por aclarar".
   - Si una nota de A3 atribuye al usuario algo asignado a otro en ADO: "por aclarar".
   - **Desfase de tiempo (pregunta obligatoria):** cada acción del usuario en ADO (comentario, creación de task, cambio de estado, cierre) con hora fuera de la jornada, o dentro de la jornada pero fuera de todo bloque reservado para ese WI en el calendario de bloques, se pregunta al usuario por qué (¿trabajo previo?, ¿otra prioridad?, ¿registro tardío?). Agrupa por WI y ventana de tiempo en una sola pregunta; tolera 15 min de margen (por defecto). Una acción dentro de una reunión del calendario principal también se pregunta, salvo que la reunión trate de ese WI. No asumas la causa.
2. **Reconciliación de cruces** (la skill corre una vez al cierre del día: los cruces se resuelven aquí, no en tiempo real). Cruce = bloque del calendario de bloques ∩ evento del calendario principal.
   - Estado de respuesta del usuario: reunión `declined` no cuenta como cruce; `tentative` se pregunta al usuario; `accepted` o propia cuenta.
   - Reunión del mismo WI (`#id` o tema del WI en su `summary`/`description`): no es cruce, esa reunión **es** el trabajo y suma al tiempo del WI. Si no está claro, pregunta.
   - **Tiempo efectivo** del bloque = duración − cruces. Ej.: bloque 11:00–12:00 y reunión 11:30–12:00 → 30 min efectivos.
   - **Agregada tras planear:** `gog --readonly calendar changed --all --since <inicio del día, RFC3339 con la zona configurada> --json --wrap-untrusted`. Si la reunión se creó o movió después de la creación del bloque (`created` del bloque), etiqueta el cruce "agregada tras planear": no genera pregunta de desfase.
   - **Remanente** = duración del bloque − tiempo efectivo. Si el veredicto no es `terminado`, pasa a la fase C como arrastre.
3. **Veredicto:** `terminado` (WI cerrado o criterio cumplido) / `seguimiento` (pendientes, WI abierto o criterio sin cumplir) / `sin evidencia` / `por aclarar`.
4. **Sin movimiento:** WI cuyo `ChangedDate` es de hace más de 14 días **y** no se menciona en A3 ni A4. Se listan aparte, sin bloque de tiempo, salvo que el usuario pida agendarlos.
5. **Nuevos:** `CreatedDate` de hoy, o aparecen en A3 como asignación nueva.
