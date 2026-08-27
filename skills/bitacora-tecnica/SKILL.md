---
name: bitacora-tecnica
description: >
  Usa esta skill cuando necesites retomar el contexto de una sesión de
  trabajo previa, documentar decisiones técnicas o el estado actual de
  una tarea. También se activa cuando se solicita crear una bitácora
  de sesión o cuando se va a iniciar/implementar una solución y se
  necesita contexto de trabajo anterior.
compatibility: Requires git
metadata:
  author: CEIBA DevOps
  version: 2.0.0
---

# Skill: Bitácora de Sesiones de Trabajo

Registra el progreso de sesiones de trabajo para retomar contexto más adelante.

## Plantilla

- Plantilla base limpia: `{file:./assets/plantilla-bitacora.md}`

---

## Ruta de Almacenamiento

```
bitacora-tecnica/
├── [slug-tarea]/
│   ├── bitacora.md          ← Registro principal de la sesión
│   └── EVIDENCIAS/          ← Logs, queries, scripts, screenshots
│       ├── error_YYYY-MM-DD.txt
│       ├── query_diagnostico.sql
│       └── ...
```

El `slug-tarea` se genera así:
- Si hay un ID de referencia (WI, issue, ticket): `[ID]-[descripcion-corta]`
- Si es una tarea general: `[descripcion-kebab-case]`
- Ejemplos: `131735-consultar-saldo`, `optimizar-queries-dashboard`, `hotfix-login-timeout`

---

## Flujo Principal

### Al CREAR un registro (fin de sesión o checkpoint)

Preguntar al usuario:

> **¿Qué tipo de registro deseas crear?**
> - **[F]** Fin de sesión — Resumir todo lo realizado
> - **[C]** Checkpoint — Guardar estado intermedio sin cerrar
> - **[D]** Decisión técnica — Documentar una decisión y su justificación

#### Paso 1 — Identificar la tarea

Preguntar: "¿Cuál es el identificador o nombre de la tarea?"
- Si ya hay contexto en la conversación, usarlo directamente.
- Si no, pedir una descripción breve para generar el slug.

#### Paso 2 — Verificar si ya existe bitácora

```bash
ls bitacora-tecnica/[slug-tarea]/
```

- Si existe `bitacora.md` → leerlo para agregar de forma incremental.
- Si no existe → crear directorio y plantilla vacía.

#### Paso 3 — Recopilar información de la sesión

El agente debe_EXTRAER_ del contexto de la conversación:

| Dato | Fuente |
|------|--------|
| Archivos modificados | `git diff --name-only` o contexto de la sesión |
| Commits realizados | `git log --oneline -5` o contexto |
| Errores encontrados | Mensajes de error en la conversación |
| Decisiones tomadas | Acuerdos con el usuario |
| Estado actual | Última acción ejecutada |
| Pendientes | Lo que falta por hacer |

#### Paso 4 — Generar el registro

Crear o actualizar `bitacora.md` usando la plantilla de `{file:./assets/plantilla-bitacora.md}`.

#### Paso 5 — Guardar evidencias (si aplican)

Guardar en `EVIDENCIAS/`:
- Queries SQL o scripts ejecutados
- Logs de error relevantes
- Capturas de terminal
- Configuraciones utilizadas

---

### Al RETOMAR trabajo (inicio de sesión)

#### Paso 1 — Buscar bitácoras existentes

```bash
ls bitacora-tecnica/
```

Si hay múltiples bitácoras, preguntar:

> **¿Qué tarea deseas retomar?**
> - [1] [slug-tarea-1] — [título descriptivo del bitacora.md]
> - [2] [slug-tarea-2] — [título descriptivo del bitacora.md]
> - [N] Crear nueva bitácora

#### Paso 2 — Leer la bitácora

Leer `bitacora.md` completo y `EVIDENCIAS/` si existe.

#### Paso 3 — Presentar contexto resumido

Mostrar al usuario un resumen conciso:

```
📋 TAREA: [título]
   Última actualización: [fecha]
   Estado: [En progreso / Bloqueado / Pendiente]

📌 ÚLTIMO PUNTO:
   [Descripción breve de dónde se quedó]

🔄 LO REALIZADO:
   • [Acción 1]
   • [Acción 2]
   • [Acción 3]

⏳ PENDIENTES:
   • [Pendiente 1]
   • [Pendiente 2]

⚠️ BLOQUEANTES (si existen):
   • [Bloqueante 1]

🔗 EVIDENCIAS: [lista de archivos en EVIDENCIAS/]
```

