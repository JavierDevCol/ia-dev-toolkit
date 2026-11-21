# Design — Memoria SAC en email-composer (archivado de correos generados)

- **Fecha:** 2026-11-21
- **Rama:** `fix-email-composer-hardening` (worktree `~/Documentos/squad-skills-fix-email-composer-hardening`)
- **Tamaño:** cambio pequeño — design doc corto.

## Intento y por qué

`email-composer` genera el HTML de un correo y lo devuelve en el chat; nada persiste. Se integra la memoria SAC del ecosistema (`sac.json` vía `memctl`) para que la skill sepa **dónde archivar los correos que genera**: bajo `{documentacion_sac_path}/correos_salientes/`, con las convenciones ya establecidas por las skills archivadoras del repo.

## Goals

- Leer `{documentacion_sac_path}` con el contrato memctl estándar (bloque `## Configuración` literal en SKILL.md).
- **Al generar** el correo (opción A elegida), guardar el HTML en `{documentacion_sac_path}/correos_salientes/` (crear la subcarpeta si no existe) y reportar la ruta en el chat.
- Nombre de archivo `correo_{asunto-slug}_{fecha}.html` con fecha ISO (`YYYY-MM-DD`).
- Helper `save_email()` en `build_email_html.py`, cubierto con tests TDD.

## Non-goals

- No enviar correos ni crear borradores (contrato vigente de la skill, sin cambios).
- No índice persistente de lo archivado (convención del repo: reportar la ruta al finalizar).
- No sección propia en `sac.json` — solo se lee `documentacion_sac_path`.
- No guardar el resumen en texto plano (sigue viviendo en el chat).

## Anti-goals

- **Nunca bloquear la generación del correo** por falta de SAC o de config: el HTML se entrega igual y se avisa que no se archivó.
- **Nunca escribir fuera de `{documentacion_sac_path}`** (frase de contrato del ecosistema).

## Constraints (investigadas en el repo)

- Fila literal `| \`{documentacion_sac_path}\` | \`sh .SAC/memctl.sh get documentacion_sac_path\` |` + frase canónica de fallback: memctl ausente (exit 127) → leer `.SAC/config/sac.json` con `jq`; exit 1 (JSON inválido) → detenerse y avisar, no editar a mano; `null`/vacío/exit 2 → "No hay instalación SAC"; nunca inventar ni recalcular rutas ("su salida ES el valor").
- `INSTALACION/tests/test_repo_sin_legado.py` exige que todo placeholder se mapee a su comando memctl — el bloque debe seguir el patrón literal o la suite del repo falla.
- Subcarpetas de salida: dos palabras snake_case en español (estilo `auditoria_seguridad/`, `calidad_codigo/`, `config_entorno/`, `handoff_release/`), con la frase "(crear la subcarpeta si no existe; nunca escribir fuera de `{documentacion_sac_path}`)".
- Reporte final tipo `✅ ... | Ruta: [ruta]` (estilo `sac-crear-adr`).

## Approaches

- **A · Guardar al generar (ELEGIDA):** el HTML se archiva en el Step 3 (Deliver) y se reporta la ruta. Consistente con el patrón de todas las skills archivadoras del repo y con el objetivo declarado ("saber dónde guardar los correos **generados**").
- B · Guardar al confirmar el envío: descartada — añade un paso de interacción, el archivo puede quedar sin guardar nunca, y la skill nunca envía (el nombre `correos_enviados/` exigiría esa confirmación para no mentir).
- Nombre de carpeta: **`correos_salientes/` (ELEGIDO)** — preciso (lo que sale), no afirma envío, calza con la convención de dos palabras. Descartados: `correos/` (vago), `correos_enviados/` (solo válido con B), `comunicaciones/` (colisiona con el tipo `comunicado` del propio skill).

## Decisiones del builder (mis llamadas)

- Solo se guarda el HTML; el resumen en texto plano se muestra en el chat como hoy.
- `save_email(html, dest_dir, filename)` en `build_email_html.py`: crea `dest_dir` si no existe (`mkdir -p` semántica), escribe UTF-8, devuelve la ruta final; validaciones `ValueError`/`TypeError` en línea con el endurecimiento existente.
- SKILL.md: nuevo bloque `## Configuración` (patrón de `chat-equipo`) + en Step 3, tras mostrar HTML+resumen, el paso de archivado con resolución memctl.
- Slug del asunto: minúsculas, no-alfanuméricos → `-`, truncado a ~60 chars.
- Fallback: sin instalación SAC o sin clave → entregar el HTML + aviso "No hay instalación SAC / no archivado"; nunca abortar el correo.
- TDD: tests de `save_email()` (creación de dir, contenido, ruta devuelta) y test de contrato de docs (bloque memctl literal presente); suite existente (29) se mantiene verde.
- Este design doc se commitea junto con la implementación en la misma rama.

## Lo que queda al builder

- Copiar la frase canónica de fallback literalmente desde `sac-tomar-contexto/SKILL.md:89` (idéntica en las skills del repo).
- Formato exacto del reporte final `✅`.
