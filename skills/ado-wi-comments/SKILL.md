---
name: ado-wi-comments
description: >
  Registra comentarios estructurados en Work Items de Azure DevOps
  para el proyecto FINTIA. Úsala cuando necesites agregar un comentario
  de entrega (RELEASE, FEATURE, FIX, HOTFIX) o un comentario técnico
  general a un WI, incluyendo menciones a colaboradores y reasignación.
  No la uses para crear o modificar campos del WI (usar bmm-crear-hu-devops).
compatibility: Requires Azure DevOps MCP server configured
metadata:
  author: CEIBA DevOps
  version: 1.0.0
---

# Skill: ADO WI Comments

Gestiona comentarios y menciones en Work Items de Azure DevOps.

## Referencias

- Plantilla de entrega: `{file:./assets/plantilla-entrega.md}`

---

## Reglas Universales (aplican a todo comentario)

### Formato
- Todo comentario debe usar sintaxis limpia de Markdown.
- Enviar siempre el texto final como **texto plano Markdown directo** (sin envolver en bloques de código contenedores).
- La plataforma interpreta los estilos de forma nativa.

### Menciones ADO [OBLIGATORIO]

Antes de publicar **cualquier comentario**, preguntar siempre:

> **¿Deseas etiquetar a alguno de estos colaboradores en el comentario?**
> - **[A]** Edgar Alexander Torres Erazo → `@<96517b2d-3823-62fd-ae74-0872c1c9c3a9>`
> - **[L]** Lady Marcela Suarez Agudelo → `@<7c277620-4b79-652b-a18d-5d93dd85fff6>`
> - **[AL]** Ambos
> - **[N]** Ninguno

Insertar las menciones seleccionadas **al inicio del comentario**, antes del cuerpo principal. Usar siempre el formato de ID de ADO `@<GUID>` para que la plataforma resuelva la mención nativa correctamente.

### Reasignación Automática [OBLIGATORIO]

Si el usuario selecciona etiquetar a **Alexander** (`[A]` o `[AL]`), inmediatamente después de publicar el comentario, **reasignar el WI** a Edgar Alexander Torres Erazo:

```
wit_update_work_item:
  id: [WI_ID]
  updates:
    - path: "/fields/System.AssignedTo"
      value: "ettorres@bmm.com.co"
```

Notificar al usuario: "Responsable actualizado a Edgar Alexander Torres Erazo."

---

## Caso A: Comentarios de Entrega Formal

Aplica cuando el usuario solicite un comentario de entrega (`RELEASE`, `FEATURE`, `FIX`, `HOTFIX`).

### Configuración Dinámica

| Campo | Regla |
|-------|-------|
| Emoji | `🔧` para FIX · `🚨` para HOTFIX · `🚀` para RELEASE/FEATURE |
| Rama | Si no hay `{rama_origen}`, eliminar su línea de la plantilla |
| Fecha | Insertar automáticamente la fecha actual `{YYYY-MM-DD}` |

### Flujo

#### Paso 1 — Recopilar datos

Solicitar al usuario:
1. Tipo de entrega (RELEASE, FEATURE, FIX, HOTFIX)
2. Versión (ej: v2.2.3)
3. Nombre del repo
4. Rama origen (opcional)
5. Breve descripción de los cambios
6. Lista de cambios (feat, fix, chore, etc.)
7. Ruta de entrega de artefactos
8. Notas adicionales (opcional)

#### Paso 2 — Generar plantilla

Usar la plantilla de `{file:./assets/plantilla-entrega.md}` con los datos recopilados.

#### Paso 3 — Preview y Aprobación

Mostrar el código crudo en un bloque `` ```markdown `` y solicitar confirmación:

> **¿El formato Markdown del comentario de entrega es correcto?**
> - **[C]** Confirmar y continuar
> - **[E]** Editar datos

#### Paso 4 — Mención posterior

Tras confirmar con `[C]`, aplicar el flujo de menciones definido en **Reglas Universales §Menciones ADO**.

#### Paso 5 — Publicar comentario

Usar `wit_work_item_comment_write`:
```
action: add
workItemId: [WI_ID]
text: [contenido Markdown generado]
format: Markdown
```

---

## Caso B: Comentarios Generales y Técnicos

Aplica para cualquier anotación, duda, tarea o actualización en el WI que no sea entrega formal.

### Flujo

#### Paso 1 — Diseñar mensaje

Estructurar el mensaje usando títulos, negritas o viñetas según amerite el texto.

#### Paso 2 — Preview Obligatorio

Mostrar el texto final crudo dentro de un bloque `` ```markdown `` y solicitar validación:

> **¿El formato de este comentario es correcto antes de publicarlo?**
> - **[C]** Confirmar e insertar comentario
> - **[E]** Editar el contenido

#### Paso 3 — Mención posterior

Tras confirmar con `[C]`, aplicar el flujo de menciones definido en **Reglas Universales §Menciones ADO**.

#### Paso 4 — Publicar comentario

Usar `wit_work_item_comment_write`:
```
action: add
workItemId: [WI_ID]
text: [contenido Markdown generado]
format: Markdown
```

---

## Reglas obligatorias

1. **Mención siempre.** Preguntar por Alexander y/o Lady antes de cada comentario.
2. **Reasignar si Alexander.** Si se menciona a Alexander, reasignar el WI inmediatamente.
3. **Preview antes de publicar.** Nunca publicar sin aprobación del usuario.
4. **Markdown plano.** No envolver en bloques de código contenedores.
5. **Fecha automática.** Insertar fecha actual en comentarios de entrega.

---

## Gotchas

- **Mención no resuelta:** Si el GUID de ADO no resuelve, usar el formato `@nombre@dominio.com` como fallback.
- **Comentario muy largo:** Si el comentario excede 4000 caracteres, dividir en múltiples comentarios.
- **WI cerrado:** No se pueden agregar comentarios a WIs cerrados. Informar al usuario.
- **Reasignación fallida:** Si la reasignación falla (permisos), notificar pero no bloquear la publicación del comentario.

---