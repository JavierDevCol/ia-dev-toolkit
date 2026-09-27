```mermaid
%%{init: {'themeVariables': {'signalColor':'#888888'}}}%%
sequenceDiagram
    autonumber
    rect rgba(0, 150, 255, 0.15)
        Note over Cliente,Servicio: Fase 1 — Descripción
        Cliente->>Servicio: Mensaje de solicitud
        Servicio-->>Cliente: Respuesta
    end
    rect rgba(0, 255, 127, 0.15)
        Note over Cliente,Servicio: Fase 2 — Descripción
        Cliente->>Servicio: Siguiente acción
        Servicio-->>Cliente: Resultado
    end
```
