# Manual de Herramientas OpenCode - Análisis Detallado

> **Fuente:** [https://opencode.ai/docs/es/tools/](https://opencode.ai/docs/es/tools/)
> **Fecha de análisis:** 31 de agosto de 2026
> **Propósito:** Guía de referencia de las herramientas integradas en OpenCode.

---

## Tabla de Contenidos

1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Configuración de Herramientas](#2-configuración-de-herramientas)
3. [Herramientas Integradas](#3-herramientas-integradas)
4. [Herramientas Personalizadas](#4-herramientas-personalizadas)
5. [Servidores MCP](#5-servidores-mcp)
6. [Ignorar Patrones](#6-ignorar-patrones)
7. [Buenas Prácticas](#7-buenas-prácticas)

---

## 1. Conceptos Fundamentales

### ¿Qué son las herramientas en OpenCode?

Las **herramientas** permiten que LLM realice acciones en su código base.

**Características principales:**
- Viene con herramientas integradas
- Ampliable con herramientas personalizadas
- Ampliable con servidores MCP
- Controlada mediante [permisos](permissions.md)

### Diferencia entre Herramientas Integradas y Personalizadas

| Característica | Integradas | Personalizadas |
|----------------|------------|----------------|
| Origen | OpenCode | Usuario |
| Configuración | Predefinida | Personalizada |
| Flexibilidad | Limitada | Completa |
| Mantenimiento | OpenCode | Usuario |

---

## 2. Configuración de Herramientas

### Habilitar/Deshabilitar

Usa `permission` para controlar el comportamiento:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "deny",
    "bash": "ask",
    "webfetch": "allow"
  }
}
```

### Comodines para Servidores MCP

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "mymcp_*": "ask"
  }
}
```

---

## 3. Herramientas Integradas

### 3.1 bash

Ejecuta comandos de shell en el entorno del proyecto.

```json
{ "permission": { "bash": "allow" } }
```

**Uso:**
- Ejecutar `npm install`
- Ejecutar `git status`
- Cualquier comando de terminal

### 3.2 edit

Modifica archivos existentes usando reemplazos de cadenas exactas.

```json
{ "permission": { "edit": "allow" } }
```

**Uso:**
- Cambiar código específico
- Actualizar configuraciones
- Corregir errores

### 3.3 write

Crea nuevos archivos o sobrescribe existentes.

```json
{ "permission": { "edit": "allow" } }
```

**Nota:** Controlada por permiso `edit` (cubre `edit`, `write`, `patch`).

### 3.4 read

Lee contenido de archivos. Soporta rangos de líneas específicos.

```json
{ "permission": { "read": "allow" } }
```

**Uso:**
- Leer archivos completos
- Leer secciones específicas
- Inspeccionar código

### 3.5 grep

Busca contenido usando expresiones regulares.

```json
{ "permission": { "grep": "allow" } }
```

**Características:**
- Usa ripgrep internamente
- Soporta sintaxis regex completa
- Filtrado por patrón de archivos

### 3.6 glob

Busca archivos por patrones.

```json
{ "permission": { "glob": "allow" } }
```

**Ejemplos de patrones:**
- `**/*.js` - Todos los archivos JS
- `src/**/*.ts` - Archivos TS en src
- `*.md` - Archivos Markdown en raíz

### 3.7 lsp (experimental)

Interactúa con servidores LSP para inteligencia de código.

```json
{ "permission": { "lsp": "allow" } }
```

**Requiere:** `OPENCODE_EXPERIMENTAL_LSP_TOOL=true` o `OPENCODE_EXPERIMENTAL=true`

**Operaciones soportadas:**
- `goToDefinition`
- `findReferences`
- `hover`
- `documentSymbol`
- `workspaceSymbol`
- `goToImplementation`
- `prepareCallHierarchy`
- `incomingCalls`
- `outgoingCalls`

### 3.8 patch

Aplica parches a archivos.

```json
{ "permission": { "edit": "allow" } }
```

**Nota:** Controlada por permiso `edit`.

### 3.9 skill

Carga una [skill](https://opencode.ai/docs/skills/) y devuelve su contenido.

```json
{ "permission": { "skill": "allow" } }
```

### 3.10 todowrite

Administra listas de tareas pendientes.

```json
{ "permission": { "todowrite": "allow" } }
```

**Nota:** Deshabilitada por defecto en subagentes.

### 3.11 webfetch

Obtiene contenido web de URLs.

```json
{ "permission": { "webfetch": "allow" } }
```

**Uso:**
- Buscar documentación
- Investigar recursos en línea
- Leer páginas web

### 3.12 websearch

Búsqueda web usando Exa AI.

```json
{ "permission": { "websearch": "allow" } }
```

**Requiere:** Proveedor OpenCode o `OPENCODE_ENABLE_EXA=true`

```bash
OPENCODE_ENABLE_EXA=1 opencode
```

**No requiere API key:** Se conecta directamente al servicio MCP de Exa AI.

### 3.13 question

Hace preguntas al usuario durante ejecución.

```json
{ "permission": { "question": "allow" } }
```

**Uso:**
- Recopilar preferencias del usuario
- Aclarar instrucciones ambiguas
- Tomar decisiones de implementación
- Ofrecer opciones

---

## 4. Herramientas Personalizadas

Las herramientas personalizadas permiten definir funciones que LLM puede llamar.

**Documentación completa:** [Herramientas Personalizadas](custom-tools.md)

---

## 5. Servidores MCP

Los servidores MCP (Model Context Protocol) permiten integrar herramientas y servicios externos.

**Documentación completa:** [Servidores MCP](https://opencode.ai/docs/mcp-servers/)

---

## 6. Ignorar Patrones

### Archivo `.ignore`

Crea un archivo `.ignore` en la raíz del proyecto para incluir archivos ignorados:

```
!node_modules/
!dist/
!build/
```

### Comportamiento por Defecto

- Usa ripgrep internamente
- Respeta `.gitignore`
- Archivos en `.gitignore` se excluyen de búsquedas

---

## 7. Buenas Prácticas

### 7.1 Configuración

- Usa `permission` para controlar herramientas
- Define permisos granulares cuando sea necesario
- Usa comodines para servidores MCP

### 7.2 Herramientas Integradas

- Conoce las herramientas disponibles
- Usa la herramienta adecuada para cada tarea
- Combina herramientas para flujos complejos

### 7.3 Seguridad

- Usa `deny` para herramientas peligrosas
- Usa `ask` para acciones irreversibles
- Define permisos por agente cuando sea necesario

### 7.4 Rendimiento

- Usa `glob` para buscar archivos
- Usa `grep` para buscar contenido
- Evita `bash` para operaciones simples

### 7.5 Personalizaciones

- Crea herramientas personalizadas para tareas repetitivas
- Usa servidores MCP para integraciones externas
- Documenta tus herramientas personalizadas

---

## Referencia Rápida

### Herramientas Principales

| Herramienta | Descripción | Permiso |
|-------------|-------------|---------|
| `bash` | Ejecutar comandos shell | `bash` |
| `edit` | Modificar archivos | `edit` |
| `write` | Crear archivos | `edit` |
| `read` | Leer archivos | `read` |
| `grep` | Buscar contenido | `grep` |
| `glob` | Buscar archivos | `glob` |
| `patch` | Aplicar parches | `edit` |

### Herramientas de Conocimiento

| Herramienta | Descripción | Permiso |
|-------------|-------------|---------|
| `lsp` | Consultas LSP | `lsp` |
| `skill` | Cargar skills | `skill` |

### Herramientas de Interacción

| Herramienta | Descripción | Permiso |
|-------------|-------------|---------|
| `webfetch` | Obtener URLs | `webfetch` |
| `websearch` | Buscar en web | `websearch` |
| `question` | Preguntar al usuario | `question` |
| `todowrite` | Gestionar tareas | `todowrite` |

### Herramientas de Seguridad

| Herramienta | Descripción | Permiso |
|-------------|-------------|---------|
| `external_directory` | Directorios externos | `external_directory` |
| `doom_loop` | Detección de bucles | `doom_loop` |

---

*Manual generado a partir de la documentación oficial de OpenCode.*
*Última actualización de la fuente: 31 de agosto de 2026.*
