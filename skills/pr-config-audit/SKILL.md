---
name: pr-config-audit
description: >
  Usa esta skill cuando necesites auditar la configuración de un PR, commit o
  rama, al revisar un pull request, al planificar un paso entre ambientes
  (DES→QA→PROD), al incorporar un nuevo microservicio, o cuando pidan mapear
  variables de entorno, revisar colas, analizar configuración del PR o documentar
  configuraciones nuevas.
compatibility: Requires git. Optional: HashiCorp Vault, RabbitMQ, Redis
metadata:
  memory_skill: ./memory_skill.json
---

## Convenciones de la skill

Leer {{memory_skill}} . Si el archivo no existe o los campos son `null`, usar los defaults indicados.

### Configuración (`config`)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `name_repo_source` | `pr_remote` | Obtener nombre del repo del PR (remote) |
| `name_ms_source` | `same_as_repo` | Nombre microservicio = nombre repo |
| `id_source` | `user_or_pr_link` | ID del documento: usuario indica o se detecta del link PR |
| `version_pattern.auto_detect_last_tag` | `true` | Buscar último tag automáticamente |
| `version_pattern.suggest_next` | `true` | Sugerir siguiente versión (patch) |
| `version_pattern.force_v_prefix` | `true` | Agregar prefijo `v` si el usuario no lo incluye |

### Memoria (`memory`)

| Campo | Default | Descripción |
|-------|---------|-------------|
| `output_base_path` | `null` | Ruta base para guardar el documento de salida |

# PR Config Audit

## What I do

- Analizar un commit/PR/diff y extraer variables de entorno nuevas, modificadas o eliminadas
- Detectar colas RabbitMQ declaradas en código o config (queues, exchanges, bindings)
- Clasificar cada variable por ámbito: **pipeline** (Variable Group ADO) o **runtime** (Vault)
- Indicar exactamente qué crear/actualizar y dónde (nombre del VG, path de Vault, archivo de config, declaración de cola)
- Preguntar al usuario sobre variables cuyo origen no se puede inferir
- Mostrar preview de acciones propuestas antes de generar el documento
- Generar documento final solo con la configuración de variables y colas

**Lo que NO hace:** setup local, instalación, health checks, smoke tests, infraestructura,
pasos de build/deploy, rollback, migraciones BD, diagramas de arquitectura, documentación de APIs.

## Conceptos clave — Variable Groups ADO vs Vault

| Ámbito | Plataforma | ¿Qué contiene? | ¿Quién lo consume? | Ejemplos |
|--------|-----------|----------------|---------------------|----------|
| **Pipeline** | Variable Groups ADO | Variables que el pipeline necesita: nombres de ambiente, tags, flags de CI/CD | `azure-pipelines.yml` | `DOCKER_REGISTRY`, `KUBE_NAMESPACE`, `IMAGE_TAG` |
| **Runtime** | Vault corporativo | Secretos que la aplicación lee en ejecución | `application.yml`, `os.getenv`, `System.getenv`, etc. | `DB_PASSWORD`, `API_KEY`, `JWT_SECRET` |

**Regla práctica:**
- Se usa en `azure-pipelines.yml` para decidir *cómo* desplegar → **Variable Group ADO**
- Se usa en `application.yml`/`os.getenv`/`@Value` para configurar *qué hace* la app → **Vault**
- Si es secreto y lo necesita la app → **siempre Vault**, nunca Variable Group

## Fase 0 — Tipo de análisis

> ¿El análisis es para un **microservicio nuevo** (inventario completo)
> o una **funcionalidad en uno existente** (solo delta del PR/diff)?

| Opción | Alcance |
|--------|---------|
| **MS nuevo** | Inventario completo del servicio: variables en código, configs y pipeline |
| **Funcionalidad** | Solo cambios detectados en el PR/diff |

## Fase A — Detección de cambios desde el PR/commit

Analizar el diff (o el repositorio completo si es MS nuevo) para detectar:

