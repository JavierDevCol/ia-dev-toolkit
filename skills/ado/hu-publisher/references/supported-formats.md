# Supported HU Formats

## Format A — ADO pull output

Identified by: presence of `🔗 **ADO**` or `| **ID** | [number] |` with a valid numeric ID in the technical sheet table.

**Anti-duplicate guard mandatory:** If the file already contains a real ADO ID in the technical sheet or a link `dev.azure.com/.../_workitems/edit/[ID]`, the skill **stops creation** and offers:
- **[U]** Update the existing work item in ADO
- **[N]** Cancel — do nothing
- **[V]** View current state in ADO only

## Format B — Local draft

Identified by: absence of a real ADO ID. May contain `**ID Original:**` as historical reference — this is **not** treated as an existing ADO ID. Patterns:
- `# Historia #[Local-Code]:` or `# 📘 User Story — [Title]` (no ADO number)
- No `dev.azure.com/.../edit/[number]` link with real ID

## Format C — Freeform / minimal

Identified by: none of the above patterns. Agent applies **progressive extraction** (see extraction-map.md) and always shows the preview with a low-confidence warning before allowing publication.
