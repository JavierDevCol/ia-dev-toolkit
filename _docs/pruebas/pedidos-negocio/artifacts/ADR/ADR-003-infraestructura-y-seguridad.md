# ADR-003: Infraestructura Cloud, Redes y Seguridad

- **Estado:** Aprobado
- **Fecha:** 2026-09-30
- **Decisor:** User & Onad (Arquitecto de Soluciones) — autoaprobado en esta simulación.

## Contexto
El sitio es estático (ADR-001, ADR-002), sin backend propio ni datos sensibles que proteger (no hay pagos ni cuentas de usuario). La infraestructura debe ser la mínima necesaria para publicar el sitio de forma confiable y con HTTPS, sin costo recurrente relevante, dado que es un negocio pequeño sin presupuesto de TI.

## Opciones Evaluadas
1. **Opción A — Hosting estático gratuito con CDN y HTTPS automático (Vercel / Netlify / GitHub Pages) (Seleccionada):** Despliegue directo desde el repositorio Git, certificado TLS automático, CDN global incluido sin configuración adicional. Costo: $0 en el tier gratuito para este volumen.
2. **Opción B — VPS propio (ej. DigitalOcean droplet) con Nginx:** Requiere aprovisionar, parchear y monitorear un servidor Linux, configurar Nginx y renovar certificados manualmente (o con Certbot). Se descarta: introduce mantenimiento operativo que nadie en este proyecto tiene capacidad de sostener.
3. **Opción C — AWS S3 + CloudFront + WAF:** Técnicamente válida pero requiere configurar IAM, distribución CDN, políticas de bucket y WAF; complejidad y curva de aprendizaje desproporcionadas frente a un sitio estático de una sola página. Se descarta por sobre-ingeniería.

| Criterio | Opción A (Vercel/Netlify) | Opción B (VPS propio) | Opción C (AWS S3+CloudFront+WAF) |
| :--- | :--- | :--- | :--- |
| Costo | $0 | ~$5-6 USD/mes + tiempo de mantenimiento | Variable, requiere configuración experta |
| Mantenimiento operativo | Ninguno | Alto (parches, TLS, updates OS) | Medio (IAM, políticas) |
| HTTPS y CDN | Incluidos por defecto | Configuración manual | Configuración manual |
| Curva de aprendizaje | Baja | Media-alta | Alta |

## Decisión Aprobada
Se adopta **hosting estático gratuito con CDN y HTTPS automático** (Vercel o Netlify, indistintamente — se recomienda Netlify por simplicidad de configuración para sitios sin build complejo). No aplica topología de redes tipo VPC/subredes/API Gateway porque no existe backend propio que aislar.

### Topología de Red
- No aplica VPC, subredes públicas/privadas ni API Gateway: el hosting estático sirve directamente los archivos vía CDN con HTTPS forzado.
- El único "servicio externo" con el que se integra el sitio es WhatsApp, a través de un enlace `wa.me` (no es una integración de red gestionada por nosotros, es una URL estándar que el navegador/SO resuelve).

### Estrategia Security by Design
- **Autenticación/Autorización:** No aplica para clientes (no hay cuentas de usuario) ni para el catálogo (se edita vía archivo versionado en Git, protegido por el control de acceso del propio repositorio, no por un panel expuesto en internet).
- **Gestión de secretos:** No se requieren credenciales ni tokens en el sitio (no hay llamadas a APIs autenticadas). El número de WhatsApp del negocio es intencionalmente público, ya que es el canal de atención al cliente.
- **Validación de entrada:** El formulario de armado de pedido valida en el cliente (cantidades numéricas, campos requeridos) antes de generar el enlace `wa.me`, evitando mensajes malformados.
- **Transporte:** HTTPS forzado por la plataforma de hosting (redirección automática de HTTP a HTTPS).

## Consecuencias

### Positivas
- Superficie de ataque mínima: no hay servidor, base de datos ni API expuestos a internet.
- Cero costo de infraestructura y cero carga operativa de mantenimiento de servidores/certificados.
- Despliegue y rollback prácticamente instantáneos desde la plataforma de hosting.

### Negativas / Riesgos Aceptados
- Dependencia de un proveedor externo (Vercel/Netlify) y de su tier gratuito; si el negocio creciera mucho, se debería evaluar un plan pagado (riesgo aceptado, bajo impacto al volumen actual).
- Si en el futuro se agrega un webhook (ej. a Google Sheets, ver ADR-002), se deberá revisar en ese momento cómo proteger la URL/token del webhook; fuera de alcance de este ADR por no existir en v1.
