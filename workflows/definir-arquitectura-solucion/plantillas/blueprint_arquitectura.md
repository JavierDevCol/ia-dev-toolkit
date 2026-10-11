---
target_path: "./artifacts/blueprint_arquitectura.md"
type: architecture_blueprint
---

# 🏗️ Blueprint de Arquitectura: [Nombre del Proyecto]

**Versión:** 1.0  
**Fecha:** [YYYY-MM-DD]  
**Arquitecto Responsable:** Onad  

---

## 1. Resumen Ejecutivo y Estrategia de Solución
- **Visión General:** [Resumen de la solución técnica diseñada]
- **Estilo Arquitectónico:** [Monolito Modular / Microservicios / Serverless] *(Ref: ADR-001)*

---

## 2. Atributos de Calidad y Trade-Offs

| Atributo | Decisión de Arquitectura | Trade-Off / Compromiso |
| :--- | :--- | :--- |
| **Disponibilidad** | Multi-AZ Deployment | Mayor costo de infraestructura |
| **Escalabilidad** | Autoscaling por métricas CPU/RAM | Complejidad operacional |
| **Seguridad** | OAuth2 + Mutual TLS | Latencia adicional en Handshake |

---

## 3. Patrones de Software y Estructura de Proyecto *(Ref: ADR-002)*

### Patrón Seleccionado
[Descripción de Clean Architecture, Hexagonal, etc.]

### Estructura de Directorios Recomendada
```plaintext
src/
├── domain/       # Entidades y reglas de negocio
├── application/  # Casos de uso y puertos
├── infrastructure/ # Adaptadores, BD, APIs externas
└── config/       # Variables de entorno y DI
```

### Reglas Base Recomendadas (No Oficiales)
[Resumen de: regla de dependencias entre capas, convención de nombres, manejo de errores, estrategia de testing por capa y migraciones de esquema — detalle completo en ADR-002]

---

## 4. Modelo de Datos y Persistencia (Ref: ADR-002)
- Motor Principal: [PostgreSQL / MongoDB / DynamoDB]

- Volumetría Estimada: [registros esperados al lanzamiento / proyección a 1 año]

- Estrategia de Caching: [Redis / Memcached]

- Estrategia de Migraciones: [Flyway / Liquibase / Prisma Migrations]

---

## 5. Infraestructura Cloud, Redes y Seguridad (Ref: ADR-003)

### Clasificación de Datos y Cumplimiento
[Tipo de datos manejados (PII/financieros/salud/públicos) y marco regulatorio aplicable, o N/A]

### Componentes Cloud y Sizing
- Proveedor: [AWS / GCP / Azure / Vercel]
- Capacidad: [instancias mín/máx, vCPU/RAM, triggers de autoscaling]
- Costo mensual estimado: [cifra aproximada]

### Diagrama de Topología de Red
[Diagrama Mermaid embebido tal cual desde ADR-003]

### Resiliencia (DR/Backup)
[Multi-AZ / Multi-Región, frecuencia de backup, RTO/RPO]

### Observabilidad
[Logging centralizado, monitoreo, alerting mínimo]

### Seguridad
- Autenticación/Autorización: [esquema OAuth2/OIDC/JWT y modelo de roles]
- Gestión de Secretos: [Vault / Secrets Manager / KMS]
- Herramienta de IaC: [Terraform / Pulumi / CloudFormation / CDK]

> El Threat Model STRIDE completo vive en `ADR-003-infraestructura-y-seguridad.md` — no se duplica aquí.

---

## 6. DevOps, CI/CD y Comunicación (Ref: ADR-004)

- Estrategia Git: [Trunk-Based / GitFlow]

- Pipeline CI/CD: [Stages y gates de calidad — ej. cobertura mínima, severidad SAST bloqueante]

- Estrategia de Despliegue y Rollback: [Blue-Green / Canary / Rolling Update]

- Protocolos de Comunicación: [REST / gRPC / Event-Driven]

- Contrato de API y Versionado: [OpenAPI / AsyncAPI + convención de versionado semántico]

---

## 7. Supuestos Abiertos y Riesgos Aceptados

| ADR | Supuesto / Riesgo | Estado |
| :--- | :--- | :--- |
| [ADR-00X] | [Supuesto no confirmado o riesgo aceptado, copiado tal cual del ADR] | [Pendiente de validar / Aceptado] |