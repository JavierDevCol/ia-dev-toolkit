---
name: git-doc-sync
description: >
  Sincronización selectiva de documentación en repositorios Git. Permite elegir
  qué archivos subir (commit/push parcial) desde un inventario de repos, validando
  ramas protegidas. Usa esta skill cuando el usuario quiera subir documentos,
  sincronizar docs con Git, hacer push selectivo, revisar git status de un repo
  de documentación, o gestionar qué archivos commitear. Also triggers on: push
  selected files, sync documentation, selective git commit, upload docs to repo.
compatibility: Requires git, Python 3
---

# Git Documentation Synchronizer

Facilita la subida parcial de documentos (HU, Contextos, Diagramas) permitiendo al usuario separar el "Trabajo en Progreso" de lo "Completado".

## Resolución de rutas

Todos los paths a scripts e `inventory.json` son **relativos al directorio de esta skill**.
Antes de ejecutar cualquier comando, resuelve `SKILL_DIR` — el directorio donde se encuentra este `SKILL.md`.
Usa `SKILL_DIR` como prefijo en todos los comandos:

```bash
# Ejemplo: si la skill está en .github/agents/skills/git-doc-sync/
SKILL_DIR=".github/agents/skills/git-doc-sync"
python3 "$SKILL_DIR/scripts/sync_logic.py" inventory --file "$SKILL_DIR/inventory.json"
```

## Scripts disponibles

- **`scripts/sync_logic.py status`** — Muestra archivos modificados/nuevos/eliminados en formato JSON.
- **`scripts/sync_logic.py sync`** — Ejecuta git add + commit + push para los archivos seleccionados.
- **`scripts/sync_logic.py inventory`** — Lista los repositorios registrados en el inventario.

## Flujo de trabajo

1. **Obtención de ruta del repo — Fuente primaria: `config.yaml`**

   **Primero** intenta leer la ruta desde la configuración central:
   ```
   metodoceiba-vfs:/.ceiba-metodo/metodo-ceiba/config.yaml → campo output_folder
   ```

   **Si `output_folder` se obtiene correctamente:**
   - Extrae el nombre del último segmento de la ruta (ej: `/ruta/a/Doc_BancaPorWhatsapp` → `Doc_BancaPorWhatsapp`).
   - Actualiza `inventory.json` automáticamente con `name` y `path` obtenidos.
   - **Solo pregunta al usuario por las ramas permitidas** si `settings.required_branches` está vacío:
     > "Obtuve la ruta del repo de documentación desde config.yaml: `[output_folder]`. ¿En qué ramas se permite hacer push? (ej: main, develop)"
   - Si las ramas ya están configuradas en `inventory.json`, no preguntes nada — continúa al paso 2.

   **Si NO se puede obtener `output_folder`** (archivo no existe, campo vacío, o error de lectura):
   - Cae al **flujo fallback con `inventory.json`**:
     ```bash
     python3 "$SKILL_DIR/scripts/sync_logic.py" inventory --file "$SKILL_DIR/inventory.json"
     ```
     - Si el inventario tiene repos configurados (con `name`, `path` y `required_branches` válidos), úsalos.
     - Si el inventario está vacío o incompleto, pregunta al usuario CADA campo:
       1. "¿Cuál es el **nombre** del repositorio?"
       2. "¿Cuál es la **ruta absoluta** en tu sistema?"
       3. "¿En qué **ramas** se permite hacer push?"
     - **NO busques repos por tu cuenta. NO asumas rutas.** Espera las respuestas del usuario.

2. **Selección de repo:** Si hay múltiples repos en el inventario, muestra la lista y solicita que elija uno. Si solo hay uno, úsalo directamente.

3. **Validación de rama:** Verifica que la rama actual esté en `settings.required_branches`:
   ```bash
   python3 "$SKILL_DIR/scripts/sync_logic.py" status --path /ruta/al/repo --branches main,develop
   ```
   Si la rama no está permitida, **detente y notifica al usuario**. No continúes.

4. **Análisis de status:** El comando `status` devuelve JSON con los archivos categorizados:
   - `NEW` — archivos untracked
   - `MODIFIED` — archivos modificados
   - `DELETED` — archivos borrados

   Presenta la lista numerada al usuario.

5. **Selección humana:** El usuario indica qué archivos subir (ej: "1, 3"). **No asumas archivos; espera la selección explícita.**

6. **Sincronización:** Ejecuta el push selectivo:
   ```bash
   python3 "$SKILL_DIR/scripts/sync_logic.py" sync --path /ruta/al/repo --files "archivo1.md,archivo2.md" --message "docs: actualización parcial"
   ```
   **Confirma con el usuario antes de ejecutar el push.** Muestra el resumen de lo que se va a subir.

## Gotchas

- **Fuente primaria de rutas es `config.yaml`, no `inventory.json`.** Siempre intenta `config.yaml` primero. Solo usa el flujo manual de `inventory.json` como fallback. Cuando `config.yaml` provee la ruta, actualiza `inventory.json` automáticamente — pero nunca inventes ni busques rutas por tu cuenta.
- **Rutas de scripts:** Los scripts están dentro del directorio de esta skill, NO en la raíz del workspace. Siempre usa la ruta completa relativa al workspace (ej: `.github/agents/skills/git-doc-sync/scripts/sync_logic.py`). Si el comando falla con "No such file", verifica el `SKILL_DIR`.
- La rama actual **debe** estar en `settings.required_branches` del `inventory.json`. Si no lo está, el push fallará. Siempre valida antes del paso 6.
- `inventory.json` contiene rutas absolutas del sistema. Nunca asumas la ruta; léela del inventario.
- El script requiere que el directorio del repo exista y tenga un `.git` inicializado. Si `status` falla con "not a git repository", informa al usuario.
- El push va siempre a `origin`. Si el usuario necesita otro remote, debe indicarlo explícitamente.
- No ejecutes `sync` sin que el usuario haya seleccionado archivos. El staging parcial es el valor central de esta skill.