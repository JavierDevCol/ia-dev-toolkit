---
name: autoaprendizaje
description: Use when user expresses dissatisfaction ("no me gusta", "no así no es como lo quiero", "corregir", "cambiar", "usa ..."), requests corrections, or indicates preferences for style, format, tone, or workflow. Detects learning opportunities in real-time and persists them to config files.
ready: true
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

## Quick Reference

| Acción | Comando |
|--------|---------|
| Detectar | Buscar frases trigger |
| Persistir | Auto-actualizar config files |
| Notificar | Confirmación sutil al usuario |
| Aplicar | Leer LECCIONES APRENDIDAS en futuras sesiones |

## Detection → Capture → Persist

### 1. Detectar

Buscar frases trigger en tiempo real:

| Frase | Categoría |
|-------|-----------|
| "no me gusta" | Preferencia |
| "no así no es como lo quiero" | Corrección |
| "corregir" / "corrige" | Corrección |
| "cambiar" / "cambia" | Corrección |
| "no quiero que" | Restricción |
| "siempre hazlo" / "nunca hagas" | Regla/Restricción |
| "más formal" / "más casual" | Estilo |
| "bullets" / "párrafos" | Formato |

### 2. Persistir

Guardar automáticamente sin preguntar. Notificación sutil:
- "De acuerdo, lección aprendida. No volverá a suceder."
- "Ok, anotado."

**Reglas:** No mostrar categorías/destinos técnicos. No usar emojis. Respuesta breve, natural.

### 3. Actualizar archivo

Estructura en AGENTS.md / CLAUDE.md:

```markdown
### LECCIONES APRENDIDAS

#### Lo que no le gusta al usuario
- [Aprendizaje]

#### Preferencias de estilo / formato
- [Preferencia]

#### Reglas de workflow
- [Regla]

#### Restricciones
- [Restricción]
```

| Agente | Archivo |
|--------|---------|
| OpenCode / Codex | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Gemini | `GEMINI.md` |

**Multi-agente:** Actualizar TODOS los archivos relevantes.

### 4. Aplicar

En sesiones futuras: leer "LECCIONES APRENDIDAS" → aplicar preferencias → no repetir errores.

## Anti-Patterns

| Racionalización | Realidad |
|-----------------|----------|
| "No tengo memoria persistente" | Usar archivos de configuración |
| "Cada sesión es independiente" | Persistir entre sesiones |
| "¿Debería preguntar antes?" | No, auto-guardar y notificar |

**Detailed scenarios:** See references/escenarios-complejos.md

## Common Mistakes

1. **Notificación formal o elaborada** → Respuesta sutil y natural, como una confirmación humana
2. **Mostrar detalles técnicos** → No categorías, destinos ni formato técnico
3. **Solo actualizar un archivo** → Multi-agente requiere actualizar todos los archivos
4. **No aplicar en futuro** → Leer LECCIONES APRENDIDAS al inicio de cada sesión
