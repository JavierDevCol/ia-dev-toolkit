# Catálogo de Vulnerabilidades — Backend

> Referencia para el sub-agente de análisis Backend. Mapeado a OWASP Top 10 (2021) y CWE, adaptado a
> revisión estática de código (sin ejecución). Cada hallazgo debe citar el CWE correspondiente para
> trazabilidad. Ver también `catalogo-frontend.md` y `catalogo-devops.md` para esos dominios.

## Inyección (SQL/NoSQL/Comandos/LDAP)
- **CWE:** CWE-89 (SQL), CWE-78 (Comandos OS), CWE-943 (NoSQL/LDAP) · **OWASP:** A03:2021
- **Indicador:** Concatenación de input de usuario en queries, comandos de shell, o filtros LDAP sin parametrizar/escapar.
- **Ejemplo vulnerable:** `db.query("SELECT * FROM users WHERE id = " + userId)`
- **Remediación:** Prepared statements / queries parametrizadas, ORM con binding, `execFile` en vez de `exec` con input crudo.
- **Severidad típica:** Crítica.

## Path Traversal
- **CWE:** CWE-22 · **OWASP:** A01:2021
- **Indicador:** Input de usuario usado para construir una ruta de archivo sin normalizar/validar contra directorio base (`../../etc/passwd`, nombre de archivo de upload sin sanitizar).
- **Ejemplo vulnerable:** `fs.readFile(basePath + req.query.file)`
- **Remediación:** Resolver ruta absoluta y verificar que siga dentro del directorio base (`path.resolve` + comparación de prefijo), whitelist de nombres/extensiones permitidas.
- **Severidad típica:** Crítica.

## XXE (XML External Entity)
- **CWE:** CWE-611 · **OWASP:** A05:2021
- **Indicador:** Parser XML configurado con resolución de entidades externas/DTD habilitada al procesar XML de origen no confiable.
- **Ejemplo vulnerable:** Parser Java/Python/PHP con `DOCTYPE`/entidades externas habilitadas por default, sin deshabilitar explícitamente.
- **Remediación:** Deshabilitar DTD y entidades externas en el parser (`disallow-doctype-decl`, `XMLConstants.FEATURE_SECURE_PROCESSING`, `resolve_entities=False`).
- **Severidad típica:** Crítica.

## XSS (Cross-Site Scripting)
- **CWE:** CWE-79 · **OWASP:** A03:2021
- **Indicador:** Input de usuario insertado en HTML/DOM sin sanitizar/escapar (`innerHTML`, `dangerouslySetInnerHTML`, `v-html`, render de plantillas server-side sin auto-escape).
- **Ejemplo vulnerable:** `element.innerHTML = req.query.name`
- **Remediación:** Escapar output, usar APIs seguras (`textContent`), sanitizar con librería (DOMPurify), CSP.
- **Severidad típica:** Alta.

## CSRF (Cross-Site Request Forgery)
- **CWE:** CWE-352 · **OWASP:** A01:2021
- **Indicador:** Endpoints que mutan estado (POST/PUT/DELETE) sin token anti-CSRF ni verificación de origen, dependiendo solo de cookies de sesión.
- **Remediación:** Token CSRF por sesión/request, `SameSite=Strict/Lax` en cookies, verificar header `Origin`/`Referer`.
- **Severidad típica:** Alta.

## SSRF (Server-Side Request Forgery)
- **CWE:** CWE-918 · **OWASP:** A10:2021
- **Indicador:** El servidor hace requests HTTP a una URL controlada (parcial o totalmente) por el usuario, sin validar destino.
- **Ejemplo vulnerable:** `fetch(req.body.callbackUrl)`
- **Remediación:** Allowlist de dominios/IPs permitidos, bloquear rangos internos (169.254.0.0/16, 10.0.0.0/8, etc.), resolver DNS antes de permitir.
- **Severidad típica:** Alta.

## Open Redirect
- **CWE:** CWE-601 · **OWASP:** A01:2021
- **Indicador:** Redirección (`res.redirect`, `Location:`) construida con una URL/parámetro controlado por el usuario sin validar contra allowlist.
- **Ejemplo vulnerable:** `res.redirect(req.query.next)`
- **Remediación:** Allowlist de rutas/dominios permitidos, o solo rutas relativas propias.
- **Severidad típica:** Media.

