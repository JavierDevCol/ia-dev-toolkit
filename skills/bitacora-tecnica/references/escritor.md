# Escritor de bitácora (instrucciones para el subagente)

Archivo: `<raiz_proyecto>/bitacora-tecnica/<slug>/bitacora.md`. Plantilla: `../assets/plantilla-bitacora.md` (relativa a este archivo).

## Reglas

- Solo checkpoints de 1–2 líneas que ayuden a retomar o eviten repetir trabajo. Nunca paso a paso.
- Nunca escribir secrets, JWTs, contraseñas, connection strings ni PII: reemplazar por `[REDACTADO]`.
- Evidencias solo como enlaces/rutas; no pegar logs completos.
- Fecha y hora actuales del sistema (`date "+%d-%m-%Y %H:%M"`): la misma hora para todos los checkpoints de una llamada; nunca inventar horas. Cada checkpoint lleva fecha y hora (`DD-MM-YYYY HH:MM`) para distinguir horas iguales en días distintos.
- No modificar nada fuera de `bitacora-tecnica/<slug>/`.

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
3. Agregar `- DD-MM-YYYY HH:MM — <checkpoint>` al final de esa sesión. Si el checkpoint es un problema resuelto o un camino descartado, agregarlo también en `## Incidencias y solución`; si es un pendiente, en `## Pendientes` (y marcar `[x]` los pendientes que el checkpoint cierre). Actualizar `**Rama:**` si cambió.

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

## Respuesta

Solo una línea (salvo `retomar`): `✅ creada|actualizada|cerrada: <ruta>` o el `⚠️` correspondiente. Sin explicar el contenido escrito.
