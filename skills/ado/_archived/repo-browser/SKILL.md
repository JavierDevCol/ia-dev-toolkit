---
name: ado-repo-browser
description: >
  Exploración read-only de repositorios Git en Azure DevOps: lista repos,
  consulta ramas y Pull Requests activos. Usa esta skill cuando el usuario
  quiera listar repos, ver ramas, consultar PRs abiertos o clonar un
  repositorio. No modifica repos ni crea ramas.
  Triggers on: listar repos, ver ramas, PRs activos, repositorios del proyecto,
  clonar repo, mis repos, list repositories, browse repos, active pull requests,
  repo branches.
compatibility: Requires Azure DevOps MCP server configured
---

# ADO Repo Browser

Exploración de repositorios Git vinculados al proyecto del perfil activo en Azure DevOps.

## Contexto del perfil activo

Esta skill lee del perfil activo (standalone) en `memory_skill.json` → `[ado].config.perfiles[perfil_activo]`:
- `project_name` — proyecto ADO resuelto desde `project_map.repos`
- `user_email` — email del perfil activo
- `base_reports_path` — ruta base de reportes

La skill lee el perfil activo desde `memory_skill.json` → `[ado].config.perfiles[perfil_activo]` (standalone).

## Comando: LISTAR-REPOS

### Fase A — Validación de Perfil

1. Verifica que el agente haya pasado `project_name`.
2. Si `project_name` está vacío o ausente → detén el flujo e informa: "El perfil activo no resolvió el proyecto para el dominio `repos`. Verifica que `project_map.repos` esté configurado en `memory_skill.json` → `[ado].config.perfiles[perfil_activo]`."

### Fase B — Extracción desde ADO

Invoca `ado/repo_list_repos_by_project` con el `project_name` del perfil activo.
Extrae: nombre, ID, URL de clonación y rama por defecto de cada repositorio.

### Fase C — Resultado

Presenta una tabla organizada en el chat:

| Nombre del Repo | ID | URL de Clonación | Rama Default |
| :-------------- | :- | :--------------- | :----------- |
| [Nombre]        | [ID-UUID] | [URL-HTTPS] | [main/develop/...] |

### Fase D — Interacción Post-Listado

Al finalizar:
> 📂 **Repositorios cargados.** ¿Deseas realizar alguna acción?
> **[B]** Ver ramas de un repo | **[P]** Ver Pull Requests activos | **[C]** Clonar (instrucciones) | **[N]** Nada

**Si elige [B]:**
1. Pregunta qué repo (por nombre o número de la tabla).
2. Invoca `ado/repo_list_branches_by_repo` con el ID del repo seleccionado.
3. Muestra las ramas con nombre, fecha del último commit y autor.

**Si elige [P]:**
1. Pregunta qué repo (o si quiere PRs de todo el proyecto).
2. Invoca `ado/repo_list_pull_requests_by_repo_or_project` con status `active`.
3. Presenta tabla:

| PR ID | Título | Autor | Rama Origen → Destino | Reviewers | Estado |
| :---- | :----- | :---- | :-------------------- | :-------- | :----- |
| [ID]  | [Título] | [Autor] | `[source]` → `[target]` | [Nombres] | [Active] |

**Si elige [C]:**
1. Pregunta qué repo.
2. Muestra el comando de clonación:
   ```
   git clone [URL-HTTPS]
   ```

## Errores comunes

- Si `ado/repo_list_repos_by_project` devuelve lista vacía → responde: "No se encontraron repositorios para el proyecto **[project_name]**. Verifica que `project_map.repos` tenga el nombre correcto en `memory_skill.json` → `[ado].config.perfiles[perfil_activo]`."
- Si la API devuelve error de permisos (403/401) → responde: "No tienes acceso al proyecto **[project_name]**. Contacta al administrador del proyecto en Azure DevOps."
- Si la llamada falla por timeout o error de red → reintenta una vez. Si persiste, informa al usuario.

## Gotchas

- Los IDs de repo son UUIDs. Nunca muestres el UUID completo como dato principal — usa el nombre del repo como identificador visible y el UUID internamente.
- `ado/repo_list_pull_requests_by_repo_or_project` puede devolver PRs en estado `abandoned` o `completed`. Filtra solo `active` por defecto.
- Si el proyecto tiene más de 20 repos, muestra los primeros 20 y pregunta si quiere ver más.
- Las URLs de clonación pueden ser HTTPS o SSH. Muestra HTTPS por defecto; si el usuario pide SSH, menciónalo.
