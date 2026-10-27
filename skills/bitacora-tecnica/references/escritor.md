# Escritor de bitácora (instrucciones para el subagente)

Archivo: `<raiz_proyecto>/bitacora-tecnica/<slug>/bitacora.md`. Plantilla: `../assets/plantilla-bitacora.md` (relativa a este archivo).

## Reglas

- Solo checkpoints de 1–2 líneas que ayuden a retomar o eviten repetir trabajo. Nunca paso a paso.
- Nunca escribir secrets, JWTs, contraseñas, connection strings ni PII: reemplazar por `[REDACTADO]`.
- Evidencias solo como enlaces/rutas; no pegar logs completos.
- Fecha y hora actuales del sistema (`date "+%Y-%m-%d %H:%M"`): la misma hora para todos los checkpoints de una llamada; nunca inventar horas.
- No modificar nada fuera de `bitacora-tecnica/<slug>/`.

## Modos

**crear**
1. Si el archivo ya existe y su `## Objetivo` es de otra tarea → no escribir; responder `⚠️ slug existe con otro objetivo: <ruta>`. Si es la misma tarea → seguir como `checkpoint`.
2. Crear la carpeta (`mkdir -p`) y el archivo desde la plantilla con título, slug, rama y objetivo. Quitar las secciones de ejemplo que queden vacías salvo `## Pendientes / próxima sesión`.
3. Agregar los checkpoints recibidos bajo `## Sesión <fecha de hoy>`.

**checkpoint**
1. Leer el archivo. Si no existe → responder `⚠️ no existe: <ruta>` y no crear.
2. Si no hay `## Sesión <fecha de hoy>`, crearla antes de `## Incidencias y solución`.
3. Agregar `- HH:MM — <checkpoint>` al final de esa sesión. Si el checkpoint es un problema resuelto o un camino descartado, agregarlo también en `## Incidencias y solución`; si es un pendiente, en `## Pendientes` (y marcar `[x]` los pendientes que el checkpoint cierre). Actualizar `**Rama:**` si cambió.

**cerrar**
1. Igual que `checkpoint` con los checkpoints recibidos.
2. Cambiar `**Estado:**` a `Cerrada`.
3. Firma: ejecutar con `<raiz_proyecto>` como directorio de trabajo `sh .SAC/memctl.sh get usuario.nombre` y `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` (memctl solo lee; si falla, omitir la firma); si `usuario.incluir_firma_en_documentos` es `true` y `usuario.nombre` no está vacío, agregar al final `> **Generado y revisado por:** <nombre> · <fecha>`. Si falta algo, omitir la firma; no inventar un nombre.

**retomar**
1. Sin slug → listar `bitacora-tecnica/*/bitacora.md` con su título y estado, y responder esa lista.
2. Con slug → leer el archivo y responder un resumen ≤10 líneas:
   ```
   📋 <título> · <estado> · rama <rama>
   📌 Último checkpoint: <...>
   ✅ Ya hecho (no repetir): • ...
   ⏳ Pendientes: • ...
   ⚠️ Incidencias abiertas: • ...
   ```

## Respuesta

Solo una línea (salvo `retomar`): `✅ creada|actualizada|cerrada: <ruta>` o el `⚠️` correspondiente. Sin explicar el contenido escrito.
