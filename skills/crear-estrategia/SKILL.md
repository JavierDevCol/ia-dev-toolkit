---
name: crear-estrategia
description: >
  Skill para crear estrategias de interacción en ms-banca-conversacion.
  Genera clases Java que extienden EstrategiaBase (Template Method + FSM),
  registra beans en MotorFsmConfiguration, agrega etapas al enum EtapaInteraccion,
  crea enums de opciones de menú y genera tests unitarios.
  Triggers: crear estrategia, nueva estrategia, agregar etapa, nuevo flujo conversacional,
  nueva etapa FSM, strategy, add strategy, create strategy.
compatibility: Requires specific codebase structure (ms-banca-conversacion)
---

# Crear Estrategia — ms-banca-conversacion

Genera estrategias de interacción para la máquina de estados finita (FSM) del chatbot de WhatsApp.

## Contexto

Cada estrategia es un nodo de la FSM identificado por el par `(EtapaInteraccion, DisparadorDeEstrategia)`. Todas extienden `EstrategiaBase` (Template Method) que orquesta auditoría, reintentos, desborde a agente humano y envío de mensajes WhatsApp.

## Rutas del proyecto

```
DOMINIO  = ms-banca-conversacion/microservicio/dominio/src/main/java/co/com/bmm
INFRA    = ms-banca-conversacion/microservicio/infraestructura/src/main/java/co/com/bmm
TESTS    = ms-banca-conversacion/microservicio/dominio/src/test/java/co/com/bmm
```

| Archivo | Ruta |
|---------|------|
| EstrategiaBase | `{DOMINIO}/maquina_estados/estrategias/EstrategiaBase.java` |
| EstrategiaDeInteraccionPorEtapa | `{DOMINIO}/puerto/EstrategiaDeInteraccionPorEtapa.java` |
| DependenciasEstrategiaBase | `{DOMINIO}/maquina_estados/estrategias/DependenciasEstrategiaBase.java` |
| EtapaInteraccion | `{DOMINIO}/modelo/EtapaInteraccion.java` |
| DisparadorDeEstrategia | `{DOMINIO}/modelo/DisparadorDeEstrategia.java` |
| ContextoEstrategia | `{DOMINIO}/modelo/ContextoEstrategia.java` |
| ResultadoEstrategia | `{DOMINIO}/dto/ResultadoEstrategia.java` |
| PlantillaMensajeId | `{DOMINIO}/modelo/PlantillaMensajeId.java` |
| MotorFsmConfiguration | `{INFRA}/configuracion/MotorFsmConfiguration.java` |
| Estrategias existentes | `{DOMINIO}/maquina_estados/estrategias/` (subcarpetas temáticas) |

## Flujo de trabajo

### Paso 1 — Recolectar información

Pregunta al usuario lo siguiente (usa el formato de opciones de respuesta rápida):

1. **Nombre del flujo/funcionalidad** — Ejemplo: "tarjeta de crédito", "seguros vida"
2. **Subflujo padre** — ¿Dentro de qué carpeta? (`productos/`, `retiros/`, `creditos/`, `referidos/`, o una nueva)
3. **Etapas del flujo** — Lista de etapas con:
   - Nombre descriptivo (se convertirá a SCREAMING_SNAKE_CASE para el enum)
   - Descripción breve de qué hace
   - Transición: ¿a qué etapa siguiente va?
4. **Disparador por etapa** — En la mayoría de casos es `EVENTO_MENSAJE_WHATSAPP`. Preguntar solo si hay etapas que reaccionen a eventos de otros microservicios.
5. **¿Permite desborde a agente humano?** — ¿Las etapas permiten transferir al usuario a un agente si supera reintentos?
6. **¿Captura flujo de navegación?** — ¿Alguna etapa necesita registrar la ruta de navegación del usuario?
7. **Opciones de menú** — Si hay menús con opciones fijas, listar las opciones (se creará un enum `OpcionMenu{Nombre}`).
8. **Dependencias adicionales** — ¿Necesita servicios más allá de `DependenciasEstrategiaBase`? (ej: `ServicioGestionFlujos`, `@Value` de properties, puertos específicos)
9. **Plantillas de mensaje** — Nombres de las plantillas de WhatsApp que se enviarán (se verificará que existan en `PlantillaMensajeId` o se agregarán).

