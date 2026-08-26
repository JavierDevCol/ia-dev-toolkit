---
name: entrega-ambiente-banco
description: >
  Prepara y ejecuta la entrega de releases al banco para el proyecto
  Banca por WhatsApp. Úsala cuando necesites preparar una entrega formal
  al banco, crear un release branch, generar release notes, CONFIG_ENTORNO_PR,
  feature lista para release, ajustar release (RC), hotfix release.
  NOTA: No debes activarte para desarrollo normal de features, solo
  para preparación de entregas formales al banco.
compatibility: Requires BancaPorWhatsApp project context
metadata:
  author: CEIBA DevOps
  version: 1.0.0
---

# Skill: Entrega Ambiente Banco

Orquesta la entrega de releases de CEIBA al banco siguiendo el manual de paso entre ambientes.

## Referencias

- Manual completo: `{file:./references/MANUAL_PASO_AMBIENTES.md}` (usar como fuente de verdad)

---

## Menú Principal

Siempre que se active esta skill, muestra el siguiente menú y espera la selección del usuario:

```
╔══════════════════════════════════════════════════════════╗
║          HANDOFF CEIBA → BANCO                          ║
║                                                        ║
║  ¿Qué tipo de entrega necesitas preparar?               ║
║                                                        ║
║  [1] Entregar release desde DEVELOP                     ║
║      → La feature ya está integrada en develop via PR   ║
║      → Crea release/vX.Y.Z desde develop                ║
║                                                        ║
║  [2] Entregar release desde feature/fix/hotfix          ║
║      → El código NO está en develop o ya hay release    ║
║      → El agente determina el flujo según el caso       ║
║      → Incluye hotfix y ajustes RC en DES              ║
║                                                        ║
╚══════════════════════════════════════════════════════════╝
```

---

## Opción 1: Entregar release desde DEVELOP

**Cuándo:** La feature ya está integrada a develop mediante PR aprobado. Sigue §3.2 del manual.

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

#### Paso 5 — Checklist de entrega (§10 del manual)

Mostrar checklist completo. Los items marcados con ⚠️ no los resuelve esta skill — el usuario debe ejecutar las skills correspondientes por separado:

```
CHECKLIST DE ENTREGA — Handoff vX.Y.Z

[✓] Release branch creado o actualizado desde develop
[✓] develop y release/vX.Y.Z apuntan al mismo commit
[ ] Versión actualizada en artefactos
[✓] Release notes generados
[⚠] Pruebas unitarias ejecutadas (100% OK)
     → Ejecuta /ado-pipeline-analyzer para verificar
[⚠] Cobertura ≥ 80% verificada
     → Ejecuta /ado-pipeline-analyzer para verificar
[⚠] DAST ejecutado (0 High/Critical)
     → Ejecuta /ado-pipeline-analyzer para verificar
[⚠] SonarQube Quality Gate passed
     → Ejecuta /ado-pipeline-analyzer para verificar
[⚠] CONFIG_ENTORNO_PR generado
     → Ejecuta /pr-config-audit sobre diff develop..release/vX.Y.Z
[ ] Artefactos listos para entregar al banco

NOTA: Las skills ´pr-config-audit´ y ´ado-pipeline-analyzer´, se recomienda ejecutar en el mismo chat. 
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
  └── RESUMEN_ENTREGA_release (<nombre_repo>).txt → <ruta-base>/entrega_release/<nombre_repo>/<version>/RESUMEN_ENTREGA_release (<nombre_repo>).txt

📌 Pendientes (ejecutar skills por separado):
  ├── @pr-config-audit        → CONFIG_ENTORNO_PR_{ID}.md
  └── @ado-pipeline-analyzer  → validar build, tests, cobertura, DAST, SonarQube

👉 El banco debe:
  1. Crear PR de release/vX.Y.Z → des
  2. Mergear el PR a des
  3. Taggear vX.Y.Z en des
  4. Desplegar en DES
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

## Opción 2: Entregar release desde feature/fix/hotfix

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
║  [b] hotfix → Bug en PRU/PREPRO/PRO                     ║
║      Merge a develop primero → nuevo release            ║
║      Flujo completo por todos los ambientes             ║
║                                                        ║
║  [c] ajuste RC → Banco pidió cambios en DES             ║
║      Fix sobre release vivo → RC efímera → PR a des     ║
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

2. **Informar sobre CONFIG_ENTORNO_PR:**
   - Indicar al usuario: "Si quieres generar el CONFIG_ENTORNO_PR del diff de tu rama, ejecuta `@pr-config-audit` por separado con el diff develop..<rama>"

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
        y selecciona la Opción 1 "Entregar release desde DEVELOP"
        usando la versión vX.Y.Z
     3. Opcional: ejecuta @pr-config-audit sobre el diff develop..<rama>
        para adelantar el CONFIG_ENTORNO_PR
   ```

---

### Opción 2b: hotfix post-entrega (§5.2 del manual)

#### Datos de entrada
1. Preguntar: "¿En qué ambiente se detectó el bug?" (PRU / PREPRO / PRO)
2. Preguntar: "¿Cuál es la versión del release afectado?" (ej. v2.2.3)
3. Validar que el tag existe: `git tag -l "v2.2.3-pro"` (o `-pru`, `-prepro`)
4. Preguntar: "¿Qué ajuste necesita?" — registrar descripción textual

#### Flujo

