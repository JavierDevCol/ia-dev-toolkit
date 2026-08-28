# Autoaprendizaje Skill

Captura aprendizajes del usuario en tiempo real y persiste en archivos de configuración.

## Uso

La skill se activa automáticamente cuando detecta expresiones de insatisfacción:

- "no me gusta"
- "no así no es como lo quiero"
- "corregir" / "corrige"
- "cambiar" / "cambia"
- "no quiero que"
- "siempre hazlo"
- "nunca hagas"

## Flujo

1. **Detecta** frases trigger en la conversación
2. **Propone** registrar el aprendizaje
3. **Persiste** en AGENTS.md/CLAUDE.md/GEMINI.md
4. **Aplica** en sesiones futuras

## Archivos que actualiza

| Agente | Archivo |
|--------|---------|
| OpenCode | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| Gemini | `GEMINI.md` |
| Codex | `AGENTS.md` |

## Estructura en archivos de configuración

```markdown
### LECCIONES APRENDIDAS

#### Lo que no le gusta al usuario
- [Aprendizaje 1]

#### Preferencias de estilo
- [Preferencia 1]

#### Preferencias de formato
- [Preferencia 1]

#### Reglas de workflow
- [Regla 1]

#### Restricciones
- [Restricción 1]
```

## Referencia rápida

| Acción | Comando |
|--------|---------|
| Detectar aprendizaje | Buscar frases trigger en conversación |
| Proponer registro | Mostrar categoría, aprendizaje, destino |
| Persistir | Actualizar AGENTS.md/CLAUDE.md/GEMINI.md |
| Aplicar | Leer LECCIONES APRENDIDAS en sesiones futuras |
| Matching de tono | Detectar estilo del usuario y adaptar |
