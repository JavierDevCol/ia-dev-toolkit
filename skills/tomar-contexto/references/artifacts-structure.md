# Estructura de Artifacts (tomar-contexto)

Usar las rutas cargadas de `CONFIG_SYSTEM` / `CONFIG_USER`:

```
{artifacts_folder}/
├── HU/
│   └── [ID-HU]/
│       ├── HU.md              (desde skills/refinar-hu/assets/HU.md)
│       ├── Refinamiento.md    (desde skills/refinar-hu/assets/Refinamiento.md)
│       ├── RefinamientoBug.md (solo bugs, desde skills/registrar-hallazgo/assets/RefinamientoBug.md)
│       ├── Plan.md            (desde skills/planificar-hu/assets/Plan.md)
│       └── Tracking.md        (desde skills/ejecutar-plan/assets/Tracking.md)
├── {adr_folder relative}/
├── {code_smells_folder relative}/
├── {contextos_folder relative}/
├── {deuda_tecnica_folder relative}/
├── {pendientes_folder relative}/
├── backlog_desarrollo.md      (desde assets/backlog_desarrollo_plantilla.md)
├── lecciones_aprendidas.md    (desde assets/lecciones_aprendidas_plantilla.md)
├── pendientes.md              (desde assets/pendientes_plantilla.md)
└── workspace.md               (desde assets/workspace_plantilla.md)
```

## Crear carpetas del sistema
- Crear `{artifacts_folder}/` y subcarpetas: `HU/`, `ADR/`, `code_smells/`, `{contextos_folder}/`, `deuda_tecnica/`, `pendientes/`.
- Crear `.SAC/config/` si no existe.

## Generar archivos de contexto
- **Mono-Proyecto:** `{contextos_folder}/contexto_proyecto.md` (desde `{file:./assets/contexto_proyecto_plantilla.md}`) + `{archivos.workspace}` (Tipo: Mono-Proyecto).
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
