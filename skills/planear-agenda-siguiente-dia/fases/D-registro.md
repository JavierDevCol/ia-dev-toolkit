# D. Registro de cierre del día

Soporte para auditoría de tiempos. Se escribe **solo cuando el día quedó claro**: ningún ítem abierto.

## Condición de escritura

Ítems abiertos = cualquiera de estos sin respuesta del usuario:
- veredicto `por aclarar` o `sin evidencia` (se cierra si el usuario responde o declara "no hubo evidencia"),
- desfase de tiempo preguntado (fase B),
- reunión `tentative` o del mismo WI sin confirmar,
- bloque sin WI ni tema claro.

Si hay ítems abiertos: **no escribas el archivo**. Lista lo que falta como preguntas concretas, espera las respuestas, reevalúa y escribe cuando la lista quede vacía. No pidas otra confirmación para escribir: es un archivo local; al terminar informa la ruta.

## Archivo

`{documentacion_sac_path}/registro_tiempos/AAAA-MM-DD.md` (crea la carpeta si no existe; nunca escribas fuera de `{documentacion_sac_path}`). Si el archivo ya existe, no lo sobrescribas: usa `AAAA-MM-DD-2.md`, `-3`, etc.

## Contenido

Cada dato lleva su fuente y hora (zona configurada). No inventes causas ni completes huecos.

```
# Registro de tiempos · AAAA-MM-DD (día de la semana)
Generado: <fecha-hora en la zona configurada> · Cuenta: <correo> · Perfil ADO: <perfil_activo>

## Jornada
<horario aplicable>, almuerzo <hora>.

## Tiempo por WI
| #WI · título | Reservado | Efectivo | En reunión del mismo WI | Remanente | Veredicto |

## Reuniones (calendario principal)
| Hora | Duración | Título | Respuesta |

## Evidencia por WI
Por cada WI: acciones en ADO con hora (comentarios, tasks creadas/cerradas, cambios de estado) y sesión de bitácora usada. Fuente en cada línea.

## Desfases y aclaraciones
| Hecho observado | Pregunta | Respuesta del usuario (textual, "declarado") |

## Horas registradas vs. observadas
`CompletedWork` por WI frente al tiempo transcurrido, solo como dato.

## Totales
Horas en WI · en reuniones · sin asignar · total del día.

## Fuentes
Calendario principal, calendario de bloques, ADO (proyecto), notas Daily/Planning usadas, bitácoras leídas.
```

Notas:
- Lo que quedó sin evidencia y el usuario lo confirmó se escribe "sin evidencia (confirmado por el usuario)".
- Las explicaciones del usuario se copian textuales y se marcan "declarado".
- No escribas en ADO ni dejes comentarios allí.
- Firma: si `usuario.incluir_firma_en_documentos` es `true`, agrega al final `> **Generado por:** {{usuario.nombre}}`; si el nombre está vacío o la clave no existe, omite la línea y no inventes un nombre.
