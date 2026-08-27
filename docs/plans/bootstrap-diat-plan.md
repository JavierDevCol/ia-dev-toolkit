# Plan: Actualizar Bootstrap para instalar comando `diat`

## Contexto

El bootstrap actual (`install.sh` / `install.ps1`) crea un comando global llamado `skills` que ejecuta `instalar.py` y clona el repo completo.

El usuario quiere:
1. Comando global se llame `diat` (acrónimo de **IA** **D**ev **T**oolkit)
2. **NO clonar el repo** — solo descargar el script `diat` (~10KB)
3. Componentes se descargan bajo demanda con `diat --update`

## Estado Actual

### Flujo actual (comando `skills` con clon):
```
curl | bash
    ↓
Clona repo → ~/.local/share/ia-dev-toolkit/repo/ (~400KB)
    ↓
Crea script ~/.local/bin/skills → ejecuta instalar.py
    ↓
Agrega ~/.local/bin al PATH
```

## Flujo Nuevo (sin clon)

```
curl -fsSL .../install.sh | bash
    ↓
Descarga SOLO script diat → ~/.local/bin/diat (~10KB)
    ↓
Agrega ~/.local/bin al PATH (si no está)
    ↓
Reiniciar terminal → diat --help funciona
```

### Comandos disponibles desde cero (sin `--update`):

| Comando | ¿Funciona? | Nota |
|---|---|---|
| `diat --version` | ✅ | Versión hardcodeada |
| `diat --help` | ✅ | Solo muestra texto |
| `diat --check` | ✅ | Verifica Python/Git/Node |
| `diat --status /ruta` | ✅ | Lee estado del proyecto |
| `diat --list` | ❌ | Requiere `diat --update` |
| `diat /ruta` | ❌ | Requiere `diat --update` |
| `diat --update` | ✅ | Descarga componentes |

### Comandos que requieren componentes:
```
$ diat --list
❌ No se encontraron componentes. Ejecuta `diat --update` primero.

$ diat /mi-proyecto
❌ No se encontraron componentes. Ejecuta `diat --update` primero.
```

## Plan de Cambios

### 1. `install.sh` — Reescritura mayor

**Eliminar:**
- Clon de repo (líneas 112-130)
- Creación de wrapper que ejecuta `instalar.py` (líneas 132-153)

**Agregar:**
- Descarga directa de `diat` desde GitHub (raw content)
- Script wrapper mínimo

**Nuevo flujo `install.sh`:**
```bash
# 1. Verificar Python
check_prerequisites

# 2. Crear directorios
mkdir -p "$HOME/.local/bin"

# 3. Descargar diat desde GitHub
DIAT_URL="https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/diat"
curl -fsSL "$DIAT_URL" -o "$HOME/.local/bin/diat"
chmod +x "$HOME/.local/bin/diat"

# 4. Verificar PATH
add_to_path

# 5. Mostrar resumen
print_summary
```

### 2. Script `diat` — Agregar verificación de componentes

Modificar `cmd_list()` y el flujo de instalación para verificar si hay componentes:

```python
def get_components_path():
    """Retorna la ruta donde se almacenan los componentes."""
    return get_temp_repo_path()

def ensure_components():
    """Verifica que existan componentes, sugiere --update si no."""
    components_path = get_components_path()
    if not components_path.exists() or not (components_path / "skills").exists():
        print("❌ No se encontraron componentes. Ejecuta `diat --update` primero.")
        return False
    return True
```

### 3. `install.ps1` — Cambios equivalentes para Windows

```powershell
# Descargar diat desde GitHub
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

```bash
# Instalación
curl -fsSL https://raw.githubusercontent.com/JavierDevCol/ia-dev-toolkit/main/INSTALACION/bootstrap/install.sh | bash

# Uso
diat --update          # Descargar componentes (primera vez)
diat --help            # Ver ayuda
diat "/mi-proyecto"    # Instalar en proyecto
```

## Archivos a Modificar

| Archivo | Acción |
|---|---|
| `INSTALACION/bootstrap/install.sh` | Reescribir (descarga directa, sin clon) |
| `INSTALACION/bootstrap/install.ps1` | Reescribir (descarga directa, sin clon) |
| `INSTALACION/bootstrap/skills.sh` | Eliminar |
| `INSTALACION/bootstrap/skills.bat` | Eliminar |
| `INSTALACION/diat` | Agregar verificación `ensure_components()` |
| `INSTALACION/README.md` | Actualizar ejemplos |

## Pruebas

1. Ejecutar `install.sh` en entorno limpio
2. Verificar que `diat` se crea en `~/.local/bin/` (~10KB)
3. Verificar que `diat --help` funciona inmediatamente
4. Verificar que `diat --version` muestra `v0.2.1`
5. Verificar que `diat --check` funciona
6. Verificar que `diat --list` muestra mensaje de `--update`
7. Ejecutar `diat --update` y verificar descarga de componentes
8. Ejecutar `diat --list` y verificar que muestra componentes
9. Ejecutar `diat /ruta` y verificar instalación

## Riesgos

| Riesgo | Mitigación |
|---|---|
| GitHub rate limit | Mensaje claro, sugerir `--update` manual |
| Python no encontrado | Verificación previa en bootstrap |
| PATH no actualizado | Mensaje para reiniciar terminal |
| Sin conexión | Mensaje de error con instrucciones |