### Paso 2 — Agregar etapas al enum `EtapaInteraccion`

Abrir `{DOMINIO}/modelo/EtapaInteraccion.java` y agregar las nuevas etapas **antes de `FINAL_INTERACCION`**, agrupadas con un comentario de sección.

**Convenciones:**
- Usar SCREAMING_SNAKE_CASE
- Constructor `(boolean capturaFlujoNavegacion)` si NO permite desborde
- Constructor `(boolean capturaFlujoNavegacion, boolean permiteDesborde)` si SÍ permite desborde
- Agregar Javadoc para etapas complejas

```java
// ═══ Etapas Flujo {NOMBRE_FLUJO} ═══
/** Descripción de la etapa */
{NOMBRE_ETAPA_1}(false, true),   // capturaFlujo=false, permiteDesborde=true
{NOMBRE_ETAPA_2}(true),          // capturaFlujo=true, SIN desborde
```

### Paso 3 — Agregar disparadores (si se necesitan nuevos)

Solo si el flujo necesita un disparador que NO exista en `DisparadorDeEstrategia`. Los disparadores existentes más comunes:

| Disparador | Uso |
|------------|-----|
| `EVENTO_MENSAJE_WHATSAPP` | Usuario envía mensaje de texto/botón |
| `EVENTO_RESPUESTA_SERVICIOS_MS` | Respuesta de otro microservicio vía RabbitMQ |
| `EVENTO_ERROR_SERVICIO_EXTERNO` | Error de servicio externo |
| `VALIDACION_EXITOSA` | Validación interna exitosa |
| `EVENTO_RESPUESTA_OTP_INFOBIT` | Respuesta del servicio OTP |

### Paso 4 — Crear enum de opciones de menú (si aplica)

Si el flujo tiene un menú con opciones fijas, crear en `{DOMINIO}/modelo/`:

```java
package co.com.bmm.modelo;

import java.util.Arrays;
import java.util.Optional;

public enum OpcionMenu{NombreFlujo} {
    {OPCION_1}("{id_1}"),
    {OPCION_2}("{id_2}"),
    VOLVER("VOLVER");

    private final String id;

    OpcionMenu{NombreFlujo}(String id) {
        this.id = id;
    }

    public String getId() {
        return id;
    }

    public static Optional<OpcionMenu{NombreFlujo}> fromId(String id) {
        return Arrays.stream(values())
                .filter(opcion -> opcion.id.equalsIgnoreCase(id))
                .findFirst();
    }
}
```

### Paso 5 — Crear la(s) clase(s) de estrategia

Crear en `{DOMINIO}/maquina_estados/estrategias/{subflujo}/{nombre_flujo}/`:

```java
package co.com.bmm.maquina_estados.estrategias.{subflujo}.{nombre_flujo};

import co.com.bmm.dto.ResultadoEstrategia;
import co.com.bmm.maquina_estados.estrategias.DependenciasEstrategiaBase;
import co.com.bmm.maquina_estados.estrategias.EstrategiaBase;
import co.com.bmm.modelo.ContextoEstrategia;
import co.com.bmm.modelo.DisparadorDeEstrategia;
import co.com.bmm.modelo.EtapaInteraccion;
import co.com.bmm.modelo.PlantillaMensajeId;

import java.util.List;

public class Estrategia{NombreEstrategia} extends EstrategiaBase {

    // Si necesita dependencias adicionales, declararlas como campos finales
    // private final ServicioGestionFlujos servicioGestionFlujos;

    public Estrategia{NombreEstrategia}(DependenciasEstrategiaBase dependencias) {
        super(dependencias);
    }

    @Override
    protected ResultadoEstrategia logicaEspecificaDeEtapa(ContextoEstrategia contextoEstrategia) {
        // Lógica de negocio de esta etapa
        // Retornar ResultadoEstrategia con:
        //   - siguienteEtapa: EtapaInteraccion.XXX
        //   - mensajeParaServicio: null (o MensajeParaServicio si publica a RabbitMQ)
        //   - nombrePlantillas: List.of(PlantillaMensajeId.XXX)
        //   - args: dependencias.LISTA_ARGS_VACIA (o List.of("arg1", "arg2"))
        return new ResultadoEstrategia(
                EtapaInteraccion.{SIGUIENTE_ETAPA},
                null,
                List.of(PlantillaMensajeId.{PLANTILLA}),
                dependencias.LISTA_ARGS_VACIA
        );
    }

    @Override
    protected boolean respuestaValidada(String respuesta) {
        // Validar si el mensaje del usuario es procesable
        // Ejemplos:
        //   - OpcionMenu{Nombre}.fromId(respuesta).isPresent()  → menú con opciones
        //   - respuesta != null && !respuesta.isBlank()          → texto libre
        //   - true                                                → siempre válido (ej: respuesta de servicio)
        return true;
    }

    @Override
    protected ResultadoEstrategia manejarRespuestaInvalida(ContextoEstrategia contexto) {
        // Qué hacer cuando respuestaValidada() retorna false
        // Patrón común: repetir el menú con mensaje de error
        return new ResultadoEstrategia(
                getEtapa(),  // Quedarse en la misma etapa
                null,
                List.of(PlantillaMensajeId.ERROR_RESPUESTA_INVALIDA, PlantillaMensajeId.{PLANTILLA_MENU}),
                dependencias.LISTA_ARGS_VACIA
        );
    }

    @Override
    public EtapaInteraccion getEtapa() {
        return EtapaInteraccion.{ETAPA};
    }

    @Override
    public DisparadorDeEstrategia getDisparador() {
        return DisparadorDeEstrategia.{DISPARADOR};
    }
}
```

