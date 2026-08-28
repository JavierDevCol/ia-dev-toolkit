# Sesión: Instalador Modular — ia-dev-toolkit
- **ID:** 2026-08-27-instalador-modular
- **Fecha inicio:** 2026-08-27 17:30
- **Última actualización:** 2026-08-28 01:00
- **Estado:** En progreso
- **Rama de Trabajo:** `main`
- **Tags:** `instalador`, `modular`, `workflows`, `tools`, `checkboxes`, `diat`, `cli`
- **Ambiente:** Local

## Tiempo
- **Invertido:** 3h
- **Estimado restante:** 1h
- **Deadline:** N/A

## Objetivo de la Sesión
Rediseñar el instalador de ia-dev-toolkit para permitir instalación modular de componentes individuales: skills, agentes, workflows, tools y configuración. Crear CLI `diat` con comandos completos.

## Lo Realizado
- **Commits:**
  - `425e709` — feat: e2e tests expansion + workspace fixtures
  - `7c5c14e` — feat(installer): modular installation with checkboxes
  - `8d5cce3` — feat(installer): autocompletado interactivo de CONFIG_USER.yaml
  - `7e004f7` — feat(installer): descarga selectiva desde GitHub API
  - `ff0bb10` — refactor: rename squad-skills → ia-dev-toolkit
  - `20f39cb` — feat: CLI diat con comandos --help, --list, --version, --update, --check, --status
  - `e8aa488` — docs: plan bootstrap diat
  - `eb1c236` — docs: plan bootstrap diat sin clon de repo
  - `445df17` — docs: plan bootstrap diat corregido
  - `f320cf1` — docs: plan bootstrap diat - comportamiento corregido
  - `8841255` — feat(installer): opción alma + cambio orden plataformas
  - `3677376` — refactor: rename AGENTS.md → ALMA.md
  - `e084732` — refactor(installer): actualizar referencias AGENTS.md → ALMA.md
  - `fc91f21` — chore: limpiar .gitignore
  - `b0adb64` — docs: actualizar README.md con opciones actuales
  - `86902a6` — feat(bootstrap): migrar a diat sin clon de repo
  - `ae91245` — feat: comando --uninstall para desinstalar diat
  - `45e2259` — fix(diat): descargar instalar.py bajo demanda
  - `053620d` — fix: descargar ALMA.md en cache + comandos --install y --alma

- **Cambios en Código:**
  - `INSTALACION/instalar.py` — Reescrito con menú de 7 opciones, checkboxes, autocompletado config
  - `INSTALACION/diat` — CLI principal con 10 comandos
  - `INSTALACION/diat.bat` — Wrapper Windows
  - `INSTALACION/bootstrap/install.sh` — Descarga directa diat (sin clon)
  - `INSTALACION/bootstrap/install.ps1` — Descarga directa diat (sin clon)
  - `INSTALACION/bootstrap/uninstall.sh` — Desinstalador Linux/Mac
  - `INSTALACION/bootstrap/uninstall.ps1` — Desinstalador Windows
  - `ALMA.md` — Personalidad del agente (renombrado de AGENTS.md)
  - `docs/plans/bootstrap-diat-plan.md` — Plan de implementación

- **Decisiones Técnicas:**
  - CLI `diat` como comando principal (acrónimo de IA Dev Toolkit)
  - Descarga selectiva desde GitHub API (~322KB vs ~2-3MB del repo)
  - Cache en `~/.local/share/ia-dev-toolkit/repo/`
  - `instalar.py` se descarga bajo demanda con `ensure_instalar()`
  - Orden prioridad plataformas: `.claude` → `.opencode` → `.agent`
  - Default si no existe: crea `.agent/`
  - Opción Alma copia `ALMA.md` al archivo de personalidad según plataforma

## Estado Actual
CLI `diat` funcional con todos los comandos. Bootstrap descarga solo `diat` (~10KB). Cache descarga componentes selectivos (~322KB). Menú interactivo con curses nativo. Flag `ready` para filtrar componentes. Skill auto-versioning con análisis de diffs.

### Pendientes
- [x] **Menú interactivo con flechas y espacio** — Implementado con curses nativo (interactive_menu.py)
- [x] Evaluar librerías: `inquirer`, `pick`, `simple-term-menu`, `blessed` — Se usó curses nativo (sin dependencias)
- [x] Skills ADO archived muestran "Sin descripción" — Agregadas descripciones
- [x] Flag `--non-interactive` para instalación automatizada — Implementado
- [x] **Flag `ready: true/false`** — Filtra componentes en instalador (default: false = oculto)
- [x] **Versionado con Git Tags** — `diat --version` obtiene versión desde GitHub API
- [x] **Auto-versioning skill** — `diat --analyze-version` analiza diffs y sugiere versión

### Bloqueantes
- Ninguno

### Tests
- [ ] Unitarios: Pendiente
- [ ] Integración: Pendiente
- [x] E2E: OK (prueba manual)

### Rollback Plan
Si algo sale mal, ejecutar:
1. `git checkout main`
2. `git branch -D feat/installer-modular`

## Análisis: Menú Interactivo

### Problema Actual
El menú de selección requiere escribir números:
```
Selección: 5
Seleccionados: transversales-workitems
¿Confirmar selección? (s/N):
```

### Solución Implementada
Menú interactivo con navegación por teclado usando curses nativo:
- Flechas ↑↓ para navegar
- Espacio para marcar/desmarcar
- Enter para confirmar selección
- Fallback a modo texto si curses falla

### Implementación
```python
# interactive_menu.py - Menú con curses nativo (sin dependencias)
from interactive_menu import show_interactive_menu

def show_checkbox_menu(items, item_type):
    options = [{"name": item["name"], "description": item["description"]} for item in items]
    selected = show_interactive_menu(options, f"📦 {item_type}")
    return selected
```
        options,
        title=f"{item_type} DISPONIBLES",
        multi_select=True,
        show_multi_select_hint=True
    )
    selected_indices = terminal_menu.show()
    return [items[i] for i in selected_indices]
```

## Próxima Sesión
1. Implementar menú interactivo con flechas y espacio
2. Evaluar `simple-term-menu` o `inquirer` para menús interactivos
3. Agregar descripciones a skills ADO archived
4. Considerar flag `--non-interactive` para CI/CD
