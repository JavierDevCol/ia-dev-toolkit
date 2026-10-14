# Auditoría 2 — Propagación/gestión de la ref: `update.py`, `registro.py`, `paths.py`, `github.py`, bootstraps

> Auditoría delegada a subagente explore (solo lectura) — 2026-10-13, rama `feature/mejoras-plugin-workflow-sac`.
> Ficheros leídos íntegros: `update.py`, `registro.py`, `paths.py`, `github.py`, `install.sh`, `install.ps1`, más contexto necesario de `INSTALACION/diat` (CLI: `ensure_cache`, `--status`, `--list`, `cmd_install`), `instalar.py`, `deps.py` y `desinstalar.py`.

## 🔴 CRÍTICOS

### C-1 — `INSTALACION/diatlib/update.py:97-104` — `--update` en lote reescribe la ref de TODOS los proyectos a la del env
- Escenario: 5 proyectos instalados desde `main`. El usuario prueba algo con `DIAT_REF=v0.20-test diat --update` → se re-descarga el caché del canal de prueba y **todos** los proyectos se reinstalan con ese contenido y quedan registrados con `inst["ref"] = "v0.20-test"` (línea 104). Al día siguiente, un `diat --update` sin env los vuelve a pisar a `main` (y viceversa): los proyectos no tienen canal propio, lo decide el env de la última invocación.
- Fix: en el bucle, si `inst.get("ref")` difiere de `ref` y no hay ruta explícita, instalar usando la ref persistida del proyecto (`github.download_and_stage` por-ref) o pedir confirmación antes de migrar de canal; nunca reetiquetar `inst["ref"]` sin consentimiento.

### C-2 — `INSTALACION/diat:55-56,65-67` + `INSTALACION/diat:186-187` — Instalación offline/rate-limit registra una ref que no es la del contenido
- Escenario: `DIAT_REF=feature/x diat --install /p` sin conexión (o con límite de API). `get_remote_sha()` devuelve `None` → `ensure_cache` no descarga, **sin ningún aviso** (el `elif not have` solo falla si no hay caché), devuelve el caché viejo de `main`, y `cmd_install` llama `save_installation(...)` sin `ref` → `registro.py:74` graba `ref="feature/x"`, `sha=` el `.sha` de `main`. Resultado persistente: proyecto declarado en `feature/x` con bytes de `main` y sha ajeno.
- Fix: si `remote_sha is None`, registrar `ref=registro.get_installed_ref()` (ref real del snapshot) y sha del caché, o abortar la instalación cuando `paths.get_ref() != registro.get_installed_ref()` sin verificación remota.

### C-3 — `INSTALACION/diat:260-268` (`_status_project`) — Compara el sha del proyecto contra el sha remoto del ref del ENTORNO, no contra su propia ref
- Escenario: proyecto instalado desde `main` (sha S_main). `DIAT_REF=feature/x diat --status /p` → `github.get_remote_sha()` (línea 261, sin `ref=`) resuelve feature/x → "⚠️ desactualizado (S_main → S_fx)" falso, aunque en `main` esté al día. El campo `ref` del proyecto se muestra (línea 257) pero no se usa.
- Fix: `remote_sha = github.get_remote_sha(ref=inst.get("ref", paths.DEFAULT_REF))` — `github.py:81` ya acepta `ref`.

### C-4 — `INSTALACION/diat:292,303-306` (`cmd_list`) — Mismo error en lote
- Escenario: con `DIAT_REF=vX-test diat --list`, todos los proyectos registrados en `main` se marcan "⚠️ desactualizado" porque se comparan contra el sha remoto de vX-test. Ruina la utilidad del listado mientras se prueba un canal.
- Fix: mismo que C-3 (sha remoto por `inst["ref"]`), o mostrar el canal por proyecto y comparar solo dentro del mismo canal.

