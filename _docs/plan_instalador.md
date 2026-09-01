
## Carpeta cache donde se instala DIAT
```
~/.local/share/ia-dev-toolkit/          # Cache global
├── diat                                # CLI principal
├── instalar.py                         # Instalador modular
├── interactive_menu.py                 # Menú interactivo
├── INSTALACIONES.json                  # Registro de instalaciones
└── .version                            # Versión actual
```


## Flujo de Ejecución

### diat --install /ruta/proyecto
```
1. Descarga instalar.py desde GitHub
2. Ejecuta instalar.py con ruta
3. Escanea componentes disponibles
4. Muestra menú interactivo
5. Instala componentes seleccionados
6. Guarda en instalacion.json
7. Muestra resumen
```

### diat --install (sin ruta)
```
1. Muestra banner 
2. Nota: instalación global
3. Pregunta agente (solo OpenCode funciona)
4. Instala en ~/.opencode/
5. Guarda en instalacion.json
```
# Sistema de dependencias unificado
```json
 {
    # Workflows → dependencies
    "workflows": {
        "definir-vision-producto": {
            "requires": {
                "tools": [],
                "commands": [],
                "skills": [],
                "plugins": []
            },
            "optional": {
                "skills": ["tomar-contexto"]
            }
        },
        "definir-arquitectura-solucion": {
            "requires": {
                "tools": ["workflow-sac", "workflow-discover"],
                "commands": ["workflow-sac"],
                "skills": [],
                "plugins": []
            },
            "optional": {
                "skills": ["crear-adr"]
            }
        },
        "gestionar-backlog-roadmap": {
            "requires": {
                "tools": ["workflow-sac", "workflow-discover"],
                "commands": ["workflow-sac"],
                "skills": [],
                "plugins": []
            },
            "optional": {
                "skills": ["sincronizar-backlog"]
            }
        }
    },

    # Agents → dependencies
    "agents": {
        "PO": {
            "requires": {
                "skills": ["refinar-hu", "validar-hu"],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {
                "skills": ["sincronizar-backlog", "planificar-hu"]
            }
        },
        "ARQUITECTO-SOFTWARE": {
            "requires": {
                "skills": ["crear-adr", "init-reglas-arquitectonicas"],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {
                "skills": ["analizar-calidad-codigo"]
            }
        },
        "ARQUITECTO-DEVOPS": {
            "requires": {
                "skills": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {
                "skills": ["tomar-contexto"]
            }
        },
        "DESARROLLADOR": {
            "requires": {
                "skills": ["git-branch-commit"],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {
                "skills": ["analizar-calidad-codigo"]
            }
        }
    },

    # Skills → dependencies
    "skills": {
        "validar-ca": {
            "requires": {
                "skills": ["planificar-hu"],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {
                "skills": ["registrar-hallazgo"]
            }
        },
        "ejecutar-plan": {
            "requires": {
                "skills": ["planificar-hu"],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {}
        },
        "sincronizar-backlog": {
            "requires": {
                "skills": [],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {}
        },
        "planificar-hu": {
            "requires": {
                "skills": ["tomar-contexto"],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {}
        },
        "refinar-hu": {
            "requires": {
                "skills": ["tomar-contexto"],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {}
        },
        "analizar-calidad-codigo": {
            "requires": {
                "skills": [],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {}
        },
        "bitacora-tecnica": {
            "requires": {
                "skills": [],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {}
        },
        "git-branch-commit": {
            "requires": {
                "skills": [],
                "workflows": [],
                "tools": [],
                "commands": [],
                "plugins": []
            },
            "optional": {}
        }
    }
}
```


## Estructura de instalacion.json
```json
{
  "version": "0.5.1",
  "last_update": "2026-08-31T22:30:00",
  "installations": [
    {
      "project_path": "/home/user/proyecto-1",
      "platform": ".opencode",
      "installed_at": "2026-08-31T18:00:00",
      "components": {
        "skills": ["skill-1", "skill-2", "skill-3"],
        "agents": ["PO"],
        "workflows": ["workflow-1"],
        "tools": ["workflow-sac", "workflow-discover"],
        "commands": ["workflow-sac"],
        "config": true
      }
    },
    {
      "project_path": "/home/user/proyecto-2",
      "platform": ".opencode",
      "installed_at": "2026-08-30T10:00:00",
      "components": {
        "skills": ["skill-4"],
        "agents": [],
        "workflows": [],
        "tools": [],
        "commands": [],
        "config": false
      }
    }
  ]
}
```

Vamos a trabajar solo enla carpeta @INSTALACION/ 

