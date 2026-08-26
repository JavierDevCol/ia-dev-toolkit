---
name: fix-develop
description: >
  Usa esta skill cuando necesites arreglar un bug durante el desarrollo
  en el proyecto Banca por WhatsApp. Aplica para: bug encontrado en DEVELOP,
  bug durante feature, bug en DES antes de entrega formal, o corrección rápida
  sobre develop. No la uses para bugs en releases ya entregados al banco
  (usar fix-release) ni para entregas formales (usar entrega-ambiente-banco).
compatibility: Requires git
metadata:
  author: CEIBA DevOps
  version: 1.0.0
  manual-ref: MANUAL_PASO_AMBIENTES.md §3.1, §5
---

# Skill: Fix Develop

Gestiona la resolución de bugs durante el desarrollo, antes de la entrega formal al banco.

## Referencias

- Manual: `{file:./references/MANUAL_PASO_AMBIENTES_SECCIONES.md}`

---

## Menú Principal

```
╔══════════════════════════════════════════════════════════╗
║          BUGFIX CEIBA                                    ║
║                                                        ║
║  ¿Dónde se detectó el bug?                              ║
║                                                        ║
║  [1] Bug en DEVELOP                                     ║
║      → Merge a develop ya hecho, CI falla o bug visible ║
║      → Fix directo sobre develop o branch bugfix        ║
║                                                        ║
║  [2] Bug durante feature                                ║
║      → La feature aún NO se mergeó a develop            ║
║      → Fix sobre la misma feature branch                ║
║                                                        ║
║  [3] Bug en DES (antes de entrega formal)               ║
║      → develop tiene el bug, release aún no se creó     ║
║      → Fix sobre develop antes de crear release         ║
║                                                        ║
║  [4] Bug en DES (después de entrega) / PRU / PREPRO/PRO║
║      → Usar @fix-release (RC o hotfix)              ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
```

---

## Opción 1: Bug en DEVELOP

**Cuándo:** El merge a develop ya se hizo. El pipeline falla o el bug es visible en DEVELOP.

### Datos de entrada
1. Preguntar: "¿Cuál es el ID del bug?" (WA2-xxx o descripción)
2. Preguntar: "¿Qué commit introdujo el bug?" (si se conoce)
3. Mostrar estado de develop: `git log develop --oneline -10`

### Flujo

#### Si el fix es trivial (1-2 commits, no rompe nada)
```bash
# Fix directo sobre develop
git checkout develop && git pull
# aplicar fix
git add .
git commit -m "fix: [WA2-xxx] <descripción>"
```

**Validar tests antes de push:**
```bash
# Detectar tipo de proyecto y ejecutar tests
# Node.js (package.json):    npm test
# Java/Maven (pom.xml):      mvn test
# Java/Gradle (build.gradle): gradle test
# .NET (*.csproj):            dotnet test
# Python (pyproject.toml):    pytest
# Go (go.mod):                go test ./...
```

Si fallan → detener y corregir. Si pasan:

```bash
git push origin develop
```

#### Si el fix es complejo o necesita revisión
```bash
# 1. Crear branch bugfix desde develop
git checkout develop && git pull
git checkout -b bugfix/WA2-xxx-<descripcion-corta>

# 2. Aplicar fix
# ... correcciones ...
git add .
git commit -m "fix: [WA2-xxx] <descripción>"

# 3. Validar tests (detectar tipo de proyecto: npm test / mvn test / dotnet test / pytest / go test ./...)
# Si fallan → corregir antes de push

# 4. Push y PR
git push origin bugfix/WA2-xxx-<descripcion-corta>
```

Crear PR `bugfix/WA2-xxx → develop`:
- Título: `fix: [WA2-xxx] <descripción>`
- Descripción: incluir causa raíz y qué se corrigió

#### Paso 3 — Validar
```
CHECKLIST BUGFIX — DEVELOP

[ ] Fix aplicado
[ ] Tests ejecutados y pasan (npm test / mvn test / dotnet test / pytest / go test ./...)
[ ] Pipeline de develop pasa
[ ] Bug verificado en DEVELOP
[ ] PR creado y aprobado (si aplica)
```

#### Resumen
```
✅ Bugfix completado.

📦 Cambios:
  • Branch: bugfix/WA2-xxx-<desc> (o directo en develop)
  • PR: bugfix/WA2-xxx → develop

📌 Siguiente paso:
  • Si hay release pendiente → incluir este fix antes de handoff
  • Si no → esperar próximo ciclo de release
```

---