**Hooks opcionales que se pueden sobreescribir:**

| Método | Cuándo usarlo |
|--------|---------------|
| `respuestaValidadaConContexto(ContextoEstrategia)` | Si la validación necesita más que solo el texto del mensaje |
| `capturarFlujoNavegacion(ContextoEstrategia, ResultadoEstrategia)` | Si `getEtapa().capturaFlujoNavegacion() == true` |
| `getPlantillaPreguntaEtapa()` | Para definir la plantilla que se muestra al volver de desborde a agente |
| `getFlowInfoDesborde()` | Si la etapa usa WhatsApp Flows y necesita restaurar al volver de agente |
| `getCampoActual()` | Para identificar qué campo se captura (conteo de errores) |

### Paso 6 — Registrar beans en `MotorFsmConfiguration`

Abrir `{INFRA}/configuracion/MotorFsmConfiguration.java` y agregar un `@Bean` por cada estrategia nueva:

```java
// ═══════════════════════════════════════════════════════════════
// {NOMBRE_FLUJO}
// ═══════════════════════════════════════════════════════════════

@Bean
public Estrategia{NombreEstrategia} estrategia{NombreEstrategia}(
        DependenciasEstrategiaBase dependencias) {
    return new Estrategia{NombreEstrategia}(dependencias);
}
```

**Si la estrategia tiene dependencias adicionales:**

```java
@Bean
public Estrategia{NombreEstrategia} estrategia{NombreEstrategia}(
        DependenciasEstrategiaBase dependencias,
        ServicioGestionFlujos servicioGestionFlujos) {
    return new Estrategia{NombreEstrategia}(dependencias, servicioGestionFlujos);
}
```

**Si usa @Value de properties:**

```java
@Bean
public Estrategia{NombreEstrategia} estrategia{NombreEstrategia}(
        DependenciasEstrategiaBase dependencias,
        @Value("${whatsapp.flow.{nombre}.id}") String flowId) {
    return new Estrategia{NombreEstrategia}(dependencias, flowId);
}
```

> **IMPORTANTE:** No usar `@Component` ni `@Service` en las clases de estrategia. El registro es explícito vía `@Bean` en `MotorFsmConfiguration` para mantener Clean Architecture (dominio libre de anotaciones Spring).

### Paso 7 — Crear tests unitarios

Crear en `{TESTS}/maquina_estados/estrategias/{subflujo}/{nombre_flujo}/`:

