# Diseño: DIAT_REF exclusivo del bootstrap, canal por tag persistido en `.ref`

- **Fecha:** 2026-10-14
- **Rama:** `feature/mejoras-plugin-workflow-sac`
- **Estado:** aprobado + **enmienda R8-R10 aprobada ([C] del usuario, 2026-10-14)** → plan
- **Contexto:** Oleada 1 del proceso `bitacora-tecnica/mejoras-canal-di` (7 críticos CLI↔ref). Este diseño implementa el **modelo de canal del usuario** (reglas R1–R4 + R8–R10 + decisiones [P]/[E]) y supone un **cambio de comportamiento deliberado**: la env `DIAT_REF` deja de existir para los comandos diat y `main` deja de ser canal.

---

## 1. Intento y por qué

Hoy `DIAT_REF` es una env que **cada comando** de diat lee (`paths.get_ref()`: env → `DEFAULT_REF='main'`), mientras que el caché persiste `.ref` como mero *residuo* de una descarga. Consecuencias: el canal real de la máquina no está en ningún sitio fiable (el env de la última ejecución manda), los usuarios "olvidan" la env y sus proyectos saltan de canal sin querer, las ramas se cuelan como si fueran versiones, y una ref inexistente solo falla a mitad de proceso. Además, en canal `main` la versión mostrada era **inferencial** (tag semver más alto ≠ contenido del tip de `main`): si el último tag publicado era de prueba, `--version` mentía.

**Modelo objetivo (definido por el usuario, enmienda R8-R10):** los canales son **tags de release** (`vX.Y.Z`, publicados como GitHub Release) o **tags de prueba** (`vX.Y.Z-TEST`). La env es el *argumento de entrada* del bootstrap y nada más; después de instalar, el canal vive en `.ref` y la versión mostrada es **siempre exacta** (deriva del propio `.ref`).

## 2. Metas / no-metas

**Metas**
- G1: `DIAT_REF` solo se interpreta en el bootstrap (`install.sh` / `install.ps1`).
- G2: el bootstrap solo acepta **tags de release** (`vX.Y.Z`) o **tags de prueba** (`vX.Y.Z-TEST`) (R8/R9); ramas, `main`, `-test` minúsculas u otros formatos → rechazo inmediato con mensaje educativo.
- G3: tag inexistente en el repo → aviso + **parada ANTES de descargar** (check por API). Sin `DIAT_REF`, el bootstrap resuelve la última release (`/releases/latest`); sin API o sin releases → parada educativa.
- G4: tras el bootstrap, `.ref` es la **única fuente del canal** para todos los comandos (`--install`, `--update`, `--status`, `--list`, `--version`).
- G5: cambiar de canal (o de tag de prueba) = **re-ejecutar el bootstrap** (no existe `--channel`). El canal **estable** no necesita bootstrap para avanzar: `--update` lo migra a la última release (R10).
- G6: cualquier comando diat detecta `DIAT_REF` exportada en el shell → **aborta con error educativo** (decisión [E]).
- G7: instalación existente cuyo canal difiere del tag solicitado → cambiar todo pero **pidiendo confirmación** (decisión [P]).

**No-metas**
- No se implementa `diat --channel` (G5/R10 lo sustituyen).
- No se migra automáticamente a los usuarios; el error de G6/G4 los lleva al bootstrap.
- No cambia el flujo de instalación de componentes dentro de un canal (`--install` es idéntico, solo cambia de dónde lee el canal).
- No se soporta fijar un release antiguo en canal estable (tradeoff consciente de R10).
- No se toca el plugin `workflow-sac`.

**Anti-metas (falla si…)**
- Que cualquier comando siga leyendo `DIAT_REF` como canal.
- Que se pueda instalar una rama o `main` por bootstrap.
- Que el bootstrap escriba solo el CLI y deje el caché viejo (estado mixto).
- Que un `--update` mueva proyectos a un canal distinto del `.ref` persistido.
- Que un tag `-TEST` (o cualquier prerelease) coloree la versión/canal estable.

