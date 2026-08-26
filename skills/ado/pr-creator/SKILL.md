---
name: ado-pr-creator
description: >
  Creación guiada de Pull Requests en Azure DevOps con validación de repositorio,
  ramas, revisión de duplicados activos y vista previa antes de publicar. Usa
  esta skill cuando el usuario quiera crear un PR, abrir un pull request,
  generar un PR, proponer merge entre ramas, asignar reviewers a un PR nuevo o
  vincular work items al PR al crearlo. También activa cuando mencione: crear
  PR, abrir PR, nuevo pull request, generar pull request, create pull request,
  open pull request, new PR.
compatibility: Requires Azure DevOps MCP server configured
---

# ADO PR Creator

Creación estructurada de Pull Requests en Azure DevOps con confirmación explícita antes de publicar.

## Contexto del perfil activo

Esta skill asume que el agente orquestador ya resolvió el perfil activo desde `config_consultas.json` y pasa:
- `project_repos` — proyecto ADO resuelto desde `project_map.repos` (para operaciones de repositorio y PR)
- `project_workitems` — proyecto ADO resuelto desde `project_map.workitems` (para vincular work items)
- `user_email` — email del perfil activo
- `base_reports_path` — ruta base de reportes, si existe

> **Nota:** `project_repos` y `project_workitems` pueden apuntar a proyectos ADO distintos.

## Comando: CREAR-PR [repo_opcional]

### Fase A — Validación de perfil

1. Verifica que el agente haya pasado `project_repos`.
2. Si falta, detén el flujo e informa: "El agente no resolvió el proyecto para el dominio `repos`. Verifica que `project_map.repos` esté configurado en `config_consultas.json`."

### Fase B — Resolución del repositorio

1. **Si el usuario indicó repo en el comando o en lenguaje natural:**
   - Invoca `ado/repo_get_repo_by_name_or_id` para resolver el `repositoryId`.
2. **Si no indicó repo:**
   - Intenta inferir el repositorio actual con terminal local:
     ```bash
     git remote get-url origin
     ```
   - Si el remote permite deducir el nombre del repo, úsalo y confirma al usuario.
   - Si no es posible inferirlo, invoca `ado/repo_list_repos_by_project` con `project_repos` y pregunta qué repositorio desea usar.
3. Extrae del repo resuelto:
   - nombre del repo
   - `repositoryId`
   - rama por defecto (`defaultBranch`) si viene disponible
4. Si el repo no existe en el proyecto activo, informa al usuario y detén el flujo.

### Fase C — Resolución de ramas

Resolver siempre una **rama origen** y una **rama destino**.

1. **Rama origen (`sourceBranch`):**
   - Si el usuario la indicó, úsala.
   - Si no la indicó y el repo coincide con el workspace local, intenta detectarla con:
     ```bash
     git branch --show-current
     ```
   - Si sigue vacía, pregunta al usuario.
2. **Rama destino (`targetBranch`):**
   - Si el usuario la indicó, úsala.
   - Si no la indicó, invoca `ado/repo_list_branches_by_repo` y lista las ramas de ambiente detectadas.
   - Considera como ramas de ambiente las que coincidan con patrones como `develop`, `development`, `qa`, `test`, `uat`, `staging`, `release`, `main`, `master`, `produccion` o `production`.
   - Presenta al usuario solo esas ramas de ambiente ya normalizadas sin el prefijo `refs/heads/` y solicita explícitamente a cuál rama desea hacer el PR.
   - Si no se detectan ramas de ambiente claras, muestra una lista acotada de ramas candidatas del repo y solicita que el usuario elija la rama destino.
3. Valida ambas ramas con `ado/repo_get_branch_by_name`.
4. Si alguna rama no existe, detén el flujo y explica cuál falta.
5. Si `sourceBranch = targetBranch`, detén el flujo: no se puede crear un PR hacia la misma rama.

### Fase D — Datos del PR

Recopila o completa los siguientes campos:

1. **Título:**
   - Debe seguir una convención guiada por Conventional Commits con formato: `type(scope): resumen`.
   - Tipos recomendados: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `build`, `ci`, `chore`.
   - Si el usuario ya lo dio, valídalo contra ese formato y, si no cumple, propón una versión corregida antes de continuar.
   - Si no lo dio, constrúyelo a partir de la rama origen y del objetivo del cambio, y pide confirmación o edición.
2. **Descripción:**
   - Debe quedar guiada por la misma convención semántica del título.
   - Si el usuario ya la dio, revísala para que sea consistente con el `type(scope): resumen` del título.
   - Si no, construye un borrador breve y editable con esta estructura:
     ```md
     Tipo: [type]
     Scope: [scope o N/A]

     ## Resumen
     [Objetivo del PR]

     ## Cambios principales
     - [Cambio 1]
     - [Cambio 2]

     ## Commits esperados
     - [type(scope): cambio principal]
     - [type(scope): ajuste secundario]

     ## Validación
     - [Prueba o validación realizada]

     ## Breaking Changes
     - [Ninguno o detalle]

     ## Work Items
     - [IDs o Ninguno]
     ```
   - Si el cambio implica ruptura compatible con Conventional Commits, refleja claramente el impacto en `Breaking Changes`.
