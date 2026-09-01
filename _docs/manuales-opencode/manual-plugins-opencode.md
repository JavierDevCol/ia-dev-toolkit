# Manual de Plugins OpenCode - Análisis Detallado

> **Fuente:** [https://opencode.ai/docs/plugins/](https://opencode.ai/docs/plugins/)
> **Fecha de análisis:** 31 de agosto de 2026
> **Propósito:** Guía de referencia para la creación y uso de plugins en OpenCode.

---

## Tabla de Contenidos

1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Usar un Plugin](#2-usar-un-plugin)
3. [Crear un Plugin](#3-crear-un-plugin)
4. [Eventos Disponibles](#4-eventos-disponibles)
5. [Ejemplos Prácticos](#5-ejemplos-prácticos)
6. [Buenas Prácticas](#6-buenas-prácticas)

---

## 1. Conceptos Fundamentales

### ¿Qué es un plugin en OpenCode?

Un **plugin** es un módulo JavaScript/TypeScript que extiende OpenCode conectándose a eventos y personalizando el comportamiento.

**Características principales:**
- Se ejecuta al iniciar OpenCode
- Puede escuchar eventos del sistema
- Puede modificar herramientas existentes
- Puede crear herramientas nuevas
- Puede inyectar variables de entorno

### Diferencia entre Plugin y Herramienta

| Característica | Plugin | Herramienta |
|----------------|--------|-------------|
| Alcance | Global/Proyecto | Por sesión |
| Estado | Persiste entre sesiones | Se reinicia |
| Complejidad | Múltiples hooks | Una función |
| Eventos | Puede escuchar todos | Solo se invoca |
| Uso | Integración continua | Acción específica |

---

## 2. Usar un Plugin

### 2.1 Desde Archivos Locales

Coloca archivos JavaScript o TypeScript en:

| Alcance | Ubicación |
|---------|-----------|
| Por proyecto | `.opencode/plugins/` |
| Global | `~/.config/opencode/plugins/` |

Los archivos se cargan automáticamente al iniciar.

### 2.2 Desde npm

Especifica paquetes npm en la configuración:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": [
    "opencode-helicone-session",
    "opencode-wakatime",
    "@my-org/custom-plugin"
  ]
}
```

Los plugins npm se instalan automáticamente usando Bun.

### 2.3 Orden de Carga

Los plugins se cargan en este orden:
1. Config global (`~/.config/opencode/opencode.json`)
2. Config de proyecto (`opencode.json`)
3. Directorio de plugins global (`~/.config/opencode/plugins/`)
4. Directorio de plugins de proyecto (`.opencode/plugins/`)

Los paquetes npm duplicados (mismo nombre y versión) se cargan una sola vez.

---

## 3. Crear un Plugin

### 3.1 Estructura Básica

```javascript
export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  console.log("Plugin inicializado!")
  
  return {
    // Implementación de hooks aquí
  }
}
```

### 3.2 Dependencias

Para usar paquetes npm externos, crea un `package.json` en `.opencode/`:

```json
{
  "dependencies": {
    "shescape": "^2.1.0"
  }
}
```

Ejemplo con dependencia:

```javascript
import { escape } from "shescape"

export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        output.args.command = escape(output.args.command)
      }
    },
  }
}
```

### 3.3 Soporte TypeScript

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // Implementación tipada
  }
}
```

### 3.4 Propiedades del Contexto

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `project` | object | Información del proyecto actual |
| `client` | object | Cliente SDK de OpenCode |
| `$` | function | API de shell de Bun |
| `directory` | string | Directorio de trabajo actual |
| `worktree` | string | Ruta del árbol de trabajo de git |

---

## 4. Eventos Disponibles

### 4.1 Eventos de Comandos
- `command.executed`

### 4.2 Eventos de Archivos
- `file.edited`
- `file.watcher.updated`

### 4.3 Eventos de Instalación
- `installation.updated`

### 4.4 Eventos LSP
- `lsp.client.diagnostics`
- `lsp.updated`

### 4.5 Eventos de Mensajes
- `message.part.removed`
- `message.part.updated`
- `message.removed`
- `message.updated`

### 4.6 Eventos de Permisos
- `permission.asked`
- `permission.replied`

