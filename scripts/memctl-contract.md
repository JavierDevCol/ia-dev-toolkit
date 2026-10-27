# Contrato `memctl` — acceso transversal a la configuración SAC

Bloque para incluir en SKILL.md / instrucciones de agente. Garantiza el mismo
comportamiento en OpenCode, Claude Code, Codex o cualquier harness.

## Regla de uso

> **Antes de consultar configuración, intenta `memctl`.**
> 1. Si `.SAC/memctl.sh` (Unix) o `.SAC/memctl.ps1` (Windows) existe, úsalo
>    (en el repo fuente: `scripts/`). La respuesta que devuelve ES la respuesta.
> 2. Si no existe (exit 127), resuelve con `jq` / lectura directa del archivo respetando el
>    mismo contrato de salida (en instalación global, prueba `~/.SAC/memctl.sh`). Si memctl
>    existe y sale con **exit 1** (JSON inválido, truncado o vacío): detente y avisa; **no leas
>    ni edites el archivo a mano**.
> 3. Nunca inventes un valor. Si la clave no existe o el formato no se puede
>    interpretar, dilo explícitamente.

## Interfaz

```
memctl get <ruta>    # valor o subárbol
memctl list          # claves de primer nivel, en orden de aparición
```

Fuente única: `sac.json` (JSON).

| layout | archivo |
|---|---|
| instalado en un proyecto | `.SAC/config/sac.json` (con `.SAC/memctl.sh` al lado) |
| repo fuente | `config/config/sac.json` |

- `<ruta>`: segmentos separados por `.` — `ado.config.perfil_activo`, `usuario.nombre`.
  Un nombre de clave con `.` no es direccionable (p. ej. un perfil ADO `javier.garcia`).
- Variables: `MEMCTL_ROOT` (raíz del repo fuente; por defecto la del script),
  `MEMCTL_FILE` (ruta explícita a `sac.json`; pisa todo lo demás),
  `MEMCTL_ENGINE` (`auto|jq|python3|node|restricted` en `.sh`; `auto|restricted` en `.ps1`).

## Contrato de salida

- Escalares → impresión cruda: `true`, `null`, `3`, `DEV`, `{project-root}/x`.
  El string vacío imprime una línea vacía y sale con código 0.
- Objetos/arrays → JSON con indentación 2; vacíos → `{}` / `[]`.
- `list` → una clave por línea, en orden de aparición en el archivo.

## Códigos de salida

| código | significado | acción del agente |
|---|---|---|
| `0` | ok | usar la salida |
| `1` | JSON inválido (truncado, vacío, más de un documento) o motor insuficiente | detenerse y reportar: no leer ni editar el archivo a mano |
| `2` | clave o archivo inexistente | la clave NO existe: no inventar ni asumir `null` |

## Parser restringido (fallback sin runtimes)

Cualquier documento JSON válido (scaneo carácter a carácter). Valida el archivo
completo antes de responder: un `sac.json` truncado falla con código 1, nunca
devuelve datos parciales.

## Plantilla de bloque para SKILL.md

Cada skill que necesita config o memoria incluye este bloque, con SOLO las claves que usa.
Los placeholders de ruta se escriben en forma corta (`{hu_folder}`, no `{artifacts.hu_folder}`) y todo
lo que la skill cree vive bajo `{documentacion_sac_path}`; cada placeholder de ruta lleva su fila en la tabla.
memctl solo lee: la persistencia de datos sigue como la define cada skill (edición
directa de `.SAC/config/sac.json`, únicamente bajo su propia sección).

````markdown
**Leer config con memctl** (solo lectura; su salida ES la respuesta):

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa tal cual
en el resto de la skill (no recalcular ni inventar rutas):

| Placeholder / dato | Valor = salida de |
|---|---|
| `{hu_folder}` | `sh .SAC/memctl.sh get artifacts.hu_folder` |
| `{{usuario.nombre}}` | `sh .SAC/memctl.sh get usuario.nombre` |
| `ado.config.perfil_activo` | `sh .SAC/memctl.sh get ado.config.perfil_activo` |

- Exit 0 + `null` → dato no configurado: aplicar el flujo "pregunta una vez y persiste" de esta skill.
- Exit 2 → clave o archivo inexistente: tratarlo como no configurado.
- Exit 127 (memctl no existe) → leer `.SAC/config/sac.json` con `jq`, o usar `~/.SAC/memctl.sh` en instalación global.
- Exit 1 (JSON inválido, truncado o vacío) → detenerse y avisar al usuario: no leer ni editar el archivo a mano. Nunca inventar valores.
- Consultar solo las claves de esta skill; no volcar secciones completas con datos de terceros.
````

Perfiles ADO: el perfil es un mapa por nombre, así que se resuelve en dos pasos
(`P=$(sh .SAC/memctl.sh get ado.config.perfil_activo)` y luego
`sh .SAC/memctl.sh get ado.config.perfiles.$P.<campo>`).

## Nombres reservados de `sac.json`

Ninguna sección de skill puede usar estos nombres:
`schema_version, usuario, idiomas, documentacion_sac_path, archivos, artifacts,
multi_proyecto`.
Las secciones de skill viven al tope del archivo (`ado`, `handoff-release`,
`env-config-audit`, `gh-pr-reviewer`).

## Mantenimiento

- La tabla `scripts/tests/memctl-parity.sh` define el comportamiento y debe
  pasar en verde en ambas implementaciones tras cualquier cambio
  (`sh scripts/tests/memctl-parity.sh`).
- Cambiar el contrato implica actualizar esa tabla PRIMERO (TDD) y después
  `memctl.sh`, `memctl.ps1` y este documento.
