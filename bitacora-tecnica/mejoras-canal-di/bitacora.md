# Sesión: Mejoras canal DIAT — acoplamiento CLI↔ref

- **ID:** 2026-10-13-mejoras-canal-di
- **Fecha inicio:** 2026-10-13 23:08
- **Última actualización:** 2026-10-13 23:08
- **Estado:** En progreso
- **Rama de Trabajo:** `feature/mejoras-plugin-workflow-sac` (base `develop@cd77930`)
- **Tags:** `diat`, `canal-di`, `diat_ref`, `auditoria`, `cli-ref-coupling`
- **Ambiente:** Local

## Tiempo
- **Invertido:** ~2h (limpieza de ramas + integración a develop + auditoría delegada)
- **Estimado restante:** Oleada 1 ~3-4h · Oleadas 2-3 pendientes de estimar
- **Deadline:** —

## Objetivo de la Sesión
Proceso estructurado de mejoras al canal de prueba de DIAT (CLI instalador): eliminar los puntos de acoplamiento entre el **CLI local** (grafo de deps, layout, skills SAC, migraciones hardcodeados) y la **ref descargada** (`DIAT_REF`), que producen instalaciones mixtas, registros envenenados y falsos "desactualizado". Trabajo por oleadas con validación manual en HOME aislado por cada fix.

## Lo Realizado
- **Commits:**
  - `5763ad8` — chore: start workflow-sac plugin improvements (rama creada desde `develop@cd77930`)
- **Cambios en Código:**
  - Ninguno aún (fase de auditoría)
- **Decisiones Técnicas:**
  - Auditoría delegada a **2 subagentes** (protocolo orquestador): uno cubrió `diat`+`deps.py`+`instalar.py`, otro `update.py`+`registro.py`+`paths.py`+`github.py`+bootstraps → **34 hallazgos únicos deduplicados** (7 críticos, ~15 medium, ~12 low).
  - **Patrón raíz (convergencia de ambas auditorías):** 4 piezas de estado de canal sin fuente única de verdad (env `DIAT_REF` · `.ref` del caché · `inst["ref"]` por proyecto · contenido real de bin/caché) + el CLI local lleva hardcoded grafo/layout/skills que la ref puede contradecir.
  - **Plan por oleadas:**
    - **O1 — coherencia de canal:** los 7 críticos C1–C7 (tabla en "Estado Actual")
    - **O2 — integridad del caché + persistencia del canal:** purgado al cambiar de ref · sonda de validez · tarball anclado al sha · `--channel` persistente · bootstrap escribe `.ref` · skip "al día" considera ref · seeds sin trazabilidad · DownloadError capturado · `--version` por canal
    - **O3 — UX/robustez:** mensaje de deps con `DIAT_REF` · validación de formato de ref · 403≠offline · "0 componentes" como éxito · config/assets viejos · `LEGACY_REPLACED` en ref · `is_test_channel` único
  - Validación por fix: HOME aislado + `DIAT_REF` (procedimiento ya probado en la fase de canal de prueba).

## Evidencias
- **Descripción:** {file:./EVIDENCIAS/auditoria-cli-ref-deps.md} — Auditoría 1: `diat` + `deps.py` + `instalar.py` (C-01…C-04, M-01…M-12, B-01…B-08)
- **Descripción:** {file:./EVIDENCIAS/auditoria-ref-propagacion.md} — Auditoría 2: `update.py`+`registro.py`+`paths.py`+`github.py`+bootstraps (C-1…C-5, M-1…M-10, B-1…B-7)

## Estado Actual
Auditoría completada y registrada. Rama `feature/mejoras-plugin-workflow-sac` limpia en `5763ad8`. **Esperando decisión del usuario sobre el alcance de la Oleada 1.**

### Hallazgos críticos (Oleada 1)

| # | Hallazgo | Fichero |
|---|---|---|
| C1 | Validación grafo LOCAL vs catálogo de la REF aborta instalación completa *(el known)* | `deps.py:75-85` |
| C2 | Ref nueva declara deps que el CLI local no conoce → instalación rota en silencio | `deps.py:91-125` |
| C3 | Offline/rate-limit: registra ref del env con contenido/sha de OTRA ref | `diat:55-67,186` |
| C4 | `--update` en lote reetiqueta TODOS los proyectos con la ref del env | `update.py:97-104` |
| C5 | `--status`/`--list` comparan contra ref del ENV, no la del proyecto | `diat:261,292` |
| C6 | `.version` se escribe ANTES de validar/descargar | `update.py:54-56` |
| C7 | Auto-update en caliente: valida con módulos viejos tras sobrescribir `bin/` | `diat:59` |

### Pendientes
- [ ] **Decidir alcance O1** → opción [O1] completa (C1–C7) · [O1-s] subconjunto (C1–C4) · [IDs] a medida
- [ ] Decidir renombrar rama → `feature/mejoras-canal-di` (el trabajo es de INSTALACION/, no del plugin)
- [ ] C1: `validate_dependencies` → validar solo subgrafo de las seeds + warning no-aborto + mensaje con ref activa
- [ ] C2: manifiesto de deps versionado en la ref (`components.manifest.json`) con fallback al grafo local
- [ ] C3: sin verificación remota → abortar o registrar la ref real del caché (nunca la del env)
- [ ] C4: `--update` en lote respeta `inst["ref"]` persistida; migrar de canal solo con confirmación
- [ ] C5: `remote_sha = get_remote_sha(ref=inst.get("ref", DEFAULT_REF))` en status y list
- [ ] C6: mover `save_installed_version` tras descarga/validación exitosas + try/except en descarga
- [ ] C7: relanzar CLI tras staging (`os.execv`) o advertir "CLI actualizado: re-ejecuta"
- [ ] Commit por fix (conventional commits, preview antes de push)
- [ ] Oleadas 2 y 3 (detalle completo en EVIDENCIAS)

### Bloqueantes
- Ninguno.

### Tests
- [ ] Unitarios: N/A — el CLI no tiene suite; validación manual por fix en HOME aislado
- [ ] Integración: Pendiente — instalación `DIAT_REF=v0.18.1-test` en HOME aislado tras cada fix
- [ ] E2E: Pendiente — proyecto de prueba con `--install` + `--status` + `--update` + `--list`

### Rollback Plan
Si algo sale mal, ejecutar:
1. `git checkout develop` (la rama no está mergeada — nada afecta a develop/main)
2. Por fix individual: `git reset --hard <último commit verde de la rama>`
3. Abortar todo: `git branch -D feature/mejoras-plugin-workflow-sac`

## Próxima Sesión
1. Confirmar alcance de la Oleada 1 (y renombre de rama)
2. Implementar C1 (el known, mayor impacto inmediato) → validar en HOME aislado
3. Seguir con C5 y C6 (los más aislados entre sí), luego C3, C4, C7, C2
4. Actualizar esta bitácora tras cada fix (checkpoint [C])
