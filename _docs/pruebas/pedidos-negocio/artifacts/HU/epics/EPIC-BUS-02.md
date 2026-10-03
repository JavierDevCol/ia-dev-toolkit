---
target_path: "./artifacts/HU/epics/EPIC-BUS-02.md"
type: business_epic
---

# 📦 Épica de Negocio: Recepción de Pedidos y Consultas vía WhatsApp

- **ID:** `EPIC-BUS-02`
- **Módulo / Dominio:** Canal de Pedidos
- **Objetivo Comercial:** Que el cliente pueda armar y enviar su pedido (o una consulta) directamente al WhatsApp del negocio con la información ya organizada, y que la dueña reciba ese pedido de forma clara, sin ambigüedad ni pasos manuales adicionales para ninguna de las dos partes.

---

## 📜 Historias de Usuario (HUs)

### `HU-201`: Armar el pedido seleccionando productos y cantidades

- **User Story:**
  - **Como** cliente
  - **Quiero** seleccionar productos del catálogo y definir cantidades
  - **Para** armar mi pedido completo antes de enviarlo, sin tener que escribirlo todo a mano

- **Dependencia Técnica:** `STORY-ENABLER-02` (Debe estar en `DONE` para iniciar).

- **Criterios de Aceptación (BDD):**
  - **Escenario 1:** Selección de productos
    - **Given** el cliente ve el catálogo (HU-101)
    - **When** selecciona uno o más productos y define una cantidad para cada uno
    - **Then** ve un resumen de su pedido actual (productos, cantidades y subtotal) antes de enviarlo

  - **Escenario 2:** Intento de envío sin productos seleccionados
    - **Given** el cliente no ha seleccionado ningún producto
    - **When** intenta presionar "Enviar pedido"
    - **Then** el sistema le indica que debe seleccionar al menos un producto antes de continuar

---

### `HU-202`: Enviar el pedido por WhatsApp con un clic

- **User Story:**
  - **Como** cliente
  - **Quiero** enviar mi pedido armado directamente al WhatsApp del negocio con un solo clic
  - **Para** no tener que copiar y pegar manualmente los productos que elegí

- **Dependencia Técnica:** `STORY-ENABLER-03` (Debe estar en `DONE` para iniciar).

- **Criterios de Aceptación (BDD):**
  - **Escenario 1:** Envío exitoso
    - **Given** el cliente tiene un pedido armado (HU-201) y presiona "Enviar pedido por WhatsApp"
    - **When** el sistema genera el enlace `wa.me` con el detalle del pedido
    - **Then** se abre WhatsApp (app o web) con un mensaje prellenado listo para enviar al número del negocio, incluyendo productos, cantidades y un campo para el nombre del cliente

  - **Escenario 2:** Cliente sin WhatsApp instalado en el dispositivo
    - **Given** el cliente usa un dispositivo sin la app de WhatsApp instalada
    - **When** presiona "Enviar pedido por WhatsApp"
    - **Then** el enlace `wa.me` redirige a WhatsApp Web como comportamiento estándar del propio esquema `wa.me` (sin lógica adicional a implementar por el proyecto)

---

### `HU-203`: Enviar una consulta general por WhatsApp

- **User Story:**
  - **Como** cliente
  - **Quiero** enviar una consulta general al negocio por WhatsApp sin tener que armar un pedido primero
  - **Para** resolver dudas (disponibilidad, encargos especiales, etc.) antes de decidir comprar

- **Dependencia Técnica:** `STORY-ENABLER-03` (Debe estar en `DONE` para iniciar).

- **Criterios de Aceptación (BDD):**
  - **Escenario 1:** Botón de consulta siempre visible
    - **Given** el cliente está en cualquier punto de la página
    - **When** presiona el botón "Consultar por WhatsApp"
    - **Then** se abre WhatsApp con un mensaje base editable dirigido al número del negocio, sin requerir haber seleccionado productos

  - **Escenario 2:** Consulta con texto libre
    - **Given** el cliente quiere agregar una pregunta específica
    - **When** escribe su consulta en un campo de texto antes de presionar el botón
    - **Then** el mensaje prellenado en WhatsApp incluye ese texto libre correctamente codificado (acentos, saltos de línea)

---

### `HU-204`: Recibir pedidos con formato claro y completo

- **User Story:**
  - **Como** dueña del negocio
  - **Quiero** recibir los pedidos por WhatsApp con los productos, cantidades y nombre del cliente organizados de forma clara
  - **Para** no confundirme ni tener que volver a preguntar datos al preparar el pedido

- **Dependencia Técnica:** `STORY-ENABLER-03` (Debe estar en `DONE` para iniciar).

- **Criterios de Aceptación (BDD):**
  - **Escenario 1:** Mensaje recibido con formato estándar
    - **Given** un cliente envía un pedido (HU-202)
    - **When** la dueña abre el mensaje en su WhatsApp
    - **Then** el mensaje sigue un formato fijo y legible: lista de productos con cantidades, subtotal, nombre del cliente y notas adicionales (si las hay), en ese orden

  - **Escenario 2:** Pedido con notas especiales
    - **Given** el cliente agregó una nota (ej. "sin cebolla")
    - **When** la dueña recibe el mensaje
    - **Then** la nota aparece claramente asociada al producto correspondiente, no mezclada de forma ambigua con el resto del pedido