### C-5 — `INSTALACION/diatlib/update.py:54-56` — `.version` se guarda ANTES de cualquier validación o descarga (y de las salidas tempranas)
- Escenario A: `DIAT_REF=v0.9.0-test diat --update /ruta-no-registrada` → línea 56 escribe `.version` = tag más alto del repo, luego línea 63 aborta por "no registrado": cache/CLI viejos pero `diat --version` (diat:335) muestra la versión nueva. Escenario B: `validate_dependencies` falla (líneas 73-76) → mismo desfase versión/caché. Escenario C: `download_and_stage()` lanza `DownloadError` **sin try/except** (ver M-1) tras haber escrito `.version` → traceback y versión falsa.
- Fix: mover `save_installed_version` al final del branch de descarga exitoso (tras línea 79), y envolver la descarga en try/except.

## 🟠 MEDIUM

### M-1 — `INSTALACION/diatlib/update.py:70` — `DownloadError` no capturado en `--update`
- Escenario: red inestable durante `github.download_and_stage()` → `github.py:53` lanza `DownloadError` y, a diferencia de `ensure_cache` (`diat:58-62`), `cmd_update` no lo captura → traceback crudo para el usuario (y `.version` ya guardado, C-5).
- Fix: `try: cache = github.download_and_stage() except github.DownloadError as e: ui.print_error(str(e)); return`.

### M-2 — `INSTALACION/diatlib/update.py:97` — El skip "Al día" compara solo sha, no ref
- Escenario: proyecto en `main` con sha S; `DIAT_REF=feature/x` apunta al mismo commit S (rama recién cortada desde main, o tag en HEAD de main). `--update` con el canal de prueba: caché y `.ref` pasan a feature/x, pero el proyecto se salta ("Al día") y su `inst["ref"]` queda `"main"` → el registro de proyectos y el caché declaran canales distintos para el mismo contenido.
- Fix: `if inst.get("sha") == remote_sha and inst.get("ref", paths.DEFAULT_REF) == ref:` — si solo cambia la ref, forzar reetiquetado/reinstalación.

### M-3 — `INSTALACION/diat:237-245` — `--status` asume "main" como ref del caché y emite "hay actualización (shaA → shaA)"
- Escenarios: (a) `.ref` ausente (snapshots previos al soporte de canales, o tras bootstrap) → `ref_cache = ... or "main"` afirma "Ref: main → feature/x" sin fundamento; (b) sha local == sha remoto pero ref distinta → la condición de la línea 242 falla por la ref y la línea 245 imprime `⚠️ hay actualización (abc1234 → abc1234)`: aviso falso con el mismo sha a ambos lados.
- Fix: tres estados distintos: "al día (sha coincide)", "cambio de canal pendiente (mismo sha)" y "hay actualización"; y `ref_cache = registro.get_installed_ref() or "desconocida"`.

### M-4 — `INSTALACION/bootstrap/install.sh:71-77` e `install.ps1:52-58` — El bootstrap cambia el CLI de canal pero nunca toca el estado del caché
- Escenario: usuario existente ejecuta `curl ... | DIAT_REF=vX-test bash` → el CLI en bin pasa a ser el de vX-test, pero no se escribe `.ref`, `.sha`, `.version` ni se tocan los componentes → conviven CLI de vX-test + componentes de `main` + `.ref` que dice "main" (o ausente). `diat --version` dirá "versión desconocida, ejecuta diat --update" (diat:339) aunque acaba de instalar desde un tag.
- Fix: al final del bootstrap, persistir `$REF` en `$CACHE/.ref` (y `.version` si la ref es un tag), y avisar/comandar `diat --update` para resincronizar componentes.

### M-5 — `INSTALACION/diatlib/paths.py:23-32` — Cero validación de formato de `DIAT_REF`
- Escenario: `DIAT_REF="v1 beta"`, `"feature/x?foo"`, `"main#x"` o `"../../etc"` → `get_remote_sha` (github.py:88) construye una URL inválida → HTTPError no-404/422 o excepción → `return None` → el usuario ve "No se pudo obtener la versión remota" / "sin conexión" en vez de "ref inválida"; en el bootstrap, `curl | tar` muere con un error críptico de tar (install.sh:58). El comentario de paths.py:24 promete "commit" como ref, pero nada valida longitud hex vs. nombre de rama.
- Fix: en `get_ref()`, validar `re.fullmatch(r"[A-Za-z0-9._\-]+(/[A-Za-z0-9._\-]+)*", ref)` y fallar con mensaje claro; en install.sh/ps1, pre-chequear existencia (API o `curl -fsSL -o /dev/null -w '%{http_code}'`) y abortar con "La ref '$REF' no existe en el repo".

