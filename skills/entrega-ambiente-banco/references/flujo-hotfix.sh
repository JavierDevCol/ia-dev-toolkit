# Opción 2b: hotfix post-entrega (§5.2 del manual)

# Datos de entrada:
# - Ambiente donde se detectó el bug (PRU / PREPRO / PRO)
# - Versión del release afectado (ej. v2.2.3)
# - Tag validado: git tag -l "v2.2.3-pro" (o -pru, -prepro)
# - Descripción del ajuste

# Flujo:

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
