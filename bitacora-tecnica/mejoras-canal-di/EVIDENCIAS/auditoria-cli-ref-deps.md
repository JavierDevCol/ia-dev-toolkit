# Auditoría 1 — CLI↔ref: `INSTALACION/diat`, `diatlib/deps.py`, `diatlib/instalar.py`

> Auditoría delegada a subagente explore (solo lectura) — 2026-10-13, rama `feature/mejoras-plugin-workflow-sac`.
> Contexto de apoyo verificado: `paths.py` (DEFAULT_REF, COMPONENT_LAYOUT, RECURSIVE_TYPES), `github.py` (get_remote_sha, scan_components vs build_catalog, download_and_stage, stage_cli_to_bin), `registro.py` (merge, save_installation), `update.py`.

## 🔴 CRÍTICOS

### C-01 — Validación del grafo LOCAL contra el catálogo de la REF aborta toda la instalación
- **Ubicación:** `INSTALACION/diatlib/deps.py:75` y `deps.py:80` (raise en `:85`), invocado desde `INSTALACION/diat:160-163`
- **Escenario (el KNOWN, 3 disparadores concretos):** `COMPONENT_DEPENDENCIES` (`deps.py:26-62`) vive en el CLI local, pero `catalog` viene de `github.scan_components(cache)` de la ref objetivo (`diat:158`). Disparadores: (a) `DIAT_REF` = tag beta antigua sin `workflows:demo-delegacion` → error `tiene deps pero no está en el catálogo` (`deps.py:76`); (b) ref sin `plugins/` (layout viejo) o sin `commands:workflow-sac` / `agents:PO` → error `NO existe en el catálogo` (`deps.py:83`); (c) la ref marcó un workflow con `ready: false` → `scan_components` lo excluye del catálogo (`github.py:227-234`) → falso "no está en el catálogo" aunque el fichero exista (y `update.py:71` valida con `build_catalog` *sin* filtro ready → `--install` y `--update` discrepan). El aborto es total (`diat:163 return`): no permite siquiera instalar skills no relacionadas, pese a que la instalación pedida sería consistente.
- **Fix:** en `validate_dependencies`, separar owner-hueco-falta-catálogo en *warning* salvo que el owner/dep sea alcanzable desde las seeds seleccionadas, y validar solo el subgrafo de las seeds elegidas (llamar tras `diat:165`, no antes); añadir al mensaje `deps.py:85` el par `CLI local ↔ ref={paths.get_ref()}`.

### C-02 — Dirección inversa: la ref declara dependencias que el grafo local no conoce → instalación rota en silencio
- **Ubicación:** `INSTALACION/diatlib/deps.py:91-125` (`resolve_closure`), `deps.py:128-141`, desde `INSTALACION/diat:172-176`, `diat:184`
- **Escenario:** la tag beta añade `workflows:nuevo-flujo` con `requires: plugins:nuevo-plugin` (o cualquier dep nueva); el CLI de `main` no tiene esa entrada → `resolve_closure` devuelve solo la seed → `install_component` copia el workflow sin su plugin/command/agente → fallo en runtime, cero avisos. Ídem `collect_optional` (`diat:173`): opcionales existentes en la ref jamás se ofrecen. El catálogo de la ref no lleva manifiesto de deps (todo es grafo local), así que no hay validación posible de "lo seleccionado está completo".
- **Fix:** añadir al repo (en la ref) un manifiesto `components.manifest.json` con requires/optional por componente; que `resolve_closure`/`validate` lo lean del cache si existe y solo usen `COMPONENT_DEPENDENCIES` como fallback del CLI local.