1. BAnner compartido: 


# ============================================
# COLORES
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================
print_banner() {
    echo ""
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠏⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⢠⠀⠈⢣⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡴⠋⠀⡀⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠀⣼⣷⠀⠀⠙⠒⠚⠛⠛⠛⠛⠛⠓⠒⠒⠦⠚⠀⢀⣴⡇⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠃⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⣀⡠⠤⢴⡷⠤⢤⡤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⢠⢾⣅⠙⢦⡀⠙⢦⡀⠙⢦⡈⠻⣕⢦⡀⠀⠀⠀⠀⠀⠀⣠⠴⢶⡋⠙⠫⣍⠙⢯⡉⠙⢯⡲⣄⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⢸⡄⠙⢷⡀⠙⢦⡀⠙⢦⡀⠙⢦⡘⢧⣷⠚⠉⠉⠛⠒⣾⠉⠳⡄⠙⢦⡀⠈⠳⣄⠉⠢⣄⠙⢾⡄⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠸⡝⢧⡀⠙⢦⡀⠙⢦⡀⠙⢦⡀⠙⢦⡝⠀⣠⣤⣤⠀⢹⠳⣄⠙⢦⡀⠉⠳⣄⠈⠑⢄⠈⠳⣼⠁⠀⠀⠀${NC}"
    echo -e "${CYAN}⠁⠒⠒⠦⠽⣄⠙⢦⡀⠙⢦⡀⠙⢷⣄⠙⣦⠞⠁⠀⠈⢻⠋⠀⠀⢣⡈⠳⣄⠙⢦⡀⠈⠳⣄⠀⠙⣶⣃⣀⣀⣀⣄${NC}"
    echo -e "${CYAN}⣀⣀⣀⣀⣀⣀⣻⡶⣿⣦⣤⣿⣦⣤⠿⠟⠃⠀⠀⠀⠀⢸⠀⠀⠀⠀⠻⢦⣜⣷⣄⣻⣦⣀⣸⣷⠟⠃⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠉⠉⠉⠉⠉⠉⢹⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣘⠀⠀⠀⠀⠀⠀⠈⠉⠙⠛⠛⠉⠩⢼⠒⠒⠲⠤⠤⠤⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠇⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠙⠢⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⠢⠤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⡤⠤⠒⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo -e "${CYAN}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀${NC}"
    echo ""
    echo -e "${CYAN}                         AI DEVELOPER TOOLKIT${NC}"
    echo ""
    echo -e "${CYAN}        ┌─────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}        │  Skills · Agents · Workflows · Tools · Commands         │${NC}"
    echo -e "${CYAN}        └─────────────────────────────────────────────────────────┘${NC}"
    echo ""
}


2. el instalador de DIAT, 
        a. mostrar banner 
        b. mostrar info: 

                🔍 Verificando requisitos previos...

                ✅ Python encontrado: Python 3.14.4

                📦 Instalando diat...

                ✅ diat instalado
                ℹ️  Instalando versión...
                ✅ Versión 0.6.1 Instalada
                ℹ️  Verificando PATH...
                ✅ PATH configurado    ## [SIEMPRE SE SOBRE ESCRIBE]


                ╔═══════════════════════════════════════════════════════════════╗
                ║                                                               ║
                ║   ✅ DIAT - IA DEV TOOLKIT INSTALADO CORRECTAMENTE            ║
                ║                                                               ║
                ╚═══════════════════════════════════════════════════════════════╝

                🚀 Comandos disponibles:

                diat                     Ver comandos disponibles
                diat --install            Instalar componentes
                diat --help               Ver ayuda

                ⚠️  IMPORTANTE: Reinicia la terminal o ejecuta:
                source ~/.bashrc  (o ~/.zshrc)


3. DIAT tiene los siguientes comandos:

        diat --help --h             Mostrar ayuda detallada de comandos
        diat --version --v          Mostrar versión actual
        diat --check                Verificar requisitos del sistema
        diat --install/--i [/ruta]   Instalar componentes en proyecto
        diat --install/--i           Instalar componentes globalmente segun agente en el que se trabaja
        diat --update [/ruta]    Actualizar componentes en proyecto
        diat --update            Actualizar componentes globales segun el agente en el que se trabaje
        diat --status [/ruta]    Mostrar estado de instalación
        diat --list              Listar en que proyectos se instalaron compoenentes DIAT y cuales.
        diat --uninstall         Desinstalar ia-dev-toolkit

