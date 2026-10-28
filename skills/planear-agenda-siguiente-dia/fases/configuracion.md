# Fase: configuración (solo cuando falta algo)

Se lee únicamente cuando memctl devolvió `null`, línea vacía, `[]` o exit 2 en alguna clave `agenda-laboral.config.*`, o cuando el usuario pide "reconfigurar". **Pregunta solo lo que falta**, de una cosa por vez, explicando qué es. Nunca adivines ni uses un valor por defecto: espera la respuesta del usuario y valida cada una.

## Qué preguntar

1. **Zona horaria** (`zona_horaria`).
   *"Tu diferencia con UTC, en formato `±HH:MM` (por ejemplo `-05:00`). La uso para convertir las horas de Azure DevOps, que llegan en UTC, a las de tu calendario."* Valida `±HH:MM`.
2. **Nombre del calendario de bloques** (`calendario_bloques.nombre`).
   *"El calendario secundario de Google Calendar donde se guardan tus bloques de trabajo por tarea, aparte de tu calendario principal, para que tus compañeros no te vean ocupado. Si ya tienes uno, escribe su nombre exacto; si no, lo creo con el nombre que me des."*
3. **Calendario de bloques** (`calendario_bloques.id`), una vez conocido el nombre:
   - Consulta los calendarios con `gog --readonly calendar calendars --json`. Si ya hay uno con ese nombre exacto, **no crees un duplicado**: pregunta "ya existe «<nombre>», ¿lo uso o prefieres otro nombre?". Si lo usas, toma su ID.
   - Si no existe, muestra el resumen ("voy a crear el calendario «<nombre>» en tu cuenta de Google") y espera confirmación; luego `gog calendar create-calendar "<nombre>"`. Toma el ID del resultado; si el resultado no lo trae, vuelve a listar y busca el nombre exacto que acabas de crear.
   - Sin ID no continúes: la propuesta no puede crear ni leer los bloques.
4. **Jornada** (`jornada.lunes_jueves.inicio/fin` y `jornada.viernes.inicio/fin`).
   *"Tu horario de trabajo: hora de inicio y de fin (`HH:MM`, 24 h) de lunes a jueves y del viernes. Solo planifico bloques dentro de él, y las acciones tuyas en ADO fuera de ese horario te las marco para revisar."* Valida `HH:MM` y que el inicio sea anterior al fin.
5. **Almuerzo** (`almuerzo.inicio` y `almuerzo.duracion_min`).
   *"A qué hora reservas el almuerzo (`HH:MM`) y cuántos minutos dura. Lo bloqueo dentro de tu jornada y lo muevo si un evento fijo lo ocupa."* La duración, un entero positivo; el almuerzo debe caber en la jornada.
6. **Tus nombres en las notas** (`alias_en_notas`, lista).
   *"Cómo te llaman tus compañeros en las notas Daily/Planning (tu nombre, un apodo…), separados por coma. Lo uso para saber qué tareas que mencionan esas notas son tuyas."* Al menos uno.

## Guardar

- Si memctl salió con exit 1, `sac.json` es inválido: detente y avisa; no escribas nada.
- Lee `.SAC/config/sac.json`, cambia **solo** `agenda-laboral.config` (las claves que preguntaste) y escribe el JSON completo con todo lo demás intacto (2 espacios de indentación). Esta sección la comparte `iniciar-dia-laboral`: no borres claves que no preguntaste.
- Vuelve a leer con memctl las claves guardadas para comprobar que quedaron bien, y continúa con el flujo.