### C-03 — Auto-actualización a mitad de proceso: se valida con el grafo EN MEMORIA viejo contra el caché YA nuevo
- **Ubicación:** `INSTALACION/diat:59` (`github.download_and_stage()` dentro de `ensure_cache`), con imports en `diat:22-24` y validación en `diat:160`
- **Escenario:** `diat --install` con `DIAT_REF` cambiada → `ensure_cache` descarga el snapshot y `stage_cli_to_bin` **sobrescribe `bin/diat` + `bin/diatlib/`** (`github.py:156, 162-186`) mientras el proceso sigue vivo con los módulos viejos ya importados en `diat:22`. Acto seguido `diat:160` valida el grafo VIEJO contra el catálogo NUEVO → `DependencyError` falso exactamente en la ejecución que trae el fix; el usuario debe re-ejecutar. Agravante: cualquier import diferido posterior (p. ej. `from diatlib import desinstalar` en `diat:318`) carga código NUEVO en un proceso sembrado con módulos VIEJOS → mezcla de versiones en un solo run.
- **Fix:** en `ensure_cache`, si hubo staging del CLI (`download_and_stage` → True), hacer `os.execv(sys.executable, [sys.executable] + sys.argv)` para relanzar con el CLI nuevo antes de validar; o como mínimo, advertir "CLI actualizado: re-ejecuta el comando".

### C-04 — Sin conexión: se instala caché de OTRA ref y el registro queda envenenado con la ref del env
- **Ubicación:** `INSTALACION/diat:47-68` (ensure_cache con `remote_sha=None` → devuelve caché viejo sin más condiciones, `diat:55-67`), `diat:186-187` (`save_installation`)
- **Escenario:** usuario con `DIAT_REF=v0.18.1-test` ejecuta `diat --install` sin red. `get_remote_sha()` devuelve `None` (`github.py:102-104`) → la condición de re-descarga (`diat:55`) es falsa → se devuelve el caché de `main` **sin comprobar `registro.get_installed_ref() != ref`**. Se instalan componentes de `main` y luego `save_installation(..., sha=get_installed_sha())` con `ref=None` → `registro.py:74` escribe `ref=get_ref()` = la ref del env → **el registro afirma ref beta + sha ajeno**. Consecuencia: `--status`/`--list` mienten durante toda la vida del registro ("al día" vs remote de beta con contenido de main).
- **Fix:** en `ensure_cache`, si `remote_sha is None` y `registro.get_installed_ref() != ref`, abortar con "caché pertenece a ref '{cached}', se requiere conexión para '{ref}'"; y en `cmd_install` pasar `ref=paths.get_ref()` capturado en `ensure_cache` (no el default de `registro`).

## 🟠 MEDIUM

### M-01 — El caché no se purga al cambiar de ref → componentes fantasma de la ref anterior
- **Ubicación:** `INSTALACION/diat:59` (usa `download_and_stage`); raíz en `github.py:147-153`
- **Escenario:** `main` (con `plugins/`, `config/`, 20 skills) → `DIAT_REF` a tag antigua sin esas carpetas: `download_and_stage` solo hace `rmtree` de los dirs **presentes en el snapshot nuevo**; `cache/plugins`, skills eliminadas, etc. permanecen → `scan_components` (`diat:158`) incluye componentes que **no existen en la ref objetivo** → instalación de componentes de otra ref etiquetada como "ref beta".
- **Fix:** antes del bucle de `download_and_stage`, `shutil.rmtree` de todas las `paths.COMPONENT_DIRS` del caché (o borrar el caché completo preservando `.sha/.ref/.version/instalacion.json`).

### M-02 — `--status`/`--list` comparan el sha del proyecto contra la ref del ENV → falsos "desactualizado" al cambiar de canal
- **Ubicación:** `INSTALACION/diat:261` + `diat:265-268` (`_status_project`), `INSTALACION/diat:292` + `diat:303-306` (`cmd_list`), `INSTALACION/diat:233` + `diat:242-245` (`_status_system`)
- **Escenario:** proyecto instalado desde `main` (sha S1). Usuario con `DIAT_REF=v0.18.1-test` ejecuta `diat --status /ruta` → `get_remote_sha()` usa la ref del env (`github.py:87`) → sha S2 de beta → "⚠️ desactualizado (S1 → S2)" en **todos** los proyectos aunque nada cambió en `main`. `inst.get('ref')` (`diat:257`) se muestra pero no se usa en la comparación. Ídem `cmd_list` marca todos "desactualizado" y `--version`/`--list` no distingue "cambio de canal" de "hay updates".
- **Fix:** `remote_sha = github.get_remote_sha(ref=inst.get('ref', paths.DEFAULT_REF))` en ambos; en `_status_system`, si `ref_cache != ref` imprimir "cambio de canal pendiente" y usar `get_remote_sha(ref=ref_cache)` para el estado de sha.

