# Instalador de squad-skills

> Instalador multiplataforma de skills y agentes IA

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

El instalador ofrece 4 opciones:

```
[1] Skills       — Seleccionar skills específicas
[2] Agents       — Seleccionar agentes específicos
[3] Team Dev SAC — Skills SAC + Configuración
[4] Todo         — Skills + Agents + Team Dev SAC
```

### Instalar Skills

El instalador categoriza las skills automáticamente:

- **Genéricas** — Sin dependencias especiales
- **Requieren Git** — Necesitan git instalado
- **Requieren Herramientas** — Vault, kubectl, Node.js, etc.
- **Team Dev SAC** — Skills que requieren configuración SAC

### Team Dev SAC

Al instalar cualquier skill SAC, se instala automáticamente:

```
.SAC/
├── config/
│   ├── CONFIG_SYSTEM.yaml
│   └── CONFIG_USER.yaml
├── plantillas/
│   ├── ADR (3 formatos)
│   ├── HU, Bug, Plan
│   └── ... (16 templates)
└── session/
```

### Instalar Agents

Agentes disponibles:

| Agente | Descripción |
|--------|-------------|
| ARQUITECTO-DEVOPS | Arquitecto DevOps y SRE |
| ARQUITECTO-SOFTWARE | Arquitecto de Software |
| DESARROLLADOR | Desarrollador de software |
| PO | Product Owner |

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

### Requisitos por Skill

| Skill | Requisitos |
|-------|------------|
| architecture-inception | Ninguno |
| bitacora-tecnica | Git |
| git-branch-commit | Git |
| handoff-release | Git |
| mermaid-diagram | Ninguno |
| vault-manager | Vault CLI, kubectl |
| pr-config-audit | Git. Opcional: Vault, RabbitMQ |
| ado/* | Azure DevOps MCP server |
| SAC skills | .SAC/config/CONFIG_SYSTEM.yaml |

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
