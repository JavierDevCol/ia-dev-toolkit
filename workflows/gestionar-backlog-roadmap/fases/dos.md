# FASE 2: Construcción del User Story Map y Slicing Funcional

## Objetivo
Desglosar la Visión del Producto y Requerimientos Funcionales de Negocio en una jerarquía clara de Épicas, Features e Historias de Usuario (HUs).

## 🔄 Regla de Sincronización Incremental (Si existen artefactos previos)
- **Preservación de IDs:** Mantén intactos los IDs de HUs y Épicas previas (`HU-101`, `EPIC-01`).
- **Modificación vs. Adición:** Detecta si la nueva documentación MODIFICA Criterios de Aceptación (DoD) de HUs existentes o si AÑADE nuevas `HU-XXX` al mapa.

## Pasos de Ejecución

1. **Mapear Épicas de Negocio (`EPIC-BUS-XXX`):**
   - Identificar los grandes bloques de valor funcional desde la perspectiva del usuario final o del negocio.

2. **Identificar Features de Negocio (`FEAT-BUS-XXX`):**
   - Agrupar capacidades funcionales concretas que resuelven una necesidad del usuario dentro de cada Épica.

3. **Redactar Historias de Usuario (`HU-XXX`):**
   - Aplicar formato estándar: `Como [Rol], Quiero [Acción], Para [Beneficio/Valor]`.

4. **Definir Criterios de Aceptación (BDD):**
   - Cada HU debe contar con al menos 2 criterios de aceptación en formato BDD:
     - **Given** [Contexto / Dado que]
     - **When** [Acción / Cuando]
     - **Then** [Resultado Esperado / Entonces]