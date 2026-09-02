# Workflows SAC

Un **workflow** orquesta una secuencia de fases con *gates* (pausas de aprobación),
ejecutada por el agente a través de la tool `workflow-sac`. A diferencia de una skill
(capacidad discreta), un workflow guía un proceso completo paso a paso.

---

## Estructura de un workflow

```
workflows/<nombre-workflow>/
├── workflow.md          # Manifiesto (fuente de verdad) + prosa de comportamiento
├── fases/
│   ├── uno.md           # Script detallado de cada fase (1 fase = 1 archivo)
│   ├── dos.md
│   └── ...
├── templates/           # (opcional) plantillas que las fases instancian
└── artifacts/           # (runtime) salidas generadas por las fases
```

### Regla de oro
> **1 fase lógica = 1 archivo en `fases/`.** El nombre del archivo es libre
> (`uno.md`, `uno_descubrimiento.md`, …); lo que manda es el **orden del manifiesto**.

---

## `workflow.md` — dos secciones con roles distintos

### 1. Frontmatter: el manifiesto `phases` (para la tool)

Es la **fuente de verdad** que la tool `workflow-sac` lee para el orden, los gates y las salidas.

```yaml
---
name: definir-arquitectura-solucion
description: Diseña colaborativamente la arquitectura...
ready: true
phases:
  - file: uno.md
    title: Análisis NFRs y Estilo Arquitectónico
    gate: approval
    output: artifacts/ADR/ADR-001-estilo-arquitectonico.md
  - file: seis.md
    title: Validación Cruzada por Sub-Agente Auditor
    gate: auto
    pre: "Actúa como auditor independiente; solo verifica trazabilidad, no reabras decisiones."
---
```

| Campo | Oblig. | Uso |
|-------|:---:|-----|
| `file` | ✅ | Archivo en `fases/`. Define **orden** e identidad de la fase. |
| `title` | | Nombre legible; lo muestran `next` y `status`. |
| `gate` | | `approval` (pausa y espera OK del usuario) · `auto` (corre y se aprueba sola, sin pausa). Default: `approval`. |
| `output` | | Artefacto esperado de la fase (para documentar/validar). |
| `pre` | | Instrucción de comportamiento que la tool **inyecta antes** del contenido de la fase. |

### 2. Cuerpo (prosa): comportamiento, NO la lista de fases

La lista de fases ya vive en el manifiesto — **no la repitas**. El cuerpo es el
"playbook del director": guía que aplica a todo el workflow.

- **Rol** — cómo debe actuar el agente en todas las fases.
- **Antes de cada fase** — recap de decisiones previas, contexto a cargar, cómo presentar propuestas.
- **Pipeline** — diagrama visual para el humano.
- **Al terminar** — verificaciones finales.

Ver `definir-arquitectura-solucion/workflow.md` como ejemplo de referencia.

---

## `fases/<archivo>.md` — el script de la fase

Instrucciones detalladas que el agente ejecuta. Formato sugerido:

```markdown
# FASE N: Título

**Objetivo:** ...

## Pasos de Ejecución
1. ...
2. ...

## Entregable
- ...
```

---

## Cómo se ejecuta (tool `workflow-sac`)

La tool **entrega y rastrea**; el agente **ejecuta** el markdown. Estado en `.SAC/workflow-state/`.

| Acción | Qué hace |
|--------|----------|
| `list` | Lista los workflows disponibles. |
| `read` | Devuelve el `workflow.md` (pipeline + gates). |
| `next` | **La siguiente fase pendiente** con su nombre exacto. *Úsalo en vez de adivinar.* |
| `execute` | Inyecta el contenido de la fase. **Bloquea si una fase anterior no está aprobada.** |
| `approve` | Marca una fase como aprobada. |
| `status` | Progreso (⏳/🔄/✅) por fase. |
| `reset` | Reinicia el progreso. |

