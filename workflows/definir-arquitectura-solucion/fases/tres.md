# FASE 3: Infraestructura Cloud, Redes y Seguridad

**Objetivo:** Proponer el modelo de despliegue en la nube, aislamiento de red y autenticación/autorización — coherente con ADR-001 y ADR-002.

## Pasos de Análisis

1. **Proveedor y Servicios Cloud:** Propón la infraestructura objetivo (ej. *AWS ECS/Fargate*, *GCP Cloud Run*, *Vercel/Supabase*) con estimación de capacidad.
2. **Topología de Redes:** Propón el aislamiento (subredes públicas/privadas, API Gateway, WAF).
3. **Estrategia Security by Design:** Define autenticación/autorización (OAuth2/OIDC/JWT) y gestión de secretos.

## Criterios a Evaluar por Opción

- Costo estimado por tier de tráfico (bajo/medio/alto).
- Vendor lock-in del proveedor cloud elegido.
- Superficie de ataque y defensa en profundidad de la topología propuesta.
- Estrategia de rotación de secretos y su automatización.
- Cumplimiento regulatorio si la visión del producto maneja datos sensibles.

Indica cuál opción recomendás y por qué, con base en estos criterios.

## Entregable esperado

`ADR-003-infraestructura-y-seguridad.md` (lo escribe el orquestador tras tu propuesta y la aprobación del usuario).
