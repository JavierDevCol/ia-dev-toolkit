# Catálogo de Vulnerabilidades

> Referencia común para los sub-agentes de análisis de seguridad. Mapeado a OWASP Top 10 (2021) y CWE, adaptado a revisión estática de código (sin ejecución). Cada hallazgo debe citar el CWE correspondiente para trazabilidad.

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
- **Indicador:** Input de usuario insertado en HTML/DOM sin sanitizar/escapar (`innerHTML`, `dangerouslySetInnerHTML`, `v-html`, render de plantillas sin auto-escape).
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
- **CWE:** CWE-639, CWE-862 · **OWASP:** A01:2021
- **Indicador:** Endpoint usa un ID recibido del cliente para acceder a un recurso sin verificar que el usuario autenticado sea dueño/tenga permiso sobre ese recurso.
- **Ejemplo vulnerable:** `GET /orders/:id` retorna la orden sin comparar `order.userId === session.userId`.
- **Remediación:** Verificar ownership/rol en cada acceso a recurso, no confiar en IDs opacos como control de acceso.
- **Severidad típica:** Crítica.

## Autenticación y Gestión de Sesión Rota
- **CWE:** CWE-287 (auth rota), CWE-613 (expiración de sesión), CWE-307 (falta de rate-limiting/lockout) · **OWASP:** A07:2021
- **Indicador:** Contraseñas en texto plano o con hash débil (MD5/SHA1 sin salt), tokens de sesión predecibles, sesiones sin expiración, falta de rate-limiting en login.
- **Remediación:** bcrypt/argon2 para contraseñas, tokens aleatorios largos, expiración e invalidación de sesión, rate-limiting/lockout.
- **Severidad típica:** Crítica.

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

## Logging y Monitoreo Insuficiente
- **CWE:** CWE-778, CWE-532 (datos sensibles en logs) · **OWASP:** A09:2021
- **Indicador:** Eventos de seguridad (login fallido, cambio de permisos, acceso a datos sensibles) sin registrar, o logs que incluyen datos sensibles (contraseñas, tokens) en texto plano.
- **Remediación:** Registrar eventos de seguridad con contexto (usuario, IP, timestamp) sin loguear secretos/PII en claro.
- **Severidad típica:** Media.

## Fuera de Alcance (no cubierto por análisis estático)
- **Insecure Design (A04:2021) y fallas de lógica de negocio** (ej. race conditions en flujos de pago, límites de negocio ausentes): requieren entender el dominio/threat model, no solo el código — señalar como sospecha si aparece, no como hallazgo confirmado.
- **ReDoS (CWE-1333):** patrones regex catastróficos son detectables pero de alto falso-positivo sin probarlos — marcar `⚠️ Verificar manualmente` si se sospecha.
