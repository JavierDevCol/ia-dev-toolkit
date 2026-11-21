# Escritor de bitácora (instrucciones para el subagente)

Archivo: `<raiz_proyecto>/bitacora-tecnica/<slug>/bitacora.md`. Plantilla: `../assets/plantilla-bitacora.md` (relativa a este archivo).

## Reglas

- Solo checkpoints de 1–2 líneas que ayuden a retomar o eviten repetir trabajo. Nunca paso a paso.
- Nunca escribir secrets, JWTs, contraseñas, connection strings ni PII: reemplazar por `[REDACTADO]`.
- Evidencias solo como enlaces/rutas; no pegar logs completos.
- Fecha y hora actuales del sistema (`date "+%d-%m-%Y %H:%M"`): la misma hora para todos los checkpoints de una llamada; nunca inventar horas. Cada checkpoint lleva fecha y hora (`DD-MM-YYYY HH:MM`) para distinguir horas iguales en días distintos.
- No modificar nada fuera de `bitacora-tecnica/<slug>/`.
- Formato de pendiente: abierto = `- [ ] <texto> — desde DD-MM-YYYY`; cerrado = `- [x] <texto> — desde DD-MM-YYYY · cierra DD-MM-YYYY` (fecha del checkpoint que lo cierra). Redactar `<texto>` como resultado esperado (ej. `Respuesta de pepito sobre permisos`), nunca como estado (`Esperando respuesta…`); el estado vive en la línea de checkpoint.

## Tipos de checkpoint

Un checkpoint puede tener varios efectos a la vez (ej. "Se envió correo a pepito; esperando respuesta" = estándar + apertura).

| Tipo | Señal | Efecto en el archivo |
|---|---|---|
| estándar | acción pasada + resultado | línea en `## Sesión` |
| apertura | expectativa o bloqueo: "esperando", "pendiente de", "bloqueado por" | línea + `- [ ] … — desde DD-MM-YYYY` |
| cierre confirmado | resolución que casa con un `- [ ]` existente | línea + `[x] … · cierra DD-MM-YYYY` |
| cierre incierto | cierre parcial, borrador, falta de confirmación o correspondencia ambigua | línea + `— ¿cierra DD-MM-YYYY? revisar` y `⚠️ cierre incierto` en la respuesta |
| incidencia | causa raíz encontrada o camino descartado | línea + entrada en `## Incidencias y solución` |

Clasificación de cada checkpoint (los efectos mecánicos se aplican en el paso 3 de `**checkpoint**`):

1. Trabajo hecho o resuelto → estándar.
2. Expectativa futura → apertura (si ya existe un pendiente igual o equivalente, no duplicar).
3. Resolución que casa con un `- [ ]` existente → cierre confirmado.
4. Cierre parcial o correspondencia ambigua → cierre incierto; nunca `[x]` por suposición.
5. Causa raíz encontrada o camino descartado → incidencia.

## Sesiones de trabajo

Cada bloque `## Sesión <fecha> · inicio HH:MM` es una sesión de trabajo. Se abre bloque nuevo:

- al **`crear`**: primera sesión, `inicio` = hora de `**Creada:**`
- al **`retomar`**: `inicio` = hora de la llamada
- **automáticamente** cuando un checkpoint llega a más de 2h del último evento del bloque más reciente (su último checkpoint, o su `· inicio` si aún no tiene) o en otra fecha: `inicio` = hora del checkpoint

Mientras el bloque más reciente esté dentro del plazo de 2h, los checkpoints siguientes se acumulan ahí. Los bloques antiguos sin `· inicio` cuentan como abiertos desde su primer checkpoint.

## Modos

**crear**
1. Si el archivo ya existe y su `## Objetivo` es de otra tarea → no escribir; responder `⚠️ slug existe con otro objetivo: <ruta>`. Si es la misma tarea → seguir como `checkpoint`.
2. Crear la carpeta (`mkdir -p`) y el archivo desde la plantilla con título, slug, rama, objetivo y `- **Creada:** DD-MM-YYYY HH:MM` (hora actual del sistema; se registra solo al crear). Quitar las secciones de ejemplo que queden vacías salvo `## Pendientes / próxima sesión`.
3. Agregar los checkpoints recibidos bajo `## Sesión <fecha de hoy> · inicio HH:MM` (HH:MM = la hora de `**Creada:**`).

