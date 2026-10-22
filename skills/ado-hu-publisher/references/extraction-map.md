# Field Extraction Map — Progressive Strategy

For each field, try patterns in priority order (P1 → P2 → P3 → Fallback). First non-empty value wins.

## System.Title (Required)

| Priority | Pattern |
|----------|---------|
| P1 | Value in `| **Title** |` cell of technical sheet table |
| P2 | H1 heading text (`# ...`), stripping emojis, `#ID` prefixes, and `—` |
| P3 | First significant H2 heading if no meaningful H1 |
| ❌ Fail | Ask user to enter title manually |

## System.Description (Required)

| Priority | Pattern |
|----------|---------|
| P1 | Section under `## Historia de Usuario` (As a/I want/So that narrative) + Description, Business Rules, Technical Observations, Dependencies sections |
| P2 | Section under `## 📝 Descripción` or `## Descripción` |
| P3 | Entire file text excluding acceptance criteria, relations, and metrics |
| ❌ Fail | Ask user to confirm if remaining content is the description |

**After extraction:** Run the INVEST narrative guard (see invest-guard.md).

## Microsoft.VSTS.Common.AcceptanceCriteria (Required)

| Priority | Pattern |
|----------|---------|
| P1 | Section under `## Criterios de Aceptación` / `## ✅ Criterios de Aceptación` — items `- [ ]` or `- [x]` |
| P2 | Section under `## Criterios` (any variant without emoji) |
| P3 | BDD scenarios under `### Escenario N:` — group as numbered list |
| ❌ Fail | **Blocks publication.** No acceptance criteria = no coherent HU. |

## System.IterationPath (Recommended)

| Priority | Pattern |
|----------|---------|
| P1 | `| **Iteration Path** |` in table |
| P2 | `config_extras.default_iteration` or `default_sprint` from active profile |
| P3 | Ask user |

## Microsoft.VSTS.Common.Priority — Default: `2`

| Priority | Pattern |
|----------|---------|
| P1 | `| **Priority** |` in table |
| P2 | `2` (silent default) |

## Story Points (Optional)

See [sp-derivation.md](sp-derivation.md) for the full derivation logic.

| Priority | Pattern |
|----------|---------|
| P1 | `| **Story Points** |` or `| Story Points |` in any table — direct numeric value |
| P2 | Config-driven estimation table — see sp-derivation.md |
| P3 | `**Complexity:**` field — map via `config_extras.complexity_sp` or defaults: LOW→1, MEDIUM→3, HIGH→8, VERY HIGH→13 |
| P4 | Omit field (don't send to ADO) |

**Transparency:** If derived (not explicit), show note in preview: `Story Points: N ⚙️ (derived from estimation table)`

## Parent Relation (Optional)

| Priority | Pattern |
|----------|---------|
| P1 | `| **Padre** |` with `#[number]` or URL `.../edit/[number]` |
| P2 | `| ⬆️ Parent |` in relations table |
| P3 | Omit relation |

## Confidence Level (Composite)

Final confidence = worst of extraction confidence and narrative confidence:
- Extraction High + Narrative High → ✅ **High**
- Any Medium component → ⚠️ **Medium** (list warnings in preview)
- Missing benefit + user chose [F] → ⚠️ **Medium** (stamp with `sin-beneficio` note)
- Required field unresolved → ❌ **Blocking** (cannot publish)
