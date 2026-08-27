# Convenciones de configuración — handoff-release

## Carga de configuración

Buscar `memory_skill.json` con `glob **/memory_skill.json`. Si no existe, crear en `skills/memory_skill.json` (al mismo nivel que las carpetas de skills). Leer sección `[handoff-release]` del archivo. Si campos son `null`, usar los defaults indicados.

## Configuración (`config`)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `environments.dev` | `DEV` | Nombre ambiente desarrollo |
| `environments.staging` | `STAGING` | Nombre ambiente staging |
| `environments.prod` | `PROD` | Nombre ambiente producción |
| `roles.preparer` | `Equipo Dev` | Quién prepara releases |
| `roles.deployer` | `Equipo Ops` | Quién despliega |
| `branch_format` | `release/vX.Y.Z` | Formato ramas release |
| `tag_format` | `vX.Y.Z-{env}` | Formato tags |
| `output_path` | `null` | Ruta base para artefactos |

## Memoria (`memory`)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `last_release` | `null` | Última versión release |
| `output_base_path` | `null` | Ruta base para guardar artefactos |

## Editar configuración

1. Mostrar configuración actual (ambientes, responsables, formatos).
2. Preguntar qué cambiar: [E] Ambientes / [R] Responsables / [F] Formatos / [G] Guardar / [C] Cancelar.
3. Guardar cambios en `memory_skill.json` → sección `[handoff-release].config`.
