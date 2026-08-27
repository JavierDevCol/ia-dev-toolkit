---
name: refinar-hu
description: >
  Usa esta skill cuando el usuario proporcione una HU para refinamiento
  o solicite refinar una HU existente.
---

# Refinar HU

## Overview

Refina una HU definiendo criterios de aceptación SMART, estimación y desglose técnico vertical, con soporte para partición en tasks.

## When to Use

- El usuario proporciona una HU nueva para refinamiento
- Solicitud de re-refinamiento (modo ajuste)
- HU sin `Refinamiento.md` o con estado `[N]`

**Cuándo NO usar:** HU en `[R]` sin cambios → `>validar_hu`; HU en `[A]` o `[P]` → ya pasó este flujo; sin contexto → `>tomar_contexto`.

## Implementation

### 1. Configuración y modo

Leer config, detectar workspace (multi/proyecto). Verificar `{hu_folder}/[ID-HU]/`: existe → **MODO_AJUSTE**; no existe → **MODO_NUEVO**.

**SI Tipo = Bug:** pre-poblar con archivos afectados, CA base "bug no se reproduce", incorporar Causa Raíz.

### 2. Complejidad y partición

| Nivel | Indicadores | SP |
|-------|-------------|----|
| 🟢 BAJO | CRUD básico | 2-3 |
| 🟡 MEDIO | Lógica moderada, 1-2 integraciones | 5-8 |
| 🔴 ALTO | Múltiples integraciones, impacto arquitectónico | 13+ |

**Partición:** solo si complejidad ≥ MEDIO, CAs ≥ 3, estimación ≥ 8 SP → proponer (sugerencia, no obligatoria).

### 3. Refinamiento y desglose

Aplicar SMART a cada CA. Desglose técnico vertical end-to-end.

**Plano:** IDs `HU-XXX-UI-01`, `HU-XXX-API-01`.
**Particionado:** CAs integración (padre) → CAs granulares por task → IDs `[ID-HU]-TASK-N-API-01`.

```
HU-001/           ← padre: HU.md + Refinamiento.md
HU-001-TASK-01/   ← hija: HU.md ("Padre: HU-001") + Refinamiento.md
```

Trazabilidad: CAs TASK-N completadas → CA padre `[~]` → `>validar_ca --scope integracion` → HU completada.

### 4. Estimación y persistencia

Calcular SP, analizar riesgos (`--incluir_riesgos`). Modo Nuevo: crear carpetas, plantillas, backbone `[N/R] → [R]`. Modo Ajuste: incrementar Iteración.

```
✅ REFINAMIENTO COMPLETADO: [ID-HU] | CA: [X] | SP: [Z] | Siguiente: >validar_hu [ID-HU]
```

## Quick Reference

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `id_hu` | string | — | ID de la HU a refinar |
| `--proyecto` | string | null | Proyecto destino (requerido multi-proyecto) |
| `--formato_estimacion` | option | `ambos` | `story_points`, `horas`, `ambos` |
| `--nivel_detalle` | option | `medio` | `alto`, `medio`, `bajo` |
| `--incluir_riesgos` | flag | true | Análisis de riesgos |
| `--generar_tareas` | flag | true | Desglose técnico |
| `--incluir_testing` | flag | true | Testing en estimación |

**Reglas:** CA no medibles → rechazar. Desglose SIEMPRE vertical. No forzar partición en BAJO.

## Common Mistakes

| Error | Causa | Solución |
|-------|-------|----------|
| HU incompleta | Formato incorrecto | Solicitar: "Como [rol], quiero [func], para [beneficio]" |
| Sin CA | Faltantes | Generar CA inferidos, solicitar validación |
| HU épica | Demasiado grande | Sugerir partición |
| Proyecto no encontrado | Nombre incorrecto | Verificar en workspace.md |