## Opción 2: Bug durante feature

**Cuándo:** La feature branch aún no se mergeó a develop. El bug está en el código de la feature.

### Flujo

```bash
# 1. Sobre la misma feature branch
git checkout feature/WA2-xxx
# aplicar fix
git add .
git commit -m "fix: [WA2-xxx] <descripción del bug>"

# 2. Validar tests (detectar tipo de proyecto: npm test / mvn test / dotnet test / pytest / go test ./...)
# Si fallan → corregir antes de push

# 3. Push
git push origin feature/WA2-xxx
```

No se crea branch adicional. El fix va como commit dentro de la feature.

#### Validación
- Ejecutar tests del proyecto (detectar: `npm test` / `mvn test` / `dotnet test` / `pytest` / `go test ./...`)
- Verificar que el bug no afecta otras features ya integradas en develop

#### Resumen
```
✅ Bugfix aplicado sobre feature/WA2-xxx.

📦 Cambios:
  • Commit: fix: [WA2-xxx] <descripción>
  • Push a origin feature/WA2-xxx

📌 Siguiente paso:
  • Cuando la feature esté lista → PR feature/WA2-xxx → develop
  • El fix se incluye automáticamente en el PR
```

---

## Opción 3: Bug en DES antes de entrega formal

**Cuándo:** El banco o CEIBA detectó un bug en DES, pero el release formal aún no se creó (o se creó pero no se entregó). El fix va sobre develop.

### Flujo

```bash
# 1. Verificar que NO existe release branch activo
git branch -a | grep release/
# Si existe release/vX.Y.Z → redirigir a @fix-release (Opción 1 RC)

# 2. Fix sobre develop
git checkout develop && git pull
# aplicar fix
git add .
git commit -m "fix: [WA2-xxx] <descripción>"

# 3. Validar tests (detectar tipo de proyecto: npm test / mvn test / dotnet test / pytest / go test ./...)
# Si fallan → corregir antes de push

# 4. Push
git push origin develop

# 5. Validar en DEVELOP que el fix funciona
```

#### Resumen
```
✅ Fix integrado en develop.

📦 Cambios:
  • develop actualizado con el fix
  • Pipeline de develop despliega a DEVELOP

📌 Siguiente paso:
  • Validar en DEVELOP
  • Cuando esté OK → crear release y handoff a banco
```

---

## Cuándo NO usar esta skill

| Escenario | Skill correcta |
|-----------|----------------|
| Bug en DES después de entrega (release entregado) | `fix-release` Opción 1 (RC) |
| Bug en PRU/PREPRO/PRO | `fix-release` Opción 2 (hotfix) |
| Entrega formal de release | `entrega-ambiente-banco` |
| Feature nueva (no es bug) | Desarrollo normal → PR a develop |

---

## Convención de ramas

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Bug en desarrollo | `bugfix/WA2-xxx-<desc>` | `bugfix/WA2-123-login-error` |
| Bug durante feature | (dentro de la feature branch) | `feature/WA2-123` |
| Hotfix release (entregado) | `hotfix/<desc>` | `hotfix/login-crash` |

---

## Reglas

1. **Bug en develop = fix en develop.** No crear release branch para un bugfix pre-entrega.
2. **Bug durante feature = fix en la misma feature.** No crear branch separado.
3. **Si hay release branch activo** → redirigir a `fix-release`.
4. **Siempre verificar que el fix no rompe otras features** antes de push a develop.
5. **Naming del commit:** `fix: [WA2-xxx] <descripción>` o `fix: <descripción>` si no hay ID.

## Gotchas

- **develop protegida:** Si push directo falla, crear PR de `bugfix/WA2-xxx → develop`.
- **Bug causado por otro merge:** Verificar `git log develop --oneline -20` para identificar el commit culpable.
- **Fix que requiere cambio de config:** Ejecutar `@pr-config-audit` después del fix.
- **Bug en DES pero release ya entregado:** NO es esta skill. Usar `fix-release`.

## Skills complementarias

| Skill | Qué hace | Cuándo |
|-------|----------|--------|
| `fix-release` | Fix sobre release entregado (RC/hotfix) | Bug en DES post-entrega o PRU/PREPRO/PRO |
| `entrega-ambiente-banco` | Entrega formal al banco | Después de validar fix en DEVELOP |
| `pr-config-audit` | Genera CONFIG_ENTORNO_PR | Si el fix incluye cambios de config |
| `ado-pipeline-analyzer` | Valida pipeline | Verificar que fix no rompe build/tests |
