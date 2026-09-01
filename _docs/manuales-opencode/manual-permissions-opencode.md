# Manual de Permisos OpenCode - Análisis Detallado

> **Fuente:** [https://opencode.ai/docs/es/permissions/](https://opencode.ai/docs/es/permissions/)
> **Fecha de análisis:** 31 de agosto de 2026
> **Propósito:** Guía de referencia para el control de permisos en OpenCode.

---

## Tabla de Contenidos

1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Acciones](#2-acciones)
3. [Configuración](#3-configuración)
4. [Reglas Granulares](#4-reglas-granulares)
5. [Comodines](#5-comodines)
6. [Expansión del Directorio Inicio](#6-expansión-del-directorio-inicio)
7. [Directorios Externos](#7-directorios-externos)
8. [Permisos Disponibles](#8-permisos-disponibles)
9. [Valores Predeterminados](#9-valores-predeterminados)
10. [¿Qué Significa "Preguntar"?](#10-qué-significa-preguntar)
11. [Permisos por Agente](#11-permisos-por-agente)
12. [Ejemplos Prácticos](#12-ejemplos-prácticos)
13. [Buenas Prácticas](#13-buenas-prácticas)

---

## 1. Conceptos Fundamentales

### ¿Qué es un permiso en OpenCode?

Un **permiso** controla si una acción determinada debe ejecutarse automáticamente, avisar o bloquearse.

**Características principales:**
- Se configura con `permission` en `opencode.json`
- Controla acciones de herramientas
- Soporta reglas granulares por patrón
- Se evalúa por orden (última regla coincide gana)

### Diferencia entre Permiso y Policy

| Característica | Permiso | Policy |
|----------------|---------|--------|
| Alcance | Acciones (herramientas) | Recursos (proveedores) |
| Configuración | `permission` | `experimental.policies` |
| Granularidad | Por herramienta/patrón | Por recurso |
| Ejemplo | Denegar ejecución de bash | Denegar proveedor OpenAI |

---

## 2. Acciones

Cada regla de permiso se resuelve en una de:

| Acción | Descripción |
|--------|-------------|
| `"allow"` | Ejecutar sin aprobación |
| `"ask"` | Solicitar aprobación |
| `"deny"` | Bloquear la acción |

---

## 3. Configuración

### Configuración Global

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "bash": "allow",
    "edit": "deny"
  }
}
```

### Todos los Permisos de Una Vez

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow"
}
```

### Configuración por Herramienta

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": "allow",
    "edit": "ask",
    "bash": {
      "*": "ask",
      "git *": "allow"
    }
  }
}
```

---

## 4. Reglas Granulares (Sintaxis de Objeto)

Para la mayoría de permisos, usa un objeto para aplicar diferentes acciones según la entrada:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "npm *": "allow",
      "rm *": "deny",
      "grep *": "allow"
    },
    "edit": {
      "*": "deny",
      "packages/web/src/content/docs/*.mdx": "allow"
    }
  }
}
```

### Orden de Evaluación

**Las reglas se evalúan por orden y la última coincidente gana.**

Patrón recomendado:
1. Primero la regla general `"*"`
2. Después reglas más específicas

---

## 5. Comodines

Los patrones de permisos utilizan coincidencia simple:

| Wildcard | Descripción | Ejemplo |
|----------|-------------|---------|
| `*` | Cero o más caracteres | `git *` coincide con `git status` |
| `?` | Exactamente un carácter | `git ?` coincide con `git a` |
| (literal) | Todos los demás caracteres | `git` coincide solo con `git` |

### Ejemplos

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "git status": "allow",
      "git commit *": "deny",
      "npm test": "allow"
    }
  }
}
```

---

## 6. Expansión del Directorio Inicio

Puedes usar `~` o `$HOME` al inicio de un patrón:

| Patrón | Expansión |
|--------|-----------|
| `~/projects/*` | `/Users/username/projects/*` |
| `$HOME/projects/*` | `/Users/username/projects/*` |
| `~` | `/Users/username` |

### Ejemplo

```json
{
  "permission": {
    "external_directory": {
      "~/projects/personal/**": "allow"
    }
  }
}
```

---

## 7. Directorios Externos

Usa `external_directory` para permitir acceso a rutas fuera del directorio de trabajo:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "external_directory": {
      "~/projects/personal/**": "allow"
    }
  }
}
```

### Restricciones Adicionales

Los directorios permitidos heredan los valores predeterminados. Para restringir herramientas específicas:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "external_directory": {
      "~/projects/personal/**": "allow"
    },
    "edit": {
      "~/projects/personal/**": "deny"
    }
  }
}
```

---

## 8. Permisos Disponibles

### Herramientas Principales

| Permiso | Descripción |
|---------|-------------|
| `read` | Leer archivos |
| `edit` | Todas las modificaciones de archivos (edit, write, patch) |
| `glob` | Búsqueda de archivos por patrón |
| `grep` | Búsqueda de contenido |
| `bash` | Ejecutar comandos shell |
| `task` | Lanzar subagentes |
| `skill` | Cargar una skill |
| `lsp` | Ejecución de consultas LSP |
| `webfetch` | Obtener URLs |
| `websearch` | Búsqueda web |
| `external_directory` | Acceso a directorios externos |
| `doom_loop` | Detección de bucles (misma llamada 3 veces) |

### Permisos con Patrones

| Permiso | Patrón |
|---------|--------|
| `read` | Ruta del archivo |
| `edit` | Ruta del archivo |
| `glob` | Patrón global |
| `grep` | Expresión regular |
| `bash` | Comando parseado |
| `webfetch` | URL |
| `websearch` | Consulta |
| `external_directory` | Ruta del sistema |
| `skill` | Nombre de la skill |

### Permisos sin Patrones

| Permiso | Descripción |
|---------|-------------|
| `todowrite` | Solo action (allow/ask/deny) |
| `question` | Solo action |
| `doom_loop` | Solo action |

---

## 9. Valores Predeterminados

Si no especificas nada, OpenCode usa valores predeterminados permisivos:

```json
{
  "permission": {
    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "*.env.example": "allow"
    },
    "edit": "allow",
    "glob": "allow",
    "grep": "allow",
    "bash": "allow",
    "task": "allow",
    "skill": "allow",
    "lsp": "allow",
    "webfetch": "allow",
    "websearch": "allow",
    "external_directory": "ask",
    "doom_loop": "ask"
  }
}
```

### Notas Importantes

- `read` es `"allow"` excepto archivos `.env`
- `doom_loop` y `external_directory` son `"ask"` por defecto
- La mayoría de herramientas son `"allow"` por defecto

---

## 10. ¿Qué Significa "Preguntar"?

Cuando OpenCode solicita aprobación, la interfaz ofrece tres resultados:

| Opción | Descripción |
|--------|-------------|
| `once` | Aprobar solo esta solicitud |
| `always` | Aprobar futuras solicitudes que coincidan con patrones sugeridos (para la sesión actual) |
| `reject` | Rechazar la solicitud |

### Patrones Sugeridos

La herramienta proporciona el conjunto de patrones que `always` aprobaría:
- Aprobaciones de bash generalmente incluyen prefijos de comandos seguros
- Permisos de archivo incluyen rutas específicas

---

## 11. Permisos por Agente

Los permisos del agente se combinan con la configuración global:

### Configuración en JSON

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "git commit *": "deny",
      "git push *": "deny",
      "grep *": "allow"
    }
  },
  "agent": {
    "build": {
      "permission": {
        "bash": {
          "*": "ask",
          "git *": "allow",
          "git commit *": "ask",
          "git push *": "deny",
          "grep *": "allow"
        }
      }
    }
  }
}
```

### Configuración en Markdown

~/.config/opencode/agents/review.md

```markdown
---
description: Code review sin ediciones
mode: subagent
permission:
  edit: deny
  bash: ask
  webfetch: deny
---

Solo analiza código y sugiere cambios.
```

---

## 12. Ejemplos Prácticos

### 12.1 Solo Lectura

```json
{
  "permission": {
    "edit": "deny",
    "bash": "deny",
    "read": "allow",
    "glob": "allow",
    "grep": "allow"
  }
}
```

### 12.2 Bash Restringido

```json
{
  "permission": {
    "bash": {
      "*": "deny",
      "git *": "allow",
      "npm test": "allow",
      "ls *": "allow"
    }
  }
}
```

### 12.3 Edición Restringida

```json
{
  "permission": {
    "edit": {
      "*": "deny",
      "src/**": "allow",
      "*.md": "allow"
    }
  }
}
```

### 12.4 Acceso a Directorios Externos

```json
{
  "permission": {
    "external_directory": {
      "~/projects/personal/**": "allow",
      "~/secrets/**": "deny"
    },
    "edit": {
      "~/projects/personal/**": "ask"
    }
  }
}
```

### 12.5 Permisos por Agente

```json
{
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny",
        "bash": "ask",
        "webfetch": "allow"
      }
    },
    "build": {
      "permission": {
        "edit": "allow",
        "bash": {
          "*": "ask",
          "git *": "allow"
        }
      }
    }
  }
}
```

---

## 13. Buenas Prácticas

### 13.1 Estructura

- Usa `permission` para control de acciones
- Usa objetos para reglas granulares
- Coloca reglas generales primero, específicas después

### 13.2 Comodines

- Usa `*` para comandos con argumentos
- Usa `?` para un solo carácter
- Recuerda: última regla coincide gana

### 13.3 Directorios

- Usa `external_directory` para rutas externas
- Combina con `edit` para restricciones adicionales
- Usa `~` o `$HOME` para el directorio inicio

### 13.4 Agentes

- Define permisos por agente para mayor control
- Los permisos del agente se combinan con los globales
- Usa Markdown para agentes simples

### 13.5 Testing

- Prueba permisos con diferentes patrones
- Verifica que `"ask"` muestra el diálogo correcto
- Valida que `"deny"` bloquea la acción

---

## Referencia Rápida

| Permiso | Patrón | Descripción |
|---------|--------|-------------|
| `read` | Ruta | Leer archivos |
| `edit` | Ruta | Modificar archivos |
| `glob` | Patrón | Buscar archivos |
| `grep` | Regex | Buscar contenido |
| `bash` | Comando | Ejecutar shell |
| `task` | Tipo | Lanzar subagentes |
| `skill` | Nombre | Cargar skill |
| `webfetch` | URL | Obtener web |
| `websearch` | Query | Buscar en web |
| `external_directory` | Ruta | Directorios externos |
| `doom_loop` | - | Detección de bucles |

| Acción | Descripción |
|--------|-------------|
| `allow` | Ejecutar sin preguntar |
| `ask` | Solicitar aprobación |
| `deny` | Bloquear acción |

| Wildcard | Descripción |
|----------|-------------|
| `*` | Cero o más caracteres |
| `?` | Exactamente un carácter |

---

*Manual generado a partir de la documentación oficial de OpenCode.*
*Última actualización de la fuente: 31 de agosto de 2026.*
