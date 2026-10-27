---
name: refinar-hu
description: >
  Use when the user provides a HU for refinement or requests refining
  an existing HU.
ready: true
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

Leer config con memctl (`{hu_folder}` = `artifacts.hu_folder`), detectar workspace (multi/proyecto). Verificar `{hu_folder}/[ID-HU]/`: existe → **MODO_AJUSTE**; no existe → **MODO_NUEVO**.

Comandos de config y firma:

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa tal cual en el resto de esta skill (no recalcular ni inventar rutas):

| Placeholder / dato | Valor = salida de |
|---|---|
| `{{usuario.nombre}}` | `sh .SAC/memctl.sh get usuario.nombre` |
| `usuario.incluir_firma_en_documentos` | `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` |
| `{hu_folder}` | `sh .SAC/memctl.sh get artifacts.hu_folder` |

memctl es solo lectura y su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq` o usar `~/.SAC/memctl.sh` (instalación global); si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores. `null`, vacío o exit 2 → no configurado.

`usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el Refinamiento en el paso 4. Si está vacío o la clave no existe, omitir el sufijo de la firma; no inventar un nombre.

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

Si `usuario.incluir_firma_en_documentos` es `true`, agregar al final de `Refinamiento.md`:

```
> **Refinador:** {{usuario.nombre}}
> **Fecha:** {{fecha}}
```

Sin `usuario.nombre` configurado, la línea queda `> **Refinador**`.

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
