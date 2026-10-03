---
target_path: "./artifacts/HU/enablers/EPIC-ENABLER-02.md"
type: enabler_epic
---

# 🧱 Épica Enabler: Integración de Mensajería (WhatsApp Click-to-Chat)

- **ID:** `EPIC-ENABLER-02`
- **Origen Arquitectónico:** ADR-001 (Estilo Arquitectónico), ADR-004 (Protocolos de Comunicación)
- **Objetivo:** Construir el componente técnico reutilizable que arma el enlace `wa.me` con el mensaje prellenado (pedido o consulta), correctamente codificado, para que todas las HUs de negocio que envían algo a WhatsApp lo reutilicen sin duplicar lógica.

---

## ⚙️ Features Enablers Contenidas

### Feature: Generador de Enlace WhatsApp con Mensaje Prellenado
- **ID:** `FEAT-ENABLER-03`
- **Descripción:** Función JavaScript (`pedido.js`) que recibe una lista de productos/cantidades y datos del cliente (o un texto libre de consulta) y devuelve una URL `https://wa.me/<numero>?text=<mensaje-url-encoded>` lista para abrir en una nueva pestaña/intent del sistema operativo.

---

## 📜 Historias Enablers Refinadas

### `STORY-ENABLER-03` (Arquitectura / Backend — en este proyecto, lógica de cliente en JS)
- **Rol:** As Software Developer
- **Necesidad:** Implementar la función que arma el link `wa.me` con el detalle del pedido (productos, cantidades, nombre del cliente, notas) o de la consulta general, aplicando `encodeURIComponent` correctamente sobre acentos, saltos de línea y caracteres especiales.
- **Para:** Permitir que HU-202 (enviar pedido), HU-203 (consulta general) y HU-204 (formato claro para la dueña) reutilicen un único generador de enlaces confiable, evitando mensajes malformados.
- **Definition of Done (DoD):**
  - [ ] El enlace generado abre WhatsApp con el mensaje correcto en un dispositivo Android y uno iOS (o simulación equivalente).
  - [ ] Se prueba explícitamente con acentos, ñ, saltos de línea y comas sin que el mensaje se corte o desordene.
  - [ ] El número de WhatsApp del negocio es configurable en un único punto (constante/variable), no hardcodeado en múltiples archivos.