- Variables de entorno en código (según el lenguaje del proyecto)
- Variables en archivos de configuración (appsettings, .env, application.yml, config.yaml, etc.)
- Variables en pipeline CI/CD (azure-pipelines.yml, .github/workflows/, .gitlab-ci.yml)
- Referencias a Variable Groups ADO y Vault corporativo
- Colas RabbitMQ (queues, exchanges, bindings en código o config)
- Redis (caché, sesiones, pub-sub, estructuras en código o config)
- Migraciones de base de datos (scripts SQL, ORM migrations, DDL)
- Secretos hardcodeados → alertar

## Fase B — Clasificación de variables

Para cada variable detectada, registrar:

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

Para cada cola detectada, registrar:

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

Para cada cambio en Redis detectado, registrar:

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

Para cada migración detectada, registrar:

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

## Fase C — Entrevista

Agrupar TODAS las variables sin origen en un solo bloque:

```
Variables sin origen claro:
- API_GATEWAY_URL
  Usada en: src/config/app.config.ts:42
  Usada en: docker-compose.yml:18
  Pregunta: ¿Dónde obtiene el equipo este valor?

- INTERNAL_API_KEY
  Usada en: src/services/internal.client.ts:15
  Pregunta: ¿Dónde obtiene el equipo este valor?
```

**Preguntas de contexto:**
- Nombres de Variable Groups por ambiente (`vg-{app}-des`, `vg-{app}-qa`, etc.)
- URL/base path de Vault y convención de nombres
- Ambientes destino (DES, QA, PROD)
- **Ubicación del archivo de salida:**
  - Si `memory.output_base_path` tiene valor → preguntar: *"¿Usar esta ruta guardada? [ruta]"*
  - Si es `null` → preguntar al usuario la ruta base
  - Construir la carpeta: `<ruta-base>/entrega_release/{nombre_repo}/{release}/`

**Datos del PR** (según `config`):
- `{nombre_repo}` → según `config.name_repo_source`
- `{nombre microservicio}` → según `config.name_ms_source`
- `{ID}` → según `config.id_source`
- `{release}` → sugerir según `config.version_pattern`

## Fase D — Preview y confirmación

Mostrar resumen consolidado antes de generar el documento:

```
════════════════════════════════════════════════════
 PREVIEW — Proyecto: auth-svc
 PR: #42 — feature/add-oauth2-provider → develop
════════════════════════════════════════════════════

🔧 Variable Groups ADO — Actualizar
  ┌──────────────────────┬────────────────┬──────────────────┐
  │ Variable Group       │ Variable       │ Acción           │
  ├──────────────────────┼────────────────┼──────────────────┤
  │ vg-auth-svc-des      │ OAUTH_ISSUER   │ ➕ Crear         │
  │ vg-auth-svc-qa       │ OAUTH_ISSUER   │ ➕ Crear         │
  │ vg-auth-svc-prod     │ OAUTH_ISSUER   │ ➕ Crear         │
  └──────────────────────┴────────────────┴──────────────────┘

🔐 Vault corporativo — Crear secretos
  ┌──────────────────────────────────────────────┬──────────────────┬──────────┐
  │ Path                                         │ Variable         │ Acción   │
  ├──────────────────────────────────────────────┼──────────────────┼──────────┤
  │ secret/auth-svc/des/oauth/client-secret      │ OAUTH_CLIENT_SEC │ ➕ Crear │
  │                                              │ RET              │          │
  │ secret/auth-svc/qa/oauth/client-secret       │ OAUTH_CLIENT_SEC │ ➕ Crear │
  │                                              │ RET              │          │
  │ secret/auth-svc/prod/oauth/client-secret     │ OAUTH_CLIENT_SEC │ ➕ Crear │
  │                                              │ RET              │          │
  └──────────────────────────────────────────────┴──────────────────┴──────────┘

⚠️ Variables sin origen definido
  ┌──────────────────┬─────────────────────────────┬──────────────────┐
  │ Variable         │ Usada en                   │ Estado           │
  ├──────────────────┼─────────────────────────────┼──────────────────┤
  │ OAUTH_CLIENT_ID  │ src/config/oauth.ts:12     │ Pendiente definir│
  └──────────────────┴─────────────────────────────┴──────────────────┘

📤 Colas RabbitMQ — Declarar
  ┌────────────────────────┬──────────┬──────────────────┬──────────────────┐
  │ Cola / Exchange        │ Tipo     │ Acción           │ Dónde se declara │
  ├────────────────────────┼──────────┼──────────────────┼──────────────────┤
  │ order.created.queue    │ Queue    │ ➕ Crear         │ rabbitmq.ts:25   │
  │ order.exchange         │ Exchange │ ➕ Crear         │ rabbitmq.ts:28   │
  │ order.created.queue →  │ Binding  │ ➕ Crear         │ rabbitmq.ts:31   │
  │   order.exchange       │          │                  │                  │
  └────────────────────────┴──────────┴──────────────────┴──────────────────┘

🗄️ Redis — Configurar
  ┌──────────────────────┬──────────────┬──────────────────┬──────────────────┐
  │ Tipo                 │ Clave/patrón │ Acción           │ Dónde se usa     │
  ├──────────────────────┼──────────────┼──────────────────┼──────────────────┤
  │ Cache                │ products:*   │ ➕ Crear         │ redis-cache.ts:22 │
  │ Session store        │ user:{id}:ss │ ✏️ Actualizar    │ session.store:15 │
  │ Pub-Sub channel      │ order.events │ ➕ Crear         │ redis-pubsub:8   │
  └──────────────────────┴──────────────┴──────────────────┴──────────────────┘

🗄️ Migraciones BD — Ejecutar
  ┌────────────────────────────────────┬────────────┬──────────────────┬──────────────────┐
  │ Archivo                            │ Herramienta│ Tablas afectadas │ Acción           │
  ├────────────────────────────────────┼────────────┼──────────────────┼──────────────────┤
  │ db/migrations/V42__add_oauth_token │ Flyway     │ oauth_tokens     │ ▶️ Ejecutar      │
  │ s.sql                              │            │                  │                  │
  │ src/Data/Migrations/20260327_AddRe │ EF Core    │ refresh_tokens   │ ▶️ Ejecutar      │
  │ freshToken.cs                      │            │                  │                  │
  └────────────────────────────────────┴────────────┴──────────────────┴──────────────────┘

════════════════════════════════════════════════════
¿Confirmas?
(1) Sí, generar documento
(2) No, quiero corregir
(3) Cancelar
════════════════════════════════════════════════════

**Persistencia:** Actualizar `memory_skill.json` → `memory.output_base_path` con la ruta base usada para que esté disponible en la próxima ejecución.
```

**Reglas:** Solo incluir secciones con cambios. NO incluir migraciones, service connections,
infraestructura, health checks, ni pasos de deploy.

## Fase E — Generación del documento
Generar `CONFIG-ENTORNO-PR-{ID} ({nombre microservicio}).md`, Usando como base `assets/template-CONFIG-ENTORNO-PR.md`.

El alcance según Fase 0:
- **MS nuevo:** inventario completo de variables, colas, redis y migraciones
- **Funcionalidad:** solo el delta detectado en el PR/diff

## Reglas obligatorias

1. Solo documentar configuración de variables — nada de setup local, infra, deploy, health checks
2. Generar documento según convenciones definidas en Fase C y estructura de `memory_skill.json`.
3. Nunca asumir origen de variables — preguntar al usuario con archivo+línea de contexto
4. Nunca incluir secretos reales; alertar si hay secretos commiteados
5. Mostrar preview antes de generar el documento final
6. Si el usuario no sabe el origen → `⚠️ Pendiente de definir`

## Gotchas

- **Vault corporativo ≠ Azure Key Vault:** No confundir. Preguntar si hay ambigüedad.
- **Nunca asumir origen:** Aunque el nombre sea descriptivo (`DB_HOST`), no inferir origen sin
  evidencia en pipeline o config.
- **Variable Groups vs variables inline:** Distinguir `- group:` de `variables:` en el YAML.
- **Multi-ambiente:** Una variable puede tener valor distinto por ambiente.
- **Pipeline no visible:** Si no hay `azure-pipelines.yml`, buscar en `.azuredevops/` o
  preguntar si está en otro repo.
- **Secretos hardcodeados:** Revisar configs commiteados y alertar.

## Condiciones de entrada

- Acceso al repositorio (clonado o en workspace)
- PR creado o diff disponible entre ramas
- Usuario con conocimiento de dónde se configuran las variables del proyecto

