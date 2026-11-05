# Fase: enviar mensaje (con aprobación)

1. **Contenido.** Si el usuario no dio el contenido real, pregúntalo (qué se quiere comunicar, a quién se le pide qué, fechas/#WI). No inventes datos ni rellenes con texto genérico.
2. **Redactar** con el formato de abajo, en español, tono laboral. Si el usuario ya nombró destinatarios, resuélvelos ahora contra la lista de memoria (solo lectura); si alguno no está, dilo antes de la vista previa. Fechas relativas ("mañana") → fecha absoluta con `date` (macOS: `date -v+1d +%Y-%m-%d`; Linux: `date -d tomorrow +%Y-%m-%d`); si cae en fin de semana, dilo. Saludo neutro (`Hola 👋` / `Buen día, equipo:`) cuando el mismo texto va a varios destinos.
3. **Vista previa.** Muestra el mensaje tal cual se enviará (bloque de cita o de código). Pregunta: "¿Apruebas este mensaje? [S/N, o dime qué cambiar]". Si pide cambios → paso 2 y nueva vista previa.
4. **Destinatario** (solo tras aprobar el texto). Si el usuario ya los nombró, salta la lista y pasa al paso 5 con ellos; si no, ofrece la lista numerada (alias y tipo) y pregunta a cuál enviar; acepta varios.
5. **Confirmar el envío.** Muestra "Enviaré el mensaje aprobado a: <alias(es)>". El texto no cambia desde la aprobación; si cambia algo, vuelve al paso 3. Espera un sí explícito al destino. Aprobar el texto no es aprobar el destino, y la aprobación no cubre un mensaje modificado ni otro destinatario.
6. **Enviar** (uno por destinatario, texto exacto aprobado, guardado en un archivo del scratchpad y pasado con `$(cat …)`):
   - `tipo: dm` → `gog chat dm send <valor> --text "$(cat <archivo>)"`
   - `tipo: space` → `gog chat messages send <valor> --text "$(cat <archivo>)"`
   - Ensayo: el mismo comando con `--dry-run` justo tras `gog` (`gog --dry-run chat dm send <valor> --text "$(cat <archivo>)"`).
   - Reporta el resultado de cada envío tal cual (éxito o error). No reintentes en silencio.

## Formato (Google Chat)

Chat no renderiza Markdown estándar: no uses `#` títulos, tablas ni `**negrita**`.

| Elemento | Sintaxis |
|---|---|
| Negrita | `*texto*` |
| Cursiva | `_texto_` |
| Tachado | `~texto~` |
| Código / IDs | `` `texto` `` |
| Bloque de código | ```` ``` ```` |
| Viñetas | `- ítem` |

Estructura, en este orden:
1. Saludo corto (`Hola <nombre> 👋` / `Buen día, equipo:`).
2. Título en negrita con emoji de tipo (ℹ️ informativo, ❓ pregunta, ⚠️ urgente/riesgo, ✅ resuelto).
3. Contexto en 1–2 líneas.
4. Detalle en viñetas cortas (`#WI`, fechas y cifras en `código`).
5. Si hay petición: línea final `*Necesito:* … para <fecha>`.
6. Cierre (`Gracias.`). Sin firma.

Mensaje corto (una pregunta simple): saludo + una o dos líneas, sin título ni viñetas.

## Errores comunes

| Error | Corrección |
|---|---|
| Enviar al aprobar el texto, sin preguntar el destino | Dos confirmaciones: texto (3) y destino (5) |
| Markdown estándar (`**`, `#`, tablas) | Sintaxis de Chat de la tabla |
| Editar el mensaje tras aprobarlo | Nueva vista previa y nueva aprobación |
| Enviar a un grupo por coincidencia de nombre | Usa el `valor` (`spaces/…`) |
| "Mensaje de prueba" real | Solo `--dry-run` |
