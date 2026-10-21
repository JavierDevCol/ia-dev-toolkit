# Paso 2a — feature/fix → develop (Opción 2a)

**Cuándo:** El cambio NO está en develop todavía y aún no existe release. Sigue el flujo estándar de PR.

**Inputs (pedir/validar antes de empezar):**
- Nombre de la rama `<rama>` (feature o fix).
- Versión de la entrega `vX.Y.Z` — validar formato semver (Regla 2).

**Outputs:** PR `<rama> → develop` abierto en ADO + comando de `@env-config-audit` informado. No se crea ninguna rama `release/*` (eso es la Opción 1).

**Confirmaciones del usuario:** ✋ versión antes del paso 2 · ✋ OK para crear el PR.

1. **Validar la rama:**
   ```bash
   git fetch origin
   git branch -a | grep <rama>
   git ls-remote --heads origin <rama>
   ```
   Sin resultados → **detener**: la rama no existe, o existe solo localmente y no está publicada (publicarla o detener y preguntar).

2. **env-config-audit:** `@env-config-audit sobre el diff develop..<rama>` (diff de esta fase — ver `SKILL.md` → Skills sugeridas). Sustituir `<rama>` por el nombre real antes de mostrarlo.

3. **Crear PR `<rama> → develop`** (cliente ADO), título sugerido: "Release vX.Y.Z — <descripción>". **Verificación:** el PR queda abierto y su diff coincide con `develop..<rama>`.

4. **Instrucciones al usuario:** aprobar el PR (≥1 approval — develop está protegida: sin push directo) y, una vez mergeado, re-ejecutar la Opción 1.
