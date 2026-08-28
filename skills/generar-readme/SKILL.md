---
name: generar-readme
description: Use when user requests to generate, create, or improve a README.md file for a project. Validates project structure, enforces mandatory sections, and ensures professional documentation standards.
---

# Generar README

## Overview

Genera READMEs profesionales y completos validando la estructura del proyecto y siguiendo mejores prácticas. Nunca genera un README sin antes validar que el proyecto tenga la información necesaria.

## When to Use

- Usuario pide "genera un README", "crea un README", "mejora el README"
- Usuario necesita documentar un proyecto
- Usuario quiere un README profesional o completo
- Proyecto no tiene README o tiene uno incompleto

## When NOT to Use

- Usuario solo pregunta sobre READMEs (consulta teórica)
- Usuario ya tiene un README completo y funcional
- Proyecto es un script simple de una línea

## Protocolo de Generación

### Paso 1: Validar Proyecto (OBLIGATORIO)

**ANTES** de generar el README, validar la estructura del proyecto:

1. **Verificar archivos del proyecto:**
   - `package.json`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod` (dependencias)
   - `LICENSE` (licencia)
   - `tests/`, `__tests__/`, `*_test.*`, `*_spec.*`, `test_*.py` (pruebas)
   - `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` (CI/CD)
   - `CONTRIBUTING.md` (contribución)
   - `.eslintrc`, `.prettierrc`, `pyproject.toml` (herramientas de calidad)

2. **Identificar tecnologías:**
   - Lenguaje principal
   - Frameworks y librerías
   - Herramientas de desarrollo

3. **Detectar información faltante:**
   - ¿Tiene licencia?
   - ¿Tiene tests?
   - ¿Tiene instrucciones de instalación?
   - ¿Tiene documentación?

4. **Auto-detectar secciones a incluir:**
   - **Tests:** Si existe `tests/`, `__tests__/`, `*_test.*`, `*_spec.*`, `test_*.py` → INCLUIR sección de Pruebas
   - **Badges:** Si existe `.github/workflows/`, `.gitlab-ci.yml`, `package.json` con versión → INCLUIR sección de Badges
   - **Contribución:** Si existe `CONTRIBUTING.md` o es repositorio público → INCLUIR sección de Contribución
   - **CI/CD:** Si existe `.github/workflows/`, `.gitlab-ci.yml` → INCLUIR badges de build status

### Paso 2: Recopilar Información (OBLIGATORIO)

**SIEMPRE** preguntar información faltante antes de generar:

**Formato de preguntas:**
> **📋 Información requerida para el README:**
> - **Nombre del proyecto:** [detectar del package.json o preguntar]
> - **Descripción:** [qué hace, por qué es útil]
> - **Instalación:** [cómo instalar dependencias]
> - **Uso:** [cómo ejecutar y usar]
> - **Licencia:** [tipo de licencia]
> - **Créditos:** [autores, colaboradores]
>
> **🤷 ¿Puedes proporcionar la información faltante?**
> - ✅ [P] **Proporcionar información**
> - ✅ [G] **Generar con información disponible** (puede ser incompleto)

### Paso 3: Generar README (OBLIGATORIO)

**Incluir TODAS las secciones obligatorias + auto-detectadas:**

```markdown
# Nombre del Proyecto

