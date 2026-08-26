---
name: git-branch-commit
description: >
  Crea ramas y gestiona commits siguiendo convenciones del proyecto.
  Úsala cuando el usuario pida crear una rama, hacer commit, o
  verificar formato de mensajes de commit. Detecta automáticamente
  qué necesita el usuario (rama o commit) y ejecuta directamente.
  No la uses para entregas (usar entrega-ambiente-banco) ni para
  fixes post-entrega (usar fix-release).
compatibility: Requires git
metadata:
  author: CEIBA DevOps
  version: 2.0.0
---

# Skill: Git Branch & Commit

Crea ramas y gestiona commits de forma directa según la solicitud del usuario.

---

## Detección Automática

La skill detecta qué necesita el usuario:

| Solicitud del usuario | Acción |
|-----------------------|--------|
| "Crear rama para HU 131735" | → **Crear rama** |
| "Nueva rama feature X" | → **Crear rama** |
| "Hacer commit" / "Commitear" | → **Commit** |
| "Guardar cambios" | → **Commit** |
| "¿Cómo se llama esta rama?" | → **Crear rama** |

---

## Crear Rama

### 1. Validar origen

```bash
git fetch origin
```

Preguntar: "¿Desde qué rama base?" (main, develop, release/vX.Y.Z)
- Si no responde, usar `develop` como defecto.
- Validar que existe: `git branch -a | grep "rama_origen"`
- Si no existe → error. Detener.

### 2. Generar nombre

**Si es HU** (el usuario menciona ID de historia):
- Formato: `hu-[ID]-[descripcion-kebab-case]`
- Ejemplo: `hu-131735-consultar-saldo-tarjeta`

**Si es caso general:**
- Formato: `[tipo]-[descripcion-kebab-case]`
- Tipos: `feature`, `hotfix`, `chore`, `refactor`, `docs`
- Ejemplo: `feature-agregar-filtro-fechas`

### 3. Crear y pushear

```bash
git checkout -b [nombre_rama] [rama_origen]
git push -u origin [nombre_rama]
```

### 4. Commit inicial obligatorio

```bash
git commit --allow-empty -m "chore: iniciar [descripción]"
```

**Formato:**
- Si es HU: `chore: iniciar desarrollo de HU [ID]`
- Si es general: `chore: iniciar cambios en [descripcion]`

### 5. Resumen

```
✅ Rama creada.
  • Nombre: [nombre_rama]
  • Origen: [rama_origen]
  • Commit: chore: iniciar [descripción]
```

---

## Hacer Commit

### 1. Verificar estado

```bash
git status
git diff --staged
git diff
```

### 2. Agregar archivos

Preguntar: "¿Archivos a commitear?"
- **[T]** Todos (`git add .`)
- **[E]** Elegir específicos
- **[S]** Solo staged

### 3. Tipo de commit

```
¿Qué tipo de cambio es?

  [f] feat:      Nueva funcionalidad
  [x] fix:       Corrección de errores
  [r] refactor:  Optimización sin cambio funcional
  [d] docs:      Solo documentación
  [c] chore:     Mantenimiento o configuración
  [b] BREAKING:  Rompe compatibilidad anterior
```

### 4. Scope (opcional)

Preguntar: "¿Aplica algún ámbito?" (api, ui, auth, etc.)
- Si aplica: `tipo(ámbito): descripción`
- Si no: `tipo: descripción`

### 5. Generar mensaje

Reglas:
- Descripción en inglés, imperativo, sin punto final
- Máximo 72 caracteres en primera línea
- Si es BREAKING CHANGE, agregar `BREAKING CHANGE:` en el cuerpo

### 6. Preview y Aprobación

**NUNCA** ejecutar sin aprobación:

```
PREVIEW DEL COMMIT

  Título: [tipo(ámbito): descripción]
  Archivos: [lista]

  [S] Confirmar y push
  [E] Editar mensaje
  [N] Cancelar
```

### 7. Ejecutar

```bash
git commit -m "[tipo(ámbito): descripción]"
git push origin [rama_actual]
```

### 8. Resumen

```
✅ Commit realizado.
  • Hash: [hash_corto]
  • Mensaje: [tipo(ámbito): descripción]
  • Rama: [nombre_rama]
```

---

## Reglas

1. **Commit inicial siempre.** Toda rama nueva empieza con commit vacío.
2. **Conventional Commits estricto.** Tipo + descripción en imperativo.
3. **Preview obligatorio.** Nunca ejecutar sin aprobación.
4. **Push automático.** Después del commit, hacer push.
5. **Kebab-case.** Minúsculas, guiones, sin espacios.

---

## Gotchas

- **Rama ya existe:** Preguntar si usar la existente o crear otra.
- **develop protegida:** Crear PR en lugar de push directo.
- **Commit vacío rechazado:** Usar `.gitkeep` temporal.
