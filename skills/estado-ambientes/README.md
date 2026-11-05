# estado-ambientes

Muestra en qué ambiente (DES, PRU, PRE, PRO) está cada release de los repos de Banca por WhatsApp, qué falta por promover, qué tags faltan y qué releases se pueden eliminar. Es de solo lectura: lo único que hace en git es `fetch --tags`.

## Uso

```
bash scripts/estado-ambientes.sh <repos> [opciones]
```

- Si no pasas repos, usa todos los que haya en la carpeta (o `.` si estás dentro de un repo). Pasa solo los que necesites: `-d` hace una consulta por archivo y con todos los repos tarda ~1 min, con uno ~2 s.
- Las opciones van en cualquier posición.
- `-t` y `-r` necesitan un valor; si falta, el script avisa. Los modificadores `-b` y `-l` se eliminaron (el script lo indica si se usan): `-r all` reemplaza a `-l`.

## Ramas y tags por ambiente

| Ambiente | Rama | Tag |
|---|---|---|
| DES | `des` | `vX.Y.Z-DES` |
| PRU | `pru` | `vX.Y.Z-PRU` |
| PRE | `prepro` | `vX.Y.Z-PRE` |
| PRO | `main` | `vX.Y.Z-PRO` |

## Columna `TAG` y el `*`

- **Qué tag muestra:** el tag con el sufijo del ambiente (`-DES`, `-PRU`, `-PRE`, `-PRO`) **más cercano a la punta de la rama del ambiente** (`git describe --tags --match "*-<AMBIENTE>" --abbrev=0`). No usa la fecha de creación ni la versión más alta, y solo ve tags alcanzables desde esa rama. Sin tag: `-`.
- **Cuándo lleva `*`:** cuando la versión del tag difiere de la de la columna `RELEASE` de la misma fila (en la tabla por defecto, `ULTIMO_TAG` contra `DES_TIENE`). Se compara sin el sufijo ni la `v` y sin distinguir mayúsculas: `v1.0.3-DES` → `1.0.3` contra `release/v1.0.4` → `1.0.4`.
  - Tag menor que la release: `*` — falta el tag de la versión contenida.
  - Tag mayor que la release: `*` — tag sin contenido o release incompleta.
  - Iguales, o tag/`RELEASE` en `-`: sin `*`.
- **Dónde se explica:** cada `*` se detalla al pie en `REVISAR TAGS`.
- **Límite:** como compara contra `RELEASE`, hereda sus límites. Si `RELEASE` sale más vieja de lo real (rama de release borrada, conflicto o entrega parcial), puede salir un `*` "adelantado" que no es un problema real; verifica con `-r release/vX.Y.Z`.

## Vistas (cada una imprime su tabla y termina)

Cada vista empieza con una línea de título en negrita y una descripción en gris (`CANDIDATAS A ELIMINAR — qué releases se pueden borrar y qué falta para poder hacerlo`) para saber qué se va a ver. El título del comando por defecto sigue al destino (`ESTADO DE PASO A PRU` con `-t pru`).