### 4.7 Eventos de Servidor
- `server.connected`

### 4.8 Eventos de Sesión
- `session.created`
- `session.compacted`
- `session.deleted`
- `session.diff`
- `session.error`
- `session.idle`
- `session.status`
- `session.updated`

### 4.9 Eventos de Todo
- `todo.updated`

### 4.10 Eventos de Shell
- `shell.env`

### 4.11 Eventos de Herramientas
- `tool.execute.after`
- `tool.execute.before`

### 4.12 Eventos TUI
- `tui.prompt.append`
- `tui.command.execute`
- `tui.toast.show`

---

## 5. Ejemplos Prácticos

### 5.1 Notificaciones

```javascript
export const NotificationPlugin = async ({ $ }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        await $`osascript -e 'display notification "Sesión completada!" with title "opencode"'`
      }
    },
  }
}
```

### 5.2 Protección de .env

```javascript
export const EnvProtection = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("No leer archivos .env")
      }
    },
  }
}
```

### 5.3 Variables de Entorno

```javascript
export const InjectEnvPlugin = async () => {
  return {
    "shell.env": async (input, output) => {
      output.env.MY_API_KEY = "secret"
      output.env.PROJECT_ROOT = input.cwd
    },
  }
}
```

### 5.4 Herramientas Personalizadas

```javascript
import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "Herramienta personalizada",
        args: {
          foo: tool.schema.string(),
        },
        async execute(args, context) {
          const { directory, worktree } = context
          return `Hola ${args.foo} desde ${directory}`
        },
      }),
    },
  }
}
```

### 5.5 Logging Estructurado

```typescript
export const MyPlugin = async ({ client }) => {
  await client.app.log({
    body: {
      service: "my-plugin",
      level: "info",
      message: "Plugin inicializado",
      extra: { foo: "bar" },
    },
  })
}
```

Niveles: `debug`, `info`, `warn`, `error`.

### 5.6 Compaction Hooks

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const CompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      output.context.push(`## Contexto personalizado
Incluir estado que debe persistir:
- Estado actual de la tarea
- Decisiones importantes
- Archivos en uso`)
    },
  }
}
```

### 5.7 Reemplazar Prompt de Compaction

```typescript
export const CustomCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      output.prompt = `Genera un prompt de continuación para sesión multi-agente.
Resume:
1. Tarea actual y estado
2. Archivos modificados
3. Bloqueos o dependencias
4. Siguientes pasos

Formato estructurado para que otro agente pueda continuar.`
    },
  }
}
```

---

## 6. Buenas Prácticas

### 6.1 Estructura del Plugin

- Un plugin por archivo
- Nombres descriptivos
- Exporta una función async que retorna hooks

### 6.2 Hooks

- Mutate `output` in place
- Retorna `void` (no objetos)
- Usa tipos TypeScript para seguridad

### 6.3 Dependencias

- Usa `package.json` para dependencias npm
- Evita dependencias innecesarias
- Usa la API de shell de Bun (`$`) para comandos del sistema

### 6.4 Eventos

- Escucha solo los eventos necesarios
- Filtra por tipo de evento en el handler
- Maneja errores gracefulmente

### 6.5 Logging

- Usa `client.app.log()` en lugar de `console.log`
- Incluye contexto relevante
- Usa niveles apropiados

---

## Referencia Rápida

| Hook | Descripción |
|------|-------------|
| `event` | Cada evento del bus |
| `config` | Una vez al inicio con config mergeada |
| `chat.message` | Mensajes de chat |
| `tool.execute.before` | Antes de ejecutar herramienta |
| `tool.execute.after` | Después de ejecutar herramienta |
| `tool.definition` | Definición de herramienta |
| `shell.env` | Variables de entorno del shell |
| `permission.ask` | Cuando se solicita permiso |

| Contexto | Descripción |
|----------|-------------|
| `project` | Información del proyecto |
| `directory` | Directorio de trabajo |
| `worktree` | Ruta del árbol de trabajo git |
| `client` | Cliente SDK de OpenCode |
| `$` | API de shell de Bun |

---

*Manual generado a partir de la documentación oficial de OpenCode.*
*Última actualización de la fuente: 31 de agosto de 2026.*
