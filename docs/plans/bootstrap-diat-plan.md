# Plan: Actualizar Bootstrap para instalar comando `diat`

## Contexto

El bootstrap actual (`install.sh` / `install.ps1`) crea un comando global llamado `skills` que ejecuta `instalar.py`. 

El usuario quiere que el comando global se llame `diat` (acrónimo de **IA** **D**ev **T**oolkit) y que ejecute el nuevo CLI `INSTALACION/diat` en lugar de `instalar.py` directamente.

## Estado Actual

### Flujo actual (comando `skills`):
```
curl | bash
    ↓
Clona repo → ~/.local/share/ia-dev-toolkit/repo/
    ↓
Crea script ~/.local/bin/skills → ejecuta instalar.py
    ↓
Agrega ~/.local/bin al PATH
```

### Archivos involucrados:
- `INSTALACION/bootstrap/install.sh` — Bootstrap Linux/Mac (226 líneas)
- `INSTALACION/bootstrap/install.ps1` — Bootstrap Windows
- `INSTALACION/bootstrap/skills.sh` — Wrapper global Linux/Mac
- `INSTALACION/bootstrap/skills.bat` — Wrapper global Windows

## Plan de Cambios

### 1. `install.sh` — Cambios menores

| Línea | Actual | Nuevo |
|---|---|---|
| 132 | `print_info "Creando comando global 'skills'..."` | `print_info "Creando comando global 'diat'..."` |
| 133 | `SKILLS_SCRIPT="$BIN_PATH/skills"` | `DIAT_SCRIPT="$BIN_PATH/diat"` |
| 135-153 | Script wrapper que ejecuta `instalar.py` | Script wrapper que ejecuta `diat` |
| 155 | `chmod +x "$SKILLS_SCRIPT"` | `chmod +x "$DIAT_SCRIPT"` |
| 156 | `print_success "Comando 'skills' creado..."` | `print_success "Comando 'diat' creado..."` |
| 193 | `SQUAD-SKILLS INSTALADO` | `IA DEV TOOLKIT INSTALADO` |
| 201 | `skills --help` | `diat --help` |
| 202 | `skills "/ruta/proyecto"` | `diat "/ruta/proyecto"` |

### 2. Script wrapper generado (reemplaza líneas 135-153)

```bash
#!/bin/bash
# diat — IA Dev Toolkit CLI

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

DIAT_PATH="$HOME/.local/share/ia-dev-toolkit/repo/INSTALACION/diat"

if [ -f "$DIAT_PATH" ]; then
    $PYTHON_CMD "$DIAT_PATH" "$@"
else
    echo "❌ Error: No se encontró diat"
    echo "   Ejecuta el script de instalación nuevamente"
    exit 1
fi
```

### 3. `install.ps1` — Cambios equivalentes para Windows

| Sección | Cambio |
|---|---|
| Línea 138 | `set INSTALLER_PATH=...instalar.py` → `set DIAT_PATH=...diat` |
| Script wrapper | Ejecutar `diat.bat` en lugar de `instalar.py` |
| Mensajes | `skills` → `diat` |

### 4. `skills.sh` y `skills.bat` — Eliminar o renombrar

**Opción A (Recomendada):** Eliminar estos archivos ya que el wrapper se genera dinámicamente en el bootstrap.

**Opción B:** Renombrar a `diat.sh` y `diat.bat` como scripts de respaldo.

### 5. Documentación — `README.md` de INSTALACION

Actualizar ejemplos de uso:
```bash
# Antes
skills --help
skills "/home/usuario/proyecto"

# Después
diat --help
diat "/home/usuario/proyecto"
```

## Flujo Nuevo

```
curl -fsSL .../install.sh | bash
    ↓
Verifica requisitos (Python, Git)
    ↓
Clona repo → ~/.local/share/ia-dev-toolkit/repo/
    ↓
Crea script ~/.local/bin/diat → ejecuta INSTALACION/diat
    ↓
Agrega ~/.local/bin al PATH (si no está)
    ↓
Reiniciar terminal → diat --help funciona
```

## Comandos Resultantes

| Comando | Función |
|---|---|
| `diat` | Modo interactivo (instalar) |
| `diat /ruta` | Instalar en proyecto |
| `diat --help` | Mostrar ayuda |
| `diat --list` | Listar componentes |
| `diat --version` | Mostrar versión |
| `diat --update` | Actualizar toolkit |
| `diat --check` | Verificar requisitos |
| `diat --status /ruta` | Estado de instalación |

## Archivos a Modificar

| Archivo | Acción |
|---|---|
| `INSTALACION/bootstrap/install.sh` | Editar (cambiar skills → diat) |
| `INSTALACION/bootstrap/install.ps1` | Editar (cambiar skills → diat) |
| `INSTALACION/bootstrap/skills.sh` | Eliminar o renombrar |
| `INSTALACION/bootstrap/skills.bat` | Eliminar o renombrar |
| `INSTALACION/README.md` | Actualizar ejemplos |

## Pruebas

1. Ejecutar `install.sh` en entorno limpio
2. Verificar que `diat` se crea en `~/.local/bin/`
3. Verificar que `diat --help` funciona
4. Verificar que `diat --version` muestra `v0.2.1`
5. Verificar que `diat /ruta` ejecuta el instalador

## Riesgos

| Riesgo | Mitigación |
|---|---|
| PATH no actualizado | Mensaje claro para reiniciar terminal |
| Python no encontrado | Verificación previa en bootstrap |
| Repo no accesible | Mensaje de error con URL de descarga manual |
