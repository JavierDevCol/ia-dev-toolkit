## 🔍 Reporte de Revisión: PR #[number]

> 🚨 **NOTA PARA EL AGENTE:** Este reporte es temporal. Cuando el autor del PR resuelva
> los comentarios de corrección agregados por el revisor, **eliminar este archivo
> automáticamente** y confirmar al usuario: `🗑️ Reporte de revisión PR #[number]
> eliminado — comentarios resueltos.` (GitHub REST no expone estado resuelto/no-resuelto
> por thread — usar criterio manual o el conteo de comentarios nuevos del autor.)

> **[VEREDICTO_EMOJI] [VEREDICTO_TEXTO]**
> 📅 Fecha: `[timestamp]` | 👤 Revisado por: `[reviewer_login]` | 📂 Autor del PR: `[user.login]`

---

### 📌 Información del PR

| Campo | Valor |
|-------|-------|
| **Título** | [title] |
| **Autor** | [user.login] |
| **Rama** | `[head.ref]` → `[base.ref]` |
| **Estado** | [state] |
| **Merge** | [mergeable_state_emoji] [mergeable_state] |
| **Antigüedad** | [X] días abierto |
| **Issues vinculados** | [Closes/Fixes #N detectados en el body, o "Ninguno"] |
| **Labels** | [labels o "Sin labels"] |

---

### 📁 Archivos modificados

| Tipo | Archivo |
|------|---------|
| [added/modified/removed/renamed] | `[filename]` |

**Total:** [X] archivos ([Y] añadidos, [Z] modificados, [W] eliminados)

---

### 📝 Commits incluidos

| SHA corto | Mensaje | Autor |
|-----------|---------|-------|
| `[sha_corto]` | [mensaje_commit] | [autor] |

---

### 🏗️ Validación de Estándares

> 📄 Fuente: `[coding_standards_path]` + `[architecture_guide_path]`

#### Metadatos del PR

| # | Estándar | Estado | Detalle |
|---|----------|--------|---------|
| 1 | [Convención de ramas / Commits / Descripción] | [🔴/🟡/🟢] | [Explicación breve] |

#### Código modificado

| # | Archivo | Línea | Regla violada | Severidad | Fragmento |
|---|---------|-------|---------------|-----------|-----------|
| 1 | `[filename]` | L[N] | [Nombre regla del estándar] | [🔴/🟡] | `[fragmento_codigo_breve]` |

**Resumen:** 🟢 [X] Conforme | 🟡 [X] Advertencias | 🔴 [X] Violaciones

---

### ⚡ Conflictos de Merge

<!-- Si no hay conflictos: -->
<!-- 🟢 **Sin conflictos de merge detectados.** -->

<!-- Si hay conflictos: GitHub REST solo da el agregado mergeable_state=dirty,
     sin detalle por línea. Reportar el hecho, no inventar detalle que la API no da: -->
<!-- 🔴 **Conflictos detectados.** Resolución manual requerida (rebase/merge local). -->

---

### 💬 Comentarios de revisión

| Tipo | Cantidad |
|------|----------|
| Inline (anclados a código) | [X] |
| Generales (issue comments) | [X] |
| **Total** | [X] |

> Nota: sin distinción resuelto/no-resuelto (limitación de la REST API — ver "Known gap" en SKILL.md).

---

### 🏥 Salud General del PR

| Indicador | Estado |
|-----------|--------|
| Conflictos de merge | [🟢/🔴] [Sin conflictos / Conflictos detectados] |
| Cumplimiento de estándares | [🟢/🟡/🔴] [Conforme / Con advertencias / Violaciones] |
| Comentarios de revisión | [🟢/🟡] [X registrados] |
| Antigüedad del PR | [🟢/🟡/🔴] [<3 días / 3-7 días / >7 días] |
| Coherencia título-descripción | [🟢/🟡] [Coherente / Mejorable] |

---

### 🎯 Veredicto

**[VEREDICTO_EMOJI] [VEREDICTO_TEXTO]**

[Resumen ejecutivo del análisis: 2-3 líneas con los hallazgos principales y la recomendación.]

<!-- Si hay revisión previa pendiente del mismo PR: -->
<!-- > 📂 **Revisión previa registrada:** [fecha_previa] — [motivo_previo] -->