<!-- BADGES (auto-incluir si se detecta CI/CD o package.json) -->
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)
[![Versión](https://img.shields.io/badge/versión-1.0.0-blue.svg)]()
[![Build Status](https://img.shields.io/github/actions/workflow/status/usuario/repo/ci.yml?branch=main)](https://github.com/usuario/repo/actions)
[![Cobertura](https://img.shields.io/badge/cobertura-80%25-green.svg)]()

## Descripción

[Qué hace el proyecto, por qué es útil, qué problema resuelve]

## Tabla de Contenidos

- [Instalación](#instalación)
- [Uso](#uso)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Pruebas](#pruebas)
- [Contribución](#contribución)
- [Créditos](#créditos)
- [Licencia](#licencia)

## Instalación

### Prerrequisitos

- [Requisito 1]
- [Requisito 2]

### Pasos

1. Clonar el repositorio
   ```bash
   git clone [url-del-repositorio]
   ```

2. Instalar dependencias
   ```bash
   [comando-de-instalación]
   ```

3. Configurar variables de entorno
   ```bash
   cp .env.example .env
   ```

## Uso

[Ejemplos de uso con código y capturas de pantalla]

```bash
[comando-de-ejemplo]
```

## Características

- [Característica 1]
- [Característica 2]
- [Característica 3]

## Tecnologías

- [Tecnología 1] - [Versión]
- [Tecnología 2] - [Versión]
- [Tecnología 3] - [Versión]

## Estructura del Proyecto

```
├── src/
│   ├── [archivo-1]
│   └── [archivo-2]
├── tests/
├── docs/
├── [archivo-config]
└── README.md
```

## Pruebas

<!-- INCLUIR SI: se detecta tests/, __tests__/, *_test.*, *_spec.*, test_*.py -->

### Ejecutar pruebas

```bash
# Pruebas unitarias
[comando-de-pruebas]

# Pruebas con cobertura
[comando-de-cobertura]
```

### Pruebas específicas

```bash
# Ejecutar pruebas de integración
[comando-de-integración]

# Ejecutar pruebas e2e
[comando-de-e2e]
```

## Contribución

<!-- INCLUIR SI: se detecta CONTRIBUTING.md o es repositorio público -->

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit (`git commit -m 'Add nueva funcionalidad'`)
4. Push (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## Créditos

- [Autor 1](https://github.com/autor1)
- [Autor 2](https://github.com/autor2)

## Licencia

Distribuído bajo la licencia [Tipo]. Ver `LICENSE` para más información.
```

### Paso 4: Validar README (OBLIGATORIO)

**Después** de generar, validar:

1. **Completitud:** ¿Todas las secciones obligatorias están presentes?
2. **Auto-detección:** ¿Se incluyeron Badges y Tests si el proyecto los tiene?
3. **Validez:** ¿Los comandos son ejecutables?
4. **Claridad:** ¿Las instrucciones son comprensibles?
5. **Enlaces:** ¿Los enlaces son válidos?
6. **Badges:** ¿Los badges son funcionales?

**Formato de validación:**
> **✅ README generado y validado:**
> - Secciones obligatorias: [X/6]
> - Secciones auto-detectadas: [Badges: Sí/No, Tests: Sí/No, Contribución: Sí/No]
> - Instrucciones ejecutables: [Sí/No]
> - Enlaces válidos: [Sí/No]
> - Badges funcionales: [Sí/No]

## Secciones Obligatorias

| Sección | Descripción | Validación |
|---------|-------------|------------|
| **Título** | Nombre del proyecto | Detectar de package.json o preguntar |
| **Descripción** | Qué hace, por qué, cómo | Preguntar si no está claro |
| **Instalación** | Cómo instalar y ejecutar | Verificar comandos reales |
| **Uso** | Cómo usar el proyecto | Incluir ejemplos y capturas |
| **Créditos** | Colaboradores y referencias | Detectar de git log o preguntar |
| **Licencia** | Qué pueden hacer con el código | Verificar archivo LICENSE |

## Secciones Auto-detectadas (INCLUIR si el proyecto las tiene)

| Sección | Cuándo incluir | Cómo detectar |
|---------|----------------|---------------|
| **Badges** | Siempre | Auto-generar badges de: licencia, versión, build status, cobertura |
| **Pruebas/Tests** | Si tiene tests | Detectar: `tests/`, `__tests__/`, `*_test.*`, `*_spec.*`, `test_*.py` |
| **Contribución** | Si es público o tiene CONTRIBUTING.md | Detectar: `CONTRIBUTING.md`, repositorio público |
| **CI/CD** | Si tiene pipelines | Detectar: `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` |
| **Tabla de Contenidos** | README > 100 líneas | Contar líneas del README generado |
| **Estructura del Proyecto** | Proyectos complejos | Detectar: múltiples directorios, monorepo |
| **Tecnologías** | Siempre | Detectar de: package.json, requirements.txt, Cargo.toml, go.mod |

## Anti-Patterns (Racionalizaciones a Rechazar)

| Racionalización | Realidad |
|-----------------|----------|
| "Generé un README básico" | Exigir completitud, no básico |
| "No me diste información" | Preguntar antes de generar |
| "Incluí las secciones estándar" | Verificar que sean necesarias |
| "Incluí todas las secciones que pude" | Seguir estructura obligatoria |
| "Generé el README como pediste" | Validar calidad después |
| "El usuario pidió rápido" | Rápido no significa incorrecto |
| "Él lo ajustará después" | Generar listo para usar |
| "Es mejor entregar algo" | No entregar incompleto |
| "No importa si no es perfecto" | Información errónea es peor que no tener README |
| "No tengo tiempo de dar información" | Usar placeholders [COMPLETAR], no inventar |
| "El proyecto es muy complejo" | Complejidad requiere más documentación |
| "Solo pediste mejorarlo" | Verificar qué hace realmente el proyecto |

## Red Flags - STOP y Validar

- Usuario pide README sin dar contexto → Preguntar información
- Proyecto no tiene licencia → Preguntar tipo de licencia
- Proyecto no tiene tests → Sugerir agregar sección de tests
- README generado es genérico → Validar que refleje el proyecto real
- Instrucciones no son ejecutables → Verificar comandos reales
- Usuario pide "rápido" → Rápido no significa incorrecto
- Usuario no tiene tiempo → Usar placeholders [COMPLETAR]
- Proyecto es complejo → Documentar cada componente
- README existente incompleto → Verificar qué hace realmente

**Todos estos significan: Validar antes de generar, no después.**

## Manejo de Escenarios Complejos

### README Rápido

**Problema:** Usuario pide README rápido, "no importa si no es perfecto".

**Protocolo:**
1. Validar que al menos las secciones críticas sean precisas
2. Incluir: título, descripción, instalación, uso básico
3. No omitir validación por velocidad
4. Rápido ≠ incorrecto

### README Sin Información

**Problema:** Usuario no tiene tiempo de dar información.

**Protocolo:**
1. Nunca inventar información
2. Usar placeholders claros: `[COMPLETAR]`, `[AGREGAR]`, `[PENDIENTE]`
3. Generar estructura completa con espacios para completar
4. Preguntar qué información puede proporcionar

### README para Proyecto Complejo

**Problema:** Proyecto con microservicios, Docker, CI/CD, múltiples lenguajes.

**Protocolo:**
1. Documentar cada componente por separado
2. Incluir sección de arquitectura
3. Documentar Docker y CI/CD
4. Estructura de microservicios
5. Requisitos por lenguaje

### README Existente Incompleto

**Problema:** README actual solo tiene título y descripción.

**Protocolo:**
1. Leer el código del proyecto para entender qué hace
2. No agregar secciones genéricas
3. Completar secciones existentes con información real
4. Agregar secciones faltantes basadas en el código

## Ejemplo de Flujo

```
Usuario: "Genera un README para mi proyecto Python."

Agente:
1. Valida estructura del proyecto:
   - Detecta: requirements.txt, tests/, LICENSE (MIT)
   - Detecta: .github/workflows/ci.yml (CI/CD)
   - Identifica: Python 3.11, Flask, pytest

2. Auto-detecta secciones:
   - ✅ Tests: detectado tests/ y pytest
   - ✅ Badges: detectado .github/workflows/
   - ✅ Contribución: repositorio público

3. Pregunta información faltante:
   "📋 Información requerida para el README:
   - Nombre del proyecto: [detectado: mi-app-flask]
   - Descripción: ¿Qué hace tu aplicación?
   - Uso: ¿Cómo se usa?
   - Créditos: ¿Quiénes son los autores?"

4. Genera README completo con:
   - Secciones obligatorias (6/6)
   - Badges auto-generados (licencia, versión, build status)
   - Sección de Pruebas con comandos de pytest
   - Sección de Contribución

5. Valida:
   "✅ README generado y validado:
   - Secciones obligatorias: 6/6
   - Secciones auto-detectadas: Badges: Sí, Tests: Sí, Contribución: Sí
   - Instrucciones ejecutables: Sí
   - Enlaces válidos: Sí"
```

## Quick Reference

| Acción | Comando |
|--------|---------|
| Validar proyecto | Verificar archivos y estructura |
| Auto-detectar secciones | Buscar tests/, .github/workflows/, CONTRIBUTING.md |
| Recopilar info | Preguntar información faltante |
| Generar README | Incluir obligatorias + auto-detectadas |
| Validar README | Verificar completitud y validez |
| Mejorar README | Agregar secciones adicionales |

## Common Mistakes

1. **Generar sin validar** → Siempre validar proyecto primero
2. **No preguntar información** → Preguntar antes de generar
3. **Secciones incompletas** → Incluir TODAS las obligatorias
4. **No auto-detectar Badges/Tests** → Buscar tests/, .github/workflows/, CONTRIBUTING.md
5. **Instrucciones genéricas** → Usar comandos reales del proyecto
6. **No validar después** → Verificar calidad del README generado
