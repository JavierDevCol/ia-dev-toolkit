# Proceso del Cuestionario de Reglas Arquitectónicas

> Flujo detallado paso a paso para generar las reglas arquitectónicas del proyecto.

---

## 1. Cargar Configuración

- Leer la config con memctl (solo lectura; su salida ES la respuesta; si memctl no existe (exit 127), leer `.SAC/config/sac.json` con `jq`; si sale con exit 1 (JSON inválido o vacío), detenerse y avisar: no leer ni editar el archivo a mano; nunca inventar valores):

Ejecutar cada comando: **su salida ES el valor del placeholder** de su fila y se usa tal cual en el resto de esta skill (no recalcular ni inventar rutas):

| Placeholder / dato | Valor = salida de |
|---|---|
| `{reglas_arquitectonicas}` | `sh .SAC/memctl.sh get archivos.reglas_arquitectonicas` |
| `{workspace}` | `sh .SAC/memctl.sh get archivos.workspace` |
| `{contextos_folder}` | `sh .SAC/memctl.sh get artifacts.contextos_folder` |
| `{adr_folder}` | `sh .SAC/memctl.sh get artifacts.adr_folder` |
| `{documentacion_sac_path}` | `sh .SAC/memctl.sh get documentacion_sac_path` |
| `idiomas.documentacion` | `sh .SAC/memctl.sh get idiomas.documentacion` |
| `{{usuario.nombre}}` | `sh .SAC/memctl.sh get usuario.nombre` |
| `usuario.incluir_firma_en_documentos` | `sh .SAC/memctl.sh get usuario.incluir_firma_en_documentos` |

  `idiomas.documentacion` (`es|en|pt`) es el idioma; vacío o exit 2 → preguntar.
- **Plantilla propia:** leer `{file:./assets/reglas_arquitectonicas_plantilla.md}`
- Verificar que existe contexto del proyecto:
  - Buscar `{workspace}` o archivo de contexto en `{contextos_folder}/`
  - Si NO existe → Informar: "Necesito conocer el proyecto primero. Ejecuta >sac_tomar_contexto"
  - Extraer stack tecnológico y arquitectura del contexto

## 2. Detectar Modo de Operación

- Si ya existen reglas arquitectónicas Y `--force` no está activo:
  > ℹ️ Ya existen reglas arquitectónicas configuradas.
  > - [V] Ver actuales
  > - [E] Editar secciones específicas
  > - [R] Regenerar desde cero
- Si no existen → Continuar con modo nuevo

## 3. Ejecutar Cuestionario

**Reglas del cuestionario:**
- Hacer **UNA pregunta a la vez**
- **ESPERAR** respuesta antes de siguiente pregunta
- Ofrecer opciones predefinidas [A/B/C]
- Permitir respuestas personalizadas con "Otro: ..."
- Si usuario responde "default" o "d" → usar valor sugerido
- Si usuario responde "saltar" o "s" → omitir pregunta

**Secciones del cuestionario** (ver `references/cuestionario.md` para preguntas completas):

| # | Sección | Preguntas | Tags |
|---|---------|-----------|------|
| 1 | Nomenclatura | 6 | Clases, métodos, variables, constantes, interfaces, implementaciones |
| 2 | Arquitectura | 4 | Estilo, carpetas, dependencias, DDD |
| 3 | Patrones | 3 | Obligatorios, prohibidos, creación de objetos |
| 4 | Principios | 5 | SOLID, inmutabilidad, nulls, paradigma, composición |
| 5 | Dependencias | 4 | Testing libs, logging, prohibidas, política actualización |
| 6 | Testing | 4 | Metodología, cobertura, nombres, integración |
| 7 | Documentación | 3 | Código, ADRs, formato ADR |
| 8 | Seguridad | 4 | Logging sensible, validación, límites código, análisis estático |

**Adaptar preguntas según stack:**
- Algunas preguntas tienen `aplica_a` → si el stack actual no está en la lista, saltar
- Mostrar valor sugerido basado en el contexto del proyecto
- After each section → Mostrar resumen y ofrecer [CONTINUAR | EDITAR SECCIÓN]

## 4. Compilar Configuración

- Consolidar todas las respuestas
- Aplicar valores por defecto donde se usó "default" o "saltar"
- Generar estructura completa del documento

## 5. Mostrar Configuración Completa

- Mostrar **TODO** el documento generado (no resumen)
- Incluir todas las secciones con sus valores
- Solicitar confirmación:
  > 📋 **REVISIÓN DE CONFIGURACIÓN**
  >
  > Arriba puedes ver la configuración completa que se guardará.
  >
  > **Opciones:**
  > - **OK** → Guardar archivo y finalizar
  > - **EDITAR [sección]** → Modificar una sección
  > - **EDITAR [pregunta_id]** → Modificar una respuesta específica
  > - **REGENERAR** → Volver a empezar

## 6. Procesar Ediciones (si aplica)

- Si usuario elige EDITAR → Identificar sección o pregunta
- Mostrar pregunta(s), recopilar nueva(s) respuesta(s)
- Actualizar configuración, volver a mostrar documento
- Repetir hasta que usuario responda OK

## 7. Generar Archivo de Reglas

- Crear `{documentacion_sac_path}/` si no existe
- Generar `{reglas_arquitectonicas}` desde `{file:./assets/reglas_arquitectonicas_plantilla.md}`
- Incluir metadata: fecha, versión, aprobado_por

## 8. Actualizar Contexto del Proyecto

- Abrir contexto del proyecto
- Buscar sección "## Referencias" o "## Artefactos Relacionados"
- Si no existe → Crearla al final
- Agregar referencia:
  ```
  ### Reglas Arquitectónicas
  - **Archivo:** {reglas_arquitectonicas}
  - **Generado:** {fecha}
  - **Versión:** 1.0
  - **Estado:** ✅ Configurado
  ```

## Restricciones

- **NUNCA** generar archivo final sin confirmación explícita del usuario (OK)
- Mostrar configuración **COMPLETA** antes de solicitar confirmación, NO resúmenes
- Ofrecer siempre opciones EDITAR para modificar secciones específicas
- Adaptar preguntas dinámicamente según stack detectado
- Ejecutar cuestionario PREGUNTA POR PREGUNTA, esperar respuesta antes de continuar

## Formato de salida

```
✅ REGLAS ARQUITECTÓNICAS CONFIGURADAS

📁 Archivo generado: {reglas_arquitectonicas}
📝 Contexto actualizado: (ver workspace)

📊 Configuración aplicada:
- Nomenclatura: [resumen]
- Arquitectura: [estilo seleccionado]
- Patrones obligatorios: [lista]
- Testing: [metodología] con [cobertura]%

💡 Los agentes consultarán estas reglas para tomar decisiones consistentes.

Siguiente: >refinar_hu o >validar_hu
```
