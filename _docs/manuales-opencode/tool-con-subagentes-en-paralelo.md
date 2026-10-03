Sí, puedes llamar a subagentes desde una herramienta personalizada (custom tool) escrita en JavaScript o TypeScript.

Para lograrlo desde tu código JS, tienes dos caminos principales según la arquitectura de OpenCode:

## 1. Utilizando el SDK oficial de OpenCode (`@opencode-ai/sdk`)

La forma más limpia y recomendada es inicializar el cliente de OpenCode dentro de tu `execute()` e interactuar con su API local. El contexto de la herramienta te provee el `sessionID` actual si deseas continuar un hilo o crear uno nuevo.

```javascript
// .opencode/tools/llamarSubagente.js
import { tool } from "@opencode-ai/plugin";
import { OpenCode } from "@opencode/client"; // Cliente oficial del SDK

export default tool({
  description: "Llama a un subagente específico para resolver una tarea de código.",
  args: {
    instrucciones: tool.schema.string().describe("Qué debe hacer el subagente"),
  },
  async execute(args, context) {
    // 1. Conectar con el servidor local de OpenCode que corre en segundo plano
    const client = OpenCode.make({
      baseUrl: "http://localhost:4096", 
    });

    // 2. Mandar un prompt invocando explícitamente al subagente usando la sintaxis de mención '@'
    // Ejemplo usando el subagente integrado 'explore'
    const respuesta = await client.session.prompt({
      sessionID: context.sessionID, // Mantiene la persistencia en el hilo actual
      text: `@explore analiza esto: ${args.instrucciones}`, 
    });

    return `Subagente invocado exitosamente. Respuesta: ${respuesta.text}`;
  },
});
```
*Use code with caution.*

## 2. Invocando la herramienta nativa `subagent` mediante comandos del sistema

Las herramientas personalizadas en OpenCode corren sobre el entorno de ejecución Bun. Puedes usar las utilidades nativas de la terminal (`Bun.$`) para invocar la CLI de OpenCode directamente o disparar flujos que fuercen al agente padre a usar su propia herramienta interna de delegación (`subagent`).

### Requisitos previos indispensables

- Permisos del Agente: Asegúrate de que el agente primario que use tu herramienta personalizada tenga habilitados los permisos para invocar subagentes en su archivo `opencode.json`:

```json
{
  "action": "subagent",
  "resource": "*",
  "effect": "allow"
}
```
*Use code with caution.*

¿Qué comportamiento o lógica exacta deseas que ejecute tu subagente al ser llamado por tu herramienta? Te puedo ayudar a afinar los argumentos (args) o la gestión de la respuesta.

- **OpenCode** — *Custom Tools | OpenCode*
  JavaScript files utilizing the tool() Custom tools take precedence over built-in names. definition using utilities like Bun.$.
- **OpenCode** — *Agents - OpenCode*
  Runs either as a primary agent or a subagent. The parent agent's subagent permissions control which agents it may launch; the chil...
- **SpinSpire** — *Enhance OpenCode with Custom Tools and Skills - SpinSpire*
  useful when you need to resolve paths relative to the project root. Tools in Any Language The tool definition must be TypeScript o...

Show all

---

te propongo el siguiente caso, inicie opencode en una temrinal normalmente en la carpeta PROYECTO-X. En este proyecto tengo instalada una tool perzonalizada en .opencode/tools/toolPrueba.js. ahora toolPrueba.js es invocada por la sesion en la que estoy interactuando, correcto. ahora mi pregunta es toolPrueba.js puede ejecutar un sub-agente en paralelo y luego entregar ese resultado a la sesion en la que estoy interactuando para iterar sobre ese resultado ?

Sí, es totalmente posible y es uno de los casos de uso más avanzados y potentes en OpenCode.