| Comando | Qué hace | Salida | Ejemplo |
|---|---|---|---|
| *(sin opciones)* | Analiza si hay cambios **pendientes por pasar a `des` mediante una release** (flujo `release → ambiente`; `develop` no se promueve directo). Compara la release más nueva contra el destino y mira si `develop` tiene commits fuera de ella. | Una fila por repo: `RELEASE_MAS_NUEVA` (la de mayor versión entre las `release/*` que existen: contra ella se compara), `DES_TIENE` (release más nueva ya contenida en el destino), `VEREDICTO` (estado de `RELEASE_MAS_NUEVA` respecto al destino: `APLICADA`, `PR_PENDIENTE`, `PR_PENDIENTE (choca)`, `PR_CONFLICTO`, `SIN_RELEASE`), `QUE_TRAE` (diferencia de archivos release → destino, o `choca en N archivo(s)`), `CREAR_RELEASE` (`SI (n)` = `develop` tiene n commits fuera de la release más nueva, `NO`, o `-` si el destino no es `des`: cortar una release es el paso previo a DES, así que con `-t pru`, `-t pre` o `-t pro` no aplica y el grupo "cortar release" no se imprime) y `ULTIMO_TAG`. Después: leyenda (columnas, veredictos, flujo) y `PARA PASAR A DES` con las acciones por tipo (abrir PR, revisar conflicto, cortar release). | `estado-ambientes.sh ms-banca-*` |
| `-e` | Última entrega de cada ambiente: cuándo, por qué PR y quién la mergeó. | Una fila por repo y ambiente: `FECHA`, `PR`, `MERGEADO_POR`, `RELEASE`, `TAG`, `ASUNTO`. El `*` en el tag y `REVISAR TAGS` al pie avisan si el tag está desactualizado. Si el título del último PR nombra una release distinta de `RELEASE`, un aviso al pie lo indica (ej.: hotfix entregado después). Los nombres de release salen en minúscula. Al final, la tabla **`VERSIÓN ACTUAL POR AMBIENTE`**: una fila por repo con la release más nueva cuyo contenido ya tiene cada ambiente (`DES PRU PRE PRO`; `(por PR)` si sale del título de un PR; `-` si ninguna). Sus límites son los de la columna `RELEASE`. | `estado-ambientes.sh ms-banca-retiros -e` |
| `-d` | Detecta **desvíos**: archivos de un ambiente cuya versión **nunca existió en el historial de `develop`** (fix, hotfix o commit directo que no volvió). Que `develop` tenga cosas nuevas no cuenta. No depende de las `release/*`. | 1) Resumen por ambiente: `CONTENIDO` o `CON DESVIOS (n)`. 2) Detalle por archivo: `X` (el ambiente tiene esa versión; rojo en PRO), `=` (igual a develop), `~` (otra versión), `-` (no tiene el archivo); `EN_DEVELOP` (`no existe` / `otra versión`), `EDAD` y último commit. 3) Resumen, repos sin desvíos y comandos `git diff` sugeridos. No detecta archivos borrados solo en el ambiente. | `estado-ambientes.sh ms-banca-retiros -d` |
| `-r release/vX` | Estado de **una** release en los 4 ambientes. | `APLICADA(tag)`, `APLICADA_SIN_TAG`, `APLICADA_VIA_vX`, `PR_PENDIENTE` (merge limpio que cambia el ambiente: abrir el PR), `PR_PENDIENTE_CHOCA` (pendiente y el PR chocará: ninguna versión de la release pasó por el ambiente), `APLICADA_CON_CAMBIOS` (todas las versiones de la release pasaron por el ambiente y este las cambió después), `APLICADA_POR_PR` (el merge choca pero el título de un PR mergeado nombra la release), `PR_CONFLICTO` (el merge choca y la prueba de historial no es concluyente: revisar el diff), `TAG_SIN_CONTENIDO`, `SIN_RAMA`. Avisa (`DES CON CONTENIDO PROPIO`) si DES tiene archivos cuya versión nunca existió en `develop` (mismo método que `-d`, no depende de las releases que existan). Si la release llegó dentro de otra, el estado dice `APLICADA_VIA_vX`. | `estado-ambientes.sh ms-banca-localizacion -r release/v1.0.5` |
| `-r all` | Igual que `-r`, con **todas** las `release/*` de cada repo (una fila por release). | Tabla por repo y, al pie, `FALTAN TAGS` con los nombres exactos (`v1.0.4-DES`) y `SALTO` (la release está en un ambiente posterior pero falta en uno anterior: entrega fuera de orden, p. ej. `localizacion release/v1.0.3.1: está en PRE pero falta en PRU`; puede ser intencional, como un hotfix urgente; los conflictos y las ramas inexistentes no cuentan). La fila afectada lleva `SALTO` en rojo en negrita. | `estado-ambientes.sh ms-banca-* -r all` |
| `-r missing` | Como `all`, pero solo las releases con tag faltante o `TAG_SIN_CONTENIDO`. | Misma tabla, filtrada. | `estado-ambientes.sh ms-banca-* -r missing` |
| `-c` | **Candidatas a eliminar.** Las `release/*` se cortan de `develop` sin squash, así que la **más nueva** contiene (por ancestría de commits) a las anteriores. Una release **contenida en la más nueva** es candidata (su contenido viaja con ella), salvo que tenga ramas de trabajo sin integrar basadas en ella. Una **no contenida** (hotfix, línea antigua) necesita: contenido en DES, PRU, PRE y PRO; tag `vX-PRO` en `main` (no se exige si llegó vía otra release); sus cambios ya existieron en `develop`; sin ramas basadas. Se **conservan siempre** la más nueva y la base de PRO (por contenido y por el último tag `-PRO`). | Cinco bloques: 1) resumen por repo (`MAS_NUEVA`, `BASE_PRO`, candidatas, bloqueadas, en curso); 2) detalle con matriz `DES PRU PRE PRO TAG DEV RAM ANC` y estado `ELIMINAR (contenida en vX)`, `ELIMINAR`, `BLOQUEADA` o `CONSERVAR (...)`; 3) **leyenda** (marcas, columnas, estados y reglas) y 4) **PARA PODER ELIMINAR**: acciones por tipo (aviso si la más nueva tiene cambios sin devolver a `develop`, crear tag, llevar a develop, resolver ramas, revisar); 5) candidatas con los `git push origin --delete` sugeridos (no los ejecuta; al eliminar se abandonan los PRs abiertos de esa rama: revisarlos en ADO). | `estado-ambientes.sh ms-banca-* -c` |

**Marcas del detalle de `-c`**

