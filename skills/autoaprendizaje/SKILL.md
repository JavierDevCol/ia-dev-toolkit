---
name: autoaprendizaje
description: Use when user expresses dissatisfaction ("no me gusta", "no así no es como lo quiero", "corregir", "cambiar"), requests corrections, or indicates preferences for style, format, tone, or workflow. Detects learning opportunities in real-time and persists them to config files.
---

# Autoaprendizaje

## Overview

Captura aprendizajes del usuario en tiempo real y persiste en archivos de configuración para que no se repitan errores. Detecta insatisfacción, corrige y registra.

## When to Use

- Usuario dice "no me gusta", "no así no es como lo quiero", "corregir", "cambiar"
- Usuario pide corregir texto, plan, código, formato
- Usuario indica preferencias de estilo, tono, formato
- Usuario corrige workflow o forma de trabajo
- Usuario expresa insatisfacción con respuesta

## When NOT to Use

- Consultas teóricas o preguntas puntuales
- Soporte superficial sin preferencias claras
- Conversaciones sin feedback del usuario

## Detección de Oportunidades de Aprendizaje

### Frases Trigger (Detectar en tiempo real)

| Frase | Categoría |
|-------|-----------|
| "no me gusta" | Preferencia |
| "no así no es como lo quiero" | Corrección |
| "corregir" / "corrige" | Corrección |
| "cambiar" / "cambia" | Corrección |
| "no quiero que" | Restricción |
| "siempre hazlo" | Regla |
| "nunca hagas" | Restricción |
| "más formal" / "más casual" | Estilo |
| "bullets" / "párrafos" | Formato |
| "respuestas cortas" / "respuestas largas" | Formato |
| "profesional" / "alegre" / "serio" | Tono |

### Categorías de Aprendizaje

| Categoría | Ejemplo | Destino |
|-----------|---------|---------|
| **Preferencia de estilo** | "No me gusta tan formal" | AGENTS.md, CLAUDE.md |
| **Preferencia de formato** | "Usa bullets no párrafos" | AGENTS.md, CLAUDE.md |
| **Preferencia de tono** | "Soy más alegre/profesional" | AGENTS.md, CLAUDE.md |
| **Corrección de workflow** | "No hagas commits automáticos" | AGENTS.md, CLAUDE.md |
| **Corrección de contenido** | "El plan debe ser en este orden" | AGENTS.md, CLAUDE.md |
| **Restricción** | "Nunca hagas X" | AGENTS.md, CLAUDE.md |
| **Regla** | "Siempre haz Y" | AGENTS.md, CLAUDE.md |

## Protocolo de Captura

### Paso 1: Detectar

Cuando detectes una frase trigger o expresión de insatisfacción:

1. **Identifica la categoría** (estilo, formato, tono, workflow, contenido, restricción, regla)
2. **Extrae el aprendizaje** específico (qué prefiere el usuario)
3. **Determina el destino** (qué archivo actualizar)

### Paso 2: Persistir (Auto-guardar)

**Guardar automáticamente** sin preguntar. Notificar de forma sutil y natural.

**Formato de notificación (sutil):**
> - "De acuerdo, lección aprendida. No volverá a suceder."
> - "Ok, anotado y guardado tu observación."
> - "Entendido, no lo repito."
> - "Anotado. Lo tendré en cuenta siempre."
> - "Listo, queda registrado."

**Reglas:**
- NO mostrar categorías, destinos ni detalles técnicos
- NO usar emojis ni formato elaborado
- Respuesta breve, natural, como una confirmación humana
- Integrar la notificación al flujo de la respuesta, no como bloque separado

### Paso 3: Actualizar archivo

#### Estructura en AGENTS.md / CLAUDE.md

```markdown
### LECCIONES APRENDIDAS

#### Lo que no le gusta al usuario
- [Aprendizaje 1]
- [Aprendizaje 2]

#### Preferencias de estilo
- [Preferencia 1]

#### Preferencias de formato
- [Preferencia 1]

#### Reglas de workflow
- [Regla 1]

#### Restricciones
- [Restricción 1]
```

#### Archivos a actualizar

| Agente | Archivo |
|--------|---------|
| OpenCode | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Gemini | `GEMINI.md` |
| Codex | `AGENTS.md` |

**Multi-agente:** Si el proyecto usa múltiples agentes, actualizar TODOS los archivos relevantes.

### Paso 4: Aplicar

En sesiones futuras, **antes** de generar respuestas:

1. Leer sección "LECCIONES APRENDIDAS" del archivo de configuración
2. Aplicar preferencias aprendidas
3. No repetir errores corregidos

## Detección de Estilo de Comunicación

### Matching de Tono

Detectar el estilo del usuario y adaptar:

| Señal del usuario | Estilo detectado | Adaptación |
|-------------------|------------------|------------|
| Emojis 😊🎉 | Alegre | Usar emojis moderadamente |
| "porfa", "gracias", "vale" | Casual | Tono relajado |
| "estimado", "cordialmente" | Profesional | Tono formal |
| "rápido", "directo" | Conciso | Respuestas cortas |
| "explícame", "detalla" | Explicativo | Respuestas detalladas |

### Reglas de Matching

