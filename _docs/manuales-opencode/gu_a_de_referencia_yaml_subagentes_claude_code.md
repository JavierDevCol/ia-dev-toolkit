# Guía de Referencia: Encabezado YAML (Frontmatter) para Subagentes en Claude Code

Los subagentes en Claude Code se definen mediante archivos Markdown (`.claude/agents/<nombre>.md` o `~/.claude/agents/<nombre>.md`) que inician con un bloque YAML delimitado por `---`.

## 1. Campos Obligatorios

| Campo | Formato / Valores permitidos | Función y comportamiento |
| :--- | :--- | :--- |
| **`name`** | Cadena de texto en minúsculas con guiones (máx. 256 caracteres, sin espacios ni `:`).<br>Ej: `arquitecto-hibrido` | Identificador único del subagente. Es el nombre que usas para invocarlo (`@agent-nombre` o `--agent nombre`) y el que reciben los *hooks* como `agent_type`. |
| **`description`** | Texto descriptivo en lenguaje natural. | **El disparador principal.** Claude lee este campo para decidir cuándo delegar una tarea automáticamente. Incluir frases como *"Úsalo proactivamente cuando..."* mejora la activación automática. |

---

## 2. Control de Herramientas y Capacidades

| Campo | Formato / Valores permitidos | Función y comportamiento |
| :--- | :--- | :--- |
| **`tools`** | Lista YAML o texto separado por comas.<br>Valores comunes: `Read`, `Write`, `Edit`, `MultiEdit`, `Bash`, `Grep`, `Glob`, `LS`, `WebSearch`, `WebFetch`, `Task` (o `Agent`), `Skill`, `NotebookEdit`, `TodoRead`, `TodoWrite`. | Lista blanca (*allowlist*) de herramientas que el subagente puede ejecutar. Si se omite, hereda todas las herramientas disponibles en la sesión principal. |
| **`disallowedTools`** | Lista YAML o texto separado por comas (mismos valores que `tools`). | Lista negra (*denylist*) de herramientas prohibidas. Se eliminan del conjunto heredado o especificado. |
| **`skills`** | Lista YAML de nombres de *skills*.<br>Ej: `[terraform-standards, aws-security]` | Precarga el contenido completo de las *skills* indicadas en el contexto inicial del subagente al arrancar. |
| **`mcpServers`** | Lista con nombres de servidores MCP ya configurados (ej. `github`) o definiciones inline en YAML. | Define qué servidores MCP tiene disponibles exclusivamente este subagente. *(Ignorado en subagentes de plugins)*. |

---

## 3. Modelo, Razonamiento y Permisos

| Campo | Valores permitidos | Función y comportamiento |
| :--- | :--- | :--- |
| **`model`** | • `sonnet`<br>• `opus`<br>• `haiku`<br>• `fable`<br>• `inherit` (hereda el de la sesión)<br>• ID completo de modelo (ej. `claude-sonnet-4-6` o `claude-opus-4-5`) | Define el modelo que ejecutará el subagente. Si se omite, Claude Code usa el orden predeterminado de subagentes o el de la conversación principal. |
| **`effort`** | • `low`<br>• `medium`<br>• `high`<br>• `xhigh`<br>• `max` | Ajusta el nivel de esfuerzo/razonamiento del modelo mientras el subagente está activo. Sobrescribe el nivel de la sesión (pero no la variable `CLAUDE_CODE_EFFORT_LEVEL`). |
| **`permissionMode`** | • `default` (o alias `manual`): pide confirmación normal.<br>• `acceptEdits`: aprueba ediciones de archivos automáticamente.<br>• `auto`: modo autónomo.<br>• `dontAsk`: no solicita confirmaciones interactivas.<br>• `bypassPermissions`: omite todos los chequeos de permisos.<br>• `plan`: modo solo lectura / planificación. | Controla cómo el subagente solicita permisos para ejecutar acciones. *(Ignorado en subagentes de plugins por seguridad)*. |

---

## 4. Contexto, Ejecución y Memoria

| Campo | Valores permitidos | Función y comportamiento |
| :--- | :--- | :--- |
| **`memory`** | • `user` (global en `~/.claude/`)<br>• `project` (compartida en `.claude/`)<br>• `local` (local del proyecto, ignorada por Git) | Habilita memoria persistente entre sesiones para que el subagente guarde aprendizajes y notas propias. |
| **`maxTurns`** | Número entero positivo (ej. `15`). | Límite máximo de turnos agénticos antes de detenerse. Si lo alcanza, devuelve un resultado parcial que puede reanudarse. |
| **`background`** | `true` \| `false` | Si es `true`, fuerza al subagente a ejecutarse siempre en segundo plano incluso si el flujo principal pide esperarlo. |
| **`isolation`** | `worktree` | Ejecuta el subagente dentro de un *git worktree* temporal aislado para que sus cambios no afecten tu directorio de trabajo actual. |
| **`omitClaudeMd`** | `true` \| `false` | Si es `true`, inicia el subagente sin cargar los archivos `CLAUDE.md` del usuario/proyecto, dejando un contexto limpio basado solo en el prompt de delegación. |
| **`autoCompactWindow`** | Número entero `>= 100000` (ej. `120000`). | Reduce el umbral de tokens en el que el subagente compacta automáticamente su propio contexto. |

---

## 5. Automatización, Interfaz y Arranque

| Campo | Valores permitidos | Función y comportamiento |
| :--- | :--- | :--- |
| **`hooks`** | Objeto YAML de eventos (`PreToolUse`, `PostToolUse`, `Stop`, etc.). | Define *hooks* de ciclo de vida que aplican únicamente cuando este subagente está en ejecución. *(Ignorado en plugins)*. |
| **`color`** | • `blue` / `cyan` (análisis/revisión)<br>• `green` (tareas de ejecución/éxito)<br>• `yellow` (validación/precaución)<br>• `red` (seguridad/crítico)<br>• `magenta` (generación/creativo) | Color de identificación visual del subagente en la interfaz de terminal de Claude Code. |
| **`initialPrompt`** | Cadena de texto. | Prompt inicial que se envía automáticamente si inicias toda la sesión directamente con este agente (`claude --agent <nombre>`). |

---

## 6. Plantilla Completa de Ejemplo

```markdown
---
name: arquitecto-hibrido
description: Experto en infraestructura TI, AWS, redes, servidores autoalojados (Proxmox, K3s, Docker), Terraform y Ansible. Úsalo proactivamente cuando se diseñen topologías, se revisen archivos .tf o playbooks, o se evalúen costos, alta disponibilidad y continuidad operativa.
tools:
  - Read
  - Grep
  - Glob
  - Bash
disallowedTools:
  - Write
  - Edit
model: sonnet
effort: high
permissionMode: plan
memory: project
maxTurns: 20
color: cyan
---

# Rol y Perfil Profesional
Actúa como un Arquitecto Principal de Infraestructura Híbrida, AWS y Entornos Autoalojados...
```