---
name: ado-pr-reviewer
description: >
  Revisión de Pull Requests en Azure DevOps con validación contra estándares de
  codificación del equipo (coding-standards.md y architecture_[repo].md). Analiza
  cambios de código via git diff, conflictos de merge, threads pendientes y
  cumplimiento de estándares sobre las líneas modificadas. Genera reporte
  estructurado con hallazgos y acciones: aprobar, comentar, rechazar, o cancelar
  con registro de pendiente. Usa esta skill cuando el usuario quiera revisar un
  PR, hacer code review, analizar un Pull Request, validar estándares en un PR,
  o verificar conflictos. También activa cuando mencione: revisar PR, code
  review, análisis de PR, PR review, validar PR, pendientes de PR, pull request,
  PR ID, PR link. Also triggers on: review pull request, PR analysis, check
  coding standards, merge conflicts.
compatibility: Requires Azure DevOps MCP server configured
---

# ADO PR Reviewer

Revisión estructurada de Pull Requests con validación contra estándares del equipo y registro de revisiones pendientes.

## Contexto del perfil activo

Esta skill recibe del agente orquestador el contexto ya resuelto:
- `project_name` — proyecto ADO resuelto desde `project_map.repos`
- `user_email` — email del revisor (perfil activo)
- `base_reports_path` — ruta base de reportes

La skill **no lee `config_consultas.json` directamente**. Todo el contexto es inyectado por el agente.

Si el contexto no fue pasado, solicita al usuario que re-invoque desde el agente principal.

Los estándares del equipo se encuentran en:
- `/Users/javier.garcia/Documents/BMM/BANCA_X_WHATSAPP/Doc_BancaPorWhatsapp/docs/architecture/coding-standards.md` — estándares principales
- `/Users/javier.garcia/Documents/BMM/BANCA_X_WHATSAPP/Doc_BancaPorWhatsapp/docs/architecture/architecture_[nombre_del_repo].md` — guía de arquitectura específica del repositorio del PR

## Estándar de rutas

Los reportes de PR se generan en la carpeta del **autor del PR** (no del revisor):

| Concepto | Patrón |
|----------|--------|
| Ruta Base Autor | `[base_reports_path]/[project_name]/[autor_pr_email]/` |
| Ruta Reviews Autor | `[Ruta Base Autor]/pr_reviews/` |
| Reporte PR | `review_PR_[PR_ID]_[timestamp].md` |
| Ruta Pendientes Revisor | `[base_reports_path]/[project_name]/[user_email]/pr_reviews/` |
| Registro pendientes | `pending_reviews.json` |

- **`autor_pr_email`** = `createdBy.uniqueName` del PR (se obtiene en Fase B).
- **`pending_reviews.json`** vive en la carpeta del **revisor** (`user_email`), porque es SU lista de pendientes.
- El campo `revisado_por` dentro del reporte traza quién hizo la revisión.

---

## Comando: REVISAR-PR [PR_ID_o_URL]

### Fase A — Resolución de entrada

1. **Parsear input:**
   - **Número puro** (ej. `12345`): tratar como `pullRequestId`.
   - **URL de ADO** (contiene `_git/` y `pullrequest/`): extraer `repositoryName` y `pullRequestId` del path.
2. **Resolver repositorio:**
   - Si se tiene el nombre del repo (de URL), invocar `ado/repo_get_repo_by_name_or_id` para obtener el `repositoryId`.
   - Si solo hay PR ID numérico, invocar `ado/repo_list_pull_requests_by_repo_or_project` con `project_name` y status `All` para localizar el PR y su `repositoryId`.
3. **Obtener PR:**
   - Invocar `ado/repo_get_pull_request_by_id` con `repositoryId`, `pullRequestId`, `includeWorkItemRefs = true`.
   - Si el PR no existe o no pertenece al proyecto activo → informar al usuario y detener.

### Fase B — Extracción de datos del PR

**B.1 — Metadatos del PR** (desde `get_pull_request_by_id`):
- Título, descripción, autor (`createdBy.displayName` y `createdBy.uniqueName`)
- Ramas: `sourceRefName` → `targetRefName` (limpiar prefijo `refs/heads/`)
- Estado: `status`, `mergeStatus`
- Work Items vinculados
- Fecha de creación (calcular antigüedad en días)

