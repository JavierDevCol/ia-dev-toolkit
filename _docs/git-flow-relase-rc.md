Ciclo de Vida de Software y Gestión de RC
El flujo está diseñado sobre un pipeline de 5 entornos (DEVELOP → DES → PRU → PRE → PRO) respaldado por ramas de infraestructura independientes. La estrategia utiliza una rama Release Padre como línea base de la versión, y ramas RC (Release Candidate) como paquetes congelados de entrega y prueba.
       [ FEATURE ] (Tu código base)
            │
            ▼
      [ DEVELOP ]  ──► Entorno local/Dev (Validación técnica)
            │
            ▼
    [ Release Padre ] ──► Dueño de la versión (Línea base)
            │
            ▼
    [ RCs (rc.1, rc.2) ] ──► Paquetes congelados (Candidatos a pruebas)
            │
            ▼
[ DES ] ──► [ PRU ] ──► [ PRE ] ──► [ PRO ] (Rutas de ambientes del Banco)

Diagrama de Flujo Completo (Camino Feliz y Bugfix)
Este diagrama detalla cómo avanza una característica y exactamente qué pasa si QA detecta un error en el ambiente de pruebas (PRU):
  [ Feature: prueba-5 ]
           │
           ▼ (PR)
     [ DEVELOP ] ──────────────────────────────────────────┐
           │                                               │
           ▼ (Se crea rama versión base)                   │
   [ Release Padre ] <─────────────────────────────────┐   │
    (release/v1.5.0)                                   │   │
           │                                           │   │
           ├───► (Crea RC.1) ──► [ release/v1.5.0-rc.1 ]│   │
           │                               │           │   │
           │                               ▼           │   │
           │                         [ Env: DES ]      │   │
           │                               │           │   │
           │                               ▼           │   │
           │                         [ Env: PRU ]      │   │
           │                               │           │   │
           │                         ¿Tiene Bug?       │   │
           │                          /          \     │   │
           │                    (SÍ) /            \ (NO)   │
           │                        /              \       │
           │                       ▼               ▼       │
           │               [ Aplicar Fix ]   [ PROMOVER RC.2 ]
           │               en Release Padre        │       │
           │                       │               │       │
           │                       ▼               ▼       │
           └───► (Crea RC.2) ──► [ release/v1.5.0-rc.2 ]   │
                                           │               │
                                           ▼ (PR exitoso)  │
                                     [ DEVELOP ] <─────────┘
                                           │
                                           ▼ (PR exitoso)
                                     [ Env: DES ]
                                           │
                                           ▼
                                     [ Env: PRU ] (¡Aprobado por QA!)
                                           │
                                           ▼ (Se promueve el Release Padre)
                                     [ Env: PRE ] ──► Genera Tag: v1.5.0-PRE
                                           │
                                           ▼
                                     [ Env: PRO ] ──► Genera Tag: v1.5.0-PRO

Ejemplo Práctico de Extremo a Extremo
Escenario: Desarrollas la "Feature Prueba 5" (Versión v1.5.0)
Paso 1: Finalización en Local
Terminas tu código en la rama feature/prueba-5.
Abres un PR hacia la rama DEVELOP. Tu pipeline compila y despliega en el servidor DEVELOP donde haces tus pruebas iniciales.
Paso 2: Creación de la Versión Base (Padre)
Creas la rama padre release/v1.5.0 a partir de DEVELOP. Esta rama centralizará el código oficial de la entrega.
Paso 3: Entrega del Primer Candidato (RC.1)
A partir del padre, creas la rama release/v1.5.0-rc.1.
Ejecutas un PR desde release/v1.5.0-rc.1 hacia la rama del entorno DES. El banco realiza pruebas de integración. Todo marcha bien.
Promueves ese mismo paquete ejecutando el PR de release/v1.5.0-rc.1 hacia PRU. El equipo de QA inicia la certificación.
Paso 4: El Imprevisto (Gestión del Bug en PRU)
El problema: QA encuentra un error crítico en PRU usando el rc.1. El paquete rc.1 queda descartado.
La solución:
Te ubicas en la rama padre release/v1.5.0 y corriges el bug directamente ahí.
Creas el nuevo paquete candidato: release/v1.5.0-rc.2.
Pruebas el rc.2 en tu ambiente DEVELOP. Al funcionar correctamente, abres un PR de la rama padre release/v1.5.0 hacia DEVELOP para dejar el fix guardado en la historia del proyecto.
Entregas el nuevo paquete abriendo el PR de release/v1.5.0-rc.2 hacia DES y luego hacia PRU.
Paso 5: Certificación y Promoción Final (PRE y PRO)
QA certifica que el rc.2 solucionó el error y aprueba la entrega en PRU.
La promoción: Al estar aprobado el código, se procede a desplegar en los entornos superiores. Lo que viaja a PRE y PRO es la rama Release Padre (release/v1.5.0), ya que su código es idéntico al del rc.2 pero sin la nomenclatura de "candidato".
Inmutabilidad por Tags:
Al desplegar en PRE se estampa el Tag: v1.5.0-PRE.
Al desplegar en PRO (Producción) se estampa el Tag definitivo: v1.5.0-PRO.

