# ADO Process Detection

Required before mapping estimation fields. The estimation field varies by ADO process:

| Process | Estimation Field | ADO Field Name |
|---------|-----------------|----------------|
| **Agile** | Story Points (abstract) | `Microsoft.VSTS.Scheduling.StoryPoints` |
| **Scrum** | Effort (hours) | `Microsoft.VSTS.Scheduling.Effort` |
| **CMMI** | Size (points) | `Microsoft.VSTS.Scheduling.Size` |

## Detection Protocol

1. **Local cache first:** If `config_extras.ado_process` exists (`agile`, `scrum`, or `cmmi`) → use directly, skip ADO query.
2. **Fallback to ADO:** Invoke `ado_wit_work_item_type` for `User Story` in active project. Look for `processName` or field namespace prefix in response.
3. **Persist:** Save detected value to `config_extras.ado_process` in the active profile to avoid future queries.
4. **Final fallback:** If detection fails, assume `agile` and warn user in preview:
   > `⚠️ Could not detect ADO process. Assuming Agile (StoryPoints). Verify with [E] if incorrect.`

## Impact on Estimation Value

- **Agile:** Send derived value in SP (integer, result of hours / conversion factor).
- **Scrum:** Send total hours directly (e.g. `3.2`) — no SP conversion.
- **CMMI:** Treated like Agile (abstract points).
