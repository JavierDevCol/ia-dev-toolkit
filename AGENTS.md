# Instrucciones del agente

## 📊 Presentación de Work Items [OBLIGATORIO]
Siempre que se listen Work Items (resultado de consultas, búsquedas o resúmenes), presentarlos en una **tabla ordenada** que incluya como mínimo:
`ID` | `Tipo` | `Título` | `Estado` | `Horas completadas` (si aplica)
Agrupar por estado: Active → New → Closed.

## Formato de Preguntas
Toda interacción interactiva debe usar el snippet de **respuesta rápida**:
> **🤷 [Pregunta]?**
> - [Ícono] [Letra] **Texto de la opción**

## 🔄 Control de Cambios (Modo Nota)
Siempre que el usuario solicite leer, modificar o crear archivos en el repositorio, incluye este recordatorio:
> **Rectifica la rama en la que trabajamos.**

## 🌳 Gestión de Ramas y Commits

### 1. Creación de Rama
Cuando el usuario solicite crear una nueva rama de trabajo, ejecuta este flujo:
1. **Validación de Origen:** Consulta la rama base utilizando el protocolo de respuesta rápida.
2. **Formato de Nombre (kebab-case y minúsculas):**
   - Si está asociada a una historia de usuario: `hu-[ID]-[descripcion-kebab-case]`
   - Si es un caso general (Hotfix, chore, etc.): `[descripcion-kebab-case]`

### 2. Commit Inicial [OBLIGATORIO]
Inmediatamente después de crear la rama, debes realizar un **commit vacío** obligatorio:
- Formato para HU: `chore: iniciar desarrollo de HU [ID]`
- Formato general: `chore: iniciar cambios en [descripcion]`

### 3. Mensajes de Commit (Conventional Commits) [OBLIGATORIO]
Todo commit subsiguiente debe seguir estrictamente la estructura: `<tipo>[ámbito opcional]: <descripción compacta pero detallada>`.
- `feat:` — Nueva funcionalidad.
- `fix:` — Corrección de errores.
- `refactor:` — Optimización de código sin cambios funcionales.
- `docs:` — Modificaciones exclusivas en documentación.
- `chore:` — Tareas de mantenimiento o configuración.

*Nota de seguridad:* Si el código rompe la compatibilidad anterior, incluye obligatoriamente `BREAKING CHANGE:` al inicio del cuerpo o en el pie del mensaje.

### 4. Flujo de Aprobación de Commit [OBLIGATORIO]
**NUNCA** ejecutes un commit final sin aprobación. Muestra un preview del título y descripción del mensaje al usuario utilizando el formato estándar:

> **🤷 ¿Confirmo el commit con el mensaje estructurado?**
> - ✅ [S] **Sí, realizar commit y push**
> - ✏️ [E] **Editar el mensaje del commit**
> - ❌ [N] **No, mantener los cambios en staging sin commitear**


## 💬 Gestión y Registro de Comentarios en WIs [OBLIGATORIO]

### 1. Directrices Universales (Aplican a todo comentario)
- **Formato:** Todo comentario insertado en un Work Item (WI) debe estructurarse obligatoriamente usando sintaxis limpia de Markdown.
- **Inserción Líquida:** Envía siempre el texto final al WI como **texto plano Markdown directo** (sin envolver el resultado en bloques de código contenedores), permitiendo que la plataforma interprete los estilos de forma nativa.
- **Menciones ADO [OBLIGATORIO]:** Antes de publicar **cualquier comentario** (Caso A o Caso B), preguntar siempre:
  > **🤷 ¿Deseas etiquetar a alguno de estos colaboradores en el comentario?**
  > - 👤 **[A]** Edgar Alexander Torres Erazo → `@<96517b2d-3823-62fd-ae74-0872c1c9c3a9>`
  > - 👤 **[L]** Lady Marcela Suarez Agudelo → `@<7c277620-4b79-652b-a18d-5d93dd85fff6>`
  > - 👥 **[AL]** Ambos
  > - 🔕 **[N]** Ninguno

  Insertar las menciones seleccionadas **al inicio del comentario**, antes del cuerpo principal. Usar siempre el formato de ID de ADO `@<GUID>` para que la plataforma resuelva la mención nativa correctamente.

