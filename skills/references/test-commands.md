# Comandos de validación de tests

Detectar el tipo de proyecto y ejecutar el comando correspondiente antes de push:

| Tipo de proyecto | Indicador | Comando |
|------------------|-----------|---------|
| Node.js | `package.json` | `npm test` |
| Java/Maven | `pom.xml` | `mvn test` |
| Java/Gradle | `build.gradle` | `gradle test` |
| .NET | `*.csproj` | `dotnet test` |
| Python | `pyproject.toml` | `pytest` |
| Go | `go.mod` | `go test ./...` |

Si los tests fallan → detener y corregir antes de continuar.