**Flujo recomendado:** `read` → repetir[ `next` → `execute` → (aprobación) → `approve` ] → `status`.

### Qué acciones tocan el estado

El estado vive en `.SAC/workflow-state/<workflow>.state.json`.

| Acción | ¿Escribe estado? | Qué cambia |
|--------|:---:|-----------|
| `list`, `read`, `read_phase`, `next`, `status` | ❌ (solo lee) | — |
| `execute` | ✅ | `current_phase` = fase; `phases[fase].status = in_progress`. Si `gate: auto`, además `= approved`. |
| `approve` | ✅ | `phases[fase].status = approved` + `approved_at`. |
| `reset` | ✅ | reinicia todo el estado. |

> Clave: **`next` NO modifica el estado** — solo lee el manifiesto + el estado y te dice cuál sigue. El estado avanza con `execute` (in_progress) y `approve` (approved).

---

## Ejemplo paso a paso (con el estado)

Workflow `ejemplo` con 3 fases: `uno.md` (approval), `dos.md` (approval), `tres.md` (**auto**).

```
Agente                         Tool                      .SAC/workflow-state/ejemplo.state.json
──────                         ────                      ──────────────────────────────────────
1. read ejemplo         ──►    (devuelve workflow.md)    (sin cambios)

2. next ejemplo         ──►    "(1/3) uno.md"            (sin cambios) — next solo LEE

3. execute uno.md       ──►    inyecta fase + pide OK    current_phase: uno.md
                                                          phases.uno.md: { status: in_progress }

4. (usuario aprueba)
   approve uno.md        ──►    "aprobada"                phases.uno.md: { status: approved, approved_at }

5. next ejemplo         ──►    "(2/3) dos.md"            (sin cambios)

6. execute dos.md       ──►    gate: uno.md ✅ → inyecta  current_phase: dos.md
                                                          phases.dos.md: { status: in_progress }

7. approve dos.md       ──►    "aprobada"                phases.dos.md: { status: approved }

8. next ejemplo         ──►    "(3/3) tres.md [auto]"    (sin cambios)

9. execute tres.md      ──►    gate: dos.md ✅ → inyecta  phases.tres.md: { status: in_progress }
                               fase AUTO: se auto-aprueba → phases.tres.md: { status: approved }
                                                          (no requiere approve del usuario)

10. next ejemplo        ──►    "✅ completo (3/3)"        (sin cambios)
```

**Snapshot final** de `ejemplo.state.json`:
```json
{
  "workflow": "ejemplo",
  "started_at": "2026-09-02T…",
  "current_phase": "tres.md",
  "phases": {
    "uno.md":  { "status": "approved", "started_at": "…", "approved_at": "…" },
    "dos.md":  { "status": "approved", "started_at": "…", "approved_at": "…" },
    "tres.md": { "status": "approved", "started_at": "…", "approved_at": "…" }
  }
}
```

Si en el paso 6 intentaras `execute tres.md` sin aprobar `dos.md`, la tool responde:
`⛔ No puedes ejecutar 'tres.md': la fase anterior 'dos.md' (…) no está aprobada.`

---

## Crear un workflow nuevo

1. Crea `workflows/<nombre>/workflow.md` con frontmatter (`name`, `description`, `ready: true`, `phases`).
2. Crea un archivo por fase en `fases/` (1 fase = 1 archivo).
3. Declara cada fase en el manifiesto `phases` **en orden**, con su `gate` y `output`.
4. Escribe la prosa de comportamiento (rol, antes de cada fase, pipeline).
5. `ready: true` para que el instalador y la tool lo tomen.

---

## Compatibilidad hacia atrás

Si un `workflow.md` **no** tiene manifiesto `phases`, la tool cae a modo *legacy*:
extrae las referencias `./fases/<archivo>.md` del cuerpo, en el orden en que aparecen.
Funciona, pero sin `title`/`gate`/`output`/`pre`. **Se recomienda el manifiesto.**
