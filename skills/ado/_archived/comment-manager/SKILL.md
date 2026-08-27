---
name: ado-comment-manager
description: >
  Lee y agrega comentarios en Work Items de Azure DevOps. Muestra todo el
  historial de comentarios con autor y fecha, detecta adjuntos e imágenes
  en comentarios, y al final pregunta si se desea agregar un nuevo comentario.
  También lista los adjuntos (archivos, imágenes, documentos) vinculados al WI.
  Usa esta skill cuando el usuario pida ver comentarios de un work item,
  agregar un comentario, revisar el historial, o ver adjuntos de un WI.
  Also triggers on: ver comentarios, historial WI, agregar comentario,
  mostrar adjuntos, attachments del work item, discusión del ítem.
compatibility: Requires Azure DevOps MCP server configured
---
## Contexto
- project_name — proyecto ADO
- user_email — email del perfil activo

## Comando: COMENTARIOS [ID]

### Fase 1 — Obtener Comentarios
1. Invoca ado/wit_list_work_item_comments con [ID].
2. Muestra cada comentario en orden cronológico:
   | # | Fecha | Autor | Comentario |
   - Si el comentario contiene URLs o etiquetas <img>, indica que tiene imágenes embebidas.
   - Si el comentario es muy extenso (>500 chars), muestra un resumen y pregunta si verlo completo.

### Fase 2 — Adjuntos del WI
1. Invoca ado/wit_get_work_item con [ID] para obtener relaciones.
2. Revisa el campo Relations buscando tipo AttachedFile.
3. Si hay adjuntos, listarlos:
   | Archivo | Tipo | URL |
   - Imágenes: muestrar que son imágenes (no se pueden previsualizar en chat).
   - Documentos/PDFs/etc: indicar nombre y tipo.
4. Si no hay adjuntos: "📎 Sin adjuntos."

### Fase 3 — Agregar Comentario
1. Preguntar:
   > 📝 ¿Quieres agregar un comentario a este WI?
   > - ✅ [S] Sí
   > - ❌ [N] No
2. Si [S]:
   - Solicitar el texto del comentario.
   - Preguntar si debe etiquetar a alguien:
     > 🏷️ ¿Quieres etiquetar a alguien en el comentario?
     > - ✅ [S] Sí
     > - ❌ [N] No
   - Si [S]: preguntar nombre o correo y agregar la etiqueta en el texto con formato @<{nombre o correo}>.
   - Aplicar formato coloquial consistente:
     <p><b>💬 Asunto:</b> [línea corta con el motivo]</p>
     <p>[cuerpo del comentario con <b>negritas</b> si aplica]</p>
   - Invoca ado/wit_add_work_item_comment con [ID] y el texto en HTML.
   - Confirmar: ✅ Comentario agregado a #{ID}.

## Gotchas
- Los comentarios pueden contener HTML (img, a, etc.). Limpiar o mostrar inline.
- Si un comentario tiene una imagen embebida vía <img>, indicar que hay una imagen sin poder renderizarla.
- Los adjuntos tipo AttachedFile en Relations pueden tener URLs directas de descarga.
- No descargar archivos adjuntos sin preguntar al usuario.
- Si el WI no tiene comentarios, indicar: "💬 Sin comentarios."
