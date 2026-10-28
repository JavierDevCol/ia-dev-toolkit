# Fase: configuración (solo cuando falta algo)

Se lee únicamente cuando memctl devolvió `null`, línea vacía o exit 2 en `agenda-laboral.config.zona_horaria` o `agenda-laboral.config.calendario_bloques.*`, o cuando el usuario pide "reconfigurar". **Pregunta solo lo que falta**, de una cosa por vez, explicando qué es. Nunca adivines ni uses un valor por defecto: espera la respuesta del usuario.

## Qué preguntar

1. **Zona horaria** (`zona_horaria`).
   *"Tu diferencia con UTC, en formato `±HH:MM` (por ejemplo `-05:00`). La uso para interpretar las horas de tu calendario y de Azure DevOps."* Valida `±HH:MM`.
2. **Nombre del calendario de bloques** (`calendario_bloques.nombre`).
   *"El calendario secundario de Google Calendar donde viven tus bloques de trabajo por tarea, aparte de tu calendario principal. Si ya tienes uno, escribe su nombre exacto; si no, lo creo con el nombre que me des."*
3. **Calendario de bloques** (`calendario_bloques.id`), una vez conocido el nombre:
   - Consulta los calendarios con `gog --readonly calendar calendars --json`. Si ya hay uno con ese nombre exacto, **no crees un duplicado**: pregunta "ya existe «<nombre>», ¿lo uso o prefieres otro nombre?". Si lo usas, toma su ID.
   - Si no existe, muestra el resumen ("voy a crear el calendario «<nombre>» en tu cuenta de Google") y espera confirmación; luego `gog calendar create-calendar "<nombre>"`. Toma el ID del resultado; si el resultado no lo trae, vuelve a listar y busca el nombre exacto que acabas de crear.
   - Sin ID no continúes: sin él no se distinguen bloques de reuniones.

## Guardar

- Si memctl salió con exit 1, `sac.json` es inválido: detente y avisa; no escribas nada.
- Lee `.SAC/config/sac.json`, cambia **solo** `agenda-laboral.config` (las claves que preguntaste) y escribe el JSON completo con todo lo demás intacto (2 espacios de indentación). Esta sección la comparte `planear-agenda-siguiente-dia`: no borres claves que no preguntaste (`jornada`, `almuerzo`, `alias_en_notas`).
- Vuelve a leer con memctl las claves guardadas para comprobar que quedaron bien, y continúa con el flujo.
