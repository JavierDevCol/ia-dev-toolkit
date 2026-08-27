#!/bin/bash

# install-skill.sh — Instala skills desde el repositorio squad-skills
# Escanea recursivamente skills/ y subcarpetas.
# Detecta plataforma (.claude, .opencode, .agent) y crea symlinks.

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/skills"

# Array para almacenar rutas de skills encontradas
declare -a SKILL_PATHS=()
declare -a SKILL_NAMES=()
declare -a SKILL_REL_PATHS=()

# ─────────────────────────────────────────────────────────
# Funciones auxiliares
# ─────────────────────────────────────────────────────────

print_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║          INSTALADOR DE SKILLS — squad-skills        ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_platform() {
    local platform=$1
    local path=$2
    echo -e "${GREEN}✓ Plataforma detectada: ${BLUE}${platform}${NC}"
    echo -e "  Ruta: ${path}"
    echo ""
}

# Detectar plataforma
detect_platform() {
    local target_dir=""

    if [ -d "${SCRIPT_DIR}/.claude" ]; then
        target_dir="${SCRIPT_DIR}/.claude"
        platform="claude"
    elif [ -d "${SCRIPT_DIR}/.opencode" ]; then
        target_dir="${SCRIPT_DIR}/.opencode"
        platform="opencode"
    elif [ -d "${SCRIPT_DIR}/.agent" ]; then
        target_dir="${SCRIPT_DIR}/.agent"
        platform="agent"
    else
        target_dir="${SCRIPT_DIR}/.agent"
        platform="agent"
        mkdir -p "${target_dir}"
        echo -e "${YELLOW}⚠ No se encontró .claude/, .opencode/ ni .agent/${NC}"
        echo -e "${GREEN}✓ Creando directorio: ${target_dir}${NC}"
    fi

    skills_target="${target_dir}/skills"
    mkdir -p "${skills_target}"

    print_platform "${platform}" "${target_dir}"
}

# Escanear skills recursivamente
scan_skills() {
    SKILL_PATHS=()
    SKILL_NAMES=()
    SKILL_REL_PATHS=()

    while IFS= read -r skill_file; do
        local skill_dir="$(dirname "${skill_file}")"
        local rel_path="${skill_dir#${SKILLS_DIR}/}"
        local skill_name="$(basename "${skill_dir}")"

        # Evitar duplicados (mismo nombre en diferentes rutas)
        local already_exists=false
        for existing in "${SKILL_NAMES[@]}"; do
            if [ "${existing}" = "${skill_name}" ]; then
                already_exists=true
                break
            fi
        done

        if [ "${already_exists}" = false ]; then
            SKILL_PATHS+=("${skill_dir}")
            SKILL_NAMES+=("${skill_name}")
            SKILL_REL_PATHS+=("${rel_path}")
        fi
    done < <(find "${SKILLS_DIR}" -name "SKILL.md" -type f | sort)
}

# Listar skills disponibles
list_skills() {
    echo -e "${CYAN}Skills disponibles:${NC}"
    echo ""

    local i=1
    for rel_path in "${SKILL_REL_PATHS[@]}"; do
        local name="${SKILL_NAMES[$((i-1))]}"
        local parent="$(dirname "${rel_path}")"

        if [ "${parent}" = "." ]; then
            echo -e "  ${GREEN}[$i]${NC} ${BLUE}${name}${NC}"
        else
            echo -e "  ${GREEN}[$i]${NC} ${BLUE}${name}${NC} ${DIM}(${parent})${NC}"
        fi
        ((i++))
    done

    total_skills=${#SKILL_NAMES[@]}
    echo ""
    echo -e "  ${YELLOW}[T]${NC} Instalar TODAS las skills"
    echo -e "  ${RED}[Q]${NC} Salir"
    echo ""
}

# Instalar skill
install_skill() {
    local skill_index=$1
    local skill_src="${SKILL_PATHS[$((skill_index-1))]}"
    local skill_name="${SKILL_NAMES[$((skill_index-1))]}"
    local skill_dst="${skills_target}/${skill_name}"

    if [ ! -f "${skill_src}/SKILL.md" ]; then
        echo -e "${RED}✗ Skill '${skill_name}' no encontrada en ${skill_src}${NC}"
        return 1
    fi

    if [ -L "${skill_dst}" ] || [ -d "${skill_dst}" ]; then
        echo -e "${YELLOW}⚠ '${skill_name}' ya instalada — sobrescribiendo${NC}"
        rm -rf "${skill_dst}"
    fi

    ln -s "${skill_src}" "${skill_dst}"
    echo -e "${GREEN}✓ ${skill_name}${NC}"
}

# ─────────────────────────────────────────────────────────
# Flujo principal
# ─────────────────────────────────────────────────────────

print_header

if [ ! -d "${SKILLS_DIR}" ]; then
    echo -e "${RED}✗ No se encontró el directorio skills/ en ${SCRIPT_DIR}${NC}"
    exit 1
fi

detect_platform
scan_skills
list_skills

echo -e "${CYAN}Ingresa los números de las skills a instalar (separados por espacio):${NC}"
read -p "> " selections

if [ "$(echo "${selections}" | tr '[:lower:]' '[:upper:]')" = "Q" ]; then
    echo -e "${YELLOW}Cancelado.${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}Instalando skills...${NC}"
echo ""

if [ "$(echo "${selections}" | tr '[:lower:]' '[:upper:]')" = "T" ]; then
    for i in "${!SKILL_PATHS[@]}"; do
        install_skill $((i+1))
    done
else
    for num in ${selections}; do
        if [[ "${num}" =~ ^[0-9]+$ ]] && [ "${num}" -ge 1 ] && [ "${num}" -le "${total_skills}" ]; then
            install_skill "${num}"
        else
            echo -e "${RED}✗ Opción inválida: ${num}${NC}"
        fi
    done
fi

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║               INSTALACIÓN COMPLETA                  ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Plataforma: ${BLUE}${platform}${NC}"
echo -e "Ruta:       ${BLUE}${skills_target}${NC}"
echo ""
echo -e "Skills instaladas:"
ls -1 "${skills_target}" 2>/dev/null | while read -r skill; do
    echo -e "  ${GREEN}→${NC} ${skill}"
done
echo ""
