---
name: bmm-manual-tecnico
description: >
  Usa esta skill cuando el usuario pida crear, generar o documentar un
  manual técnico o funcional de instalación para un microservicio del
  ecosistema BancaPorWhatsapp de BMM.
compatibility: Requires Azure DevOps, HashiCorp Vault, Kubernetes
---

# Skill: Generación de Manual Técnico y Funcional – BancaPorWhatsapp BMM

## Descripción

Genera un documento Word (.docx) con el Manual Técnico y Funcional completo de un microservicio del ecosistema BancaPorWhatsapp de BMM, siguiendo la plantilla corporativa. El documento incluye: descripción del requerimiento, solución técnica, arquitectura, proceso de despliegue CI/CD, secrets de Vault, parametrización por ambiente, descripción funcional, modelo lógico, PT-007 y pruebas.

---

## PASO 1 – Recopilación de datos de entrada (OBLIGATORIO, hacer PRIMERO)

**Antes de leer cualquier archivo o código**, solicita al usuario los siguientes datos mediante preguntas directas en un solo mensaje. Presenta cada campo con su nombre, una descripción breve y si es opcional:

```
Para generar el Manual Técnico y Funcional necesito los siguientes datos:

OBLIGATORIOS:
1. [MICROSERVICIO]      Nombre del microservicio
                        Ejemplo: ms-banca-cdts
2. [HU_NUMERO]         Número de la Historia de Usuario
                        Ejemplo: WA2-002.2
3. [HU_TITULO]         Título / descripción corta de la HU
                        Ejemplo: Simulación de CDTs para Banca por WhatsApp
4. [PULL_REQUESTS]     Números de PR involucrados (separados por coma)
                        Ejemplo: 4488, 4490, 4521
5. [DESARROLLADOR]     Nombre del desarrollador o equipo
                        Ejemplo: Laboratorio FINTIA

OPCIONALES (presiona Enter para omitir):
6. [NUMERO_REQ]        Número del requerimiento/solicitud en el sistema
                        Ejemplo: 108091
7. [NUMERO_PASO]       Número del paso del proceso
                        Ejemplo: B_BMMATE007
8. [VAULT_FILE]        Ruta al archivo .txt con la estructura de secrets de Vault
                        Ejemplo: C:\Program Files\Notepad++\vault-cdts.txt
9. [NOTAS_EXTRA]       Notas adicionales o contexto especial para incluir en el manual
```

Espera la respuesta completa del usuario antes de continuar.

---

## PASO 2 – Recopilación automática de información

Con los datos del paso 1, ejecuta las siguientes acciones **en paralelo**:

### 2a. Explorar el microservicio
Usa el agente `Explore` (subagent_type=Explore) con esta instrucción:

```
Explora exhaustivamente D:\BMM\{MICROSERVICIO} y extrae:
1. Contenido completo de: build.gradle, settings.gradle, gradle.properties
2. Todos los application*.yml / application*.yaml
3. Dockerfile
4. deployment.yaml
5. azure-pipelines.yml (estructura completa)
6. db/migration/**/*.sql (si existe)
7. Clases principales: paquetes Java, entidades de dominio, puertos, servicios, consumidores, publicadores, adaptadores, configuraciones
8. Variables de entorno referenciadas en los YAMLs y en el código
```

### 2b. Git log y diff
Ejecuta via PowerShell en `D:\BMM\{MICROSERVICIO}`:
```powershell
git fetch origin
git log origin/des..origin/develop --oneline
git diff origin/des..origin/develop --name-status
```

### 2c. Leer archivo de Vault (si se proporcionó VAULT_FILE)
Lee el archivo con la herramienta Read. Extrae: rutas de cada secret y claves del JSON.

### 2d. Leer la plantilla de referencia (si está disponible)
Si existe `C:\Temp\pdf_content.txt`, léelo para mantener la estructura corporativa.

---

## PASO 3 – Construir el contexto del documento

Con toda la información recopilada, consolida en las siguientes variables que usarás en el script Python:

| Variable | Fuente |
|----------|--------|
| `MICROSERVICIO` | Entrada del usuario |
| `HU_NUMERO` | Entrada del usuario |
| `HU_TITULO` | Entrada del usuario |
| `DESARROLLADOR` | Entrada del usuario |
| `PRS_LIST` | Lista de tuplas `(PR#, commit, descripción)` del git log |
| `RAMA_DEPLOY` | Del pipeline: rama → ambiente (desarrollar tabla completa) |
| `VAULT_SECRETS` | Del archivo de Vault: lista de `(nombre_secreto, ruta, campos_json)` |
| `TABLAS_BD` | Del SQL de Flyway: DDL de cada tabla |
| `COLAS_RABBITMQ` | De los YAMLs y código: nombre, routing-key, propósito de cada cola |
| `TECNOLOGIAS` | Del build.gradle: spring boot version, java, dependencias clave |
| `FLUJO_DATOS` | Del código: cadena de clases desde entrada hasta salida |
| `INTEGRACIONES` | Del código y YAMLs: sistemas externos, tipo de conexión |

