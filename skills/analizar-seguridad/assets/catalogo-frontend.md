# Catálogo de Vulnerabilidades — Frontend

> Referencia para el sub-agente de análisis Frontend. Mapeado a OWASP Top 10 (2021) y CWE, adaptado a
> revisión estática de código client-side (sin ejecución). Cada hallazgo debe citar el CWE
> correspondiente para trazabilidad. Ver también `catalogo-backend.md` (XSS/CSRF completos viven ahí,
> aplican igual a código frontend) y `catalogo-devops.md`.

## XSS (Cross-Site Scripting)
- **CWE:** CWE-79 · **OWASP:** A03:2021
- **Indicador:** Input de usuario insertado en HTML/DOM sin sanitizar/escapar (`innerHTML`, `dangerouslySetInnerHTML`, `v-html`, template literals inyectados en el DOM).
- **Ejemplo vulnerable:** `element.innerHTML = new URLSearchParams(location.search).get('name')`
- **Remediación:** Escapar output, usar APIs seguras (`textContent`), sanitizar con librería (DOMPurify), CSP.
- **Severidad típica:** Alta.

## DOM Clobbering
- **CWE:** CWE-79 (variante de XSS), CWE-1321 (relacionado a prototype pollution) · **OWASP:** Top 10 Client-Side Security Risks
- **Indicador:** Código JS que confía en que una variable global o `document.getElementById(...)` referencia lo que el desarrollador espera, sin validar su tipo — un atacante que controle HTML (aunque no pueda ejecutar `<script>` por CSP) puede "clobberear" esa referencia inyectando elementos con `id`/`name` que coincidan (`<img name="config">` sobreescribe `window.config` si el código no lo inicializó explícitamente). Se puede encadenar con `postMessage` o bypasses de CSP para escalar a XSS.
- **Ejemplo vulnerable:** `if (window.config.isAdmin) { ... }` donde `config` nunca se inicializó explícitamente en JS y depende de que no exista un elemento HTML con `id="config"` inyectable.
- **Remediación:** Inicializar explícitamente toda variable global usada para lógica de seguridad (`window.config = window.config || {}` no es suficiente — validar el tipo, ej. `typeof window.config === 'object' && !(window.config instanceof HTMLElement)`), no depender de convenciones de nombre de `id`/`name` de HTML para lógica sensible.
- **Severidad típica:** Media (por sí sola) a Alta (si se encadena con otro bypass para lograr XSS).

## Clickjacking
- **CWE:** CWE-1021 · **OWASP:** A05:2021 (aledaño)
- **Indicador:** Ausencia del header `X-Frame-Options` o de la directiva `frame-ancestors` en CSP, permitiendo que la página se embeba en un `<iframe>` de un sitio malicioso para engañar al usuario a hacer clic en algo distinto de lo que ve (incluye variantes recientes como "DoubleClickjacking", que explota el gap de tiempo entre `mousedown` y `onclick` para evadir protecciones tradicionales).
- **Remediación:** `frame-ancestors 'self'` en CSP (cubre más casos que `X-Frame-Options` y es el estándar recomendado hoy), o `X-Frame-Options: DENY/SAMEORIGIN` como fallback para navegadores viejos. Para flujos sensibles (confirmación de pago, cambio de permisos), no depender solo de temporización de eventos — usar confirmación explícita.
- **Severidad típica:** Media (depende de qué acción se pueda "clickjackear").

## Content Security Policy Insegura o Ausente
- **CWE:** CWE-1021, CWE-693 (protección ausente) · **OWASP:** A05:2021
- **Indicador:** CSP ausente, o presente pero con `unsafe-inline`/`unsafe-eval` en `script-src` (anula gran parte de la protección contra XSS), sin `object-src 'none'` (permite inyección vía `<object>`), con wildcards amplios (`script-src *`), o con un endpoint JSONP/open-redirect propio incluido en la allowlist (permite bypass vía ese endpoint).
- **Ejemplo vulnerable:** `Content-Security-Policy: script-src 'self' 'unsafe-inline'`
- **Remediación:** Usar nonces (`'nonce-...'`) o hashes (`'sha256-...'`) para scripts inline en vez de `unsafe-inline`; `object-src 'none'`; `default-src 'none'` como fallback y allowlist explícita de lo necesario; servir CSP vía header HTTP, no `<meta>` (cobertura más completa); no incluir en la allowlist ningún endpoint propio que sea JSONP o permita redirect abierto.
- **Severidad típica:** Media (ausente) a Alta (presente pero con `unsafe-inline`/`unsafe-eval`, da falsa sensación de protección).

