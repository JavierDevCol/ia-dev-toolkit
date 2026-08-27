---
name: handoff-release
description: >
  Usa esta skill cuando necesites crear release branches, generar release
  notes, hacer handoff entre equipos, gestionar hotfixes o ajustes RC
  para cualquier proyecto.
compatibility: Requires git
metadata:
  author: CEIBA DevOps
  version: 1.0.0
---

# Skill: Handoff Release

Orquesta la entrega de releases para cualquier proyecto siguiendo buenas prácticas de GitFlow.

---

## Convenciones de la skill

Buscar `memory_skill.json` con `glob **/memory_skill.json`. Si no existe, crear en `skills/memory_skill.json` (al mismo nivel que las carpetas de skills). Leer sección `[handoff-release]` del archivo. Si campos son `null`, usar los defaults indicados.

### Configuración (`config`)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `environments.dev` | `DEV` | Nombre ambiente desarrollo |
| `environments.staging` | `STAGING` | Nombre ambiente staging |
| `environments.prod` | `PROD` | Nombre ambiente producción |
| `roles.preparer` | `Equipo Dev` | Quién prepara releases |
| `roles.deployer` | `Equipo Ops` | Quién despliega |
| `branch_format` | `release/vX.Y.Z` | Formato ramas release |
| `tag_format` | `vX.Y.Z-{env}` | Formato tags |
| `output_path` | `null` | Ruta base para artefactos |

### Memoria (`memory`)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `last_release` | `null` | Última versión release |
| `output_base_path` | `null` | Ruta base para guardar artefactos |

---

## Menú Principal

Siempre que se active esta skill, muestra el siguiente menú y espera la selección del usuario:

```
╔══════════════════════════════════════════════════════════╗
║          HANDOFF RELEASE — Gestión de Entregas          ║
║                                                        ║
║  ¿Qué tipo de entrega necesitas preparar?               ║
║                                                        ║
║  [1] Release desde develop                              ║
║      → La feature ya está integrada en develop          ║
║      → Crea release branch desde develop                ║
║                                                        ║
║  [2] Release desde feature/fix/hotfix                   ║
║      → El código NO está en develop                     ║
║      → Incluye hotfix y ajustes RC                      ║
║                                                        ║
║  [3] Configurar ambientes y naming                      ║
║      → Personalizar nombres de ambientes                ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
```

---

## Opción 1: Release desde DEVELOP

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado.

### Pasos

#### Paso 1 — Verificar develop
1. `git fetch origin`
2. Verificar que `develop` existe y está actualizada
3. Mostrar último commit (hash, mensaje, autor, fecha)
4. Preguntar al usuario: "¿El pipeline de develop pasó correctamente?"
   - Si responde que no o no sabe → detener, indicar que revise el pipeline primero

#### Paso 2 — Generar release notes
1. `git checkout develop && git pull`
2. Obtener tag anterior: `git tag --sort=-version:refname | head -5` para identificar el último tag semver.
3. Generar release notes:
   ```bash
   git log <TAG_ANTERIOR>..HEAD --oneline --no-merges > release-notes.md
   ```
   Si no hay tag anterior, usar `git log --oneline --no-merges > release-notes.md`.
4. Obtener el nombre del repo desde el remoto: `basename $(git remote get-url origin) .git`.
5. Preguntar al usuario la ruta base donde guardar (ej. `../documentacion`, `/ruta/completa`). Sobre esa ruta, construir y crear la carpeta `entrega_release/{nombre_repo}/{release_version}/` y mover `release-notes.md` allí.

#### Paso 3 — Crear/actualizar release/vX.Y.Z
1. Preguntar: "¿Qué versión corresponde a este release?" (formato: vMAJOR.MINOR.PATCH)
2. Validar que el tag no exista ya: `git ls-remote --tags origin vX.Y.Z`
   - Si el tag ya existe → error. Detener.
3. Buscar si release/vX.Y.Z existe:
    ```bash
    git branch -a | grep "release/vX.Y.Z"
    ```
    - **CASO A — No existe:**
      ```bash
      git checkout develop && git pull
      git checkout -b release/vX.Y.Z
      ```
    - **CASO B — Ya existe (ff-only):**
      ```bash
      git checkout release/vX.Y.Z && git pull origin release/vX.Y.Z
      git merge --ff-only develop
      ```
    - Si `--ff-only` falla → error. Detener.
4. Hacer push de la rama release:
   ```bash
   git push origin release/vX.Y.Z
   ```