#### Paso 4 — Preguntar continuación

> **¿Qué deseas hacer?**
> - **[C]** Continuar desde donde quedó
> - **[A]** Actualizar el registro con nuevo progreso
> - **[N]** Cerrar esta bitácora y crear nueva

---

## Plantilla del Registro

Usar la estructura de `{file:./assets/plantilla-bitacora.md}`. Ejemplo:

```markdown
# Sesión: Optimización de queries del dashboard
- **ID:** 2026-08-24-opt-dashboard
- **Fecha inicio:** 2026-08-24 09:15
- **Última actualización:** 2026-08-24 15:30
- **Estado:** En progreso
- **Rama de Trabajo:** `feat/optimize-dashboard-queries`
- **Tags:** `performance`, `sql`, `dashboard`
- **Ambiente:** Local → DES

## Tiempo
- **Invertido:** 6h
- **Estimado restante:** 2h
- **Deadline:** 2026-08-26

## Objetivo de la Sesión
Las queries del dashboard principal tardaban >3s. Reducir a <500ms.

## Lo Realizado
- **Commits:**
  - `a1b2c3d` — refactor: add composite index on transactions
  - `e4f5g6h` — fix: eliminate N+1 query in dashboard handler
- **Cambios en Código:**
  - `src/db/queries/dashboard.sql` — Reescritura completa con JOINs
  - `src/handlers/dashboard.ts` — Batch loading en vez de N+1
- **Decisiones Técnicas:**
  - Índices compuestos vs separados → Mejor rendimiento para filtros combinados
  - Paginación cursor-based vs offset → Evita problemas con datos concurrentes

## Evidencias
- **Query optimizada:** {file:./EVIDENCIAS/query_dashboard_optimized.sql}
- **Benchmark:** {file:./EVIDENCIAS/benchmark_results.txt}

## Estado Actual
Las queries están optimizadas y funcionando en local. Falta validar en DES.

### Pendientes
- [ ] Subir cambios a rama feature
- [ ] Crear PR
- [ ] Validar en DES
- [ ] Documentar en release notes

### Bloqueantes
- [Ninguno actualmente]

### Tests
- [x] Unitarios: OK (23/23 pasando)
- [x] Integración: OK (8/8 pasando)
- [ ] E2E: Pendiente en DES

### Rollback Plan
Si el fix genera regresión:
1. `git revert e4f5g6h` (N+1 fix)
2. `git revert a1b2c3d` (índice)
3. Verificar que el dashboard vuelve a >3s (esperado)

## Próxima Sesión
1. Subir cambios: `git push origin feat/optimize-dashboard-queries`
2. Crear PR con descripción de benchmark
3. Validar queries en DES con `EXPLAIN ANALYZE`
4. Si OK → merge y documentar en release notes
```

---

## Reglas Obligatorias

1. **Leer antes de escribir.** Siempre leer la bitácora existente antes de agregar contenido.
2. **Contenido técnico directo.** Sin introducciones, sin resúmenes narrativos.
3. **Actualización incremental.** No borrar contenido previo, solo agregar o actualizar secciones.
4. **Sanitización estricta.** Prohibido guardar JWTs, contraseñas, connection strings o PII.
5. **Estado claro.** Usar siempre los campos: Estado, Última actualización, Pendientes.
6. **Contexto de reanudación.** Siempre incluir la sección "Contexto para Retomar" con pasos concretos.
7. **Evidencias referenciadas.** Guardar archivos grandes en `EVIDENCIAS/` y referenciarlos desde bitacora.md.

---

## Gotchas

- **Múltiples sesiones en paralelo:** Crear un directorio por tarea, no por sesión. Si se trabaja en varias cosas, usar bitácoras separadas.
- **Bitácora muy larga:** Si supera 300 líneas, dividir en secciones por fecha o crear un resumen ejecutivo al inicio.
- **Pérdida de contexto:** Si la conversación es muy larga, leer solo la sección "Estado Actual" y "Contexto para Retomar".
- **Permisos de escritura:** Verificar acceso a `bitacora-tecnica/` antes de escribir.
