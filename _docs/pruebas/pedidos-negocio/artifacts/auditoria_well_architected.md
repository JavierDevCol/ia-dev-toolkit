# 📋 Auditoría de Arquitectura (Well-Architected Framework)

## Evaluación por Pilares

| Pilar | Estado | Hallazgos / Recomendaciones |
| :--- | :--- | :--- |
| **Excelencia Operativa** | 🟢 Cumple | Pipeline simple de lint + deploy automático definido en ADR-004; apropiado para el tamaño del equipo (1 persona) |
| **Seguridad** | 🟢 Cumple | Sin backend expuesto ni datos sensibles almacenados (ADR-003); HTTPS forzado por la plataforma de hosting; riesgo residual mínimo y aceptado explícitamente |
| **Fiabilidad** | 🟡 Aceptable | No aplica Multi-AZ ni políticas de retry porque no existe backend (ADR-001); la disponibilidad depende del SLA del proveedor de hosting gratuito, sin compromiso contractual propio — riesgo aceptado y documentado en ADR-003 |
| **Eficiencia del Rendimiento** | 🟢 Cumple | CDN estático + sitio sin frameworks pesados cubre holgadamente la volumetría proyectada (20-30 usuarios simultáneos, ver Visión) |
| **Optimización de Costos** | 🟢 Cumple | Costo de infraestructura y persistencia en $0 (hosting estático gratuito, sin base de datos ni backend que operar) |
| **Sostenibilidad** | 🟢 Cumple | No hay cómputo/servidores dedicados corriendo de forma continua; el consumo energético se limita a servir archivos estáticos vía CDN compartido del proveedor |

## Nota de Trazabilidad
Todos los hallazgos de esta auditoría están respaldados por decisiones documentadas en `./artifacts/ADR/ADR-001-estilo-arquitectonico.md` a `ADR-004-devops-y-comunicacion.md`. El pilar de Fiabilidad se marca como 🟡 Aceptable (no 🔴) porque la ausencia de Multi-AZ/retries es una consecuencia deliberada y proporcionada del estilo arquitectónico elegido (ADR-001), no un defecto no evaluado.
