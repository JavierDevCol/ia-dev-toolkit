# Fase: configuración (solo cuando falta algo)

Se lee únicamente cuando memctl devolvió `null`, línea vacía, `[]` o exit 2 en `chat-dm.config.*`, o cuando el usuario pide "configurar". **Pregunta solo lo que falta**, de una cosa por vez, explicando qué es. Nunca adivines ni uses un valor por defecto: espera la respuesta del usuario.

## Qué preguntar

1. **Zona horaria** (`zona_horaria`).
   *"Tu diferencia con UTC, en formato `±HH:MM` (por ejemplo `-05:00`). La uso para mostrar la hora local de cada mensaje y para fijar desde qué hora leo."* Valida `±HH:MM`.
2. **Tus nombres en los chats** (`alias_en_chat`, lista).
   *"Cómo te nombran tus compañeros en los grupos (tu nombre, un apodo…), separados por coma. Lo uso para detectar qué mensajes de un grupo son para ti."* Al menos uno.
3. **Destinatarios** (`destinatarios`, lista). Pregunta uno por uno y, tras cada uno, "¿añadir otro?":
   - `alias`: *"Un nombre corto con el que me pedirás ese chat (por ejemplo el nombre de la persona o del grupo)."*
   - `tipo`: *"`space` si es un grupo o espacio de Google Chat; `dm` si es un mensaje directo a una persona."*
   - `valor`: *"Para `space`, el identificador del espacio (`spaces/XXXX…`, lo ves en la URL del espacio en Google Chat); para `dm`, el correo de la persona."* Un `space` debe empezar por `spaces/`; un `dm` debe parecer un correo.

## Guardar

- Si `sh .SAC/memctl.sh get usuario.nombre` salió con exit 1, `sac.json` es inválido: detente y avisa; no escribas nada.
- Lee `.SAC/config/sac.json`, cambia **solo** `chat-dm.config` (las claves que preguntaste) y escribe el JSON completo con todo lo demás intacto (2 espacios de indentación). Si `destinatarios` solo tenía la entrada de ejemplo vacía (`valor: ""`), reemplázala; si ya tenía destinatarios reales, añade al final sin tocar los existentes.
- Vuelve a leer con memctl las claves guardadas para comprobar que quedaron bien, y continúa con la fase que el usuario pidió.
