# Manual de Paso entre Ambientes

| Versión | Fecha       | Autor          | Descripción                     |
|---------|-------------|----------------|---------------------------------|
| 1.0     | 2026-06-11  | DevOps Ceiba   | Versión inicial del manual      |
| 1.1     | 2026-07-08  | DevOps Ceiba   | RC versioning + flujo hotfix invertido |

---

## 1. Propósito

Definir el proceso, responsabilidades y trazabilidad para la promoción de artefactos a través de los 5 ambientes del proyecto Banca por WhatsApp: **DEVELOP → DES → PRU → PREPRO → PRO**.

Los 5 ambientes pertenecen al banco, excepto DEVELOP que es el ambiente propio de CEIBA para pruebas de integración. La gestión se divide en:

| Responsable | Ambientes que gestiona              | Handoff                         |
|-------------|-------------------------------------|----------------------------------|
| **CEIBA**   | DEVELOP (propio)                    | Entrega release en rama `des` + tag |
| **BANCO**   | DES → PRU → PREPRO → PRO            | Promueve entre sus ambientes     |

---

## 2. Arquitectura de Ramas y Ambientes

```
                      ┌─────────────────────────────────────────────────────┐
                      │                RESPONSABILIDAD CEIBA                │
                      │                                                     │
                      │   feature/WA2-xxx  ──┐                              │
                      │                      ├──►  develop  ──►  DEVELOP    │
                      │   feature/WA2-yyy  ──┘                              │
                      │                            │                        │
                      │                            ▼                        │
                      │                     release/x.y.z                    │
                      │                            │                        │
                      └────────────────────────────┼────────────────────────┘
                                                   │   ↑ Handoff (merge a des + tag)
                      ┌────────────────────────────┼────────────────────────┐
                      │       RESPONSABILIDAD BANCO                        │
                      │                            ▼                        │
                      │                      ┌──────────┐                   │
                      │                      │    des   │ ◄────── TAG vX.Y.Z│
                      │                      └────┬─────┘                   │
                      │                           │                        │
                      │                           ▼                        │
                      │                      ┌──────────┐                   │
                      │                      │   pru    │ ◄── TAG vX.Y.Z-pru│
                      │                      └────┬─────┘                   │
                      │                           │                        │
                      │                           ▼                        │
                      │                      ┌──────────┐                   │
                      │                      │  prepro  │ ◄── TAG vX.Y.Z-pp│
                      │                      └────┬─────┘                   │
                      │                           │                        │
                      │                           ▼                        │
                      │                      ┌──────────┐                   │
                      │                      │ main/pro │ ◄── TAG vX.Y.Z-pro│
                      │                      └──────────┘                   │
                      └─────────────────────────────────────────────────────┘
```

### 2.1 Correspondencia Rama ↔ Ambiente

| Rama              | Ambiente | Responsable | Tipo de despliegue       |
|-------------------|----------|-------------|--------------------------|
| `develop`         | DEVELOP  | CEIBA       | Continuo (por merge)     |
| `des`             | DES      | BANCO       | Release versionado       |
| `pru`             | PRU      | BANCO       | Promoción desde DES      |
| `prepro`          | PREPRO   | BANCO       | Promoción desde PRU      |
| `main` / `master` | PRO      | BANCO       | Promoción desde PREPRO   |

---

## 3. Flujo de Trabajo

### 3.1 Desarrollo (CEIBA)

```
1. feature/WA2-xxx ──merge──► develop ──► CI en DEVELOP
2. feature/WA2-yyy ──merge──► develop ──► CI en DEVELOP
```

- Cada merge a `develop` dispara el pipeline y despliega automáticamente a DEVELOP.
- DEVELOP es el ambiente de integración y validación de CEIBA.

### 3.2 Creación de Release y Handoff al Banco (CEIBA)

Cuando la funcionalidad está estabilizada, CEIBA prepara el release y entrega al banco:

```bash
# 1. Verificar si ya existe la rama release
git fetch origin
git branch -a | grep release/v1.2.3

# CASO A — La rama NO existe: crearla desde develop (develop y release quedan en el mismo commit)
git checkout develop
git pull
git checkout -b release/v1.2.3
git push origin release/v1.2.3

# CASO B — La rama YA existe: actualizarla con fast-forward
git checkout release/v1.2.3
git pull origin release/v1.2.3
git merge --ff-only develop   # garantiza que release quede en el mismo commit que develop
git push origin release/v1.2.3

# 2. Validar que develop y release apuntan al mismo commit (obligatorio antes de notificar al banco)
git rev-parse develop
git rev-parse release/v1.2.3
# Si los hashes son distintos → release tiene commits propios → ver §3.2.1

# 3. Ajustes de release (versión, changelog, etc.)

# 4. Notificar al banco y entregar artefactos y release notes
```

> ⚠️ **Regla de oro:** `develop` y `release/vX.Y.Z` deben apuntar al **mismo commit** antes del handoff. Usar siempre `--ff-only` al actualizar una release existente. Si el fast-forward falla, significa que la release tiene commits propios — resolver primero según §3.2.1.

**El banco toma la rama `release/v1.2.3`, crea un PR hacia `des`, lo mergea y genera el tag `v1.2.3` en `des`, y despliega en su ambiente DES para validación.**

**El release branch permanece vivo durante la validación del banco en DES para poder recibir ajustes si es necesario.**

**Reglas del release:**
- Versionamiento semántico: `vMAJOR.MINOR.PATCH` (ej. `v2.1.0`)
- Ajustes post-entrega en DES: `vMAJOR.MINOR.PATCH-rc.N` (ej. `v2.1.0-rc.1`)
- Hotfixes: incremento de PATCH (ej. `v2.1.0` → `v2.1.1`)
- El tag `v1.2.3` lo genera el banco al mergear el PR a `des` (punto de handoff)
- Los tags RC (`v1.2.3-rc.N`) los genera el banco al mergear cada RC a `des`
- Cada release debe incluir release notes con el cambio acumulado desde el tag anterior
- El archivo `release-notes.md` se genera **desde cero en cada release** sobrescribiendo el anterior, no se actualiza incrementalmente.
  - Al crear `release/vX.Y.Z` el pipeline ejecuta `git log vX.Y.Z-1..HEAD > release-notes.md`
  - Al mergear a `develop` ese archivo queda en el historial, pero el siguiente release lo reemplazará con los nuevos commits

### 3.2.1 Ajustes solicitados por el banco tras validación en DES

Si el banco solicita cambios tras validar en DES, CEIBA aplica los ajustes directamente sobre el release branch (aún vivo). Cada ajuste se entrega como **Release Candidate (RC)** con versionado diferenciado.

#### Convención de versionado RC

| Escenario | Rama | Tag en des | Ejemplo |
|-----------|------|------------|---------|
| Entrega original | `release/vX.Y.Z` | `vX.Y.Z` | `release/v2.2.3` → tag `v2.2.3` |
| Primer ajuste | `release/vX.Y.Z-rc.N` | `vX.Y.Z-rc.N` | `release/v2.2.3-rc.1` → tag `v2.2.3-rc.1` |
| Segundo ajuste | `release/vX.Y.Z-rc.N` | `vX.Y.Z-rc.N` | `release/v2.2.3-rc.2` → tag `v2.2.3-rc.2` |
| Aprobación final | — | `vX.Y.Z` (sin RC) | Tag `v2.2.3` final en des |

#### Ciclo de vida de las ramas

- **`release/vX.Y.Z`** — rama base, permanece viva durante todo el ciclo RC. Acumula los fixes.
- **`release/vX.Y.Z-rc.N`** — ramas efímeras. Se crean desde la rama base para el PR a `des`. Se eliminan inmediatamente después de que el banco mergea el PR.

```
release/v2.2.3        ← viva durante todo el ciclo RC
  ├── release/v2.2.3-rc.1  ← efímera: PR → merge → tag → eliminar
  ├── release/v2.2.3-rc.2  ← efímera: PR → merge → tag → eliminar
  └── [banco aprueba] → tag v2.2.3 final → back-merge a develop → eliminar release/v2.2.3
```