## Deserialización Insegura
- **CWE:** CWE-502 · **OWASP:** A08:2021
- **Indicador:** Deserializar input no confiable con mecanismos que ejecutan código (`pickle.loads`, `yaml.load` sin `SafeLoader`, `ObjectInputStream` de Java, `unserialize` de PHP).
- **Remediación:** Formatos de datos sin ejecución (JSON), `yaml.safe_load`, validar schema antes de deserializar.
- **Severidad típica:** Crítica.

## Control de Acceso Roto (IDOR / Falta de Autorización)
- **CWE:** CWE-639, CWE-862 · **OWASP:** A01:2021 · **OWASP API:** API1:2023 (BOLA)
- **Indicador:** Endpoint usa un ID recibido del cliente para acceder a un recurso sin verificar que el usuario autenticado sea dueño/tenga permiso sobre ese recurso.
- **Ejemplo vulnerable:** `GET /orders/:id` retorna la orden sin comparar `order.userId === session.userId`.
- **Remediación:** Verificar ownership/rol en cada acceso a recurso, no confiar en IDs opacos como control de acceso.
- **Severidad típica:** Crítica.

## Mass Assignment / Autorización a Nivel de Propiedad (BOPLA)
- **CWE:** CWE-915 (asignación masiva) · **OWASP:** A01:2021 · **OWASP API:** API3:2023 (fusiona el antiguo "Mass Assignment" con "Excessive Data Exposure": el problema de fondo es la falta de control de autorización a nivel de *propiedad*, no solo de objeto)
- **Indicador:** El body completo del cliente se pasa sin whitelist a un ORM/update (`Model.update(req.body, ...)`), o un endpoint de lectura serializa el objeto completo del modelo (incluyendo campos internos como `passwordHash`, `role`, `internalNotes`) sin un DTO/proyección explícita.
- **Ejemplo vulnerable:** `User.update(req.body, { where: { id: req.user.id } })` — el cliente puede incluir `role: "admin"` en el payload.
- **Remediación:** Whitelist explícita de campos permitidos por endpoint (allowlist, nunca blocklist), DTOs/serializers que excluyan campos internos por defecto en vez de por excepción.
- **Severidad típica:** Crítica (si el campo expuesto es de privilegio) a Media (si es solo de datos internos no sensibles).

## Consumo de Recursos No Restringido (Rate Limiting / Paginación / Payload)
- **CWE:** CWE-770 (asignación sin límites), CWE-400 · **OWASP API:** API4:2023
- **Indicador:** Endpoint sin límite de tamaño de payload/upload, sin límite de paginación (`?limit=999999` retorna toda la tabla), sin rate-limiting en operaciones costosas (envío de email/SMS, exportes, búsquedas con wildcard), o sin timeout en llamadas a servicios externos.
- **Remediación:** Límite de tamaño de body (`express.json({ limit: '100kb' })` o equivalente), paginación con tope máximo forzado en servidor (ignorar el `limit` del cliente si excede el máximo), rate-limiting por usuario/IP en operaciones costosas, timeouts explícitos.
- **Severidad típica:** Alta (DoS/costo operacional) — distinta de "Manejo de Excepciones No Controladas" (esta es sobre ausencia de límites de uso legítimo llevado al extremo, no sobre una excepción no capturada).

## Validación Insegura de JWT
- **CWE:** CWE-347 (verificación de firma incorrecta) · **OWASP:** A07:2021
- **Indicador:** `jwt.verify()` (o equivalente) llamado sin restringir `algorithms` (permite confusión de algoritmo RS256↔HS256, o el histórico bypass `alg: none`), sin validar `aud`/`iss` cuando la app acepta tokens de múltiples emisores/clientes, o validando solo la metadata del token sin verificar que la clave criptográfica referenciada (`kid`) sea una de las esperadas por el servidor (permite inyección de clave — CVE-2025-24976 es un ejemplo público de esta clase).
- **Ejemplo vulnerable:** `jwt.verify(token, secret)` sin `{ algorithms: ['HS256'] }`.
- **Remediación:** Siempre restringir `algorithms` a una whitelist explícita; validar `aud`/`iss`/`exp`/`nbf` según el modelo de la app; si se resuelve la clave dinámicamente por `kid`, validar el `kid` contra una lista conocida antes de usarlo, nunca confiar en el header del token para decidir qué clave/algoritmo usar.
- **Severidad típica:** Crítica (bypass de autenticación).

