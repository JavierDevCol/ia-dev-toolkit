# Sesión: Revisión install-skill.sh
- **ID:** 2026-08-27-revisar-install-skill
- **Fecha inicio:** 2026-08-27
- **Última actualización:** 2026-08-27
- **Estado:** En progreso
- **Rama de Trabajo:** `main`
- **Tags:** `instalador`, `skills`
- **Ambiente:** Local

## Tiempo
- **Invertido:** 0.5h
- **Estimado restante:** 1h
- **Deadline:** —

## Objetivo de la Sesión
Revisar `install-skill.sh` (desactualizado desde `dd130d7`) contra la estructura actual de `skills/`.

## Lo Realizado
- **Revisión raíz:** script instala skills vía symlink (`ln -s`) escaneando `SKILL.md` recursivo en `skills/`.
- **Hallazgos (4):**
  1. **No excluye `_archived/`** → instalaría las 5 skills obsoletas de `skills/ado/_archived/`.
  2. **No instala assets raíz compartidos** (`skills/memory_skill.json`, `skills/references/`) → `git-doc-sync`, `pr-config-audit` y skills ADO referencian `../memory_skill.json` (ruta relativa) y se rompen al instalar el skill aislado.
  3. **No limpia symlinks obsoletos** en el destino → skills eliminadas/archivadas quedan colgando en `.opencode/skills/`.
  4. **Destino solo nivel proyecto** (`.opencode/skills`, gitignored) → sin opción de instalar a nivel usuario (`~/.config/opencode/skills/`).
- **Decisión (2026-08-27):** el **instalador oficial** es `INSTALACION/instalar.py` (bootstrap global vía `curl`/`irm`, comando `skills`, GitHub `JavierDevCol/squad-skills` main). El `install-skill.sh` de raíz se declaró **legacy** y se **eliminó** del repo.
- **Dictamen plantillas (2026-08-27):** mantener `config/plantillas/` pero depurar. Se archiaron las **3 ADR** (`adr_madr`, `adr_nygard`, `adr_y_statement`) en `config/_archived_plantillas/` (conservan capacidad de ADR, no se instalan) y se **eliminaron 6 huérfanas** (0 refs en skills/agentes/workflows): `agente_plantilla`, `herramienta_plantilla`, `bug_plantilla`, `pendiente_detalle`, `plan_implementacion` (ref rota a `hu_refinamientos`), `refinamiento_hu` (duplicaba `hu.refinamiento`).
- **CONFIG_SYSTEM.yaml v7.25.0 → depurado:** se quitaron las claves `plantillas.plan_implementacion`, `plantillas.refinamiento_hu`, `plantillas.bug`, `plantillas.pendiente_detalle`. Quedan 11 plantillas activas.
- **Verificación kit-sac:** `install_sac_config()` instala 11 plantillas, sustituye `{project-root}`, sin `_archived` ni ADR en `.SAC/` (test con `python3 INSTALACION/instalar.py /tmp/sac-test`).
- **Nueva skill `crear-adr` (2026-08-27):** skill standalone que genera ADRs usando plantillas MARD/Nygard/Y-Statement. Ubicación desde `memory_skill.json` (`[crear-adr].memory.output_folder`), sin dependencia de `.SAC`. Numeración auto-incrementada (NNNN), campos obligatorios: Estado, Decisores, Fecha, Consecuencias, Validación. Plantillas movidas de `config/_archived_plantillas/` → `skills/crear-adr/assets/`. Verificación GREEN pasada (TDD writing-skills).
- **Nueva skill `crear-adr` (2026-08-27):** skill standalone que genera ADRs usando plantillas MARD/Nygard/Y-Statement. Ubicación desde `memory_skill.json` (`[crear-adr].memory.output_folder`), sin dependencia de `.SAC`. Numeración auto-incrementada (NNNN), campos obligatorios: Estado, Decisores, Fecha, Consecuencias, Validación. Plantillas movidas de `config/_archived_plantillas/` → `skills/crear-adr/assets/`. Verificación GREEN pasada (TDD writing-skills).
- **Nueva skill `crear-adr` (2026-08-27):** skill standalone que genera ADRs usando plantillas MARD/Nygard/Y-Statement. Ubicación desde `memory_skill.json` (`[crear-adr].memory.output_folder`), sin dependencia de `.SAC`. Numeración auto-incrementada (NNNN), campos obligatorios: Estado, Decisores, Fecha, Consecuencias, Validación. Plantillas movidas de `config/_archived_plantillas/` → `skills/crear-adr/assets/`. Verificación GREEN pasada (TDD writing-skills).
- **Comparativa raíz vs `INSTALACION/`:** `instalar.py` comparte los bugs 1-3 (usa `rglob("SKILL.md")` sin excluir `_archived`; symlinkea solo el skill sin assets raíz; no limpia obsoletos). Diferencia mayor: no categoriza "REQUIEREN GIT/HERRAMIENTAS" — metadata `compatibility:` solo existe en 4 skills archivadas → activas caen en GENÉRICAS/SAC.

## Evidencias
- **Respaldo del script eliminado:** `{file:./EVIDENCIAS/install-skill.sh}`
- **Instalador oficial:** `{file:./../../INSTALACION/instalar.py}`
- **README instalador:** `{file:./../../INSTALACION/README.md}`

## Estado Actual
Se determinó que el instalador oficial es `INSTALACION/instalar.py`. El `install-skill.sh` de raíz fue respaldado en `EVIDENCIAS/` y eliminado del repo (`git rm`, sin commit). Los fixes pendientes se trasladan al instalador oficial.

### Pendientes
- [x] Eliminar `install-skill.sh` de la raíz (respaldo en EVIDENCIAS/)
- [x] Depurar `config/plantillas/` (11 activas) + `CONFIG_SYSTEM.yaml` limpio
- [ ] Aplicar fix 1+2+3 a `INSTALACION/instalar.py` (excluir `_archived`, copiar assets raíz, limpiar obsoletos)
- [ ] Actualizar `INSTALACION/README.md` (cuenta de plantillas/plantillas SAC desactualizada)
- [ ] Opcional: fix 4 (instalar a `~/.config/opencode/skills/`)
- [ ] Definir metadata `compatibility:` para skills activas (categorización REAL en menú)
- [ ] Revisar campos muertos de `CONFIG_SYSTEM` (multi_proyecto, herramientas/agentes_folder, reglas_folder)

### Bloqueantes
—

### Tests
- [ ] Unitarios: No aplica (revisión documental)
- [ ] Integración: No aplica
- [ ] E2E: No aplica

## Próxima Sesión
1. Aplicar fix 1+2+3 a `instalar.py`
2. Probar instalación en `.opencode/skills/`
3. Verificar que `memory_skill.json` queda accesible para skills instaladas