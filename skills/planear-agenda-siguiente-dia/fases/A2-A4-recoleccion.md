# A2–A4. Recolección en el hilo principal

Lanza A2, A3 y A4 en paralelo, en el mismo turno que el subagente A1.

## A2. Calendario de hoy
`gog calendar time` para la fecha. `gog --readonly calendar events --today --all --json --wrap-untrusted` (`--all` lee también el calendario de bloques; sin él solo se lee el principal). Usa `startLocal`/`endLocal` para las horas: el calendario secundario llega en UTC en `start.dateTime` (`12:30Z` = 07:30), nunca lo leas crudo. La salida es larga: extrae con `python3` hora, `summary` y `description`, quitando los wrappers `<<<EXTERNAL_UNTRUSTED_CONTENT…>>>`.

- Ceremonia = Daily, Planning, Retro, informes/reuniones con terceros.
- Bloque de trabajo = cualquier otro evento; su WI sale de `#id` en `summary`/`description`, o por tema. Sin WI ni tema claro: trátalo como ceremonia **y dilo en la propuesta** para que el usuario lo corrija.

## A3. Notas del equipo
`gog --readonly gmail search 'from:gemini-notes@google.com newer_than:3d (Daily OR Planning)' --json --wrap-untrusted`. Lee la Daily de hoy y el Planning más reciente (hilos distintos); `gog gmail get` trae HTML/base64: decódificalo a texto. Extrae solo lo asignado al usuario: aparece con alguno de los nombres de `sh .SAC/memctl.sh get agenda-laboral.config.alias_en_notas` (vacío o exit 2 → lee `fases/configuracion.md`).

## A4. Bitácoras
`bitacora-tecnica/*/bitacora.md` (desde la raíz del proyecto, donde escribe `bitacora-tecnica`) con `## Sesión <fecha de hoy>`; lee esa sesión y `Pendientes / próxima sesión`. Las entradas suelen compartir una hora única: relaciónalas con bloques por tema, no por hora. Si un check dice hecho y el texto dice lo contrario, señala la contradicción.
