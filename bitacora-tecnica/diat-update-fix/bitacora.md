# Sesión: Fix diat --update — Instalación de Componentes Nuevos
- **ID:** 2026-08-31-diat-update-fix
- **Fecha inicio:** 2026-08-31 18:00
- **Última actualización:** 2026-08-31 18:30
- **Estado:** ✅ Cerrada — resuelto por el instalador v2 (commands se instalan vía tarball; --update reinstala los proyectos registrados). Confirmado por el usuario.
- **Rama de Trabajo:** `main`
- **Tags:** `diat`, `update`, `installer`, `commands`, `tools`, `auto-install`
- **Ambiente:** Local (squad-skills → ~/.local/bin/)

## Tiempo
- **Invertido:** 30min (diagnóstico)
- **Estimado restante:** 1h (implementación)
- **Deadline:** N/A

## Objetivo de la Sesión
Corregir el comando `diat --update [ruta]` para que:
1. Descargue commands al cache global (faltaba en `download_from_github()`)
2. Instale automáticamente componentes nuevos en el proyecto especificado
3. No requiera interacción del usuario para instalar dependencias

## Documentación Generada
- **Diagrama de Flujo Completo:** `bitacora-tecnica/diat-update-fix/diagrama-flujo-instalador.md`
  - Diagrama ASCII de todo el sistema de instalación
  - Flujo de descarga (GitHub API, no git clone)
  - Flujo de instalación en proyecto
  - Rutas clave del sistema
  - Tabla comparativa de métodos de descarga

## Lo Realizado

### Diagnóstico (Commits Existentes)
- `a5ed1d6` — refactor(installer): add component dependencies, remove tools/commands/alma from menu
- `5e92fc0` — feat(installer): add commands installation support

### Análisis de Código
- `INSTALACION/instalar.py` — Función `download_from_github()` (línea 1275-1416)
- `INSTALACION/diat` — Función `cmd_update()` (línea 517-580)

### Hallazgos

#### Problema 1: `download_from_github()` NO descarga commands
**Archivo:** `INSTALACION/instalar.py`
**Ubicación:** Línea 1306-1409

La función tiene 6 pasos:
1. Descargar ALMA.md ✅
2. Descargar config ✅
3. Descargar tools ✅
4. Descargar skills ✅
5. Descargar agents ✅
6. Descargar workflows ✅
7. **Descargar commands ❌ FALTA**

**Consecuencia:** El cache global (`~/.local/share/ia-dev-toolkit/repo/`) no tiene carpeta `commands/`.

#### Problema 2: `cmd_update()` NO instala en proyecto
**Archivo:** `INSTALACION/diat`
**Ubicación:** Línea 517-580

La función solo:
1. Actualiza CLI diat ✅
2. Actualiza cache global ✅
3. **NO parsea ruta del proyecto ❌**
4. **NO detecta plataforma ❌**
5. **NO compara componentes ❌**
6. **NO instala nuevos ❌**

**Consecuencia:** Al ejecutar `diat --update /ruta/proyecto`, se actualiza el cache pero el proyecto queda desactualizado.

### Evidencia

#### Cache global (`~/.local/share/ia-dev-toolkit/repo/`)
```
ALMA.md          ✅
config/          ✅
skills/          ✅ (38 skills)
tools/           ✅ (workflow-discover.ts, workflow-sac.ts, scripts/)
commands/        ❌ NO EXISTE
```

#### Proyecto app-barber (`.opencode/`)
```
skills/          ✅ (38 symlinks al cache)
tools/           ❌ (solo workflow-discover.ts y scripts/, falta workflow-sac.ts)
commands/        ❌ NO EXISTE
```

#### Repositorio fuente (squad-skills)
```
tools/           ✅ (workflow-discover.ts, workflow-sac.ts, scripts/)
commands/        ✅ (workflow-sac.md)
```

## Estado Actual

### Pendientes
- [ ] **Cambio 1:** Agregar paso 7 en `download_from_github()` para descargar commands
- [ ] **Cambio 2:** Modificar `cmd_update()` para instalar en proyecto
  - [ ] Parsear `sys.argv[2]` como ruta del proyecto
  - [ ] Detectar plataforma (`.opencode`/`.claude`/`.agent`)
  - [ ] Comparar tools instalados vs cache
  - [ ] Comparar commands instalados vs cache
  - [ ] Comparar skills instalados vs cache
  - [ ] Instalar automáticamente lo que falte (sin preguntar)

### Bloqueantes
- Ninguno

### Tests
- [ ] Unitarios: Pendiente
- [ ] Integración: Pendiente
- [ ] E2E: Pendiente

