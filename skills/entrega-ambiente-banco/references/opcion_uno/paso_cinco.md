# Opción 1 · Paso 5 — Crear y bloquear release/vX.Y.Z

5. **Crear `release/vX.Y.Z` y bloquearla** (✋ OK del usuario) — una sola vez, directamente sobre `<sha>`, y con `isLocked = true` inmediatamente después:
   ```bash
   git push origin <sha>:refs/heads/release/vX.Y.Z
   ```
   Bloquear por API REST de ADO (`az` CLI no está disponible). PAT en la variable de entorno `PAT_AZURE`, con permiso de escritura sobre Code — **nunca imprimirlo** (Regla 7):
   ```bash
   [ -n "$PAT_AZURE" ] || { echo "Falta PAT_AZURE: export PAT_AZURE=... en ~/.zshrc y reiniciar la terminal"; exit 1; }
   URL="{ado_base}/_apis/git/repositories/{nombre_repo}/refs?filter=heads/release/vX.Y.Z&api-version=7.1"
   curl -s -u ":$PAT_AZURE" -H "Content-Type: application/json" -X PATCH "$URL" -d '{"isLocked":true}'
   curl -s -u ":$PAT_AZURE" "$URL" | grep -o '"isLocked":[a-z]*'   # debe ser "isLocked":true
   ```
   El bloqueo impide cualquier commit posterior: lo que se compila es exactamente `<sha>`. **Sin PAT, HTTP distinto de 200 o `isLocked` distinto de `true` → detener y reportar**; no continuar con una rama abierta.
   El push dispara el pipeline de release. La rama no se actualiza ni se desbloquea nunca: si después hace falta un cambio, es una versión nueva (Regla 1).

---

**Siguiente:** solo con la rama creada y `"isLocked":true` verificado → cargar `paso_seis.md`. Cualquier otro resultado → detener; no cargar ningún paso más.
