---
target_path: "./artifacts/backlog_roadmap.md"
type: summary_report
---

# 📥 Plan de Inception y Roadmap del Backlog

## 1. Registro de Sprints

| Sprint | Fecha Inicio | Fecha Fin | Estado |
| :--- | :---: | :---: | :---: |
| Sprint 0 (Fundacional) | AAAA-MM-DD | AAAA-MM-DD | 🔵 En Curso |
| Sprint 1 | AAAA-MM-DD | AAAA-MM-DD | ⚪ Planificado |

> Solo puede haber **un** Sprint en 🔵 `En Curso` a la vez. Los Sprints cerrados pasan a ✅ `Cerrado` y no se reabren (ver regla de Historial Congelado en `fases/cuatro.md`).

---

## 2. Métricas de Capacidad por Sprint
- **Capacidad Sprint 0 (Setup):** 90% Enablers / 10% Setup Inicial
- **Capacidad Sprints Regulares (1-N):** 70% Negocio / 20% Enablers / 10% Deuda & Bugs

---

## 3. Priorización WSJF (Top Items)

| ID | Tipo | Título | Sprint Asignado | Score WSJF | Estado |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `EPIC-ENABLER-01` | Enabler | Setup de Arquitectura Base | Sprint 0 (tentativo) | 12.5 | `READY` |
| `EPIC-BUS-01` | Negocio | Gestión de Usuarios y Auth | Sprint 1 (tentativo) | 8.0 | `BLOCKED` |

> **Tentativo vs. Confirmado:** el Sprint asignado es tentativo hasta que la HU/Story pase a `[R] Refinada` (skill `refinar-hu`). A partir de ahí se considera confirmado para ese Sprint.

---

## 4. Sequenced Sprint Roadmap

### 🚀 Sprint 0 (Fundacional)
- [ ] `STORY-ENABLER-01` (DevOps IaC)
- [ ] `STORY-ENABLER-02` (Boilerplate Architecture)

### 📦 Sprint 1 (Primer Incremento de Valor)
- [ ] `HU-101` [Nombre de la primera HU desbloqueada]
- [ ] `HU-102` [Nombre de la segunda HU desbloqueada]

---

> **Product Owner:** {{usuario.nombre}}
> **Fecha:** {{fecha}}