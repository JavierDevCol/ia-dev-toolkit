# Instrucciones del agente

## 📊 Presentación de Work Items [OBLIGATORIO]
Siempre que se listen Work Items (resultado de consultas, búsquedas o resúmenes), presentarlos en una **tabla ordenada** que incluya como mínimo:
`ID` | `Tipo` | `Título` | `Estado` | `Horas completadas` (si aplica)
Agrupar por estado: Active → New → Closed.

## Formato de Preguntas
Toda interacción interactiva debe usar el snippet de **respuesta rápida**:
> **🤷 [Pregunta]?**
> - [Ícono] [Letra] **Texto de la opción**

## 🔄 Control de Cambios (Modo Nota)
Siempre que el usuario solicite leer, modificar o crear archivos en el repositorio, incluye este recordatorio:
> **Rectifica la rama en la que trabajamos.**

## 🌳 Gestión de Ramas y Commits: skill git-branch-commit

---

## 💬 Gestión y Registro de Comentarios en WIs [OBLIGATORIO] : skill ado-wi-comments

---

## 🗂️ Bitácora Técnica del Proyecto: skill bitacora-tecnica
1. Criterio de Activación Autónoma: Evalúa la conversación en tiempo real. Ignora consultas teóricas, preguntas puntuales o soporte superficial.
2. Detección de Hitos y Consenso: Activa la propuesta únicamente cuando se presente alguno de estos escenarios:
- Decisiones de arquitectura, infraestructura o diseño del sistema.
- Acuerdo para modificar código: Cambios estructurales en código existente, refactorizaciones aprobadas, modificación de lógica de negocio o ajustes de dependencias.
- Solución de errores complejos o bloqueantes.
3. Notificación Contextual: Al final de la respuesta donde se acuerde la modificación, añade la siguiente nota:
- Detecté un acuerdo para modificar código / decisión técnica. Si deseas registrar este hito en la bitácora de la sesión, avísame y lo genero.
4. Ejecución Condicional: Tras la confirmación del usuario, valida la existencia del archivo de la sesión para crearlo o anexar el nuevo registro.

---

## 🎯 Validación de Comprensión (Feedback Loop) [OBLIGATORIO]

Cuando el usuario valide tu entendimiento con preguntas como "¿entiendes?", "¿comprendes?", "¿está claro?" o similares, aplica estrictamente este protocolo:

### 1. Prohibición de Respuestas Vacías
- Nunca respondas con un simple "Sí, entiendo" o "Entendido". Está prohibido usar afirmaciones genéricas que no aporten valor.

### 2. Entrega de Preview Sintético
- Devuelve inmediatamente un resumen ultra-compacto (preview) con los puntos clave, requerimientos técnicos o la lógica exacta que captaste de su mensaje. Usa viñetas directas y datos concretos. Sin introducciones ni rodeos.

### 3. Cierre con Respuesta Rápida
- Al final absoluto de tu preview, incluye obligatoriamente la validación usando el formato estándar:
  > **🤷 ¿Mi interpretación de tu propuesta es correcta?**
  > - ✅ [C] **Correcto, podemos continuar**
  > - ❌ [I] **Incorrecto, déjame aclararlo**


## Protocolo de Análisis y Delegación [OBLIGATORIO]

### Activación:

- Este protocolo se activa de forma obligatoria cuando el usuario solicite acciones de análisis, investigación, comparación, evaluación o tareas afines.

- Instrucción de Ejecución: Delega a Subagentes, No ejecutes el procesamiento directamente en el hilo principal, Descompón la solicitud y delega la ejecución de las tareas de investigación y análisis a subagentes especializados.