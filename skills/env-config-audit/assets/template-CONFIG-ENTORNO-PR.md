<!--
  Plantilla para CONFIG-ENTORNO-PR-{ID} ({nombre microservicio}).md.
  {ID} = número de PR o nombre de rama.
  {nombre microservicio} = nombre del microservicio.
  Alcance: inventario completo (MS nuevo) o solo delta (funcionalidad).
  Los placeholders tienen formato {{PLACEHOLDER}}.
-->

# {{PROJECT_NAME}}

> **Tipo de entrega:** {{DELIVERY_MODE}}
> **Fecha:** {{DATE}}

## 1. Resumen

{{SUMMARY}}

- **Repositorio:** {{REPO_URL}}
- **PR / Rama:** {{PR_OR_BRANCH}}
- **Ambientes:** {{ENVIRONMENTS}}

## 2. Variables de entorno

{{ALCANCE_LABEL}}

| Nombre | Ámbito | Secreta | Obligatoria | Dónde se usa | Origen / Destino | Acción |
|--------|--------|---------|-------------|--------------|------------------|--------|
| {{VAR_NAME}} | {{VAR_SCOPE}} | {{VAR_SECRET}} | {{VAR_REQUIRED}} | {{VAR_USAGE}} | {{VAR_ORIGIN}} | {{VAR_ACTION}} |

> ⚠️ **Variables pendientes:** {{PENDING_VARIABLES}}

## 3. Acciones por plataforma

### 3.1 Variable Groups ADO

| Variable Group | Ambiente | Variable | Acción |
|----------------|----------|----------|--------|
| {{VG_NAME}} | {{VG_ENV}} | {{VG_VAR}} | {{VG_ACTION}} |

### 3.2 Vault corporativo

| Path | Ambiente | Variable | Acción |
|------|----------|----------|--------|
| {{VAULT_PATH}} | {{VAULT_ENV}} | {{VAULT_VAR}} | {{VAULT_ACTION}} |

### 3.3 Archivos de configuración

| Archivo | Cambio | Variable |
|---------|--------|----------|
| {{CONFIG_FILE}} | {{CONFIG_CHANGE}} | {{CONFIG_VAR}} |

### 3.4 Colas RabbitMQ

| Cola / Exchange / Binding | Tipo | Routing key | Consumidores | Acción | Dónde se declara |
|---------------------------|------|-------------|--------------|--------|-------------------|
| {{QUEUE_NAME}} | {{QUEUE_TYPE}} | {{ROUTING_KEY}} | {{CONSUMERS}} | {{QUEUE_ACTION}} | {{QUEUE_LOCATION}} |

### 3.5 Redis

| Tipo | Clave / patrón | TTL | Consumidores | Acción | Dónde se usa |
|------|----------------|-----|--------------|--------|--------------|
| {{REDIS_TYPE}} | {{REDIS_KEY}} | {{REDIS_TTL}} | {{REDIS_CONSUMERS}} | {{REDIS_ACTION}} | {{REDIS_LOCATION}} |

### 3.6 Migraciones BD

| Archivo | Herramienta | Descripción | Tablas afectadas | Rollback | Ambientes | Acción |
|---------|-------------|-------------|------------------|----------|-----------|--------|
| {{MIGRATION_FILE}} | {{MIGRATION_TOOL}} | {{MIGRATION_DESC}} | {{MIGRATION_TABLES}} | {{MIGRATION_ROLLBACK}} | {{MIGRATION_ENVS}} | {{MIGRATION_ACTION}} |

## 4. Observaciones

{{OBSERVATIONS}}

---

*Documento generado con env-config-audit skill — {{DATE}}*