3. **Reviewers opcionales:**
   - Si el usuario proporciona correos o nombres, resuélvelos con `ado/core_get_identity_ids`.
4. **Work items opcionales:**
   - Acepta lista de IDs para vincular después de crear el PR.

### Fase E — Validaciones previas

Antes de crear el PR:

1. Invoca `ado/repo_list_pull_requests_by_repo_or_project` sobre el repo con estado `active`.
2. Busca si ya existe un PR activo con la misma combinación `sourceBranch -> targetBranch`.
3. Si ya existe, no crees uno nuevo. Muestra al usuario el PR existente y ofrece retomar revisión o abrirlo.
4. Si no existe duplicado, continúa.

### Fase F — Vista previa obligatoria

Presenta un resumen en chat:

| Campo | Valor |
|------|-------|
| Repo | [repo_name] |
| Rama origen | `[sourceBranch]` |
| Rama destino | `[targetBranch]` |
| Título | [title] |
| Reviewers | [lista o "Sin reviewers"] |
| Work Items | [lista o "Ninguno"] |

Luego pregunta:

> **🤷 ¿Deseas crear el Pull Request con estos datos?**
> - ✅ **[S]** Sí, crear PR
> - ✏️ **[E]** Editar datos
> - ❌ **[N]** Cancelar

Nunca publiques el PR sin confirmación explícita `[S]`.

### Fase G — Creación del PR

Si el usuario confirma:

1. Invoca `ado/repo_create_pull_request` con:
   - `repositoryId`
   - `sourceRefName`: `refs/heads/[sourceBranch]`
   - `targetRefName`: `refs/heads/[targetBranch]`
   - `title`
   - `description`
2. Guarda el `pullRequestId`, la URL resultante y el resumen final del PR.
3. Si hay reviewers resueltos, invoca `ado/repo_update_pull_request_reviewers` para agregarlos.
4. Si hay work items, vincula cada uno con `ado/wit_link_work_item_to_pull_request`. Los work items pertenecen al proyecto `project_workitems`.
5. Confirma en chat:
   > ✅ **PR creado correctamente.**
   > - Repo: `[repo_name]`
   > - PR: `#[pullRequestId]`
   > - Link: `[pullRequestUrl]`
   > - Resumen: `[summary]`
   > - Flujo: `[sourceBranch]` → `[targetBranch]`
   > - Reviewers agregados: [X]
   > - Work Items vinculados: [Y]

### Fase H — Post-creación opcional

Tras crear el PR, ofrece acciones siguientes:

> 🚀 **PR listo. ¿Deseas continuar con alguna acción?**
> - 🔍 **[R]** Revisar el PR recién creado
> - 📋 **[P]** Ver PRs activos del repo
> - ❌ **[N]** Nada

- Si elige `[R]`, delega a `REVISAR-PR [pullRequestId]`.
- Si elige `[P]`, delega a la consulta de PRs activos del repo.

## Errores comunes

- Si `ado/repo_create_pull_request` devuelve error porque no hay diferencias entre ramas, responde: `No hay cambios para proponer entre [sourceBranch] y [targetBranch].`
- Si la rama origen no existe en remoto, responde: `La rama origen no existe en Azure DevOps. Debes publicarla antes de crear el PR.`
- Si falla la resolución de reviewers, continúa sin agregarlos y avisa cuáles no pudieron resolverse.
- Si falla el vínculo de algún work item, no canceles el PR creado; informa cuáles quedaron sin vincular.
- Si ADO devuelve permisos insuficientes (401/403), informa al usuario y no reintentes automáticamente más de una vez.

## Gotchas

- Limpia siempre el prefijo `refs/heads/` al mostrar ramas al usuario; vuelve a agregarlo solo al invocar la creación del PR.
- No asumas automáticamente la rama destino. Si el usuario no la indicó, debes pedirla mostrando primero las ramas de ambiente detectadas.
- Evita PRs duplicados comparando `sourceBranch` y `targetBranch` contra PRs activos antes de crear uno nuevo.
- No bloquees la creación del PR si fallan acciones posteriores no críticas como reviewers o links de work items; repórtalas por separado.
- Si el usuario pega una URL de repo o de rama en lugar del nombre, normaliza primero y luego resuelve el repo.
- Si el workspace local no corresponde al repo ADO elegido, no uses inferencias por git local para ramas o nombre de repo.
- El título del PR no debe ser libre si rompe la convención acordada; primero corrígelo a formato Conventional Commits y luego solicita confirmación.