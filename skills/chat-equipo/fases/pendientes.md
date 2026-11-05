# Fase: pendientes del chat (solo lectura)

1. **Ventana.** Por defecto desde las 00:00 de hoy (`date '+%Y-%m-%d'` + `T00:00:00` + la zona de `chat-dm.config.zona_horaria`). Si el usuario dice "desde ayer", "últimos 3 días" o nombra un chat/persona, ajusta la hora de inicio y/o los alias.
2. **Leer.** `python3 -I <skill>/scripts/leer.py <desde ISO> [alias ...] > <scratchpad>/chat.jsonl` (desde la raíz del proyecto) y lee el archivo. Una línea por mensaje (`hora` local con segundos, `origen`, `de`, `mio`, `texto` máx. 400, `hilo`, `reacciones`); las líneas con `error` o `truncado` van tal cual a "Avisos". `<scratchpad>` = el directorio scratchpad de la sesión; `<desde ISO>` con zona (p. ej. `2026-10-28T00:00:00` + la zona configurada); alias = `alias` exacto de la lista (un alias inexistente no devuelve nada: avísalo). Sin alias = todos. Lee hasta 100 mensajes por chat; si llega al tope, `truncado` lo avisa. El archivo puede ser grande: léelo por tramos o filtra con `python3 -c` en vez de volcarlo; nunca lo pegues al usuario. (`leer.py` resuelve cada DM con `gog chat dm space`: sobre un DM existente solo lo devuelve.)
3. **Detectar pendientes.** Un mensaje de otra persona (`mio: false`) es candidato si pide algo, hace una pregunta de trabajo o asigna una tarea **al usuario**: en DM, cualquiera; en grupo, solo si lo nombra (uno de `chat-dm.config.alias_en_chat`, o `@` + ese alias) o usa `@todos` con una petición de trabajo, continúa un hilo suyo o el usuario respondió comprometiéndose. Excluye charla social, curiosidad ("¿eso fue un agente?"), saludos y agradecimientos. El orden lo da `hora`; `hilo` solo sirve en grupos (en DM cada mensaje es su propio hilo). Estado:
   - `pendiente`: sin respuesta posterior del usuario.
   - `en curso`: el usuario respondió con un compromiso o acuse ("ya los miro", "ya te confirmo") pero no hay entrega ni resultado.
   - `por confirmar`: la respuesta del usuario puede haberlo cerrado o no (di el motivo).
   - cerrado (no se lista): una respuesta posterior del usuario atiende lo pedido.

   Un mensaje a todo el equipo ("¿alguien puede…?", "confirmen asistencia") que no nombra al usuario va en "Para el equipo". Un mensaje del usuario (`mio: true`) con una pregunta o petición a otro, sin respuesta posterior de esa persona en el mismo chat, va en "Esperan respuesta de otros".
4. **Reporte**, pendientes del más viejo al más nuevo:
   1. Encabezado: ventana revisada y chats leídos (los alias de los grupos y la cantidad de DMs).
   2. **Resumen:** `N pendientes · E en curso · M por confirmar · K para el equipo` (conteos salen de la tabla; un 0 se escribe).
   3. Tabla: `# | Hora | Chat | De | Qué piden (una línea) | Estado` (estado con motivo si es `por confirmar`).
   4. **Para el equipo:** `Hora | Chat | De | Qué piden`.
   5. **Esperan respuesta de otros:** `Hora | Chat | A quién | Qué preguntaste`.
   6. **Avisos:** errores de lectura, resultados truncados, chats sin mensajes.

   Sin pendientes: una línea con la ventana revisada. Cita lo mínimo de cada mensaje. Hora en la zona configurada.

## Errores comunes

| Error | Corrección |
|---|---|
| Contar como pendiente todo mensaje de un grupo | Solo si nombra al usuario, es su hilo o se comprometió |
| Dar por resuelto algo porque el usuario escribió después | Verifica que atienda lo pedido; si no, `en curso` o `por confirmar` |
| Responder o reaccionar desde esta fase | Es de solo lectura |
| Leer `createTime` en UTC | `leer.py` ya entrega `hora` local |