4. Explicacion de comandos:

        a. diat --help/--h: Este comando muestra los comandos disponibles.
        b. diat --version/-v: Muestra la version isntalada de DIAT
        c. diat --check: Verificar requisitos del sistema
        d. diat --install/--i [/ruta]: Este comando muestra el siguiente menu : "
                ╔══════════════════════════════════════════════════════════╗
                ║          INSTALADOR MODULAR — ia-dev-toolkit             ║
                ╚══════════════════════════════════════════════════════════╝

                ¿Qué deseas instalar?

                [ ] Skills — Seleccionar skills específicas
                [ ] Agents — Seleccionar agentes específicos
                [ ] Workflows — Seleccionar workflows (+ tools + commands automáticos)
                [ ] Team Dev SAC — Skills SAC + Configuración
                [ ] Kit Completo — Agents + Skills + Workflows + Config
                
                ──────────────────────────────────────────────────────────────────────
                [ESPACIO] toggle | FELCHAS ARRIBA/ABAJO MOVER EN MENU  | [Q] SALIR |
                ────────────────────────────────────────────────────────────────────── 
                Selecciona una opción: [OPCION]  "

                d-1. El menu de seleccion para cualquier es OPCION [X] COMPONENTE X muestra: "
                ══════════════════════════════════════════════════════════════════════
                📦 [COMPONENTES] DISPONIBLES
                ══════════════════════════════════════════════════════════════════════
                [ ]  1. [NOMBRE-COMPONENTE]                    —  descripción
                [ ]  2. [NOMBRE-COMPONENTE]                    —  descripción
                [ ]  3. [NOMBRE-COMPONENTE]                    —  descripción
                .
                .
                .
                ──────────────────────────────────────────────────────────────────────
                [ESPACIO] toggle | FELCHAS ARRIBA/ABAJO MOVER EN MENU | [T] Todas | [N] Ninguna | [V] Volver
                ────────────────────────────────────────────────────────────────────── " 
        

                d-2. Todo menu debe ser interactivo, el usuario puede moverse con flecha arriba/abajo y marcar componentes precionando ESPACIO. EN el menu principal al precionar ESPACIO se activa el correspondiente sub-menu

                d-3.  Al seleccionar "Team Dev SAC — Skills SAC + Configuración"  se instala todo el paquete sac 
                ══════════════════════════════════════════════════════════════════════
                📋 SKILLS SAC DISPONIBLES
                ══════════════════════════════════════════════════════════════════════
                1. analizar-calidad-codigo             — Revisa código detectando code smells y violaciones | deps: .SAC/config/
                2. ejecutar-plan                       — Implementa planes actualizando Plan.md | deps: .SAC/config/
                3. init-reglas-arquitectonicas         — Genera reglas arquitectónicas del proyecto | deps: .SAC/config/
                4. planificar-hu                       — Genera plan técnico desde HU aprobada | deps: .SAC/config/
                5. refinar-hu                          — Refina HUs con criterios SMART y estimación | deps: .SAC/config/
                6. registrar-hallazgo                  — Captura incidencias mediante análisis paralelo | deps: .SAC/config/

        

                d-4. AL seleccionar "Kit Completo — Agents + Skills + Workflows + Config" 
                "       ╔══════════════════════════════════════════════════════════╗
                        ║              KIT COMPLETO — ia-dev-toolkit               ║
                        ╚══════════════════════════════════════════════════════════╝

                        Se instalarán:
                        → X agentes
                        → X skills
                        → X workflows
                        → X tools (asociados a workflows)
                        → X commands (asociados a workflows)
                        → Configuración .SAC/

                        ¿Continuar con la instalación completa? (s/N): "


                d-5. Al instalar Configuraciones SAC (/home/javier-garcia/Documentos/squad-skills/config/config/*.yml o *.yaml)  se debe de realizar "entrevista" al usuario para completar cada campo con respuesta del usuario.

        e. diat --update  **Objetivo:**
                ```
                    1. Actualiza CLI diat
                    2. Actualiza instalar.py
                    3. Lee instalacion.json
                    4. Para cada proyecto registrado:
                    a. Compara cache vs proyecto
                    b. Instala componentes faltantes
                    5. Actualiza versión en instalacion.json
                    6. Muestra resumen
                ```







###  main() — Guardar instalación

**Ubicación:** Línea ~1202 (antes de print_summary)

```python
    # Guardar registro de instalación
    from datetime import datetime
    components = {
        "skills": installed_skills,
        "agents": installed_agents,
        "workflows": installed_workflows,
        "tools": installed_tools,
        "commands": installed_commands,
        "config": sac_config_installed
    }
    save_installation(project_path, skills_target.parent.name, components)

    print_summary(project_path, installed_skills, installed_agents, installed_workflows, installed_tools, sac_config_installed)
    return True
```



###  Función resolve_dependencies()

```python
def resolve_dependencies(component_type, component_name, installed_components):
    """Resolver todas las dependencias de un componente."""
    deps = COMPONENT_DEPENDENCIES.get(component_type, {}).get(component_name, {})
    required = deps.get("requires", {})
    optional = deps.get("optional", {})

    missing = {
        "tools": [t for t in required.get("tools", [])
                  if t not in installed_components.get("tools", [])],
        "commands": [c for c in required.get("commands", [])
                     if c not in installed_components.get("commands", [])],
        "skills": [s for s in required.get("skills", [])
                   if s not in installed_components.get("skills", [])],
        "plugins": [p for p in required.get("plugins", [])
                    if p not in installed_components.get("plugins", [])]
    }

    return missing, optional
```

###  download_from_github() — Agregar commands

**Ubicación:** Línea ~1409 (después de workflows)

```python
        # 6. Descargar workflows (CON filtro ready: true)
        print_info("Descargando workflows (solo ready: true)...")
        workflows_ready = 0
        workflows_total = 0
        try:
            wf_items = github_api_get(f"{api_base}/workflows")
            if isinstance(wf_items, list):
                (dest_path / "workflows").mkdir(parents=True, exist_ok=True)
                for wf_dir in wf_items:
                    if wf_dir["type"] != "dir":
                        continue
                    workflows_total += 1
                    try:
                        wf_md_items = github_api_get(f"{api_base}/workflows/{wf_dir['name']}")
                        for f in wf_md_items:
                            if f["name"] == "workflow.md":
                                content = github_api_get_raw(f["download_url"])
                                if parse_frontmatter_ready(content):
                                    workflows_ready += 1
                                    download_directory(api_base, raw_base, f"workflows/{wf_dir['name']}", dest_path / "workflows" / wf_dir["name"])
                                    print_success(wf_dir["name"])
                                break
                    except Exception:
                        pass
        except Exception:
            print_warning("No se encontró carpeta workflows")

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

        # Resumen
        print_info(f"Resumen: {skills_ready}/{skills_total} skills, "
                   f"{agents_ready}/{agents_total} agents, "
                   f"{workflows_ready}/{workflows_total} workflows, "
                   f"{commands_count} commands")

        return dest_path
```
###  Ruta del Cache

**Ubicación:** Función `get_temp_repo_path()` (línea ~275)

```python
def get_temp_repo_path():
    if platform.system() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "ia-dev-toolkit"
        return Path.home() / "AppData" / "Local" / "ia-dev-toolkit"
    return Path.home() / ".local" / "share" / "ia-dev-toolkit"
```

### cmd_update() — Reinstalación automática

**Ubicación:** Función `cmd_update()` (línea ~517-580)

**Nueva lógica:**
```python
def cmd_update():
    """Actualizar el toolkit y reinstalar en proyectos registrados."""
    print_banner()

    # 1. Obtener versión remota
    remote_version = get_remote_version()

    # 2. Actualizar CLI diat
    print(f"  📦 Actualizando CLI diat...")
    # ... (código existente de actualización)

    # 3. Guardar versión instalada
    if remote_version:
        save_installed_version(remote_version)
        print(f"  📌 Versión instalada: {remote_version}")

    # 4. Leer instalaciones registradas
    installations = load_installations()

    if not installations:
        print(f"\n  ℹ️  No hay instalaciones registradas")
        print(f"     Ejecuta `diat --install /ruta/proyecto` para registrar")
        return

    # 5. Reinstalar en cada proyecto
    print(f"\n  📋 Leyendo instalaciones registradas...")
    print(f"  ✅ {len(installations)} proyectos encontrados")

    for inst in installations:
        project_path = Path(inst["project_path"])
        if project_path.exists():
            print(f"\n  📦 Reinstalando en {project_path}...")
            reinstall_components(inst, remote_version)
        else:
            print(f"\n  ⚠️  Proyecto no encontrado: {project_path}")

    # 6. Actualizar versión en instalacion.json
    update_installations_version(remote_version)

    print(f"\n{'═' * 70}")
    print(f"  ✅ ACTUALIZACIÓN COMPLETADA")
    print(f"{'═' * 70}")
    print(f"\n  ⚠️  Reinicia la terminal o ejecuta: diat --version\n")
```

### 1.4 cmd_install() — Instalación global ( --install -g)

**Ubicación:** Función `cmd_install()` (línea ~583-622)

**Nueva lógica:**
```python
def cmd_install():
    """Instalar componentes en un proyecto."""
    # Verificar modo no interactivo
    non_interactive = "--non-interactive" in sys.argv or "-ni" in sys.argv

    # Determinar ruta
    if len(sys.argv) > 2 and not sys.argv[2].startswith("-"):
        project_path = Path(sys.argv[2]).resolve()
    else:
        # Sin ruta — instalación global
        print(f"\n  ⚠️  No se especificó ruta. Los componentes se instalarán")
        print(f"     globalmente en ~/.local/share/ia-dev-toolkit/\n")

        # Preguntar agente
        print(f"  ¿En qué agente trabajas?\n")
        print(f"    [1] OpenCode")
        print(f"    [2] Claude Code")
        print(f"    [3] Gemini CLI")
        print(f"    [4] Codex")
        print(f"    [5] Otro\n")

        choice = input("  Selección: ").strip()

        if choice == "1":
            project_path = Path.home() / ".opencode"
            print(f"\n  ℹ️  OpenCode seleccionado")
        elif choice in ["2", "3", "4", "5"]:
            print(f"\n  ⚠️  Implementación en curso. Disculpa las molestias.")
            return
        else:
            print(f"  ❌ Selección inválida")
            return

    # ... resto de la función existente
```

### 1.5 Nuevas Funciones para instalacion.json

```python
def get_installations_file():
    """Obtener ruta del archivo de instalaciones."""
    return get_temp_repo_path() / "instalacion.json"

def load_installations():
    """Cargar instalaciones desde JSON."""
    import json
    installations_file = get_installations_file()
    if not installations_file.exists():
        return []
    try:
        data = json.loads(installations_file.read_text(encoding="utf-8"))
        return data.get("installations", [])
    except Exception:
        return []

def save_installation(project_path, platform, components):
    """Guardar una instalación en el JSON."""
    import json
    from datetime import datetime

    installations_file = get_installations_file()
    installations_file.parent.mkdir(parents=True, exist_ok=True)

    # Cargar existentes
    installations = load_installations()

    # Verificar si ya existe para ese proyecto
    existing_idx = None
    for i, inst in enumerate(installations):
        if inst["project_path"] == str(project_path):
            existing_idx = i
            break

    new_install = {
        "project_path": str(project_path),
        "platform": platform,
        "installed_at": datetime.now().isoformat(),
        "components": components
    }

    if existing_idx is not None:
        installations[existing_idx] = new_install
    else:
        installations.append(new_install)

    # Guardar
    data = {
        "version": get_installed_version(),
        "last_update": datetime.now().isoformat(),
        "installations": installations
    }
    installations_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

def update_installations_version(version):
    """Actualizar versión en todas las instalaciones."""
    import json
    from datetime import datetime

    installations_file = get_installations_file()
    if not installations_file.exists():
        return

    try:
        data = json.loads(installations_file.read_text(encoding="utf-8"))
        data["version"] = version
        data["last_update"] = datetime.now().isoformat()
        installations_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass

def reinstall_components(installation, version):
    """Reinstalar componentes desde cache."""
    # Implementar lógica de reinstalación
    # Comparar cache vs proyecto y copiar faltantes
    pass
```

---

### 2.4 Barra de Progreso

**Ubicación:** Nueva función

```python
def print_progress_bar(current, total, prefix="", suffix="", length=50):
    """Imprimir barra de progreso."""
    if total == 0:
        return
    percent = int(100 * current / total)
    filled = int(length * current / total)
    bar = "█" * filled + "░" * (length - filled)
    print(f"\r  {prefix}[{bar}] {percent}% - {suffix}", end="", flush=True)
    if current == total:
        print()
```

**Uso en main():**
```python
    # Instalar skills
    print(f"\n  Instalando skills...")
    for i, s in enumerate(skills):
        print_progress_bar(i, len(skills), "Skills", f"{i}/{len(skills)}")
        if install_skill(s, project_path, skills_target):
            installed_skills.append(s["name"])
    print_progress_bar(len(skills), len(skills), "Skills", "Completado")
```




## Verificación

### Pruebas a realizar:
1. `diat --install /home/user/test-project` — Verificar instalación normal
2. `diat --install -g` — Verificar instalación global
3. `diat --update` — Verificar reinstalación automática
4. `diat --status /home/user/test-project` — Verificar lectura de instalacion.json
5. Verificar que `instalacion.json` se crea y actualiza correctamente

### Archivos generados:
- `~/.local/share/ia-dev-toolkit/instalacion.json`
- Componentes instalados en ruta especificada


