# Opción 2b · Paso 1 — Versión base

1. **Versión base (`vBASE`)** — la versión que tiene la falla:

   a. **Versión actual de cada ambiente** (último tag de despliegue de cada uno; la usa el paso 7):
      ```bash
      git fetch origin --tags
      for AMB in DES PRU PRE PRO; do
        echo "$AMB $(git ls-remote --tags origin | grep -oE "v[0-9]+\.[0-9]+\.[0-9]+-$AMB\$" | sort -V | tail -1)"
      done
      ```

   b. **`vBASE`** = versión del ambiente afectado sin el sufijo (ej. `v1.4.0-PRO` → `v1.4.0`). Confirmar que el tag de versión `vBASE` existe en `origin`; si no existe → **detener y reportar**.

   c. ✋ **Confirmar `vBASE` con el usuario**, mostrando la tabla de versiones por ambiente.

---

**Siguiente:** solo con `vBASE` confirmada → cargar `paso_dos.md`. Pregunta ✋ abierta → esperar la respuesta sin cargar nada. Detener → no cargar ningún paso más.
