# Instalador Modular de squad-skills

> Instalador multiplataforma de skills, agentes, workflows y tools para equipos de desarrollo IA

---

## Instalación Rápida

### Opción 1: Bootstrap (Primera Instalación)

**Linux/Mac:**
```bash
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/squad-skills/main/INSTALACION/bootstrap/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://github.com/JavierDevCol/squad-skills/main/INSTALACION/bootstrap/install.ps1 | iex
```

Después de reiniciar la terminal:
```bash
skills --help                    # Ver ayuda
skills "/home/usuario/proyecto"  # Instalar en un proyecto
```

### Opción 2: Script Directo

```bash
python instalar.py
# o
python instalar.py "C:/mi-proyecto"
```

---

## Uso del Instalador

El instalador ofrece 6 opciones modulares:

```
╔══════════════════════════════════════════════════════════╗
║          INSTALADOR MODULAR — squad-skills              ║
╚══════════════════════════════════════════════════════════╝

¿Qué deseas instalar?

  [1] Skills — Seleccionar skills específicas
  [2] Agents — Seleccionar agentes específicos
  [3] Workflows — Seleccionar workflows (+ tools automáticos)
  [4] Tools — Seleccionar tools individuales
  [5] Team Dev SAC — Skills SAC + Configuración
  [6] Kit Completo — Agents + Skills + Workflows + Tools + Config
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

---

## Estructura del Instalador

```
INSTALACION/
├── README.md              ← Este archivo
├── instalar.py            ← Instalador principal (Python)
└── bootstrap/
    ├── install.sh         ← Bootstrap Linux/Mac
    ├── install.ps1        ← Bootstrap Windows
    ├── skills.sh          ← Comando global Linux/Mac
    └── skills.bat         ← Comando global Windows
```

---

## Requisitos

- **Python 3.8+**
- **Git** (para clonar desde GitHub)

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

---

## Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `skills` | Modo interactivo |
| `skills "RUTA"` | Instalar en la ruta especificada |
| `skills --help` | Mostrar ayuda |

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