### M-03 — Sin podado: reinstalar sobre otro ref mezcla componentes y etiqueta todo con UNA ref/sha
- **Ubicación:** `INSTALACION/diat:184-187` (+ `instalar.py:31-33` solo sobrescribe, nunca borra ausentes)
- **Escenario:** proyecto instalado con 15 skills de `main`; se reinstala con ref beta que tiene 10 (5 renombradas) → `install_component` sobrescribe/crea pero **no elimina** las 5 viejas → disco mixto main+beta. `registro.save_installation` fusiona `selection`/`components` (`registro.py:64-67`) → registro declara UN `ref`/`sha` para la unión de dos canales → `--status` muestra componentes que no pertenecen a esa ref.
- **Fix:** en `cmd_install`, tras instalar, calcular `stale = prev_components - nuevos_por_ref` y ofrecer borrado (o borrado silencioso con aviso), y en `_merge_dict` de components no fusionar cuando cambió la ref de la instalación previa.

### M-04 — `SAC_SKILLS` hardcodeada en el CLI → "Team Dev SAC" parcial según ref
- **Ubicación:** `INSTALACION/diat:29-37`, consumo en `diat:116`
- **Escenario:** ref beta renombra `validar-hu` o no incluye `init-reglas-arquitectonicas` → el filtro `if s in catalog.get("skills", set())` descarta **silenciosamente** → "Team Dev SAC" instala un stack incompleto sin ningún aviso (el usuario cree que tiene la metodología completa). Recíproco: skills SAC nuevas en la ref jamás entran en team_sac.
- **Fix:** generar en CI un fichero `sac_skills.json` dentro del repo (viaja con la ref) y que `team_sac` lo lea del cache, con `set(SAC_SKILLS) - catalog` como *warning* explícito de faltantes.

### M-05 — Layout hardcodeado local: `KeyError` y catálogo vacío ante cambios de la ref
- **Ubicación:** `INSTALACION/diatlib/instalar.py:24` (`paths.COMPONENT_LAYOUT[ctype]`), con `diat:158` (scan con marcadores locales)
- **Escenario:** (a) la ref cambia el marcador (p. ej. `workflow.md` → `flow.md`) o mueve `agents/` a subcarpetas → `build_catalog`/`scan_components` no ven nada → menús "No hay X disponibles" (`diat:78`) o errores C-01 con catálogo vacío, siendo que el caché está lleno; (b) un grafo (local o manifiesto futuro) referencie un ctype no listado — p. ej. `"config"` (existe en `COMPONENT_DIRS` pero NO en `COMPONENT_LAYOUT`) → `KeyError` crudo en `instalar.py:24` → traceback sin UX.
- **Fix:** `kind, spec = paths.COMPONENT_LAYOUT.get(ctype)` con `if not kind: print_warning(...); return False`; añadir al final de `ensure_cache` un sanity-check: si `COMPONENT_DIRS` del caché tiene carpetas no contempladas por `COMPONENT_LAYOUT`, warn "ref introduce tipos nuevos no soportados por este CLI".

### M-06 — Omisión silenciosa + mensaje de éxito igual
- **Ubicación:** `INSTALACION/diatlib/instalar.py:28-30, 36-38` (return False con warning) con `INSTALACION/diat:189-190`
- **Escenario:** cualquier componente no encontrado en caché (M-01/M-05, o `reinstall_components` de `update` con seeds de ref vieja) → "omitido" en scrolling, y luego **`print_success("Instalado en ...")` + "N componentes"** igualmente; si todo se omite: "Instalado en … 0 componentes". Además `selection` (`diat:183`) guarda la seed como si se instalara → `--update` la reintenta para siempre.
- **Fix:** en `cmd_install`, si `not installed` o `len(installed) < len(seeds)`, imprimir warning con la lista de `seeds - installed` y no usar `print_success`; guardar en `selection` solo lo realmente instalado.

