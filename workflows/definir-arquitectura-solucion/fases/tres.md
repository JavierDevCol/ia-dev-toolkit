# FASE 3: Infraestructura Cloud, Redes y Seguridad

**Objetivo:** Proponer la infraestructura objetivo en la nube, el aislamiento de red, la resiliencia operativa y la estrategia de seguridad (*Security by Design*) — garantizando total coherencia con `ADR-001`, `ADR-002` y los NFRs de `./artifacts/vision_producto.md`.

## Pasos de Análisis

1. **Diseño de Infraestructura Cloud y Cómputo:** 
   - Selecciona el proveedor cloud y el modelo de cómputo (ej. *PaaS/Serverless* como GCP Cloud Run / AWS Fargate vs *IaaS/K8s*).
   - Valida que la opción elegida sea operable por el **Equipo** y ejecutable dentro del **Presupuesto** definidos en `vision_producto.md`.
2. **Topología de Redes, Ingress y Egress:** 
   - Diseña el aislamiento de red (VPC, subredes públicas/privadas, API Gateway, WAF).
   - Especifica cómo se protegerán las comunicaciones entrantes (usuarios) y salientes hacia los **Sistemas Externos** del Mapa de Actores (ej. IPs fijas para pasarelas de pago, mTLS).
3. **Resiliencia y Alta Disponibilidad:** 
   - Diseña la estrategia para cumplir con el SLA, RTO y RPO exigidos en los Atributos de Calidad (ej. despliegue Multi-AZ, políticas de backup, auto-scaling).
4. **Estrategia Security by Design & IAM:** 
   - Define la autenticación/autorización de usuarios (OAuth2 / OIDC / JWT / RBAC).
   - Define el almacenamiento y rotación de secretos (ej. AWS Secrets Manager, HashiCorp Vault).
   - Define la política de mínimo privilegio para roles de infraestructura y acceso a entornos.

## Criterios a Evaluar por Opción (Trade-offs)

Debes comparar las opciones basándote en los siguientes pilares:

* **Costo Operativo vs Tráfico:** Estimación de costos para el MVP vs. el horizonte proyectado a 1 año.
* **Complejidad de Mantenimiento:** Carga operativa impuesta al equipo según su tamaño y madurez.
* **Superficie de Ataque y Cumplimiento:** Nivel de protección de datos sensibles y alineación con normativas requeridas (GDPR, PCI-DSS, etc.).
* **Vendor Lock-in y Portabilidad:** Grado de acoplamiento al proveedor cloud seleccionado.

Indica cuál opción recomiendas y justifica tu elección con base en estos criterios.

## Entregable Esperado (Borrador del ADR)

Genera el texto exacto que el orquestador usará para crear el archivo `ADR-003-infraestructura-y-seguridad.md`, respetando la estructura de `./plantillas/adr_template.md`:

- **Contexto:** Resume los NFRs de seguridad, resiliencia (SLA/RTO) y las restricciones de equipo/presupuesto que impulsan esta decisión.
- **Opciones Evaluadas:** Compara al menos 2 alternativas de infraestructura y topología de red.
- **Decisión Aprobada:** Detalla el proveedor cloud, servicios de cómputo, componentes de red, estrategia de resiliencia y modelo de seguridad aprobados.
- **Consecuencias:**
  - *Positivas:* Beneficios en seguridad, automatización, escalabilidad o cumplimiento de SLA.
  - *Negativas / Riesgos Aceptados:* Costos fijos de infraestructura, complejidad de red o acoplamiento al proveedor nube.