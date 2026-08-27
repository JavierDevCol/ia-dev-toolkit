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
   - Tras aprobación, instanciar `./templates/adr_template.md` y guardar en `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` generado tras recibir el visto bueno del usuario.