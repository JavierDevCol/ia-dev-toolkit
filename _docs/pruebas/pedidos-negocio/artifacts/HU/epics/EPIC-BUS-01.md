---
target_path: "./artifacts/HU/epics/EPIC-BUS-01.md"
type: business_epic
---

# 📦 Épica de Negocio: Catálogo Digital y Página del Negocio

- **ID:** `EPIC-BUS-01`
- **Módulo / Dominio:** Vitrina Digital
- **Objetivo Comercial:** Que cualquier cliente pueda ver desde su celular qué vende el negocio, a qué precio, y cuándo/dónde puede pedirlo, sin tener que llamar o escribir primero para preguntar.

---

## 📜 Historias de Usuario (HUs)

### `HU-101`: Ver catálogo de productos con fotos y precios

- **User Story:**
  - **Como** cliente
  - **Quiero** ver el catálogo de productos del negocio con foto, nombre y precio
  - **Para** decidir qué quiero pedir sin tener que llamar a preguntar

- **Dependencia Técnica:** `STORY-ENABLER-02` (Debe estar en `DONE` para iniciar).

- **Criterios de Aceptación (BDD):**
  - **Escenario 1:** Catálogo con productos disponibles
    - **Given** el cliente abre la página desde su celular
    - **When** la página termina de cargar
    - **Then** ve una lista de productos, cada uno con foto, nombre y precio, leída desde `catalogo.json`

  - **Escenario 2:** Catálogo vacío o en mantenimiento
    - **Given** `catalogo.json` no tiene productos cargados
    - **When** el cliente abre la página
    - **Then** se muestra un mensaje amigable indicando que el menú se está actualizando, en vez de una sección vacía o un error

---

### `HU-102`: Ver información del negocio (horarios, dirección, contacto)

- **User Story:**
  - **Como** cliente
  - **Quiero** ver los horarios de atención, la dirección y un contacto directo del negocio
  - **Para** saber si está abierto ahora y cómo llegar o comunicarme

- **Dependencia Técnica:** `STORY-ENABLER-02` (Debe estar en `DONE` para iniciar).

- **Criterios de Aceptación (BDD):**
  - **Escenario 1:** Información visible sin necesidad de scroll excesivo
    - **Given** el cliente está en la página principal
    - **When** busca los horarios o la dirección
    - **Then** encuentra esta información en una sección fija y visible, sin tener que navegar a otra página

  - **Escenario 2:** Horario fuera de atención
    - **Given** la hora actual está fuera del horario de atención declarado
    - **When** el cliente consulta la sección de horarios
    - **Then** puede ver claramente cuál es el horario de atención (la validación de "abierto/cerrado en este momento" queda fuera de alcance del MVP; ver Visión de Producto)

---

### `HU-103`: Actualizar el catálogo de forma simple

- **User Story:**
  - **Como** dueña del negocio
  - **Quiero** poder actualizar el catálogo (productos, precios, fotos) editando un único archivo simple
  - **Para** mantener la información al día sin depender de un programador cada vez que cambio un precio

- **Dependencia Técnica:** `STORY-ENABLER-02` (Debe estar en `DONE` para iniciar).

- **Criterios de Aceptación (BDD):**
  - **Escenario 1:** Edición exitosa del catálogo
    - **Given** la dueña (o quien la apoye) edita `data/catalogo.json` siguiendo el formato documentado en el README
    - **When** el cambio se publica (merge a `main`)
    - **Then** el catálogo público refleja el nuevo precio/producto sin que se haya tocado ningún otro archivo del sitio

  - **Escenario 2:** Formato inválido
    - **Given** el archivo `catalogo.json` editado tiene un error de formato (JSON inválido)
    - **When** se intenta desplegar el cambio
    - **Then** el proceso de build/lint falla de forma visible antes de llegar a producción, evitando romper el sitio en vivo