## Autenticación y Gestión de Sesión Rota
- **CWE:** CWE-287 (auth rota), CWE-613 (expiración de sesión), CWE-307 (falta de rate-limiting/lockout) · **OWASP:** A07:2021
- **Indicador:** Contraseñas en texto plano o con hash débil (MD5/SHA1 sin salt), tokens de sesión predecibles, sesiones sin expiración, falta de rate-limiting en login.
- **Remediación:** bcrypt/argon2 para contraseñas, tokens aleatorios largos, expiración e invalidación de sesión, rate-limiting/lockout.
- **Severidad típica:** Crítica.

## Prototype Pollution
- **CWE:** CWE-1321 · **OWASP:** A08:2021 (aledaño; no tiene entrada dedicada en Top 10 2021)
- **Indicador:** Merge/copia recursiva de un objeto controlado por el cliente (`req.body`, query params parseados) hacia otro objeto, sin excluir las claves `__proto__`, `constructor` o `prototype` (`for...in` genérico, librerías de merge sin protección, `JSON.parse` con reviver inseguro).
- **Ejemplo vulnerable:** función `deepMerge` propia con `for (const k in source) { target[k] = ... }` recibiendo `req.body` directo.
- **Remediación:** Excluir explícitamente `__proto__`/`constructor`/`prototype` en cualquier merge recursivo, usar `Object.create(null)` para objetos que solo almacenan datos, o una librería de merge con protección conocida contra pollution.
- **Severidad típica:** Crítica (puede escalar a bypass de auth/lógica o RCE según qué consuma la propiedad contaminada).

## GraphQL Inseguro
- **CWE:** CWE-400 (introspección/batching sin límite), CWE-285 (autorización por campo ausente) · **OWASP:** A05:2021/A01:2021
- **Indicador:** Introspección (`__schema`) habilitada en producción o accesible sin autenticación, sin límite de profundidad/complejidad de query (permite queries anidadas costosas), sin límite de batching (múltiples queries de máximo costo en una sola request evade rate-limiting basado en requests HTTP), resolvers que no repiten el chequeo de autorización a nivel de campo (un campo sensible resuelto sin verificar el rol del solicitante, aunque la query raíz sí esté protegida).
- **Remediación:** Deshabilitar introspección en producción (o restringirla a usuarios autenticados/internos), límite de profundidad y de "costo" de query, límite de cantidad de operaciones por batch, autorización verificada en cada resolver de campo sensible, no solo en el query raíz.
- **Severidad típica:** Alta (DoS vía queries costosas) a Crítica (si el bypass de autorización por campo expone datos sensibles).

## Fallas Criptográficas
- **CWE:** CWE-327 (algoritmo débil), CWE-330 (aleatoriedad insegura) · **OWASP:** A02:2021
- **Indicador:** Uso de algoritmos rotos/obsoletos (DES, RC4, MD5/SHA1 para integridad o firmas), modo ECB, IV/salt fijo o reutilizado, `Math.random()`/`rand()` para generar tokens de sesión, reset-password o claves — en vez de un CSPRNG (`crypto.randomBytes`, `secrets.token_bytes`).
- **Ejemplo vulnerable:** `const token = Math.random().toString(36)` usado como token de reset de contraseña.
- **Remediación:** Algoritmos modernos (AES-GCM, bcrypt/argon2, SHA-256+), CSPRNG para cualquier valor con propósito de seguridad.
- **Severidad típica:** Alta-Crítica (depende de qué protege).

