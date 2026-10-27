# Convenciones de configuración — handoff-release

## Carga de configuración

Leer la sección `handoff-release` de `.SAC/config/sac.json` con memctl (solo lectura; su salida ES la respuesta; si falla, leer el archivo con `jq`; nunca inventar valores):

```sh
sh .SAC/memctl.sh get handoff-release.config.environments.dev      # .staging / .prod
sh .SAC/memctl.sh get handoff-release.config.roles.preparer        # .deployer
sh .SAC/memctl.sh get handoff-release.config.branch_format
sh .SAC/memctl.sh get handoff-release.config.tag_format
sh .SAC/memctl.sh get output_folder
```

Si un campo es `null` o memctl sale con exit 2, usar los defaults indicados. Si `.SAC/config/sac.json` no existe, la instalación SAC está incompleta: indicar al usuario que ejecute `diat`; no crear el archivo a mano.

**Ruta de artefactos:** usar `output_folder` global. Si es `null`, preguntar al usuario la carpeta donde guardar artefactos de releases y persistirla en `output_folder` de `.SAC/config/sac.json` (editando solo esa clave).

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

## Editar configuración

1. Mostrar configuración actual (ambientes, responsables, formatos).
2. Preguntar qué cambiar: [E] Ambientes / [R] Responsables / [F] Formatos / [G] Guardar / [C] Cancelar.
3. Guardar cambios en `.SAC/config/sac.json` → sección `handoff-release.config` (editando solo esa sección).