**B.2 — Threads y discusiones:**
Invocar `ado/repo_list_pull_request_threads` y clasificar:
- Threads `Active` o `Pending` → discusiones **sin resolver**
- Threads `Fixed`, `Closed`, `WontFix` → discusiones **resueltas**
- Filtrar threads de sistema (push notifications, policy checks) — solo contar los de autoría humana.

**B.3 — Commits del PR:**
Invocar `ado/repo_search_commits` filtrando por la rama origen para identificar los commits incluidos en el PR. Extraer: hash corto, mensaje, autor.

**B.4 — Diff de cambios del PR (git local):**

El agente tiene acceso directo al repositorio. Ejecutar en terminal:

```bash
# 1. Actualizar referencias remotas de ambas ramas
git fetch origin [target_branch] [source_branch]

# 2. Lista de archivos modificados por el PR (solo nombres y tipo de cambio)
git diff origin/[target_branch]...origin/[source_branch] --name-status
```

Esto devuelve el listado con tipo: `A` (added), `M` (modified), `D` (deleted), `R` (renamed).

Para cada archivo modificado o añadido, obtener **solo las líneas cambiadas**:

```bash
# 3. Diff con contexto por archivo (solo líneas +/- con 5 líneas de contexto)
git diff origin/[target_branch]...origin/[source_branch] -U5 -- [ruta/archivo]
```

Almacenar internamente:
- `archivos_tocados[]` — lista con `{path, tipo_cambio, diff_content}`
- Solo guardar diff de archivos de código (filtrar binarios, imágenes, lockfiles).
- Si hay más de 30 archivos tocados, informar al usuario y preguntar si quiere análisis completo o solo archivos críticos.

**B.5 — Detalle de conflictos (si `mergeStatus = conflicts`):**

Si B.1 indica conflictos, obtener detalle sin alterar el working tree:

```bash
# Obtener merge base
git merge-base origin/[target_branch] origin/[source_branch]

# Simular merge para ver conflictos (solo output, no modifica nada)
git merge-tree $(git merge-base origin/[target_branch] origin/[source_branch]) origin/[target_branch] origin/[source_branch]
```

Del output de `merge-tree`, extraer:
- Archivos en conflicto (marcados con `changed in both`)
- Secciones con marcas `<<<<<<<`, `=======`, `>>>>>>>` — el detalle del conflicto

Si `merge-tree` no está disponible (git antiguo), fallback:
```bash
git diff origin/[target_branch]...origin/[source_branch] --check
```
Esto lista conflictos de whitespace y marcadores de merge.

Almacenar: `conflictos[]` — lista con `{path, detalle_conflicto, seccion_afectada}`

**B.6 — Revisión previa pendiente:**
Verificar si existe un registro previo de este PR en `[Ruta Pendientes Revisor]/pending_reviews.json`. Si existe, cargarlo como contexto para la Fase D.

### Fase C — Carga de estándares del equipo

1. Lee `[base_reports_path]/architecture/coding-standards.md`.
2. Determina el nombre del repositorio del PR (obtenido en Fase A).
3. Lee `[base_reports_path]/architecture/architecture_[nombre_del_repo].md`.
4. Consolida las reglas de ambos archivos en un contexto de validación.

Si `coding-standards.md` no existe:
> 🚫 **No se encontró `coding-standards.md` en `[base_reports_path]/architecture/`.**
> **El análisis de estándares no es posible.** Se entregará únicamente un resumen del PR (metadatos, conflictos, threads) sin validación de código.
> Saltar directamente a Fase D con solo D.1 (conflictos) y D.3 (salud general). No ejecutar D.2.

Si `architecture_[nombre_del_repo].md` no existe:
> 💬 **No se encontró guía de arquitectura específica para el repo `[nombre_del_repo]`.** La validación se basará únicamente en `coding-standards.md`.

### Fase D — Análisis

Ejecutar cuatro dimensiones:

