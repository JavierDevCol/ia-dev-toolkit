# Opción 2c: ajuste RC post-entrega en DES
# Detalle de pasos: references/paso_dos_c.md

# Datos de entrada:
# - Versión del release activo (ej. v2.2.3)
# - Rama validada: git branch -a | grep "release/v2.2.3"   (vacío → NO es 2c)
# - Descripción del ajuste solicitado por el banco
# - Número de RCs: git ls-remote --tags origin 'refs/tags/v2.2.3-rc.*'  → N = máximo(rc) + 1

# Flujo:

# 1. Aplicar fix sobre la rama base (release/vX.Y.Z sigue viva)
git fetch origin
git checkout release/v2.2.3 && git pull origin release/v2.2.3
# ... correcciones ...
git add .
git commit -m "fix: <descripción del ajuste>"
git push origin release/v2.2.3

# 2. env-config-audit sobre el diff que entra a des (antes del back-merge)
# @env-config-audit sobre el diff origin/des..release/v2.2.3

# 3. Crear y publicar rama RC efímera para el PR al banco
git checkout -b release/v2.2.3-rc.1 release/v2.2.3
git push origin release/v2.2.3-rc.1

# 4. GATE — validar el fix en DEVELOP (el pipeline despliega la RC).
#    Salvo fixes triviales (typo/config): sin validación NO hay back-merge.

# 5. Back-merge a develop mediante PR (develop está protegida: ≥1 approval, sin push directo)
#    Crear PR: release/v2.2.3 → develop   (≥1 approval, sin push directo)
#    Conflictos → detener y reportar; nunca forzar.

# 6. El banco crea PR release/v2.2.3-rc.1 → des, mergea y taggea v2.2.3-rc.1

# 7. Eliminar rama RC después de que el banco mergea
git push origin --delete release/v2.2.3-rc.1
git branch -d release/v2.2.3-rc.1
# La rama base release/v2.2.3 sigue viva hasta la aprobación final del banco
