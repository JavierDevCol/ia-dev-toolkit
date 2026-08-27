Fase 2: Delimitación del MVP

**Objetivo:** Definir el Producto Mínimo Viable (MVP) que resuelve el problema identificado.

---

## Pre-requisito

Completar `fases/uno_descubrimiento_problema.md` antes de iniciar esta fase.

---

🔄 Regla de Sincronización (Si existe un archivo previo):
Si ./artifacts/vision_producto.md ya existe, no lo recrees desde cero. Lee el contenido actual, compara los nuevos inputs con la versión previa y actualiza únicamente las secciones impactadas (marcando los cambios en la sección de histórico o aprobaciones).

## Preguntas guía

### 2.1 ¿Qué incluye el MVP?

- ¿Cuál es la funcionalidad核心 que resuelve el problema?
- ¿Qué es imprescindible vs deseable?
- ¿Cuál es la experiencia mínima aceptable?
- ¿Qué NO incluimos en esta versión?
### 2.2 ¿Cómo se usa?

- ¿Cuál es el flujo principal del usuario?
- ¿Cuántos pasos tiene?
- ¿Dónde vive el usuario? (web, móvil, escritorio)
- ¿Qué integraciones necesita?

### 2.3 ¿Qué restricciones tenemos?

- **Tiempo:** ¿Cuándo debe estar listo?
- **Presupuesto:** ¿Cuál es el límite?
- **Equipo:** ¿Quiénes participan?
- **Tecnología:** ¿Qué stack usamos?

### 2.4 ¿Cómo validamos?

- ¿Cómo sabemos que funciona?
- ¿A quién se lo mostramos primero?
- ¿Qué métricas trackeamos?
- ¿Cuándo consideramos éxito?

### 2.5 Mapa de Actores / Roles
   - Identificar usuarios finales (ej. *Cliente, Barbero, Administrador*).
   - Identificar sistemas externos con los que debe interactuar (ej. *Pasarela de Pago, Servicio SMS*).

### 2.6 Criterios de Slicing Funcional (In-Scope vs. Out-of-Scope):
   - **Dentro del MVP (In-Scope):** Funcionalidades mínimas sin las cuales el producto **no puede operar ni generar valor**.
   - **Fuera del MVP (Out-of-Scope):** Ideas valiosas pero no críticas para el lanzamiento inicial (ej. *Motor de IA para recomendaciones, programa de fidelización avanzado*).

### 2.7 Módulos / Épicas Candidatas:
   - Agrupar las capacidades del MVP en 3 a 5 grandes módulos conceptuales (ej. *Gestión de Citas, Autenticación, Pagos*).
---

## Entregable

Construye y rellena la **Sección 2. MVP Definido** en la plantilla final (`./plantillas/vision_producto.md`), asegurando poblar la tabla de funcionalidades MUST/SHOULD, el flujo principal y las restricciones.

---

## Criterios de completitud

- [ ] Las funcionalidades MUST están definidas
- [ ] El flujo principal está documentado
- [ ] Las restricciones están cuantificadas
- [ ] Los criterios de éxito son medibles
- [ ] El equipo aprueba el alcance

---

## Siguiente fase

Una vez completada, proceder a `fases/tres_atributos_calidad.md`
