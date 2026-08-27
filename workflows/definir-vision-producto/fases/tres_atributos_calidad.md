# Fase 3: Atributos de Calidad

**Objetivo:** Definir los atributos de calidad (no funcionales) que el producto debe cumplir.

---

## Pre-requisito

Completar `fases/dos_delimitacion_mvp.md` antes de iniciar esta fase.

---

🔄 Regla de Sincronización (Si existe un archivo previo):
Si ./artifacts/vision_producto.md ya existe, no lo recrees desde cero. Lee el contenido actual, compara los nuevos inputs con la versión previa y actualiza únicamente las secciones impactadas (marcando los cambios en la sección de histórico o aprobaciones).

## Preguntas guía

### 3.1 Rendimiento

- ¿Cuántos usuarios simultáneos debe soportar?
- ¿Cuál es el tiempo de respuesta máximo aceptable?
- ¿Cuántos transacciones por segundo?
- ¿Cuánto tiempo de downtime es aceptable?

### 3.2 Seguridad

- ¿Qué datos sensibles maneja?
- ¿Qué autenticación necesita?
- ¿Qué autorización requiere?
- ¿Qué normativas cumple? (GDPR, HIPAA, PCI-DSS)

### 3.3 Usabilidad

- ¿Qué nivel de experiencia tiene el usuario?
- ¿Qué accesibilidad requiere? (WCAG)
- ¿Qué idiomas soporta?
- ¿Qué dispositivos soporta?

### 3.4 Escalabilidad

- ¿Cómo crece la demanda en 6 meses?
- ¿Cómo crece en 1 año?
- ¿Qué Componentes deben escalar horizontalmente?
- ¿Qué componentes deben escalar verticalmente?

### 3.5 Mantenibilidad

- ¿Qué tan fácil es bugfixing?
- ¿Qué tan fácil es agregar features?
- ¿Qué cobertura de tests se requiere?
- ¿Qué documentación es obligatoria?

### 3.6 Disponibilidad

- ¿Qué SLA se promete? (99.9%, 99.99%)
- ¿Qué estrategia de disaster recovery?
- ¿Qué backups se requieren?
- ¿Qué tiempo de recuperación (RTO)?

---

## Entregable
Construye y rellena la **Sección 3. Atributos de Calidad** en la plantilla final (`./plantillas/vision_producto.md`), completando las matrices de Rendimiento, Seguridad, Usabilidad, Escalabilidad, Mantenibilidad y Disponibilidad.
---

## Criterios de completitud

- [ ] Todos los atributos están definidos
- [ ] Los objetivos son medibles
- [ ] Las herramientas de medición están identificadas
- [ ] El equipo aprueba los compromisos
- [ ] Se documentan trade-offs (ej: seguridad vs rendimiento)

---

## Resultado final

Al completar las 3 fases, usar `plantillas/vision_producto.md` para consolidar el documento final.
