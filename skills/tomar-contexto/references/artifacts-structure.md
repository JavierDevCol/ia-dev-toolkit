# Estructura de Artifacts (tomar-contexto)

Usar las rutas cargadas de `CONFIG_SYSTEM` / `CONFIG_USER`:

```
{artifacts_folder}/
├── HU/
│   └── [ID-HU]/
│       ├── HU.md              (desde plantillas.hu.hu)
│       ├── Refinamiento.md    (desde plantillas.hu.refinamiento)
│       ├── RefinamientoBug.md (solo bugs, desde plantillas.hu.refinamiento_bug)
│       ├── Plan.md            (desde plantillas.hu.plan)
│       └── Tracking.md        (desde plantillas.hu.tracking)
├── {adr_folder relative}/
├── {code_smells_folder relative}/
├── {contextos_folder relative}/
├── {deuda_tecnica_folder relative}/
├── {pendientes_folder relative}/
├── backlog_desarrollo.md      (desde plantillas.backlog)
├── lecciones_aprendidas.md    (desde plantillas.lecciones_aprendidas)
├── pendientes.md              (desde plantillas.pendientes)
└── workspace.md               (desde plantillas.workspace)
```

## Crear carpetas del sistema
- Crear `{artifacts_folder}/` y subcarpetas: `HU/`, `ADR/`, `code_smells/`, `{contextos_folder}/`, `deuda_tecnica/`, `pendientes/`.
- Crear `.SAC/config/`, `.SAC/plantillas/`, `.SAC/reglas/` si no existen.

## Generar archivos de contexto
- **Mono-Proyecto:** `{contextos_folder}/contexto_proyecto.md` (desde `{plantillas.contexto}`) + `{archivos.workspace}` (Tipo: Mono-Proyecto).
- **Multi-Proyecto:** por cada proyecto `{contextos_folder}/contexto_proyecto_{nombre}.md`, documentando relaciones en "Dependencias de Proyecto"; `{archivos.workspace}` con Tipo: Multi-Proyecto.

## Formato de salida
**Mono-Proyecto:**
```
✅ WORKSPACE CONFIGURADO (Mono-Proyecto)
📁 .SAC/workspace.md
📁 .SAC/artifacts/contextos/contexto_proyecto.md
📊 Scorecard: Arq X/10 | Stack X/10 | Test X/10 | DevOps X/10 | Docs X/10
```

**Multi-Proyecto:**
```
✅ WORKSPACE CONFIGURADO (Multi-Proyecto)
📁 .SAC/workspace.md
📁 .SAC/artifacts/contextos/ (N contextos generados)
📊 Scorecard Global: X/10
```