Buenas Prácticas y Reglas de Oro para el Banco
Inyección de Configuración Externa: El código de la aplicación en el Release Padre debe ser exactamente el mismo para todos los entornos. Las contraseñas, URLs de bases de datos y llaves de acceso del banco deben ser inyectadas por el pipeline de infraestructura de cada entorno, nunca quemadas en el código fuente.
El Cierre de Git (Merge Back): Una vez que el Tag v1.5.0-PRO está en producción con éxito, debes fusionar la rama release/v1.5.0 hacia la rama principal de producción (main o master) y hacer un último PR hacia DEVELOP. Esto asegura que los fixes de última hora queden en la base del repositorio.
Limpieza de ramas: Las ramas temporales rc.1 y rc.2 se pueden borrar de Git tras el éxito en producción. Los Tags jamás se borran; actúan como la bitácora legal ante cualquier auditoría del banco.
Lo que se propaga a las ramas de los siguientes entornos (PRE y PRO) es el Release Padre (la rama/código), pero el despliegue físico en los servidores se ejecuta y se congela utilizando los Tags.
Para entenderlo de forma sencilla en el contexto de tu Git y tu infraestructura: la rama es el vehículo que transporta el código, pero el Tag es el candado de seguridad que exige el banco.
Aquí te detallo exactamente cómo se maneja esta propagación en las herramientas y en los entornos superiores:
1. En Git: Propagas el Release Padre (Ramas)
Para mover el código de un entorno a otro, utilizas el flujo de Pull Requests (PR) entre tus ramas fijas de infraestructura. El orden de propagación es el siguiente:
Abres un PR desde la rama release/v1.5.0 hacia la rama del entorno PRE.
Tras validar en PRE, abres un PR desde la rama release/v1.5.0 hacia la rama del entorno PRO.
Al hacer esto, aseguras que el código base de la aplicación sea exactamente el mismo que QA aprobó en la etapa del rc.2.
2. En el Servidor/Infraestructura: Propagas el Tag
Una vez que el PR es aprobado y el código del Release Padre se fusiona con la rama del entorno correspondiente, tu pipeline de CI/CD debe generar y estampar un Tag específico para ese momento.
Al fusionar en PRE: El pipeline genera automáticamente el Tag v1.5.0-PRE. El servidor de PRE se despliega apuntando a este Tag exacto.
Al fusionar en PRO: El pipeline genera el Tag final v1.5.0-PRO. El servidor de producción compila y despliega basándose únicamente en esta etiqueta de oro.
¿Por qué se hace así en un entorno bancario?
Garantía de Inmutabilidad: Si despliegas en producción apuntando a una "rama", corres el riesgo de que alguien suba un cambio de última hora a esa rama y altere el servidor de forma imprevista. Al desplegar apuntando a un Tag, el código queda "congelado en el tiempo". Aunque la rama siga avanzando, el Tag siempre representará el mismo código matemático exacto.
Trazabilidad para Auditoría: Si ocurre un incidente en producción en el futuro, el equipo de operaciones del banco no buscará la rama; buscará el Tag v1.5.0-PRO para saber con precisión milimétrica qué líneas de código se enviaron al servidor ese día.