- **Reasignación automática [OBLIGATORIO]:** Si el usuario selecciona etiquetar a **Alexander** (`[A]` o `[AL]`), inmediatamente después de publicar el comentario, **reasignar el WI** a Edgar Alexander Torres Erazo usando `wit_update_work_item` con el campo `System.AssignedTo = ettorres@bmm.com.co`. Notificar al usuario que el responsable fue actualizado.

---

### 2. Caso A: Comentarios de Entrega Formal
Aplica este flujo específico cuando el usuario solicite un comentario de entrega (`RELEASE`, `FEATURE`, `FIX`, `HOTFIX`):

#### ⚙️ Configuración Dinámica y Emojis
- **Emojis:** `🔧` para FIX | `🚨` para HOTFIX | `🚀` para RELEASE/FEATURE.
- **Rama:** Si no hay `{rama_origen}`, elimina su línea de la plantilla.
- **Fecha:** Inserta automáticamente la fecha actual `{YYYY-MM-DD}`.

#### 📄 Plantilla de Entrega (Markdown)
```markdown
### {Emoji} ENTREGA: `{RELEASE | FEATURE | FIX | HOTFIX}` v`{versión}`
- **📦 PROYECTO:** `{nombre_repo}`
- **📅 FECHA:** `{YYYY-MM-DD}`
- **🌿 RAMA:** `{rama_origen}`

---

#### 📋 DESCRIPCIÓN
{Breve descripción de lo que se entrega}

#### 🔄 CAMBIOS
• `{feat|fix|chore}`: {descripción del cambio}
• `{feat|fix|chore}`: {descripción del cambio}

#### 📦 ENTREGABLES
• **`release-notes.md`** ➔ `{ruta}/entrega_release/{nombre_repo}/{version}/`
• **`CONFIG-ENTORNO-PR`** ➔ `{ruta}/entrega_release/{nombre_repo}/{version}/`

#### ⚙️ ACCIONES REQUERIDAS AL BANCO
1. Crear PR de `{rama}` ➔ `des`
2. Mergear PR a `des`
3. Taggear `v{versión}` en `des`
4. Desplegar en **DES**
5. Configurar variables/colas según **`CONFIG-ENTORNO-PR`**

> ⚠️ **NOTAS ADICIONALES**
> {Notas adicionales si aplica. Si no hay notas, eliminar este bloque}
```

#### 🔄 Flujo de Aprobación y Mención (Caso A)
1. **Preview:** Muestra el código crudo en un bloque ` ```markdown ` y solicita confirmación:
   > **🤷 ¿El formato Markdown del comentario de entrega es correcto?**
   > - ✅ [C] **Confirmar y continuar**
   > - ✏️ [E] **Editar datos**

2. **Mención posterior:** Tras confirmar con `[C]`, aplicar el flujo de menciones definido en **Directrices Universales §1** (preguntar por Alexander y/o Lady usando sus IDs de ADO).

---

## 🗂️ Bitácora Técnica del Proyecto [PROTOCOLO]

Ruta raíz local: ` /Users/javier.garcia/Documents/BMM/BANCA_X_WHATSAPP/bitacora-tecnica/ `

### 🚨 Reglas de Operación (Bitácora)

1. **Lectura Condicional (Según la Intención):**
   - **Consultas Generales (ADO):** Si solo se pide el estado, título o descripción del WI desde Azure DevOps, responde usando los datos de la plataforma sin leer archivos locales.
   - **Análisis Técnico o Debugging:** Si se solicita solucionar un bug, desarrollar o investigar una falla, lee obligatoriamente el archivo `analisis.md` **Y todos los archivos `.txt` de la carpeta `LOGS/`** dentro del directorio del `[ID_WI]` antes de responder.

2. **Escritura Al Grano [CRÍTICO]:** Al terminar la sesión, crea o actualiza `analisis.md` y guarda las trazas en `LOGS/`. El contenido de la bitácora debe ser **estrictamente técnico y directo**: registra datos puntuales, hashes, queries y hechos concretos en viñetas cortas. Prohíbe introducciones, resúmenes narrativos o explicaciones redundantes.

3. **Sincronización Proactiva (Solo durante Análisis Técnico):** Esta regla **SOLO** se ejecuta si ya estás leyendo la bitácora local debido a una solicitud de análisis o desarrollo (Punto 1, Caso 2). Si detectas que el estado real en ADO cambió respecto a lo escrito en el `analisis.md` local, alerta al usuario:
   > ⚠️ **Divergencia detectada:** El PR #[Número] figura como MERGEADO en ADO, pero está PENDIENTE en local.
   > **🤷 ¿Actualizo el archivo `analisis.md` con los nuevos datos de ADO?**
   > - 🔄 [S] **Sí, sincronizar bitácora local**
   > - ❌ [N] **No, mantener archivo sin cambios**


### 📄 Estructura Base: `analisis.md`
```markdown
# 🔍 Análisis: WI #[ID_WI] — [Título Corto de la Falla]
- **Fecha:** YYYY-MM-DD
- **Microservicio / Componente:** [Nombre]
- **Rama de Trabajo:** ` [nombre_rama] `

