---
name: bmm-manual-tecnico
description: >
  Usa esta skill cuando el usuario pida crear o generar un manual técnico
  y funcional de instalación para un microservicio del ecosistema
  BancaPorWhatsapp, entregando un documento Word (.docx) con la plantilla
  corporativa.
ready: true
---

# Generación de Manual Técnico y Funcional

## Overview
Genera un documento Word (.docx) con el Manual Técnico y Funcional completo de un microservicio, incluyendo requerimiento, solución, arquitectura, CI/CD, Vault, parametrización por ambiente, descripción funcional, modelo lógico, PT-007 y pruebas.

## When to Use
- El usuario pide crear, generar o documentar un manual técnico/funcional de instalación.
- Se necesita documentar un microservicio para el proceso de control de paso a producción.
- Se solicita la plantilla corporativa BMM en formato .docx.

**Cuándo NO usar:**
- Solo se necesita documentar un cambio puntual sin el alcance completo del manual.
- El microservicio no es parte del ecosistema BancaPorWhatsapp/BMM.

## Implementation
1. **Recopilar datos (obligatorio):** Solicita: `MICROSERVICIO` (nombre), `HU_NUMERO`, `HU_TITULO`, `PULL_REQUESTS` (separados por coma), `DESARROLLADOR`. Opcionales: `NUMERO_REQ`, `NUMERO_PASO`, `VAULT_FILE` (ruta a secrets de Vault), `NOTAS_EXTRA`.
2. **Recopilación automática:** Ejecuta en paralelo: exploración del microservicio (build.gradle, application.yml, Dockerfile, deployment.yaml, pipeline, migraciones, clases principales), git log/diff, lectura de Vault y plantilla de referencia.
3. **Construir contexto:** Consolida variables: HU, PRs, tecnología, Vault secrets, tablas BD, colas RabbitMQ, integraciones y flujo de datos.
4. **Generar y ejecutar script:** Ejecuta `scripts/generar_manual.py` con los datos recopilados. Instala `python-docx` si no está disponible. Salida: `D:\BMM\MANUAL_TECNICO_FUNCIONAL_{MICROSERVICIO}.docx`.
5. **Validación:** Verifica el archivo generado, informa la ruta. Si falla, muestra traceback y corrige. Si quedaron datos genéricos, pídelos.

## Quick Reference

| Paso | Acción | Herramienta |
|------|--------|-------------|
| 1 | Recopilar datos de entrada (5 obligatorios, 4 opcionales) | Interacción con el usuario |
| 2 | Explorar microservicio, git log/diff, Vault, plantilla | Subagent + Bash + Read |
| 3 | Consolidar variables del documento | Análisis de código y configuración |
| 4 | Generar script Python y ejecutar | `scripts/generar_manual.py` |
| 5 | Validar y entregar .docx | Verificación de archivo |

## Common Mistakes
- Generar el manual sin recopilar los datos del Paso 1 primero.
- No instalar `python-docx` antes de ejecutar el script.
- No leer `VAULT_FILE` cuando el usuario lo proporciona (sus rutas tienen prioridad).
- No explorar el microservicio completo: omitir `refinamiento.md`, migraciones o configuraciones.
- Colocar el archivo de salida en una ruta incorrecta (siempre `D:\BMM\MANUAL_TECNICO_FUNCIONAL_{MICROSERVICIO}.docx`).
