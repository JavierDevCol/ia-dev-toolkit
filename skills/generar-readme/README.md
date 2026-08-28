# Generar README Skill

Genera READMEs profesionales y completos validando la estructura del proyecto.

## Instalación

La skill ya está instalada en `.opencode/skills/generar-readme/`.

## Uso

La skill se activa cuando el usuario pide:
- "genera un README"
- "crea un README"
- "mejora el README"
- "necesito documentar mi proyecto"

## Protocolo

1. **Validar proyecto** - Verificar archivos y estructura
2. **Auto-detectar secciones** - Buscar tests, CI/CD, contribución
3. **Recopilar información** - Preguntar información faltante
4. **Generar README** - Incluir secciones obligatorias + auto-detectadas
5. **Validar README** - Verificar completitud y validez

## Secciones Obligatorias

| Sección | Descripción |
|---------|-------------|
| Título | Nombre del proyecto |
| Descripción | Qué hace, por qué, cómo |
| Instalación | Cómo instalar y ejecutar |
| Uso | Cómo usar el proyecto |
| Créditos | Colaboradores y referencias |
| Licencia | Qué pueden hacer con el código |

## Secciones Auto-detectadas

| Sección | Cuándo incluir | Cómo detectar |
|---------|----------------|---------------|
| Badges | Siempre | Auto-generar badges de licencia, versión, build |
| Pruebas/Tests | Si tiene tests | Detectar: tests/, __tests__/, *_test.*, *_spec.* |
| Contribución | Si es público | Detectar: CONTRIBUTING.md, repositorio público |
| CI/CD | Si tiene pipelines | Detectar: .github/workflows/, .gitlab-ci.yml |

## Referencia rápida

| Acción | Comando |
|--------|---------|
| Validar proyecto | Verificar archivos y estructura |
| Auto-detectar secciones | Buscar tests/, .github/workflows/, CONTRIBUTING.md |
| Recopilar info | Preguntar información faltante |
| Generar README | Incluir obligatorias + auto-detectadas |
| Validar README | Verificar completitud y validez |
