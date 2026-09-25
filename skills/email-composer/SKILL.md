---
name: email-composer
license: MIT
description: "Use to generate the HTML content of an outgoing email, color-coded by type (laboral, comunicado, urgente). Content-only — sending or draft creation is handled by a separate skill or tool."
tags: [email, html, templates, compose]
---

# Email Composer

Generates the finished HTML content for an email, ready to paste into Gmail (or any client). This skill only produces HTML — it never sends email or creates drafts itself.

## Core Rules

1. **Output is HTML only.** This skill does not send email or create drafts in Gmail or any other client.
2. Ask for the real content before generating — never fill blocks with placeholder text as the final output.
3. Pick blocks based on the email's purpose (informativo, decisión, sincronización, ...) — add or omit freely, there is no fixed section list.
4. Show the generated HTML plus a plain-text summary of its content before considering the task done.

## Email Types

Sets the header banner color only — it doesn't constrain which blocks you use. Every type uses the same signature (see Signature below).

| Type | Header color |
|---|---|
| laboral | #4169E1 |
| comunicado | #50C878 |
| urgente | #DC143C |

## Block Types

Each email is an ordered list of blocks. Use whichever mix fits the content — a sync update might be `text` + `table` + `list`; a decision request might be `text` + `callout` + `card`.

| Type | Use for | Key fields |
|---|---|---|
| `text` | Greeting, plain paragraphs, closing | `content` (html) |
| `heading` | Numbered section title (like a report) | `title`, `number` (optional), `content` (optional paragraph below) |
| `callout` | Something that needs to stand out | `variant` (`amber`=decisión/nota, `red`=riesgo/bloqueo, `green`=resuelto/ok, `blue`=informativo), `label`, `content` |
| `table` | Comparable/structured data (status, estimates) | `headers` (list), `rows` (list of lists) |
| `card` | One bordered unit of detail (e.g. one task) — nest a `render_callout(...)` inside `content` if it has a risk/decision | `title`, `content` (html) |
| `list` | Bullet points | `items` (list of str) |

## Three-Layer Flow

1. **This file (SKILL.md)** — process only: what to ask, what to show, which blocks fit which purpose. Never contains markup.
2. **`build_email_html.py`** — reusable base: `COLORS` map, `render_email(email_type, header, blocks)`, and `render_callout(variant, label, content)` for nesting a callout inside a card. Reads `templates/*.html` and returns the finished HTML string.
3. **Custom script per email** — written fresh for each request: imports from `build_email_html.py`, builds the `header` and the exact list of `blocks` this email needs, and prints/saves the resulting HTML. This is the final deliverable — nothing is sent or drafted.

## Procedure

### Step 1: Detect Intent

When the user wants to compose an email, ask:
1. What type? (laboral/comunicado/urgente)
2. Purpose: informativo, sincronización, solicitud de decisión, etc. — this drives which blocks to use.
3. Subject / header (kicker, title, subtitle)
4. Key content per block (what's structured data → `table`, what's a risk/decision → `callout`, what's per-item detail → `card`)

### Step 2: Build HTML

Write a custom script per email (layer 3) that imports from `build_email_html.py` in this skill's directory and calls it with the real content:

```python
from build_email_html import render_email, render_callout

html = render_email(
    email_type="laboral",
    header={"kicker": "Equipo X", "title": "Estado de bloqueos", "subtitle": "Corte al 25 de septiembre"},
    blocks=[
        {"type": "text", "content": "Buen día, equipo:"},
        {"type": "heading", "number": 1, "title": "Resumen", "content": "..."},
        {"type": "table", "headers": ["Tarea", "Estado"], "rows": [["#123", "En revisión"]]},
        {"type": "card", "title": "#123 — Detalle", "content": "..." + render_callout("red", "Riesgo.", "...")},
        {"type": "text", "content": "Saludos,"},
    ],
)
print(html)
```

### Step 3: Deliver

Show the generated HTML to the user (or save it to a `.html` file if they want to paste it elsewhere), along with:

```
📋 Asunto: [title]

📝 CONTENIDO:
• [block 1 summary]
• [block 2 summary]
• ...
```

## Signature

Same signature for every email type, appended automatically by `render_email` — never pass or choose one:

```
Javier Brandon García Maldonado
Arquitecto(a) Desarrollador(a) · Ceiba Software
Tel: Medellín (+57)604-444-5111 || Cel: (+57)3105789665
```

## Pitfalls

- This skill only outputs HTML — it never sends email or creates drafts anywhere.
- Never ship placeholder text as final content — always fill blocks with the real information the user gave you.
- Don't force every email into the same block sequence — an informativo email and a decisión email should look different.
- Show the full HTML/summary before considering the task done.
- Check that the HTML renders correctly (no broken tags).
