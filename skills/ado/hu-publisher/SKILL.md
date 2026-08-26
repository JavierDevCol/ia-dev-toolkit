---
name: ado-hu-publisher
description: >
  Publicación de una Historia de Usuario (HU) redactada localmente hacia Azure DevOps.
  Parsea un archivo Markdown de HU local (en cualquier formato: salida de ado-item-detail
  o borrador del Analista de Requisitos), extrae los campos mínimos requeridos, muestra
  una vista previa editable y crea el Work Item en ADO con un solo comando. Actualiza
  el archivo local con el ID y enlace ADO asignado. Usa esta skill cuando el usuario
  quiera publicar una HU local en ADO, sincronizar una historia redactada localmente,
  crear una User Story desde un archivo Markdown, o subir una HU al backlog de ADO.
  También activa cuando mencione: publicar HU, subir HU a ADO, crear HU en ADO, sincronizar
  historia, push HU, publicar historia de usuario, crear work item desde archivo.
  Also triggers on: publish user story, push HU to ADO, create work item from local file,
  sync local story to Azure DevOps.
compatibility: Requires Azure DevOps MCP server configured
---

# ADO HU Publisher

Publicación de Historias de Usuario locales (Markdown) hacia Azure DevOps en dos fases: validación y vista previa local, luego creación en ADO.

## Contexto del perfil activo

Cuando esta skill se ejecuta dentro del agente **SAC - ADO Power Suite**, recibe el contexto ya resuelto:
- `project_name` — proyecto ADO resuelto desde `project_map.workitems`
- `user_email`, `base_reports_path`, `organization_url`
- `config_extras` — reglas dinámicas de área, iteration path, estimación, tags, etc.

La skill **no lee `config_consultas.json` directamente** en modo agente. Todo el contexto es inyectado por el agente.

Cuando se invoca de forma **standalone** (sin el agente suite), el perfil debe resolverse desde el primer mensaje del usuario. Si faltan campos críticos, solicitarlos antes de continuar.

## Detección del Proceso ADO (Obligatorio antes de mapear estimación)

El campo de estimación de una User Story varía según el proceso configurado en la organización ADO:

| Proceso | Campo de estimación en HU | Campo ADO |
|---|---|---|
| **Agile** | Story Points (abstracto) | `Microsoft.VSTS.Scheduling.StoryPoints` |
| **Scrum** | Effort (horas directas) | `Microsoft.VSTS.Scheduling.Effort` |
| **CMMI** | Size (puntos) | `Microsoft.VSTS.Scheduling.Size` |

### Protocolo de detección

1. **Caché local primero:** Si `config_extras.ado_process` existe (`agile`, `scrum` o `cmmi`) → úsalo directamente sin consultar ADO.
2. **Fallback a ADO:** Si no existe en config, invoca `ado/wit_get_work_item_type` con tipo `User Story` del proyecto activo. Busca en la respuesta el nombre del proceso (`processName` o el prefijo del namespace de campos).
3. **Persistencia:** Tras detectarlo, guarda el valor en `config_extras.ado_process` del perfil activo en `config_consultas.json` para evitar la consulta en futuras ejecuciones.
4. **Fallback final:** Si la detección falla, asume `agile` y avisa al usuario en la Vista Previa:
   > `⚠️ No se pudo detectar el proceso ADO. Se asume Agile (StoryPoints). Verifica con [E] si es incorrecto.`

### Impacto en el valor de estimación

- **Agile:** envía el valor derivado en SP (entero, resultado de `horas / horas_por_sp`).
- **Scrum:** envía las horas totales directamente (ej: `3.2`) sin conversión a SP.
- **CMMI:** trata igual que Agile (puntos abstractos).

## Formatos de HU Soportados

La skill reconoce y parsea dos formatos principales:

### Formato A — Salida de `ado-item-detail` (pull desde ADO)
Identificador: presencia de `🔗 **ADO**` o `| **ID** | [número] |` con un ID numérico válido en la tabla de ficha técnica.