### M-07 — Config SAC preservada al pie de la letra → esquema de ref viejo marcado como ✅
- **Ubicación:** `INSTALACION/diatlib/instalar.py:63-65` (solo copia ficheros nuevos) y `instalar.py:67-68` (`already → return True`), efecto en `instalar.py:186-187` y `diat:277-278`
- **Escenario:** la ref beta añade claves nuevas a `CONFIG_SYSTEM.yaml`/nuevos `.yaml` → los ficheros existentes jamás se actualizan (solo se copian inexistentes) → runtime SAC corre con schema de otra ref; `installed["config"]=True` → `--status` del proyecto dice `config: ✅` → mensaje confuso. Además el placeholder `{project-root}` solo se resuelve en config nueva (`instalar.py:70-74`).
- **Fix:** separar `CONFIG_USER.yaml` (preservar siempre) del resto (sobrescribir con backup `.bak` si cambió el sha del origen); añadir a `install_sac_config` detección de claves nuevas en el yaml destino vs origen y warn.

### M-08 — Assets compartidos: `memory_skill.json` viejo preservado contra skills nuevas
- **Ubicación:** `INSTALACION/diatlib/instalar.py:145-146` (`if target.exists(): continue`)
- **Escenario:** la ref cambia el esquema de `memory_skill.json` (o de `references/`) → la skill nueva se copia, el asset viejo se conserva por "guardar estado runtime" → la skill nueva rompe en runtime con fichero de schema ajeno. Ídem dirs completos (`copytree` solo si no existe, `instalar.py:149-150`).
- **Fix:** versionar el asset: si el destino existe y el origen tiene un hash/schema-version distinto, copiar a `*.bak` y sobrescribir (preservar solo campos de estado, no estructura).

### M-09 — `LEGACY_REPLACED` vive en el CLI local
- **Ubicación:** `INSTALACION/diatlib/instalar.py:158-170`
- **Escenario:** la ref beta introduce su propia migración (p. ej. renombra `plugins/workflow-sac/index.ts` o retira un command) → el CLI local solo sabe borrar `tools/workflow-sac.ts` → artefactos V1 de refes antiguas quedan **mezclados** con V2 (OpenCode V2 ignora los `.ts`, pero quedan muertos en el repo). Recíproco: si la ref ya no trae el plugin, el CLI local borra el legacy igual (inofensivo pero engañoso: "legado eliminado" por un componente que ya no existe).
- **Fix:** mover `LEGACY_REPLACED` a un fichero `migrations.json` en el repo (viaja con la ref) y ejecutar la lista de la ref descargada, no la del CLI.

### M-10 — `--version` informa el tag semver más alto de `main`, ignorando el canal y sin parsear prereleases
- **Ubicación:** `INSTALACION/diat:334-339` (lee `.version` escrito por `update.py:54-56` desde `github.get_remote_version`, `github.py:107-134`)
- **Escenario:** con `DIAT_REF=v0.18.1-test`, `get_remote_version` hace `parse("0.18.1-test")` → `int("1-test")` → `ValueError` → tag descartado (`github.py:123-134`) → `.version` = tag más alto de la rama principal → el usuario en canal beta ve "DIAT — ia-dev-toolkit v0.18.0" mientras ejecuta código 0.18.1-test (o al revés tras `--update` en beta). El `__version__` local de `diatlib/__init__.py` ni se consulta → CLI y versión mostrada pueden divergir siempre.
- **Fix:** en `cmd_version`, si `paths.get_ref() != DEFAULT_REF`, imprimir `f"v{version} (canal: {ref})"` usando también la ref cacheada (`.ref`); y en `get_remote_version` filtrar/soportar tags con sufijo `-test` (`re.match(r"v?(\d+)\.(\d+)\.(\d+)")`).

### M-11 — Sonda de validez del caché = "existe `skills/`"
- **Ubicación:** `INSTALACION/diat:54` (`have = (cache / "skills").exists()`) y `diat:65-67`
- **Escenario:** (a) ref sin `skills/` (o `COMPONENT_DIRS` futuro renombrado) → la condición `not have` es siempre true → re-descarga en **cada** ejecución aunque sha y ref coincidan; (b) offline con ese caché → error falso "No hay componentes en cache y no hay conexión" con un caché perfectamente válido para otros tipos.
- **Fix:** `have = any((cache / d).exists() for d in paths.COMPONENT_DIRS)`.