### M-6 — `INSTALACION/diatlib/github.py:96-104` — 403 (rate-limit) y otros HTTP se confunden con "sin conexión"
- Escenario: API de GitHub sin token limita a 60 req/h (`get_remote_sha` se invoca en install, update, status, list) → 403 → `return None` → `ensure_cache` procede con el caché local **sin avisar** y `cmd_install` registra sha/ref del estado cacheado como si fuera el remoto (agrava C-2); `--status` muestra "⚠️ sin conexión" engañoso.
- Fix: tratar 403/429 aparte: imprimir "rate-limit de GitHub, usando caché local SIN verificar" (y no re-registrar sha/ref de proyectos en ese modo).

### M-7 — `INSTALACION/diatlib/github.py:39,147-153` + `INSTALACION/diatlib/update.py:42,70,77` — Tarball sin anclar al sha + staging no atómico
- Escenarios: (a) rama móvil (`main` o feature activa) avanza entre `get_remote_sha` (update.py:42) y la descarga del tarball por nombre de ref (update.py:70) → el `.sha` persistido (línea 77) **no corresponde** al contenido cacheado; cada `--status` dirá "al día" con contenido de otro commit hasta el siguiente avance; (b) crash/ctrl-C a mitad del reemplazo de carpetas (github.py:147-153) → caché mezcla directorios de dos canales/commits con `.sha`/`.ref` aún antiguos.
- Fix: pedir el tarball por sha exacto (`codeload.github.com/.../tar.gz/<remote_sha>`) cuando se haya resuelto el sha, y staging a `_staging` + rename por directorio (o manifest `cache.meta` con sha/ref validado en `ensure_cache`).

### M-8 — `INSTALACION/diatlib/paths.py:32` (env efímera) + `INSTALACION/diat:231,238` + `INSTALACION/diatlib/update.py:50-52` — El canal no es fijable: estado persistente + canal volátil
- Escenario: no existe forma de persistir "uso el canal feature/x"; `.ref` solo se escribe como *consecuencia* de una descarga. El usuario que instala con `DIAT_REF=x` y luego olvida la env en cualquier `--update` es migrado silenciosamente a main (y viceversa, C-1). `--status` muestra "canal de prueba" solo según el env (diat:238), no según lo que está realmente instalado.
- Fix: política explícita — p. ej. `get_ref()` usa `.ref` como default cuando la env no está definida, más un `diat --channel <ref>` que ancla el canal con confirmación.

### M-9 — `INSTALACION/diat:54` + `INSTALACION/diatlib/github.py:147-153` — Integridad del caché validada solo con `skills/`
- Escenario: un solo caché compartido por canales; si el reemplazo por carpetas falla a mitad, o el usuario borra `workflows/`/`plugins/`, `have = (cache/"skills").exists()` sigue `True` → `ensure_cache` devuelve un caché incompleto/mixto y `install_component` (instalar.py:28-30,36-38) omite componentes con un warning por archivo, sin re-descarga.
- Fix: comprobar las 7 `paths.COMPONENT_DIRS` (o un manifest sha/ref por dir) antes de dar el caché por válido; re-descargar si falta alguna.

### M-10 — `INSTALACION/diatlib/update.py:102-104` + `INSTALACION/diatlib/registro.py:42-51,66` — Seeds de una ref que no existen en otra desaparecen sin trazabilidad
- Escenario: `selection` fusiona historial (registro.py:42-51), pero si se cambia de canal a una rama donde una skill/seed seleccionada no existe, `reinstall_components` → `install_component` la omite ("no está en cache — omitido") y `update.py:102` **reemplaza** `inst["components"]` → el proyecto queda con menos componentes sin aviso agregado, y `selection` la conserva para siempre (todo `--update` futuro la reintentará en silencio). El contador final (línea 112) no lo refleja.
- Fix: tras el bucle, cruzar `selection` contra el catálogo de la ref activa e imprimir "N seeds no disponibles en '{ref}': ..." y/o marcar la instalación `incomplete: true`.