> ⚠️ **GUARDIA ANTI-DUPLICADO:** Si el archivo ya contiene un ID ADO real en la ficha técnica o un enlace `dev.azure.com/.../_workitems/edit/[ID]`, la skill **DETIENE la creación** e informa:
> > **🛑 Esta HU ya existe en ADO (ID: #[ID]).** ¿Deseas actualizar el work item existente en su lugar?
> > - 🔄 **[U]** Sí, actualizar campos en ADO
> > - ❌ **[N]** Cancelar — no hacer nada
> > - 📋 **[V]** Solo ver el estado actual en ADO

### Formato B — Borrador local (salida del Analista de Requisitos u otro)
Identificador: ausencia de ID ADO real. Puede contener `**ID Original:**` como referencia histórica — esto **NO** se toma como ID ADO existente. El agente busca patrones como:
- `# Historia #[Código-Local]:` o `# 📘 User Story — [Título]` (sin número ADO)
- Ausencia de enlace `dev.azure.com/.../edit/[número]` con ID real.

### Formato C — HU Libre o Mínima (cualquier Markdown con campos suficientes)
Identificador: ninguno de los patrones anteriores. El agente aplica **Extracción Progresiva** (ver Mapa de Extracción) y siempre muestra la Vista Previa con una advertencia de confianza baja antes de permitir publicar.

## Mapa de Extracción de Campos — Estrategia Progresiva

Para cada campo, el agente intenta los patrones en orden de prioridad (P1 → P2 → P3 → Fallback). El primero que produzca un valor no vacío gana.

### `System.Title` (Obligatorio)
| Prioridad | Patrón buscado |
|---|---|
| P1 | Valor en celda `\| **Título** \|` de tabla de ficha técnica |
| P2 | Texto del encabezado H1 (`# ...`), limpiando emojis, `#ID` iniciales y `—` |
| P3 | Primer encabezado H2 si no hay H1 significativo |
| ❌ Falla | Solicita al usuario ingresar el título manualmente |

### `System.Description` (Obligatorio)
| Prioridad | Patrón buscado |
|---|---|
| P1 | Sección bajo `## Historia de Usuario` (narrativa Como/Quiero/Para) + secciones Descripción, Reglas de Negocio, Observaciones técnicas, Dependencias |
| P2 | Sección bajo `## 📝 Descripción` o `## Descripción` |
| P3 | Todo el texto del archivo excluyendo criterios de aceptación, relaciones y métricas |
| ❌ Falla | Solicita al usuario confirmar si el contenido restante es la descripción |

> **⚠️ Tras extraer la descripción, ejecutar la Guardia de Valor (ver sección siguiente).**

## Guardia de Valor — Validación de Narrativa INVEST

Esta guardia se ejecuta **siempre**, inmediatamente después de extraer `System.Description`. Su objetivo es verificar que la HU exprese valor de negocio real, no solo un requerimiento funcional.

### Algoritmo de detección

El agente busca en el texto de la descripción los tres componentes de la narrativa:

| Componente | Señales de presencia (case-insensitive) |
|---|---|
| **Rol** (`Como`) | `Como `, `As a `, `As an `, `En mi rol de`, `Siendo ` |
| **Acción** (`Quiero`) | `quiero `, `necesito `, `deseo `, `I want `, `I need `, `me gustaría ` |
| **Beneficio** (`Para`) | `para `, `para que `, `con el fin de `, `a fin de `, `so that `, `in order to `, `con el objetivo de ` |

### Resultados y acciones

**Caso 1 — Los 3 componentes presentes → Narrativa Completa ✅**
- Registra confianza de narrativa: **Alta**. Continúa sin interrupciones.

**Caso 2 — Falta solo el Beneficio (`Para`) → Valor de Negocio Ausente ⚠️**
- **DETIENE el flujo** y muestra al usuario:
  > **⚠️ Guardia de Valor:** La descripción tiene Rol y Acción, pero **no expresa el beneficio** (*"para que..."*).
  > Sin el beneficio, esta HU no comunica valor de negocio — es un requerimiento funcional disfrazado.
  >
  > **Descripción detectada:**
  > > *[primeras 200 chars de la descripción extraída]*
  >
  > **🤷 ¿Cómo deseas continuar?**
  > - ✏️ **[B]** Ingresar el beneficio ahora — lo agrego a la descripción antes de publicar
  > - ⚠️ **[F]** Publicar sin beneficio (confianza Media — queda registrado en el sello local)
  > - ❌ **[N]** Cancelar y corregir el archivo primero

  Si el usuario elige **[B]**, solicita el texto del beneficio, lo concatena al final de la narrativa existente con el prefijo `**Para que:** ` y actualiza el campo `System.Description` antes de continuar.

**Caso 3 — Falta Rol o Acción → Sin Narrativa Estructurada ⚠️**
- No bloquea (puede ser una HU en formato técnico sin narrativa explícita), pero registra confianza de narrativa: **Media**.
- Añade una nota en la Vista Previa:
  > `⚠️ Narrativa: No se detectó estructura Como/Quiero/Para. Verifica que la descripción exprese el valor de negocio.`

**Caso 4 — Descripción vacía o irrecuperable → ❌ Bloqueante**
- Igual que el fallo de `System.Description` — solicita al usuario antes de continuar.

### `Microsoft.VSTS.Common.AcceptanceCriteria` (Obligatorio)
| Prioridad | Patrón buscado |
|---|---|
| P1 | Sección bajo `## Criterios de Aceptación` / `## ✅ Criterios de Aceptación` — items `- [ ]` o `- [x]` |
| P2 | Sección bajo `## Criterios` (cualquier variante sin emoji) |
| P3 | Escenarios BDD bajo `### Escenario N:` — los agrupa como lista numerada |
| ❌ Falla | **BLOQUEA la publicación.** Sin criterios no hay HU coherente. Informa al usuario. |

### `System.IterationPath` (Recomendado)
| Prioridad | Patrón buscado |
|---|---|
| P1 | `\| **Iteration Path** \|` en tabla |
| P2 | `config_extras.default_iteration` o `default_sprint` del perfil activo |
| P3 | Solicita al usuario |

### `Microsoft.VSTS.Common.Priority` — Default: `2`
| Prioridad | Patrón buscado |
|---|---|
| P1 | `\| **Prioridad** \|` en tabla |
| P2 | `2` (default silencioso) |

### `Microsoft.VSTS.Scheduling.StoryPoints` (Opcional)
| Prioridad | Patrón buscado |
|---|---|
| P1 | `\| **Story Points** \|` o `\| Story Points \|` en cualquier tabla — valor numérico directo |
| P2 | Tabla de **Totales Comparativos por Rol** — extrae el valor de la columna `Método Ceiba` del rol definido en `config_extras.rol_estimacion` (default: `Senior`). Suma el total de horas Método Ceiba + Tareas Manuales usando la línea `⏱ Tiempo comprometido por desarrollador` si existe, o la fórmula `[Método Ceiba rol] + [Total Tareas Manuales]`. Aplica el proceso ADO detectado: **Agile/CMMI** → convierte horas a SP con `config_extras.horas_por_sp` (default: `4`), redondea al entero ≥ 1, envía a `StoryPoints`. **Scrum** → envía las horas totales directamente a `Effort` sin conversión. |
| P3 | Campo `**Complejidad:**` en el texto — aplica tabla de conversión de `config_extras.complejidad_sp` si existe, o usa el default: `BAJA→1`, `MEDIA→3`, `ALTA→8`, `MUY ALTA→13` |
| P4 | Omite el campo (no lo envía a ADO) |

> **Transparencia de derivación:** Si el valor de SP se derivó por P2 o P3 (no era un número explícito), la Vista Previa lo muestra con nota:
> `Story Points: 2 ⚙️ (derivado de tabla de estimación — Senior 3.2h / 4h por SP)`
> El colaborador puede corregirlo antes de publicar con la opción `[E]`.

### Relación Padre (Opcional)
| Prioridad | Patrón buscado |
|---|---|
| P1 | `\| **Padre** \|` con valor `#[número]` o URL `.../edit/[número]` |
| P2 | `\| ⬆️ Parent \|` en tabla de relaciones |
| P3 | Omite la relación |

> **Regla de confianza (compuesta):** El nivel final es el **peor** entre la confianza de extracción y la confianza de narrativa.
> - Extracción Alta + Narrativa Alta → ✅ **Alta**
> - Cualquier componente en Media → ⚠️ **Media** (se muestra lista de advertencias en Vista Previa)
> - Beneficio ausente y usuario elige [F] → ⚠️ **Media** (queda registrado en sello local con nota `sin-beneficio`)
> - Campo obligatorio sin resolver → ❌ **Bloqueante** (no se puede publicar hasta resolverlo)

## Comando: PUBLICAR-HU [ruta_archivo_HU]

---

### Fase 1 — Parseo y Vista Previa Local (Cero Consumo ADO)

**A. Lectura del Archivo:**
1. Lee `[ruta_archivo_HU]` con `read/readFile`.
2. Detecta el formato (A o B según los identificadores descritos arriba).
3. Ejecuta la **Guardia Anti-Duplicado** (solo Formato A).

**B. Extracción de Campos:**
1. Aplica el **Mapa de Extracción — Estrategia Progresiva** para cada campo (P1→P2→P3→Fallback).
2. Convierte HTML a Markdown limpio si el campo viene en HTML.
3. Convierte la lista de criterios de aceptación a HTML de lista `<ul>` para el campo `AcceptanceCriteria` de ADO (ADO requiere HTML en ese campo).
4. Si la descripción contiene secciones adicionales relevantes (Consideraciones, Observaciones técnicas, Reglas de Negocio, Dependencias, etc.), las incluye dentro del campo `System.Description` como secciones HTML.
5. Registra internamente el **nivel de confianza de extracción** (Alta/Media) para mostrarlo en la vista previa.

**B.1 — Guardia de Valor:**
Ejecuta la **Guardia de Valor — Validación de Narrativa INVEST** sobre el texto extraído de `System.Description`. Sigue el protocolo definido en esa sección. Puede interrumpir el flujo para solicitar el beneficio antes de continuar.

**C. Solicitud de Campos Faltantes:**
Si faltan campos obligatorios o recomendados sin fallback disponible, detiene el flujo y pregunta:

> **🤷 Faltan campos requeridos para publicar la HU:**
> 1. **Iteration Path:** *(no encontrado)* → ¿A qué sprint/iteración pertenece?
>
> Ingresa los valores o responde **[C]** para cancelar.

**D. Tabla de Vista Previa:**
Muestra en el chat el resumen completo antes de tocar ADO:

```
📋 Vista Previa — HU a publicar en ADO
──────────────────────────────────────────
  Confianza       : ✅ Alta  /  ⚠️ Media
  Narrativa INVEST: ✅ Completa (Como/Quiero/Para)  /  ⚠️ Incompleta
  Título          : [Título extraído]
  Tipo            : User Story
  Iteration Path  : [Iteration Path]
  Prioridad       : [1-4]
  Story Points    : [N] o —
  Padre (ID ADO)  : #[ID] o Ninguno
──────────────────────────────────────────
  Descripción     : [Primeras 150 chars...]
  Criterios AC    : [N criterios detectados]
──────────────────────────────────────────
  ⚠️ Advertencias : [lista o Ninguna]
```

**E. Confirmación:**

> **🤷 ¿Publicamos esta HU en Azure DevOps?**
> - ✅ **[S]** Sí, crear en ADO
> - ✏️ **[E]** Editar un campo antes de publicar
> - 💾 **[L]** Solo guardar vista previa localmente (no publicar)
> - ❌ **[N]** Cancelar

---

### Fase 2 — Creación en ADO (Solo tras confirmación [S])

**A. Validación de Asignado:**
1. Invoca `ado/core_get_identity_ids` con `user_email` del perfil activo.
2. Si el email no existe en la organización:
   > ⚠️ El correo `{user_email}` no existe en la organización ADO.
   > 📧 Ingresa el correo válido del responsable:
   > ❌ [X] Cancelar
   - Si usuario ingresa un nuevo email, reintenta la validación.
   - Si cancela, continúa sin asignado.
3. Usa el email válido como `System.AssignedTo`.

**B. Creación del Work Item:**
1. Invoca `ado/wit_create_work_item` con tipo `User Story` y los campos mapeados:
   - `System.Title`
   - `System.Description` (HTML)
   - `Microsoft.VSTS.Common.AcceptanceCriteria` (HTML)
   - `System.AssignedTo` — email validado
   - `System.IterationPath`
   - `Microsoft.VSTS.Common.Priority`
   - `Microsoft.VSTS.Scheduling.StoryPoints` (si aplica)

**C. Vinculación de Padre (si existe):**
2. Si se detectó un ID de padre, invoca `ado/wit_works_items_link` o incluye la relación `System.LinkTypes.Hierarchy-Reverse` en la creación para vincularlo al padre.

**C. Reporte de Resultado:**
3. Si la creación es exitosa, muestra:

> ✅ **HU publicada exitosamente.**
> - **ID ADO:** #[NUEVO_ID]
> - **Enlace:** [Abrir en ADO](https://dev.azure.com/.../edit/[NUEVO_ID])
> - **Título:** [Título]
> - **Sprint:** [Iteration Path]

4. Si la creación falla, reporta el error específico de ADO y ofrece reintentar o cancelar.

---

### Fase 3 — Actualización del Archivo Local

**A. Sello de Publicación:**
1. Inserta al inicio del archivo local (justo bajo el H1 principal) el bloque de sello usando `assets/template-sello-ado.md` como referencia:

```markdown
> ✅ **Publicado en ADO** | **ID:** #[NUEVO_ID] | [Abrir en ADO](enlace) | **Fecha:** [YYYY-MM-DD]
```

2. Si el archivo era Formato B (borrador) y tenía `**ID Original:**` con un ID distinto, NO sobreescribe ese campo — añade el sello como bloque separado.

---

## Uso Standalone (sin Agent Suite)

Cuando el colaborador usa esta skill directamente sin el agente suite:

1. El colaborador provee la ruta al archivo HU en el chat:
   > "Publica esta HU: `/ruta/a/mi-proyecto/HU-002-simulacion-cdt.md`"

2. Si no hay perfil activo, la skill solicita solo los campos mínimos indispensables:
   - **Organización ADO** (URL base, ej: `https://dev.azure.com/MiOrganizacion`)
   - **Proyecto ADO** (nombre del proyecto)
   - **Iteration Path** (si no está en el archivo)

3. El flujo de fases es idéntico al descrito arriba.

---

## Gotchas

- **NUNCA crees el work item en ADO sin confirmación explícita [S].** La Fase 1 es solo parseo y vista previa local.
- La **Guardia Anti-Duplicado** es obligatoria. No saltarla aunque el usuario insista, salvo que confirme explícitamente querer crear una copia.
- `Microsoft.VSTS.Common.AcceptanceCriteria` en ADO requiere **HTML**, no Markdown. Convierte los checkboxes `- [ ]` a `<li>` dentro de `<ul>`.
- `System.Description` también requiere HTML en ADO. Usa `<h3>`, `<p>`, `<ul>`, `<li>`, `<strong>` para estructurar el contenido.
- Si el Título extraído supera 255 caracteres, trunca y avisa al usuario.
- Al insertar el sello en el archivo local, usa `edit/createFile` o `edit/editFiles` sobre el archivo existente — no crees un archivo nuevo.
- Si el ID de padre detectado no es un número puro (ej: `#96613` → toma `96613`), extrae solo los dígitos.
- La creación de tipo `User Story` puede variar por organización ADO. Si falla con ese tipo, intenta con `User Story` en español o consulta `ado/wit_get_work_item_type` para confirmar el nombre exacto.