| Columnas | Marca | Significado |
|---|---|---|
| `DES PRU PRE PRO` (¿el contenido de la release ya está en la rama del ambiente?) | `✓` | sí, el contenido ya está en la rama |
| | `≈` | sí, pero llegó dentro de otra release posterior que ya está en la rama |
| | `✗` | todavía no: falta entregarla (el merge entraría limpio). Si la release está contenida en la más nueva, llegará con ella y **no bloquea** la eliminación |
| | `!` | el merge simulado choca: revisar con `estado-ambientes.sh <repo> -r release/vX` |
| | `·` | no evaluado |
| `TAG DEV RAM ANC` | `✓` / `✗` / `–` / `·` | cumple / no cumple (`✗n` = n archivos o ramas) / no aplica / no evaluado |

**Cuando el merge simulado choca.** El script no se queda en "conflicto": (1) si el título de algún PR mergeado en el ambiente nombra la release (`Merged PR N: Release/vX - DES`), es `APLICADA_POR_PR`; (2) si no, mira los archivos en que la release y el ambiente difieren y si la versión de la release de cada uno **existió alguna vez en el historial del ambiente**: todos = `APLICADA_CON_CAMBIOS`, ninguno = `PR_PENDIENTE_CHOCA`, mezcla = `PR_CONFLICTO`. Además, `DES_TIENE` (tabla por defecto) y `RELEASE` (`-e`) muestran `vX (por PR)` cuando el título de un PR nombra una release más nueva que la del contenido (choca o su rama se borró). Los títulos solo llevan versión en DES hoy; con el flujo nuevo (`Release/vX.Y.Z - PRU`) funcionaría en los 4 ambientes.

## Modificador (cambia la tabla por defecto)

| Opción | Qué hace | Ejemplo |
|---|---|---|
| `-t X` | Rama **destino** (por defecto `des`). Acepta `des`, `pru`, `pre`/`prepro` y `pro`/`main`. | `estado-ambientes.sh ms-banca-* -t pre` |


## Reglas generales

- **Por contenido, no por tags.** Las decisiones salen de comparar los árboles de las ramas. DES recibe las releases por squash (`git log des..develop` o `git cherry` dan falsos pendientes) y los tags no se ponen de forma constante. Los tags solo se informan.
- **`APLICADA_VIA_vX`:** la release no está tal cual, pero llegó dentro de la release `vX`, que la contiene. No se le exige tag propio.
- **Combinaciones.** `-e`, `-d`, `-r` y `-c` son vistas exclusivas: si pasas varias, el script avisa cuáles ignora (prioridad `-e`, `-d`, `-r`, `-c`). `-t` solo afecta la tabla por defecto.
- **Tags.** Se comparan sin distinguir mayúsculas (`V1.0.2-PRO` = `v1.0.2-PRO`).
- **Formato.** Color solo en terminal (`NO_COLOR=1` lo apaga), por gravedad:

  | Color | Nivel | Ejemplos |
  |---|---|---|
  | Verde | Todo bien | `APLICADA(tag)`, `APLICADA_VIA_vX`, `CONTENIDO`, `=` |
  | Cian | Trabajo normal | `PR_PENDIENTE` |
  | Amarillo | Atención | `APLICADA_SIN_TAG`, tag con `*`, `~`, `CREAR_RELEASE: SI (n)` |
  | Rojo | Revisar | `PR_CONFLICTO`, `PR_PENDIENTE (choca)`, `CON DESVIOS (n)`, `X` fuera de PRO |
  | Rojo en negrita | Bloquea | `TAG_SIN_CONTENIDO`, `SALTO`, `X` en PRO |
  | Gris | Sin dato | `SIN_RAMA`, `-` |

  El color nunca va solo: siempre acompaña al nombre del estado. Al pie, `-r` explica cada estado que aparece en la tabla, con su acción.
- **Release borrada.** Si una release ya se eliminó (cumplió su ciclo hasta PRO), `-d` y `DES CON CONTENIDO PROPIO` siguen siendo correctos porque no dependen de las ramas de release. `RELEASE` en `-e` y `DES_TIENE` mostrarían la release más nueva que *aún exista* y el tag posterior saldría con `*`; un `PR_CONFLICTO` puede ser una release ya entregada cuya release posterior se borró (revisar el diff). Por eso conviene no borrar una release hasta que `-c` la marque candidata.
- **No usar `git fetch --prune`:** elimina referencias remotas locales que otras ramas pueden necesitar.

## Flujo objetivo de entregas

La misma `release/vX.Y.Z` (cortada desde `develop`, sin squash) se promueve a cada ambiente (`release → des → pru → pre → pro`). Una release se elimina cuando una más nueva la contiene (su contenido viaja con ella) o, si no está contenida (hotfix, línea antigua), cuando completó su ciclo; para decidirlo se usa `-c`, que siempre conserva la más nueva y la base de PRO. Cualquier cambio hecho en la release o en un ambiente debe volver a `develop` (`-d` lo detecta). Todos los archivos deben ser idénticos en todas las ramas y ambientes, sin excepciones.

Más detalle de diseño y interpretación: `SKILL.md`.