#### Flujo de ajuste

```bash
# 1. Aplicar fix sobre la rama base (release/vX.Y.Z sigue viva)
git checkout release/v2.2.3
# aplicar ajustes
git commit -m "fix: ajuste solicitado por banco en DES"
git push origin release/v2.2.3

# 2. Crear rama RC efímera y probar en DEVELOP antes de propagar
git checkout -b release/v2.2.3-rc.1 release/v2.2.3
git push origin release/v2.2.3-rc.1
# El pipeline despliega en DEVELOP → validar que el fix funciona correctamente

# 3. Propagar el fix a develop mediante PR (back-merge validado)
# Crear PR: release/v2.2.3 → develop
# El PR debe incluir descripción del fix y link al WI/bug original
# Requiere al menos 1 approval (ver §8)

# 4. El banco crea PR release/v2.2.3-rc.1 → des, mergea y taggea v2.2.3-rc.1 en des

# 5. Eliminar rama RC (su propósito está cumplido)
git push origin --delete release/v2.2.3-rc.1
git branch -d release/v2.2.3-rc.1
```

> ⚠️ **Regla de oro:** Nunca hacer back-merge a develop sin haber probado el fix en DEVELOP primero. El paso 2 es obligatorio, excepto para fixes triviales (typo, config) que no afectan lógica de negocio.

#### Aprobación final

Cuando el banco aprueba la versión (después de 0 o más RCs):

```bash
# El banco crea PR desde release/vX.Y.Z (rama base, no RC) → des
# El banco mergea y taggea el tag final vX.Y.Z (sin sufijo RC) en des

# CEIBA hace back-merge final a develop mediante PR y elimina la rama base
# Crear PR: release/v2.2.3 → develop
# Requiere al menos 1 approval (ver §8)

git push origin --delete release/v2.2.3
git branch -d release/v2.2.3
```

> ℹ️ Después del back-merge, develop y release volverán a tener commits distintos (develop tendrá el merge commit `--no-ff`). Esto es intencional y no requiere corrección.

### 3.2.2 Eliminación del release branch tras aprobación

Una vez que el banco aprueba la versión en DES, el release branch ya cumplió su propósito y se elimina:

```bash
# Eliminar rama local
git branch -d release/v1.2.3

# Eliminar rama remota
git push origin --delete release/v1.2.3
```

A partir de este punto, la versión sigue su curso en manos del banco (DES → PRU → PREPRO → PRO). CEIBA solo interviene nuevamente si se requiere un hotfix.

### 3.3 Promoción DES → PRU (BANCO)

El banco valida en DES y promueve a PRU. CEIBA registra el avance **cuando el banco confirma**:

```bash
# Cuando el banco confirma la promoción a PRU
git checkout pru
git merge --ff-only v1.2.3     # fast-forward desde el tag de release
git tag -a v1.2.3-pru -m "v1.2.3 promovido a PRU"
git push origin pru v1.2.3-pru
```

### 3.4 Promoción PRU → PREPRO (BANCO)

```bash
# Cuando el banco confirma la promoción a PREPRO
git checkout prepro
git merge --ff-only v1.2.3-pru
git tag -a v1.2.3-prepro -m "v1.2.3 promovido a PREPRO"
git push origin prepro v1.2.3-prepro
```

### 3.5 Promoción PREPRO → PRO (BANCO)

```bash
# Cuando el banco confirma la promoción a PRO
git checkout main
git merge --ff-only v1.2.3-prepro
git tag -a v1.2.3-pro -m "v1.2.3 promovido a PRODUCCIÓN"
git push origin main v1.2.3-pro
```

---

## 4. Matriz de Responsabilidades

