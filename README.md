# DIAT (IA DEV TOOLKIT)

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)
[![Versión](https://img.shields.io/badge/versión-v0.2.2-blue.svg)]()

> Toolkit multiplataforma de skills, agents, workflows y tools para equipos de desarrollo IA con OpenCode/Claude Code.

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Instalación](#instalación)
- [Uso](#uso)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Pruebas](#pruebas)
- [Créditos](#créditos)
- [Licencia](#licencia)

---

## Descripción

DIAT es un ecosistema completo para potenciar equipos de desarrollo con agentes de IA. Incluye:

- **42+ skills** para AI agents (gestión de HU, calidad de código, seguridad, Git, ADO, ADRs, etc.)
- **4 agents** especializados (PO, Arquitecto Software, Arquitecto DevOps, Desarrollador)
- **3 workflows** de proceso (visión producto, arquitectura solución, backlog roadmap)
- **CLI `diat`** multiplataforma para instalación y gestión

---

## Instalación

Para instrucciones detalladas de instalación, consulta [INSTALACION/README.md](INSTALACION/README.md).

### Resumen rápido

**Linux/Mac:**
```bash
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
```

**Versión de prueba (canal de prueba):**
```bash
# Instala el CLI y componentes desde una rama, tag o commit sin publicar en main
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | DIAT_REF=v1.2.3-test bash
```
```powershell
$env:DIAT_REF="v1.2.3-test"; irm https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.ps1 | iex
```
Tras la instalación, `DIAT_REF` sigue siendo útil: `DIAT_REF=feature/x diat --install` y
`DIAT_REF=feature/x diat --update` prueban componentes desde esa ref. `diat --status` muestra
la ref activa (ver sección "Canales de prueba" en `INSTALACION/README.md`).

**Python:**
```bash
python instalar.py
```

### Prerrequisitos

- **Python 3.8+**
- **Git** (para skills de Git)
- **Azure DevOps MCP** (para skills ADO)
- **Vault CLI** (para vault-manager)

---

## Uso

### Comandos CLI `diat`

| Comando | Descripción |
|---------|-------------|
| `diat` | Menú de comandos |
| `diat --help` | Ayuda detallada |
| `diat --version` | Versión actual |
| `diat --check` | Verificar requisitos |
| `diat --install [/ruta]` | Instalar componentes |
| `diat --update [/ruta]` | Actualizar componentes |
| `diat --status [/ruta]` | Estado de instalación |
| `diat --list` | Listar componentes en cache |
| `diat --alma [/ruta]` | Instalar personalidad del agente |

### Ejemplos

```bash
# Verificar requisitos del sistema
diat --check

# Instalar toolkit en proyecto
diat --install ~/mi-proyecto

# Verificar estado
diat --status ~/mi-proyecto

# Instalar personalidad del agente
diat --alma ~/mi-proyecto
```

---

## Características

- **Multiplataforma**: Linux, Mac, Windows
- **Modular**: Instala solo lo que necesitas
- **Skills**: 42+ habilidades para AI agents
- **Agents**: 4 roles especializados (PO, Arquitecto Software, DevOps, Desarrollador)
- **Workflows**: 3 flujos de proceso automatizados
- **CLI `diat`**: Interfaz de línea de comandos completa
- **Bootstrap**: Instalación rápida con curl/irm

---

## Tecnologías

- **Python 3.8+** - Instalador principal
- **Bash/PowerShell** - Scripts de instalación
- **TypeScript** - Tools y plugins
- **Docker** - Contenedor OpenCode
- **OpenCode AI** - Plataforma de AI agents
- **Claude Code** - Compatible con Claude Code
- **MCP Servers** - Azure DevOps, Context7, SonarQube

---

## Estructura del Proyecto

```
DIAT/
├── INSTALACION/              # Instalador multiplataforma
│   ├── instalar.py           # Instalador principal (Python)
│   ├── diat                  # CLI Linux/Mac
│   ├── diat.bat              # CLI Windows
│   └── bootstrap/            # Scripts de instalación rápida
├── skills/                   # 42+ skills para AI agents
├── agents/                   # 4 agents especializados
├── workflows/                # 3 workflows de proceso
├── plugins/                  # Plugins V2 de OpenCode (workflow-sac)
├── tools/                    # Tools legacy (V1)
├── config/                   # Configuración del sistema
├── tests/                    # Pruebas E2E
└── docs/                     # Documentación
```

---

## Pruebas

El proyecto incluye 11 escenarios de pruebas E2E.

### Ejecutar pruebas

```bash
# Ejecutar todas las pruebas
cd tests/e2e
./run-all.sh

# Ejecutar setup primero
./setup.sh
```

### Escenarios de prueba

- Flujo feature
- Flujo bug
- Prerrequisitos
- Transiciones
- Detección de modo
- Filesystem
- Escenarios específicos
- SAC core
- Git-release
- Documentación
- ADO meta

---

## Créditos

- [JavierDevCol](https://github.com/JavierDevCol) - Autor principal

---

## Licencia

Distribuído bajo la licencia MIT. Ver `LICENSE` para más información.
