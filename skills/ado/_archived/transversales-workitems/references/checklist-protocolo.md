# Checklist de Cumplimiento del Protocolo

Usar en **CREAR** (recolectar/validar antes de registrar) y en **VERIFICAR**
(auditar un WI existente punto por punto). Un WI está alineado solo si cumple **todos**.

## Obligatorios — bloquean el registro si faltan

| # | Ítem                       | Criterio de cumplimiento                                                                 | Dónde se valida (Azure DevOps)             |
| - | -------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------ |
| 1 | Enlace al Feature          | Es **hijo del Feature 128821** (proyecto FINTIA).                                         | Relación `Parent` = 128821                 |
| 2 | Título                     | Claro y conciso: identifica **qué falla** y **dónde** (componente).                      | `System.Title`                             |
| 3 | ¿Qué está ocurriendo?      | La descripción responde el estado actual del fallo.                                      | `description`                              |
| 4 | ¿Qué se esperaba?          | La descripción indica el comportamiento esperado.                                        | `description`                              |
| 5 | Pasos para reproducir      | Pasos exactos y numerados.                                                                | `description` / `ReproSteps`               |
| 6 | Sistema / Aplicación       | Uno de: Portal Clientes, App Móvil BMM, Core Transaccional, APIs/Kong Gateway, WhatsApp. | `tags` + descripción                       |
| 7 | Ambiente                   | Uno de los **cinco**: Desarrollo Ceiba, Desarrollo Fintia, QA/Pruebas, Preproducción, Producción. | `tags` + descripción              |
| 8 | Prioridad                  | P1–P4 según la matriz, coherente con el impacto descrito.                                | `priority` (1–4) + `tags`                  |
| 9 | Usuarios afectados         | Volumen estimado + área del banco impactada.                                             | `description`                              |
| 10 | Fecha y hora de detección | Momento exacto de la falla.                                                              | `description`                              |
| 11 | Evidencias técnicas       | Capturas, logs, payloads de API o video (adjuntos o referenciados).                      | adjuntos / `description`                   |
| 12 | Datos del solicitante     | Nombre de contacto + área operativa.                                                     | `description`                              |
| 13 | Responsable               | Persona asignada.                                                                        | `assignedTo` / `System.AssignedTo`         |

### Solo si es registro retroactivo (incidente ya resuelto)

| #  | Ítem                       | Criterio de cumplimiento                                                                 | Dónde se valida (Azure DevOps)             |
| -- | -------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------ |
| 14 | Estado resuelto            | El WI está en `Resolved` o `Closed`, no en New/Active.                                    | `System.State`                             |
| 15 | Sección de Resolución      | Causa raíz + solución aplicada + fecha/hora de resolución + ambiente(s).                  | `description`                              |
| 16 | Tiempo de atención *(opcional)* | Duración total desde la detección hasta la resolución (ej: "3 días", "4 horas"). Pedirlo si el usuario lo conoce; no bloquear si no está disponible. | `description` (bloque Resolución) + `Microsoft.VSTS.Scheduling.CompletedWork` (horas numéricas, si aplica) |

## Matriz de prioridades (para validar el ítem 8)

| Prioridad        | Cuándo aplica                                                  | Criterio operativo BMM                                       |
| ---------------- | ------------------------------------------------------------- | ------------------------------------------------------------ |
| **P1 — Crítico** | Sistema caído o inoperable. Afectación masiva.                | Canales transaccionales detenidos en días de nómina o picos. |
| **P2 — Alto**    | Funcionalidad core afectada. Existe workaround temporal.      | Errores de encolamiento RabbitMQ que demoran transacciones.  |
| **P3 — Medio**   | Afectación limitada. No bloquea la operación del Banco.       | Inconsistencia menor de visualización en Portal Clientes.    |
| **P4 — Bajo**    | Consultas o sugerencias. Mejoras que entran a backlog.        | Alineación de textos, reportes informativos no urgentes.     |

## Reglas especiales

- **Ambiente = Producción** → marcar en el reporte: *"Requiere doble check"*.
- Si falta **cualquier** ítem 1–13 → el WI **NO cumple**; en CREAR, pedir el dato; en VERIFICAR, listar el faltante.
- Si es **registro retroactivo** (incidente ya resuelto) → además exigir los ítems **14 y 15**.
- El ítem **16 (Tiempo de atención)** es **opcional**: pedirlo siempre en registros retroactivos (ACTUALIZAR o CREAR retroactivo), pero no bloquear ni marcar como ❌ si el usuario no lo tiene. Registrarlo en la descripción (bloque Resolución) y, si se expresó en horas, también en `CompletedWork`.

## Formato del reporte de verificación

```
Verificación WI #<id> — <título>
Resultado: <CUMPLE | NO CUMPLE (n faltantes)>

  1. Enlace al Feature 128821 ......... ✅ / ❌  <detalle>
  2. Título claro ..................... ✅ / ❌  <detalle>
  ...
 13. Responsable asignado ............. ✅ / ❌  <detalle>

Acciones sugeridas: <qué corregir, si aplica>
```
