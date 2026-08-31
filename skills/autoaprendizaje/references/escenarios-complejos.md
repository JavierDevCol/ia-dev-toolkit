# Escenarios Complejos - Autoaprendizaje

## Detección de Estilo de Comunicación

### Matching de Tono

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

## Manejo de Escenarios Complejos

### Correcciones Contradictorias

Usuario dice "usa bullets" en una sesión y "no usa bullets" en otra.

**Protocolo:** Detectar → Preguntar contextos → Registrar preferencia contextual:
```markdown
#### Preferencias de formato
- Bullets para listas y pasos
- Párrafos cortos para explicaciones
```

### Correcciones Vagas

Usuario dice "no me gusta como organizas" sin especificar.

**Protocolo:** No asumir → Preguntar ejemplo concreto → Registrar tendencia al feedback vago.

### Correcciones con Contexto Técnico

Usuario dice "soy programador senior, no expliques básicas".

**Protocolo:** Detectar nivel → Preguntar si siempre asumir ese nivel → Registrar perfil técnico.

### Múltiples Correcciones en un Mensaje

Usuario da 3+ correcciones en un solo mensaje.

**Protocolo:** Agrupar como conjunto → Registrar como bloque:
```markdown
#### Preferencias activas
- Tono: informal, casual
- Formato: bullets, no párrafos
- Workflow: preguntar antes de commits
```

### Correcciones de Estilo de Comunicación

Usuario indica su estilo (alegre, profesional, etc.).

**Protocolo:** Detectar señales → Adaptar tono → Registrar:
```markdown
#### Estilo de comunicación
- Tono: [alegre/profesional/casual]
- Emojis: [sí/no/moderado]
- Formalidad: [alta/media/baja]
```