## Almacenamiento Inseguro de Tokens en Cliente
- **CWE:** CWE-522 · **OWASP:** A07:2021
- **Indicador:** Token de sesión/JWT/refresh token guardado en `localStorage` o `sessionStorage` (accesible a cualquier script vía JS, incluido uno inyectado por XSS) en vez de una cookie `httpOnly`.
- **Ejemplo vulnerable:** `localStorage.setItem('token', jwt)`
- **Remediación:** Cookie `httpOnly` + `secure` + `sameSite` para el token de sesión; si se necesita un token accesible por JS (ej. para llamadas API desde SPA), usar uno de corta duración y aceptar el riesgo documentado, nunca el token de larga vida.
- **Severidad típica:** Alta (el impacto depende de si ya existe un XSS explotable en la misma app — reportar igual como hallazgo independiente, no condicionarlo a encontrar el XSS primero).

## Validación de Origen en postMessage
- **CWE:** CWE-346 · **OWASP:** A01:2021
- **Indicador:** Listener de `window.addEventListener('message', ...)` que procesa `event.data` sin verificar `event.origin` contra un valor esperado.
- **Ejemplo vulnerable:** `window.addEventListener('message', (e) => { eval(e.data) })`
- **Remediación:** Verificar `event.origin === 'https://dominio-esperado'` al inicio del handler, antes de usar `event.data`.
- **Severidad típica:** Alta (depende de qué hace el handler con el dato).

## Integridad de Recursos de Terceros Ausente (SRI)
- **CWE:** CWE-829 · **OWASP:** A08:2021
- **Indicador:** `<script src="https://cdn-externo/...">` o `<link>` a un recurso de un origen de terceros sin atributo `integrity` (Subresource Integrity).
- **Remediación:** Agregar `integrity="sha384-..."` + `crossorigin="anonymous"`, o self-host el recurso si es crítico.
- **Severidad típica:** Media.

## Enforcement de Seguridad Solo en Cliente
- **CWE:** CWE-602 · **OWASP:** A01:2021
- **Indicador:** Control de acceso (ocultar un botón, un route guard de React Router/Vue Router, un `if (user.role === 'admin')` en el componente) que decide qué se muestra, pero el endpoint/acción que invoca no repite la misma verificación en el servidor.
- **Ejemplo vulnerable:** Botón "Eliminar" oculto para no-admins en el frontend, pero `DELETE /api/users/:id` no valida el rol del solicitante.
- **Remediación:** Toda decisión de autorización debe repetirse en el servidor; el frontend solo mejora la UX, nunca es el control real.
- **Severidad típica:** Crítica (si el endpoint de backend es alcanzable directamente sin el check). Si no hay forma de confirmar el comportamiento del backend desde el código frontend, reportar con `confianza: media` y aclarar la suposición.

## Exposición de Datos Sensibles / Secretos en Bundle
- **CWE:** CWE-798, CWE-312 · **OWASP:** A02:2021
- **Indicador:** Credenciales, API keys o tokens escritos directamente en código que termina en el bundle de producción (`import.meta.env`/`process.env` inline en build client-side, constantes hardcodeadas).
- **Nota:** un secreto en el bundle de producción **ya es público** una vez servido — no es "hardcodeado sin desplegar" como en backend, es "hardcodeado y expuesto a cualquier visitante" (basta abrir devtools). Reportar con severidad Crítica igual, pero aclarar en la explicación que el vector es "cualquier visitante", no "acceso al repositorio". Si la clave es de un servicio que soporta scoping (ej. clave pública de Stripe, API key con permisos restringidos por dominio), verificar si es la variante pensada para ser pública antes de reportar — no todo valor en el bundle es un hallazgo.
- **Remediación:** Mover al backend cualquier llamada que requiera el secreto real; si la clave debe ser pública, confirmar que el servicio la trata como tal (scoping/rate-limit por dominio). Remitir a `env-config-audit` para el inventario completo — no duplicar ese análisis aquí.
- **Severidad típica:** Crítica.

## Dependencias con Versiones Vulnerables Conocidas
- **CWE:** CWE-1104 · **OWASP:** A06:2021
- **Indicador:** `package.json`/`package-lock.json` del frontend con versiones de librerías con vulnerabilidades públicamente conocidas y ampliamente documentadas.
- **Límite:** Sin consulta a CVE en línea — solo se reportan casos de conocimiento general y verificable por versión. Si hay duda, marcar `⚠️ Verificar manualmente` en vez de afirmar.
- **Remediación:** Actualizar a versión parchada, o correr `npm audit`/equivalente localmente.
- **Severidad típica:** Variable (depende de la CVE).

## Fuera de Alcance
- Ver `catalogo-backend.md` sección "Fuera de Alcance" (Insecure Design/lógica de negocio, ReDoS) — aplica igual a código frontend.
- **Prototype Pollution:** ver `catalogo-backend.md` — el patrón (merge recursivo sin filtrar `__proto__`) es idéntico en frontend (ej. parseo de query params en un merge de estado), reportar con el mismo CWE-1321 si aparece en código cliente.