## 🟡 LOW

- **B-1 — `INSTALACION/bootstrap/install.sh:10-16` e `install.ps1:8-13` — Constantes y normalización duplicadas respecto de `paths.py:18-32`:** OWNER/REPO/DEFAULT_REF y el trim de la env están duplicados en 3 sitios (sh, ps1, Python); si en `paths.py` cambia `DEFAULT_REF` o el repo, los bootstraps quedan desalineados silenciosamente. Fix: única fuente (p. ej. un `diat.conf`/JSON versionado que consuman ambos) o test de consistencia sh/ps1/Python.
- **B-2 — `INSTALACION/diatlib/registro.py:92-101` vs `:107-116` — Doble fuente de verdad del sha (`.sha` vs `instalacion.json["sha"]`):** si `.sha` se borra a mano (o falla `save_installed_sha` entre las dos escrituras de `update.py:77` y `:108`), `--status` muestra `(?)` y `ensure_cache` re-descarga aunque el json diga que está al día. Fix: `get_installed_sha()` con fallback al `"sha"` del json (y viceversa en `_write`).
- **B-3 — `INSTALACION/diatlib/registro.py:96` — El json persiste `version` tomada del código local (`__version__` del snapshot activo):** en canal de prueba, `_write` escribe en el json la versión del código del canal mientras `.version` (fuente de `--version`) contiene otra → dos "versiones instaladas" distintas en disco. Fix: no persistir `version` en el json, o derivarla siempre de `.version`.
- **B-4 — `INSTALACION/diatlib/update.py:51-52`, `INSTALACION/diat:238`, `install.sh:54`, `install.ps1:40` — La lógica "canal de prueba" está duplicada como `ref != "main"` sin normalización:** `DIAT_REF="refs/heads/main"` o `"main "` se anuncia falsamente como canal de prueba en 4 sitios que pueden divergir. Fix: helper único `is_test_channel(ref)` con normalización.
- **B-5 — `INSTALACION/bootstrap/install.ps1:53-54` — `Copy-Item` de `diat.bat` incondicional (el sh lo protege en install.sh:73):** una ref futura sin `diat.bat` aborta la instalación entera en Windows (`$ErrorActionPreference="Stop"`) dejando el bin a medias. Fix: `if (Test-Path ...)` y ordenar el copiado de `diatlib` antes que los launchers.
- **B-6 — `INSTALACION/diatlib/update.py:80-82` — El branch "Cache ya está al día" no revalida la integridad del caché (a diferencia de `ensure_cache`, diat:54):** `.sha`/`.ref` intactos pero dirs borrados parcialmente → `--update` imprime "Cache ya está al día" y la reinstalación masiva omite todo componente ausente. Fix: condicionar el branch a integridad + manifiesto (ver M-9), o delegar en `ensure_cache`.
- **B-7 — `INSTALACION/diat:232-236` — `_status_system` aborta con `return` tras banner parcial cuando la ref no existe:** typo en `DIAT_REF` → `RefNotFoundError` → el estado del sistema queda a medias (banner + cache, sin Ref/Repo/proyectos); la línea "Ref:" ni siquiera se llega a imprimir. Fix: imprimir primero cache/PATH/`Ref: {ref_cache} → {ref} (no existe en el repo)` y continuar con el resto.

## Resumen / patrón raíz
El sistema mantiene **cuatro piezas de estado de canal** (`DIAT_REF` efímera, `.ref` del caché, `inst["ref"]` por proyecto, y el contenido real del caché/bin) sin un único punto de verdad: los bootstraps no escriben `.ref` (M-4), la instalación offline graba refs ajenas (C-2), los skip por sha ignoran la ref (M-2), y status/list comparan contra el ref del entorno en vez del registrado (C-3/C-4). Prioridad sugerida: C-1 → C-2 → C-3/C-4 → M-4/M-8 (persistir el canal como fuente de verdad) → el resto.
