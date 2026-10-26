# Contrato `memctl` — acceso transversal a la configuración SAC

Bloque para incluir en SKILL.md / instrucciones de agente. Garantiza el mismo
comportamiento en OpenCode, Claude Code, Codex o cualquier harness.

## Regla de uso

> **Antes de consultar configuración, intenta `memctl`.**
> 1. Si `.SAC/memctl.sh` (Unix) o `.SAC/memctl.ps1` (Windows) existe, úsalo
>    (en el repo fuente: `scripts/`). La respuesta que devuelve ES la respuesta.
> 2. Si no existe o falla (motor ausente, entorno restringido), resuelve con las
>    herramientas nativas del agente (`jq` / `yq` / lectura directa del archivo)
>    respetando el mismo contrato de salida.
> 3. Nunca inventes un valor. Si la clave no existe o el formato no se puede
>    interpretar, dilo explícitamente.

## Interfaz

```
memctl get <ruta> [fuente]    # valor o subárbol
memctl list [fuente]          # claves de primer nivel, en orden de aparición
```

| fuente | archivo | formato |
|---|---|---|
| `memory` (default) | `skills/memory_skill.json` | JSON |
| `user` | `config/config/CONFIG_USER.yaml` | YAML |
| `system` | `config/config/CONFIG_SYSTEM.yaml` | YAML |

- `<ruta>`: segmentos separados por `.` — `ado.config.perfiles`, `usuario.nombre`.
- Variables: `MEMCTL_ROOT` (raíz del proyecto; por defecto la del script), `MEMCTL_MEMORY` (ruta a `memory_skill.json`; pisa la derivada de la raíz; layout instalado: el YAML se lee de `config/` junto al script),
  `MEMCTL_ENGINE` (`auto|jq|python3|node|ruby|restricted` en `.sh`; `auto|restricted` en `.ps1`).

## Contrato de salida

- Escalares → impresión cruda: `true`, `null`, `3`, `DEV`, `{project-root}/x`.
  El string vacío imprime una línea vacía y sale con código 0.
- Objetos/arrays → JSON con indentación 2; vacíos → `{}` / `[]`.
- `list` → una clave por línea, en orden de aparición en el archivo.

## Códigos de salida

| código | significado | acción del agente |
|---|---|---|
| `0` | ok | usar la salida |
| `1` | formato no soportado o motor insuficiente | no interpretar a mano: reportar |
| `2` | clave o fuente inexistente | la clave NO existe: no inventar ni asumir `null` |

## Perfil soportado por los parsers restringidos (fallback sin runtimes)

- **JSON:** cualquier documento JSON válido (scaneo carácter a carácter).
- **YAML:** mapas anidados por indentación, escalares (comillas simples/dobles,
  planos, `true`/`false`/`null`, números), flow `["a","b"]` y `{}`/`[]` de
  escalares, comentarios `#`.
- **Fuera de perfil** (secuencias `- `, anclas `&`/`*`, escalares de bloque
  `|`/`>`, tabulaciones, `\uXXXX`): **fallo ruidoso** (código 1), nunca se
  adivina ni se degrada en silencio.

## Plantilla de bloque para SKILL.md

Cada skill que necesita memoria incluye este bloque, con SOLO las claves que usa.
`memory_skill.json` vive en la raíz de skills del proyecto (`$SKILL_DIR/../memory_skill.json`).
memctl solo lee: la persistencia de datos sigue como la define cada skill.

````markdown
**Leer config con memctl** (solo lectura; su salida ES la respuesta):

```sh
M='MEMCTL_MEMORY="$SKILL_DIR/../memory_skill.json" sh .SAC/memctl.sh'
$M get <clave>                 # memoria de skill (memory_skill.json)
$M get <clave> user            # CONFIG_USER.yaml
$M get <clave> system          # CONFIG_SYSTEM.yaml
```

- Exit 0 + `null` → dato no configurado: aplicar el flujo "pregunta una vez y persiste" de esta skill.
- Exit 2 → clave o archivo inexistente: tratarlo como no configurado.
- Exit 1 u otro fallo → leer el archivo directo con `jq`/`yq`. Nunca inventar valores.
- Consultar solo las claves de esta skill; no volcar secciones completas con datos de terceros.
````

Perfiles ADO: el perfil es un mapa por nombre, así que se resuelve en dos pasos
(`P=$($M get ado.config.perfil_activo)` y luego `$M get ado.config.perfiles.$P.<campo>`).
Un nombre de perfil con `.` rompe la ruta.

## Mantenimiento

- La tabla `scripts/tests/memctl-parity.sh` define el comportamiento y debe
  pasar en verde en ambas implementaciones tras cualquier cambio
  (`sh scripts/tests/memctl-parity.sh`).
- Cambiar el contrato implica actualizar esa tabla PRIMERO (TDD) y después
  `memctl.sh`, `memctl.ps1` y este documento.
