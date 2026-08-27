#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║           INSTALADOR DE SKILLS — squad-skills                ║
║   Instalador multiplataforma de skills y agentes IA          ║
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
REPO_URL = "https://github.com/JavierDevCol/squad-skills.git"
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
║   🛠️  INSTALADOR DE SKILLS — squad-skills                    ║
║   Instalador multiplataforma de skills y agentes IA           ║
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
            base_path = Path(local_app_data) / "squad-skills" / "repo"
        else:
            base_path = Path.home() / "AppData" / "Local" / "squad-skills" / "repo"
    else:
        base_path = Path.home() / ".local" / "share" / "squad-skills" / "repo"
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

        skills.append({
            "name": skill_name,
            "path": skill_dir,
            "rel_path": str(rel_path),
            "parent": str(rel_path.parent) if str(rel_path.parent) != "." else None,
            "compatibility": compatibility,
            "is_sac": is_sac,
            "tools_required": extract_required_tools(compatibility)
        })
    return skills


def scan_agents(agents_dir):
    agents = []
    if not agents_dir.exists():
        return agents
    for agent_file in sorted(agents_dir.glob("*.md")):
        agents.append({
            "name": agent_file.stem,
            "path": agent_file,
            "filename": agent_file.name
        })
    return agents


# ============================================
# FUNCIONES DE INSTALACIÓN
# ============================================

def get_skills_target(project_path):
    for platform_dir in [".opencode", ".claude", ".agent"]:
        platform_path = project_path / platform_dir
        if platform_path.exists():
            return platform_path / "skills"
    target = project_path / ".opencode" / "skills"
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


def install_sac_config(project_path, root_dir):
    sac_dest = project_path / ".SAC"

    print_info("Instalando configuración Team Dev SAC...")

    (sac_dest / "config").mkdir(parents=True, exist_ok=True)
    (sac_dest / "session").mkdir(exist_ok=True)

    config_source = root_dir / "config" / "config"
    if config_source.exists():
        for config_file in config_source.glob("*.yaml"):
            shutil.copy2(config_file, sac_dest / "config" / config_file.name)
            print_success(f"config/{config_file.name}")

    # Plantillas HU movidas a assets/ de cada skill (refinar-hu, planificar-hu, registrar-hallazgo, ejecutar-plan)
    # No se copian plantillas desde config/plantillas/ (directorio eliminado)

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

    return True


# ============================================
# MENÚS
# ============================================

def show_main_menu():
    print("""
╔══════════════════════════════════════════════════════════╗
║          INSTALADOR DE SKILLS — squad-skills            ║
╚══════════════════════════════════════════════════════════╝

¿Qué deseas instalar?

  [1] Skills — Seleccionar skills específicas
  [2] Agents — Seleccionar agentes específicos
  [3] Team Dev SAC — Skills SAC + Configuración
  [4] Todo — Skills + Agents + Team Dev SAC
  [Q] Salir
    """)


def show_skills_menu(skills):
    generic = [s for s in skills if not s["tools_required"] and not s["is_sac"]]
    git_required = [s for s in skills if "git" in s["tools_required"] and not s["is_sac"]]
    tools_required = [s for s in skills if s["tools_required"] and "git" not in s["tools_required"] and not s["is_sac"]]
    sac_skills = [s for s in skills if s["is_sac"]]

    idx = 1

    if generic:
        print(f"\n📦 GENÉRICAS (sin dependencias):")
        for s in generic:
            print(f"  [{idx}] {s['name']}")
            idx += 1

    if git_required:
        print(f"\n🔧 REQUIEREN GIT:")
        for s in git_required:
            print(f"  [{idx}] {s['name']}")
            idx += 1

    if tools_required:
        print(f"\n🛠️  REQUIEREN HERRAMIENTAS:")
        for s in tools_required:
            tools = [t for t in s["tools_required"] if t != "git"]
            print(f"  [{idx}] {s['name']} — {', '.join(tools)}")
            idx += 1

    if sac_skills:
        print(f"\n📋 TEAM DEV SAC (config + skills):")
        for s in sac_skills:
            print(f"  [{idx}] {s['name']} ⚡")
            idx += 1

    print(f"\n  [T] Instalar TODAS las skills")
    print(f"  [G] Instalar solo genéricas")
    print(f"  [S] Instalar solo Team Dev SAC")
    print(f"  [V] Volver")

    return idx


def show_agents_menu(agents):
    print(f"\n👤 AGENTES DISPONIBLES:")
    for i, agent in enumerate(agents, 1):
        print(f"  [A{i}] {agent['name']}")
    print(f"\n  [T] Instalar TODOS los agentes")
    print(f"  [V] Volver")


