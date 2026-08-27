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
