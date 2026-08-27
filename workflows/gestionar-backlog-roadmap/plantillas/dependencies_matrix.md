---
target_path: "./artifacts/HU/dependencies_matrix.md"
type: dependency_matrix
---

# 🔗 Matriz de Dependencias y Bloqueos

## Grafo de Impacto Técnico / Funcional

| Item Bloqueado (Negocio) | Enabler Requerido (Bloqueante) | Nivel de Riesgo | Estado de Desbloqueo |
| :--- | :--- | :---: | :---: |
| `HU-101` [Nombre HU] | `STORY-ENABLER-01` | **Crítico** | 🔴 Bloqueado |
| `HU-102` [Nombre HU] | `STORY-ENABLER-02` | **Alto** | 🟢 Desbloqueado |

---

## Acciones de Desbloqueo Requeridas
- La finalización de `STORY-ENABLER-01` por parte de DevOps habilitará la ejecución de `HU-101` en el siguiente Sprint.