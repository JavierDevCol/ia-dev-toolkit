# Paso 2a — feature/fix → develop (Opción 2a)

**Cuándo:** El cambio NO está en develop todavía y aún no existe release. Sigue el flujo estándar de PR.

**Inputs (pedir/validar antes de empezar):**
- Nombre de la rama `<rama>` (feature o fix).

**Outputs:** PR `<rama> → develop` abierto en ADO + comando de `@env-config-audit` informado. No se crea ninguna rama `release/*` ni se calcula versión (eso es la Opción 1).

**Confirmaciones del usuario:** ✋ OK para crear el PR.

1. **Validar la rama:**
   ```bash
   git fetch origin
   git ls-remote --heads origin <rama>
   git log --oneline origin/develop..origin/<rama>
   ```
   - `ls-remote` sin resultados → **detener**: la rama no existe, o existe solo localmente y no está publicada (publicarla o detener y preguntar).
   - `git log` vacío → **detener**: la rama ya está en develop; sugerir la Opción 1.

2. **env-config-audit:** `@env-config-audit sobre el diff origin/develop...origin/<rama>` (diff de esta fase — ver `SKILL.md` → Skills sugeridas). Sustituir `<rama>` por el nombre real antes de mostrarlo.

3. **Crear PR `<rama> → develop`** (cliente ADO, PR activo), título: `<tipo>: <descripción>` (`feat` si la rama es feature, `fix` si es fix; descripción derivada del nombre de la rama). **Verificación:** el PR queda abierto y su diff coincide con `origin/develop...origin/<rama>`.

4. **Instrucciones al usuario:** aprobar el PR (≥1 approval — develop está protegida: sin push directo). Una vez mergeado, esperar a que el pipeline de develop de ese merge termine OK y luego re-ejecutar la Opción 1 (su paso 1 lo exige).