1. **Detectar** el estilo en los primeros mensajes
2. **Adaptar** el tono de la respuesta
3. **Proponer** registrar el estilo preferido
4. **Persistir** en configuración para sesiones futuras

## Anti-Patterns (Racionalizaciones a Rechazar)

| Racionalización | Realidad |
|-----------------|----------|
| "No tengo memoria persistente" | Usar archivos de configuración como memoria |
| "Cada sesión es independiente" | El aprendizaje debe persistir entre sesiones |
| "Debería decírmelo cada vez" | Ineficiente, registrar automáticamente |
| "Es solo para esta conversación" | El aprendizaje debe ser permanente |
| "No sé qué archivo actualizar" | Usar convención del proyecto (AGENTS.md/CLAUDE.md) |
| "Son sesiones diferentes, cambió de opinión" | Registrar tendencia, no incidente aislado |
| "Es solo una queja puntual, no un patrón" | Toda queja recurrente es patrón |
| "Quizás solo fue en ese tema específico" | Registrar como preferencia general |
| "Son demasiadas preferencias" | Registrar como conjunto, no individualmente |
| "No puedo registrar algo tan ambiguo" | Registrar la tendencia al feedback vago |
| "¿Debería preguntar antes?" | No, auto-guardar y notificar |

## Red Flags - STOP y Registrar

- Usuario dice "no me gusta" → Detectar y proponer registro
- Usuario pide corregir → Capturar el patrón
- Usuario indica preferencia → Registrar para futuro
- Usuario corrige workflow → Actualizar configuración
- Usuario expresa tono preferido → Guardar estilo

**Todos estos significan: Capturar aprendizaje y persistir.**

## Manejo de Escenarios Complejos

### Correcciones Contradictorias

**Problema:** Usuario dice "usa bullets" en una sesión y "no uses bullets" en otra.

**Protocolo:**
1. Detectar la contradicción
2. Preguntar: "¿En qué contextos prefieres X vs Y?"
3. Registrar la preferencia contextual:
   ```markdown
   #### Preferencias de formato
   - Bullets para listas y pasos
   - Párrafos cortos para explicaciones
   ```

### Correcciones Vagas

**Problema:** Usuario dice "no me gusta como organizas" sin especificar.

**Protocolo:**
1. No asumir qué le gusta
2. Preguntar: "¿Puedes mostrarme un ejemplo de lo que prefieres?"
3. Registrar la tendencia al feedback vago:
   ```markdown
   #### Patrones de comunicación
   - Usuario tiende a dar feedback vago
   - Siempre preguntar ejemplos concretos
   ```

### Correcciones con Contexto Técnico

**Problema:** Usuario dice "soy programador senior, no expliques básicas".

**Protocolo:**
1. Detectar el nivel técnico
2. Preguntar: "¿Prefieres que siempre asuma este nivel?"
3. Registrar el perfil técnico:
   ```markdown
   #### Perfil del usuario
   - Nivel: Programador senior
   - Preferencia: Respuestas directas, sin explicaciones básicas
   ```

### Múltiples Correcciones en un Mensaje

**Problema:** Usuario da 3+ correcciones en un solo mensaje.

**Protocolo:**
1. No registrar individualmente
2. Agrupar como conjunto de preferencias
3. Registrar como bloque:
   ```markdown
   #### Preferencias activas
   - Tono: informal, casual
   - Formato: bullets, no párrafos
   - Workflow: preguntar antes de commits
   ```

### Correcciones de Estilo de Comunicación

**Problema:** Usuario indica su estilo (alegre, profesional, etc.).

**Protocolo:**
1. Detectar el estilo en señales del usuario
2. Adaptar el tono de la respuesta
3. Proponer registrar el estilo:
   ```markdown
   #### Estilo de comunicación
   - Tono: [alegre/profesional/casual]
   - Emojis: [sí/no/moderado]
   - Formalidad: [alta/media/baja]
   ```

## Ejemplo de Flujo

```
Usuario: "No me gusta como respondiste, muy formal. Yo habla más casual."

Agente:
1. Detecta: "no me gusta" + preferencia de estilo
2. Actualiza AGENTS.md automáticamente
3. Responde de forma sutil:
   "De acuerdo, lección aprendida. No volverá a suceder."
   (o variaciones: "Ok, anotado.", "Entendido, no lo repito.")

4. En sesiones futuras:
   Lee "LECCIONES APRENDIDAS" y aplica tono casual
```

## Quick Reference

| Acción | Comando |
|--------|---------|
| Detectar aprendizaje | Buscar frases trigger en conversación |
| Persistir | Actualizar AGENTS.md/CLAUDE.md/GEMINI.md automáticamente |
| Notificar | Mostrar qué se guardó al usuario |
| Aplicar | Leer LECCIONES APRENDIDAS en sesiones futuras |
| Matching de tono | Detectar estilo del usuario y adaptar |

## Common Mistakes

1. **Notificación formal o elaborada** → Respuesta sutil y natural, como una confirmación humana
2. **Mostrar detalles técnicos** → No categorías, destinos ni formato técnico
3. **Solo actualizar un archivo** → Multi-agente requiere actualizar todos los archivos
4. **No aplicar en futuro** → Leer LECCIONES APRENDIDAS al inicio de cada sesión
5. **No detectar tono** → Analizar señales del usuario en primeros mensajes
