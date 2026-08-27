# Opción 2c: ajuste RC post-entrega en DES (§3.2.1 del manual)

# Datos de entrada:
# - Versión del release activo (ej. v2.2.3)
# - Rama validada: git branch -a | grep "release/v2.2.3"
# - Descripción del ajuste solicitado por el banco
# - Número de RCs existentes: git tag -l "v2.2.3-rc.*"

# Flujo:

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
