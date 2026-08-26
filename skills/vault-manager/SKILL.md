---
name: vault-manager
description: >
  Gestiona HashiCorp Vault mediante CLI. Autentica con userpass usando
  VAULT_USER y VAULT_PASS desde un .env, y ejecuta cualquier comando
  vault que el usuario solicite (leer/escribir secretos, listar paths,
  etc.). Usa esta skill cuando el usuario mencione vault, secretos,
  credenciales, tokens, o quiera consultar/administrar Vault.
  Also triggers on: vault secrets, read secret, vault login, vault
  commands, hashicorp vault.
compatibility: Requires HashiCorp Vault CLI, kubectl
---
## Prerequisitos
1. Verificar que vault CLI esté instalado: `vault --version`
2. Si no está instalado: informar al usuario y detener.

## Autenticación
1. Buscar archivo .env en la raíz del proyecto o ruta indicada por el usuario.
2. Leer VAULT_USER y VAULT_PASS del .env.
3. Autenticar: `vault login -method=userpass username=VAULT_USER password=VAULT_PASS`
4. Si la autenticación falla: informar error y detener.

## Logs / Auditoría
Si el usuario pide logs de vault, auditoría, o audit:
- Indicar que ejecute manualmente en el pod (reemplazar [NOMBRE_POD] con el pod real de vault):
  ```
  kubectl exec -n middleware [NOMBRE_POD] -- tail -20 /vault/logs/audit.log
  ```
  > El nombre del pod puede variar. Obtenerlo con: `kubectl get pods -n middleware | grep vault`
- Pedir que copie el output en el chat para analizarlo.
- Cada entrada del log contiene: remote_address, display_name, policies, operation, path, y timestamp. Úsalos para responder consultas del usuario sobre quién accedió a qué y cuándo.

## Ejecución de Comandos
1. Recibir el comando vault que el usuario quiere ejecutar.
2. Ejecutar: `vault [comando solicitado]`
3. Mostrar el resultado al usuario.
4. Si el comando falla: mostrar el error de vault.

## Gotchas
- El .env debe estar en formato: VAULT_USER=usuario y VAULT_PASS=contraseña.
- No mostrar VAULT_PASS en pantalla ni en logs.
- Si el token de vault expira, re-autenticar antes de ejecutar el comando.
- Para leer secretos: `vault kv get [path]`
- Para listar: `vault kv list [path]`
- Para escribir: `vault kv put [path] clave=valor`