| Actividad                                         | CEIBA | BANCO |
|---------------------------------------------------|-------|-------|
| Desarrollo y pruebas unitarias                    | ✅    |       |
| Integración en develop + CI                       | ✅    |       |
| Pruebas en ambiente DEVELOP                       | ✅    |       |
| Estabilización del release branch                 | ✅    |       |
| Merge a `des` + tag vX.Y.Z (handoff)             |       | ✅    |
| Entrega formal de artefacto y release notes       | ✅    |       |
| Despliegue en ambiente DES                        |       | ✅    |
| Validación funcional en DES                       |       | ✅    |
| Promoción DES → PRU                               |       | ✅    |
| Pruebas de integración en PRU                     |       | ✅    |
| Promoción PRU → PREPRO                            |       | ✅    |
| Pruebas de aceptación en PREPRO                   |       | ✅    |
| Promoción PREPRO → PRO                            |       | ✅    |
| Pruebas en PRO / Go-Live                          |       | ✅    |
| Registro de tags post-promoción (en repos CEIBA)  | ✅    |       |

---

## 5. Hotfixes

### 5.1 Hotfix en DES (no ha pasado a PRU)

Cuando el bug se detecta en DES y aún no ha sido promovido a PRU, se aplica el fix directamente sobre la rama release viva y se entrega como RC:

```bash
git checkout release/v2.2.3
# aplicar fix
git commit -m "fix: corregir [descripción]"
git push origin release/v2.2.3

# Probar fix en DEVELOP antes de propagar
git checkout -b release/v2.2.3-rc.1 release/v2.2.3
git push origin release/v2.2.3-rc.1
# El pipeline despliega en DEVELOP → validar que el fix funciona

# Back-merge a develop mediante PR (ya validado)
# Crear PR: release/v2.2.3 → develop
# Requiere al menos 1 approval (ver §8)

# El banco mergea PR a des → tag v2.2.3-rc.1 → eliminar RC
git push origin --delete release/v2.2.3-rc.1
git branch -d release/v2.2.3-rc.1
```

### 5.2 Hotfix en PRU, PREPRO o PRO (bug reportado por el banco)

Cuando el banco reporta un bug en un ambiente superior (PRU, PREPRO o PRO), el flujo es:

1. **Analizar el bug desde el tag del ambiente afectado**
2. **Verificar que develop también necesita el fix** (para merge limpio)
3. **Merge a develop primero**
4. **Crear nuevo release** (`vX.Y.Z+1` — incremento de PATCH)
5. **Flujo normal de release:** develop → des → pru → prepro → pro

```bash
# 1. Crear hotfix branch desde el tag del ambiente afectado
git checkout -b hotfix/arreglo-x v2.2.3-pro    # o v2.2.3-pru, v2.2.3-prepro

# 2. Analizar y aplicar el fix
# ... correcciones ...
git commit -m "fix: corregir [descripción]"

# 3. Verificar que develop tiene el problema y necesita el fix
git log develop --oneline | head -10   # confirmar que el bug existe en develop

# 4. Merge a develop PRIMERO mediante PR
# Crear PR: hotfix/arreglo-x → develop
# Requiere al menos 1 approval (ver §8)

# 5. Crear nuevo release desde develop (ya tiene el fix)
git checkout develop
git pull
git checkout -b release/v2.2.4
git push origin release/v2.2.4

# 6. El banco toma release/v2.2.4 y sigue el flujo normal:
#    PR a des → tag v2.2.4 → des → pru → prepro → pro

# 7. Eliminar hotfix branch
git branch -d hotfix/arreglo-x
git push origin --delete hotfix/arreglo-x
```

### 5.3 Principios para hotfixes

1. **Siempre desde el tag del ambiente afectado** — no desde `develop`
2. **Verificar que develop necesita el fix** — antes de crear el nuevo release
3. **Merge a develop primero** — garantiza merge limpio, develop ya tiene el fix cuando se crea el release
4. **Nuevo release con incremento de PATCH** — `v2.2.3` → `v2.2.4`
5. **Flujo completo** — el hotfix pasa por todos los ambientes: develop → des → pru → prepro → pro
6. **No saltar ambientes** — el banco valida en cada paso

---

## 6. Trazabilidad con Tags

### 6.1 Convención de Tags

