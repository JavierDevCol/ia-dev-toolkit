# Diagrama de Flujo — Sistema de Instalación ia-dev-toolkit

## Archivos del Sistema (`INSTALACION/`)

```
INSTALACION/
├── diat                    # CLI principal (Python, 876 líneas)
├── diat.bat                # Wrapper Windows
├── instalar.py             # Instalador modular (Python, 1525 líneas)
├── interactive_menu.py     # Menú interactivo con curses (283 líneas)
├── bootstrap/
│   ├── install.sh          # Instalador inicial Linux/Mac
│   ├── install.ps1         # Instalador inicial Windows
│   ├── uninstall.sh        # Desinstalador Linux/Mac
│   └── uninstall.ps1       # Desinstalador Windows
└── README.md               # Documentación
```

---

## Flujo General del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USUARIO EJECUTA                              │
│                                                                     │
│   curl -fsSL https://.../install.sh | bash    (primera vez)        │
│   diat [comando] [ruta]                         (uso diario)        │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     INSTALACIÓN INICIAL                             │
│                     (bootstrap/install.sh)                          │
│                                                                     │
│   1. Descarga solo `diat` (~10KB) desde GitHub                     │
│   2. Guarda en ~/.local/bin/diat                                   │
│   3. Agrega ~/.local/bin al PATH                                   │
│   4. NO clona el repo completo                                     │
│                                                                     │
│   Resultado: ~/.local/bin/diat (CLI funcional)                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CLI diat (diat)                                │
│                                                                     │
│   Lee argumentos de sys.argv y despacha a función correspondiente   │
│                                                                     │
│   Comandos:                                                         │
│   ├── (sin args)     → show_menu()                                  │
│   ├── --help, -h     → print_help()                                 │
│   ├── --version, -v  → print_version()                              │
│   ├── --list, -l     → cmd_list()                                   │
│   ├── --check, -c    → cmd_check()                                  │
│   ├── --update, -u   → cmd_update()                                 │
│   ├── --status, -s   → cmd_status()                                 │
│   ├── --install, -i  → cmd_install()                                │
│   ├── --alma, -a     → cmd_alma()                                   │
│   ├── --uninstall    → cmd_uninstall()                              │
│   └── /ruta/proyecto → cmd_install() (asume ruta)                   │
│                                                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│   cmd_install()     │ │   cmd_update()      │ │   cmd_alma()        │
│                     │ │                     │ │                     │
│ 1. Parsea ruta      │ │ 1. Actualiza CLI    │ │ 1. Parsea ruta      │
│ 2. ensure_instalar()│ │ 2. Actualiza cache  │ │ 2. ensure_instalar()│
│ 3. Ejecuta          │ │ 3. NO instala en    │ │ 3. Busca ALMA.md    │
│    instalar.py      │ │    proyecto         │ │ 4. Instala          │
│                     │ │                     │ │    personalidad     │
└─────────┬───────────┘ └─────────┬───────────┘ └─────────┬───────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ensure_instalar()                                │
│                                                                     │
│   1. Descarga instalar.py desde GitHub RAW                         │
│   2. Guarda en ~/.local/bin/instalar.py (junto a diat)             │
│   3. Retorna directorio para importar                               │
│                                                                     │
│   NOTA: instalar.py se descarga SIEMPRE (para obtener versión      │
│   más reciente). Si falla, usa versión local si existe.            │
│                                                                     │
│   Resultado: ~/.local/bin/instalar.py actualizado                  │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    instalar.py — main()                             │
│                                                                     │
│   1. Obtiene root_dir (directorio del repo)                        │
│   2. Si no hay repo local → ensure_repo_available()                │
│   3. Escanea componentes: skills, agents, workflows, tools, cmds   │
│   4. Muestra menú interactivo                                       │
│   5. Instala según selección del usuario                            │
│                                                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ensure_repo_available()                           │
│                                                                     │
│   1. Verifica si existe cache local en:                            │
│      ~/.local/share/ia-dev-toolkit/repo/                           │
│                                                                     │
│   2. Si existe y tiene carpetas requeridas:                        │
│      ├── skills/, agents/, workflows/, tools/, config/             │
│      ├── Intenta git pull --ff-only (si tiene .git)                │
│      └── Retorna cache local                                        │
│                                                                     │
│   3. Si NO existe o está incompleto:                               │
│      └── Llama a download_from_github(cache_path)                  │
│                                                                     │
│   Resultado: Cache con componentes disponibles                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    download_from_github(dest_path)                  │
│                                                                     │
│   NO clona el repo. Usa GitHub API para descargar archivos         │
│   individuales. Filtra por ready: true en skills/agents/workflows  │
│                                                                     │
│   Paso 1: Archivos raíz                                            │
│   ├── Descarga ALMA.md desde RAW                                   │
│   └── Guarda en dest_path/ALMA.md                                  │
│                                                                     │
│   Paso 2: Config (sin filtro)                                      │
│   ├── GET /contents/config/config                                  │
│   ├── Descarga todos los .yaml                                     │
│   └── Guarda en dest_path/config/config/*.yaml                     │
│                                                                     │
│   Paso 3: Tools (sin filtro)                                       │
│   ├── GET /contents/tools                                          │
│   ├── Para cada archivo .ts/.js/.py/.sh → descarga directo         │
│   ├── Para cada subdirectorio → descarga contents recursivo        │
│   └── Guarda en dest_path/tools/                                   │
│                                                                     │
│   Paso 4: Skills (CON filtro ready: true)                          │
│   ├── GET /contents/skills                                         │
│   ├── Para cada subdirectorio:                                     │
│   │   ├── GET /contents/skills/{nombre}/SKILL.md                   │
│   │   ├── Lee frontmatter → parsea ready:                          │
│   │   ├── Si ready: true → download_directory() recursivo          │
│   │   └── Si ready: false → skip                                   │
│   └── Guarda en dest_path/skills/{nombre}/                         │
│                                                                     │
│   Paso 5: Agents (CON filtro ready: true)                          │
│   ├── GET /contents/agents                                         │
│   ├── Para cada archivo .md:                                       │
│   │   ├── Descarga contenido                                       │
│   │   ├── Lee frontmatter → parsea ready:                          │
│   │   └── Si ready: true → guarda, si no → skip                   │
│   └── Guarda en dest_path/agents/{nombre}.md                       │
│                                                                     │
│   Paso 6: Workflows (CON filtro ready: true)                       │
│   ├── GET /contents/workflows                                      │
│   ├── Para cada subdirectorio:                                     │
│   │   ├── GET /contents/workflows/{nombre}/workflow.md             │
│   │   ├── Lee frontmatter → parsea ready:                          │
│   │   ├── Si ready: true → download_directory() recursivo          │
│   │   └── Si ready: false → skip                                   │
│   └── Guarda en dest_path/workflows/{nombre}/                      │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │ FALTA: No hay paso para descargar commands               │     │
│   │ No existe sección que haga GET /contents/commands        │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│   Resumen: X/Y skills, X/Y agents, X/Y workflows                  │
│                                                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Cache Local (Resultado)                          │
│                                                                     │
│   ~/.local/share/ia-dev-toolkit/repo/                              │
│   ├── ALMA.md                                                      │
│   ├── config/config/                                               │
│   │   ├── CONFIG_SYSTEM.yaml                                       │
│   │   └── CONFIG_USER.yaml                                         │
│   ├── skills/                                                      │
│   │   ├── skill-1/SKILL.md + archivos                              │
│   │   ├── skill-2/SKILL.md + archivos                              │
│   │   └── ... (solo ready: true)                                   │
│   ├── agents/                                                      │
│   │   ├── PO.md                                                    │
│   │   ├── ARQUITECTO-SOFTWARE.md                                   │
│   │   └── ... (solo ready: true)                                   │
│   ├── workflows/                                                   │
│   │   ├── workflow-1/workflow.md + fases/ + plantillas/            │
│   │   └── ... (solo ready: true)                                   │
│   ├── tools/                                                       │
│   │   ├── workflow-discover.ts                                     │
│   │   ├── workflow-sac.ts                                          │
│   │   └── scripts/                                                 │
│   └── commands/     ← NO EXISTE (no se descarga)                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Flujo de Instalación en Proyecto

```
┌─────────────────────────────────────────────────────────────────────┐
│                    instalar.py — main()                             │
│                    (después de escanear componentes)                │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Detectar Plataforma                              │
│                                                                     │
│   get_skills_target(project_path):                                 │
│   ├── Busca .claude/ → usa .claude/skills/                         │
│   ├── Busca .opencode/ → usa .opencode/skills/                     │
│   ├── Busca .agent/ → usa .agent/skills/                           │
│   └── Ninguno existe → crea .agent/ y usa .agent/skills/           │
│                                                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Menú Interactivo                                 │
│                                                                     │
│   [1] Skills — Seleccionar skills específicas                      │
│   [2] Agents — Seleccionar agentes específicos                     │
│   [3] Workflows — Seleccionar workflows (+ tools + commands auto)  │
│   [4] Team Dev SAC — Skills SAC + Configuración                    │
│   [5] Kit Completo — Agents + Skills + Workflows + Config          │
│   [Q] Salir                                                         │
│                                                                     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│  Opción [1]   │          │  Opción [3]   │          │  Opción [5]   │
│  Skills       │          │  Workflows    │          │  Kit Completo │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                          │
        ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    install_skill(skill_info, project_path, target)  │
│                                                                     │
│   src = cache/skills/{nombre}/                                     │
│   dst = project/.opencode/skills/{nombre}/                         │
│                                                                     │
│   1. Si dst existe y es symlink → elimina                          │
│   2. Si dst existe y es directorio → elimina recursivo             │
│   3. Crea symlink: dst → src                                       │
│                                                                     │
│   NOTA: Skills se instalan como SYMLINKS al cache, no como copias. │
│   Esto ahorra espacio pero depende del cache local.                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    install_agent(agent_info, project_path)          │
│                                                                     │
│   src = cache/agents/{nombre}.md                                   │
│   dst = project/.opencode/agents/{nombre}.md                       │
│                                                                     │
│   1. Crea directorio .opencode/agents/ si no existe                │
│   2. Copia archivo (shutil.copy2)                                  │
│                                                                     │
│   NOTA: Agents se instalan como COPIAS, no symlinks.               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    install_workflow(wf_info, project_path, root)    │
│                                                                     │
│   src = cache/workflows/{nombre}/                                  │
│   dst = project/.SAC/workflows/{nombre}/                           │
│                                                                     │
│   1. Si dst existe → elimina recursivo                             │
│   2. Copia directorio completo (shutil.copytree)                   │
│     ├── workflow.md                                                │
│     ├── fases/*.md                                                 │
│     └── plantillas/*.md                                            │
│                                                                     │
│   NOTA: Workflows van a .SAC/workflows/, NO a .opencode/           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    install_tool(tool_info, project_path)            │
│                                                                     │
│   src = cache/tools/{nombre}.ts  (o scripts/*.sh)                  │
│   dst = project/.opencode/tools/{nombre}.ts                        │
│                                                                     │
│   1. Crea directorio .opencode/tools/ si no existe                 │
│   2. Si es .sh → guarda en .opencode/tools/scripts/                │
│   3. Copia archivo (shutil.copy2)                                  │
│                                                                     │
│   NOTA: Tools se instalan como COPIAS en .opencode/tools/          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    install_command(cmd_info, project_path)          │
│                                                                     │
│   src = cache/commands/{nombre}.md                                 │
│   dst = project/.opencode/commands/{nombre}.md                     │
│                                                                     │
│   1. Crea directorio .opencode/commands/ si no existe              │
│   2. Copia archivo (shutil.copy2)                                  │
│                                                                     │
│   NOTA: Commands van a .opencode/commands/                         │
│   PROBLEMA: El cache no descarga commands, esta función nunca      │
│   se ejecuta con datos reales.                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    install_sac_config(project_path, root, config)   │
│                                                                     │
│   1. Crea .SAC/config/ y .SAC/session/                             │
│   2. Copia config/*.yaml desde cache                               │
│   3. Actualiza CONFIG_SYSTEM.yaml con {project-root}               │
│   4. Actualiza CONFIG_USER.yaml con datos del proyecto             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Dependencias de Componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPONENT_DEPENDENCIES                           │
│                                                                     │
│   Cuando se instalan workflows, automáticamente se instalan:      │
│                                                                     │
│   Workflows ──┬──→ tools: ["workflow-sac", "workflow-discover"]    │
│               └──→ commands: ["workflow-sac"]                      │
│                                                                     │
│   Esto significa:                                                  │
│   - Si el usuario elige opción [3] Workflows                       │
│   - O opción [5] Kit Completo                                      │
│   - Se instalan automáticamente los tools y commands asociados     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Flujo `diat --update [ruta]` (ACTUAL - CON BUGS)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    cmd_update()                                     │
│                                                                     │
│   1. Obtener versión remota (GitHub API /tags)                     │
│                                                                     │
│   2. Actualizar CLI diat                                           │
│   ├── Descarga diat desde GitHub RAW                               │
│   ├── Guarda backup en diat.bak                                    │
│   └── Sobreescribe ~/.local/bin/diat                               │
│                                                                     │
│   3. Guardar versión instalada                                     │
│   └── Escribe en ~/.local/share/ia-dev-toolkit/.installed_version  │
│                                                                     │
│   4. Eliminar cache anterior                                       │
│   └── shutil.rmtree(~/.local/share/ia-dev-toolkit/repo/)           │
│                                                                     │
│   5. Descargar componentes nuevos                                  │
│   ├── ensure_instalar() → descarga instalar.py                     │
│   └── download_from_github(cache_path)                             │
│       ├── Descarga ALMA.md ✅                                       │
│       ├── Descarga config ✅                                        │
│       ├── Descarga tools ✅                                         │
│       ├── Descarga skills ✅                                        │
│       ├── Descarga agents ✅                                        │
│       ├── Descarga workflows ✅                                     │
│       └── Descarga commands ❌ FALTA                                │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │ BUG: La función termina aquí.                            │     │
│   │ NO parsea sys.argv[2] como ruta del proyecto.            │     │
│   │ NO instala componentes en el proyecto.                   │     │
│   │ Solo actualiza el cache global.                          │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Flujo `diat --update [ruta]` (ESPERADO - CORREGIDO)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    cmd_update() (CORREGIDO)                         │
│                                                                     │
│   1. Obtener versión remota                                        │
│                                                                     │
│   2. Actualizar CLI diat                                           │
│                                                                     │
│   3. Guardar versión instalada                                     │
│                                                                     │
│   4. Eliminar cache anterior                                       │
│                                                                     │
│   5. Descargar componentes nuevos                                  │
│   ├── ensure_instalar()                                            │
│   └── download_from_github(cache_path)                             │
│       ├── Descarga ALMA.md ✅                                       │
│       ├── Descarga config ✅                                        │
│       ├── Descarga tools ✅                                         │
│       ├── Descarga skills ✅                                        │
│       ├── Descarga agents ✅                                        │
│       ├── Descarga workflows ✅                                     │
│       └── Descarga commands ✅ (NUEVO)                              │
│                                                                     │
│   6. Instalar en proyecto (NUEVO)                                  │
│   ├── Parsea sys.argv[2] como project_path                         │
│   ├── Detecta plataforma (.opencode/.claude/.agent)                │
│   ├── Compara componentes cache vs proyecto                        │
│   │   ├── Tools: cache/tools/ vs .opencode/tools/                  │
│   │   ├── Commands: cache/commands/ vs .opencode/commands/         │
│   │   └── Skills: cache/skills/ vs .opencode/skills/               │
│   └── Instala automáticamente lo que falte (sin preguntar)         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Rutas Clave

```
Sistema:
  ~/.local/bin/diat                           # CLI principal
  ~/.local/bin/instalar.py                    # Instalador (descargado bajo demanda)
  ~/.local/share/ia-dev-toolkit/              # Datos del toolkit
  ~/.local/share/ia-dev-toolkit/.installed_version  # Versión instalada
  ~/.local/share/ia-dev-toolkit/.last_update_check  # Timestamp verificación
  ~/.local/share/ia-dev-toolkit/repo/         # Cache de componentes

Proyecto (destino):
  {proyecto}/.opencode/                       # Plataforma OpenCode
  {proyecto}/.opencode/skills/                # Skills (symlinks al cache)
  {proyecto}/.opencode/agents/                # Agents (copias)
  {proyecto}/.opencode/tools/                 # Tools (copias)
  {proyecto}/.opencode/commands/              # Commands (copias)
  {proyecto}/.SAC/                            # Configuración SAC
  {proyecto}/.SAC/config/                     # Config YAML
  {proyecto}/.SAC/workflows/                  # Workflows (copias)
  {proyecto}/.SAC/session/                    # Sesión actual
```

---

## Resumen de Métodos de Descarga

| Componente | Método | Filtro | Destino en Cache | Destino en Proyecto |
|------------|--------|--------|------------------|---------------------|
| diat | GitHub RAW | Ninguno | ~/.local/bin/ | N/A (CLI global) |
| instalar.py | GitHub RAW | Ninguno | ~/.local/bin/ | N/A (CLI global) |
| ALMA.md | GitHub RAW | Ninguno | repo/ALMA.md | .agent/ALMA.md (vía --alma) |
| Config | GitHub API + RAW | Ninguno | repo/config/ | .SAC/config/ |
| Skills | GitHub API + RAW | ready: true | repo/skills/ | .opencode/skills/ (symlink) |
| Agents | GitHub API + RAW | ready: true | repo/agents/ | .opencode/agents/ (copia) |
| Workflows | GitHub API + RAW | ready: true | repo/workflows/ | .SAC/workflows/ (copia) |
| Tools | GitHub API + RAW | Ninguno | repo/tools/ | .opencode/tools/ (copia) |
| Commands | **NO SE DESCARGA** | N/A | **NO EXISTE** | .opencode/commands/ (copia) |

---

## NOTA: NO se clona el repo

El sistema **NUNCA** ejecuta `git clone`. Utiliza la GitHub API para descargar archivos individuales:
- `https://api.github.com/repos/{owner}/{repo}/contents/{path}` — Para listar directorios
- `https://raw.githubusercontent.com/{owner}/{repo}/main/{path}` — Para descargar contenido

Esto reduce el tamaño de descarga de ~2-3MB (repo completo) a ~322KB (solo componentes ready).
