# Opción 2b · Paso 5 — Push y bloqueo de hotfix/vX.Y.Z

5. **Publicar y bloquear `hotfix/vX.Y.Z`** (✋ OK del usuario) — una sola vez, sobre `<sha>`, con `isLocked = true` inmediatamente después:
   ```bash
   git push origin <sha>:refs/heads/hotfix/vX.Y.Z
   ```
   Bloquear por API REST de ADO. PAT en `.env` de la raíz del proyecto, clave `pat_ado`, con permiso de escritura sobre Code — **nunca imprimirlo** (Regla 7):
   ```bash
   PAT=$(grep -m1 '^pat_ado=' .env | cut -d= -f2-)
   URL="{ado_base}/_apis/git/repositories/{nombre_repo}/refs?filter=heads/hotfix/vX.Y.Z&api-version=7.1"
   curl -s -u ":$PAT" -H "Content-Type: application/json" -X PATCH "$URL" -d '{"isLocked":true}'
   curl -s -u ":$PAT" "$URL" | grep -o '"isLocked":[a-z]*'   # debe ser "isLocked":true
   ```
   **Sin PAT, HTTP distinto de 200 o `isLocked` distinto de `true` → detener y reportar.**
   El push dispara el pipeline (tipo release). La rama no se actualiza ni se desbloquea nunca.

---

**Siguiente:** solo con la rama publicada y `"isLocked":true` verificado → cargar `paso_seis.md`. Cualquier otro resultado → detener; no cargar ningún paso más.
