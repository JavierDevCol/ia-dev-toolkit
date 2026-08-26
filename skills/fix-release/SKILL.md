---
name: fix-release
description: >
  Usa esta skill cuando necesites arreglar un bug sobre un release
  ya entregado al banco en el proyecto Banca por WhatsApp. Aplica para:
  banco solicita cambios en DES (RC), bug reportado en PRU/PREPRO/PRO (hotfix),
  crear release candidate, o propagar fix por todos los ambientes.
  No la uses para entregas iniciales de release (usar entrega-ambiente-banco)
  ni para bugs durante desarrollo (usar fix-develop).
compatibility: Requires git
metadata:
  author: CEIBA DevOps
  version: 1.0.0
  manual-ref: MANUAL_PASO_AMBIENTES.md §3.2.1, §5
---

# Skill: Fix Release

Gestiona fixes y hotfixes sobre releases ya entregados al banco.

## Referencias

- Manual completo: `{file:./references/MANUAL_PASO_AMBIENTES_SECCIONES.md}`

---

## Menú Principal

```
╔══════════════════════════════════════════════════════════╗
║          AJUSTE DE RELEASES                              ║
║                                                        ║
║  ¿Qué tipo de ajuste necesitas?                         ║
║                                                        ║
║  [1] Ajuste RC — Banco pidió cambios en DES             ║
║      → Fix sobre release vivo + RC efímera              ║
║      → v2.2.3 → v2.2.3-rc.1 → v2.2.3 (final)          ║
║                                                        ║
║  [2] Hotfix — Bug en PRU/PREPRO/PRO                     ║
║      → Merge a develop primero + nuevo release          ║
║      → v2.2.3 → v2.2.4 (flujo completo)                ║
║                                                        ║
║  [3] Hotfix en DES — Bug antes de promoción a PRU      ║
║      → Igual que RC (usar opción 1)                     ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
```

---

## Opción 1: Ajuste RC en DES (§3.2.1 del manual)

**Cuándo:** El banco validó en DES y pide cambios. El release branch `release/vX.Y.Z` sigue vivo.

### Datos de entrada
1. Preguntar: "¿Versión del release activo?" (ej. v2.2.3)
2. Validar rama: `git fetch origin && git branch -a | grep "release/v2.2.3"`
   - Si no existe → error. Detener.
3. Preguntar: "¿Qué ajuste solicitó el banco?"
4. Determinar N del RC: `git tag -l "v2.2.3-rc.*" | sort -V | tail -1`
   - Si no hay RCs → N=1. Si rc.1 existe → N=2, etc.

### Pasos

#### Paso 1 — Fix sobre rama base
```bash
git checkout release/v2.2.3 && git pull origin release/v2.2.3
# aplicar ajustes (mostrar archivos modificados)
git add .
git commit -m "fix: <descripción>"
```

#### Paso 1.1 — Validar tests
Antes de hacer push, ejecutar los tests del proyecto para verificar que el fix no rompe nada:

```bash
# Detectar tipo de proyecto y ejecutar tests
# Node.js (package.json):    npm test
# Java/Maven (pom.xml):      mvn test
# Java/Gradle (build.gradle): gradle test
# .NET (*.csproj):            dotnet test
# Python (pyproject.toml):    pytest
# Go (go.mod):                go test ./...
```

Si los tests fallan → detener, corregir antes de continuar.
Si los tests pasan → continuar con push.

```bash
git push origin release/v2.2.3
```

#### Paso 2 — Back-merge a develop
```bash
git checkout develop
git merge --no-ff release/v2.2.3
git push origin develop
```
Si develop está protegida → crear PR de `release/v2.2.3 → develop`.

#### Paso 3 — Crear RC efímera
```bash
git checkout -b release/v2.2.3-rc.N release/v2.2.3
git push origin release/v2.2.3-rc.N
```

#### Paso 4 — Resumen
```
✅ RC preparado.

📦 Cambios:
  • release/v2.2.3 actualizado con el fix
  • develop tiene el fix via back-merge (--no-ff)
  • Rama efímera: release/v2.2.3-rc.N (PR a des)

📌 El banco debe:
  1. Crear PR release/v2.2.3-rc.N → des
  2. Mergear → tag v2.2.3-rc.N en des
  3. Validar en DES
  4. Si aprueba → tag v2.2.3 final (sin RC) → promover

⚠️ Notas:
  • release/v2.2.3 permanece viva durante el ciclo RC
  • La rama RC se elimina después del merge a des
  • Si hay más ajustes, repetir con rc.(N+1)
  • develop y release están en commits distintos (esperado)
```

