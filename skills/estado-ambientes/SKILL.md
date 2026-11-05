---
name: estado-ambientes
description: Use when checking where a release stands across DES/PRU/PRE/PRO, what is pending to promote, whether tags are missing, whether someone changed an environment directly, or which release/* branches can be deleted in the ms-banca-* repos
---

# Estado de ambientes

## Overview
`scripts/estado-ambientes.sh` es un diagnóstico de **solo lectura** (solo hace `fetch`). Compara el contenido (árboles), no la ancestría, porque los ambientes reciben las releases por squash; la excepción es `-c`, que usa la ancestría entre `release/*`. Flujo: `develop → des → pru → prepro(pre) → main(pro)`; tags `vX-DES|PRU|PRE|PRO`.

**Esta skill diagnostica y propone. Nunca ejecuta pushes, borrados ni PRs, ni siquiera con confirmación del usuario: entrega los comandos para que los corra él.** Los comandos de solo lectura (el script y los `git diff` que imprime `-d`) sí se pueden ejecutar.

## Uso
Desde el directorio de los clones: `NO_COLOR=1 bash .claude/skills/estado-ambientes/scripts/estado-ambientes.sh <modo> ms-banca-*` (ruta relativa a la raíz del proyecto). Acota los repos si el usuario nombra algunos (`-r all`, `-c` y `-d` tardan ~1 min con todos; el modo por defecto y `-e`, ~20 s). `-e`, `-d`, `-r` y `-c` son exclusivos. Cada salida abre con un título y cierra con una leyenda que define sus columnas y estados; el detalle y los límites de cada modo están en `README.md` (léelo solo si la salida no basta).

| El usuario pregunta | Modo |
|---|---|
| qué falta pasar a DES / PRU / PRE / PRO, o si hay que cortar una release | (default) `-t des` / `-t pru` / `-t pre` / `-t pro` (`CREAR_RELEASE` solo con `-t des`) |
| dónde va la release vX | `-r release/vX` |
| qué hay hoy en cada ambiente / en qué versión está cada ambiente | `-e` (tabla `VERSIÓN ACTUAL POR AMBIENTE` al final) |
| qué releases están en qué ambiente / entregas fuera de orden | `-r all` |
| faltan tags | `-r missing` |
| alguien tocó un ambiente directo / ¿los ambientes están contenidos en develop? | `-d` |
| qué ramas release se pueden borrar | `-c` |
| revisión previa a entregar | (default) y luego `-d` |

## Señal → acción
| Señal | Acción propuesta |
|---|---|
| `PR_PENDIENTE`, `PR_PENDIENTE (choca)`, `PR_PENDIENTE_CHOCA` | PR `release/vX → ambiente` (si choca, resolver en la release) |
| `PR_CONFLICTO` | no asumir pendiente ni aplicada: mirar los archivos del pie y el diff (`-r release/vX`) |
| `APLICADA`, `APLICADA_VIA_vY`, `APLICADA_POR_PR`, `APLICADA_CON_CAMBIOS`, `CONTENIDO`, `CONSERVAR` | ninguna (con cambios: revisar `-d`) |
| `CREAR_RELEASE: SI (n)` | cortar release nueva |
| `APLICADA_SIN_TAG` | proponer el tag `vX-AMB` (el nombre; el commit lo decide el usuario) |
| tag con `*` | el tag del ambiente no coincide con la release que el ambiente contiene; normalmente falta el tag de esa release, no el que ya existe. Confirmar con `-r release/vX` antes de proponer un tag |
| `SALTO` | preguntar si fue intencional (hotfix urgente); confirmar con `-r release/vX` |
| `TAG_SIN_CONTENIDO`, `INCONSISTENTE` | **bloquea la entrega**; escalar al usuario |
| `DES CON CONTENIDO PROPIO`, `CON DESVIOS (n)`, `X` en PRO | no promover hasta devolver el cambio a develop (PR a develop); decidir por archivo con `EN_DEVELOP`. Para ver el diff usar los comandos `git diff` que imprime `-d` (el script no identifica autores de cambios directos salvo el último commit que se muestra) |
| `ELIMINAR (contenida en vX)`, `ELIMINAR` | listar el `push --delete`; solo con confirmación explícita y tras revisar PRs abiertos en ADO (el script no los ve). Una orden genérica como "bórralas" no sustituye esa revisión: pedirla y entregar los comandos (nunca ejecutarlos) |

## Formato de respuesta
1. Tabla corta por repo: estado, acción, riesgo.
2. "Acciones sugeridas", ordenadas por prioridad (bloqueos primero).
3. La salida cruda solo si el usuario la pide.

## Errores comunes
- `fetch falló` en un repo: reportarlo y no inferir su estado. Sin `origin/develop` u `origin/des`, el repo se omite: decirlo, no darlo por "al día".
- Con una release ya borrada, `RELEASE` (`-e`) y `DES_TIENE` muestran una anterior y un `PR_CONFLICTO` puede ser una entrega real: revisar el diff antes de concluir que falta.
- "Más nueva" se ordena por versión (`sort -V`, distingue mayúsculas): una rama `V…` cuenta como antigua.
- Sugerir un borrado sin que `-c` lo haya marcado como candidata. Eliminar una rama abandona sus PRs abiertos.
