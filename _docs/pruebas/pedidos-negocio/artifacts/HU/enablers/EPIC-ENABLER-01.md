---
target_path: "./artifacts/HU/enablers/EPIC-ENABLER-01.md"
type: enabler_epic
---

# 🧱 Épica Enabler: Setup de Publicación Web y Despliegue Continuo

- **ID:** `EPIC-ENABLER-01`
- **Origen Arquitectónico:** ADR-001 (Estilo Arquitectónico), ADR-003 (Infraestructura y Seguridad), ADR-004 (DevOps y Comunicación)
- **Objetivo:** Dejar publicable y desplegable de forma continua el sitio estático (repositorio, hosting con HTTPS/CDN y estructura base de carpetas), habilitando que cualquier HU de negocio posterior tenga dónde vivir y cómo salir a producción.

---

## ⚙️ Features Enablers Contenidas

### Feature: Hosting y Despliegue Continuo
- **ID:** `FEAT-ENABLER-01`
- **Descripción:** Repositorio Git conectado a una plataforma de hosting estático (Netlify/Vercel) con despliegue automático al hacer merge a `main`, HTTPS y CDN activos por defecto (ADR-003, ADR-004).

### Feature: Estructura Base del Sitio
- **ID:** `FEAT-ENABLER-02`
- **Descripción:** Esqueleto de carpetas y archivos del sitio (HTML/CSS/JS, `data/catalogo.json`) según la estructura de directorios aprobada en ADR-002, mobile-first, listo para que las HUs de negocio agreguen contenido y funcionalidad.

---

## 📜 Historias Enablers Refinadas

### `STORY-ENABLER-01` (DevOps / Infraestructura)
- **Rol:** As DevOps (rol asumido por el único desarrollador del proyecto)
- **Necesidad:** Crear el repositorio Git, conectarlo a Netlify (o Vercel) y configurar el despliegue automático a producción al hacer merge a `main`, con dominio/subdominio gratuito y HTTPS forzado.
- **Para:** Habilitar que el sitio sea publicable y actualizable sin intervención manual, cumpliendo ADR-003 y ADR-004.
- **Definition of Done (DoD):**
  - [ ] El sitio es accesible públicamente vía HTTPS en la URL del proveedor de hosting.
  - [ ] Un merge a `main` dispara un despliegue automático verificado (cambio visible en producción sin pasos manuales).
  - [ ] Rama `main` protegida, requiriendo Pull Request para cualquier cambio (GitHub Flow, ADR-004).

### `STORY-ENABLER-02` (Arquitectura / Backend — en este proyecto, Frontend estático)
- **Rol:** As Software Developer
- **Necesidad:** Crear la estructura base de carpetas (`index.html`, `/assets/css`, `/assets/js`, `/assets/img`, `/data/catalogo.json`, `/docs/README.md`) y una plantilla HTML responsive mobile-first vacía, según ADR-002.
- **Para:** Permitir que las HUs de negocio (catálogo, información del negocio, armado de pedido) se implementen sobre una base ya organizada, sin decisiones estructurales pendientes.
- **Definition of Done (DoD):**
  - [ ] Estructura de carpetas creada y versionada en el repositorio tal como está documentada en el Blueprint (`./artifacts/blueprint_arquitectura.md`, sección 3).
  - [ ] `catalogo.json` de ejemplo cargado con al menos 2 productos de prueba.
  - [ ] Plantilla HTML validada como responsive en un viewport móvil (ej. 375px de ancho).
