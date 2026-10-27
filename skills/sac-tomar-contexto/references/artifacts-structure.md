# Estructura de Artifacts (sac-tomar-contexto)

Usar las rutas cargadas con memctl desde `.SAC/config/sac.json` (`documentacion_sac_path`, `artifacts.*`, `archivos.*`):

```
{documentacion_sac_path}/
├── HU/
│   └── [ID-HU]/
│       ├── HU.md              (desde skills/sac-refinar-hu/assets/HU.md)
│       ├── Refinamiento.md    (desde skills/sac-refinar-hu/assets/Refinamiento.md)
│       ├── RefinamientoBug.md (solo bugs, desde skills/registrar-hallazgo/assets/RefinamientoBug.md)
│       ├── Plan.md            (desde skills/sac-planificar-hu/assets/Plan.md)
│       └── Tracking.md        (desde skills/sac-ejecutar-plan/assets/Tracking.md)
├── {adr_folder relative}/
├── {code_smells_folder relative}/
├── {contextos_folder relative}/
├── {deuda_tecnica_folder relative}/
├── {pendientes_folder relative}/
├── backlog_desarrollo.md      (desde assets/backlog_desarrollo_plantilla.md)
├── lecciones_aprendidas.md    (`{lecciones_aprendidas}`, desde assets/lecciones_aprendidas_plantilla.md)
├── pendientes.md              (desde assets/pendientes_plantilla.md)
└── workspace.md               (desde assets/workspace_plantilla.md)
```

## Crear carpetas del sistema
- Crear `{documentacion_sac_path}/` y subcarpetas desde las rutas de memctl: `{hu_folder}`, `{adr_folder}`, `{code_smells_folder}`, `{contextos_folder}`, `{deuda_tecnica_folder}`, `{pendientes_folder}`.
- No crear `.SAC/config/` ni `sac.json`: los instala `diat`. Si falta → avisar "No hay instalación SAC".

## Generar archivos de contexto
- **Mono-Proyecto:** `{contextos_folder}/contexto_proyecto.md` (desde `{file:./assets/contexto_proyecto_plantilla.md}`) + `{workspace}` (Tipo: Mono-Proyecto).
- **Multi-Proyecto:** por cada proyecto `{contextos_folder}/` + `{patron_contexto}` (`multi_proyecto.patron_contexto`, p. ej. `contexto_proyecto_{nombre}.md`), documentando relaciones en "Dependencias de Proyecto"; `{workspace}` con Tipo: Multi-Proyecto.

## Formato de salida
**Mono-Proyecto:**
```
✅ WORKSPACE CONFIGURADO (Mono-Proyecto)
📁 {workspace}
📁 {contextos_folder}/contexto_proyecto.md
📊 Scorecard: Arq X/10 | Stack X/10 | Test X/10 | DevOps X/10 | Docs X/10
```

**Multi-Proyecto:**
```
✅ WORKSPACE CONFIGURADO (Multi-Proyecto)
📁 {workspace}
📁 {contextos_folder}/ (N contextos generados)
📊 Scorecard Global: X/10
```
