# Sesión: Instalador Modular — squad-skills
- **ID:** 2026-08-27-instalador-modular
- **Fecha inicio:** 2026-08-27 17:30
- **Última actualización:** 2026-08-27 18:00
- **Estado:** Completado
- **Rama de Trabajo:** `feat/installer-modular`
- **Tags:** `instalador`, `modular`, `workflows`, `tools`, `checkboxes`
- **Ambiente:** Local

## Tiempo
- **Invertido:** 0.5h
- **Estimado restante:** 0h
- **Deadline:** N/A

## Objetivo de la Sesión
Rediseñar el instalador de squad-skills para permitir instalación modular de componentes individuales: skills, agentes, workflows, tools y configuración. Agregar selección interactiva con checkboxes `[x]`/`[ ]` que muestren descripción y dependencias de cada componente.

## Lo Realizado
- **Commits:**
  - `425e709` — feat: e2e tests expansion + workspace fixtures + opencode config updates (previo)
  - `7c5c14e` — feat(installer): modular installation with checkboxes, workflows, tools and kit completo
- **Cambios en Código:**
  - `INSTALACION/instalar.py` — Reescrito completamente con menú de 6 opciones y selección interactiva por checkboxes
  - `INSTALACION/README.md` — Actualizado con nuevas opciones de instalación y formato de checkboxes
- **Decisiones Técnicas:**
  - Usar `show_checkbox_menu()` como función genérica reutilizable para todos los tipos de componentes → Reduce duplicación y mantiene consistencia visual
  - Workflows instalan automáticamente sus tools requeridos → Evita que el usuario olvide dependencias
  - Skills instaladas como symlinks, agentes/workflows/tools como copias → Skills se actualizan con el repo, el resto es independiente

## Estado Actual
Instalador funcional en rama `feat/installer-modular`. Prueba exitosa en `/tmp/test-installer` con Kit Completo:
- 41 skills (symlinks)
- 4 agentes (copias)
- 3 workflows (copias con fases/ y plantillas/)
- 2 tools (copias)
- Config `.SAC/` con rutas actualizadas

### Pendientes
- [ ] Crear PR a main
- [ ] Revisar si hay skills ADO archived que no deberían instalarse por defecto

### Bloqueantes
- Ninguno

### Tests
- [ ] Unitarios: Pendiente
- [ ] Integración: Pendiente
- [x] E2E: OK (prueba manual en /tmp)

### Rollback Plan
Si algo sale mal, ejecutar:
1. `git checkout main`
2. `git branch -D feat/installer-modular`

## Próxima Sesión
1. Crear PR de `feat/installer-modular` a `main`
2. Evaluar si las skills archived de ADO deben excluirse por defecto del escaneo
3. Considerar agregar flag `--non-interactive` para instalación automatizada