**D.1 — Conflictos de merge:**
- `mergeStatus = succeeded` → 🟢 **Sin conflictos**
- `mergeStatus = conflicts` → 🔴 **CONFLICTOS DETECTADOS** — usar detalle de B.5:
  - Listar cada archivo en conflicto con la sección afectada
  - Explicar brevemente la causa probable (ambas ramas tocaron las mismas líneas)
  - Sugerir dirección de resolución si es evidente
- `mergeStatus = queued` → 🟡 **Merge aún no evaluado por ADO**

**D.2 — Validación de estándares sobre el código cambiado:**

Usando `archivos_tocados[]` de B.4 y las reglas de Fase C, analizar **solo el diff** (líneas añadidas/modificadas):

- **Convención de ramas:** ¿La rama origen sigue el patrón definido? (ej. `feature/`, `bugfix/`, `hu-[ID]-`)
- **Mensajes de commit:** ¿Siguen Conventional Commits u otra convención definida?
- **Descripción del PR:** ¿Es descriptiva y referencia work items?
- **Estructura de archivos:** ¿Los archivos nuevos/movidos están en las carpetas esperadas?
- **Código nuevo/modificado** (solo líneas `+` del diff):
  - Naming: ¿variables, funciones, clases siguen la convención del estándar?
  - Imports: ¿el orden y agrupación cumplen la guía?
  - Patrones: ¿respeta la arquitectura definida en `architecture_*.md`? (ej. capas, responsabilidades)
  - Anti-patrones: ¿introduce algún patrón prohibido por el estándar?
  - Documentación: ¿métodos públicos nuevos tienen la documentación requerida?

**Solo analizar las líneas cambiadas (`+`), nunca el código existente que no fue tocado.**

Clasificar cada hallazgo:
- 🔴 **Violación crítica** — Rompe un estándar obligatorio
- 🟡 **Advertencia** — Desvío menor o recomendación
- 🟢 **Conforme** — Cumple el estándar

Por cada hallazgo, registrar: `{archivo, linea_inicio, linea_fin, regla_violada, fragmento_codigo, severidad, explicacion}`

**D.3 — Salud general:**
- Threads sin resolver (cantidad y antigüedad)
- Días abierto el PR
- Coherencia título ↔ descripción ↔ work items
- Volumen de cambios: cantidad de archivos y líneas tocadas

### Fase E — Reporte y acciones

**E.1 — Generar reporte:**
Construir el reporte usando `assets/template-pr-review-report.md` y presentarlo en el chat.

**E.2 — Determinar veredicto y presentar opciones:**

El veredicto se deriva automáticamente del análisis:

---

**Caso 1 — PR alineado y sin conflictos** (0 violaciones críticas, 0 conflictos):
> ✅ **El PR está alineado a los estándares y sin conflictos.**
> - 👍 **[A]** Aprobar — Agregar comentario de aprobación en el PR
> - ❌ **[C]** Cancelar revisión

**Caso 2 — PR con conflictos** (mergeStatus indica conflictos):
> ⚠️ **El PR presenta los siguientes conflictos:**
> [Detalle de conflictos con explicación]
> - 🔧 **[R]** Resolver — Agregar instrucciones de resolución como comentario
> - 💬 **[G]** Agregar comentario — Publicar hallazgos como thread en el PR
> - ❌ **[C]** Cancelar revisión

**Caso 3 — PR no cumple estándares** (violaciones críticas encontradas):
> 🚫 **El PR no cumple los estándares definidos por el equipo:**
> [Lista de violaciones con referencia al estándar infringido]
> - 💬 **[G]** Agregar comentario — Publicar hallazgos como threads en el PR
> - 👎 **[Z]** Rechazar — Comentario de rechazo en el PR
> - ❌ **[C]** Cancelar revisión

**Caso mixto** (conflictos + violaciones): Combina ambos y ofrece todas las opciones aplicables: [R], [G], [Z], [C].

---

### Fase F — Ejecución de la acción seleccionada

**[A] Aprobar:**
1. Invoca `ado/repo_vote_pull_request` con:
   - `repositoryId`: ID del repositorio
   - `pullRequestId`: ID del PR
   - `vote`: `Approved`
