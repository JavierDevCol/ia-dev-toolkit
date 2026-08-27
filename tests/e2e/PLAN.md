# Plan de Pruebas E2E — Skills SAC

## Objetivo
Verificar que las skills del pipeline SAC funcionan correctamente de punta a punta, validando:
- Creación correcta de archivos
- Transiciones de estado válidas
- Validación de prerequisitos
- Sincronización del backlog

## Pipeline bajo prueba

```
tomar-contexto → refinar-hu → validar-hu → planificar-hu → ejecutar-plan → sincronizar-backlog
                                                       ↗
                              registrar-hallazgo (bugs)
```

## Escenarios de prueba

### ESC-01: Flujo completo Feature (happy path)
```
1. tomar-contexto    → crea workspace.md, contexto_proyecto.md, backlog
2. refinar-hu        → crea HU.md + Refinamiento.md (estado [R])
3. validar-hu        → aprueba HU, agrega ✅ Aprobada (estado [A])
4. planificar-hu     → crea Plan.md (estado [P])
5. ejecutar-plan     → ejecuta plan, crea Tracking.md (estado [E] → [X])
6. sincronizar-backlog → actualiza backlog con estados correctos
```

### ESC-02: Flujo completo Bug
```
1. tomar-contexto    → crea workspace
2. registrar-hallazgo → crea BUG-001/ con Refinamiento.md desde assets
3. planificar-hu     → planifica bug (estado [P])
4. ejecutar-plan     → ejecuta fix (estado [E] → [X])
```

### ESC-03: Validación de prerequisitos (fallos esperados)
```
1. planificar-hu sin Refinamiento.md → ERROR esperado
2. ejecutar-plan sin Plan.md → ERROR esperado
3. validar-hu sin HU refinada → ERROR esperado
4. sincronizar-backlog sin workspace → ERROR esperado
```

### ESC-04: Transiciones de estado inválidas
```
1. ejecutar-plan con Plan.md COMPLETADO → ERROR esperado
2. planificar-hu con HU en [R] (sin aprobación) → ERROR esperado
3. refinar-hu con HU en [A] (ya aprobada) → SKIP esperado
```

### ESC-05: Detección mono vs multi-proyecto
```
1. tomar-contexto con 1 marcador en raíz → MODO_UNICO
2. tomar-contexto con 0 marcadores + 2+ subcarpetas → MODO_MULTI
3. tomar-contexto con 0 marcadores + 1 subcarpeta → Preguntar
```

## Métricas de éxito

| Métrica | Objetivo |
|---------|----------|
| Escenarios pasados | 100% |
| Archivos generados correctamente | 100% |
| Transiciones de estado válidas | 100% |
| Errores capturados correctamente | 100% |

## Estructura de archivos

```
tests/e2e/
├── PLAN.md                    # Este archivo
├── fixtures/                  # Datos de prueba
│   ├── workspace-mono/        # Workspace mono-proyecto mock
│   └── workspace-multi/       # Workspace multi-proyecto mock
├── scripts/                   # Scripts de prueba
│   ├── setup.sh               # Crea workspaces mock
│   ├── test-01-flujo-feature.sh
│   ├── test-02-flujo-bug.sh
│   ├── test-03-prerequisitos.sh
│   ├── test-04-transiciones.sh
│   ├── test-05-deteccion-modo.sh
│   └── run-all.sh             # Ejecuta todas las pruebas
└── reports/                   # Resultados
    └── .gitkeep
```
