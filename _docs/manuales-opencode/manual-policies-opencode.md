# Manual de Policies OpenCode - Análisis Detallado

> **Fuente:** [https://opencode.ai/docs/es/policies/](https://opencode.ai/docs/es/policies/)
> **Fecha de análisis:** 31 de agosto de 2026
> **Propósito:** Guía de referencia para el control de recursos mediante policies en OpenCode.

---

## Tabla de Contenidos

1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Configuración](#2-configuración)
3. [Policies Disponibles](#3-policies-disponibles)
4. [Matching con Wildcards](#4-matching-con-wildcards)
5. [Orden de Reglas](#5-orden-de-reglas)
6. [Reemplazar Listas de Proveedores](#6-reemplazar-listas-de-proveedores)
7. [Policies Globales vs Proyecto](#7-policies-globales-vs-proyecto)
8. [Ejemplos Prácticos](#8-ejemplos-prácticos)
9. [Buenas Prácticas](#9-buenas-prácticas)

---

## 1. Conceptos Fundamentales

### ¿Qué es una policy en OpenCode?

Una **policy** es una regla que controla si OpenCode puede usar un recurso determinado (como un proveedor LLM).

**Características principales:**
- Se configura con `experimental.policies` en `opencode.json`
- Permite o denegar uso de recursos
- Soporta wildcards para patrones
- Se evalúa por orden (última regla coincide gana)

### Diferencia entre Policy y Permiso

| Característica | Policy | Permiso |
|----------------|--------|---------|
| Alcance | Recursos (proveedores) | Acciones (herramientas) |
| Configuración | `experimental.policies` | `permission` |
| Granularidad | Por recurso | Por herramienta |
| Ejemplo | Denegar proveedor OpenAI | Denegar ejecución de bash |

---

## 2. Configuración

### Estructura de un Statement

Cada policy tiene tres campos:

```json
{
  "effect": "allow" | "deny",
  "action": "provider.use",
  "resource": "nombre-del-recurso"
}
```

### Ejemplo Básico

```json
{
  "$schema": "https://opencode.ai/config.json",
  "experimental": {
    "policies": [
      {
        "effect": "deny",
        "action": "provider.use",
        "resource": "openai"
      }
    ]
  }
}
```

### Estructura Completa

```json
{
  "$schema": "https://opencode.ai/config.json",
  "experimental": {
    "policies": [
      {
        "effect": "deny",
        "action": "provider.use",
        "resource": "openai"
      },
      {
        "effect": "allow",
        "action": "provider.use",
        "resource": "anthropic"
      }
    ]
  }
}
```

---

## 3. Policies Disponibles

### Acciones Soportadas

| Acción | Recurso | Descripción |
|--------|---------|-------------|
| `provider.use` | ID del proveedor (ej: `openai`) | Permitir o denegar uso de un proveedor LLM |

### Notas Importantes

- Un proveedor denegado **no está disponible** para selección de modelos
- Un proveedor denegado **no puede ser usado** aunque tenga credenciales
- Solo hay una acción disponible actualmente: `provider.use`

---

## 4. Matching con Wildcards

El campo `resource` soporta coincidencia de patrones:

| Wildcard | Descripción | Ejemplo |
|----------|-------------|---------|
| `*` | Cero o más caracteres | `company-*` coincide con `company-us` |
| `?` | Exactamente un carácter | `compan?` coincide con `company` |

### Ejemplo con Wildcards

```json
{
  "experimental": {
    "policies": [
      {
        "effect": "deny",
        "action": "provider.use",
        "resource": "company-*"
      }
    ]
  }
}
```

Esto denegaría:
- `company-us`
- `company-eu`
- `company-apac`

Pero permitiría:
- `anthropic`
- `openai`

---

## 5. Orden de Reglas

Cuando múltiples statements coinciden con el mismo recurso, **el último coincide gana**.

### Patrón Recomendado

1. Pon reglas amplias primero
2. Pon excepciones más específicas después

### Ejemplo: Solo Permitir Anthropic

```json
{
  "experimental": {
    "policies": [
      {
        "effect": "deny",
        "action": "provider.use",
        "resource": "*"
      },
      {
        "effect": "allow",
        "action": "provider.use",
        "resource": "anthropic"
      }
    ]
  }
}
```

**Evaluación:**
1. `*` coincide con todo → deny
2. `anthropic` coincide con anthropic → allow
3. Resultado final: solo anthropic permitido

### Comportamiento por Defecto

Si **no hay policy** que coincida con un proveedor, se **permite por defecto**.

---

## 6. Reemplazar Listas de Proveedores

### Reemplazar `disabled_providers`

Para denegar proveedores específicos:

```json
{
  "experimental": {
    "policies": [
      { "effect": "deny", "action": "provider.use", "resource": "openai" },
      { "effect": "deny", "action": "provider.use", "resource": "google" }
    ]
  }
}
```

### Reemplazar `enabled_providers`

Para permitir solo proveedores específicos:

```json
{
  "experimental": {
    "policies": [
      { "effect": "deny", "action": "provider.use", "resource": "*" },
      { "effect": "allow", "action": "provider.use", "resource": "anthropic" },
      { "effect": "allow", "action": "provider.use", "resource": "openai" }
    ]
  }
}
```

---

## 7. Policies Globales vs Proyecto

Las policies pueden configurarse en dos niveles:

| Nivel | Ubicación |
|-------|-----------|
| Global | `~/.config/opencode/opencode.json` |
| Proyecto | `opencode.json` o `.opencode/opencode.json` |

### Prioridad

Si policies de ambos niveles coinciden con el mismo proveedor, **la policy global tiene prioridad**.

Esto evita que un repositorio reactive un proveedor que denegaste globalmente.

### Ejemplo

**Global (`.config/opencode/opencode.json`):**
```json
{
  "experimental": {
    "policies": [
      { "effect": "deny", "action": "provider.use", "resource": "openai" }
    ]
  }
}
```

**Proyecto (`opencode.json`):**
```json
{
  "experimental": {
    "policies": [
      { "effect": "allow", "action": "provider.use", "resource": "openai" }
    ]
  }
}
```

**Resultado:** OpenAI sigue denegado (la global gana).

---

## 8. Ejemplos Prácticos

### 8.1 Denegar Proveedor Específico

```json
{
  "experimental": {
    "policies": [
      {
        "effect": "deny",
        "action": "provider.use",
        "resource": "openai"
      }
    ]
  }
}
```

### 8.2 Solo Permitir Proveedores Corporativos

```json
{
  "experimental": {
    "policies": [
      { "effect": "deny", "action": "provider.use", "resource": "*" },
      { "effect": "allow", "action": "provider.use", "resource": "company-*" }
    ]
  }
}
```

### 8.3 Denegar Proveedores No Autenticados

```json
{
  "experimental": {
    "policies": [
      { "effect": "deny", "action": "provider.use", "resource": "free-*" }
    ]
  }
}
```

### 8.4 Permitir Solo Anthropic y OpenAI

```json
{
  "experimental": {
    "policies": [
      { "effect": "deny", "action": "provider.use", "resource": "*" },
      { "effect": "allow", "action": "provider.use", "resource": "anthropic" },
      { "effect": "allow", "action": "provider.use", "resource": "openai" }
    ]
  }
}
```

---

## 9. Buenas Prácticas

### 9.1 Estructura

- Usa `experimental.policies` (aún es experimental)
- Define cada policy con effect, action y resource
- Usa wildcards para patrones de proveedores

### 9.2 Orden

- Pon reglas deny amplias primero
- Pon reglas allow específicas después
- Recuerda: última regla coincide gana

### 9.3 Ambitos

- Define policies globales en `~/.config/opencode/opencode.json`
- Define policies de proyecto en `opencode.json`
- La global siempre tiene prioridad

### 9.4 Compatibilidad

- Reemplaza `disabled_providers` con policies deny
- Reemplaza `enabled_providers` con deny + allow
- Las policies son más flexibles y granulares

### 9.5 Testing

- Verifica que los proveedores denegados no aparezcan en selección
- Prueba que las credenciales no permiten usar proveedores denegados
- Valida que la prioridad global funciona correctamente

---

## Referencia Rápida

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `effect` | string | `"allow"` o `"deny"` |
| `action` | string | `"provider.use"` |
| `resource` | string | ID del proveedor o patrón wildcard |

| Wildcard | Descripción |
|----------|-------------|
| `*` | Cero o más caracteres |
| `?` | Exactamente un carácter |

| Comportamiento | Descripción |
|----------------|-------------|
| Sin match | Se permite por defecto |
| Múltiples matches | Última regla gana |
| Global vs Proyecto | Global tiene prioridad |

---

*Manual generado a partir de la documentación oficial de OpenCode.*
*Última actualización de la fuente: 31 de agosto de 2026.*
