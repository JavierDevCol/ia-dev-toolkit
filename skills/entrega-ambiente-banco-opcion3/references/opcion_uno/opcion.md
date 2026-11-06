# Opción 1 — Entregar versión desde DEVELOP

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado.

**Referencias:** `references/checklist-entrega.txt`

**Inputs (pedir/validar antes de empezar):**
- `nombre_repo` del repositorio que se entrega.
- La versión `vX.Y.Z` **no** se pide aquí: se calcula y confirma en el paso 2 (necesita `vPREV`).

**Valores fijos de la Opción 1:**

| Placeholder | Valor |
|---|---|
| `{ado_base}` | `https://dev.azure.com/GestionRequerimientos/BancaPorWhatsappCICD` (organización/proyecto de ADO; base de toda llamada REST) |

**Outputs** (en `{output_documentacion}/entrega_release/{nombre_repo}/{version}/`):
- `release-notes.md`, `checklist-entrega_vX.Y.Z.txt`, `resumen-entrega_release_vX.Y.Z.txt`
- Rama `release/vX.Y.Z` en `origin`, creada una sola vez sobre el commit validado. La skill la bloquea (`isLocked = true`) al crearla. El tag `vX.Y.Z` y la imagen `{nombre_ms}:X.Y.Z` los crea el **pipeline de release** — CEIBA nunca crea tags.
- 4 PR `release/vX.Y.Z → des, pru, prepro, main` **en borrador** en ADO, creados tras el pipeline de release OK. Los publica el banco.

**Confirmaciones del usuario:** ✋ versión en el paso 2 · ✋ OK para crear y bloquear la rama · ✋ OK para crear los 4 PR en borrador · ✋ cierre del checklist como estado real.

## Ejecución por pasos (obligatorio)

Cada paso vive en su propio archivo de esta carpeta. **Cargar un solo archivo de paso a la vez**, ejecutarlo completo y cargar el siguiente **solo** cuando se cumpla la condición de su línea **Siguiente**. Nunca leer, anticipar ni adelantar trabajo de un paso posterior mientras el actual espera un resultado (pipeline, sub-agente o respuesta del usuario).

| Paso | Archivo |
|---|---|
| 1 | `paso_uno.md` — Verificar develop y fijar <sha> |
| 2 | `paso_dos.md` — Versión anterior y versión de la entrega |
| 3 | `paso_tres.md` — Release notes |
| 4 | `paso_cuatro.md` — Prechequeos |
| 5 | `paso_cinco.md` — Crear y bloquear release/vX.Y.Z |
| 6 | `paso_seis.md` — Esperar y analizar el pipeline de release |
| 7 | `paso_siete.md` — Crear los 4 PR en borrador |
| 8 | `paso_ocho.md` — PR de versiones anteriores |
| 9 | `paso_nueve.md` — Checklist de entrega |
| 10 | `paso_diez.md` — Resumen y correo |

**Siguiente:** cargar `paso_uno.md`.
