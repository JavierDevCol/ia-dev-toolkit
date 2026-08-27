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
