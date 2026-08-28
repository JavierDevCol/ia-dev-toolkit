# Plan: Actualizar Bootstrap para instalar comando `diat`

## Contexto

El bootstrap actual (`install.sh` / `install.ps1`) crea un comando global llamado `skills` que ejecuta `instalar.py` y clona el repo completo.

El usuario quiere:
1. Comando global se llame `diat` (acrónimo de **IA** **D**ev **T**oolkit)
2. **NO clonar el repo** — solo descargar el script `diat` (~10KB)
3. `diat --install` muestra menú, descarga bajo demanda, instala
4. `diat --update` busca instalación en ruta actual o ruta proporcionada

## Diseño de Comandos

| Comando | Función |
|---|---|
| `diat` | Mostrar menú de comandos disponibles |
| `diat --help` | Mostrar ayuda detallada |
| `diat --version` | Mostrar versión actual |
| `diat --check` | Verificar requisitos del sistema |
| `diat --status` | Mostrar estado en ruta actual o `/ruta` |
| `diat --install` | Menú selección → descarga bajo demanda → instala |
| `diat --update` | Actualizar componentes en ruta actual o `/ruta` |
| `diat --list` | Listar componentes disponibles en cache |
| `diat --alma` | Instalar personalidad del agente (AGENTS.md) |

## Orden de Prioridad de Plataformas

| Prioridad | Plataforma | Archivo de personalidad |
|---|---|---|
| 1 | `.claude/` | `claude.md` |
| 2 | `.opencode/` | `opencode.md` |
| 3 | `.agent/` | `agent.md` |
| Default | `.agent/` | `agent.md` |

## Comando `--alma` (Personalidad)

**Qué hace:** Copia contenido de `AGENTS.md` al archivo de personalidad del proyecto.

**Reglas:**
- Siempre agrega el contenido **AL INICIO**
- Si ya existe contenido, lo deja **por debajo**
- Si no existe ningún archivo, crea el apropiado según la plataforma

**Ejemplo:**
```
diat --alma                    # Usar ruta actual
diat --alma /mi/proyecto       # Usar ruta específica
```

## Comportamiento de Rutas

Todos los comandos que aceptan `/ruta` funcionan así:

```
diat --install              → Usa ruta actual (pwd)
diat --install /mi/proyecto → Usa ruta proporcionada
diat --update               → Busca instalación en ruta actual
diat --update /mi/proyecto  → Busca instalación en ruta proporcionada
diat --status               → Muestra estado en ruta actual
diat --status /mi/proyecto  → Muestra estado en ruta proporcionada
```

## Flujo de `--install`

```
diat --install [/ruta]
    ↓
1. Mostrar menú de selección con checkboxes
    ↓
2. Usuario selecciona componentes (skills, agents, workflows, tools, config)
    ↓
3. Descargar SOLO los componentes seleccionados desde GitHub API
    ↓
4. Instalar en ruta actual o ruta proporcionada
    ↓
5. Mostrar resumen de instalación
```

### Ejemplo de menú:

```
══════════════════════════════════════════════════════════════════════
  📦 COMPONENTES DISPONIBLES
══════════════════════════════════════════════════════════════════════

  👤 AGENTES:
  [ ] 1. PO                    — Product Owner
  [ ] 2. ARQUITECTO-SOFTWARE   — Arquitecto de Software
  [ ] 3. ARQUITECTO-DEVOPS     — DevOps/SRE
  [ ] 4. DESARROLLADOR         — Desarrollador

  🔧 SKILLS SAC:
  [ ] 5. tomar-contexto        — Detecta tecnología y arquitectura
  [ ] 6. refinar-hu            — Refina HUs con criterios SMART
  ...

  📋 WORKFLOWS:
  [ ] 15. definir-vision-producto     — Transforma idea en Visión
  [ ] 16. definir-arquitectura-solucion — Diseña arquitectura
  ...

  🛠️ TOOLS:
  [ ] 19. workflow-discover    — Lista workflows disponibles

  [T] Todas | [N] Ninguna | [S] Solo SAC | [A] Solo Agentes
──────────────────────────────────────────────────────────────────────
  Selección: 
```

## Flujo de `--update`

```
diat --update [/ruta]
    ↓
1. Buscar instalación previa en ruta (.opencode/ o .SAC/)
    ↓ (si no existe)
2. Mostrar error: "No se encontró instalación. Usa --install primero"
    ↓ (si existe)
3. Detectar qué componentes están instalados
    ↓
4. Descargar última versión de esos componentes
    ↓
5. Actualizar en la ruta
    ↓
6. Mostrar resumen de cambios
```

## Cache de Componentes

Los componentes se cachean después de la primera descarga:

```
~/.local/share/ia-dev-toolkit/
└── components/          ← Cache (se descarga con --install)
    ├── skills/
    ├── agents/
    ├── workflows/
    ├── tools/
    └── config/
```

