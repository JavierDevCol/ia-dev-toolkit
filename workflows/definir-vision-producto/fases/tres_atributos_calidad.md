# Fase 3: Atributos de Calidad y Requerimientos No Funcionales

**Objetivo:** Definir los parámetros de calidad técnica que el sistema debe soportar tanto en su lanzamiento inicial (MVP) como en sus horizontes de crecimiento.

---

## Pre-requisito

Completar `fases/dos_delimitacion_mvp.md` antes de iniciar esta fase.

---

🔄 Regla de Sincronización (Si existe un archivo previo):
Si ./artifacts/vision_producto.md ya existe, no lo recrees desde cero. Lee el contenido actual, compara los nuevos inputs con la versión previa y actualiza únicamente las secciones impactadas.

## Preguntas guía

### 3.1 Rendimiento y Carga
- ¿Cuántos usuarios concurrentes y transacciones por segundo (TPS) se esperan en el MVP vs. el horizonte de 1 año?
- ¿Cuál es el tiempo de respuesta máximo aceptable para los endpoints críticos?

### 3.2 Seguridad y Cumplimiento
- ¿Qué tipo de datos sensibles procesará el sistema (personales, financieros, salud)?
- ¿Qué mecanismos de autenticación y autorización se requieren?
- ¿A qué normativas o estándares debe alinearse (PCI-DSS, GDPR, regulaciones locales)?

### 3.3 Disponibilidad y Tolerancia a Fallos
- ¿Cuál es el nivel de disponibilidad requerido (SLA)? (ej. 99.5% para MVP vs 99.99% a futuro).
- ¿Cuál es el Tiempo Máximo de Recuperación (RTO) y Pérdida de Datos (RPO) aceptable ante una caída?

### 3.4 Escalabilidad y Mantenibilidad
- ¿Qué componentes requerirán escalado automático desde el inicio?
- ¿Qué nivel de cobertura de pruebas y documentación exigirá el proyecto para garantizar su mantenibilidad a largo plazo?

---

## Entregable

Construye y rellena la **Sección 3. Atributos de Calidad** en la plantilla final (`./plantillas/vision_producto.md`), completando las matrices de Rendimiento, Seguridad, Usabilidad, Escalabilidad, Mantenibilidad y Disponibilidad con métricas cuantitativas concretas.

---

## Criterios de completitud

- [ ] Todos los NFRs tienen métricas cuantificables (tiempos, porcentajes, usuarios), evitando adjetivos ambiguos ("rápido", "seguro").
- [ ] Se contemplan métricas tanto para el MVP como para el crecimiento proyectado.
- [ ] Se documentan los compromisos aceptados (trade-offs).

---

## Resultado final

Al completar las 3 fases, usar `plantillas/vision_producto.md` para consolidar el documento final en `./artifacts/vision_producto.md`.