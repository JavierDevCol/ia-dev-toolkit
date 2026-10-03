---
name: definir-vision-producto
description: Desambigua e interpreta una idea de negocio vaga para estructurar la visión estratégica del producto a largo plazo y delimitar su primer MVP ejecutable.
ready: true
---

# Workflow: Definir Visión del Producto (PO)

## Descripción
Flujo de trabajo para transformar una idea vaga, propuesta de cliente o necesidad informal en un documento de Visión de Producto formal. Extrae la causa raíz del problema, la propuesta de valor holística, la arquitectura funcional a largo plazo, el slicing del MVP y los atributos de calidad deseados.

---

## Flujo de Trabajo (Pipeline Execution)

[Idea Cruda / Input] ──► 1. Descubrimiento & Conceptualización ──► 2. Visión Global & Slicing MVP ──► 3. NFRs & Restricciones ──► 4. Output

1. **FASE 1: Descubrimiento del Problema y Propuesta de Valor**: Seguir instrucción en estricto orden según `./fases/uno_descubrimiento_problema.md`
2. **FASE 2: Visión Holística y Delimitación del MVP**: Seguir instrucción en estricto orden según `./fases/dos_delimitacion_mvp.md`
3. **FASE 3: Atributos de Calidad y Restricciones**: Seguir instrucción en estricto orden según `./fases/tres_atributos_calidad.md`
4. **Formato de Salida Obligatorio (Template-Driven Output)**:
   Entregar el artefacto generado aplicando la plantilla `./plantillas/vision_producto.md` y escribiendo directamente en la raíz del workspace en `./artifacts/vision_producto.md`.
   Leer también `CONFIG_USER.yaml` (ruta en `archivos.config_user`) y tomar `usuario.nombre` → **`{{usuario.nombre}}`**, necesario para firmar el documento como Product Owner. Si está vacío o el archivo no existe, omitir el sufijo de la firma; no inventar un nombre.