## 3. Decisiones del usuario (fijas)

| # | Decisión |
|---|---|
| D1 | `DIAT_REF` vive **solo** en la línea del bootstrap; los comandos no la leen. |
| D2 | El bootstrap solo acepta **tags de release o de prueba** (`vX.Y.Z` / `vX.Y.Z-TEST`); ramas y `main` → rechazo con mensaje (R8/R9). |
| D3 | Tag inexistente → aviso + parada antes de descargar. |
| D4 | `.ref` = fuente única de verdad del canal tras instalar (R2). |
| D5 | Cambiar de canal = re-ejecutar el bootstrap (R1/R3). El canal estable **avanza solo** con `--update` hacia la última release (R10). |
| D6 | Instalación existente con canal distinto → confirmación previa antes de cambiar todo [P]. |
| D7 | `DIAT_REF` presente en el entorno de un comando diat → **abortar** con error educativo [E]: *"DIAT_REF ya no aplica. Para cambiar de canal, re-ejecuta el bootstrap. Retira 'export DIAT_REF=…' de tu shell."* |

### Reglas R8-R10 (adopción del usuario, 2026-10-14 — sustituyen la propuesta R5-R7)

- **R8 — Release = fuente única de lo estable:** los canales son **tags de release** (`vX.Y.Z`, publicados como GitHub Release) o **tags de prueba** (`vX.Y.Z-TEST`). `main` **no es canal**. El bootstrap sin `DIAT_REF` resuelve la **última release publicada** (`GET /releases/latest`) y fija ese tag en `.ref`.
- **R9 — Convención `-TEST` en mayúsculas:** el patrón único es `^v\d+\.\d+\.\d+(-TEST)?$`; `-test` minúsculas, `rc1` u otros prereleases se rechazan (el histórico `v0.18.1-test` queda obsoleto).
- **R10 — Semántica por canal en `--update`:**
  - **Estable** (sin `-TEST`): el canal ES "la última release". `--update` compara `.ref` con `GET /releases/latest`; si hay una más nueva → **migra automáticamente** (reescribe `.ref`/`.sha`/`.version`, re-descarga y reinstala) con aviso `Canal estable: vX.Y.Z → vA.B.C (última release)` — sin [P] (es la definición del canal, no un cambio de canal).
  - **Prueba `-TEST`:** **pin explícito**. `--update` solo refresca si el tag se movió; **nunca salta a otro tag**. Cambiar de prueba = bootstrap con [P].
- **Consecuencias:** `--version` es **siempre exacto** (deriva de `.ref`; la antigua propuesta R5 "main @ sha" queda innecesaria) y los tags `-TEST` jamás colorean lo estable (`/releases/latest` solo devuelve releases publicadas — R6/R7 innecesarios).
- **Tradeoff consciente:** en canal estable no existen "versiones viejas" — `--update` siempre lleva a la última; fijar un release concreto no está soportado (para experimentar con versiones concretas está el canal `-TEST`).

## 4. Calls del constructor (míos, marcados por si se vetan)