## 🧠 Causa Raíz Detectada
[Explicación concisa de por qué fallaba el sistema en el código o base de datos].

## 🛠️ Acciones Realizadas (Historial de Cambios)
- **Cambios en Código:** [Mapeo de archivos modificados / Firmas / Capa hexagonal]
- **Commits Ejecutados:**
  - `[hash_1]` — fix: [descripción]
  - `[hash_2]` — refactor: [descripción]
- **PRs Creados / Mergeados:**
  - **# [Número PR]** — `[Origen]` ➔ `[Destino]` ([Estado: ✅ Mergeado / 🟡 Pendiente])

## 🪵 Evidencias y Consultas de Diagnóstico
- **Logs de Error:** Encontrados en `LOGS/[nombre_log].txt`
- **Queries Útiles:** [Pega aquí los comandos SQL o scripts bash usados para aislar el problema]
[Script o query limpia]

## ⏳ Próximos Bloqueantes (Dependencias)
- [ ] [Aprobaciones de terceros, despliegues pendientes en DES por infraestructura o pruebas de QA].
```
---

### 3. Caso B: Comentarios Generales y Técnicos
Aplica este flujo para cualquier otra anotación, duda, tarea o actualización en el WI que no sea una entrega formal:

1. **Diseño:** Estructura el mensaje usando títulos, negritas o viñetas según amerite el texto.
2. **Preview Obligatorio:** Muestra el texto final crudo dentro de un bloque ` ```markdown ` y solicita validación:
   > **🤷 ¿El formato de este comentario es correcto antes de publicarlo?**
   > - ✅ [C] **Confirmar e insertar comentario**
   > - ✏️ [E] **Editar el contenido**
3. **Mención posterior:** Tras confirmar con `[C]`, aplicar el flujo de menciones definido en **Directrices Universales §1** (preguntar por Alexander y/o Lady usando sus IDs de ADO).131735


## 🎯 Validación de Comprensión (Feedback Loop) [OBLIGATORIO]

Cuando el usuario valide tu entendimiento con preguntas como "¿entiendes?", "¿comprendes?", "¿está claro?" o similares, aplica estrictamente este protocolo:

### 1. Prohibición de Respuestas Vacías
- Nunca respondas con un simple "Sí, entiendo" o "Entendido". Está prohibido usar afirmaciones genéricas que no aporten valor.

### 2. Entrega de Preview Sintético
- Devuelve inmediatamente un resumen ultra-compacto (preview) con los puntos clave, requerimientos técnicos o la lógica exacta que captaste de su mensaje. Usa viñetas directas y datos concretos. Sin introducciones ni rodeos.

### 3. Cierre con Respuesta Rápida
- Al final absoluto de tu preview, incluye obligatoriamente la validación usando el formato estándar:
  > **🤷 ¿Mi interpretación de tu propuesta es correcta?**
  > - ✅ [C] **Correcto, podemos continuar**
  > - ❌ [I] **Incorrecto, déjame aclararlo**