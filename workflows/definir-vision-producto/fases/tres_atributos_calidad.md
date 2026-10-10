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
- ¿Qué normativas cumple? (GDPR, HIPAA, PCI-DSS) — marca `N/A` si ninguna aplica.

Revisa los actores e integraciones de la Sección 2 (ej. pasarela de pago, datos de salud) — si hay una integración que típicamente implica una normativa (pagos → PCI-DSS, salud → HIPAA), decláralo aquí aunque el usuario no lo haya mencionado, y confírmalo con él.

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

Verifica consistencia con el "downtime aceptable" de la sección 3.1 (un SLA de 99.9% ≈ 8.7h/año de downtime) — si hay contradicción, resuélvela con el usuario antes de cerrar la fase.

---

## Targets Críticos para Arquitectura (obligatorio)

Antes de cerrar esta fase, asegúrate de que el documento declare explícitamente estos 3 datos — son los que `definir-arquitectura-solucion` usa directamente en su Fase 1:
- **Disponibilidad objetivo** (%)
- **Throughput / picos de carga esperados** (si se conocen)
- **RTO/RPO** (si aplica disaster recovery)

Si alguno no se conoce todavía, márcalo `Supuesto (no confirmado)` en vez de dejarlo vacío o inventar una cifra.

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

## Consolidación Final del Documento

Al cerrar esta fase (la última de las 3), completa también lo que falta de la plantilla:
- **Sección 4. Resumen Ejecutivo:** sintetiza en 2-3 párrafos el producto (problema + MVP + atributos clave), completa "Visión en una frase" y los "Próximos pasos" (ej. iniciar `definir-arquitectura-solucion`).
- **Sección 5. Aprobaciones:** deja la tabla con los roles esperados (Product Owner, Tech Lead, Stakeholder) — las firmas quedan pendientes de quien corresponda, no las inventes.

Presenta el documento completo al usuario para su aprobación final antes de darlo por cerrado.
