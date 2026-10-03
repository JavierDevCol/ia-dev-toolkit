# FASE 7: Consolidación Opcional de la Propuesta Arquitectónica

**Objetivo:** Decidir junto al usuario si se materializa de inmediato el scaffold base del proyecto (estructura de carpetas, boilerplate del stack, `.gitignore`, `.env.example` y esqueleto CI/CD) según lo aprobado en los ADRs y el Blueprint, o si su creación se delega formalmente como Historias de Usuario Enablers para el Sprint 0.

---

## Pasos de Ejecución

1. **Lectura de la Fuente de Verdad:**
   - Lee únicamente `./artifacts/blueprint_arquitectura.md` para extraer el stack, la estructura de carpetas, la base de datos y el pipeline aprobados.

2. **Confirmación con el Usuario (Gatekeeper):**
   - Presenta un mensaje ultrasintético del stack a generar (1 o 2 líneas) y pregunta:
     > **"¿Deseas consolidar y materializar la propuesta arquitectónica en el repositorio en este momento? (Responde SI/CONSOLIDA o NO)"**
   - **DETÉN LA EJECUCIÓN** y espera la respuesta explícita del usuario.

---

### Si el usuario responde SI / CONSOLIDA

3. **Inspección de Seguridad del Workspace:**
   - Verifica si el directorio raíz o `./src` ya contiene código. Si existen archivos de código preexistentes, advierte al usuario antes de modificar nada.

4. **Materialización del Scaffold Base:**
   - **Estructura de Carpetas:** Crea la jerarquía de directorios aprobada en `ADR-002` (ej. `domain/`, `application/`, `infrastructure/`).
   - **Boilerplate e Higiene:** 
     - Genera un `.gitignore` adaptado al stack tecnológico elegido (`ADR-001`/`ADR-002`).
     - Genera un `.env.example` con las variables de entorno, puertos y secretos requeridos según `ADR-003` y `ADR-004`.
     - Genera un `README.md` básico en la raíz vinculando a `./artifacts/blueprint_arquitectura.md`.
   - **Ejecución de Scaffold / Fallback:**
     - Intenta ejecutar el comando de inicialización nativo del stack (ej. `npm init -y`, `go mod init`, etc.).
     - *Estrategia Fallback:* Si el entorno no cuenta con la CLI instalada o el comando falla, genera directamente los archivos manifest estáticos mínimos (ej. `package.json`, `pom.xml`, `go.mod`, `requirements.txt`).
   - **Esqueleto de CI/CD e Infraestructura:**
     - Crea el archivo del pipeline en la ruta correspondiente (ej. `.github/workflows/ci.yml` o `bitbucket-pipelines.yml`) con las etapas definidas en `ADR-004`.
     - Crea el `Dockerfile` o archivo de IaC básico según `ADR-003`.

5. **Entregable de Registro (`./artifacts/consolidacion.md`):**
   - Documenta el estado `ESTADO: CONSOLIDADO`.
   - Detalla el inventario de carpetas y archivos creados con su trazabilidad directa al ADR correspondiente.
   - Lista cualquier componente que no se haya podido automatizar.

---

### Si el usuario responde NO

3. **Respeto Estricto del filesystem:** No crea ni modifica archivos de código o estructura en el proyecto.
4. **Entregable de Registro (`./artifacts/consolidacion.md`):**
   - Documenta el estado `ESTADO: PENDIENTE_SPRINT_0`.
   - Especifica que el scaffold base no se consolidó y debe ser absorbido en el Sprint 0.
   - **Estructuración de Enablers para Backlog:** Redacta la lista explicita de Historias de Usuario Enablers sugeridas para que el workflow `gestionar-backlog-roadmap` las ingiera directamente:
     - *HU-ENABLER-01:* Creación de Estructura de Directorios y Boilerplate Base *(Ref: ADR-001, ADR-002)*.
     - *HU-ENABLER-02:* Aprovisionamiento de Esqueleto CI/CD y Pipeline de Calidad *(Ref: ADR-004)*.
     - *HU-ENABLER-03:* Configuración de Entornos, Dockerfile e Infraestructura Base *(Ref: ADR-003)*.

---

## Formato del Entregable Final (`./artifacts/consolidacion.md`)

Lee `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y toma `usuario.nombre` → `{{usuario.nombre}}`. Si está vacío o el archivo no existe, omite el sufijo del nombre.

Escribe el archivo `./artifacts/consolidacion.md` finalizando obligatoriamente con el siguiente bloque de cierre:

```markdown
---
> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}