---

## PASO 4 – Generar el script Python y ejecutarlo

Genera un script Python en `C:\Temp\generar_manual_{MICROSERVICIO}.py` usando el **template base** de abajo, reemplazando todos los marcadores `<<...>>` con los datos recopilados. Luego ejecútalo con:

```powershell
py "C:\Temp\generar_manual_{MICROSERVICIO}.py"
```

El archivo de salida debe guardarse en `D:\BMM\MANUAL_TECNICO_FUNCIONAL_{MICROSERVICIO}.docx`.

---

## TEMPLATE BASE DEL SCRIPT PYTHON

El script usa `python-docx`. Instalar si es necesario: `py -m pip install python-docx -q`

```python
# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# ── Página ─────────────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Cm(21.59); section.page_height = Cm(27.94)
section.left_margin = section.right_margin = section.top_margin = section.bottom_margin = Cm(2.54)

# ── Colores BMM ────────────────────────────────────────────────────────────
AZUL    = RGBColor(0x00, 0x46, 0x9B)
GRIS    = RGBColor(0x40, 0x40, 0x40)
ROJO    = RGBColor(0xC0, 0x00, 0x00)

# ── Helpers ────────────────────────────────────────────────────────────────
def shd(cell, fill):
    tc = cell._tc; pr = tc.get_or_add_tcPr()
    s = OxmlElement('w:shd')
    s.set(qn('w:val'),'clear'); s.set(qn('w:color'),'auto'); s.set(qn('w:fill'),fill)
    pr.append(s)

def h(text, level, color=None):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.color.rgb = color or AZUL; r.font.bold = True

def par(text='', bold=False, italic=False, size=10, color=None, align=None):
    p = doc.add_paragraph(); r = p.add_run(text)
    r.font.size=Pt(size); r.font.bold=bold; r.font.italic=italic
    if color: r.font.color.rgb=color
    if align: p.alignment=align
    return p

def thead(table, cols, bg='004699'):
    row = table.rows[0]
    for i,c in enumerate(cols):
        cell=row.cells[i]; cell.text=c; shd(cell,bg)
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold=True; r.font.color.rgb=RGBColor(255,255,255); r.font.size=Pt(9)
            p.alignment=WD_ALIGN_PARAGRAPH.CENTER

def trow(table, values, size=9):
    row=table.add_row()
    for i,v in enumerate(values):
        row.cells[i].text=str(v)
        for p in row.cells[i].paragraphs:
            for r in p.runs: r.font.size=Pt(size)
    return row

def code(text):
    p=doc.add_paragraph(); r=p.add_run(text)
    r.font.name='Courier New'; r.font.size=Pt(8); r.font.color.rgb=RGBColor(0x1F,0x1F,0x1F)
    pr=p._p.get_or_add_pPr(); s=OxmlElement('w:shd')
    s.set(qn('w:val'),'clear'); s.set(qn('w:color'),'auto'); s.set(qn('w:fill'),'F2F2F2')
    pr.append(s)

def new_table(cols, col_headers, bg='004699'):
    t=doc.add_table(rows=1,cols=cols); t.style='Table Grid'
    t.alignment=WD_TABLE_ALIGNMENT.CENTER; thead(t,col_headers,bg); return t

# ══════════════════════════════════════════════════════════════════════════
# DATOS DEL DOCUMENTO  ← Claude reemplaza estas variables
# ══════════════════════════════════════════════════════════════════════════
MICROSERVICIO   = "<<MICROSERVICIO>>"
HU_NUMERO       = "<<HU_NUMERO>>"
HU_TITULO       = "<<HU_TITULO>>"
DESARROLLADOR   = "<<DESARROLLADOR>>"
NUMERO_REQ      = "<<NUMERO_REQ>>"          # "" si no aplica
NUMERO_PASO     = "<<NUMERO_PASO>>"         # "" si no aplica
FECHA           = "<<FECHA_HOY>>"           # dd/mm/yyyy
PRS             = [
    # ("PR XXXX", "commit_hash", "descripción del PR"),
    <<LISTA_PRS>>
]
TECNOLOGIAS     = [
    # ("Componente", "Tecnología / Versión"),
    <<LISTA_TECNOLOGIAS>>
]
VAULT_SECRETS   = [
    # {
    #   "nombre": "nombre-del-secreto",
    #   "ruta": "{env}/ms-xxx/nombre-del-secreto",
    #   "descripcion": "Para qué sirve",
    #   "campos": [
    #       ("clave_json", "descripción del valor"),
    #   ]
    # },
    <<LISTA_VAULT_SECRETS>>
]
TABLAS_BD       = [
    # {
    #   "nombre": "nombre_tabla",
    #   "descripcion": "para qué sirve",
    #   "ddl": "CREATE TABLE ...",
    #   "columnas": [("campo","tipo","long","requerido","descripcion")]
    # },
    <<LISTA_TABLAS_BD>>
]
COLAS_RABBIT    = [
    # ("nombre.cola", "routing.key", "durable", "dlx/rk-dlx o -", "Propósito: ENTRADA/SALIDA/ERROR"),
    <<LISTA_COLAS_RABBIT>>
]
INTEGRACIONES   = [
    # ("Sistema / Microservicio", "Tipo y conexión", "Descripción"),
    <<LISTA_INTEGRACIONES>>
]
FLUJO_DATOS_TXT = """<<FLUJO_DATOS>>"""
CADENA_LLAMADAS = """<<CADENA_LLAMADAS>>"""
DESCRIPCION_REQ = """<<DESCRIPCION_REQUERIMIENTO>>"""
DESCRIPCION_SOL = """<<DESCRIPCION_SOLUCION>>"""
COMPONENTES_SOL = [
    # "Descripción de cada componente entregado"
    <<LISTA_COMPONENTES>>
]
CAMPOS_ENTRADA  = [
    # ("campo", "Tipo", "Requerido", "Descripción"),
    <<LISTA_CAMPOS_ENTRADA>>
]
CAMPOS_SALIDA   = [
    # ("campo", "Tipo", "Descripción"),
    <<LISTA_CAMPOS_SALIDA>>
]
RESTRICCIONES   = [
    # "Restricción funcional o técnica",
    <<LISTA_RESTRICCIONES>>
]
# ══════════════════════════════════════════════════════════════════════════

# ── PORTADA ───────────────────────────────────────────────────────────────
for _ in range(3): doc.add_paragraph()
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('MANUAL TÉCNICO Y FUNCIONAL')
r.font.bold=True; r.font.size=Pt(22); r.font.color.rgb=AZUL

p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run(MICROSERVICIO); r.font.bold=True; r.font.size=Pt(16); r.font.color.rgb=GRIS

p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run(HU_TITULO); r.font.size=Pt(13); r.font.color.rgb=GRIS

doc.add_paragraph()
t=doc.add_table(rows=6,cols=2); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
portada=[
    ('Número del requerimiento/solicitud:', NUMERO_REQ or 'N/A'),
    ('Número del paso:',                    NUMERO_PASO or 'N/A'),
    ('Historia de usuario:',                HU_NUMERO + ' – ' + HU_TITULO),
    ('Pull Requests:',                       ', '.join(p[0] for p in PRS)),
    ('Desarrollador / Equipo:',             DESARROLLADOR),
    ('Fecha de creación:',                  FECHA),
]
for i,(k,v) in enumerate(portada):
    row=t.rows[i]; row.cells[0].text=k; row.cells[1].text=v
    shd(row.cells[0],'D9E1F2')
    for cell in row.cells:
        for pp in cell.paragraphs:
            for rr in pp.runs: rr.font.size=Pt(10)
    for pp in row.cells[0].paragraphs:
        for rr in pp.runs: rr.font.bold=True

doc.add_page_break()

# ── 1. DESCRIPCIÓN DEL REQUERIMIENTO ─────────────────────────────────────
h('1. Descripción del Requerimiento', 2)
par(DESCRIPCION_REQ, size=10)

# ── 2. SOLUCIÓN AL REQUERIMIENTO ─────────────────────────────────────────
h('2. Solución al Requerimiento', 2)
par(DESCRIPCION_SOL, size=10)
par('Componentes entregados:', bold=True, size=10)
for c in COMPONENTES_SOL:
    p=doc.add_paragraph(style='List Bullet'); r=p.add_run(c); r.font.size=Pt(10)

# 2.1 Versionamiento
h('2.1. Versionamiento', 3)
t=new_table(3,['PR #','Commit','Descripción'])
for pr in PRS: trow(t, pr)

# 2.2 Arquitectura / Tecnologías
h('2.2. Arquitectura y Tecnologías', 3)
t=new_table(2,['Componente','Tecnología / Versión'])
for row in TECNOLOGIAS: trow(t, row)
doc.add_paragraph()
par('Flujo de datos:', bold=True, size=10)
code(FLUJO_DATOS_TXT)

doc.add_page_break()

# ── 3. MANUAL TÉCNICO ─────────────────────────────────────────────────────
h('MANUAL TÉCNICO Y FUNCIONAL', 1)
h('3. Manual Técnico', 2)

# 3.1 Prerrequisitos
h('3.1. Prerrequisitos de Infraestructura', 3)
par('Antes de ejecutar el pipeline, verificar que estén disponibles:', size=10)
prereqs=[
    ('AWS EKS','Cluster Kubernetes activo para el ambiente destino.'),
    ('AWS ECR','Repositorio de imágenes Docker disponible.'),
    ('HashiCorp Vault','Instancia disponible con los secrets creados (ver sección 3.2).'),
    ('RabbitMQ','Broker disponible con las colas configuradas (ver sección 6.1).'),
    ('Redis','Instancia disponible para caché de tokens.'),
    ('PostgreSQL','Base de datos disponible. Flyway aplicará el schema automáticamente.'),
    ('Agente Azure DevOps','Configurado con acceso a red interna, AWS CLI y kubectl.'),
    ('Secure Files','Certificados cargados en Azure DevOps (ver sección 3.4).'),
]
t=new_table(2,['Componente','Requisito'])
for row in prereqs: trow(t, row)

# 3.2 Vault Secrets
h('3.2. Configuración de Secrets en HashiCorp Vault', 3)
par('Los secrets deben crearse antes del despliegue. La ruta varía según el ambiente (dev/, pru/, pre-prod/, pro/):', size=10)

# Tabla de rutas por ambiente
t=new_table(3,['Ambiente','Perfil Spring','Rutas de Secrets en Vault'])
vault_env_rows=[
    ('Desarrollo','develop','\n'.join(f"vault://dev/{s['ruta']}" for s in VAULT_SECRETS)),
    ('Pruebas','pru','\n'.join(f"vault://pru/{s['ruta']}" for s in VAULT_SECRETS)),
    ('Pre-producción','prepro','\n'.join(f"vault://pre-prod/{s['ruta']}" for s in VAULT_SECRETS)),
    ('Producción','pro','\n'.join(f"vault://pro/{s['ruta']}" for s in VAULT_SECRETS)),
]
for row in vault_env_rows: trow(t, row, size=8)

doc.add_paragraph()
par('Estructura de cada secret (JSON de creación):', bold=True, size=10)

for s in VAULT_SECRETS:
    par(f"Secret: {s['nombre']}", bold=True, size=10, color=AZUL)
    t2=doc.add_table(rows=1,cols=2); t2.style='Table Grid'
    thead(t2,['Atributo','Valor'])
    trow(t2,('Ruta en Vault', '{env}/' + s['ruta']), size=9)
    trow(t2,('Descripción', s['descripcion']), size=9)
    for cell in t2.rows[1].cells: shd(cell,'EBF3FB')
    for cell in t2.rows[2].cells: shd(cell,'EBF3FB')
    par('JSON a cargar en Vault:', size=9, italic=True)
    json_lines = '{\n' + ',\n'.join(f'  "{k}": "<{v}>"' for k,v in s['campos']) + '\n}'
    code(json_lines)

# Tabla de prefijos por ambiente
par()
par('Prefijos de ruta por ambiente:', bold=True, size=9, color=ROJO)
t=new_table(3,['Ambiente','Prefijo','Ejemplo'])
env_pref=[('Desarrollo','dev','dev/'+VAULT_SECRETS[0]['ruta'] if VAULT_SECRETS else ''),
          ('Pruebas','pru','pru/'+VAULT_SECRETS[0]['ruta'] if VAULT_SECRETS else ''),
          ('Pre-producción','pre-prod','pre-prod/'+VAULT_SECRETS[0]['ruta'] if VAULT_SECRETS else ''),
          ('Producción','pro','pro/'+VAULT_SECRETS[0]['ruta'] if VAULT_SECRETS else '')]
for row in env_pref: trow(t, row, size=9)

# Comandos AppRole
h('3.2.1. Crear rol AppRole en Vault', 4)
par('Ejecutar por ambiente desde la máquina del agente:', size=10)
code(
    '# Variables de entorno según ambiente\n'
    'set VAULT_ADDR=https://vault-middle-{env}.bmm.com/\n'
    'set VAULT_TOKEN=<token_admin>\n\n'
    'vault auth enable approle\n\n'
    f'vault write auth/approle/role/{MICROSERVICIO} ^\n'
    f'    token_policies="politica-{MICROSERVICIO},politica-certificados" ^\n'
    '    token_ttl=1h token_max_ttl=4h\n\n'
    f'# Obtener role-id (guardar en Library ADO → VAULT_ROLE_ID)\n'
    f'vault read auth/approle/role/{MICROSERVICIO}/role-id\n\n'
    f'# Obtener secret-id (guardar en Library ADO → VAULT_SECRET_ID)\n'
    f'vault write -f auth/approle/role/{MICROSERVICIO}/secret-id'
)

# 3.3 Library Variables
h('3.3. Library Variables en Azure DevOps', 3)
par(f'Grupo de variables: {MICROSERVICIO}-{{env}}  (ej: {MICROSERVICIO}-develop)', size=10)
t=new_table(4,['Variable','Descripción','Ejemplo','Secreto'])
lib_vars=[
    ('AZDO_AGENTPOOL_BUILD','Pool de agentes de build','bmm-agents-linux','No'),
    ('AWS_ACCOUNT_ID','ID de cuenta AWS','123456789012','Sí'),
    ('AWS_REGION','Región AWS','us-east-1','No'),
    ('DOCKER_REPO_NAME',f'Repositorio ECR',MICROSERVICIO,'No'),
    ('EKS_CLUSTER_NAME','Nombre del cluster EKS',f'bmm-kubernetes-{{env}}','No'),
    ('K8S_NAMESPACE','Namespace Kubernetes','banca-whatsapp','No'),
    ('K8S_DEPLOY_NAME','Nombre del Deployment',MICROSERVICIO,'No'),
    ('K8S_REPLICAS','Número de réplicas','1','No'),
    ('K8S_CONTAINER_PORT','Puerto interno del contenedor','8080','No'),
    ('K8S_EXPOSE_PORT','Puerto expuesto por el Service','8080','No'),
    ('K8S_SVC_TYPE','Tipo de Service K8s','ClusterIP','No'),
    ('VAULT_HOST','Host de Vault (sin https://)','vault-middle-des.bmm.com','No'),
    ('VAULT_ROLE_ID','AppRole role-id del microservicio','<obtenido de vault>','Sí'),
    ('VAULT_SECRET_ID','AppRole secret-id del microservicio','<obtenido de vault>','Sí'),
    ('IP_NAT','IP NAT para hostAliases del pod','10.x.x.x','No'),
    ('HOST_NAT','Hostname NAT para hostAliases','core-bancario.interno','No'),
    ('SONARQ_SONARQUBE','Service Connection SonarQube (solo develop)','SonarQube-BMM','No'),
    ('SONARQ_CLI_PROJECT_KEY','Clave proyecto SonarQube',MICROSERVICIO,'No'),
    ('SONARQ_CLI_SOURCES','Directorio fuente Sonar','microservicio','No'),
    ('SONARQ_EXCLUSIONS','Exclusiones Sonar','**/test/**,**/build/**','No'),
    ('DTRACK_SC','Service Connection Dependency Track','DTrack-BMM','No'),
    ('DTRACK_PROJ_NAME','Proyecto en Dependency Track',MICROSERVICIO,'No'),
    ('LIB_BANCA_TRANSVERSALES_USERNAME','Usuario Azure Artifacts','<usuario>','Sí'),
    ('LIB_BANCA_TRANSVERSALES_PASSWORD','PAT Azure Artifacts','<pat>','Sí'),
]
for row in lib_vars:
    r=trow(t, row, size=8)
    if row[3]=='Sí': shd(r.cells[3],'FFE0E0')

# 3.4 Secure Files
h('3.4. Secure Files Requeridos', 3)
t=new_table(3,['Archivo','Descripción','Stage'])
sf=[
    ('ca-vault.pem','Certificado CA que firmó el cert de Vault. Se importa al truststore Java del contenedor.','Push_Docker'),
    ('servidor-vault.pem','Certificado TLS del servidor Vault. Se crea como Secret TLS en Kubernetes.','Deploy'),
    ('servidor-vault.key','Clave privada del cert del servidor Vault.','Deploy'),
]
for row in sf: trow(t, row, size=9)
par('Cargar en: Azure DevOps → Pipelines → Library → Secure files → + Secure file', size=9, italic=True)

# 3.5 Pipeline CI/CD
h('3.5. Proceso de Despliegue (Pipeline CI/CD)', 3)
par('Pipeline azure-pipelines.yml – 3 stages secuenciales:', size=10)
t=new_table(4,['Stage','Nombre','Descripción','Pasos principales'])
pipeline_stages=[
    ('1','Build – Compilar',
     'Compila, ejecuta pruebas de calidad y empaqueta el JAR.',
     '1. Verificar Java/Gradle\n2. Instalar y ejecutar Gitleaks (solo develop)\n'
     '3. Generar BOM CycloneDX\n4. Gradle test + jacocoTestReport\n'
     '5. Publicar resultados JUnit y cobertura\n6. Upload BOM a Dependency Track\n'
     '7. PIT Mutation Testing\n8. SonarQube (prepare→analyze→publish→break)\n'
     '9. gradle clean build → JAR\n10. Publicar artefacto "code"'),
    ('2','Push_Docker – Push a ECR',
     'Construye imagen Docker y la sube a ECR.',
     '1. Descargar artefacto\n2. Descargar ca-vault.pem\n'
     '3. docker build (--build-arg CA_CERT_PATH)\n4. ECR Push tag=$(Build.BuildNumber)'),
    ('3','Deploy – Desplegar en EKS',
     'Aplica el manifiesto K8s en el cluster EKS.',
     '1. Descargar artefacto\n2. Replace tokens #{...}# en deployment.yaml\n'
     '3. Descargar servidor-vault.pem y .key\n4. kubectl create secret tls\n'
     '5. aws eks update-kubeconfig\n6. kubectl apply -f deployment.yaml\n'
     '7. kubectl get pods (verificación)'),
]
for row in pipeline_stages: trow(t, row, size=8)

# Estrategia de ramas
doc.add_paragraph()
par('Estrategia de ramas y mapeo a ambientes:', bold=True, size=10)
par((
    'La rama release/x.x.x actúa como puente de validación entre develop y des. '
    'NO es permanente: se crea desde develop, se despliega en des para validación, '
    'los fixes se hacen DIRECTAMENTE sobre ella, y se elimina una vez que des aprueba.'
), size=10)

t=new_table(5,['Rama','Patrón','Ambiente','Perfil Spring','Permanente'])
ramas_rows=[
    ('develop',       'develop',      'develop', 'develop', 'Sí'),
    ('release/x.x.x','release/*',    'des',     'des',     'No – se elimina tras aprobación'),
    ('des',           'des',          'des',     'des',     'Sí'),
    ('pru',           'pru',          'pru',     'pru',     'Sí'),
    ('prepro',        'prepro',       'prepro',  'prepro',  'Sí'),
    ('main/master',   'main o master','pro',     'pro',     'Sí'),
]
for row in ramas_rows:
    r=trow(t, row, size=9)
    if 'No' in row[4]: shd(r.cells[4],'FFEB9C')

doc.add_paragraph()
par('Ciclo de vida de release/:', bold=True, size=10, color=AZUL)
code(
    'PASO 1 – Creación: se crea release/x.x.x desde develop cuando está lista para des.\n'
    'PASO 2 – Despliegue: el pipeline despliega en des para validación.\n'
    'PASO 3 – Correcciones: bugs/mejoras encontrados en des se commiten sobre release/.\n'
    '          Cada commit redespliega automáticamente en des.\n'
    'PASO 4 – Aprobación: des aprueba → release/x.x.x se elimina → se promueve a des → pru → prepro → pro.\n\n'
    'IMPORTANTE: nunca volver a develop para fixes del ciclo de validación en des.'
)

# 3.6 Verificación
h('3.6. Verificación del Despliegue', 3)
code(
    '# Conectar al cluster\n'
    'aws eks update-kubeconfig --name bmm-kubernetes-{env} --region us-east-1\n\n'
    f'# Verificar pod Running\n'
    f'kubectl get pods -n {{K8S_NAMESPACE}} | grep {MICROSERVICIO}\n\n'
    f'# Ver logs (buscar "Started Application")\n'
    f'kubectl logs -n {{K8S_NAMESPACE}} deployment/{MICROSERVICIO} --tail=50\n\n'
    '# Health check (ajustar context-path si difiere)\n'
    f'kubectl port-forward -n {{K8S_NAMESPACE}} deployment/{MICROSERVICIO} 8080:8080\n'
    'curl http://localhost:8080/actuator/health\n'
    '# Esperado: {"status":"UP"}'
)

# 3.7 Parametrización
h('3.7. Parametrización por Ambiente', 3)
t=new_table(6,['Parámetro','develop','des\n(via release/)','pru','prepro','pro'])
param_rows=[
    ('Rama de origen',      'develop',           'release/x.x.x',      'des',           'pru',           'prepro'),
    ('Perfil Spring',       'develop',           'des',                 'pru',           'prepro',        'pro'),
    ('Vault path prefix',   'dev/',              'dev/',                'pru/',          'pre-prod/',     'pro/'),
    ('K8S_REPLICAS',        '1',                 '1',                   '1',             '2',             '2'),
    ('SonarQube',           'Sí',                'No',                  'No',            'No',            'No'),
    ('Gitleaks',            'Sí',                'No',                  'No',            'No',            'No'),
    ('PIT Mutation',        'Sí',                'No',                  'No',            'No',            'No'),
    ('logging.level',       'INFO',              'DEBUG',               'DEBUG',         'INFO',          'INFO'),
    ('Library ADO group',   f'{MICROSERVICIO}-develop', f'{MICROSERVICIO}-des', f'{MICROSERVICIO}-pru', f'{MICROSERVICIO}-prepro', f'{MICROSERVICIO}-pro'),
]
for prow in param_rows:
    r=trow(t, prow, size=8)
    shd(r.cells[2],'FFF2CC')  # highlight columna des/release

doc.add_page_break()

# ── 4. DESCRIPCIÓN FUNCIONAL ──────────────────────────────────────────────
h('4. Descripción Funcional Detallada', 2)
h(f'4.1. Funcionalidad: {HU_TITULO}', 3)

h('4.1.1. Campos de Entrada', 4)
t=new_table(4,['Campo','Tipo','Requerido','Descripción'])
for row in CAMPOS_ENTRADA: trow(t, row, size=9)

h('4.1.2. Campos de Salida', 4)
t=new_table(3,['Campo','Tipo','Descripción'])
for row in CAMPOS_SALIDA: trow(t, row, size=9)

h('4.1.3. Restricciones', 4)
for r in RESTRICCIONES:
    p=doc.add_paragraph(style='List Bullet'); rr=p.add_run(r); rr.font.size=Pt(10)

doc.add_page_break()

# ── 5. INTERACCIONES ──────────────────────────────────────────────────────
h('5. Interacciones con Otras Funcionalidades', 2)
t=new_table(3,['Integración / Sistema','Tipo y Conexión','Descripción'])
for row in INTEGRACIONES: trow(t, row, size=8)

doc.add_page_break()

# ── 6. MODELO LÓGICO ──────────────────────────────────────────────────────
h('MODELO LÓGICO', 1)
h('6. Descripción de Tablas', 2)
for tabla in TABLAS_BD:
    par(f"Tabla: {tabla['nombre']}", bold=True, size=10, color=AZUL)
    par(f"Descripción: {tabla['descripcion']}", size=10)
    code(tabla['ddl'])
    t=new_table(5,['Campo','Tipo','Longitud','Requerido','Descripción'])
    for col in tabla['columnas']: trow(t, col, size=9)
    doc.add_paragraph()

h('6.1. Configuración de Colas RabbitMQ', 3)
t=new_table(5,['Nombre de Cola','Routing Key','Durable','DLX','Propósito'])
for row in COLAS_RABBIT: trow(t, row, size=8)

h('7. Cadena de Llamadas', 2)
code(CADENA_LLAMADAS)

doc.add_page_break()

# ── 8. PT-007 ─────────────────────────────────────────────────────────────
h('8. Desarrollos de Interfaces al Core Bancario', 2)
h('8.1. Actas de Reuniones con Seguridad de la Información', 3)
par('Solicitar consecutivo FM-005 a: solicitudes.tecnologicas@bmm.com.co', size=10, italic=True)

h('8.2. Cumplimiento PT-007', 3)
t=new_table(4,['PT-007','Descripción','Cumple','Evidencia'])
pt007=[
    ('7.10.2.6', 'Lineamientos para desarrollo de software revisados por Gerencia de Riesgos.','Sí','Pipeline con SonarQube, PIT y JaCoCo configurados.'),
    ('7.10.2.7', 'Vincular seguridad de la información en el diseño de interfaces al Core.','Sí','Peer review incluido. Acta FM-005.'),
    ('7.10.2.8', 'Controles según sensibilidad de datos en interfaces al Core.','Sí','Encriptación JWE/RSA. SanitizadorDatos en logs.'),
    ('7.10.2.9', 'Cifrado vigente para información confidencial en interfaces.','Sí','Encriptación JWE/RSA. Certificados vía Vault.'),
    ('7.10.2.10','Controles de entrada, procesamiento y salida.','Sí','ValidadorArgumento en dominio. Fail-fast en propiedades.'),
    ('7.10.2.11','Verificar exactitud y validez de datos de transacciones.','Sí','Tests unitarios y de mutación cubren validaciones.'),
    ('7.10.2.12','Pruebas en ambientes antes de producción.','Sí','Pipeline: develop → des → pru → prepro → pro.'),
    ('7.10.2.13','Evitar configuraciones por defecto.','Sí','Todos los valores provienen de Vault o variables de entorno.'),
    ('7.10.2.14','No quemar usuarios en código fuente.','Sí','Gitleaks escanea automáticamente en el pipeline.'),
    ('7.10.2.15','Depuración de privilegios desde pruebas.','Sí','AppRole con permisos mínimos por ambiente.'),
    ('7.10.2.16','No almacenar SQL en BD.','Sí','Sin stored procedures. Solo Flyway para DDL.'),
    ('7.10.2.17','Paneles de mantenimiento para parámetros frecuentes.','N/A','Parámetros gestionados vía Vault y Azure DevOps Library.'),
    ('7.10.2.19','Ocultar/ofuscar PAN.','N/A','El microservicio no maneja números PAN.'),
]
for row in pt007:
    r=trow(t, row, size=8)
    bg='C6EFCE' if row[2]=='Sí' else ('FFEB9C' if row[2]=='N/A' else 'FFC7CE')
    shd(r.cells[2], bg)

doc.add_page_break()

# ── 9. PRUEBAS ────────────────────────────────────────────────────────────
h('9. Pruebas al Desarrollo', 2)
t=new_table(3,['Tipo de Prueba','Herramienta','Descripción'])
pruebas_rows=[
    ('Unitarias','JUnit 5 + Mockito','Pruebas aisladas de cada clase de dominio y aplicación.'),
    ('Integración','Spring Boot Test + H2','Pruebas de adaptadores con infraestructura en memoria.'),
    ('Arquitectura','ArchUnit','Valida que las capas no tengan dependencias cruzadas indebidas.'),
    ('Cobertura','JaCoCo + SonarQube','Reportes XML enviados a SonarQube. Objetivo: >80%.'),
    ('Mutación','PIT Mutation Testing','Valida efectividad de pruebas unitarias. Objetivo: >70%.'),
    ('Secretos','Gitleaks v8.28.0','Detecta credenciales expuestas en el historial de commits.'),
    ('Dependencias','Dependency Track / OWASP','Detecta vulnerabilidades (CVEs) en dependencias vía BOM CycloneDX.'),
    ('Estático','SonarQube','Detecta code smells, bugs, vulnerabilidades y cobertura insuficiente.'),
]
for row in pruebas_rows: trow(t, row, size=9)

doc.add_paragraph()
par('Checklist de verificación post-despliegue:', bold=True, size=10)
checklist=[
    'Pod en estado Running en el namespace correspondiente.',
    'Endpoint /actuator/health con respuesta {"status":"UP"}.',
    'Logs del pod confirman conexión exitosa con Vault y carga de secrets.',
    'Publicar mensaje de prueba en la cola de entrada y verificar respuesta en la cola de salida.',
    'Verificar en Redis que los tokens de sesión se almacenan correctamente.',
    'Verificar en PostgreSQL que Flyway aplicó las migraciones.',
]
for c in checklist:
    p=doc.add_paragraph(style='List Bullet'); r=p.add_run(c); r.font.size=Pt(10)

# ── 10. ANEXOS ────────────────────────────────────────────────────────────
h('10. Anexos', 2)
t=new_table(2,['Artefacto','Descripción / Ubicación'])
anexos=[
    ('azure-pipelines.yml',   f'Pipeline CI/CD. Repositorio: {MICROSERVICIO}, rama develop.'),
    ('deployment.yaml',       'Manifiesto Kubernetes. Raíz del repositorio.'),
    ('Dockerfile',            'Imagen Docker (amazoncorretto:21-alpine). Raíz del repositorio.'),
    ('Migraciones Flyway',    'microservicio/src/main/resources/db/migration/DDL/'),
    ('BOM CycloneDX',         'microservicio/build/reports/bom.xml'),
    ('Reportes JaCoCo',       'microservicio/dominio|infraestructura/build/reports/jacoco/'),
    ('Reportes PIT',          'microservicio/dominio|infraestructura/build/reports/pitest/'),
    ('Repositorio ADO',       f'https://dev.azure.com/GestionRequerimientos/BancaPorWhatsappCICD/_git/{MICROSERVICIO}'),
]
for row in anexos: trow(t, row, size=9)

# ── 11. CONTROL DE VERSIONES ──────────────────────────────────────────────
h('11. Control de Versiones del Documento', 2)
t=new_table(4,['Versión','Fecha','Descripción','Autor'])
trow(t,('1.0','01/01/2015','Creación del documento plantilla','BMM'))
trow(t,('2.0','18/01/2023','Modificación de plantilla, PT-007, versionamiento y arquitectura','Dirección de Aplicaciones'))
trow(t,('3.0','26/01/2023','Modificación en el formato, versionamiento y parametrización','Dirección de Aplicaciones'))
trow(t,('4.0', FECHA, f'Documentación de {MICROSERVICIO} – HU {HU_NUMERO}: {HU_TITULO}', DESARROLLADOR))

# ── GUARDAR ────────────────────────────────────────────────────────────────
output = rf'D:\BMM\MANUAL_TECNICO_FUNCIONAL_{MICROSERVICIO}.docx'
doc.save(output)
print(f'Documento guardado en: {output}')
```

---

## PASO 5 – Validación y entrega

1. Verifica que el archivo fue generado: `Get-Item "D:\BMM\MANUAL_TECNICO_FUNCIONAL_{MICROSERVICIO}.docx"`
2. Informa al usuario la ruta del archivo generado.
3. Si falló la generación, muestra el traceback completo y corrige el script.
4. Si alguna sección quedó con datos genéricos por falta de información, señálaselo al usuario y pídele los datos faltantes.

---

## Notas importantes

- **No generes el manual sin recopilar los datos del Paso 1 primero.** Si el usuario solo dice "genera el manual", pregunta todos los campos antes de continuar.
- El script Python usa **python-docx** (no docx-js). Si no está instalado: `py -m pip install python-docx -q`
- El archivo de salida siempre va a `D:\BMM\MANUAL_TECNICO_FUNCIONAL_{MICROSERVICIO}.docx`
- Si el usuario proporciona un archivo de Vault, sus rutas y claves tienen **prioridad** sobre las inferidas del código.
- La columna `des (via release/)` de la tabla de parametrización siempre va resaltada en amarillo para visibilidad.
- Los commits de fixes/mejoras durante validación en `des` se hacen sobre `release/`, nunca sobre `develop`.