#### Paso 4 — Validar mismo commit
```bash
git rev-parse develop
git rev-parse release/vX.Y.Z
```
- Si NO coinciden → error. Detener.

#### Paso 5 — Checklist de entrega

Mostrar checklist completo. Los items marcados con ⚠️ no los resuelve esta skill — el usuario debe ejecutar las skills correspondientes por separado:

```
CHECKLIST DE ENTREGA — Handoff vX.Y.Z

[✓] Release branch creado o actualizado desde develop
[✓] develop y release/vX.Y.Z apuntan al mismo commit
[ ] Versión actualizada en artefactos
[✓] Release notes generados
[⚠] Pruebas unitarias ejecutadas (100% OK)
     → Verificar pipeline de develop
[⚠] Cobertura ≥ 80% verificada
     → Verificar pipeline de develop
[⚠] Configuración auditada
     → Ejecuta @pr-config-audit sobre diff develop..release/vX.Y.Z
[ ] Artefactos listos para entregar
```

Preguntar al usuario: "¿Quieres continuar o revisar algo antes del resumen final?"
- [C] Continuar  [R] Revisar  [A] Abortar

#### Paso 6 — Resumen final

Mostrar al usuario el resumen y simultáneamente guardarlo en un archivo `.txt` en la misma carpeta de la entrega:

```
═══════════════════════════════════════════════════════════
 RESUMEN FINAL — Handoff vX.Y.Z
═══════════════════════════════════════════════════════════

✅ Handoff preparado.

📦 Artefactos generados por esta skill:
  ├── Rama:        release/vX.Y.Z (push a origin)
  ├── release-notes.md → <ruta-base>/entrega_release/<nombre_repo>/<version>/release-notes.md
  └── RESUMEN_ENTREGA_release (<nombre_repo>).txt → <ruta-base>/entrega_release/<nombre_repo>/<version>/

📌 Pendientes (ejecutar skills por separado):
  └── @pr-config-audit → CONFIG-ENTORNO-PR_{ID}.md

👉 El equipo deployer debe:
  1. Crear PR de release/vX.Y.Z → staging
  2. Mergear el PR a staging
  3. Taggear vX.Y.Z en staging
  4. Desplegar en STAGING
```

1. Mostrar el resumen anterior en pantalla.
2. Construir la ruta de destino usando la misma `<ruta-base>`, `<nombre_repo>` y `<version>` del Paso 2.
3. Guardar el contenido exacto del resumen en:
   ```
   <ruta-base>/entrega_release/<nombre_repo>/<version>/RESUMEN_ENTREGA_release (<nombre_repo>).txt
   ```
   El archivo `.txt` debe contener el resumen exactamente igual a como se muestra en pantalla, incluyendo los bordes `═`.
4. Confirmar al usuario: `📄 Resumen guardado en: <ruta>/RESUMEN_ENTREGA_release (<nombre_repo>).txt`

---

## Opción 2: Release desde feature/fix/hotfix

**Cuándo:** El código aún no está en develop o ya existe un release previo con ajustes solicitados.

Al seleccionar, mostrar sub-menú:

```
╔══════════════════════════════════════════════════════════╗
║  ¿Cuál es el origen del cambio?                          ║
║                                                        ║
║  [a] feature/fix → No está en develop                   ║
║      Crea PR feature → develop                          ║
║      Al aprobarse, usar Opción 1                        ║
║                                                        ║
║  [b] hotfix → Bug en staging/producción                 ║
║      Merge a develop primero → nuevo release            ║
║      Flujo completo por todos los ambientes             ║
║                                                        ║
║  [c] ajuste RC → Cambios solicitados en staging         ║
║      Fix sobre release vivo → RC efímera → PR a staging ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
```

---

### Opción 2a: feature/fix → develop

#### Pasos

1. **Datos de entrada:**
   - Preguntar: "¿Cuál es el nombre de tu rama?"
   - Preguntar: "¿Qué versión tendrá el release?" (formato: vMAJOR.MINOR.PATCH)
   - Validar que la rama existe: `git fetch origin && git branch -a | grep "rama"`
   - Si no existe → error. Detener.

2. **Informar sobre configuración:**
   - Indicar al usuario: "Si quieres generar el documento de configuración del diff de tu rama, ejecuta `@pr-config-audit` por separado con el diff develop..<rama>"

3. **Crear PR a develop:**
   - Crear PR desde `<rama>` → `develop`
   - Título sugerido: "Release vX.Y.Z — <descripción breve>"
   - Descripción: incluir referencia a release/vX.Y.Z
   - Mostrar link al PR creado

