# Manual de Herramientas Personalizadas OpenCode - Análisis Detallado

> **Fuente:** [https://opencode.ai/docs/es/custom-tools/](https://opencode.ai/docs/es/custom-tools/)
> **Fecha de análisis:** 31 de agosto de 2026
> **Propósito:** Guía de referencia para la creación y uso de herramientas personalizadas en OpenCode.

---

## Tabla de Contenidos

1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Crear una Herramienta](#2-crear-una-herramienta)
3. [Múltiples Herramientas por Archivo](#3-múltiples-herramientas-por-archivo)
4. [Argumentos con Zod](#4-argumentos-con-zod)
5. [Contexto de la Herramienta](#5-contexto-de-la-herramienta)
6. [Ejemplos Prácticos](#6-ejemplos-prácticos)
7. [Colisiones de Nombres](#7-colisiones-de-nombres)
8. [Buenas Prácticas](#8-buenas-prácticas)

---

## 1. Conceptos Fundamentales

### ¿Qué es una herramienta personalizada?

Una **herramienta personalizada** es una función que usted crea y que el LLM puede llamar durante las conversaciones.

**Características principales:**
- Se define en TypeScript o JavaScript
- Puede ejecutar código arbitrario
- Trabaja junto con herramientas integradas
- Se invoca automáticamente por el LLM
- Recibe contexto de la sesión actual

### Diferencia entre Herramienta y Comando

| Característica | Herramienta | Comando |
|----------------|-------------|---------|
| Invocación | Automática por LLM | Manual por usuario |
| Complejidad | Función programática | Prompt simple |
| Estado | Sin estado | Sin estado |
| Retorno | Resultado directo | Modificación del contexto |
| Uso | Acciones específicas | Tareas rápidas |

---

## 2. Crear una Herramienta

### 2.1 Ubicación

Las herramientas se definen como archivos TypeScript o JavaScript en:

| Alcance | Ubicación |
|---------|-----------|
| Por proyecto | `.opencode/tools/` |
| Global | `~/.config/opencode/tools/` |

**El nombre del archivo se convierte en el nombre de la herramienta:**
- `database.ts` → herramienta `database`
- `query.ts` → herramienta `query`

### 2.2 Estructura Básica

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Consultar la base de datos del proyecto",
  args: {
    query: tool.schema.string().describe("Consulta SQL a ejecutar"),
  },
  async execute(args) {
    // Lógica de base de datos aquí
    return `Consulta ejecutada: ${args.query}`
  },
})
```

### 2.3 Sin Usa `tool()` (Zod Directo)

```typescript
import { z } from "zod"

export default {
  description: "Descripción de la herramienta",
  args: {
    param: z.string().describe("Descripción del parámetro"),
  },
  async execute(args, context) {
    return "resultado"
  },
}
```

---

## 3. Múltiples Herramientas por Archivo

Puede exportar varias herramientas desde un solo archivo:

```typescript
import { tool } from "@opencode-ai/plugin"

export const add = tool({
  description: "Sumar dos números",
  args: {
    a: tool.schema.number().describe("Primer número"),
    b: tool.schema.number().describe("Segundo número"),
  },
  async execute(args) {
    return args.a + args.b
  },
})

export const multiply = tool({
  description: "Multiplicar dos números",
  args: {
    a: tool.schema.number().describe("Primer número"),
    b: tool.schema.number().describe("Segundo número"),
  },
  async execute(args) {
    return args.a * args.b
  },
})
```

**Resultado:**
- Herramienta `math_add` (suponiendo que el archivo se llama `math.ts`)
- Herramienta `math_multiply`

---

## 4. Argumentos con Zod

### 4.1 Usando `tool.schema`

```typescript
args: {
  query: tool.schema.string().describe("Consulta SQL a ejecutar"),
  limit: tool.schema.number().describe("Límite de resultados"),
  active: tool.schema.boolean().describe("Solo activos"),
}
```

### 4.2 Usando Zod Directamente

```typescript
import { z } from "zod"

args: {
  query: z.string().describe("Consulta SQL a ejecutar"),
  limit: z.number().describe("Límite de resultados"),
  active: z.boolean().describe("Solo activos"),
}
```

### 4.3 Tipos Soportados

| Tipo | Ejemplo |
|------|---------|
| `string` | `tool.schema.string()` |
| `number` | `tool.schema.number()` |
| `boolean` | `tool.schema.boolean()` |
| `array` | `tool.schema.array(tool.schema.string())` |
| `object` | `tool.schema.object({ key: tool.schema.string() })` |

---

## 5. Contexto de la Herramienta

Las herramientas reciben contexto sobre la sesión actual:

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Obtener información del proyecto",
  args: {},
  async execute(args, context) {
    const { agent, sessionID, messageID, directory, worktree } = context
    return `Agente: ${agent}, Sesión: ${sessionID}, Directorio: ${directory}`
  },
})
```

### Propiedades del Contexto

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `agent` | string | Nombre del agente actual |
| `sessionID` | string | ID de la sesión actual |
| `messageID` | string | ID del mensaje actual |
| `directory` | string | Directorio de trabajo de la sesión |
| `worktree` | string | Raíz del árbol de trabajo de git |

---

## 6. Ejemplos Prácticos

### 6.1 Herramienta en Python

**Script Python (`.opencode/tools/add.py`):**

```python
import sys

a = int(sys.argv[1])
b = int(sys.argv[2])
print(a + b)
```

**Definición de herramienta (`.opencode/tools/python-add.ts`):**

```typescript
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Sumar dos números usando Python",
  args: {
    a: tool.schema.number().describe("Primer número"),
    b: tool.schema.number().describe("Segundo número"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, ".opencode/tools/add.py")
    const result = await Bun.$`python3 ${script} ${args.a} ${args.b}`.text()
    return result.trim()
  },
})
```

### 6.2 Consulta a Base de Datos

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Ejecutar consulta SQL",
  args: {
    query: tool.schema.string().describe("Consulta SQL"),
  },
  async execute(args) {
    // Conexión a base de datos
    const result = await db.query(args.query)
    return JSON.stringify(result)
  },
})
```

### 6.3 Validación de Archivo

```typescript
import { tool } from "@opencode-ai/plugin"
import fs from "fs"

export default tool({
  description: "Validar si un archivo existe",
  args: {
    path: tool.schema.string().describe("Ruta del archivo"),
  },
  async execute(args, context) {
    const fullPath = path.join(context.directory, args.path)
    const exists = fs.existsSync(fullPath)
    return exists ? `El archivo ${args.path} existe` : `El archivo ${args.path} no existe`
  },
})
```

### 6.4 Comando del Sistema

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Ejecutar comando del sistema",
  args: {
    command: tool.schema.string().describe("Comando a ejecutar"),
  },
  async execute(args) {
    const result = await Bun.$`${args.command}`.text()
    return result
  },
})
```

---

## 7. Colisiones de Nombres

Si una herramienta personalizada tiene el mismo nombre que una integrada, **la personalizada tiene prioridad**.

### Ejemplo: Anular `bash`

```typescript
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Bash restringido",
  args: {
    command: tool.schema.string(),
  },
  async execute(args) {
    return `Bloqueado: ${args.command}`
  },
})
```

**Recomendación:** Usa nombres únicos o usa [permisos](permissions.md) para deshabilitar herramientas integradas sin anularlas.

---

## 8. Buenas Prácticas

### 8.1 Nomenclatura

- Usa nombres descriptivos y cortos
- Evita colisiones con herramientas integradas
- Usa guiones para nombres compuestos: `my-tool.ts`, no `myTool.ts`

### 8.2 Argumentos

- Incluye `.describe()` en todos los argumentos
- Usa tipos específicos (string, number, boolean)
- Valida entradas antes de procesar

### 8.3 Ejecución

- Maneja errores gracefulmente
- Retorna resultados simples (strings, objetos JSON)
- Usa `context.directory` y `context.worktree` para rutas

### 8.4 Rendimiento

- Mantén las herramientas ligeras
- Evita operaciones de E/O bloqueantes
- Usa async/await para operaciones asíncronas

### 8.5 Documentación

- Describe claramente qué hace la herramienta
- Incluye ejemplos de uso en la descripción
- Documenta los argumentos esperados

---

## Referencia Rápida

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `description` | string | Qué hace la herramienta |
| `args` | object | Schema de argumentos (Zod) |
| `execute` | function | Función que ejecuta la herramienta |

| Contexto | Descripción |
|----------|-------------|
| `agent` | Nombre del agente actual |
| `sessionID` | ID de la sesión actual |
| `messageID` | ID del mensaje actual |
| `directory` | Directorio de trabajo |
| `worktree` | Raíz del árbol de trabajo git |

| Tipo | Descripción |
|------|-------------|
| `string` | Cadena de texto |
| `number` | Número |
| `boolean` | Verdadero/Falso |
| `array` | Lista de elementos |
| `object` | Objeto con propiedades |

---

*Manual generado a partir de la documentación oficial de OpenCode.*
*Última actualización de la fuente: 31 de agosto de 2026.*