```java
package co.com.bmm.maquina_estados.estrategias.{subflujo}.{nombre_flujo};

import co.com.bmm.FabricaInteraccion;
import co.com.bmm.dto.ResultadoEstrategia;
import co.com.bmm.maquina_estados.estrategias.DependenciasEstrategiaBase;
import co.com.bmm.modelo.ContextoEstrategia;
import co.com.bmm.modelo.EtapaInteraccion;
import co.com.bmm.modelo.PlantillaMensajeId;
import co.com.bmm.modelo.dto.InteraccionDTO;
import co.com.bmm.puerto.PuertoGuardarInteraccion;
import co.com.bmm.puerto.PuertoServicioDeMensajeria;
import co.com.bmm.puerto.ServicioAuditoria;
import co.com.bmm.puerto.ServicioEventos;
import co.com.bmm.puerto.ServicioRespuestaBot;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class Estrategia{NombreEstrategia}Test {

    @Mock private FabricaInteraccion fabricaInteraccion;
    @Mock private PuertoGuardarInteraccion puertoGuardarInteraccion;
    @Mock private PuertoServicioDeMensajeria servicioDeMensajeria;
    @Mock private ServicioRespuestaBot servicioRespuestaBot;
    @Mock private ServicioAuditoria servicioAuditoria;
    @Mock private ServicioEventos servicioEventos;

    private DependenciasEstrategiaBase dependencias;
    private Estrategia{NombreEstrategia} estrategia;

    @BeforeEach
    void setUp() {
        dependencias = new DependenciasEstrategiaBase(
                fabricaInteraccion, puertoGuardarInteraccion, servicioDeMensajeria,
                servicioRespuestaBot, servicioAuditoria, servicioEventos);
        estrategia = new Estrategia{NombreEstrategia}(dependencias);
    }

    @Test
    void debeRetornarEtapaCorrecta() {
        assertEquals(EtapaInteraccion.{ETAPA}, estrategia.getEtapa());
    }

    @Test
    void debeRetornarDisparadorCorrecto() {
        assertEquals(DisparadorDeEstrategia.{DISPARADOR}, estrategia.getDisparador());
    }

    @Test
    void debeEjecutarLogicaEspecifica_conRespuestaValida() {
        InteraccionDTO interaccion = new InteraccionDTO(
                0, "id-test", "Usuario Test", "123456789", "CC", "573001234567",
                EtapaInteraccion.{ETAPA}, true, false, null);
        ContextoEstrategia contexto = new ContextoEstrategia(interaccion, "{MENSAJE_VALIDO}");

        ResultadoEstrategia resultado = estrategia.logicaEspecificaDeEtapa(contexto);

        assertNotNull(resultado);
        assertEquals(EtapaInteraccion.{SIGUIENTE_ETAPA}, resultado.siguienteEtapa());
        // Verificar plantillas, args, etc.
    }

    @Test
    void debeValidarRespuesta_valida() {
        assertTrue(estrategia.respuestaValidada("{RESPUESTA_VALIDA}"));
    }

    @Test
    void debeValidarRespuesta_invalida() {
        assertFalse(estrategia.respuestaValidada("{RESPUESTA_INVALIDA}"));
    }

    @Test
    void debeManejarRespuestaInvalida() {
        InteraccionDTO interaccion = new InteraccionDTO(
                0, "id-test", "Usuario Test", "123456789", "CC", "573001234567",
                EtapaInteraccion.{ETAPA}, true, false, null);
        ContextoEstrategia contexto = new ContextoEstrategia(interaccion, "respuesta_invalida");

        ResultadoEstrategia resultado = estrategia.manejarRespuestaInvalida(contexto);

        assertNotNull(resultado);
        assertEquals(EtapaInteraccion.{ETAPA}, resultado.siguienteEtapa());
        assertTrue(resultado.nombrePlantillas().contains(PlantillaMensajeId.ERROR_RESPUESTA_INVALIDA));
    }
}
```

### Paso 8 — Agregar PlantillaMensajeId (si se necesitan nuevas)

Si las plantillas de WhatsApp no existen en `PlantillaMensajeId`, agregarlas al enum con un nombre en SCREAMING_SNAKE_CASE descriptivo.

### Paso 9 — Validaciones finales

Antes de dar por terminado, verificar:

- [ ] No hay etapas duplicadas en `EtapaInteraccion`
- [ ] No hay pares `(Etapa, Disparador)` duplicados (el `MotorDeInteraccion` lanza excepción si detecta duplicados)
- [ ] Las transiciones forman un flujo coherente (sin etapas huérfanas ni ciclos infinitos no intencionales)
- [ ] Cada estrategia tiene su `@Bean` en `MotorFsmConfiguration`
- [ ] Cada estrategia tiene su test unitario
- [ ] Los imports son correctos y usan los packages del dominio
- [ ] Las clases de estrategia NO tienen anotaciones Spring (`@Component`, `@Service`, etc.)
- [ ] Compilar el proyecto para verificar que no hay errores