4. **Instrucciones:**
   ```
   📌 Instrucciones para continuar:
     1. Solicita la aprobación del PR #{ID}
     2. Una vez mergeado a develop, ejecuta NUEVAMENTE este agente
        y selecciona la Opción 1 "Release desde DEVELOP"
        usando la versión vX.Y.Z
     3. Opcional: ejecuta @pr-config-audit sobre el diff develop..<rama>
        para adelantar el documento de configuración
   ```

---

### Opción 2b: hotfix post-entrega

#### Datos de entrada
1. Preguntar: "¿En qué ambiente se detectó el bug?" (STAGING / PROD)
2. Preguntar: "¿Cuál es la versión del release afectado?" (ej. v2.2.3)
3. Validar que el tag existe: `git tag -l "v2.2.3-prod"` (o `-staging`)
4. Preguntar: "¿Qué ajuste necesita?" — registrar descripción textual

#### Flujo

```bash
# 1. Crear hotfix branch desde el tag del ambiente afectado
git checkout -b hotfix/arreglo-x v2.2.3-prod

# 2. Aplicar el fix
# ... correcciones ...
git add .
git commit -m "fix: <descripción del ajuste>"

# 3. Verificar que develop tiene el problema
git log develop --oneline | head -10

# 4. Merge a develop PRIMERO (merge limpio)
git checkout develop
git merge --no-ff hotfix/arreglo-x
git push origin develop   # PR si develop está protegida

# 5. Crear nuevo release desde develop (ya tiene el fix)
git checkout develop && git pull
git checkout -b release/v2.2.4
git push origin release/v2.2.4

# 6. Eliminar hotfix branch
git branch -d hotfix/arreglo-x
git push origin --delete hotfix/arreglo-x
```

#### Resumen
```
✅ Hotfix integrado y nuevo release creado.

📦 Cambios:
  • Hotfix branch: hotfix/arreglo-x (desde tag v2.2.3-prod)
  • develop tiene el fix via merge (--no-ff)
  • Nuevo release: release/v2.2.4 (push a origin)

📌 Flujo completo:
  1. Validar que develop tiene el fix ✅
  2. El equipo deployer toma release/v2.2.4
  3. Crear PR release/v2.2.4 → staging
  4. Mergear → tag v2.2.4 en staging
  5. Promoción: staging → production

⚠️ Notas:
  • El hotfix pasa por TODOS los ambientes
  • develop y release/v2.2.4 apuntan al mismo commit (merge limpio)
  • Si hay cambios de config, ejecuta @pr-config-audit
```

Guardar el resumen en:
```
<ruta-base>/entrega_release/<nombre_repo>/v2.2.4/RESUMEN_ENTREGA_hotfix (<nombre_repo>).txt
```

---

### Opción 2c: ajuste RC post-entrega en staging

**Cuándo:** Se solicitaron cambios tras validar en staging. El release ya fue entregado (vX.Y.Z existe).

#### Datos de entrada
1. Preguntar: "¿Cuál es la versión del release activo?" (ej. v2.2.3)
2. Validar que la rama existe: `git branch -a | grep "release/v2.2.3"`
3. Preguntar: "¿Qué ajuste se solicitó?" — registrar descripción textual
4. Preguntar: "¿Cuántos RCs existen ya?" — para determinar el número N (consultar `git tag -l "v2.2.3-rc.*"`)

#### Flujo

```bash
# 1. Aplicar fix sobre la rama base (release/vX.Y.Z sigue viva)
git checkout release/v2.2.3 && git pull origin release/v2.2.3
# ... correcciones ...
git add .
git commit -m "fix: <descripción del ajuste>"
git push origin release/v2.2.3

# 2. Back-merge a develop
git checkout develop
git merge --no-ff release/v2.2.3
git push origin develop   # PR si develop está protegida

# 3. Crear rama RC efímera para el PR
git checkout -b release/v2.2.3-rc.1 release/v2.2.3
git push origin release/v2.2.3-rc.1

# 4. El equipo deployer crea PR release/v2.2.3-rc.1 → staging, mergea y taggea v2.2.3-rc.1

# 5. Eliminar rama RC después de que se mergea
git push origin --delete release/v2.2.3-rc.1
git branch -d release/v2.2.3-rc.1
```