- `--install` descarga componentes si no están en cache
- `--install` usa cache si ya existe (no re-descarga)
- `--update` siempre descarga última versión (fuerza re-descarga)
- `--list` muestra componentes del cache

## Plan de Cambios

### 1. `install.sh` — Reescritura mayor

**Eliminar:**
- Clon de repo
- Creación de wrapper que ejecuta `instalar.py`

**Agregar:**
- Descarga directa de `diat` desde GitHub (raw content)

**Nuevo `install.sh`:**
```bash
#!/bin/bash
set -e

DIAT_URL="https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/diat"
BIN_PATH="$HOME/.local/bin"

# Verificar Python
check_prerequisites() { ... }

# Crear directorio
mkdir -p "$BIN_PATH"

# Descargar diat
echo "📦 Descargando diat..."
curl -fsSL "$DIAT_URL" -o "$BIN_PATH/diat"
chmod +x "$BIN_PATH/diat"

# Verificar PATH
add_to_path() { ... }

# Resumen
echo "✅ diat instalado en $BIN_PATH/diat"
echo ""
echo "🚀 Comandos disponibles:"
echo "   diat                    Ver comandos disponibles"
echo "   diat --install          Instalar componentes"
echo "   diat --help             Ver ayuda"
```

### 2. `diat` — Modificaciones principales

**Función `show_menu()`:**
```python
def show_menu():
    """Mostrar menú de comandos disponibles."""
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    diat — IA Dev Toolkit CLI                  ║
╚═══════════════════════════════════════════════════════════════╝

Comandos disponibles:

  diat --help              Mostrar ayuda detallada
  diat --version           Mostrar versión actual
  diat --check             Verificar requisitos del sistema
  diat --install [/ruta]   Instalar componentes en proyecto
  diat --update [/ruta]    Actualizar componentes en proyecto
  diat --status [/ruta]    Mostrar estado de instalación
  diat --list              Listar componentes en cache

Ejemplos:
  diat --install                    # Instalar en ruta actual
  diat --install /home/user/proy    # Instalar en ruta específica
  diat --update                     # Actualizar ruta actual
  diat --update /home/user/proy     # Actualizar ruta específica
""")
```

**Función `resolve_path()`:**
```python
def resolve_path(arg_index=2):
    """Resolver ruta: argumento proporcionado o ruta actual."""
    if len(sys.argv) > arg_index and not sys.argv[arg_index].startswith("-"):
        return Path(sys.argv[arg_index]).resolve()
    return Path.cwd().resolve()
```

**Función `cmd_install()`:**
```python
def cmd_install():
    """Mostrar menú, descargar bajo demanda, instalar."""
    project_path = resolve_path()

    print(f"📍 Ruta de instalación: {project_path}")

    # Verificar que la ruta existe
    if not project_path.exists():
        create = input(f"  La ruta no existe. ¿Crearla? (s/N): ").strip().lower()
        if create != 's':
            print("❌ Instalación cancelada")
            return
        project_path.mkdir(parents=True, exist_ok=True)

    # Mostrar menú de selección
    selected = show_install_menu()

    if not selected:
        print("❌ No se seleccionaron componentes")
        return

    # Descargar componentes seleccionados (si no están en cache)
    components_path = ensure_components(selected)

    # Instalar componentes seleccionados
    install_selected(selected, project_path, components_path)
```

**Función `show_install_menu()`:**
```python
def show_install_menu():
    """Mostrar menú de selección con checkboxes."""
    # Categorías de componentes
    categories = {
        "👤 AGENTES": ["PO", "ARQUITECTO-SOFTWARE", "ARQUITECTO-DEVOPS", "DESARROLLADOR"],
        "🔧 SKILLS SAC": ["tomar-contexto", "refinar-hu", "validar-hu", ...],
        "📋 WORKFLOWS": ["definir-vision-producto", "definir-arquitectura-solucion", ...],
        "🛠️ TOOLS": ["workflow-discover"]
    }

    # Mostrar checkboxes
    # Permitir selección por número, T (todas), N (ninguna)
    # Retornar lista de componentes seleccionados
```

**Función `cmd_update()`:**
```python
def cmd_update():
    """Actualizar componentes en proyecto existente."""
    project_path = resolve_path()

    # Buscar instalación previa
    if not find_installation(project_path):
        print("❌ No se encontró instalación previa")
        print("   Usa: diat --install")
        return

    # Detectar componentes instalados
    installed = detect_installed(project_path)

    # Descargar última versión
    components_path = download_components(force=True)

    # Actualizar componentes
    update_components(installed, project_path, components_path)
```

**Función `ensure_components()`:**
```python
def ensure_components(selected=None):
    """Verificar/descargar componentes necesarios."""
    components_path = get_components_path()

    # Si hay cache y no se fuerza descarga, usar cache
    if components_path.exists() and (components_path / "skills").exists():
        return components_path

    # Descargar componentes
    print("📥 Descargando componentes...")
    return download_from_github(components_path)
```

