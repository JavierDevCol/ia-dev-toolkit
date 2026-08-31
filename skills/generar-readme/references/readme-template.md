# README Template & Flow Example

## Full Template

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

## Ejemplo de Flujo

```
Usuario: "Genera un README para mi proyecto Python."

Agente:
1. Valida estructura del proyecto:
   - Detecta: requirements.txt, tests/, LICENSE (MIT)
   - Detecta: .github/workflows/ci.yml (CI/CD)
   - Identifica: Python 3.11, Flask, pytest

2. Auto-detecta secciones:
   - Tests: detectado tests/ y pytest
   - Badges: detectado .github/workflows/
   - Contribución: repositorio público

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