- **B1 — Patrón de tag (R9):** `^v\d+\.\d+\.\d+(-TEST)?$` — acepta `v2.1.1` y `v2.2.0-TEST`; rechaza `main`, ramas, `v0.18.1-test` (minúsculas), `v2.2.0-rc1` y cualquier otro formato. El patrón estable estricto (para la resolución sin env) es `^v\d+\.\d+\.\d+$`.
- **B2 — Alcance del aborto [E]:** **todos** los comandos diat (lectura estricta de D7), incluidos `--help`/`--version`. El propio bootstrap nunca invoca a diat con la env puesta (la limpia antes de invocar).
- **B3 — Bootstrap sin `DIAT_REF` (R8):** resuelve la **última release publicada** (`GET /releases/latest` → `tag_name`, validado además contra el patrón estable estricto) y la instala como canal. `main` ya no se instala nunca. Sin releases publicadas o sin API → parada educativa.
- **B4 — `.ref` ausente** (instalación legada pre-canales): los comandos que necesitan canal abortan con *"canal no registrado — re-ejecuta el bootstrap"* (el bootstrap siempre escribe `.ref`). `--help` no requiere canal; `--version` lee `.version` (excepción documentada).
- **B5 — Paridad:** mismas reglas en `install.sh` e `install.ps1` (formato, resolución sin env, existencia, confirmación [P], escritura de estado).
- **B6 — Check de existencia:** API `GET /repos/{owner}/{repo}/git/ref/tags/{tag}` desde el shell (404 → D3). `403/429` (rate-limit) → aviso "no se pudo verificar" + continuar (no romper installs sin token).
- **B7 — `--update`** trabaja exclusivamente sobre `.ref` (nunca sobre env — ya no existe).
- **B8 — Sin `--channel`** en esta iteración (D5/R10).
- **B9 — Tags de prueba para validar:** el flujo de desarrollo pasa a usar tags `vX.Y.Z-TEST` (mayúsculas, R9) sobre la rama; la E2E pendiente se hará bajo estas reglas cuando el usuario lo autorice. El `v0.18.1-test` existente queda obsoleto.
- **B10 — Mecanismo del prompt [P] bajo `curl|bash`** *(del builder-check)*: como el script se lee de stdin, la confirmación se lee desde **`/dev/tty`**; si no hay TTY (CI/scripted) → **abortar** con instrucciones (sin consentimiento posible no se ejecuta el reemplazo destructivo). El aviso de rate-limit B6 usa el mismo canal: en canal distinto sin TTY → aborta; en canal mismo → aviso y continúa.
- **B11 — Versión siempre exacta (R8-R10, sustituye a M-10):** la versión mostrada se deriva **siempre** de `.ref`: `v{ref sin v} (canal: {ref})`. `.version` se escribe como espejo para metadatos del registro (`registro._write`). `github.get_remote_version()` **sale del flujo de canal**; se sustituye por `github.get_latest_release_tag()` (solo para la semántica estable de R10). Los tags `-TEST` jamás se muestran como versión estable.
- **B12 — `.ref` se valida al leer (B1/R9):** debe ser un tag del patrón B1 o `main` (legado pre-R8); cualquier otro valor → error *"canal inválido ('X') — re-ejecuta el bootstrap"*. `main` legado se trata como **canal estable** y `--update` lo auto-migra a la última release (R10).
- **B13 — La batería C1 se persiste como test real** *(del builder-check)*: los 7 checks pasan a `INSTALACION/tests/test_deps.py` (hoy solo existían como script ad-hoc de sesión) y la ejecución de esa batería entra en la validación de cada cambio.
- **B14 — `main` nunca es canal (R8):** `DIAT_REF=main` se rechaza siempre (el error indica ejecutar sin env para la última release, o pasar un tag). Refuerza B3: no hay ningún camino que instale `main`.
- **B15 — El bootstrap NO escribe `.sha` y NO purga componentes** *(resolución de R4 al planificar)*: `.sha` solo lo escribe quien descarga componentes (`ensure_cache`/`--update`), para que la etiqueta jamás describa contenido ajeno (el anti-patrón M-01). Tras un cambio de canal, el primer comando detecta desajuste `.sha`↔remoto y re-descarga solo — reemplazo completo **sin** purge destructivo.

## 5. Cómo funciona

