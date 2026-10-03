---
target_path: "./artifacts/HU/dependencies_matrix.md"
type: dependency_matrix
---

# 🔗 Matriz de Dependencias y Bloqueos

## Grafo de Impacto Técnico / Funcional

| Item Bloqueado (Negocio) | Enabler Requerido (Bloqueante) | Nivel de Riesgo | Estado de Desbloqueo |
| :--- | :--- | :---: | :---: |
| `HU-101` Ver catálogo de productos | `STORY-ENABLER-02` | **Alto** | 🔴 Bloqueado |
| `HU-102` Ver información del negocio | `STORY-ENABLER-02` | **Alto** | 🔴 Bloqueado |
| `HU-103` Actualizar catálogo de forma simple | `STORY-ENABLER-02` | **Medio** | 🔴 Bloqueado |
| `HU-201` Armar pedido (selección + cantidades) | `STORY-ENABLER-02` | **Alto** | 🔴 Bloqueado |
| `HU-202` Enviar pedido por WhatsApp | `STORY-ENABLER-03` | **Crítico** | 🔴 Bloqueado |
| `HU-203` Enviar consulta general por WhatsApp | `STORY-ENABLER-03` | **Crítico** | 🔴 Bloqueado |
| `HU-204` Recibir pedidos con formato claro | `STORY-ENABLER-03` | **Alto** | 🔴 Bloqueado |
| Lanzamiento a Producción (todas las HUs de negocio) | `STORY-ENABLER-01` | **Crítico** | 🔴 Bloqueado |

---

## Acciones de Desbloqueo Requeridas
- La finalización de `STORY-ENABLER-02` (estructura base del sitio) en Sprint 0 habilita el desarrollo de `HU-101`, `HU-102`, `HU-103` y `HU-201` en Sprint 1.
- La finalización de `STORY-ENABLER-03` (generador de enlace WhatsApp) en Sprint 0 habilita el desarrollo de `HU-202`, `HU-203` y `HU-204` en Sprint 1.
- La finalización de `STORY-ENABLER-01` (repositorio + hosting + despliegue continuo) en Sprint 0 habilita que cualquier HU de negocio pueda salir a producción, independientemente del sprint en que se desarrolle.
- **Nota de secuenciación funcional (no bloqueo técnico):** `HU-201` (armar pedido) debe implementarse antes o junto con `HU-202` (enviar pedido) por dependencia funcional obvia (no se puede enviar un pedido que no se ha armado), aunque el modelo de dependencias de este workflow solo rastrea bloqueos Enabler→HU. Ambas quedan planificadas en el mismo Sprint 1 para respetar este orden natural.