2. Invoca `ado/repo_create_pull_request_thread` con:
   - `content`: `✅ **Code Review Aprobado** — PR analizado contra coding-standards.md. Sin violaciones ni conflictos. [Resumen breve]`
   - `status`: `Closed`
3. Si existía registro pendiente previo de este PR, eliminarlo de `pending_reviews.json`.
4. Confirma: `✅ PR #[PR_ID] aprobado. Voto registrado + comentario de aprobación publicado.`
5. No se genera archivo de reporte.

**[G] Agregar comentario:**
1. Por cada hallazgo relevante, invoca `ado/repo_create_pull_request_thread` con:
   - `content`: Descripción del hallazgo + referencia al estándar + fragmento de código afectado
   - `filePath`: Ruta del archivo afectado (desde la raíz del repo, ej. `/src/main/java/.../MiClase.java`)
   - `rightFileStartLine`: Número de línea inicio del hallazgo (en el lado derecho del diff)
   - `rightFileEndLine`: Número de línea fin del hallazgo
   - `rightFileStartOffset`: 1 (inicio de la línea)
   - `rightFileEndOffset`: longitud de la última línea señalada
   - `status`: `Active`
   
   > **💡 Las líneas deben tomarse del output de `git diff` (Fase B.4). Los headers `@@ -X,Y +Z,W @@` indican las líneas del lado derecho (`+Z`). Solo anclar en líneas que aparecen con `+` en el diff — nunca en código que no fue modificado por el PR.**

2. Si un hallazgo no tiene archivo/línea específica (ej. convención de rama, mensaje de commit), crear thread sin `filePath` — aparecerá como comentario general del PR.
3. Confirma: `💬 [X] threads creados en PR #[PR_ID] (Y anclados en código, Z generales).`
3. Preguntar al usuario:
   > **🤷 ¿Deseas generar el reporte de revisión como archivo?**
   > - 📄 **[S]** Sí, guardar en `[Ruta Reviews Autor]/review_PR_[PR_ID]_[timestamp].md`
   > - ❌ **[N]** No, solo el chat
4. Si acepta [S]: generar archivo usando `assets/template-pr-review-report.md`.

**[Z] Rechazar:**
> ⚠️ **Confirmación requerida:** ¿Estás seguro de publicar el rechazo en el PR?
> - ✅ **[S]** Sí, rechazar
> - ❌ **[N]** No, volver a las opciones

Si confirma:
1. Invoca `ado/repo_vote_pull_request` con:
   - `repositoryId`: ID del repositorio
   - `pullRequestId`: ID del PR
   - `vote`: `Rejected`
2. Invoca `ado/repo_create_pull_request_thread` con:
   - `content`: `🚫 **Code Review — No aprobado** — Violaciones encontradas: [lista]. Consultar coding-standards.md para referencia.`
   - `status`: `Active`
3. Confirma: `🚫 PR #[PR_ID] rechazado. Voto de rechazo registrado + comentario publicado.`
4. No se genera archivo de reporte.

**[R] Resolver (conflictos):**
1. Invoca `ado/repo_create_pull_request_thread` con instrucciones de resolución:
   - `content`: `⚠️ **Conflictos de merge detectados.** Rebase o merge manual de [targetRefName] en [sourceRefName] requerido.` + detalle de archivos en conflicto si disponible.
   - `status`: `Active`

**[C] Cancelar revisión:**
1. Registra en `[base_reports_path]/[project_name]/[user_email]/pr_reviews/pending_reviews.json`:
   ```json
   {
     "pr_id": "[PR_ID]",
     "titulo": "[Título del PR]",
     "pendiente_por": "[Motivo: conflictos/violaciones/detalle]",
     "responsable": "[createdBy.displayName]",
     "responsable_email": "[createdBy.uniqueName]",
     "rama_origen": "[sourceRefName]",
     "rama_destino": "[targetRefName]",
     "fecha_revision": "[timestamp ISO]",
     "revisado_por": "[user_email del perfil activo]"
   }
   ```
2. Si el archivo existe, agrega al array. Si no, crea el array con este primer registro.
3. Confirma:
   > 📝 **Revisión cancelada y registrada como pendiente.** PR #[PR_ID] guardado en `pending_reviews.json`.