**Función `detect_installed()`:**
```python
def detect_installed(project_path):
    """Detectar qué componentes están instalados en un proyecto."""
    installed = {
        "skills": [],
        "agents": [],
        "workflows": [],
        "tools": [],
        "config": False
    }

    # Detectar plataforma
    for pdir in [".opencode", ".claude", ".agent"]:
        platform_path = project_path / pdir
        if platform_path.exists():
            # Skills (symlinks)
            skills_path = platform_path / "skills"
            if skills_path.exists():
                installed["skills"] = [d.name for d in skills_path.iterdir() if d.is_symlink()]

            # Agents
            agents_path = platform_path / "agents"
            if agents_path.exists():
                installed["agents"] = [f.stem for f in agents_path.glob("*.md")]

            # Tools
            tools_path = platform_path / "tools"
            if tools_path.exists():
                installed["tools"] = [f.stem for f in tools_path.glob("*") if f.is_file()]
            break

    # Workflows
    workflows_path = project_path / ".SAC" / "workflows"
    if workflows_path.exists():
        installed["workflows"] = [d.name for d in workflows_path.iterdir() if d.is_dir()]

    # Config
    if (project_path / ".SAC" / "config").exists():
        installed["config"] = True

    return installed
```

**Modificar `main()`:**
```python
def main():
    if len(sys.argv) == 1:
        show_menu()
        return

    arg = sys.argv[1]

    if arg in ("--help", "-h"):
        print_banner()
        print_help()
    elif arg in ("--version", "-v"):
        print_version()
    elif arg in ("--check", "-c"):
        print_banner()
        cmd_check()
    elif arg in ("--install", "-i", "-im"):
        print_banner()
        cmd_install()
    elif arg in ("--update", "-u"):
        print_banner()
        cmd_update()
    elif arg in ("--status", "-s"):
        print_banner()
        cmd_status()
    elif arg in ("--list", "-l"):
        print_banner()
        cmd_list()
    else:
        # Asumir que es una ruta → instalar
        sys.argv.insert(1, "--install")
        cmd_install()
```

### 3. `install.ps1` — Cambios equivalentes

```powershell
$DIAT_URL = "https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/diat"
$DIAT_PATH = "$env:LOCALAPPDATA\ia-dev-toolkit\bin\diat"
Invoke-WebRequest -Uri $DIAT_URL -OutFile $DIAT_PATH

$BAT_PATH = "$env:LOCALAPPDATA\ia-dev-toolkit\bin\diat.bat"
@"
@echo off
python "$DIAT_PATH" %*
"@ | Out-File -FilePath $BAT_PATH -Encoding ASCII
```

### 4. Eliminar archivos obsoletos

| Archivo | Acción |
|---|---|
| `INSTALACION/bootstrap/skills.sh` | Eliminar |
| `INSTALACION/bootstrap/skills.bat` | Eliminar |

### 5. Actualizar `README.md`

```markdown
# Instalación

curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash

# Uso

diat                          # Ver comandos disponibles
diat --install                # Instalar en ruta actual
diat --install /mi-proyecto   # Instalar en ruta específica
diat --update                 # Actualizar ruta actual
diat --update /mi-proyecto    # Actualizar ruta específica
diat --status                 # Ver estado ruta actual
diat --list                   # Ver componentes en cache
```

## Archivos a Modificar

| Archivo | Acción |
|---|---|
| `INSTALACION/bootstrap/install.sh` | Reescribir (descarga directa, sin clon) |
| `INSTALACION/bootstrap/install.ps1` | Reescribir (descarga directa, sin clon) |
| `INSTALACION/bootstrap/skills.sh` | Eliminar |
| `INSTALACION/bootstrap/skills.bat` | Eliminar |
| `INSTALACION/diat` | Reescribir con nuevos comandos |
| `INSTALACION/README.md` | Actualizar ejemplos |

## Pruebas

1. Ejecutar `install.sh` en entorno limpio
2. Verificar que `diat` se crea en `~/.local/bin/` (~10KB)
3. Verificar que `diat` (sin args) muestra menú
4. Verificar que `diat --help` funciona
5. Verificar que `diat --version` muestra `v0.2.1`
6. Verificar que `diat --check` funciona
7. Verificar que `diat --install` muestra menú de selección
8. Verificar que descarga solo componentes seleccionados
9. Verificar que instala en ruta correcta
10. Verificar que `diat --update` actualiza instalación existente
11. Verificar que `diat --status` muestra estado correcto

## Riesgos

| Riesgo | Mitigación |
|---|---|
| GitHub rate limit | Mensaje claro, sugerir reintento |
| Python no encontrado | Verificación previa en bootstrap |
| PATH no actualizado | Mensaje para reiniciar terminal |
| Sin conexión | Mensaje de error con instrucciones |
| Cache corrupta | `--update` fuerza re-descarga |
| Ruta no existe | Preguntar si crear |
