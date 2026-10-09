# FASE 3: Infraestructura Cloud, Redes y Seguridad

**Objetivo:** Proponer el modelo de despliegue en la nube, el diseño de red, la resiliencia, la observabilidad y el modelo de seguridad del sistema.

---

## 🔄 Regla de Sincronización Incremental (Delta Sync)
Si `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` ya existe:
- No reescribir decisiones vigentes.
- Evaluar el impacto del nuevo requerimiento y proponer un ADR de modificación o adición.

---

## Pasos de Ejecución

1. **Clasificación de Datos y Cumplimiento (primero — condiciona todo lo demás):**
   - ¿Qué datos maneja el sistema (PII, financieros, salud, públicos)? Marcar `N/A` si ninguno.
   - Marco regulatorio aplicable (GDPR, HIPAA, PCI-DSS, ley local) o `N/A` si no aplica.
   - Esta clasificación determina el nivel de aislamiento de red, las restricciones de proveedor/región y la gestión de secretos de los pasos siguientes.

2. **Proveedor, Servicios Cloud y Sizing:**
   - Proponer **al menos 2 opciones de infraestructura viables** (ej. *AWS ECS/Fargate* vs *GCP Cloud Run*), comparadas en la Matriz de Decisión (costo, elasticidad, vendor lock-in, time-to-market) **anclada a los targets NFR de ADR-001** (disponibilidad, throughput) y a las restricciones de cumplimiento del paso 1 (regiones permitidas, certificaciones del proveedor).
   - Definir capacidad concreta: instancias mínimas/máximas, vCPU/RAM por instancia, triggers de autoscaling (ej. CPU > 70%), y costo mensual aproximado de la opción elegida.

3. **Topología de Red (con Diagrama Obligatorio):**
   - Proponer el aislamiento (subredes públicas/privadas, API Gateway, WAF) **ajustado al nivel de sensibilidad de datos del paso 1** (ej. datos PII → subred privada sin acceso directo a internet).
   - Representar la topología en un **diagrama Mermaid** (`graph` o `flowchart`) dentro del ADR — no solo en prosa.

4. **Autenticación, Autorización y Gestión de Secretos:**
   - Definir esquema de autenticación/autorización (OAuth2/OIDC/JWT) y modelo de roles/permisos.
   - Definir mecanismo de gestión de secretos (Vault, Secrets Manager, KMS) — nunca secretos en código/config plano.

5. **Resiliencia (DR/Backup):**
   - Traducir el target de disponibilidad y RTO/RPO fijado en ADR-001 a una decisión concreta: Multi-AZ vs Multi-Región, frecuencia de backup, estrategia de failover.

6. **Observabilidad Mínima:**
   - Definir logging centralizado, monitoreo (métricas clave) y alerting mínimo (qué condiciones disparan una alerta).

7. **Herramienta de IaC:**
   - Decidir la herramienta de Infraestructura como Código (Terraform, Pulumi, CloudFormation, CDK) que se usará para materializar esta infraestructura (relevante para la Fase 7 de consolidación).

8. **Superficie de Ataque y Threat Model (STRIDE):**
   - Identificar los puntos de entrada expuestos (APIs públicas, webhooks, integraciones de terceros).
   - Mapear **al menos una amenaza por categoría STRIDE relevante** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) con su mitigación propuesta — no amenazas genéricas desconectadas de la superficie real identificada.

9. **Regla de decisión:** en la Matriz de Decisión, la opción con mayor Total ponderado es la recomendación por defecto; si recomiendas la otra por una razón cualitativa no capturada en la matriz, decláralo como excepción justificada.

10. **Punto de Interacción (Pausa Obligatoria):**
    - Presentar la infraestructura completa (clasificación de datos, proveedor/sizing, diagrama de red, resiliencia, observabilidad, IaC, threat model) al usuario. Esperar su confirmación.

11. **Creación del ADR:**
    - Tras aprobación, instanciar `./plantillas/adr_template.md` completando **todas** sus secciones genéricas (matriz de decisión, supuestos, impacto en seguridad, confianza/reversibilidad) **más** las secciones específicas de esta fase: `## Diagrama de Topología de Red`, `## Sizing y Capacidad`, `## Resiliencia (DR/Backup)`, `## Observabilidad`, `## Herramienta de IaC`, `## Threat Model (STRIDE)`. Guardar en `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` con estado `Aprobado`.

---

## Entregable

Documento formal `./artifacts/ADR/ADR-003-infraestructura-y-seguridad.md` generado tras recibir el visto bueno del usuario.

Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el ADR. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.

Al final del ADR generado, agregar:

> **Aprobado por:** Arquitecto - {{usuario.nombre}}
> **Fecha:** {{fecha}}

Sin `{{usuario.nombre}}` configurado, la línea queda `> **Aprobado por:** Arquitecto`.
