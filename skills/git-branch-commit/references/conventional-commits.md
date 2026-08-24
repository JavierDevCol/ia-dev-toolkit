# Conventional Commits — Referencia

## Formato

```
<tipo>[ámbito]: <descripción>

[cuerpo]

[BREAKING CHANGE: ...]
```

## Tipos

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `feat` | Nueva funcionalidad | `feat(auth): add Google OAuth login` |
| `fix` | Corrección de errores | `fix(api): handle timeout on payment` |
| `refactor` | Sin cambio funcional | `refactor(db): extract query builder` |
| `docs` | Documentación | `docs: update README setup` |
| `chore` | Mantenimiento | `chore: bump lodash to 4.17.21` |
| `style` | Formato (no lógica) | `style: fix indentation in auth` |
| `test` | Tests | `test: add unit tests for user service` |
| `perf` | Rendimiento | `perf: cache database queries` |
| `ci` | CI/CD | `ci: add GitHub Actions workflow` |
| `build` | Build/dependencias | `build: migrate from webpack to vite` |
| `revert` | Revertir commit | `revert: undo changes in auth module` |

## BREAKING CHANGE

Si rompe compatibilidad, agregar al inicio del cuerpo:

```
feat(api): change authentication response format

BREAKING CHANGE: /auth/login now returns { token, refreshToken }
instead of { access_token, refresh_token }
```

## Reglas

1. **Imperativo:** "add feature" no "added feature"
2. **Sin punto final**
3. **Máximo 72 caracteres** en primera línea
4. **Ámbito opcional:** `api`, `ui`, `auth`, `db`, `config`