| Tag                  | Significado                              |
|----------------------|------------------------------------------|
| `v1.2.3`             | Release final entregado a DES / Producción |
| `v1.2.3-rc.1`        | Release candidate 1 — ajuste post-entrega en DES |
| `v1.2.3-rc.2`        | Release candidate 2 — segundo ajuste en DES |
| `v1.2.3-pru`         | Release promovido a PRU                  |
| `v1.2.3-prepro`      | Release promovido a PREPRO               |
| `v1.2.3-pro`         | Release promovido a PRODUCCIÓN           |
| `v1.2.4`             | Hotfix — nuevo release                   |

### 6.2 Estado actual por ambiente

```bash
# Consultar qué versión está en cada ambiente
git tag | sort -V | tail -20

# Ver el estado de cada rama
git log --oneline --decorate des -5
git log --oneline --decorate pru -5
git log --oneline --decorate prepro -5
git log --oneline --decorate main -5
```

### 6.3 Automatización en Pipeline

Cada pipeline de Azure DevOps debe incluir un paso que registre el tag automáticamente al desplegar:

```yaml
- script: |
    TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "sin-tag")
    echo "Versión desplegada: $TAG en ambiente: $(env)"
  displayName: 'Registrar tag de despliegue'
```

---

## 7. Release Notes

Cada entrega a DES debe incluir un release notes con el siguiente formato:

```markdown
# Release v1.2.3 — YYYY-MM-DD

## Cambios desde v1.2.2
- [WA2-xxx] Nueva funcionalidad de simulación de créditos
- [WA2-yyy] Corrección en flujo de autenticación
- [WA2-zzz] Refactor de servicio de notificaciones

## Commits incluidos
  git log v1.2.2..v1.2.3 --oneline --no-merges

## Artefactos
- Imagen Docker: banca/whatsapp-conversacion:v1.2.3
- Pipeline Build: #12345

## Pruebas realizadas
- [x] Pruebas unitarias (100% pasadas)
- [x] Cobertura ≥ 80%
- [x] Pruebas DAST en DEVELOP (0 High/Critical)
- [x] Análisis SonarQube (Quality Gate passed)
```

---

## 8. Políticas de Ramas Protegidas

| Rama      | Protección                                                |
|-----------|-----------------------------------------------------------|
| `develop` | Requiere PR con al menos 1 approval. No push directo.     |
| `des`     | Merge desde release branch. CEIBA entrega, BANCO despliega. |
| `pru`     | Solo acceso BANCO. CEIBA mergea tags post-promoción.      |
| `prepro`  | Solo acceso BANCO.                                        |
| `main`    | Solo acceso BANCO. Protegida con approvals.               |

---

## 9. Escenarios de Excepción

### 9.1 Rollback

Si un release en DES resulta defectuoso:

```bash
git checkout des
git revert v1.2.3
git tag -a v1.2.2+rollback -m "Rollback: des v1.2.3 → v1.2.2"
git push origin des
```

Si el banco reporta un bug en PRU y decide no promover:

```bash
# El banco detiene la promoción. Se aplica hotfix y se re-taggea.
git checkout -b hotfix/pru-fix v1.2.3-pru
# fix → nuevo tag v1.2.4
```

### 9.2 Release salta un ambiente

Si el banco solicita pasar directamente de DES a PREPRO (saltando PRU):

```bash
git checkout prepro
git merge --ff-only v1.2.3
git tag -a v1.2.3-prepro -m "v1.2.3 promovido directo a PREPRO (saltó PRU)"
```

Incluir en el mensaje del tag la razón: `"Promovido directo a PREPRO por solicitud del banco - [motivo]"`.

---

## 10. Checklist de Entrega

CEIBA antes de cada release a DES:

- [ ] Release branch creado o actualizado desde `develop` (ver §3.2)
- [ ] `develop` y `release/vX.Y.Z` apuntan al **mismo commit** (`git rev-parse develop == git rev-parse release/vX.Y.Z`)
- [ ] Version actualizada en artefactos
- [ ] Release notes generados
- [ ] Pruebas unitarias ejecutadas (100% OK)
- [ ] Cobertura ≥ 80% verificada
- [ ] DAST ejecutado (0 High/Critical)
- [ ] SonarQube Quality Gate passed
- [ ] Merge a `des` completado
- [ ] Tag `v1.2.3` creado y pusheado
- [ ] Release notes enviados al banco
