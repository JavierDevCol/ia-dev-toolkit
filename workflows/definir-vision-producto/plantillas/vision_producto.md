---
target_path: "./artifacts/vision_producto.md"
type: product_vision
---

# 🎯 Visión de Producto: [Nombre del Producto]

**Fecha:** [YYYY-MM-DD]  
**Versión:** 1.0  
**Autor:** {{usuario.nombre}}  

---

## 1. Problema Identificado y Propuesta de Valor

### 1.1 Diagnóstico del Problema y Causa Raíz
[Descripción clara del problema de fondo que se intenta resolver y el impacto de no resolverlo hoy]

### 1.2 Usuario e Impacto
* **Perfil / Rol:** [Perfil demográfico o rol operativo del usuario afectado]
* **Frecuencia del Dolor:** [Diario, Semanal, Eventual]
* **Impacto Operativo/Económico:** [Pérdidas financieras, de tiempo o fricción operativa]

### 1.3 Propuesta de Valor y Métricas Macro
* **Beneficio Principal:** [Qué gana el usuario de forma directa con la solución]
* **Factor Diferenciador:** [Por qué elegirá este producto sobre las alternativas actuales]
* **Métrica de Éxito de Negocio:** [Cómo medirá la organización el retorno de inversión]

### 1.4 Estado del Arte y Alternativas Actuales

| Alternativa / Proceso Actual | Limitación o Fricción Principal |
| :--- | :--- |
| [Proceso manual / Herramienta A] | [Lenta, propensa a errores, etc.] |
| [Solución de la competencia B] | [Costosa, compleja de usar, etc.] |

---

## 2. Visión Estratégica y Alcance (El Norte vs MVP)

### 2.1 Visión Holística a Largo Plazo (El Norte)
[Descripción del producto final en su máximo nivel de madurez: capacidades avanzadas, automatizaciones, ecosistema de integraciones y evolución futura del negocio]

### 2.2 Slicing y Delimitación del MVP (Fase 1)
* **Hipótesis a Validar:** [Qué necesidad u oportunidad crítica queremos probar en el mercado con la primera versión]

| # | Módulo / Funcionalidad | Prioridad | Alcance (In-Scope / Out-of-Scope) | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| 1 | [Nombre Módulo Core] | MUST | In-Scope (MVP) | [Qué hace en esta primera fase] |
| 2 | [Nombre Módulo Secundario] | SHOULD | In-Scope (MVP) | [Qué hace en esta primera fase] |
| 3 | [IA / Analítica / Módulo Avanzado] | COULD | Out-of-Scope (Futuro) | [Reservado para versiones post-MVP] |

### 2.3 Flujo Principal del Usuario (MVP)
1. **[Paso 1]:** [Entrada / Autenticación / Registro]
2. **[Paso 2]:** [Acción Core del sistema]
3. **[Paso 3]:** [Salida de valor / Confirmación]

### 2.4 Mapa de Actores
* **Usuarios Humanos:** [ej. Cliente final, Administrador, Operador de soporte]
* **Sistemas Externos:** [ej. Pasarela de pagos, Proveedor de SMS/Email, CRM]

### 2.5 Restricciones Operativas del MVP
* **Tiempo:** [Fecha límite o ventana de oportunidad de mercado]
* **Presupuesto:** [Límite financiero para la fase de construcción inicial]
* **Equipo:** [Roles disponibles y nivel de madurez técnico/operativo]
* **Stack Preferido / Obligatorio:** [Tecnologías preexistentes o restricciones de lenguaje]

---

## 3. Atributos de Calidad y Requerimientos No Funcionales

### 3.1 Rendimiento
| Métrica | Objetivo MVP | Objetivo a 1 Año | Herramienta de Medición |
| :--- | :--- | :--- | :--- |
| **Usuarios Simultáneos** | [N] | [N * X] | [ej. k6 / JMeter] |
| **Tiempo de Respuesta (P95)** | [< X ms] | [< X ms] | [ej. APM / Datadog] |
| **Transacciones / Seg (TPS)** | [N] | [N * X] | [Métrica interna] |

### 3.2 Seguridad y Cumplimiento
| Aspecto | Requisito / Estrategia |
| :--- | :--- |
| **Autenticación / Autorización** | [OAuth2, JWT, RBAC] |
| **Datos Sensibles** | [Cifrado en reposo y tránsito para datos sensibles] |
| **Normativas / Regulaciones** | [GDPR, PCI-DSS, Regulaciones locales] |

### 3.3 Usabilidad y Accesibilidad
| Aspecto | Requisito |
| :--- | :--- |
| **Experiencia de Usuario (UX)** | [Nivel de complejidad / Flujo intuitivo sin capacitación] |
| **Dispositivos y Plataformas** | [Web Responsive, App Móvil iOS/Android, Panel Desktop] |
| **Idiomas / Localización** | [Idiomas soportados en la primera fase] |

### 3.4 Escalabilidad y Disponibilidad
| Atributo | Requisito MVP | Requisito a Largo Plazo |
| :--- | :--- | :--- |
| **Disponibilidad (SLA)** | [ej. 99.5%] | [ej. 99.99%] |
| **Estrategia de Escalado** | [Horizontal / Vertical para componentes críticos] | [Autoscaling Multi-Región] |
| **Resiliencia (RTO / RPO)** | RTO: [< X horas] / RPO: [< Y min] | RTO: [< X min] / RPO: [0 pérdida datos] |

### 3.5 Mantenibilidad
| Aspecto | Requisito |
| :--- | :--- |
| **Cobertura de Pruebas** | [Porcentaje mínimo de tests unitarios/integración] |
| **Documentación Obligatoria** | [Contratos OpenAPI/Swagger, Diagramas C4] |

---

## 4. Resumen Ejecutivo

### Visión en una Frase
**[Nombre del Producto]** es una solución para **[Usuario objetivo]** que resuelve **[Problema/Causa raíz]**. A diferencia de **[Alternativas actuales]**, nuestro producto **[Diferenciador principal y propuesta de valor]**.

### Próximos Pasos Inmediatos
1. [Ejecución de Fase 1 de Arquitectura - ADR-001: Estilo Arquitectónico]
2. [Validación de prototipos/Wireframes con usuarios]
3. [Aprovisionamiento del entorno de desarrollo inicial]

---

## 5. Historial de Cambios y Aprobaciones

| Versión | Fecha | Rol | Nombre | Firma / Estado |
| :--- | :--- | :--- | :--- | :--- |
| 1.0 | [YYYY-MM-DD] | Product Owner | {{usuario.nombre}} | Aprobado |
| | | Tech Lead | | |
| | | Stakeholder / Cliente | | |