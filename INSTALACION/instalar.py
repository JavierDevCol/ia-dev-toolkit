#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║           INSTALADOR MODULAR — ia-dev-toolkit                  ║
║   Instalador multiplataforma de skills, agentes, workflows   ║
║   y tools para equipos de desarrollo IA                      ║
╚═══════════════════════════════════════════════════════════════╝

Uso:
    python instalar.py                       # Modo interactivo
    python instalar.py "C:/mi/proyecto"      # Ruta como argumento
    python instalar.py --help                # Mostrar ayuda
"""

import os
import sys
import shutil
import subprocess
import platform
import json
import tarfile
import io
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ============================================
# CONFIGURACIÓN DE CODIFICACIÓN (Windows)
# ============================================
if platform.system() == "Windows":
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            import io
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================
# CONFIGURACIÓN
# ============================================
REPO_URL = "https://github.com/JavierDevCol/ia-dev-toolkit.git"
REPO_BRANCH = "main"

SAC_SKILLS = [
    "analizar-calidad-codigo",
    "ejecutar-plan",
    "init-reglas-arquitectonicas",
    "planificar-hu",
    "refinar-hu",
    "registrar-hallazgo",
    "sincronizar-backlog",
    "tomar-contexto",
    "validar-ca",
    "validar-hu"
]

# Descripciones cortas de skills
SKILL_DESCRIPTIONS = {
    "ado-wi-comments": "Gestiona comentarios en Work Items de ADO",
    "analizar-calidad-codigo": "Revisa código detectando code smells y violaciones",
    "architecture-inception": "Transforma specs en Blueprint de Arquitectura",
    "bitacora-tecnica": "Registra progreso de sesiones de trabajo",
    "bmm-crear-hu-devops": "Crea HUs con tareas en Azure DevOps",
    "bmm-manual-tecnico": "Genera Manual Técnico en Word (.docx)",
    "crear-adr": "Registra decisiones de arquitectura (ADRs)",
    "crear-estrategia": "Genera estrategias para chatbot WhatsApp",
    "crear-skill": "Meta-skill para crear otras skills",
    "crear-workflow": "Asistente para crear workflows canónicos",
    "ejecutar-plan": "Implementa planes actualizando Plan.md",
    "entrega-ambiente-banco": "Orquesta entrega de releases al banco",
    "evaluar-skill": "Evalúa calidad de skills existentes",
    "fix-develop": "Gestiona resolución de bugs en desarrollo",
    "fix-release": "Gestiona fixes sobre releases entregados",
    "git-branch-commit": "Crea ramas y gestiona commits Conventional",
    "git-doc-sync": "Sube documentos a Git selectivamente",
    "handoff-release": "Orquesta entregas con GitFlow y release notes",
    "init-reglas-arquitectonicas": "Genera reglas arquitectónicas del proyecto",
    "mermaid-diagram": "Genera diagramas Mermaid correctos",
    "pdf-from-markdown": "Convierte Markdown a PDF con Mermaid",
    "planificar-hu": "Genera plan técnico desde HU aprobada",
    "pr-config-audit": "Analiza PR y clasifica variables/secretos",
    "refinar-hu": "Refina HUs con criterios SMART y estimación",
    "registrar-hallazgo": "Captura incidencias mediante análisis paralelo",
    "sincronizar-backlog": "Corrige discrepancias entre backlog y disco",
    "tomar-contexto": "Detecta tecnología, arquitectura y DevOps",
    "validar-ca": "Verifica cumplimiento de criterios de aceptación",
    "validar-hu": "Valida HU contra criterios SMART y arquitectura",
    "vault-manager": "Gestiona operaciones HashiCorp Vault",
    "ado/task-creator": "Crea tareas hijas en Azure DevOps",
    "ado/pipeline-analyzer": "Analiza runs de pipelines ADO",
    "ado/profile-setup": "Crea perfiles de usuario para ADO",
    "ado/pr-reviewer": "Revisión estructurada de PRs en ADO",
    "ado/pr-creator": "Creación guiada de PRs en ADO",
    "ado/hu-publisher": "Publica HUs locales a Azure DevOps",
}

# Descripciones cortas de agentes
AGENT_DESCRIPTIONS = {
    "PO": "Product Owner — Transforma visión en backlog priorizado",
    "ARQUITECTO-SOFTWARE": "Arquitecto de Software — Diseño, trade-offs y ADRs",
    "ARQUITECTO-DEVOPS": "DevOps/SRE — Pipelines, IaC y observabilidad",
    "DESARROLLADOR": "Desarrollador — Código limpio, TDD y patrones",
}

# Descripciones cortas de workflows
WORKFLOW_DESCRIPTIONS = {
    "definir-vision-producto": "Transforma idea de negocio en Visión de Producto",
    "definir-arquitectura-solucion": "Diseña arquitectura integral con ADRs por fase",
    "gestionar-backlog-roadmap": "Sincroniza backlog técnico/funcional con WSJF",
}

# Dependencias de workflows
WORKFLOW_DEPENDENCIES = {
    "definir-vision-producto": "ninguna",
    "definir-arquitectura-solucion": "Visión de Producto",
    "gestionar-backlog-roadmap": "ADRs + Visión + artefactos previos",
}

# Tools requeridos por workflows
WORKFLOW_TOOLS = {
    "definir-vision-producto": [],
    "definir-arquitectura-solucion": [],
    "gestionar-backlog-roadmap": [],
}

# Descripciones de tools
TOOL_DESCRIPTIONS = {
    "workflow-discover": "Lista workflows disponibles desde .SAC/workflows/",
}

# Dependencias de skills
SKILL_DEPENDENCIES = {
    "ado-wi-comments": "Azure DevOps MCP",
    "analizar-calidad-codigo": ".SAC/config/",
    "architecture-inception": "ninguna",
    "bitacora-tecnica": "ninguna",
    "bmm-crear-hu-devops": "Azure DevOps MCP",
    "bmm-manual-tecnico": "Python 3, python-docx",
    "crear-adr": "ninguna",
    "crear-estrategia": "ms-banca-conversacion (Java/Spring)",
    "crear-skill": "ninguna",
    "crear-workflow": "ninguna",
    "ejecutar-plan": ".SAC/config/",
    "entrega-ambiente-banco": "ninguna",
    "evaluar-skill": "ninguna",
    "fix-develop": "ninguna",
    "fix-release": "ninguna",
    "git-branch-commit": "Git",
    "git-doc-sync": "Python 3",
    "handoff-release": "Git",
    "init-reglas-arquitectonicas": ".SAC/config/",
    "mermaid-diagram": "ninguna",
    "pdf-from-markdown": "Node.js, md-to-pdf",
    "planificar-hu": ".SAC/config/",
    "pr-config-audit": "Git",
    "refinar-hu": ".SAC/config/",
    "registrar-hallazgo": ".SAC/config/",
    "sincronizar-backlog": ".SAC/config/",
    "tomar-contexto": ".SAC/config/",
    "validar-ca": ".SAC/config/",
    "validar-hu": ".SAC/config/",
    "vault-manager": "Vault CLI",
    "ado/task-creator": "Azure DevOps MCP",
    "ado/pipeline-analyzer": "Azure DevOps MCP",
    "ado/profile-setup": "Azure DevOps MCP",
    "ado/pr-reviewer": "Azure DevOps MCP",
    "ado/pr-creator": "Azure DevOps MCP",
    "ado/hu-publisher": "Azure DevOps MCP",
}

REQUIREMENTS_MAP = {
    "git": {
        "check_cmd": ["git", "--version"],
        "install_url": "https://git-scm.com/downloads"
    },
    "vault": {
        "check_cmd": ["vault", "--version"],
        "install_url": "https://www.vaultproject.io/downloads"
    },
    "kubectl": {
        "check_cmd": ["kubectl", "version", "--client"],
        "install_url": "https://kubernetes.io/docs/tasks/tools/"
    },
    "node": {
        "check_cmd": ["node", "--version"],
        "install_url": "https://nodejs.org/"
    },
    "python": {
        "check_cmd": ["python3", "--version"],
        "alt_cmd": ["python", "--version"],
        "install_url": "https://www.python.org/downloads/"
    }
}


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🛠️  INSTALADOR MODULAR — ia-dev-toolkit                      ║
║   Skills · Agents · Workflows · Tools · Config                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def print_success(message):
    print(f"  ✅ {message}")


def print_error(message):
    print(f"  ❌ {message}")


def print_info(message):
    print(f"  ℹ️  {message}")


def print_warning(message):
    print(f"  ⚠️  {message}")


def get_script_directory():
    return Path(__file__).parent.absolute()


def get_root_directory():
    return get_script_directory().parent


def get_temp_repo_path():
    if platform.system() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            base_path = Path(local_app_data) / "ia-dev-toolkit" / "repo"
        else:
            base_path = Path.home() / "AppData" / "Local" / "ia-dev-toolkit" / "repo"
    else:
        base_path = Path.home() / ".local" / "share" / "ia-dev-toolkit" / "repo"
    return base_path


# ============================================
# FUNCIONES DE VERIFICACIÓN DE REQUISITOS
# ============================================

def check_tool(tool_name):
    req = REQUIREMENTS_MAP.get(tool_name)
    if not req:
        return False
    try:
        result = subprocess.run(
            req["check_cmd"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True
        if "alt_cmd" in req:
            result = subprocess.run(
                req["alt_cmd"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return False


def parse_compatibility(skill_dir):
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return "No information available"
    try:
        content = skill_file.read_text(encoding="utf-8")
        in_frontmatter = False
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and stripped.startswith("compatibility:"):
                value = stripped.split(":", 1)[1].strip()
                value = value.strip('"').strip("'")
                return value
        return "No special requirements"
    except Exception:
        return "No information available"


def extract_required_tools(compatibility_str):
    tools = []
    lower = compatibility_str.lower()
    if "git" in lower:
        tools.append("git")
    if "vault" in lower:
        tools.append("vault")
    if "kubectl" in lower or "kube" in lower:
        tools.append("kubectl")
    if "node" in lower:
        tools.append("node")
    if "python" in lower:
        tools.append("python")
    if "azure devops" in lower or "ado mcp" in lower:
        tools.append("azure_devops")
    if ".sac" in lower or "sac/config" in lower:
        tools.append("sac_config")
    return tools


# ============================================
# FUNCIONES DE ESCANEO
# ============================================

def scan_skills(skills_dir):
    skills = []
    for skill_file in sorted(skills_dir.rglob("SKILL.md")):
        skill_dir = skill_file.parent
        skill_name = skill_dir.name
        rel_path = skill_dir.relative_to(skills_dir)

        if any(s["name"] == skill_name for s in skills):
            continue

        compatibility = parse_compatibility(skill_dir)
        is_sac = skill_name in SAC_SKILLS
        description = SKILL_DESCRIPTIONS.get(skill_name, "Sin descripción")
        dependencies = SKILL_DEPENDENCIES.get(skill_name, "ninguna")

        skills.append({
            "name": skill_name,
            "path": skill_dir,
            "rel_path": str(rel_path),
            "parent": str(rel_path.parent) if str(rel_path.parent) != "." else None,
            "compatibility": compatibility,
            "is_sac": is_sac,
            "description": description,
            "dependencies": dependencies,
            "tools_required": extract_required_tools(compatibility)
        })
    return skills


def scan_agents(agents_dir):
    agents = []
    if not agents_dir.exists():
        return agents
    for agent_file in sorted(agents_dir.glob("*.md")):
        name = agent_file.stem
        agents.append({
            "name": name,
            "path": agent_file,
            "filename": agent_file.name,
            "description": AGENT_DESCRIPTIONS.get(name, "Agente de IA"),
            "dependencies": "ninguna"
        })
    return agents


def scan_workflows(workflows_dir):
    workflows = []
    if not workflows_dir.exists():
        return workflows
    for wf_dir in sorted(workflows_dir.iterdir()):
        if not wf_dir.is_dir():
            continue
        wf_file = wf_dir / "workflow.md"
        if not wf_file.exists():
            continue
        name = wf_dir.name
        description = WORKFLOW_DESCRIPTIONS.get(name, "Workflow")
        dependencies = WORKFLOW_DEPENDENCIES.get(name, "ninguna")
        phases_dir = wf_dir / "fases"
        templates_dir = wf_dir / "plantillas"
        phase_count = len(list(phases_dir.glob("*.md"))) if phases_dir.exists() else 0
        template_count = len(list(templates_dir.glob("*.md"))) if templates_dir.exists() else 0
        workflows.append({
            "name": name,
            "path": wf_dir,
            "description": description,
            "dependencies": dependencies,
            "phase_count": phase_count,
            "template_count": template_count,
            "tools_required": WORKFLOW_TOOLS.get(name, [])
        })
    return workflows


def scan_tools(tools_dir):
    tools = []
    if not tools_dir.exists():
        return tools
    for item in sorted(tools_dir.iterdir()):
        if item.is_dir() and item.name != "scripts":
            continue
        if item.is_file() and item.suffix in (".ts", ".js", ".py", ".sh"):
            name = item.stem
            tools.append({
                "name": name,
                "path": item,
                "description": TOOL_DESCRIPTIONS.get(name, "Tool"),
                "type": item.suffix,
                "dependencies": "ninguna"
            })
        elif item.is_dir():
            for script in sorted(item.glob("*")):
                if script.is_file() and script.suffix in (".ts", ".js", ".py", ".sh"):
                    name = script.stem
                    tools.append({
                        "name": name,
                        "path": script,
                        "description": TOOL_DESCRIPTIONS.get(name, "Tool"),
                        "type": script.suffix,
                        "dependencies": "ninguna"
                    })
    return tools


# ============================================
# FUNCIONES DE INSTALACIÓN
# ============================================

def get_skills_target(project_path):
    for platform_dir in [".claude", ".opencode", ".agent"]:
        platform_path = project_path / platform_dir
        if platform_path.exists():
            return platform_path / "skills"
    target = project_path / ".agent" / "skills"
    target.mkdir(parents=True, exist_ok=True)
    return target


def install_skill(skill_info, project_path, skills_target):
    skill_src = skill_info["path"]
    skill_name = skill_info["name"]
    skill_dst = skills_target / skill_name

    if skill_dst.exists() or skill_dst.is_symlink():
        if skill_dst.is_symlink():
            skill_dst.unlink()
        else:
            shutil.rmtree(skill_dst)

    try:
        skill_dst.symlink_to(skill_src)
        print_success(f"{skill_name}")
        return True
    except Exception as e:
        print_error(f"{skill_name} — Error: {e}")
        return False


def install_agent(agent_info, project_path):
    agents_dest = project_path / ".opencode" / "agents"
    agents_dest.mkdir(parents=True, exist_ok=True)

    agent_src = agent_info["path"]
    agent_dst = agents_dest / agent_info["filename"]

    try:
        shutil.copy2(agent_src, agent_dst)
        print_success(f"{agent_info['name']}")
        return True
    except Exception as e:
        print_error(f"{agent_info['name']} — Error: {e}")
        return False


def install_workflow(workflow_info, project_path, root_dir):
    wf_dest = project_path / ".SAC" / "workflows" / workflow_info["name"]
    wf_src = workflow_info["path"]

    try:
        if wf_dest.exists():
            shutil.rmtree(wf_dest)
        shutil.copytree(wf_src, wf_dest)
        print_success(f"{workflow_info['name']}")
        return True
    except Exception as e:
        print_error(f"{workflow_info['name']} — Error: {e}")
        return False


def install_tool(tool_info, project_path):
    tools_dest = project_path / ".opencode" / "tools"
    tools_dest.mkdir(parents=True, exist_ok=True)

    tool_src = tool_info["path"]
    tool_dst = tools_dest / tool_src.name

    try:
        if tool_src.suffix == ".sh":
            scripts_dest = tools_dest / "scripts"
            scripts_dest.mkdir(exist_ok=True)
            tool_dst = scripts_dest / tool_src.name
        shutil.copy2(tool_src, tool_dst)
        print_success(f"{tool_info['name']}")
        return True
    except Exception as e:
        print_error(f"{tool_info['name']} — Error: {e}")
        return False


def ask_project_config(project_path):
    """Solicita datos del proyecto al usuario para autocompletar CONFIG_USER.yaml."""
    print(f"\n{'═' * 60}")
    print(f"  📝 CONFIGURACIÓN DEL PROYECTO")
    print(f"{'═' * 60}")
    print(f"  (Presiona Enter para usar el valor por defecto)\n")

    # Nombre del usuario
    default_user = os.environ.get("USER", os.environ.get("USERNAME", "Usuario"))
    user_name = input(f"  Tu nombre [{default_user}]: ").strip()
    if not user_name:
        user_name = default_user

    # Nombre del proyecto
    default_project = project_path.name
    project_name = input(f"  Nombre del proyecto [{default_project}]: ").strip()
    if not project_name:
        project_name = default_project

    # Idioma
    print(f"\n  Idioma para documentación:")
    print(f"    [1] Español (es)")
    print(f"    [2] English (en)")
    print(f"    [3] Português (pt)")
    lang_choice = input(f"  Selección [1]: ").strip()
    lang_map = {"1": "es", "2": "en", "3": "pt"}
    lang = lang_map.get(lang_choice, "es")

    print(f"\n  Resumen:")
    print(f"    Usuario:   {user_name}")
    print(f"    Proyecto:  {project_name}")
    print(f"    Idioma:    {lang}")

    return {
        "user_name": user_name,
        "project_name": project_name,
        "lang": lang
    }


def install_sac_config(project_path, root_dir, project_config=None):
    sac_dest = project_path / ".SAC"

    print_info("Instalando configuración Team Dev SAC...")

    (sac_dest / "config").mkdir(parents=True, exist_ok=True)
    (sac_dest / "session").mkdir(exist_ok=True)

    config_source = root_dir / "config" / "config"
    if config_source.exists():
        for config_file in config_source.glob("*.yaml"):
            shutil.copy2(config_file, sac_dest / "config" / config_file.name)
            print_success(f"config/{config_file.name}")

    # Autocompletar CONFIG_SYSTEM.yaml con rutas
    config_system = sac_dest / "config" / "CONFIG_SYSTEM.yaml"
    if config_system.exists():
        try:
            content = config_system.read_text(encoding="utf-8")
            normalized_root = Path(project_path).resolve().as_posix()
            updated = content.replace("{project-root}", normalized_root)
            if updated != content:
                config_system.write_text(updated, encoding="utf-8")
                print_success("CONFIG_SYSTEM.yaml actualizado con ruta del proyecto")
        except Exception as e:
            print_warning(f"No se pudo actualizar CONFIG_SYSTEM.yaml: {e}")

    # Autocompletar CONFIG_USER.yaml con datos del proyecto
    if project_config:
        config_user = sac_dest / "config" / "CONFIG_USER.yaml"
        if config_user.exists():
            try:
                content = config_user.read_text(encoding="utf-8")
                # Reemplazar nombre de usuario
                content = content.replace(
                    'nombre: "Javier Garcia"',
                    f'nombre: "{project_config["user_name"]}"'
                )
                # Reemplazar nombre de proyecto
                content = content.replace(
                    'nombre: "app-barber"',
                    f'nombre: "{project_config["project_name"]}"'
                )
                # Reemplazar idiomas
                content = content.replace(
                    'documentacion: "es"',
                    f'documentacion: "{project_config["lang"]}"'
                )
                content = content.replace(
                    'comunicacion: "es"',
                    f'comunicacion: "{project_config["lang"]}"'
                )
                config_user.write_text(content, encoding="utf-8")
                print_success("CONFIG_USER.yaml actualizado con datos del proyecto")
            except Exception as e:
                print_warning(f"No se pudo actualizar CONFIG_USER.yaml: {e}")

    return True


# ============================================
# FUNCIONES DE CHECKBOX INTERACTIVO
# ============================================

def show_checkbox_menu(items, item_type, show_deps=True):
    """Muestra menú con checkboxes [ ]/[x] y permite selección interactiva."""
    selected = {item["name"]: False for item in items}

    while True:
        print(f"\n{'═' * 70}")
        print(f"  {item_type} DISPONIBLES")
        print(f"{'═' * 70}")

        for i, item in enumerate(items, 1):
            check = "x" if selected[item["name"]] else " "
            deps = f" | deps: {item['dependencies']}" if show_deps and item.get("dependencies", "ninguna") != "ninguna" else ""
            desc = item.get("description", "")
            print(f"  [{check}] {i:2}. {item['name']:<35} — {desc}{deps}")

        print(f"\n{'─' * 70}")
        print(f"  Comandos: [número] toggle | [T] Todas | [N] Ninguna | [V] Volver")
        print(f"{'─' * 70}")

        response = input("  Selección: ").strip().upper()

        if response == "V":
            return None
        elif response == "T":
            for name in selected:
                selected[name] = True
        elif response == "N":
            for name in selected:
                selected[name] = False
        else:
            try:
                nums = [int(x) for x in response.split()]
                for n in nums:
                    if 1 <= n <= len(items):
                        name = items[n - 1]["name"]
                        selected[name] = not selected[name]
            except (ValueError, IndexError):
                print_error("Selección inválida")
                continue

        chosen = [item for item in items if selected[item["name"]]]
        if chosen:
            print(f"\n  Seleccionados: {', '.join(item['name'] for item in chosen)}")
            confirm = input("  ¿Confirmar selección? (s/N): ").strip().lower()
            if confirm == 's':
                return chosen


# ============================================
# INSTALACIÓN DE ALMA (PERSONALIDAD)
# ============================================

def get_personality_file(project_path):
    """Determinar qué archivo de personalidad crear/actualizar según la plataforma."""
    # Buscar plataforma existente
    for platform_dir in [".claude", ".opencode", ".agent"]:
        platform_path = project_path / platform_dir
        if platform_path.exists():
            # Mapear plataforma a archivo de personalidad
            if platform_dir == ".claude":
                return project_path / "claude.md"
            elif platform_dir == ".opencode":
                return project_path / "opencode.md"
            elif platform_dir == ".agent":
                return project_path / "agent.md"

    # Si no existe ninguna plataforma, crear .agent/ y agent.md
    (project_path / ".agent").mkdir(parents=True, exist_ok=True)
    return project_path / "agent.md"


def install_alma(project_path, root_dir):
    """Instalar alma (personalidad) del agente."""
    print(f"\n╔══════════════════════════════════════════════════════════╗")
    print(f"║              ALMA — Personalidad del Agente              ║")
    print(f"╚══════════════════════════════════════════════════════════╝")

    # Buscar archivo AGENTS.md en el repo
    agent_md_path = root_dir / "AGENTS.md"
    if not agent_md_path.exists():
        print_error("No se encontró AGENTS.md en el repositorio")
        return False

    # Leer contenido de AGENTS.md
    try:
        agent_content = agent_md_path.read_text(encoding="utf-8")
    except Exception as e:
        print_error(f"Error al leer AGENTS.md: {e}")
        return False

    # Determinar archivo de personalidad destino
    personality_file = get_personality_file(project_path)

    print_info(f"Archivo de personalidad: {personality_file.name}")

    # Si el archivo ya existe, agregar contenido al inicio
    if personality_file.exists():
        try:
            existing_content = personality_file.read_text(encoding="utf-8")
            # Verificar si el contenido ya está al inicio
            if agent_content.strip() in existing_content:
                print_warning("El contenido de AGENTS.md ya está presente")
                return True

            # Agregar contenido al inicio
            new_content = agent_content + "\n\n" + existing_content
            personality_file.write_text(new_content, encoding="utf-8")
            print_success(f"Contenido de AGENTS.md agregado al inicio de {personality_file.name}")
            return True
        except Exception as e:
            print_error(f"Error al actualizar {personality_file.name}: {e}")
            return False
    else:
        # Crear archivo con contenido de AGENTS.md
        try:
            personality_file.write_text(agent_content, encoding="utf-8")
            print_success(f"{personality_file.name} creado con contenido de AGENTS.md")
            return True
        except Exception as e:
            print_error(f"Error al crear {personality_file.name}: {e}")
            return False


# ============================================
# MENÚS
# ============================================

def show_main_menu():
    print("""