#### Resumen
```
✅ Ajuste RC preparado.

📦 Cambios:
  • release/v2.2.3 actualizado con el fix (rama base sigue viva)
  • develop tiene el fix via back-merge (--no-ff)
  • Rama efímera: release/v2.2.3-rc.1 (PR a staging)

📌 El equipo deployer debe:
  1. Crear PR release/v2.2.3-rc.1 → staging
  2. Mergear → tag v2.2.3-rc.1 en staging
  3. Validar en staging
  4. Si aprueba → tag v2.2.3 final (sin RC) → promover a production

⚠️ Notas:
  • La rama release/v2.2.3 permanece viva durante el ciclo RC
  • La rama RC es efímera — se elimina después del merge a staging
  • Si hay más ajustes, se repite el flujo con rc.2, rc.3, etc.
  • develop y release/v2.2.3 están en commits distintos (esperado)
  • Si hay cambios de config, ejecuta @pr-config-audit
```

Guardar el resumen en:
```
<ruta-base>/entrega_release/<nombre_repo>/v2.2.3/RESUMEN_ENTREGA_rc (<nombre_repo>).txt
```

---

## Opción 3: Configurar ambientes y naming

Permite personalizar los nombres de ambientes, responsables y formatos.

### Flujo

1. **Mostrar configuración actual:**
   ```
   CONFIGURACIÓN ACTUAL

   Ambientes:
     • DEV:     {config.environments.dev}
     • STAGING: {config.environments.staging}
     • PROD:    {config.environments.prod}

   Responsables:
     • Preparer: {config.roles.preparer}
     • Deployer: {config.roles.deployer}

   Formatos:
     • Ramas: {config.branch_format}
     • Tags:  {config.tag_format}
   ```

2. **Preguntar qué cambiar:**
   - [E] Editar ambientes
   - [R] Editar responsables
   - [F] Editar formatos
   - [G] Guardar y salir
   - [C] Cancelar

3. **Guardar cambios** en `memory_skill.json` → sección `[handoff-release].config`

---

## Reglas obligatorias

1. **Regla de oro:** develop y release/vX.Y.Z deben apuntar al mismo commit antes del handoff. Usar siempre `--ff-only`.
2. **Versionamiento semántico:** vMAJOR.MINOR.PATCH. Validar formato.
3. **Ajustes en staging:** usar RC — `release/vX.Y.Z-rc.N`. Ramas RC efímeras.
4. **Hotfixes:** incremento de PATCH — `vX.Y.Z` → `vX.Y.Z+1`. Merge a develop primero, nuevo release, flujo completo por todos los ambientes.
5. **release-notes.md se genera desde cero** en cada release — no se actualiza incrementalmente.
6. **El PR a staging lo crea el equipo deployer, no el preparador.** Esta skill solo prepara la rama y artefactos.
7. **No exponer tokens ni contraseñas** en ningún artefacto generado.
8. **Si `--ff-only` falla:** detener y revisar por qué release tiene commits propios.
9. **El release branch permanece vivo** durante validación en staging y ciclo RC. No eliminarlo hasta aprobación final.
10. **Hotfix merge a develop primero** — garantiza merge limpio antes de crear el nuevo release.

## Skills complementarias (NO las ejecuta esta skill)

Esta skill NO ejecuta automáticamente estas skills. Solo informa al usuario que puede ejecutarlas manualmente si las tiene disponibles:

| Skill | Qué hace | Cuándo ejecutarla |
|-------|----------|-------------------|
| `pr-config-audit` | Audita configuración de variables, colas, secretos | Opción 1 (checklist), Opción 2a, Opción 2b, Opción 2c |

## Gotchas

- **develop y release deben coincidir:** Si git merge --ff-only falla, es porque release tiene commits propios. No forzar merge.
- **El tag vX.Y.Z lo crea el equipo deployer:** Esta skill no crea tags. Solo crea la rama release.
- **Hotfix incrementa PATCH:** Los hotfixes crean un nuevo release vX.Y.Z+1. No se mantiene la versión.
- **Hotfix merge a develop primero:** No mergear a staging/production directamente. El flujo es develop → staging → production.
- **RC branches son efímeras:** Se crean para el PR a staging, se eliminan después del merge. La rama base release/vX.Y.Z sigue viva.
- **PR a develop protegida:** Si el push a develop falla, crear PR de release/vX.Y.Z → develop en lugar de push directo.
- **Si la feature branch se llama distinto:** Aceptar cualquier nombre de rama.
- **pr-config-audit va por separado:** Esta skill no lo ejecuta. El usuario debe ejecutar `pr-config-audit` manualmente.