**Comando de compilación:**
```bash
cd ms-banca-conversacion && ./gradlew compileJava compileTestJava
```

## Patrones de ResultadoEstrategia

Los factory methods disponibles en `ResultadoEstrategia`:

| Patrón | Uso |
|--------|-----|
| `new ResultadoEstrategia(etapa, null, plantillas, args)` | Transición simple con mensajes |
| `ResultadoEstrategia.sinEvento(etapa, plantillas, args)` | Equivalente al anterior (sin evento RabbitMQ) |
| `ResultadoEstrategia.conEstadoFinal(etapa, null, plantillas, args, estadoFinal)` | Finalizar interacción |
| `ResultadoEstrategia.conFlow(etapa, null, plantillas, args, flowInfo)` | Enviar WhatsApp Flow |
| `ResultadoEstrategia.conMensajesPreviosYFlow(...)` | Mensajes previos + WhatsApp Flow |

## Ejemplo rápido: Estrategia con switch de opciones de menú

```java
@Override
protected ResultadoEstrategia logicaEspecificaDeEtapa(ContextoEstrategia ctx) {
    String id = ctx.mensaje();
    return switch (OpcionMenuMiFlujo.fromId(id).get()) {
        case OPCION_A -> new ResultadoEstrategia(
                EtapaInteraccion.MI_FLUJO_DETALLE_A, null,
                List.of(PlantillaMensajeId.MI_FLUJO_INFO_A),
                dependencias.LISTA_ARGS_VACIA);
        case OPCION_B -> new ResultadoEstrategia(
                EtapaInteraccion.MI_FLUJO_DETALLE_B, null,
                List.of(PlantillaMensajeId.MI_FLUJO_INFO_B),
                dependencias.LISTA_ARGS_VACIA);
        case VOLVER -> new ResultadoEstrategia(
                EtapaInteraccion.VALIDAR_OPCION_SELECCIONADA_MENU_INICIAL, null,
                List.of(PlantillaMensajeId.MENU_INICIAL),
                dependencias.LISTA_ARGS_VACIA);
    };
}

@Override
protected boolean respuestaValidada(String respuesta) {
    return OpcionMenuMiFlujo.fromId(respuesta).isPresent();
}
```

## Ejemplo rápido: Estrategia que espera respuesta de servicio externo

```java
@Override
public DisparadorDeEstrategia getDisparador() {
    return DisparadorDeEstrategia.EVENTO_RESPUESTA_SERVICIOS_MS;
}

@Override
protected boolean respuestaValidada(String respuesta) {
    return true; // Las respuestas de servicios siempre son válidas
}

@Override
protected ResultadoEstrategia logicaEspecificaDeEtapa(ContextoEstrategia ctx) {
    // Parsear la respuesta del servicio externo
    // Determinar siguiente etapa según resultado
    return new ResultadoEstrategia(
            EtapaInteraccion.{SIGUIENTE_ETAPA}, null,
            List.of(PlantillaMensajeId.{PLANTILLA_RESULTADO}),
            dependencias.LISTA_ARGS_VACIA);
}
```

## Ejemplo rápido: Estrategia con WhatsApp Flow

```java
public class EstrategiaMiFlujoInicioFormulario extends EstrategiaBase {
    private final String flowId;

    public EstrategiaMiFlujoInicioFormulario(DependenciasEstrategiaBase dependencias, String flowId) {
        super(dependencias);
        this.flowId = flowId;
    }

    @Override
    protected ResultadoEstrategia logicaEspecificaDeEtapa(ContextoEstrategia ctx) {
        return ResultadoEstrategia.conMensajesPreviosYFlow(
                EtapaInteraccion.MI_FLUJO_ESPERANDO_FLOW, null,
                List.of(PlantillaMensajeId.MI_FLUJO_INSTRUCCIONES),
                dependencias.LISTA_ARGS_VACIA,
                new FlowInfo(flowId, PlantillaMensajeId.MI_FLUJO_FLOW_BODY, PlantillaMensajeId.MI_FLUJO_FLOW_CTA)
        );
    }

    @Override
    protected boolean respuestaValidada(String respuesta) {
        return true;
    }

    @Override
    protected ResultadoEstrategia manejarRespuestaInvalida(ContextoEstrategia contexto) {
        return null; // No aplica
    }
}
```