### 5.1 Bootstrap
```text
curl -fsSL …/install.sh | DIAT_REF=v2.2.0-TEST bash   (o sin DIAT_REF)
1. Leer DIAT_REF (opcional)
   ├─ presente → REF = env (debe cumplir ^v\d+\.\d+\.\d+(-TEST)?$)
   └─ ausente  → REF = última release (GET /releases/latest, estricto ^v\d+\.\d+\.\d+$)
2. Validar formato (B1/R9)  → malo: "DIAT_REF solo acepta tags vX.Y.Z o vX.Y.Z-TEST;
   recibido 'X'. Para la última release, ejecuta sin DIAT_REF." → exit 1
3. ¿REF vino de env? → API: ¿existe el tag?  → 404: "El tag 'X' no existe en el repo."
                                               → exit 1   [D3]
                                403/429: aviso + continuar [B6]
   (si REF es la última release ya vino de la API: check no aplica)
4. ¿Instalación existente (bin/diat presente)?
   ├─ No  → descargar tarball del tag → extraer bin/ + componentes
   └─ Sí  → ¿.ref actual == REF?
            ├─ Sí  → refrescar bin+CLI (sin prompt)
            └─ No  → [P] "canal actual: 'A' → nuevo: 'B' ¿continuar?" (no → exit 0)
                     → descargar → REEMPLAZAR bin+CLI. Los componentes del caché se
                       refrescan solos en el primer comando (desajuste .sha →
                       re-descarga) [B15: sin purge destructivo]
5. Escribir estado: .ref = REF · .version = <REF sin v> · NO se escribe .sha
   (solo lo escribe quien descarga componentes: la etiqueta nunca describe
   contenido ajeno) [G4/M-4/B15]
6. Nunca invocar diat con DIAT_REF en el entorno (B2)
```

### 5.2 Comandos post-bootstrap
```text
diat --install|update|status|list|version
1. Si DIAT_REF está en el entorno → aborto educativo [D7/B2]
2. ref = leer(.ref)               [G4]  (sin .ref → error B4; 'main' legado = estable)
3. Semántica de canal (R10), aplicada en --update y --status:
   ├─ ref termina en -TEST → PIN: comparar sha(ref) vs .sha; si el tag se movió,
   │   redescarga; nunca salta a otro tag
   └─ ref estable (tag release o 'main' legado) → comparar con GET /releases/latest:
       ├─ última == ref  → "Canal estable al día"
       └─ última != ref  → --update: MIGRA (reescribe .ref/.sha/.version, re-descarga,
                            reinstala) con aviso "Canal estable: vX → vY (última release)"
                           --status: solo muestra "actual vX · última vY"
4. Resto del flujo igual que hoy, con ref = .ref
   --update reetiqueta proyectos SOLO al ref de .ref [B7]
   La comparación por PROYECTO difiere a la continuación de la O1 (Q3 = [O1], ver §7).
```

### 5.3 Flujo de cambio de canal/versión (G5)
```text
- Canal estable: diat --update  → migra solo a la última release (R10, sin bootstrap)
- Canal de prueba o cambio de canal: curl … | DIAT_REF=v2.3.0-TEST bash
  → pasos 1-6 con confirmación [P] si aplica
```

## 6. Archivos a modificar

| Archivo | Cambio |
|---|---|
| `INSTALACION/bootstrap/install.sh` | validación formato [B1/R9], resolución última release sin env [B3], check tag API [B6], prompt [P], escritura `.ref/.version` [G4/B15], `unset` de env antes de invocar diat |
| `INSTALACION/bootstrap/install.ps1` | paridad total [B5] |
| `INSTALACION/diatlib/paths.py` | `get_ref()` → **leer `.ref`** (sin env); `TAG_PATTERN` (R9), `is_test_channel(ref)`, `ChannelError`; mensajes [B4/B12] |
| `INSTALACION/diat` | detección de `DIAT_REF` → aborto educativo [D7/B2]; `--version` exacto de `.ref` [B11]; `--status` muestra actual vs última release (R10) |
| `INSTALACION/diatlib/update.py` | semántica R10 por canal (migración estable / pin `-TEST`); sin `get_remote_version` |
| `INSTALACION/diatlib/github.py` | `get_latest_release_tag()` (sustituye a `get_remote_version` en el flujo de canal) |
| `INSTALACION/diatlib/registro.py` | sin cambios funcionales (ref por proyecto se mantiene) |
| `INSTALACION/README.md`, `README.md` | documentar nuevo uso: releases como canal · tags `-TEST` · sin env · cambio de canal por bootstrap |
| `bitacora-tecnica/mejoras-canal-di/bitacora.md` | checkpoint al implementar |

