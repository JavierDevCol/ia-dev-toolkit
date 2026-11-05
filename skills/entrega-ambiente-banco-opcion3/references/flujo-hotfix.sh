# Opción 2b: hotfix post-entrega
# Detalle de pasos: references/paso_dos_b.md

# Datos de entrada:
# - Ambiente donde se detectó el bug (PRU / PREPRO / PRO)
#   sufijo de tag: PRU→-pru, PREPRO→-prepro, PRO→-pro
# - Versión del release afectado (ej. v2.2.3)
# - Descripción del ajuste

# Flujo:

# 1. Validar el tag del ambiente afectado (vacío → detener y preguntar)
git fetch origin --tags
git ls-remote --tags origin 'refs/tags/v2.2.3-pro'   # o -pru, -prepro

# 2. Crear hotfix branch desde el tag del ambiente afectado
#    (si hotfix/arreglo-x ya existe → detener y preguntar; nunca sobrescribir)
git checkout -b hotfix/arreglo-x v2.2.3-pro

# 3. Aplicar el fix
# ... correcciones ...
git add .
git commit -m "fix: <descripción del ajuste>"

# 4. Verificar que develop tiene el problema y necesita el fix
git log develop --oneline | head -10

# 5. env-config-audit sobre el diff del fix (antes del PR)
# @env-config-audit sobre el diff develop..hotfix/arreglo-x

# 6. Merge a develop PRIMERO, mediante PR (develop está protegida: ≥1 approval, sin push directo)
#    Crear PR: hotfix/arreglo-x → develop   (≥1 approval, sin push directo)
#    Conflictos → detener y reportar; nunca forzar.

# 7. Crear nuevo release desde develop (ya tiene el fix) — incremento de PATCH
git checkout develop && git pull
git checkout -b release/v2.2.4
git push origin release/v2.2.4
# Regla de oro: git rev-parse origin/develop == git rev-parse origin/release/v2.2.4

# 8. Release notes desde cero (Regla 5): git log v2.2.3..HEAD --oneline --no-merges

# 9. Eliminar hotfix branch (tras el merge del PR)
git branch -d hotfix/arreglo-x
git push origin --delete hotfix/arreglo-x

# 10. El banco toma release/v2.2.4 y sigue el flujo normal:
#     PR a des → tag v2.2.4 → des → pru → prepro → pro
