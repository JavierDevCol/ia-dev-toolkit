# Plan: Actualizar Bootstrap para instalar comando `diat`

## Contexto

El bootstrap actual (`install.sh` / `install.ps1`) crea un comando global llamado `skills` que ejecuta `instalar.py` y clona el repo completo.

El usuario quiere:
1. Comando global se llame `diat` (acrónimo de **IA** **D**ev **T**oolkit)
2. **NO clonar el repo** — solo descargar el script `diat` (~10KB)
3. `diat --install` descarga componentes e instala en proyecto
4. `diat --update /ruta` actualiza componentes ya instalados

## Diseño de Comandos

| Comando | Función | Requiere componentes |
|---|---|---|
| `diat` | Mostrar menú de comandos disponibles | No |
| `diat --help` | Mostrar ayuda detallada | No |
| `diat --version` | Mostrar versión actual | No |
| `diat --check` | Verificar requisitos del sistema | No |
| `diat --status /ruta` | Mostrar estado de instalación en proyecto | No |
| `diat --install /ruta` | Descargar componentes + instalar en proyecto | Sí (descarga automática) |
| `diat --update /ruta` | Actualizar componentes en proyecto existente | Sí (descarga automática) |
| `diat --list` | Listar componentes disponibles | Sí (requiere `--install` previo) |

## Flujo de Instalación

### 1. Instalar `diat` (una vez)
```bash
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash
```

Resultado:
```
✅ diat instalado en ~/.local/bin/diat

🚀 Comandos disponibles:
   diat                    Ver comandos disponibles
   diat --install /ruta    Instalar en un proyecto
   diat --help             Ver ayuda
```

### 2. Usar `diat`
```bash
# Ver comandos
diat

# Instalar en proyecto (descarga componentes automáticamente)
diat --install /home/usuario/mi-proyecto

# Actualizar proyecto existente
diat --update /home/usuario/mi-proyecto

# Ver estado
diat --status /home/usuario/mi-proyecto
```

## Flujo Interno de `--install`

```
diat --install /ruta
    ↓
1. Verificar si componentes están en cache (~/.local/share/ia-dev-toolkit/components/)
    ↓ (si no existen)
2. Descargar componentes desde GitHub API (~400KB)
    ↓
3. Mostrar menú interactivo de selección (checkboxes)
    ↓
4. Instalar seleccionados en /ruta
```

## Flujo Interno de `--update`

```
diat --update /ruta
    ↓
1. Verificar que /ruta tiene instalación previa
    ↓ (si no)
2. Mostrar error: "No se encontró instalación. Usa --install primero"
    ↓ (si existe)
3. Descargar última versión de componentes
    ↓
4. Actualizar componentes en /ruta
```

## Cache de Componentes

Los componentes se descargan una vez y se cachean:

```
~/.local/share/ia-dev-toolkit/
└── components/          ← Cache de componentes descargados
    ├── skills/
    ├── agents/
    ├── workflows/
    ├── tools/
    └── config/
```

- `--install` y `--update` verifican si hay cache
- Si no hay cache, descargan de GitHub
- `--update` siempre descarga la última versión

## Plan de Cambios

### 1. `install.sh` — Reescritura mayor

**Eliminar:**
- Clon de repo
- Creación de wrapper que ejecuta `instalar.py`

**Agregar:**
- Descarga directa de `diat` desde GitHub (raw content)
- Creación de wrapper mínimo

**Nuevo `install.sh`:**
```bash
#!/bin/bash
set -e

# Configuración
DIAT_URL="https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/diat"
BIN_PATH="$HOME/.local/bin"

# Verificar Python
check_prerequisites() { ... }

# Crear directorios
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
echo "   diat --install /ruta    Instalar en un proyecto"
echo "   diat --help             Ver ayuda"
```

### 2. `diat` — Modificaciones

**Agregar función `show_menu()`:**
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
  diat --install /ruta     Instalar componentes en proyecto
  diat --update /ruta      Actualizar componentes en proyecto
  diat --status /ruta      Mostrar estado de instalación
  diat --list              Listar componentes disponibles

Ejemplos:
  diat --install /home/usuario/proyecto
  diat --update /home/usuario/proyecto
  diat --status /home/usuario/proyecto