**checkpoint**
1. Leer el archivo. Si no existe → responder `⚠️ no existe: <ruta>` y no crear.
2. Elegir el bloque según la regla de sesiones: si el bloque más reciente tiene su último evento a ≤2h de esta llamada y en la misma fecha, escribir ahí. Si no, crear antes de `## Incidencias y solución` el bloque `## Sesión <fecha de hoy> · inicio HH:MM` (HH:MM = hora de esta llamada).
3. Agregar `- DD-MM-YYYY HH:MM — <checkpoint>` al final de esa sesión. Si el checkpoint es un problema resuelto o un camino descartado, agregarlo también en `## Incidencias y solución`. Después, sincronizar `## Pendientes` ítem por ítem con lo que reporta el checkpoint:
   - Trabajo reportado como hecho o resuelto con pendiente existente → marcar `[x]` y anotar `· cierra DD-MM-YYYY`.
   - Cierre no concluyente (parcial, borrador, falta confirmación) o correspondencia ambigua entre checkpoint y pendiente → conservar el ítem sin `[x]`, anotar `— ¿cierra DD-MM-YYYY? revisar` y avisar en la respuesta. Cuando el cierre se confirme, el checkpoint que lo haga marca `[x]`, quita la marca `¿cierra …? revisar` y anota `· cierra DD-MM-YYYY`.
   - Trabajo nuevo pendiente → agregar `- [ ] <texto> — desde DD-MM-YYYY`; si ya existe un pendiente igual o equivalente, conservar el actual sin duplicar.
   - Pendientes que el checkpoint no menciona → conservarlos idénticos, en su mismo orden.
   - Actualizar `**Rama:**` si cambió.
   - Clasificación de tipos: ver `## Tipos de checkpoint`.

**cerrar**
1. Si llegan checkpoints, agregarlos igual que en `checkpoint`. Si no llegan, no crear bloques de sesión vacíos.
2. Estimar la duración y escribirla SIEMPRE, aunque la bitácora tenga un solo checkpoint:
   - Tramo de cada bloque `## Sesión` = último checkpoint − `· inicio HH:MM` del bloque. Si el bloque no lleva `· inicio`, el inicio es su primer checkpoint (o, en el primer bloque, `**Creada:**` si es anterior a su primer checkpoint).
   - Total = suma de los tramos de los bloques. Los días entre sesiones no cuentan: sesiones en días distintos se suman, aunque empiecen a la misma hora, y los huecos entre sesiones tampoco.
   - Formato `Xd Yh Zm` omitiendo las unidades en cero (ej. `4h`, `2d 3h 15m`).
   - Escribir en la cabecera, junto a `**Estado:**`: `- **Duración estimada:** <total>`.
   - Con 2 o más bloques de sesión, agregar el desglose al final del archivo, antes de la firma:
     ```
     ## Duración por sesión
     - Sesión <fecha>: <tramo> (HH:MM → HH:MM)
     ```
3. Cambiar `**Estado:**` a `Cerrada`.
4. Firma: ejecutar con `<raiz_proyecto>` como directorio de trabajo `sh .SAC/memctl.sh get usuario.nombre` y `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` (memctl solo lee; si falla, omitir la firma); si `usuario.incluir_firma_en_documentos` es `true` y `usuario.nombre` no está vacío, agregar al final `> **Generado y revisado por:** <nombre> · <fecha>`. Si falta algo, omitir la firma; no inventar un nombre.

**retomar**
1. Sin slug → listar `bitacora-tecnica/*/bitacora.md` con su título y estado, y responder esa lista.
2. Con slug → leer el archivo y, según la regla de sesiones, abrir bloque nuevo `## Sesión <fecha de hoy> · inicio HH:MM` (HH:MM = hora de la llamada) si el bloque más reciente quedó cerrado por el hueco de 2h u otra fecha.
3. Responder un resumen ≤10 líneas:
   ```
   📋 <título> · <estado> · rama <rama>
   📌 Último checkpoint: <...>
   ✅ Ya hecho (no repetir): • ...
   ⏳ Pendientes: • ...
   ⚠️ Incidencias abiertas: • ...
   ```

**resumen**
1. Sin slug → listar `bitacora-tecnica/*/bitacora.md` con su título y estado, y responder esa lista. Con slug → leer el archivo. **Solo lectura: no escribir nada.**
2. Fecha pedida = campo `fecha` (aceptar `YYYY-MM-DD` o `DD-MM-YYYY`); sin campo, la fecha de hoy. Filtrar los bloques `## Sesión <fecha>` (el header usa `YYYY-MM-DD`).
3. Duración de cada bloque = misma regla que `cerrar`: último checkpoint − `· inicio HH:MM` (sin `· inicio`, el primer checkpoint; o `**Creada:**` si es anterior y es el primer bloque). Excepción: el último bloque del archivo, si su fecha es la de hoy y quedó abierto → hora actual − inicio, marcado `(en curso)`. Bloques sin checkpoints no cuentan.
4. Responder el reporte (formato de tiempo `Xd Yh Zm` como en `cerrar`):
   ```
   📋 Resumen <fecha> · <título>
   ⏱ Estimado: <total> en <n> sesión|sesiones (pluralizar: 1 sesión, 2+ sesiones)
   · HH:MM–HH:MM (<tramo>): <lo hecho en la sesión, 1 línea>
   ```
   Sesión abierta: `· HH:MM–ahora (<tramo>, en curso): …`. Sin bloques ese día → `📅 Sin sesiones el <fecha>`.

## Respuesta

Una línea `✅ creada|actualizada|cerrada: <ruta>` o el `⚠️` correspondiente (en `retomar`, un resumen ≤10 líneas; en `resumen`, el reporte del día). Sin explicar el contenido escrito. Por cada marca `¿cierra …? revisar` agregada, añadir una línea `⚠️ cierre incierto: "<pendiente>" — <motivo>`.
