---
name: pdf-from-markdown
description: >
  Convert Markdown documents and Mermaid diagrams to PDF. Two modes:
  (A) Full-document export — compiles an entire Markdown file (with embedded
  Mermaid diagrams rendered as images) into a single PDF.
  (B) Diagram-only export — extracts each Mermaid diagram from a Markdown file,
  generates an individual PDF per diagram, and inserts download links back into
  the source file.
  Use this skill when the user mentions: convert markdown to PDF, export document
  as PDF, generate PDF from Mermaid, render diagrams to PDF, or any combination
  of Markdown/Mermaid and PDF output.
compatibility: Requires Node.js, @mermaid-js/mermaid-cli
metadata:
  author: javier.garcia
  version: "2.0"
---

# PDF from Markdown

## Available Scripts

- **`scripts/generate_pdf.sh`** — Renders a single `.mmd` file to PDF via Mermaid CLI. Run with `--help` for usage.

## Decide Which Mode to Use

| User intent | Mode |
|---|---|
| "Convert this markdown to PDF" / "Export document as PDF" | **A — Full Document** |
| "Generate PDFs of the diagrams" / "Extract diagrams as PDF" | **B — Diagram-Only** |
| Ambiguous | Default to **A** (full document). |

---

## Mode A — Full Document to PDF

Converts the entire Markdown file into a single PDF, pre-rendering any Mermaid blocks as PNG images so they appear correctly in the output.

### Steps

1. **Read** the original Markdown file.
2. **Create working copy** named `temp_build.md` in the same directory.
3. **Extract and render diagrams** — for each ` ```mermaid ``` ` block:
   - Save the code to `temp_diag_<index>.mmd`.
   - Render to PNG:
     ```bash
     bash scripts/generate_pdf.sh temp_diag_<index>.mmd temp_diag_<index>.png
     ```
     > If the output extension is `.png`, mmdc produces a PNG automatically.
4. **Embed images** — replace each mermaid block in `temp_build.md` with:
   ```
   ![Diagram](./temp_diag_<index>.png)
   ```
5. **Compile PDF**:
   ```bash
   npx md-to-pdf temp_build.md
   ```
   This produces `temp_build.pdf`.
6. **Rename** `temp_build.pdf` → `<original-name>.pdf`.
7. **Clean up** — delete `temp_build.md`, all `.mmd` and `.png` temp files.
8. **Notify** the user with the path of the final PDF.

---

## Mode B — Individual Diagram PDFs

Extracts each Mermaid diagram from a Markdown file, generates one PDF per diagram, and inserts a link in the source file.

### Steps

1. **Scan** the Markdown file for all ` ```mermaid ``` ` blocks.
2. **Name each output** based on the nearest preceding heading (snake_case). Example: heading "1. Vista General" → `vista_general.pdf`.
3. **Process each diagram**:
   - Save to `temp_diagram_<index>.mmd`.
   - Run:
     ```bash
     bash scripts/generate_pdf.sh temp_diagram_<index>.mmd <output_name>.pdf
     ```
4. **Insert link** — immediately after the closing ` ``` ` of each mermaid block, add:
   ```
   [📄 Ver diagrama en PDF](./<output_name>.pdf)
   ```
5. **Clean up** — delete all `temp_diagram_*.mmd` files.
6. **Notify** the user that the Markdown was updated with PDF links.

### Example

**Before:**
```markdown
### 1. Arquitectura Base
` ``mermaid
graph TD;
    A-->B;
` ``
```

**After:**
```markdown
### 1. Arquitectura Base
` ``mermaid
graph TD;
    A-->B;
` ``
[📄 Ver diagrama en PDF](./arquitectura_base.pdf)
```

---

## Gotchas

- **mmdc produce PNG por defecto con extensión .png** — no forzar `-e png`, basta con nombrar el archivo de salida con `.png`.
- **`npx md-to-pdf` descarga la dependencia al vuelo** si no está instalada globalmente — no requiere `npm install` previo.
- **No uses `npx mmdc` a secas** — el paquete correcto es `@mermaid-js/mermaid-cli`. El script bundled ya maneja esto.
- **Limpia siempre los temporales** — los archivos `.mmd` y `.png` intermedios no deben quedar en el workspace del usuario.
