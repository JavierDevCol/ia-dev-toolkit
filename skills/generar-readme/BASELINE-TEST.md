# Baseline Test - Generar README Skill

## Escenario de Presión 1: README Básico

**Contexto:** Usuario pide generar un README para su proyecto.

**Mensaje del usuario:**
> "Genera un README para mi proyecto."

**Comportamiento baseline esperado (sin skill):**
- Agente genera un README con secciones básicas
- No incluye todas las secciones necesarias
- No valida que el proyecto tenga la información requerida
- No pregunta por información faltante
- README generado es incompleto o genérico

**Racionalización del agente:**
> "Generé un README básico con las secciones principales."

**Problema:** README incompleto, falta información crítica.

---

## Escenario de Presión 2: README sin Información del Proyecto

**Contexto:** Usuario pide README sin dar contexto del proyecto.

**Mensaje del usuario:**
> "Crea un README para mi repo."

**Comportamiento baseline esperado (sin skill):**
- Agente genera README genérico
- No pregunta por: título, descripción, tecnologías, instalación
- README no refleja el proyecto real
- Secciones vacías o con placeholders

**Racionalización del agente:**
> "No me diste información, hice lo mejor que pude."

**Problema:** No valida información requerida antes de generar.

---

## Escenario de Presión 3: README Incompleto

**Contexto:** Usuario pide README pero el proyecto no tiene toda la info.

**Mensaje del usuario:**
> "Necesito un README para mi proyecto Python."

**Comportamiento baseline esperado (sin skill):**
- Agente genera README con secciones estándar
- No verifica si el proyecto tiene: requirements.txt, tests, licencia
- No sugiere agregar secciones faltantes
- README no es accionable (no se puede instalar/usar)

**Racionalización del agente:**
> "Incluí las secciones estándar de un README."

**Problema:** No valida que el proyecto tenga la información necesaria.

---

## Escenario de Presión 4: README sin Estructura

**Contexto:** Usuario pide README "completo" pero no especifica qué incluir.

**Mensaje del usuario:**
> "Hazme un README completo y profesional."

**Comportamiento baseline esperado (sin skill):**
- Agente incluye muchas secciones
- No sigue un orden lógico
- No incluye: badges, contribución, tests
- README es largo pero no estructurado

**Racionalización del agente:**
> "Incluí todas las secciones que pude."

**Problema:** No sigue mejores prácticas de estructura.

---

## Escenario de Presión 5: README sin Validación

**Contexto:** Usuario pide README pero no verifica si es correcto.

**Mensaje del usuario:**
> "Genera el README y listo."

**Comportamiento baseline esperado (sin skill):**
- Agente genera README sin validar
- No verifica: enlaces rotos, badges funcionales, instrucciones claras
- No sugiere mejoras
- README puede tener errores

**Racionalización del agente:**
> "Generé el README como pediste."

**Problema:** No valida la calidad del README generado.

---

## Patrones de Racionalización Identificados

1. **"Generé un README básico"** - No exige completitud
2. **"No me diste información"** - No valida antes de generar
3. **"Incluí las secciones estándar"** - No verifica que sean necesarias
4. **"Incluí todas las secciones que pude"** - No sigue estructura
5. **"Generé el README como pediste"** - No valida calidad

---

## Secciones Mínimas de un README (Según FreeCodeCamp)

| Sección | Obligatoria | Descripción |
|---------|-------------|-------------|
| Título | ✅ | Nombre del proyecto |
| Descripción | ✅ | Qué hace, por qué, cómo |
| Instalación | ✅ | Cómo instalar y ejecutar |
| Uso | ✅ | Cómo usar el proyecto |
| Créditos | ✅ | Colaboradores y referencias |
| Licencia | ✅ | Qué pueden hacer con el código |
| Badges | ❌ | Estadísticas y herramientas |
| Contribución | ❌ | Cómo contribuir |
| Tests | ❌ | Cómo ejecutar pruebas |

---

## Métricas de Éxito

- **Completitud:** Incluye todas las secciones obligatorias
- **Validez:** Instrucciones son ejecutables
- **Estructura:** Sigue orden lógico
- **Claridad:** Instrucciones son comprensibles
- **Profesionalismo:** Incluye badges, contribución, tests
