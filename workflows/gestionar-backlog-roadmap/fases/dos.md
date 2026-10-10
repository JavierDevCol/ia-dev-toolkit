# FASE 2: Construcción del User Story Map y Slicing Funcional

## Objetivo
Desglosar la Visión del Producto y Requerimientos Funcionales de Negocio en una jerarquía clara de Épicas, Features e Historias de Usuario (HUs).

## 🔄 Regla de Sincronización Incremental (Si existen artefactos previos)
- **Preservación de IDs:** Mantén intactos los IDs de HUs y Épicas previas (`HU-101`, `EPIC-01`).
- **Modificación vs. Adición:** Detecta si la nueva documentación MODIFICA Criterios de Aceptación (DoD) de HUs existentes o si AÑADE nuevas `HU-XXX` al mapa.

## Pasos de Ejecución

1. **Mapear Épicas de Negocio (`EPIC-BUS-XXX`):**
   - Leer `./artifacts/vision_producto.md` sección "2. MVP Definido" y reutilizar los **Módulos / Épicas Candidatas** (2.7) ya definidos ahí como punto de partida — no inventar una agrupación distinta sin justificarlo ante el usuario.
   - Etiquetar cada Épica según su origen en el MVP: `MVP-CRÍTICO` (funcionalidades MUST), `MVP-DESEABLE` (SHOULD), o `DIFERIDO` (lo que `vision_producto.md` marcó como Fuera del MVP — registrar solo como backlog futuro, sin desarrollar HUs completas todavía).

2. **Identificar Features de Negocio (`FEAT-BUS-XXX`):**
   - Agrupar capacidades funcionales concretas que resuelven una necesidad del usuario dentro de cada Épica.

3. **Redactar Historias de Usuario (`HU-XXX`):**
   - Aplicar formato estándar: `Como [Rol], Quiero [Acción], Para [Beneficio/Valor]`.
   - El `[Rol]` debe ser uno de los actores ya identificados en la Sección 2.5 (Mapa de Actores) de `vision_producto.md` — no inventar roles nuevos sin confirmarlo con el usuario.

4. **Definir Criterios de Aceptación (BDD):**
   - Cada HU debe contar con al menos 2 criterios de aceptación en formato BDD:
     - **Given** [Contexto / Dado que]
     - **When** [Acción / Cuando]
     - **Then** [Resultado Esperado / Entonces]

---

## Entregable

Épicas e Historias de Usuario de negocio (`EPIC-BUS-{{id}}.md`, nombre dinámico), aplicando `./plantillas/EPIC-BUS-XX.MD`.

---

## Criterios de completitud

- [ ] Cada Épica mapea a un Módulo/Épica Candidata o a un nuevo bloque justificado explícitamente
- [ ] Cada HU usa un Rol real del Mapa de Actores (ninguno inventado)
- [ ] Cada HU tiene al menos 2 criterios de aceptación BDD
- [ ] Ninguna HU "DIFERIDO" quedó con desarrollo completo antes de tiempo
- [ ] IDs previos (`HU-101`, `EPIC-01`) se preservaron sin modificar