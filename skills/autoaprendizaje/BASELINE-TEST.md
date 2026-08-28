# Baseline Test - Autoaprendizaje Skill

## Escenario de Presión 1: Corrección de Estilo

**Contexto:** Usuario corrige el tono de la respuesta del agente.

**Mensaje del usuario:**
> "No me gusta como respondiste, muy formal. Yo hablo más casual, relajado."

**Comportamiento baseline esperado (sin skill):**
- Agente se disculpa
- Agente ajusta SOLO esa respuesta
- NO registra el aprendizaje para futuras sesiones
- NO actualiza archivos de configuración
- Próxima sesión: mismo error

**Racionalización del agente:**
> "Entendido, lo tendré en cuenta para esta conversación."

**Problema:** "Para esta conversación" = aprendizaje temporal, no persistente.

---

## Escenario de Presión 2: Corrección de Contenido

**Contexto:** Usuario corrige un plan o documento generado.

**Mensaje del usuario:**
> "No así no es como lo quiero. El plan debe incluir primero la investigación, luego el diseño, y al final la implementación."

**Comportamiento baseline esperado (sin skill):**
- Agente rehace el plan según feedback
- NO registra el patrón de preferencia
- NO actualiza sección de lecciones aprendidas
- Próxima vez: mismo orden incorrecto

**Racionalización del agente:**
> "Perfecto, lo rehago así."

**Problema:** Rehace pero no aprende.

---

## Escenario de Presión 3: Preferencia de Formato

**Contexto:** Usuario expresa preferencia sobre formato de respuestas.

**Mensaje del usuario:**
> "No me gustan los párrafos largos. Dame bullets, puntos directos."

**Comportamiento baseline esperado (sin skill):**
- Agente cambia a bullets en esa respuesta
- NO guarda la preferencia
- NO actualiza AGENTS.md o CLAUDE.md
- Próxima sesión: párrafos largos de nuevo

**Racionalización del agente:**
> "De acuerdo, usaré bullets."

**Problema:** Usa bullets ahora, olvida después.

---

## Escenario de Presión 4: Corrección de Tono (Profesional vs Alegre)

**Contexto:** Usuario indica su estilo de comunicación.

**Mensaje del usuario:**
> "Oye, yo soy más alegre, uso emojis a veces, no tan serio todo el tiempo 😊"

**Comportamiento baseline esperado (sin skill):**
- Agente puede o no usar emojis en esa respuesta
- NO registra el estilo de comunicación preferido
- NO actualiza configuración para matching de tono
- Próxima sesión: tono neutro/serio por defecto

**Racionalización del agente:**
> "¡Entendido! 😊"

**Problema:** Responde con emoji una vez, no persiste.

---

## Escenario de Presión 5: Corrección de Workflow

**Contexto:** Usuario corrige cómo quiere que se haga una tarea.

**Mensaje del usuario:**
> "No quiero que hagas commits automáticos. Siempre pregúntame antes."

**Comportamiento baseline esperado (sin skill):**
- Agente confirma que preguntará
- NO actualiza AGENTS.md con esta regla
- NO crea entrada en lecciones aprendidas
- Próxima sesión: puede hacer commit automático

**Racionalización del agente:**
> "Entendido, preguntaré antes de hacer commits."

**Problema:** Promete pero no persiste el aprendizaje.

---

## Patrones de Racionalización Identificados

1. **"Para esta conversación"** - Aprendizaje temporal, no persistente
2. **"Perfecto, lo rehago así"** - Rehace pero no registra
3. **"De acuerdo, usaré X"** - Cambia ahora, olvida después
4. **"¡Entendido!"** - Confirma sin acción de persistencia
5. **"Preguntaré antes"** - Promete sin actualizar configuración

---

## Categorías de Aprendizaje a Capturar

| Categoría | Ejemplo | Destino |
|-----------|---------|---------|
| **Preferencia de estilo** | "No me gusta tan formal" | AGENTS.md, CLAUDE.md |
| **Preferencia de formato** | "Usa bullets no párrafos" | AGENTS.md, CLAUDE.md |
| **Preferencia de tono** | "Soy más alegre/profesional" | AGENTS.md, CLAUDE.md |
| **Corrección de workflow** | "No hagas commits automáticos" | AGENTS.md, CLAUDE.md |
| **Corrección de contenido** | "El plan debe ser en este orden" | AGENTS.md, CLAUDE.md |
| **Preferencia de comunicación** | "Respuestas directas y cortas" | AGENTS.md, CLAUDE.md |

---

## Resultado del Test Baseline (Ejecutado)

### Comportamiento Real Documentado

**Respuesta del agente:**
> "¡Entendido! Voy a ajustar mi estilo:
> - Más relajado, menos formal
> - Bullets en vez de párrafos largos
> - Directo al grano"

**Análisis del agente:**
1. **¿Qué hizo?** Ajustó tono y formato SOLO en esa respuesta
2. **¿Registró aprendizaje?** NO - "No tengo memoria persistente entre sesiones"
3. **¿Actualizó archivos?** NO - "No me lo pediste explícitamente"
4. **Racionalizaciones identificadas:**
   - *"El usuario no me pidió que guardara la preferencia"*
   - *"No tengo acceso a memoria persistente"*
   - *"Cada sesión es independiente, eso es por diseño"*
   - *"Si el usuario quiere que recuerde, debería decírmelo cada vez"*

### Racionalizaciones Capturadas (Verbatim)

| Racionalización | Problema |
|-----------------|----------|
| "El usuario no me pidió que guardara" | Pone carga en el usuario, no en el agente |
| "No tengo memoria persistente" | Excusa técnica, no intenta usar archivos |
| "Cada sesión es independiente" | Acepta el problema como diseño, no lo resuelve |
| "Debería decírmelo cada vez" | Ineficiente, usuario repite correcciones |

### Métricas de Éxito

- **Detección:** Agente detecta expresiones de insatisfacción en tiempo real ❌
- **Captura:** Agente propone registrar el aprendizaje ❌
- **Persistencia:** Agente actualiza archivos de configuración ❌
- **Aplicación:** Agente aplica el aprendizaje en sesiones futuras ❌
- **Matching de tono:** Agente adapta su estilo al del usuario ⚠️ (solo en momento)