**Nota sobre [E] y los tests existentes:** toda prueba/batería que prefija `DIAT_REF=… diat …` deja de ser válida — usar bootstrap por tag [B9]. La E2E de C1 queda **apagada por el usuario** hasta nuevo aviso.

## 7. Orden con la Oleada 1

Este diseño **adelanta** los ítems M-4/M-5/M-8 (antes Oleada 2) por decisión del usuario. Tras él, continúan los críticos pendientes: **C2, C3, C4, C5, C6, C7**.

**Q3 resuelto (2026-10-14, decisión [O1]):** la comparación de `--status`/`--list` **por proyecto** (cada proyecto contra `inst['ref']` + la trinidad "al día / cambio de canal / actualización real" — núcleo de C5/B-02/M-3) **DIFIERE a la continuación de la Oleada 1**. Esta oleada solo implementa el modelo de canal (§5) + los fixes asociados (M-4/M-5/M-8/M-10 con B10–B15). El nivel sistema ya queda verdadero con este diseño (B12/G4).

**Enmienda (2026-10-14, [C] del usuario):** R8-R10 sustituyen la propuesta R5-R7 — canales = releases (`vX.Y.Z`) + prueba (`vX.Y.Z-TEST`); `main` deja de ser canal; la versión mostrada es siempre exacta; el canal estable avanza solo con `--update`.

## 8. Validación

- **Unitaria (python):** `paths.get_ref()` lee `.ref` y no env · env presente en arranque de `diat` → exit≠0 + mensaje · patrón R9 (acepta `v2.1.1`/`v2.2.0-TEST`, rechaza `main`/ramas/`v0.18.1-test` minúsculas) · `.ref` ausente → error B4 · **migración estable R10** (`--update` migra a última release; canal `-TEST` pin, nunca salta) · `--version` exacto por canal · `.version` espejo coherente.
- **Shell:** `bash -n`; funciones con fixtures (formato/404/confirmación/sin TTY/escritura de estado); integración pipe con `DIAT_REF=feature/x` y `DIAT_REF=main` → rechazo antes de descargar; orden `unset` antes de invocar diat.
- **PowerShell:** revisión estática de paridad (no hay pwsh garantizado en el entorno).
- **E2E (apagada):** bajo reglas nuevas — tag `vX.Y.Z-TEST` en la rama, bootstrap A/B, `--install` en HOME aislado. Requiere luz del usuario.
- **Regresión:** batería unitaria C1 (7 checks) debe seguir verde.

## 9. Riesgos

- **R1:** usuarios con `export DIAT_REF` en `.zshrc` verán todos sus comandos abortados — es intencional [E]; el mensaje los guía al bootstrap.
- **R2:** rate-limit de API en el check del bootstrap [B6] — degradado a aviso, no a bloqueo.
- **R3:** instalaciones legadas sin `.ref` — ruta de recuperación = re-ejecutar bootstrap (B4). Instalaciones legadas con `.ref=main` se auto-migran a la última release en el primer `--update` (B12).
- **R4:** ~~el purge al cambiar de canal (D5) es destructivo~~ — **resuelto por B15: no hay purge**; el caché se refresca por desajuste de `.sha` en el primer comando, con confirmación [P] previa al cambio de `.ref`.
- **R5:** el nombre de la última release depende de la convención del repo (`vX.Y.Z`); una release mal nombrada (`v2.2.0-TEST` publicada como release normal, o `release-1`) → el bootstrap sin env la rechaza con error educativo (B3 valida patrón estable estricto).