### M-12 — `RECURSIVE_TYPES` es subconjunto local: deps de plugins/commands/tools jamás se resuelven
- **Ubicación:** `INSTALACION/diatlib/deps.py:11` (import de `paths.RECURSIVE_TYPES`), corte en `deps.py:109` (`if ntype in RECURSIVE_TYPES`)
- **Escenario:** si la ref necesita `plugins:workflow-sac → tools:workflow-sac` o un command con deps propias, `visit` no desciende (`deps.py:109`) → instalación incompleta silenciosa; análogamente, si la ref define un tipo recursivo nuevo (p. ej. `memories`), el CLI local nunca seguirá sus `requires`. Los seeds de tipo no-recursivo se instalan "a pelo".
- **Fix:** recorrer `requires` para **todo** ctype presente en `dependencies` (quitar el filtro `RECURSIVE_TYPES` del DFS, dejándolo solo como guard de seguridad si se prefiere), o derivarlo del manifiesto de la ref (ver C-02).

## 🟡 LOW

- **B-01 — `INSTALACION/diat:237` y `diat:257`:** fallback `or "main"` / `.get('ref', 'main')` hardcodeado en vez de `paths.DEFAULT_REF` → si cambia el canal por defecto, los registros pre-canal se reportan con la ref equivocada. Fix: `paths.DEFAULT_REF` en ambos.
- **B-02 — `INSTALACION/diat:242-245`:** si `local_sha == remote_sha` pero `ref_cache != ref` (2 ramas en el mismo commit), imprime "⚠️ hay actualización (abc1234 → abc1234)" — sha idénticos, mensaje sin sentido. Fix: rama propia para `ref_cache != ref` → "cambio de canal: {ref_cache} → {ref}".
- **B-03 — `INSTALACION/diatlib/deps.py:71, 97, 130`:** `dependencies = dependencies or COMPONENT_DEPENDENCIES` impide desactivar la validación pasando `{}` (diccionario vacío es falsy) → un caller que quiera validar/resolver "sin grafo" recibe el grafo por defecto. Fix: `if dependencies is None: dependencies = COMPONENT_DEPENDENCIES`.
- **B-04 — `INSTALACION/diat:186-187`:** si `ensure_cache` no descargó porque `get_installed_sha()` era `None` (primer caché heredado), `save_installation(sha=None)` escribe `sha: null` → `--status` mostrará "desactualizado (? → xxx)" para siempre. Fix: si `sha is None`, saltar el flag de estado o regenerarlo desde `.sha`.
- **B-05 — `INSTALACION/diatlib/instalar.py:33`:** `ignore_patterns("_archived")` es convención hardcodeada del CLI local; si la ref usa otra (p. ej. `.archive/`, `deprecated/`), los obsoletos viajan al proyecto. Fix: mover el patrón a la ref/manifiesto o a `paths.py` con comentario de contrato y test de regresión por ref.
- **B-06 — `INSTALACION/diat:173-176`:** el menú "¿INSTALAR TAMBIÉN? (opcionales)" se alimenta solo del `optional` del grafo local → en canal beta los opcionales nuevos de la ref no aparecen nunca (versión "blanda" de C-02). Fix: mismo manifiesto de C-02.
- **B-07 — `INSTALACION/diatlib/deps.py:85`:** el texto "Dependencias inválidas:" no menciona `DIAT_REF`, la ref activa ni distingue "CLI desactualizado" de "ref rota" → mensaje confuso en el caso KNOWN. Fix: sufijo `f"\n(cli local · ref activa: {paths.get_ref()} · ref caché: {registro.get_installed_ref()}). Si cambiaste DIAT_REF, ejecuta 'diat --update'."`.
- **B-08 — `INSTALACION/diat:158` vs `update.py:71`:** `--install` valida con `scan_components` (filtro `ready`) y `--update` con `build_catalog` (sin filtro) → mismos caché+ref producen validación distinta según comando. Fix: usar `scan_components` en ambos (o validar con `build_catalog` y filtrar solo el menú).

## Resumen
4 críticos (C-01 validación cruzada local↔ref en ambas direcciones — el KNOWN; C-02 deps de ref invisibles al CLI; C-03 auto-update en caliente con código en memoria viejo; C-04 registro envenenado offline), 12 medium y 8 low. El patrón raíz en casi todos: **el CLI local lleva hardcoded grafo (deps.py:26), layout (paths.py:56), skills SAC (diat:29) y migraciones (instalar.py:158) que la ref descargada puede contradecir, sin manifiesto versionado en la propia ref.**
