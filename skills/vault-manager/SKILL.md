---
name: vault-manager
description: Usa esta skill cuando el usuario necesite consultar, listar o gestionar secretos en HashiCorp Vault — ya sea para leer valores, verificar paths, revisar auditoría o ejecutar comandos vault específicos.
ready: true
---

# Vault Manager

## Overview

Gestiona operaciones sobre HashiCorp Vault: autenticación, lectura/escritura de secretos, y revisión de logs de auditoría.

## When to Use

- Consultar secretos en Vault (`vault kv get`, `vault kv list`)
- Verificar o auditar acceso a secretos
- Ejecutar comandos vault específicos solicitados por el usuario

**Cuándo NO usar:**
- Gestión de secretos en Azure Key Vault u otro proveedor
- Configuración de Vault (setup del servidor, policies, auth methods)
- Rotación automatizada de secretos

## Prerequisites

1. Verificar CLI: `vault --version`. Si no está instalado → informar al usuario y detener.
2. Verificar que `VAULT_ADDR` esté en el entorno — **siempre requerida**, sin importar el método de autenticación. Si falta, ver paso 2 de Autenticación.

## Implementation

### Autenticación

> **Seguridad:** Las credenciales viven **solo en variables de entorno del proceso**, nunca en un archivo (`.env` u otro) ni en el chat. El agente verifica que existan — nunca pide su valor por chat, nunca lo escribe en un comando ni lo imprime. Si el usuario las pega en el chat igual, no repetirlas en la respuesta.

1. **Verificar variables de entorno** (nunca imprimir sus valores, solo confirmar presencia con algo como `[ -n "$VAULT_TOKEN" ] && echo set`):
   - `VAULT_ADDR` — siempre requerida.
   - Método preferido — `VAULT_TOKEN`.
   - Método alternativo — `VAULT_USER` + `VAULT_PASS` (solo si no hay `VAULT_TOKEN`).
2. **Si falta `VAULT_ADDR`, o no hay ninguna combinación de auth completa:** decirle al usuario exactamente qué falta y darle el/los comando(s) `export` como plantilla (sin valor), para que los ejecute él mismo en su terminal:
   ```bash
   export VAULT_ADDR="https://vault.tuempresa.com:8200"
   export VAULT_TOKEN="tu-token"
   # — o, si el método es userpass —
   export VAULT_USER="tu-usuario"
   export VAULT_PASS="tu-password"
   ```
   Pedirle que confirme cuando estén exportadas, y volver al paso 1.
3. **Autenticar según lo disponible** (token tiene prioridad — no requiere `vault login`):
   - **Token:** usar directo. Validar con `vault token lookup` (confirma validez, no expone el valor).
   - **Userpass:** `vault login -method=userpass username="$VAULT_USER" password=- <<< "$VAULT_PASS"` — **nunca** `password="$VAULT_PASS"` como argumento expandido: el shell lo vuelca en texto plano al `argv` del proceso, visible vía `ps aux`/`/proc/[pid]/cmdline` mientras corre, igual de expuesto que escribir la contraseña literal.
4. Si la autenticación falla → informar error y detener.

### Comandos comunes

| Operación | Comando |
|-----------|---------|
| Leer secreto | `vault kv get [path]` |
| Listar secretos | `vault kv list [path]` |
| Escribir secreto | `vault kv put [path] clave=valor` |

### Logs / Auditoría

Si el usuario pide logs de Vault:
```bash
kubectl exec -n middleware [NOMBRE_POD] -- tail -20 /vault/logs/audit.log
```
> Obtener el pod real con: `kubectl get pods -n middleware | grep vault`

Pedir al usuario que copie el output. Cada entrada contiene: `remote_address`, `display_name`, `policies`, `operation`, `path`, `timestamp`.

## Quick Reference

| Tarea | Comando / Acción |
|-------|-----------------|
| Verificar CLI | `vault --version` |
| Verificar token existente | `vault token lookup` |
| Login interactivo | `vault login -method=userpass username=USER` |
| Login no interactivo | `vault login -method=userpass username="$VAULT_USER" password=- <<< "$VAULT_PASS"` |
| Leer secreto | `vault kv get [path]` |
| Listar | `vault kv list [path]` |
| Escribir | `vault kv put [path] clave=valor` |
| Ver logs | `kubectl exec -n middleware [POD] -- tail -20 /vault/logs/audit.log` |

## Common Mistakes

- **Credenciales en línea de comandos:** Nunca usar `password=MI_PASS` ni `password="$VAULT_PASS"` como argumento — en ambos casos el shell deja el valor en texto plano en el `argv` del proceso (visible vía `ps aux`/`/proc/[pid]/cmdline`), no solo en el historial. Usar input interactivo o `password=- <<< "$VAULT_PASS"` (stdin).
- **Token expirado:** Si un comando falla con error de autenticación, re-autenticar antes de reintentar.
- **`VAULT_ADDR` no seteada:** `vault` cae por defecto a `https://127.0.0.1:8200` sin avisar — falla con "connection refused" sin explicar por qué. Verificarla siempre, incluso si ya hay token o userpass.
- **Usar userpass habiendo `VAULT_TOKEN`:** El token tiene prioridad — no pedir/usar usuario y contraseña si ya hay un token en el entorno.
- **Pedir o mostrar credenciales:** Nunca preguntar "¿cuál es tu contraseña/token?" por chat, ni escribir su valor en un comando, ni imprimirlo en pantalla o logs. Solo verificar que la variable de entorno exista.
