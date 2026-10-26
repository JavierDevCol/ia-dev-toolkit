## 🔍 Reporte de Revisión: PR #[PR_ID]

> 🚨 **NOTA PARA EL AGENTE:** Este reporte es temporal. Cuando el autor del PR resuelva
> todos los comentarios de corrección agregados por el revisor (todos los threads
> creados pasen a estado `Fixed` o `Closed`), **eliminar este archivo automáticamente**
> y confirmar al usuario: `🗑️ Reporte de revisión PR #[PR_ID] eliminado — todos los
> comentarios fueron resueltos.`

> **[VEREDICTO_EMOJI] [VEREDICTO_TEXTO]**
> 📅 Fecha: `[timestamp]` | 👤 Revisado por: `[user_email]` | 📂 Autor del PR: `[createdBy.uniqueName]`

---

### 📌 Información del PR

| Campo | Valor |
|-------|-------|
| **Título** | [Título del PR] |
| **Autor** | [createdBy.displayName] (`[createdBy.uniqueName]`) |
| **Rama** | `[sourceRefName]` → `[targetRefName]` |
| **Estado** | [status] |
| **Merge** | [mergeStatus_emoji] [mergeStatus] |
| **Antigüedad** | [X] días abierto |
| **Work Items** | [IDs vinculados o "Ninguno"] |
| **Labels** | [Labels o "Sin labels"] |

---

### � Archivos modificados

| Tipo | Archivo |
|------|---------|
| [A/M/D/R] | `[ruta/archivo]` |

**Total:** [X] archivos ([Y] añadidos, [Z] modificados, [W] eliminados)

---

### �📝 Commits incluidos

| Hash | Mensaje | Autor |
|------|---------|-------|
| `[hash_corto]` | [mensaje_commit] | [autor] |

---

### 🏗️ Validación de Estándares

> 📄 Fuente: `[base_reports_path]/architecture/coding-standards.md` + `architecture_[nombre_del_repo].md`

#### Metadatos del PR

| # | Estándar | Estado | Detalle |
|---|----------|--------|---------|
| 1 | [Convención de ramas / Commits / Descripción] | [🔴/🟡/🟢] | [Explicación breve] |

#### Código modificado

| # | Archivo | Línea | Regla violada | Severidad | Fragmento |
|---|---------|-------|---------------|-----------|----------|
| 1 | `[ruta/archivo]` | L[N] | [Nombre regla del estándar] | [🔴/🟡] | `[fragmento_codigo_breve]` |

**Resumen:** 🟢 [X] Conforme | 🟡 [X] Advertencias | 🔴 [X] Violaciones

---

### ⚡ Conflictos de Merge

<!-- Si no hay conflictos: -->
<!-- 🟢 **Sin conflictos de merge detectados.** -->

<!-- Si hay conflictos (detalle de merge-tree): -->
<!-- 🔴 **Conflictos detectados en [X] archivos:** -->

| # | Archivo | Sección afectada | Causa probable |
|---|---------|-----------------|----------------|
| 1 | `[ruta/archivo]` | Líneas [N-M] | [Ambas ramas modificaron la misma sección / etc.] |

<!-- Para cada conflicto, mostrar el fragmento: -->
<!-- ```diff -->
<!-- <<<<<<< origin/[target] -->
<!-- [código de target] -->
<!-- ======= -->
<!-- [código de source] -->
<!-- >>>>>>> origin/[source] -->
<!-- ``` -->
<!-- Sugerencia de resolución: [si es evidente] -->

---

### 💬 Threads de discusión

| Estado | Cantidad |
|--------|----------|
| 🔴 Sin resolver (`Active`/`Pending`) | [X] |
| 🟢 Resueltos (`Fixed`/`Closed`) | [X] |
| **Total** | [X] |

[Si hay threads sin resolver, listar los más relevantes:]
<!-- | Thread ID | Autor | Extracto | Estado | -->
<!-- |-----------|-------|----------|--------| -->

---

### 🏥 Salud General del PR

| Indicador | Estado |
|-----------|--------|
| Conflictos de merge | [🟢/🔴] [Sin conflictos / Conflictos detectados] |
| Cumplimiento de estándares | [🟢/🟡/🔴] [Conforme / Con advertencias / Violaciones] |
| Threads sin resolver | [🟢/🟡/🔴] [0 pendientes / X pendientes / X+ pendientes] |
| Antigüedad del PR | [🟢/🟡/🔴] [<3 días / 3-7 días / >7 días] |
| Coherencia título-descripción | [🟢/🟡] [Coherente / Mejorable] |

---

### 🎯 Veredicto

**[VEREDICTO_EMOJI] [VEREDICTO_TEXTO]**

[Resumen ejecutivo del análisis: 2-3 líneas con los hallazgos principales y la recomendación.]

<!-- Si hay revisión previa pendiente del mismo PR: -->
<!-- > 📂 **Revisión previa registrada:** [fecha_previa] — [motivo_previo] -->