## Exposición de Datos Sensibles / Secretos Hardcodeados
- **CWE:** CWE-798, CWE-312 · **OWASP:** A02:2021
- **Indicador:** Credenciales, API keys, tokens o connection strings escritos directamente en código/config versionado.
- **Remediación:** Variables de entorno, Vault/Secrets Manager. **Reportar el hallazgo puntual y remitir a `env-config-audit` para el inventario completo — no duplicar ese análisis aquí.**
- **Severidad típica:** Crítica.

## Configuración Insegura
- **CWE:** CWE-16, CWE-346 (CORS) · **OWASP:** A05:2021
- **Indicador:** CORS con `Access-Control-Allow-Origin: *` en endpoints con credenciales, modo debug/stack traces expuestos en producción, headers de seguridad ausentes (`Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`).
- **Remediación:** CORS con allowlist explícita, deshabilitar debug en prod, agregar headers de seguridad estándar.
- **Severidad típica:** Media-Alta.

## Dependencias con Versiones Vulnerables Conocidas
- **CWE:** CWE-1104 · **OWASP:** A06:2021
- **Indicador:** Manifiestos (`package.json`, `pom.xml`, `requirements.txt`, etc.) con versiones de librerías con vulnerabilidades públicamente conocidas y ampliamente documentadas.
- **Límite:** Sin consulta a CVE en línea — solo se reportan casos de conocimiento general y verificable por versión. Si hay duda, marcar `⚠️ Verificar manualmente` en vez de afirmar.
- **Remediación:** Actualizar a versión parchada, o correr `npm audit`/`pip-audit`/equivalente localmente.
- **Severidad típica:** Variable (depende de la CVE).

## Manejo de Excepciones No Controladas (DoS por crash)
- **CWE:** CWE-248 (excepción no capturada), CWE-400 (consumo de recursos no controlado) · **OWASP:** A05:2021 (aledaño; no hay categoría dedicada en Top 10 2021)
- **Indicador:** API que requiere callback/argumento obligatorio llamada como si devolviera Promise (ej. `await crypto.scrypt(...)` sin el callback que la función exige), o cualquier operación que lance una excepción síncrona dentro de un handler `async` sin `try/catch`, alcanzable con una request no autenticada. En Node ≥15 una excepción no capturada en una promesa rechazada sin manejar termina el proceso por defecto.
- **Ejemplo vulnerable:** `const valid = await crypto.scrypt(password, user.salt, 64)` — `crypto.scrypt` es callback-only; sin callback lanza `TypeError` síncrono antes de calcular nada, y sin `try/catch` alrededor tumba el proceso con una sola petición.
- **Remediación:** `try/catch` (o wrapper `asyncHandler`) alrededor de toda lógica async en handlers HTTP; usar la variante correcta de la API (`util.promisify(crypto.scrypt)` o `crypto.scryptSync`); no depender de que Node crashee "seguro" ante una excepción no manejada.
- **Severidad típica:** Alta (DoS no autenticado con una sola request) — no reportar si el código sí envuelve la lógica en `try/catch` u otro manejo de errores.

## Logging y Monitoreo Insuficiente
- **CWE:** CWE-778, CWE-532 (datos sensibles en logs) · **OWASP:** A09:2021
- **Indicador:** Eventos de seguridad (login fallido, cambio de permisos, acceso a datos sensibles) sin registrar, o logs que incluyen datos sensibles (contraseñas, tokens) en texto plano.
- **Remediación:** Registrar eventos de seguridad con contexto (usuario, IP, timestamp) sin loguear secretos/PII en claro.
- **Severidad típica:** Media.

## Fuera de Alcance (no cubierto por análisis estático)
- **Insecure Design (A04:2021) y fallas de lógica de negocio** (ej. race conditions en flujos de pago, límites de negocio ausentes): requieren entender el dominio/threat model, no solo el código — señalar como sospecha si aparece, no como hallazgo confirmado. Aplica a los 3 catálogos (backend/frontend/devops).
- **ReDoS (CWE-1333):** patrones regex catastróficos son detectables pero de alto falso-positivo sin probarlos — marcar `⚠️ Verificar manualmente` si se sospecha. Aplica también a regex en código frontend.