Preguntar: "¿Deseas eliminar la rama RC después de que el banco mergee?"
- Si sí → instruir: `git push origin --delete release/v2.2.3-rc.N && git branch -d release/v2.2.3-rc.N`

#### Paso 5 — Aprobación final (cuando el banco aprueba)
Cuando el banco confirma que no hay más ajustes:
```bash
# El banco crea PR release/v2.2.3 (rama base) → des y taggea v2.2.3 final

# CEIBA: back-merge final + limpieza
git checkout develop
git merge --no-ff release/v2.2.3
git push origin develop

git push origin --delete release/v2.2.3
git branch -d release/v2.2.3
```

---

## Opción 2: Hotfix en PRU/PREPRO/PRO (§5.2 del manual)

**Cuándo:** El banco reporta un bug en un ambiente superior. Se crea un nuevo release con PATCH incrementado.

### Datos de entrada
1. Preguntar: "¿En qué ambiente está el bug?" (PRU / PREPRO / PRO)
2. Preguntar: "¿Versión del release afectado?" (ej. v2.2.3)
3. Validar tag: `git tag -l "v2.2.3-<ambiente>"`
   - Si no existe → error. Detener.
4. Preguntar: "¿Qué bug reportó el banco?"

### Pasos

#### Paso 1 — Hotfix branch desde tag
```bash
git checkout -b hotfix/arreglo-x v2.2.3-pro
```

#### Paso 2 — Analizar y aplicar fix
```bash
# ... correcciones ...
git add .
git commit -m "fix: <descripción>"
```

#### Paso 2.1 — Validar tests
```bash
# Detectar tipo de proyecto y ejecutar tests
# Node.js (package.json):    npm test
# Java/Maven (pom.xml):      mvn test
# Java/Gradle (build.gradle): gradle test
# .NET (*.csproj):            dotnet test
# Python (pyproject.toml):    pytest
# Go (go.mod):                go test ./...
```

Si fallan → detener y corregir.

#### Paso 3 — Verificar develop
```bash
git log develop --oneline | head -10
# Confirmar que develop tiene el mismo código y necesita el fix
```

#### Paso 4 — Merge a develop PRIMERO (via PR)

develop está protegida → crear PR:

```bash
# Crear PR de hotfix → develop
git checkout -b hotfix/arreglo-x
git push origin hotfix/arreglo-x

# Crear PR via ADO o gh cli
# Título: "fix: <descripción> — hotfix desde v2.2.3-pro"
# Source: hotfix/arreglo-x
# Target: develop
```

Esperar aprobación y merge del PR.

#### Paso 5 — Esperar merge del PR

Una vez creado el PR, informar al usuario:

```
📌 PR creado: hotfix/arreglo-x → develop

Esperando aprobación y merge...

INFORMAME CUANDO EL PR SE ACEPTE PARA SEGUIR EL FLUJO.
```

**Cuando el usuario confirme que el PR se mergeó**, preguntar:

```
╔══════════════════════════════════════════════════════════╗
║  Hotfix mergeado a develop.                              ║
║                                                        ║
║  ¿Qué sigue?                                            ║
║                                                        ║
║  [S] Entrega formal — Ejecutar @entrega-ambiente-banco           ║
║      Genera release-notes, checklist, RESUMEN_ENTREGA   ║
║      Crama release/vX.Y.Z con artefactos completos      ║
║                                                        ║
║  [N] Instrucciones simples                              ║
║      Solo mostrar pasos al banco sin artefactos         ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
```

#### Paso 6a — Si elige [S]: Delegar a entrega-ambiente-banco

```
Ejecutar: @entrega-ambiente-banco

Seleccionar: [1] Entregar release desde DEVELOP

La skill entrega-ambiente-banco se encarga de:
  ├── Verificar que develop pasó pipeline
  ├── Generar release-notes.md
  ├── Crama release/vX.Y.Z
  ├── Validar mismo commit (develop === release)
  ├── Checklist de entrega completo
  ├── RESUMEN_ENTREGA_*.txt
  └── Instrucciones al banco
```

#### Paso 6b — Si elige [N]: Instrucciones simples

```bash
# Crear release desde develop
git checkout develop && git pull
git checkout -b release/v2.2.4
git push origin release/v2.2.4
```

