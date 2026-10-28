# C. Propuesta y creación de eventos

1. **Siguiente día.** `gog --readonly calendar events --from <día> --to <día+1> --all --json --wrap-untrusted` (no combines `--days` con `--to`). Lee las horas de `startLocal`/`endLocal`, no de `start.dateTime` (UTC en el calendario secundario). Respeta todos los eventos del calendario principal (incluidos CeibaCLIP y pausas), e incluido uno de "organizar agenda": no lo propongas otra vez. Hueco libre = jornada menos almuerzo menos eventos del principal.
   - **Bloques ya existentes mañana** en el calendario de bloques que choquen con un evento del principal (reunión agendada después de crear el bloque; ignora `declined`, pregunta por `tentative`): márcalos "en conflicto" y propón moverlos al siguiente hueco libre, con el mismo `#WI` y duración. No muevas nada sin confirmación (`gog calendar update`, `--dry-run` primero). Si la reunión es del mismo WI, no hay conflicto.
2. **Propuesta.** Orden: ceremonias fijas → seguimientos y arrastres → nuevos → resto. Los **arrastres** (remanentes de la fase B) llevan como duración el remanente y origen `arrastre`. Duración: horas restantes de la ficha si existen (suma de tasks hijas abiertas para una US); si no, 1 h. Criterio de hecho: sale de los criterios de aceptación y tasks abiertas. Entrega:
   - Resumen de hoy: hecho / seguimiento / por aclarar.
   - Tabla `hora | duración | #WI · acción | criterio de hecho | origen (seguimiento/arrastre/nuevo/planning/por aclarar)`.
   - "Cruces de hoy": por bloque, tiempo efectivo vs. reservado y la reunión que lo cortó (etiqueta "agregada tras planear" si aplica).
   - "Bloques de mañana en conflicto": bloque, reunión que choca y hueco propuesto.
   - "Por aclarar": cada ítem con una pregunta concreta para el usuario (incluye bloques sin evidencia).
   - "Sin movimiento": `#WI · título · último cambio`.
3. **Crear eventos** solo tras confirmación explícita, `--dry-run` primero, cuenta explícita.
   - Los bloques de trabajo van en el calendario secundario de bloques (`{calendario_nombre}`, no compartido), para que no te marquen ocupado en tu calendario principal. Su ID es `{calendario_id}` (ver Configuración en `SKILL.md`); si falta, `fases/configuracion.md` lo crea o lo pide: no busques ni crees calendarios aquí.
   - Comando: `gog calendar create {calendario_id} --summary '#WI · acción' --description '<objetivo y criterio de hecho>' --from <RFC3339 con la zona configurada> --to <RFC3339 con la zona configurada> --transparency free --no-reminders`.
   - Las ceremonias y reuniones reales no se crean aquí: ya están en el calendario principal.
   - Deja al menos un hueco de 1 h sin bloques (por defecto, el último de la jornada) para que puedan citarte.