### Rollback Plan
Si algo sale mal:
1. `git checkout main -- INSTALACION/instalar.py INSTALACION/diat`
2. O usar backup generado por `diat` en `~/.local/bin/diat.bak`

## Plan de Implementación

### Cambio 1: `INSTALACION/instalar.py`

**Ubicación:** Después del paso 6 (workflows, línea ~1409), antes del resumen.

```python
# 7. Descargar commands (sin filtro, como tools)
print_info("Descargando commands...")
commands_count = 0
try:
    commands_items = github_api_get(f"{api_base}/commands")
    if isinstance(commands_items, list):
        (dest_path / "commands").mkdir(parents=True, exist_ok=True)
        for item in commands_items:
            if item["type"] == "file" and item["name"].endswith(".md"):
                content = github_api_get_raw(item["download_url"])
                (dest_path / "commands" / item["name"]).write_bytes(content)
                commands_count += 1
                print_success(item["name"])
except Exception:
    print_warning("No se encontró carpeta commands")
```

**Actualizar resumen** (línea 1412) para incluir `commands_count`.

### Cambio 2: `INSTALACION/diat`

**Ubicación:** Función `cmd_update()` (línea 517-580).

**Nueva lógica después de actualizar cache (después de línea 575):**

```python
    # 5. Instalar componentes nuevos en proyecto (si se especificó ruta)
    if len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
        project_path = Path(sys.argv[2]).resolve()
        if project_path.exists():
            print(f"\n  📦 Instalando componentes en: {project_path}")
            auto_install_missing(project_path, temp_repo_path)
```

**Nueva función auxiliar:**

```python
def auto_install_missing(project_path, cache_path):
    """Instalar componentes nuevos sin preguntar al usuario."""
    # Detectar plataforma
    platform_dir = None
    for pdir in [".opencode", ".claude", ".agent"]:
        if (project_path / pdir).exists():
            platform_dir = project_path / pdir
            break
    
    if not platform_dir:
        print(f"  ⚠️  No se detectó plataforma en {project_path}")
        return
    
    installed = {"tools": 0, "commands": 0, "skills": 0}
    
    # Instalar tools faltantes
    cache_tools = cache_path / "tools"
    project_tools = platform_dir / "tools"
    if cache_tools.exists():
        project_tools.mkdir(parents=True, exist_ok=True)
        for item in cache_tools.iterdir():
            if item.is_file() and item.suffix in (".ts", ".js", ".py", ".sh"):
                dst = project_tools / item.name
                if not dst.exists():
                    shutil.copy2(item, dst)
                    installed["tools"] += 1
                    print_success(f"tool: {item.name}")
            elif item.is_dir() and item.name == "scripts":
                scripts_dst = project_tools / "scripts"
                scripts_dst.mkdir(exist_ok=True)
                for script in item.iterdir():
                    if script.is_file() and script.suffix in (".ts", ".js", ".py", ".sh"):
                        dst = scripts_dst / script.name
                        if not dst.exists():
                            shutil.copy2(script, dst)
                            installed["tools"] += 1
                            print_success(f"tool: scripts/{script.name}")
    
    # Instalar commands faltantes
    cache_commands = cache_path / "commands"
    project_commands = platform_dir / "commands"
    if cache_commands.exists():
        project_commands.mkdir(parents=True, exist_ok=True)
        for item in cache_commands.iterdir():
            if item.is_file() and item.suffix == ".md":
                dst = project_commands / item.name
                if not dst.exists():
                    shutil.copy2(item, dst)
                    installed["commands"] += 1
                    print_success(f"command: {item.name}")
    
    # Instalar skills faltantes (solo symlinks si ya existen skills)
    cache_skills = cache_path / "skills"
    project_skills = platform_dir / "skills"
    if cache_skills.exists() and project_skills.exists():
        for item in cache_skills.iterdir():
            if item.is_dir():
                dst = project_skills / item.name
                if not dst.exists():
                    dst.symlink_to(item)
                    installed["skills"] += 1
                    print_success(f"skill: {item.name}")
    
    # Resumen
    total = sum(installed.values())
    if total > 0:
        print(f"\n  ✅ Instalados: {installed['tools']} tools, {installed['commands']} commands, {installed['skills']} skills")
    else:
        print(f"\n  ✅ Todos los componentes están actualizados")
```

## Próxima Sesión
1. Implementar Cambio 1: Agregar descarga de commands en `download_from_github()`
2. Implementar Cambio 2: Modificar `cmd_update()` con `auto_install_missing()`
3. Probar con `diat --update /home/javier-garcia/Documentos/estudio/PROYETOS/app-barber/`
4. Verificar que se instalan `workflow-sac.ts` y `workflow-sac.md`
5. Commitear cambios
