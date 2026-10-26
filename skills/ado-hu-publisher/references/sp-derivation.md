# Story Point Derivation (Parametrized)

All derivation rules are driven by `config_extras`. No project-specific methods are hardcoded.

## Configuration Keys

| Key | Purpose | Default |
|-----|---------|---------|
| `config_extras.estimation_method` | Name of the estimation method (display only) | `"default"` |
| `config_extras.estimation_role` | Role column to read from estimation table | `"Senior"` |
| `config_extras.horas_por_sp` | Hours-per-Story-Point conversion factor (Agile/CMMI) | `4` |
| `config_extras.manual_task_column` | Column header for manual tasks in estimation table | `"Tareas Manuales"` |
| `config_extras.method_column` | Column header for the estimation method values | derived from `estimation_method` |
| `config_extras.complexity_sp` | Map of complexity labels to SP values | `{"LOW":1, "MEDIUM":3, "HIGH":8, "VERY HIGH":13}` |

## Derivation Priority (matches extraction-map.md P2)

### P1 — Direct value
User provided explicit `| **Story Points** |` in a table. Use as-is.

### P2 — Estimation table derivation
1. Read total hours from the estimation table for the configured role (`config_extras.estimation_role`).
2. If `⏱ Tiempo comprometido por desarrollador` row exists, use it as total committed time.
3. Otherwise compute: `[method column for role] + [manual task column total]`.
4. Apply ADO process (see process-detection.md):
   - **Agile/CMMI:** Convert: `hours / config_extras.horas_por_sp`, round to nearest integer ≥ 1 → send to `StoryPoints`.
   - **Scrum:** Send total hours directly to `Effort` without conversion.

### P3 — Complexity mapping
Read `**Complexity:**` field, map via `config_extras.complexity_sp` (or defaults).

### P4 — Omit
Don't send estimation field to ADO.

## Transparency

If value was derived (P2 or P3, not explicit P1), show in preview:
> `Story Points: N ⚙️ (derived from [estimation_method] — [role] Xh / [h_per_sp]h per SP)`
