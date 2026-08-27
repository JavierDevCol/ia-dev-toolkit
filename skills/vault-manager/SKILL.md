---
name: vault-manager
description: Usa esta skill cuando el usuario necesite consultar, listar o gestionar secretos en HashiCorp Vault — ya sea para leer valores, verificar paths, revisar auditoría o ejecutar comandos vault específicos.
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

1. Verificar CLI: `vault --version`
2. Si no está instalado → informar al usuario y detener.

## Implementation

### Autenticación

> **Seguridad:** Nunca pasar credenciales en línea de comandos. El historial de shell y procesos puede exponer passwords.

1. Buscar archivo `.env` en la raíz del proyecto o ruta indicada por el usuario.
2. Leer `VAULT_USER` y `VAULT_PASS` del `.env`.
3. Autenticar usando input interactivo:
   ```bash
   vault login -method=userpass username="$VAULT_USER"
   ```
   Vault solicitará la contraseña de forma interactiva.
4. Alternativa: exportar `VAULT_PASS` como variable de entorno (menos seguro que interactivo):
   ```bash
   export VAULT_PASS
   vault login -method=userpass username="$VAULT_USER" password="$VAULT_PASS"
   ```
5. Si la autenticación falla → informar error y detener.

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
| Login interactivo | `vault login -method=userpass username=USER` |
| Leer secreto | `vault kv get [path]` |
| Listar | `vault kv list [path]` |
| Escribir | `vault kv put [path] clave=valor` |
| Ver logs | `kubectl exec -n middleware [POD] -- tail -20 /vault/logs/audit.log` |

## Common Mistakes

- **Credenciales en línea de comandos:** Nunca usar `password=MI_PASS` directamente. El historial de shell expone la contraseña. Usar siempre input interactivo o variable de entorno.
- **Token expirado:** Si un comando falla con error de autenticación, re-autenticar antes de reintentar.
- **`.env` mal formateado:** Debe ser `VAULT_USER=usuario` y `VAULT_PASS=contraseña` (sin espacios alrededor de `=`).
- **Mostrar VAULT_PASS:** Nunca imprimir la contraseña en pantalla ni en logs.