def show_requirements_preview(skill_info):
    print(f"\n{'═' * 60}")
    print(f" REQUISITOS — {skill_info['name']}")
    print(f"{'═' * 60}")
    print(f"\n  {skill_info['compatibility']}")

    if skill_info['tools_required']:
        print(f"\n  Herramientas detectadas:")
        for tool in skill_info['tools_required']:
            if tool in REQUIREMENTS_MAP:
                status = "✅" if check_tool(tool) else "❌"
                print(f"    {status} {tool}")
            elif tool == "azure_devops":
                print(f"    ⚠️  azure_devops — Requiere MCP server configurado")
            elif tool == "sac_config":
                print(f"    📦 sac_config — Se instala con Team Dev SAC")

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

    print_info("Escaneando skills y agentes...")
    skills = scan_skills(skills_dir)
    agents = scan_agents(agents_dir)
    print_success(f"Encontradas {len(skills)} skills y {len(agents)} agentes")

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
    sac_config_installed = False

    while True:
        show_main_menu()
        choice = input("  Selecciona una opción: ").strip().upper()

        if choice == "Q":
            break

        elif choice == "1":
            max_idx = show_skills_menu(skills)
            response = input("\n  Selecciona skills (números separados por espacio): ").strip().upper()

            if response == "Q":
                break
            elif response == "T":
                selected = skills
            elif response == "G":
                selected = [s for s in skills if not s["tools_required"] and not s["is_sac"]]
            elif response == "S":
                selected = [s for s in skills if s["is_sac"]]
            else:
                try:
                    indices = [int(x) for x in response.split()]
                    selected = [skills[i-1] for i in indices if i <= len(skills)]
                except (ValueError, IndexError):
                    print_error("Selección inválida")
                    continue

            if not selected:
                continue

            print(f"\n  Verificando requisitos...")
            for s in selected:
                show_requirements_preview(s)

            confirm = input("\n  ¿Continuar con la instalación? (s/N): ").strip().lower()
            if confirm != 's':
                continue

            print(f"\n  Instalando skills...")
            has_sac = any(s["is_sac"] for s in selected)

            if has_sac and not sac_config_installed:
                install_sac_config(project_path, root_dir)
                sac_config_installed = True

            for s in selected:
                if install_skill(s, project_path, skills_target):
                    installed_skills.append(s["name"])

        elif choice == "2":
            if not agents:
                print_warning("No se encontraron agentes")
                continue

            show_agents_menu(agents)
            response = input("  Selecciona agentes (A1 A2... o T): ").strip().upper()

            if response == "T":
                selected_agents = agents
            elif response == "V":
                continue
            else:
                try:
                    indices = [int(x.replace("A", "")) for x in response.split()]
                    selected_agents = [agents[i-1] for i in indices if i <= len(agents)]
                except (ValueError, IndexError):
                    print_error("Selección inválida")
                    continue

            print(f"\n  Instalando agentes...")
            for a in selected_agents:
                if install_agent(a, project_path):
                    installed_agents.append(a["name"])

        elif choice == "3":
            sac_skills_list = [s for s in skills if s["is_sac"]]

            print(f"\n╔══════════════════════════════════════════════════════════╗")
            print(f"║              TEAM DEV SAC — Skills + Config             ║")
            print(f"╚══════════════════════════════════════════════════════════╝")

            print(f"\nSkills SAC disponibles:")
            for i, s in enumerate(sac_skills_list, 1):
                print(f"  [{i}] {s['name']}")

            print(f"\n  [T] Instalar TODAS las skills SAC")

            response = input("\n  Selecciona: ").strip().upper()

            if response == "T":
                selected_sac = sac_skills_list
            else:
                try:
                    indices = [int(x) for x in response.split()]
                    selected_sac = [sac_skills_list[i-1] for i in indices if i <= len(sac_skills_list)]
                except (ValueError, IndexError):
                    continue

            if not selected_sac:
                continue

            if not sac_config_installed:
                print(f"\n  Instalando configuración Team Dev SAC...")
                install_sac_config(project_path, root_dir)
                sac_config_installed = True

            print(f"\n  Instalando skills SAC...")
            for s in selected_sac:
                if install_skill(s, project_path, skills_target):
                    installed_skills.append(s["name"])

        elif choice == "4":
            print(f"\n  Instalando todo...")

            if not sac_config_installed:
                install_sac_config(project_path, root_dir)
                sac_config_installed = True

            for s in skills:
                if install_skill(s, project_path, skills_target):
                    installed_skills.append(s["name"])

            for a in agents:
                if install_agent(a, project_path):
                    installed_agents.append(a["name"])

        else:
            print_error("Opción inválida")

    print_summary(project_path, installed_skills, installed_agents, sac_config_installed)
    return True


def ensure_repo_available():
    temp_repo_path = get_temp_repo_path()

    if temp_repo_path.exists() and (temp_repo_path / ".git").exists():
        print_info(f"Repositorio encontrado en {temp_repo_path}")
        try:
            subprocess.run(
                ["git", "-C", str(temp_repo_path), "pull", "--ff-only"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return temp_repo_path
        except Exception:
            pass

    print_info("Clonando repositorio...")
    try:
        if temp_repo_path.exists():
            shutil.rmtree(temp_repo_path)

        result = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", REPO_BRANCH, REPO_URL, str(temp_repo_path)],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print_success("Repositorio clonado")
            return temp_repo_path
        else:
            print_error(f"Error al clonar: {result.stderr}")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None


def print_summary(project_path, skills, agents, sac_installed):
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

    print("🚀 Cómo usar:")
    print("   1. Abre tu IDE (VS Code, Cursor, etc.)")
    print("   2. Activa las skills según la documentación")
    print("   3. Usa los agentes en tu chat de IA\n")


def print_help():
    print("""
📖 USO:
    python instalar.py [RUTA]           Instala en la ruta especificada
    python instalar.py                  Modo interactivo
    python instalar.py --help           Mostrar ayuda

📍 EJEMPLOS:
    python instalar.py "C:/mi-proyecto"
    python instalar.py "/home/usuario/mi-proyecto"
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