╔══════════════════════════════════════════════════════════╗
║          INSTALADOR MODULAR — ia-dev-toolkit              ║
╚══════════════════════════════════════════════════════════╝

¿Qué deseas instalar?

  [1] Skills — Seleccionar skills específicas
  [2] Agents — Seleccionar agentes específicos
  [3] Workflows — Seleccionar workflows (+ tools automáticos)
  [4] Tools — Seleccionar tools individuales
  [5] Team Dev SAC — Skills SAC + Configuración
  [6] Kit Completo — Agents + Skills + Workflows + Tools + Config
  [7] Alma — Personalidad del agente (AGENT.md)
  [Q] Salir
    """)


def show_agents_menu(agents):
    """Muestra menú de agentes con checkboxes."""
    return show_checkbox_menu(agents, "👤 AGENTES", show_deps=False)


def show_workflows_menu(workflows):
    """Muestra menú de workflows con checkboxes."""
    return show_checkbox_menu(workflows, "📋 WORKFLOWS", show_deps=True)


def show_tools_menu(tools):
    """Muestra menú de tools con checkboxes."""
    return show_checkbox_menu(tools, "🔧 TOOLS", show_deps=False)


def show_requirements_preview(items, item_type):
    print(f"\n{'═' * 60}")
    print(f" REQUISITOS — {item_type}")
    print(f"{'═' * 60}")

    for item in items:
        deps = item.get("dependencies", "ninguna")
        if deps != "ninguna":
            print(f"\n  {item['name']}: {deps}")

    print(f"{'═' * 60}")


# ============================================
# FLUJO PRINCIPAL
# ============================================

def main():
    print_banner()

    root_dir = get_root_directory()

    if not (root_dir / "skills").exists():
        print_info("No se encontró instalación local, usando repositorio remoto...")
        root_dir = ensure_repo_available()
        if not root_dir:
            print_error("No se pudo obtener el repositorio")
            return False

    skills_dir = root_dir / "skills"
    agents_dir = root_dir / "agents"
    workflows_dir = root_dir / "workflows"
    tools_dir = root_dir / "tools"

    print_info("Escaneando componentes...")
    skills = scan_skills(skills_dir)
    agents = scan_agents(agents_dir)
    workflows = scan_workflows(workflows_dir)
    tools = scan_tools(tools_dir)
    print_success(f"Encontrados: {len(skills)} skills, {len(agents)} agentes, {len(workflows)} workflows, {len(tools)} tools")

    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        project_path = Path(sys.argv[1])
    else:
        response = input("\n  Ruta del proyecto: ").strip()
        if not response:
            print_error("Debe especificar una ruta")
            return False
        project_path = Path(response)

    if not project_path.exists():
        create = input(f"  La ruta {project_path} no existe. ¿Crearla? (s/N): ").strip().lower()
        if create == 's':
            project_path.mkdir(parents=True, exist_ok=True)
        else:
            print_error("Instalación cancelada")
            return False

    skills_target = get_skills_target(project_path)
    print_success(f"Plataforma detectada: {skills_target.parent.name}")

    installed_skills = []
    installed_agents = []
    installed_workflows = []
    installed_tools = []
    sac_config_installed = False

    while True:
        show_main_menu()
        choice = input("  Selecciona una opción: ").strip().upper()

        if choice == "Q":
            break

        # ─── [1] SKILLS ───────────────────────────────────────
        elif choice == "1":
            selected = show_checkbox_menu(skills, "📦 SKILLS")
            if selected is None:
                continue

            print(f"\n  Verificando requisitos...")
            show_requirements_preview(selected, "SKILLS")

            confirm = input("\n  ¿Continuar con la instalación? (s/N): ").strip().lower()
            if confirm != 's':
                continue

            print(f"\n  Instalando skills...")
            has_sac = any(s["is_sac"] for s in selected)

            if has_sac and not sac_config_installed:
                project_config = ask_project_config(project_path)
                install_sac_config(project_path, root_dir, project_config)
                sac_config_installed = True

            for s in selected:
                if install_skill(s, project_path, skills_target):
                    installed_skills.append(s["name"])

        # ─── [2] AGENTS ───────────────────────────────────────
        elif choice == "2":
            if not agents:
                print_warning("No se encontraron agentes")
                continue

            selected = show_agents_menu(agents)
            if selected is None:
                continue

            print(f"\n  Instalando agentes...")
            for a in selected:
                if install_agent(a, project_path):
                    installed_agents.append(a["name"])

        # ─── [3] WORKFLOWS ────────────────────────────────────
        elif choice == "3":
            if not workflows:
                print_warning("No se encontraron workflows")
                continue

            selected = show_workflows_menu(workflows)
            if selected is None:
                continue

            # Verificar si se necesitan tools adicionales
            all_wf_tools = set()
            for wf in selected:
                all_wf_tools.update(wf.get("tools_required", []))

            if all_wf_tools:
                print(f"\n  ⚠️  Tools requeridos por los workflows seleccionados:")
                for tool_name in all_wf_tools:
                    print(f"    → {tool_name}")

            # Instalar tools automáticamente
            print(f"\n  Instalando tools requeridos...")
            for tool in tools:
                if install_tool(tool, project_path):
                    installed_tools.append(tool["name"])

            print(f"\n  Instalando workflows...")
            for wf in selected:
                if install_workflow(wf, project_path, root_dir):
                    installed_workflows.append(wf["name"])

        # ─── [4] TOOLS ────────────────────────────────────────
        elif choice == "4":
            if not tools:
                print_warning("No se encontraron tools")
                continue

            selected = show_tools_menu(tools)
            if selected is None:
                continue

            print(f"\n  Instalando tools...")
            for t in selected:
                if install_tool(t, project_path):
                    installed_tools.append(t["name"])

        # ─── [5] TEAM DEV SAC ─────────────────────────────────
        elif choice == "5":
            sac_skills_list = [s for s in skills if s["is_sac"]]

            print(f"\n╔══════════════════════════════════════════════════════════╗")
            print(f"║              TEAM DEV SAC — Skills + Config             ║")
            print(f"╚══════════════════════════════════════════════════════════╝")

            selected = show_checkbox_menu(sac_skills_list, "📋 SKILLS SAC")
            if selected is None:
                continue

            if not sac_config_installed:
                project_config = ask_project_config(project_path)
                print(f"\n  Instalando configuración Team Dev SAC...")
                install_sac_config(project_path, root_dir, project_config)
                sac_config_installed = True

            print(f"\n  Instalando skills SAC...")
            for s in selected:
                if install_skill(s, project_path, skills_target):
                    installed_skills.append(s["name"])

        # ─── [6] KIT COMPLETO ─────────────────────────────────
        elif choice == "6":
            print(f"\n╔══════════════════════════════════════════════════════════╗")
            print(f"║              KIT COMPLETO — ia-dev-toolkit                ║")
            print(f"╚══════════════════════════════════════════════════════════╝")

            print(f"\n  Se instalarán:")
            print(f"    → {len(agents)} agentes")
            print(f"    → {len(skills)} skills")
            print(f"    → {len(workflows)} workflows")
            print(f"    → {len(tools)} tools")
            print(f"    → Configuración .SAC/")

            confirm = input("\n  ¿Continuar con la instalación completa? (s/N): ").strip().lower()
            if confirm != 's':
                continue

            # Instalar config SAC
            if not sac_config_installed:
                project_config = ask_project_config(project_path)
                install_sac_config(project_path, root_dir, project_config)
                sac_config_installed = True

            # Instalar agentes
            print(f"\n  Instalando agentes...")
            for a in agents:
                if install_agent(a, project_path):
                    installed_agents.append(a["name"])

            # Instalar skills
            print(f"\n  Instalando skills...")
            for s in skills:
                if install_skill(s, project_path, skills_target):
                    installed_skills.append(s["name"])

            # Instalar tools
            print(f"\n  Instalando tools...")
            for t in tools:
                if install_tool(t, project_path):
                    installed_tools.append(t["name"])

            # Instalar workflows
            print(f"\n  Instalando workflows...")
            for wf in workflows:
                if install_workflow(wf, project_path, root_dir):
                    installed_workflows.append(wf["name"])

        # ─── [7] ALMA (PERSONALIDAD) ──────────────────────────
        elif choice == "7":
            install_alma(project_path, root_dir)

        else:
            print_error("Opción inválida")

    print_summary(project_path, installed_skills, installed_agents, installed_workflows, installed_tools, sac_config_installed)
    return True


def ensure_repo_available():
    temp_repo_path = get_temp_repo_path()

    # Si ya existe el repo local con las carpetas necesarias, usarlo
    if temp_repo_path.exists():
        required_dirs = ["skills", "agents", "workflows", "tools", "config"]
        if all((temp_repo_path / d).exists() for d in required_dirs):
            print_info(f"Repositorio local encontrado en {temp_repo_path}")
            # Intentar actualizar
            try:
                if (temp_repo_path / ".git").exists():
                    subprocess.run(
                        ["git", "-C", str(temp_repo_path), "pull", "--ff-only"],
                        capture_output=True, text=True, timeout=60
                    )
                else:
                    # Sin git, verificar si tiene contenido reciente
                    print_info("Repositorio sin git, usando versión local")
            except Exception:
                pass
            return temp_repo_path

    # Descargar solo lo necesario desde GitHub API
    print_info("Descargando componentes desde GitHub...")
    return download_from_github(temp_repo_path)


def download_from_github(dest_path):
    """Descarga solo las carpetas necesarias desde GitHub usando la API."""
    # Extraer owner/repo de la URL
    # REPO_URL = "https://github.com/JavierDevCol/ia-dev-toolkit.git"
    parts = REPO_URL.replace("https://github.com/", "").replace(".git", "").split("/")
    owner, repo = parts[0], parts[1]

    # URL del tarball
    tarball_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{REPO_BRANCH}.tar.gz"

    # Carpetas necesarias para el instalador
    REQUIRED_DIRS = ["skills", "agents", "workflows", "tools", "config"]

    try:
        print_info(f"Descargando desde {tarball_url}...")
        req = urllib.request.Request(tarball_url, headers={"User-Agent": "ia-dev-toolkit-installer"})
        response = urllib.request.urlopen(req, timeout=120)
        tarball_data = response.read()

        print_info(f"Descargado: {len(tarball_data) / 1024:.0f} KB")
        print_info("Extrayendo componentes necesarios...")

        # Crear directorio destino
        dest_path.mkdir(parents=True, exist_ok=True)

        # Extraer solo las carpetas necesarias del tarball
        with tarfile.open(fileobj=io.BytesIO(tarball_data), mode="r:gz") as tar:
            # El tarball tiene prefijo "ia-dev-toolkit-main/"
            prefix = f"{repo}-{REPO_BRANCH}/"

            for member in tar.getmembers():
                # Verificar si el archivo pertenece a una carpeta necesaria
                if not member.name.startswith(prefix):
                    continue

                rel_path = member.name[len(prefix):]
                if not rel_path:
                    continue

                # Verificar si pertenece a una carpeta requerida
                is_required = False
                for req_dir in REQUIRED_DIRS:
                    if rel_path.startswith(req_dir + "/") or rel_path == req_dir:
                        is_required = True
                        break

                if not is_required:
                    continue

                # Extraer archivo
                dest_file = dest_path / rel_path

                if member.isdir():
                    dest_file.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    src_file = tar.extractfile(member)
                    if src_file:
                        with open(dest_file, "wb") as f:
                            f.write(src_file.read())

        print_success(f"Componentes descargados en {dest_path}")

        # Verificar que se descargaron las carpetas necesarias
        missing = [d for d in REQUIRED_DIRS if not (dest_path / d).exists()]
        if missing:
            print_warning(f"Carpetas no encontradas: {', '.join(missing)}")
            return None

        return dest_path

    except urllib.error.URLError as e:
        print_error(f"Error de red: {e}")
        print_info("Verifica tu conexión a internet")
        return None
    except Exception as e:
        print_error(f"Error al descargar: {e}")
        return None


def print_summary(project_path, skills, agents, workflows, tools, sac_installed):
    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                  ✅ INSTALACIÓN COMPLETADA                    ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    print(f"📍 Ubicación: {project_path}\n")

    if sac_installed:
        print("📁 Team Dev SAC instalado:")
        print(f"   ├── .SAC/config/")
        print(f"   └── .SAC/session/\n")

    if skills:
        print(f"📦 Skills instaladas ({len(skills)}):")
        for s in skills:
            print(f"   → {s}")
        print()

    if agents:
        print(f"👤 Agentes instalados ({len(agents)}):")
        for a in agents:
            print(f"   → {a}")
        print()

    if workflows:
        print(f"📋 Workflows instalados ({len(workflows)}):")
        for w in workflows:
            print(f"   → {w}")
        print()

    if tools:
        print(f"🔧 Tools instalados ({len(tools)}):")
        for t in tools:
            print(f"   → {t}")
        print()

    print("🚀 Cómo usar:")
    print("   1. Abre tu IDE (VS Code, Cursor, etc.)")
    print("   2. Activa las skills según la documentación")
    print("   3. Usa los agentes en tu chat de IA")
    print("   4. Ejecuta workflows desde .SAC/workflows/\n")


def print_help():
    print("""
📖 USO:
    python instalar.py [RUTA]           Instala en la ruta especificada
    python instalar.py                  Modo interactivo
    python instalar.py --help           Mostrar ayuda

📍 EJEMPLOS:
    python instalar.py "C:/mi-proyecto"
    python instalar.py "/home/usuario/mi-proyecto"

📦 OPCIONES DE INSTALACIÓN:
    [1] Skills — Seleccionar skills específicas con checkboxes
    [2] Agents — Seleccionar agentes específicos con checkboxes
    [3] Workflows — Seleccionar workflows (+ tools automáticos)
    [4] Tools — Seleccionar tools individuales
    [5] Team Dev SAC — Skills SAC + Configuración
    [6] Kit Completo — Agents + Skills + Workflows + Tools + Config
    """)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
    else:
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n  Instalación cancelada por el usuario.")
            sys.exit(0)
