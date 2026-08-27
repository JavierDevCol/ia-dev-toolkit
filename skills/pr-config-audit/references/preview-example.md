# Ejemplo de Preview (Fase D)

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
```