""")
```

**Agregar función `cmd_install()`:**
```python
def cmd_install(project_path=None):
    """Descargar componentes e instalar en proyecto."""
    if not project_path:
        print("❌ Especifica la ruta: diat --install /ruta/proyecto")
        return

    # Verificar/descargar componentes
    components_path = ensure_components()

    # Ejecutar instalador
    sys.path.insert(0, str(get_script_directory()))
    from instalar import main as install_main
    sys.argv = ["instalar.py", project_path]
    install_main()
```

**Agregar función `cmd_update()`:**
```python
def cmd_update(project_path=None):
    """Actualizar componentes en proyecto existente."""
    if not project_path:
        print("❌ Especifica la ruta: diat --update /ruta/proyecto")
        return

    project_path = Path(project_path)
    if not (project_path / ".opencode").exists() and not (project_path / ".SAC").exists():
        print("❌ No se encontró instalación previa. Usa --install primero.")
        return

    # Forzar descarga de última versión
    download_components(force=True)

    # Ejecutar actualización
    # ... (reinstalar componentes)
```

**Agregar función `ensure_components()`:**
```python
def ensure_components():
    """Verificar que componentes estén descargados, descargar si no."""
    components_path = get_components_path()

    if not components_path.exists() or not (components_path / "skills").exists():
        print("📥 Descargando componentes por primera vez...")
        return download_components()

    return components_path
```

**Modificar `main()`:**
```python
def main():
    if len(sys.argv) == 1:
        show_menu()  # Mostrar menú en lugar de instalar
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
        cmd_install(sys.argv[2] if len(sys.argv) > 2 else None)
    elif arg in ("--update", "-u"):
        print_banner()
        cmd_update(sys.argv[2] if len(sys.argv) > 2 else None)
    elif arg in ("--status", "-s"):
        print_banner()
        cmd_status(sys.argv[2] if len(sys.argv) > 2 else None)
    elif arg in ("--list", "-l"):
        print_banner()
        if ensure_components():
            cmd_list()
    else:
        # Asumir que es una ruta → instalar
        cmd_install(arg)
```

### 3. `install.ps1` — Cambios equivalentes

```powershell
# Descargar diat
$DIAT_URL = "https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/diat"
$DIAT_PATH = "$env:LOCALAPPDATA\ia-dev-toolkit\bin\diat"
Invoke-WebRequest -Uri $DIAT_URL -OutFile $DIAT_PATH

# Crear wrapper .bat
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
diat --install /mi-proyecto   # Instalar en proyecto
diat --update /mi-proyecto    # Actualizar proyecto
diat --status /mi-proyecto    # Ver estado
```

## Archivos a Modificar

| Archivo | Acción |
|---|---|
| `INSTALACION/bootstrap/install.sh` | Reescribir (descarga directa, sin clon) |
| `INSTALACION/bootstrap/install.ps1` | Reescribir (descarga directa, sin clon) |
| `INSTALACION/bootstrap/skills.sh` | Eliminar |
| `INSTALACION/bootstrap/skills.bat` | Eliminar |
| `INSTALACION/diat` | Agregar `show_menu()`, `cmd_install()`, `cmd_update()`, `ensure_components()` |
| `INSTALACION/README.md` | Actualizar ejemplos |

## Pruebas

1. Ejecutar `install.sh` en entorno limpio
2. Verificar que `diat` se crea en `~/.local/bin/` (~10KB)
3. Verificar que `diat` (sin args) muestra menú
4. Verificar que `diat --help` funciona
5. Verificar que `diat --version` muestra `v0.2.1`
6. Verificar que `diat --check` funciona
7. Verificar que `diat --install /ruta` descarga componentes + instala
8. Verificar que `diat --update /ruta` actualiza componentes
9. Verificar que `diat --status /ruta` muestra estado

## Riesgos

| Riesgo | Mitigación |
|---|---|
| GitHub rate limit | Mensaje claro, sugerir descarga manual |
| Python no encontrado | Verificación previa en bootstrap |
| PATH no actualizado | Mensaje para reiniciar terminal |
| Sin conexión | Mensaje de error con instrucciones |
| Cache corrupta | `--update` fuerza re-descarga |
