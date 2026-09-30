# FASE 3: Infraestructura Cloud, Redes y Seguridad

**Objetivo:** Proponer el modelo de despliegue en la nube, aislamiento de red y autenticación/autorización.

---

## Pasos de Ejecución

1. **Proveedor y Servicios Cloud:** Proponer la infraestructura objetivo (ej. *AWS ECS/Fargate*, *GCP Cloud Run*, *Vercel/Supabase*) con estimación de capacidad.
2. **Topología de Redes:** Proponer el aislamiento (Subredes públicas/privadas, API Gateway, WAF).
3. **Estrategia Security by Design:** Definir autenticación/autorización (OAuth2/OIDC/JWT) y gestión de secretos.
4. **Punto de Interacción (Pausa Obligatoria):**
   - Presentar la arquitectura Cloud y el modelo de seguridad al usuario. Esperar su confirmación.
5. **Creación del ADR:**
   - Tras aprobación, instanciar `./plantillas/adr_template.md` y guardar en `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` generado tras recibir el visto bueno del usuario.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el ADR. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final del ADR generado, agregar:

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.