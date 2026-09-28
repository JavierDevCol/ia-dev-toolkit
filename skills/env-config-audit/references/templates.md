# Tablas-template por fase

## Fase B — Clasificación de variables

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Variable exacta (ej. `DB_CONNECTION_STRING`) |
| **Ámbito** | **Pipeline** (usa CI/CD) o **Runtime** (consume la app) |
| **Obligatoria** | Sí / No / Condicional |
| **Dónde se usa** | Archivo + línea (ej. `src/config/db.ts:42`, `azure-pipelines.yml:25`) |
| **Origen** | Variable Group ADO, Vault, config file, portal, equipo interno |
| **¿Secreta?** | Sí / No |
| **Ambientes** | Local, DES, QA, PROD (o varios) |
| **Acción** | Crear / Actualizar / Eliminar / Solo documentar |
| **Destino exacto** | Nombre del VG, path de Vault, o archivo de config |

Si no se infiere el origen → `⚠️ Sin origen conocido` → Fase C.

## Fase B2 — Clasificación de colas RabbitMQ

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Nombre de la cola (ej. `order.created.queue`) |
| **Tipo** | Queue / Exchange / Binding |
| **Dónde se declara** | Archivo + línea (ej. `src/config/rabbitmq.ts:25`) |
| **Exchange** | Exchange al que está vinculada (si aplica) |
| **Routing key** | Routing key del binding (si aplica) |
| **Consumidores** | Qué servicios/métodos la consumen |
| **Acción** | Crear / Actualizar / Eliminar / Solo documentar |
| **Ambientes** | DES, QA, PROD (o varios) |
| **Se Crea** | AUTO / MANUAL |

## Fase B3 — Clasificación de Redis

| Campo | Descripción |
|-------|-------------|
| **Tipo** | Cache / Pub-Sub / Session store / Data structure / Config |
| **Dónde se usa** | Archivo + línea (ej. `src/config/redis.ts:15`) |
| **Uso** | Strings, Hashes, Lists, Sets, Sorted Sets, Streams, Pub/Sub, Cache |
| **Clave/patrón** | Ej: `user:{id}:session`, `cache:products:*` |
| **TTL / Expiración** | Si aplica (segundos, minutos, etc.) |
| **Consumidores** | Qué servicios/modulos la usan |
| **Acción** | Crear / Actualizar / Eliminar / Solo documentar |
| **Ambientes** | DES, QA, PROD (o varios) |

## Fase B4 — Clasificación de migraciones BD

| Campo | Descripción |
|-------|-------------|
| **Nombre/archivo** | Ej. `V42__add_oauth_tokens.sql`, `*_add_oauth_tokens.py`, `AddOAuthTokensTable.cs` |
| **Tipo** | SQL script / ORM migration / Schema change |
| **Herramienta** | Flyway / Liquibase / EF Core / Alembic / Django / Prisma / TypeORM / Sequelize |
| **Descripción** | Ej. "Crear tabla oauth_tokens", "Agregar columna refresh_token" |
| **BD / esquema** | Base de datos y esquema afectado |
| **Tablas afectadas** | Lista de tablas creadas/modificadas/eliminadas |
| **Rollback** | Script o comando para revertir (si aplica) |
| **Ambientes** | DES, QA, PROD (o varios) |
| **Acción** | Ejecutar / Revisar / Documentar |