Mostrar resumen simple:
```
✅ Hotfix integrado — nuevo release creado.

📦 Cambios:
  • Hotfix: hotfix/arreglo-x (desde tag v2.2.3-pro)
  • develop tiene el fix via PR mergeado
  • Nuevo release: release/v2.2.4 (push a origin)

📌 Flujo completo (el banco valida en cada paso):
  1. release/v2.2.4 → PR a des → tag v2.2.4 → validar en DES
  2. des → pru → tag v2.2.4-pru → validar en PRU
  3. pru → prepro → tag v2.2.4-prepro → validar en PREPRO
  4. prepro → pro → tag v2.2.4-pro → PRODUCCIÓN

⚠️ Notas:
  • Si hay cambios de config, ejecutar @pr-config-audit
  • No saltar ambientes — el banco valida en cada uno
```

#### Paso 7 — Limpieza
```bash
git branch -d hotfix/arreglo-x
git push origin --delete hotfix/arreglo-x
```

---

## Opción 3: Hotfix en DES

Igual que la Opción 1 (Ajuste RC). El bug en DES antes de promoción a PRU se maneja como RC:

```bash
git checkout release/v2.2.3
# aplicar fix
git commit -m "fix: corregir [descripción]"

# Validar tests (detectar tipo de proyecto: npm test / mvn test / dotnet test / pytest / go test ./...)
# Si fallan → detener y corregir

git push origin release/v2.2.3

# Back-merge a develop
git checkout develop
git merge --no-ff release/v2.2.3
git push origin develop

# RC efímera
git checkout -b release/v2.2.3-rc.1 release/v2.2.3
git push origin release/v2.2.3-rc.1
```

---

## Convención de Versionado

| Escenario | Formato | Ejemplo |
|-----------|---------|---------|
| Release normal | `vMAJOR.MINOR.PATCH` | `v2.2.3` |
| RC en DES | `vMAJOR.MINOR.PATCH-rc.N` | `v2.2.3-rc.1` |
| Hotfix (nuevo release) | `vMAJOR.MINOR.PATCH+1` | `v2.2.4` |
| Promoción PRU | `vMAJOR.MINOR.PATCH-pru` | `v2.2.3-pru` |
| Promoción PREPRO | `vMAJOR.MINOR.PATCH-prepro` | `v2.2.3-prepro` |
| Promoción PRO | `vMAJOR.MINOR.PATCH-pro` | `v2.2.3-pro` |

---

## Reglas obligatorias

1. **RC = rama efímera.** Crear para PR a des, eliminar después del merge.
2. **Rama base viva.** `release/vX.Y.Z` permanece durante todo el ciclo RC.
3. **Hotfix merge a develop primero.** Garantiza merge limpio antes de crear el nuevo release.
4. **Hotfix = nuevo release.** Incrementar PATCH. No reutilizar la versión original.
5. **Flujo completo para hotfix.** develop → des → pru → prepro → pro. No saltar ambientes.
6. **No crear tags.** Los tags los genera el banco al mergear a des.
7. **Back-merge siempre.** Todo fix en release debe propagarse a develop.
8. **develop protegida.** Merge a develop siempre via PR. Nunca push directo.
9. **Delegar a entrega-ambiente-banco.** Después de merge a develop, ofrecer entrega formal con artefactos completos.

## Gotchas

- **develop y release distintos después de fix:** Esperado. El release tiene commits propios. No forzar coincidencia.
- **develop protegida:** Si push directo falla, crear PR de `release/vX.Y.Z → develop`.
- **RC branch eliminada pero tag persiste:** El tag `vX.Y.Z-rc.N` en des preserva trazabilidad aunque la rama se elimine.
- **Hotfix desde develop NO:** Siempre desde el tag del ambiente afectado. develop puede tener commits nuevos que contaminan el fix.
- **Tag RC vs tag final:** El banco taggea `v2.2.3-rc.1` al mergear RC. Cuando aprueba, taggea `v2.2.3` (sin RC) como final.

## Skills complementarias

| Skill | Qué hace | Cuándo |
|-------|----------|--------|
| `entrega-ambiente-banco` | Entrega formal con artefactos | Opción 2: después de merge a develop (paso 6a) |
| `entrega-ambiente-banco` | Entrega inicial de release | Primera entrega a DES |
| `pr-config-audit` | Genera CONFIG_ENTORNO_PR | Si el fix incluye cambios de config |
| `ado-pipeline-analyzer` | Valida pipeline | Verificar que el fix no rompe build/tests |