Cuando ejecutas opencode en la carpeta PROYECTO-X e invocas tu herramienta toolPrueba.js, esta se ejecuta dentro del entorno nativo basado en Bun. Desde ahí puedes disparar subagentes en paralelo, esperar a que terminen, capturar su respuesta y devolver el resultado estructurado al agente principal de tu sesión actual para continuar iterando.

Para lograr que tu herramienta personalizada haga esto de forma paralela y controlada, debes implementar el siguiente patrón en tu código:

### 1. El código de tu herramienta (`.opencode/tools/toolPrueba.js`)

Para evitar bloquear el hilo principal de manera síncrona o ensuciar el contexto, puedes utilizar la API interna de OpenCode. Lo ideal es configurar la llamada al subagente indicando explícitamente `background: true` y luego resolver las promesas en paralelo utilizando `Promise.all`.

```javascript
import { tool } from "@opencode-ai/plugin";
import { OpenCode } from "@opencode/client"; // Cliente para interactuar con las sesiones

export default tool({
  description: "Ejecuta subagentes en paralelo para procesar tareas complejas.",
  args: {
    tareas: tool.schema.array(tool.schema.string()).describe("Lista de prompts individuales para los subagentes"),
  },
  async execute(args, context) {
    const client = OpenCode.make({ baseUrl: "http://localhost:4096" });

    // 1. Lanzamos los subagentes en paralelo usando Promise.all
    const promesasSubagentes = args.tareas.map(async (promptTarea, index) => {
      // Invocamos un subagente integrado (ej. 'general' o 'explore') en una sesión hija
      const respuesta = await client.subagent.run({
        agentId: "general", 
        prompt: promptTarea,
        parentSessionId: context.sessionID, // Vincula el ciclo a tu sesión interactiva actual
        background: true // Mantiene la ejecución fluida en segundo plano
      });
      
      return `Resultado Tarea ${index + 1}: ${respuesta.text}`;
    });

    // 2. Esperamos a que todas las ejecuciones paralelas terminen
    const resultadosparalelos = await Promise.all(promesasSubagentes);

    // 3. Unimos los resultados en una cadena limpia
    const resultadoConsolidado = resultadosparalelos.join("\n\n");

    // 4. Se lo entregamos a la sesión interactiva actual
    return `Análisis paralelo completado exitosamente. Aquí tienes los datos recolectados:\n\n${resultadoConsolidado}\n\nPor favor, analiza estos resultados y dime cuál es el siguiente paso a iterar.`;
  },
});
```
*Use code with caution.*

### 2. ¿Cómo interactúa el agente principal contigo tras la ejecución?

Cuando toolPrueba.js termina su función `execute()`, el String que retorna el método se inyecta directamente como un mensaje del sistema/herramienta en tu chat interactivo actual.

1. El Agente Principal (con el que estás chateando en la terminal) leerá ese resultadoConsolidado.
2. Como el retorno de la herramienta explícitamente le pide al final "analiza estos resultados y dime cuál es el siguiente paso", el modelo tomará el control automáticamente en tu pantalla, procesará la información combinada de los subagentes y te presentará una propuesta de diseño, código o solución para que tú sigues iterando con él en caliente.

### Asegura los permisos en tu `opencode.json`

Para que tu herramienta no sea bloqueada por el sistema de seguridad al intentar desplegar subagentes, la sesión padre en PROYECTO-X debe tener estos permisos habilitados en su archivo de configuración local:

```json
{
  "permissions": [
    {
      "action": "subagent",
      "resource": "*",
      "effect": "allow"
    },
    {
      "action": "execute",
      "resource": "*",
      "effect": "allow"
    }
  ]
}
```
*Use code with caution.*

Si quieres, cuéntame:

- ¿Qué tarea específica (pruebas unitarias, auditoría de seguridad, refactorización) van a hacer los subagentes en paralelo?
- ¿Qué subagente especializado (general, explore o uno personalizado creado por ti) tienes en mente utilizar?