```bash
# 1. Crear hotfix branch desde el tag del ambiente afectado
git checkout -b hotfix/arreglo-x v2.2.3-pro

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
  • Hotfix branch: hotfix/arreglo-x (desde tag v2.2.3-pro)
  • develop tiene el fix via merge (--no-ff)
  • Nuevo release: release/v2.2.4 (push a origin)

📌 Flujo completo:
  1. Validar que develop tiene el fix ✅
  2. El banco toma release/v2.2.4
  3. Crear PR release/v2.2.4 → des
  4. Mergear → tag v2.2.4 en des
  5. Promoción: des → pru → prepro → pro

⚠️ Notas:
  • El hotfix pasa por TODOS los ambientes (política del banco)
  • develop y release/v2.2.4 apuntan al mismo commit (merge limpio)
  • Si hay cambios de config, ejecuta @pr-config-audit
```

Guardar el resumen en:
```
<ruta-base>/entrega_release/<nombre_repo>/v2.2.4/RESUMEN_ENTREGA_hotfix (<nombre_repo>).txt
```

---

### Opción 2c: ajuste RC post-entrega en DES (§3.2.1 del manual)

**Cuándo:** El banco solicitó cambios tras validar en DES. El release ya fue entregado (vX.Y.Z existe).

#### Datos de entrada
1. Preguntar: "¿Cuál es la versión del release activo?" (ej. v2.2.3)
2. Validar que la rama existe: `git branch -a | grep "release/v2.2.3"`
3. Preguntar: "¿Qué ajuste solicitó el banco?" — registrar descripción textual
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

# 3. Crear rama RC efímera para el PR al banco
git checkout -b release/v2.2.3-rc.1 release/v2.2.3
git push origin release/v2.2.3-rc.1

# 4. El banco crea PR release/v2.2.3-rc.1 → des, mergea y taggea v2.2.3-rc.1

# 5. Eliminar rama RC después de que el banco mergea
git push origin --delete release/v2.2.3-rc.1
git branch -d release/v2.2.3-rc.1
```

#### Resumen
```
✅ Ajuste RC preparado.

📦 Cambios:
  • release/v2.2.3 actualizado con el fix (rama base sigue viva)
  • develop tiene el fix via back-merge (--no-ff)
  • Rama efímera: release/v2.2.3-rc.1 (PR a des)

📌 El banco debe:
  1. Crear PR release/v2.2.3-rc.1 → des
  2. Mergear → tag v2.2.3-rc.1 en des
  3. Validar en DES
  4. Si aprueba → tag v2.2.3 final (sin RC) → promover a PRU

⚠️ Notas:
  • La rama release/v2.2.3 permanece viva durante el ciclo RC
  • La rama RC es efímera — se elimina después del merge a des
  • Si hay más ajustes, se repite el flujo con rc.2, rc.3, etc.
  • develop y release/v2.2.3 están en commits distintos (esperado según §3.2.1)
  • Si hay cambios de config, ejecuta @pr-config-audit
```

Guardar el resumen en:
```
<ruta-base>/entrega_release/<nombre_repo>/v2.2.3/RESUMEN_ENTREGA_rc (<nombre_repo>).txt
```

---

## Reglas obligatorias

1. **Regla de oro:** develop y release/vX.Y.Z deben apuntar al mismo commit antes del handoff. Usar siempre `--ff-only`.
2. **Versionamiento semántico:** vMAJOR.MINOR.PATCH. Validar formato.
3. **Ajustes en DES:** usar RC — `release/vX.Y.Z-rc.N`. Ramas RC efímeras.
4. **Hotfixes:** incremento de PATCH — `vX.Y.Z` → `vX.Y.Z+1`. Merge a develop primero, nuevo release, flujo completo por todos los ambientes.
5. **release-notes.md se genera desde cero** en cada release — no se actualiza incrementalmente.
6. **El PR a des lo crea el banco, no CEIBA.** El agente solo prepara la rama y artefactos.
7. **No exponer tokens ni contraseñas** en ningún artefacto generado.
8. **Si `--ff-only` falla:** detener y remitir al usuario a §3.2.1 del manual.
9. **El release branch permanece vivo** durante validación del banco y ciclo RC. No eliminarlo hasta aprobación final.
10. **Hotfix merge a develop primero** — garantiza merge limpio antes de crear el nuevo release.

## Skills complementarias (NO las ejecuta esta skill)

Esta skill NO ejecuta automáticamente estas skills. Solo informa al usuario que puede ejecutarlas manualmente en el mismo chat del handoff ceiba si lo necesita:

| Skill | Qué hace | Cuándo ejecutarla |
|-------|----------|-------------------|
| `pr-config-audit` | Genera CONFIG_ENTORNO_PR_*.md analizando el diff | Opción 1 (paso 5 del checklist), Opción 2a, Opción 2b, Opción 2c |
| `ado-pipeline-analyzer` | Valida build, tests, cobertura, DAST, SonarQube | Opción 1 (paso 5 del checklist) |

## Gotchas

- **develop y release deben coincidir:** Si git merge --ff-only falla, es porque release tiene commits propios. No forzar merge.
- **El tag vX.Y.Z lo crea el banco en des:** CEIBA no crea tags. Solo crea la rama release.
- **Hotfix incrementa PATCH:** Los hotfixes crean un nuevo release vX.Y.Z+1. No se mantiene la versión.
- **Hotfix merge a develop primero:** No mergear a main/des directamente. El flujo es develop → des → pru → prepro → pro.
- **RC branches son efímeras:** Se crean para el PR a des, se eliminan después del merge. La rama base release/vX.Y.Z sigue viva.
- **PR a develop protegida:** Si el push a develop falla, crear PR de release/vX.Y.Z → develop en lugar de push directo.
- **Si la feature branch se llama distinto:** Aceptar cualquier nombre de rama, no solo feature/WA2-xxx.
- **CONFIG_ENTORNO_PR va por separado:** Esta skill no lo genera. El usuario debe ejecutar `pr-config-audit` manualmente.
