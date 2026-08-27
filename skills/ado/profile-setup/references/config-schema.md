# Profile Config Schema & Templates

## JSON Structure

```json
{
  "perfil_activo": "NOMBRE",
  "perfiles": {
    "NOMBRE": {
      "user_email": "EMAIL",
      "project_map": {
        "workitems": "PROJ_WI",
        "repos": "PROJ_REPOS",
        "pipelines": "PROJ_REPOS",
        "wiki": "PROJ_WI",
        "testplans": "PROJ_WI",
        "default": "PROJ_WI"
      },
      "base_reports_path": "RUTA",
      "default_query": {
        "nombre": "NOMBRE_QUERY",
        "tipo": "saved_query|wiql",
        "proyecto": "PROJ_WI",
        "query_id": "SOLO SI tipo=saved_query",
        "query": "SOLO SI tipo=wiql",
        "resumen_legible": "DESCRIPCION LEGIBLE DE LA CONSULTA",
        "origen": {
          "tipo": "manual|wi_ejemplo",
          "wi_id": "SOLO SI origen=wi_ejemplo",
          "wi_url": "SOLO SI origen=wi_ejemplo"
        }
      },
      "config_extras": {
        "formato_fecha": "ISO-8601",
        "idioma_reportes": "es"
      }
    }
  }
}
```

## default_query — Case A (Saved Query)

```json
"default_query": {
  "nombre": "NOMBRE_QUERY",
  "tipo": "saved_query",
  "proyecto": "PROJ_WI",
  "query_id": "QUERY_ID"
}
```

## default_query — Case B (WI Example)

```json
"default_query": {
  "nombre": "Desde WI #{ID}",
  "tipo": "wiql",
  "proyecto": "PROJ_WI",
  "query": "SELECT ... FROM WorkItems WHERE ...",
  "resumen_legible": "WIs asignados a mí en {PROJ_WI}, tipo {tipos}, tag {tags}, excluye Closed/Done/Removed",
  "origen": {
    "tipo": "wi_ejemplo",
    "wi_id": ID,
    "wi_url": "URL"
  }
}
```

## default_query — Case C (Manual)

```json
"default_query": {
  "nombre": "Consulta personalizada",
  "tipo": "wiql",
  "proyecto": "PROJ_WI",
  "query": "SELECT ... FROM WorkItems WHERE ...",
  "resumen_legible": "WIs asignados a mí en {PROJ_WI}, tipo {tipos}, ..."
}
```

## Manual Questionnaire Defaults

| Filter | Default |
|--------|---------|
| Tipos de WI | `["Bug", "Task"]` |
| Estados | Excluir `["Closed", "Done", "Removed"]` |
| Asignado | Sí (`@me`) |
| Tags | No filtrar |
| Área | No filtrar |
| Parent | No filtrar |
| Iteración | No filtrar |

## WIQL Field Extraction (Case B)

When building from a WI example, extract:

| ADO Field | Maps To |
|-----------|---------|
| `System.WorkItemType` | tipos |
| `System.AreaPath` | area_path |
| `System.Tags` | tags (split by comma) |
| `System.Parent` | parent_id |
| `System.State` | reference states |

## Write Rules

- File: `config_consultas.json` at workspace root
- Indentation: 2 spaces
- Does not exist → create template, insert new profile, set as active
- Exists valid → insert new profile name, activate it, do not modify others
- Exists invalid → ask user whether to overwrite; if no → cancel
