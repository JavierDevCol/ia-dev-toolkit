---
name: bitacora-tecnica
description: >
  Usa esta skill cuando necesites retomar contexto de una sesión previa,
  documentar decisiones técnicas, registrar estado actual de una tarea
  o crear una bitácora de sesión. Se activa al inicio o fin de una
  sesión de trabajo técnica.
---

# Bitácora de Sesiones de Trabajo

## Overview

Registra progreso de sesiones de trabajo para retomar contexto de forma incremental.

## When to Use

- Fin de sesión: resumir lo realizado y pendientes
- Checkpoint intermedio: guardar estado sin cerrar
- Decisión técnica: documentar decisión y justificación
- Inicio de sesión: retomar contexto de trabajo anterior

### Cuándo NO usar

- Para documentación formal de proyecto (usar wiki o README)
- Para logs de aplicación o monitoreo de producción
- Para notas personales no relacionadas con tareas técnicas

## Implementation

### Plantilla

- Plantilla base: `{file:./assets/plantilla-bitacora.md}`

### Ruta de Almacenamiento

```
bitacora-tecnica/
├── [slug-tarea]/
│   ├── bitacora.md          ← Registro principal
│   └── EVIDENCIAS/          ← Logs, queries, scripts, screenshots
```

**Generación de slug:** `[ID]-[descripcion]` si hay ID de referencia, o `[descripcion-kebab-case]` si es general.

### Al CREAR un registro

Preguntar tipo de registro: **[F]** Fin de sesión · **[C]** Checkpoint · **[D]** Decisión técnica

1. **Identificar tarea:** usar contexto o pedir descripción breve
2. **Verificar si ya existe:** `ls bitacora-tecnica/[slug-tarea]/` → si existe, leer y agregar incrementalmente
3. **Recopilar info:** archivos modificados (`git diff --name-only`), commits (`git log --oneline -5`), errores, decisiones, estado actual, pendientes
4. **Generar registro:** crear o actualizar `bitacora.md` con la plantilla
5. **Guardar evidencias:** SQL, logs, configs en `EVIDENCIAS/`

### Al RETOMAR trabajo

1. **Buscar bitácoras:** `ls bitacora-tecnica/` → si hay múltiples, preguntar cuál retomar
2. **Leer bitácora:** `bitacora.md` completo + `EVIDENCIAS/`
3. **Presentar resumen:**

```
📋 TAREA: [título]   |   📌 ÚLTIMO PUNTO: [dónde quedó]
🔄 REALIZADO: • [acción]   |   ⏳ PENDIENTES: • [pendiente]
⚠️ BLOQUEANTES: • [si existen]   |   🔗 EVIDENCIAS: [archivos]
```

4. **Preguntar continuación:** **[C]** Continuar · **[A]** Actualizar registro · **[N]** Cerrar y crear nueva

## Quick Reference

| Operación | Comando/Acción |
|-----------|----------------|
| Verificar bitácora existente | `ls bitacora-tecnica/[slug]/` |
| Archivos modificados | `git diff --name-only` |
| Últimos commits | `git log --oneline -5` |
| Referenciar plantilla | `{file:./assets/plantilla-bitacora.md}` |
| Guardar evidencias | `bitacora-tecnica/[slug]/EVIDENCIAS/` |

## Common Mistakes

- **Múltiples sesiones en paralelo:** Un directorio por tarea, no por sesión; usar bitácoras separadas
- **Bitácora >300 líneas:** Dividir por fecha o crear resumen ejecutivo al inicio
- **Pérdida de contexto:** Si la conversación es larga, leer solo "Estado Actual" y "Contexto para Retomar"
- **Permisos de escritura:** Verificar acceso a `bitacora-tecnica/` antes de escribir
- **Olvidar leer antes de escribir:** Siempre leer bitácora existente antes de agregar contenido
- **Guardar secrets:** Prohibido guardar JWTs, contraseñas, connection strings o PII
