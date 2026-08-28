# Instalador Modular de ia-dev-toolkit

> Instalador multiplataforma de skills, agentes, workflows y tools para equipos de desarrollo IA

---

## Instalación Rápida

### Opción 1: Bootstrap (Primera Instalación)

**Linux/Mac:**
```bash
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://github.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
```

Después de reiniciar la terminal:
```bash
diat                          # Ver comandos disponibles
diat --install                # Instalar en ruta actual
diat --install /mi-proyecto   # Instalar en ruta específica
```

### Opción 2: Script Directo

```bash
python instalar.py
# o
python instalar.py "C:/mi-proyecto"
```

---

## Uso del Instalador

El instalador ofrece 7 opciones modulares:

```
╔══════════════════════════════════════════════════════════╗
║          INSTALADOR MODULAR — ia-dev-toolkit              ║
╚══════════════════════════════════════════════════════════╝

¿Qué deseas instalar?

  [1] Skills — Seleccionar skills específicas
  [2] Agents — Seleccionar agentes específicos
  [3] Workflows — Seleccionar workflows (+ tools automáticos)
  [4] Tools — Seleccionar tools individuales
  [5] Team Dev SAC — Skills SAC + Configuración
  [6] Kit Completo — Agents + Skills + Workflows + Tools + Config
  [7] Alma — Personalidad del agente (ALMA.md)
  [Q] Salir
```

### Formato de Selección con Checkboxes

Cada componente muestra:
- **Checkbox** `[x]` seleccionado / `[ ]` no seleccionado
- **Descripción** corta del componente
- **Dependencias** requeridas (si aplica)

```
══════════════════════════════════════════════════════════════════════
  📦 SKILLS DISPONIBLES
══════════════════════════════════════════════════════════════════════
  [ ]  1. bitacora-tecnica                 — Registra progreso de sesiones
  [x]  2. git-branch-commit                — Gestiona ramas y commits | deps: Git
  [ ]  3. vault-manager                    — Gestiona secretos Vault | deps: Vault CLI
  [x]  4. ado-wi-comments                  — Comentarios en Work Items | deps: Azure DevOps MCP

──────────────────────────────────────────────────────────────────────
  Comandos: [número] toggle | [T] Todas | [N] Ninguna | [V] Volver
──────────────────────────────────────────────────────────────────────
```

---

## Opciones de Instalación

### [1] Skills — Seleccionar skills específicas

Muestra todas las skills disponibles con checkboxes. Puedes:
- Toggle individual con número
- Seleccionar todas con `[T]`
- Deseleccionar todas con `[N]`

Al instalar skills SAC, se instala automáticamente la configuración `.SAC/`.

### [2] Agents — Seleccionar agentes específicos

Agentes disponibles:

| Agente | Descripción |
|--------|-------------|
| PO | Product Owner — Transforma visión en backlog priorizado |
| ARQUITECTO-SOFTWARE | Arquitecto de Software — Diseño, trade-offs y ADRs |
| ARQUITECTO-DEVOPS | DevOps/SRE — Pipelines, IaC y observabilidad |
| DESARROLLADOR | Desarrollador — Código limpio, TDD y patrones |

### [3] Workflows — Seleccionar workflows (+ tools automáticos)

Workflows disponibles:

| Workflow | Descripción | Dependencias |
|----------|-------------|--------------|
| definir-vision-producto | Transforma idea de negocio en Visión | ninguna |
| definir-arquitectura-solucion | Diseña arquitectura con ADRs por fase | Visión de Producto |
| gestionar-backlog-roadmap | Sincroniza backlog con WSJF | ADRs + Visión |

**Importante:** Al instalar workflows, se instalan automáticamente los tools requeridos.

### [4] Tools — Seleccionar tools individuales

Tools disponibles:

| Tool | Descripción |
|------|-------------|
| workflow-discover | Lista workflows disponibles desde .SAC/workflows/ |

### [5] Team Dev SAC — Skills SAC + Configuración

Instala las 10 skills del pipeline SAC más la configuración:

```
.SAC/
├── config/
│   ├── CONFIG_SYSTEM.yaml
│   └── CONFIG_USER.yaml
└── session/
```

Skills SAC:
- analizar-calidad-codigo
- ejecutar-plan
- init-reglas-arquitectonicas
- planificar-hu
- refinar-hu
- registrar-hallazgo
- sincronizar-backlog
- tomar-contexto
- validar-ca
- validar-hu

### [6] Kit Completo — Agents + Skills + Workflows + Tools + Config

Instala todo el ecosistema:
- 4 agentes
- 34+ skills
- 3 workflows
- Tools requeridos
- Configuración `.SAC/`

### [7] Alma — Personalidad del agente

Copia el contenido de `ALMA.md` al archivo de personalidad del proyecto.

**Comportamiento según plataforma:**

| Plataforma | Archivo creado/actualizado |
|---|---|
| `.claude/` | `claude.md` |
| `.opencode/` | `opencode.md` |
| `.agent/` | `agent.md` |
| Ninguna (default) | `agent.md` |

**Reglas:**
- Siempre agrega el contenido **AL INICIO**
- Si ya existe contenido, lo deja **por debajo**
- Si no existe ningún archivo, crea el apropiado

---

## CLI `diat`

Comando principal del toolkit:

| Comando | Función |
|---|---|
| `diat` | Mostrar menú de comandos disponibles |
| `diat --help` | Mostrar ayuda detallada |
| `diat --version` | Mostrar versión actual |
| `diat --check` | Verificar requisitos del sistema |
| `diat --install [/ruta]` | Instalar componentes en proyecto |
| `diat --update [/ruta]` | Actualizar componentes en proyecto |
| `diat --status [/ruta]` | Mostrar estado de instalación |
| `diat --list` | Listar componentes en cache |
| `diat --alma [/ruta]` | Instalar personalidad del agente |

**Ejemplos:**
```bash
diat                          # Ver comandos disponibles
diat --install                # Instalar en ruta actual
diat --install /mi-proyecto   # Instalar en ruta específica
diat --update                 # Actualizar ruta actual
diat --status                 # Ver estado ruta actual
diat --alma                   # Instalar personalidad
```

---

## Orden de Prioridad de Plataformas

El instalador detecta automáticamente la plataforma del proyecto:

| Prioridad | Plataforma | Skills en |
|---|---|---|
| 1 | `.claude/` | `.claude/skills/` |
| 2 | `.opencode/` | `.opencode/skills/` |
| 3 | `.agent/` | `.agent/skills/` |
| Default | `.agent/` | `.agent/skills/` |

---

## Estructura del Instalador

```
INSTALACION/
├── README.md              ← Este archivo
├── instalar.py            ← Instalador principal (Python)
├── diat                   ← CLI principal (Linux/Mac)
├── diat.bat               ← CLI principal (Windows)
└── bootstrap/
    ├── install.sh         ← Bootstrap Linux/Mac
    ├── install.ps1        ← Bootstrap Windows
    ├── skills.sh          ← Wrapper global Linux/Mac
    └── skills.bat         ← Wrapper global Windows
```

---

## Requisitos

- **Python 3.8+**

### Requisitos por Componente

| Componente | Requisitos |
|------------|------------|
| Skills genéricas | Ninguno |
| git-branch-commit | Git |
| vault-manager | Vault CLI |
| ado/* skills | Azure DevOps MCP server |
| SAC skills | .SAC/config/CONFIG_SYSTEM.yaml |
| Workflows | Ninguno (instalan tools automáticamente) |
| Agentes | Ninguno |
| Alma | Ninguno |

---

## Solución de Problemas

### "Python no encontrado"

```bash
# Linux/Mac
sudo apt install python3
# o
brew install python3

# Windows
winget install Python.Python.3.11
```

### "Git no encontrado"

```bash
# Linux/Mac
sudo apt install git

# Windows
winget install Git.Git
```

### "Permission denied" en Linux/Mac

```bash
chmod +x install.sh
./install.sh
```