De esta forma puedo ayudarte a escribir los prompts internos exactos de la herramienta para optimizar el consumo de tokens y la precisión de la respuesta.

- **OpenCode** — *Agents - OpenCode*
  Subagents are specialized assistants that primary agents can invoke for specific tasks. OpenCode comes with three built-in subagen...
- **OpenCode** — *Custom Tools | OpenCode*
  TypeScript or JavaScript files utilizing the tool() Python or other external scripts can be invoked within the TypeScript/JavaScri...
- **Moncef Abboud** — *How Coding Agents Actually Work: Inside OpenCode*
  The key parts of a tool definition are its description (prompt), parameters (args), and the execute function that performs the act...

Show all

---

osea la tool toolPrueba.js nunca le entrega al agente principal un prompt tipo "ejecuta un subagente con bla bla bla y el output sea esto", solo le entrega la respuesta del subagente que ejecuto paralelamente mediante la api ?

Exactamente, has capturado la esencia del patrón a la perfección. La herramienta toolPrueba.js nunca le pide al agente principal que ejecute los subagentes; ella misma toma el control del proceso técnico, los ejecuta directamente a través de la API y le entrega al agente principal solo el resultado final.

Para el agente principal con el que estás chateando en la terminal, lo que ocurre tras bambalinas es completamente transparente (invisible). El flujo mental del agente principal funciona así:

1. El Agente Principal detecta la necesidad: "Para resolver la solicitud del usuario, necesito usar la herramienta toolPrueba".
2. Invoca la herramienta: Llama a toolPrueba.js pasándole los argumentos requeridos. En este punto, el modelo "se sienta a esperar".
3. La herramienta hace el trabajo pesado: Tu código JS se ejecuta en el entorno Bun de tu máquina, habla con la API local de OpenCode, levanta los subagentes en paralelo, recopila sus respuestas y las une.
4. La herramienta responde: Devuelve un String con los datos ya procesados.
5. El Agente Principal recibe el output: Para el modelo, es exactamente igual a cuando una herramienta lee un archivo del disco o hace una petición web (HTTP). No sabe ni le importa que ese texto provenga de otros agentes; simplemente lee los datos combinados y continúa la conversación contigo para iterar sobre ellos.

### 🎭 La diferencia entre los dos enfoques

Si tu herramienta hiciera lo que mencionas (entregarle un prompt tipo "ejecuta un subagente..."), estarías obligando al agente principal a realizar múltiples turnos de pensamiento innecesarios y gastarías muchos tokens de manera ineficiente.

| Característica | Enfoque 1: Delegación desde el Código (Tu propuesta con API) | Enfoque 2: Delegación por Prompt (Texto plano) |
|---|---|---|
| Control del Flujo | Estricto y determinista. Tu código JS decide exactamente cuántos agentes se lanzan en paralelo y cómo se unifican. | Impreciso. Depende de que el modelo decida obedecer el texto y ejecutar la herramienta nativa paso a paso. |
| Paralelismo Real | Sí. Mediante Promise.all en JavaScript controlas hilos paralelos reales. | No. El agente principal ejecutaría un subagente, esperaría su respuesta, y luego ejecutaría el siguiente secuencialmente. |
| Eficiencia de Tokens | Alta. El agente principal solo lee el reporte final consolidado. | Baja. El contexto se llena con las instrucciones de control de flujos intermedios. |

Al abstraer la complejidad dentro de toolPrueba.js, logras que el agente de tu terminal se comporte como un verdadero "Director de Orquesta" que delega una tarea compleja a una herramienta, y esta le devuelve un reporte ejecutivo limpio y listo para la acción.

Si te interesa profundizar en la implementación, cuéntame:

- ¿Quieres estructurar el output final que devuelve la herramienta en formato JSON o Markdown para que el agente principal lo procese con mayor facilidad?
- ¿Te gustaría añadir manejo de errores en el código JS por si alguno de los subagentes en paralelo falla o excede el tiempo límite (timeout)?