---

## Comando: PENDIENTES-PR

Lista las revisiones pendientes del **revisor actual** (`user_email`).

### Flujo

1. Lee `[base_reports_path]/[project_name]/[user_email]/pr_reviews/pending_reviews.json`. Si no existe: `📭 No hay revisiones pendientes registradas.`
2. Presenta tabla:

| PR ID | Título | Pendiente por | Responsable | Rama | Fecha |
|-------|--------|---------------|-------------|------|-------|
| [ID]  | [Título] | [Motivo resumido] | [Autor] | `[source]` → `[target]` | [fecha] |

3. Opciones:
> 📋 **Revisiones pendientes cargadas.**
> - 🔄 **[R]** Retomar revisión de un PR (ejecuta `REVISAR-PR`)
> - 🗑️ **[D]** Descartar un pendiente (elimina del JSON)
> - ❌ **[N]** Nada

---

## Gotchas

- **Formatos de PR ID:** Número puro (`12345`) o URL completa de ADO. Siempre normaliza a `repositoryId` + `pullRequestId` numérico antes de invocar herramientas.
- **`mergeStatus` es el campo clave para conflictos.** Valores: `succeeded` (sin conflictos), `conflicts` (hay conflictos), `queued` (no evaluado aún). Si es `queued`, informa y sugiere esperar o forzar evaluación.
- **Los archivos de estándares pueden no existir.** No bloquees la revisión — analiza conflictos y threads igualmente, pero indica que no se validaron estándares.
- **Threads de sistema vs. usuario:** ADO crea threads automáticos (push, policy). Filtra por autoría humana al contar discusiones pendientes.
- **Antes de [Z] Rechazar, siempre pide confirmación explícita.** Es la acción más impactante.
- **`createdBy` del PR = responsable.** Usa `displayName` para mostrar, `uniqueName` (email) para registros.
- **Si ya existe un registro pendiente del mismo PR**, muéstralo al inicio de la Fase E como contexto de revisión previa.
- **No autoaprubes ni autorechaces.** Toda acción que impacte el PR en ADO requiere selección explícita del usuario.
- **Si el PR tiene más de 50 threads**, muestra un resumen agrupado (resueltos vs. pendientes) en lugar de listar todos.
- **Solo analizar líneas `+` del diff.** Nunca validar código que no fue tocado por el PR — el code review es sobre los cambios, no sobre deuda técnica preexistente.
- **Limpiar prefijo `refs/heads/` de los nombres de rama** antes de usar en comandos git. `sourceRefName: refs/heads/feature/xyz` → `feature/xyz`.
- **Filtrar archivos no analizables del diff:** binarios, imágenes, `package-lock.json`, `yarn.lock`, archivos `.min.js`, etc. No aportan al análisis de estándares.
- **`git diff ...` (tres puntos) vs `..` (dos puntos):** Usar tres puntos (`origin/target...origin/source`) para obtener solo los cambios que la rama source introduce desde el punto de bifurcación. Dos puntos mostraría también cambios en target que source no tiene.
- **Si `git fetch` falla** (rama no existe en remote, permisos), informar al usuario y continuar solo con análisis de metadatos vía MCP ADO.
- **Volumen de diff:** Si un archivo individual tiene más de 500 líneas de diff, mostrar un resumen por secciones en lugar del análisis línea por línea.
- **Líneas para anclaje de comentarios:** Los números de línea para `rightFileStartLine`/`rightFileEndLine` corresponden al archivo en la versión nueva (lado derecho del diff). Extraerlos del header `@@ -X,Y +Z,W @@` del diff de cada archivo. `Z` es la línea inicio del bloque en el lado derecho.
- **`vote_pull_request` es irreversible por sesión.** Una vez emitido el voto, solo se puede cambiar con otro voto. Siempre confirmar con el usuario antes de votar.
- **Votos disponibles:** `Approved` (aprueba), `ApprovedWithSuggestions` (aprueba con sugerencias), `WaitingForAuthor` (espera cambios), `Rejected` (rechaza), `NoVote` (quitar voto). El skill usa `Approved` para [A] y `Rejected` para [Z].
