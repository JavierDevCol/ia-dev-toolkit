# Opción 2b — Hotfix sobre una versión entregada

**Cuándo:** Hay una falla en una versión ya desplegada en un ambiente (DES/PRU/PRE/PRO) que no puede esperar a la siguiente entrega desde develop. Si puede esperar → Opción 2a y luego Opción 1 (Regla 3).

**La skill no implementa el fix.** El fix se desarrolla, prueba y revisa antes, en una rama `fix/<desc>` creada desde el tag de la versión con la falla (`fix/*` no dispara el pipeline). La skill lo recibe, lo empaqueta como `hotfix/vX.Y.Z` y lo entrega.

**Referencias:** `references/checklist-entrega.txt` · `references/resumen-entrega.txt` (variante HOTFIX)

**Inputs (pedir/validar antes de empezar):**
- `nombre_repo` del repositorio.
- Ambiente donde se detectó la falla: DES, PRU, PRE o PRO.
- Descripción del bug y WI asociado.
- Origen del fix: **(a)** rama `fix/<desc>` creada desde el tag base, o **(b)** SHA de commits que ya están en develop. Sin fix todavía → el paso 3 lo indica y detiene.

**Placeholders de esta opción:** `vBASE` = versión con la falla (paso 1) · `vX.Y.Z` = versión del hotfix, PATCH+1 de `vBASE` (paso 2) · `<sha>` = commit del hotfix (paso 3).

**Valores fijos:**

| Placeholder | Valor |
|---|---|
| `{ado_base}` | `https://dev.azure.com/GestionRequerimientos/BancaPorWhatsappCICD` (organización/proyecto de ADO; base de toda llamada REST) |

**Outputs** (en `{output_documentacion}/entrega_release/{nombre_repo}/vX.Y.Z/`):
- `release-notes.md`, `checklist-entrega_vX.Y.Z.txt`, `resumen-entrega_hotfix_vX.Y.Z.txt`
- Rama `hotfix/vX.Y.Z` en `origin`, creada una sola vez sobre `<sha>` y bloqueada (`isLocked = true`). El tag `vX.Y.Z` y la imagen `{nombre_ms}:X.Y.Z` los crea el **pipeline** — CEIBA nunca crea tags.
- 4 PR `hotfix/vX.Y.Z → des, pru, prepro, main` **en borrador** (los publica el banco) y 1 PR **activo** `hotfix/vX.Y.Z → develop`.

**Confirmaciones del usuario:** ✋ versión base (paso 1) · ✋ fix completo y revisado (paso 4) · ✋ push y bloqueo (paso 5) · ✋ 4 PR en borrador (paso 7) · ✋ PR a develop (paso 8) · ✋ cierre del checklist (paso 10).

## Ejecución por pasos (obligatorio)

Cada paso vive en su propio archivo de esta carpeta. **Cargar un solo archivo de paso a la vez**, ejecutarlo completo y cargar el siguiente **solo** cuando se cumpla la condición de su línea **Siguiente**. Nunca leer, anticipar ni adelantar trabajo de un paso posterior mientras el actual espera un resultado (pipeline, sub-agente o respuesta del usuario).

| Paso | Archivo |
|---|---|
| 1 | `paso_uno.md` — Versión base |
| 2 | `paso_dos.md` — Versión del hotfix y prechequeos |
| 3 | `paso_tres.md` — Recibir y validar el fix |
| 4 | `paso_cuatro.md` — Confirmar fix completo y release notes |
| 5 | `paso_cinco.md` — Push y bloqueo de hotfix/vX.Y.Z |
| 6 | `paso_seis.md` — Esperar y analizar el pipeline |
| 7 | `paso_siete.md` — Crear los 4 PR en borrador |
| 8 | `paso_ocho.md` — PR hotfix → develop |
| 9 | `paso_nueve.md` — PR de versiones anteriores |
| 10 | `paso_diez.md` — Checklist de entrega |
| 11 | `paso_once.md` — Resumen y correo |

**Siguiente:** cargar `paso_uno.md`.
