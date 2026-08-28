---
name: pdf-from-markdown
description: >
  Usa esta skill cuando el usuario mencione convertir markdown a PDF,
  exportar documento como PDF, generar PDF desde Mermaid o renderizar
  diagramas a PDF.
ready: true
---

# PDF from Markdown

## Overview

Convierte archivos Markdown a PDF, pre-renderizando bloques Mermaid como imágenes. Soporta exportación de documento completo o diagramas individuales.

## When to Use

**Activar cuando:**
- El usuario quiere convertir un archivo `.md` a PDF
- Se necesita exportar un documento con diagramas Mermaid a PDF
- Se solicita generar PDFs individuales por diagrama

**NO activar cuando:**
- El usuario solo quiere visualizar el Markdown sin exportar (usar preview del editor)
- No está instalado Node.js ni `@mermaid-js/mermaid-cli` (verificar antes de ejecutar)

## Implementation

**Script principal:** `scripts/generate_pdf.sh` — Renderiza un archivo `.mmd` a PDF via Mermaid CLI. Ejecutar con `--help` para uso.

**Modos disponibles:**

| User intent | Modo |
|---|---|
| "Convertir markdown a PDF" / "Exportar documento como PDF" | **A — Full Document** |
| "Generar PDFs de los diagramas" / "Extraer diagramas como PDF" | **B — Diagram-Only** |
| Ambiguo | Default **A** (full document) |

### Modo A — Documento Completo

1. Leer Markdown original → crear `temp_build.md`
2. Extraer cada bloque ` ```mermaid ``` ` → renderizar a PNG con `bash scripts/generate_pdf.sh temp_diag_<index>.mmd temp_diag_<index>.png`
3. Reemplazar bloques mermaid con `![Diagram](./temp_diag_<index>.png)`
4. Compilar: `npx md-to-pdf temp_build.md`
5. Renombrar output → limpiar temporales

### Modo B — Diagramas Individuales

1. Escanear bloques ` ```mermaid ``` ` en el Markdown
2. Nombrar cada output con heading precedente (snake_case)
3. Renderizar cada diagrama con `bash scripts/generate_pdf.sh temp_diagram_<index>.mmd <output_name>.pdf`
4. Insertar enlace `[📄 Ver diagrama en PDF](./<output_name>.pdf)` después de cada bloque
5. Limpiar temporales

## Quick Reference

| Comando | Descripción |
|---------|-------------|
| `bash scripts/generate_pdf.sh input.mmd output.pdf` | Renderiza un diagrama a PDF |
| `bash scripts/generate_pdf.sh input.mmd output.png` | Renderiza un diagrama a PNG |
| `npx md-to-pdf temp_build.md` | Compila Markdown completo a PDF |

## Common Mistakes

- `mmdc` produce PNG por defecto con extensión `.png` — no forzar `-e png`, basta con nombrar el archivo de salida con `.png`
- `npx md-to-pdf` descarga la dependencia al vuelo — no requiere `npm install` previo
- No usar `npx mmdc` a secas — el paquete correcto es `@mermaid-js/mermaid-cli` (el script bundled ya maneja esto)
- Siempre limpiar archivos temporales `.mmd` y `.png` intermedios
