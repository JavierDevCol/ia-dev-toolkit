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
