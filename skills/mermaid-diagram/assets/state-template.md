```mermaid
%%{init: {'themeVariables': {'transitionColor':'#888888','transitionLabelColor':'#888888'}}}%%
stateDiagram-v2
    [*] --> EstadoInicial
    EstadoInicial --> EnProceso: evento_inicio
    EnProceso --> Completado: evento_fin
    EnProceso --> Error: evento_fallo
    Error --> EstadoInicial: reintento
    Completado --> [*]
```
