# Guía de Configuración MCP para OpenCode y Claude Code

> **Referencias oficiales:**
> - OpenCode: https://opencode.ai/docs/es/mcp-servers/
> - Claude Code: https://code.claude.com/docs/es/mcp-quickstart
> - Claude Code Reference: https://code.claude.com/docs/es/mcp

---

## Diferencias entre Plataformas

| Aspecto | OpenCode | Claude Code |
|---------|----------|-------------|
| **Archivo config** | `opencode.json` | `.mcp.json` |
| **Sección** | `mcp` | `mcpServers` |
| **Tipo local** | `"type": "local"` | `"type": "stdio"` |
| **Comando** | `["npx", "-y", "..."]` (array) | `"npx"` + `args: [...]` (separado) |
| **Variables env** | `environment` | `env` |
| **Habilitar/deshabilitar** | `"enabled": true/false` | No existe (se elimina el servidor) |

---

## Configuración para OpenCode

**Archivo:** `opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "ado": {
      "type": "local",
      "command": ["npx", "-y", "@azure-devops/mcp@latest", "GestionRequerimientos"],
      "enabled": true,
      "description": "Azure DevOps MCP - 90 tools"
    },
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp@latest"],
      "enabled": true,
      "description": "Context7 - Documentación actualizada"
    },
    "sonarqube": {
      "type": "local",
      "command": ["docker", "run", "-i", "--rm", "-e", "SONARQUBE_TOKEN", "-e", "SONARQUBE_URL", "docker.io/mcp/sonarqube:latest"],
      "environment": {
        "SONARQUBE_TOKEN": "sqa_xxx",
        "SONARQUBE_URL": "http://host.docker.internal:9000"
      },
      "enabled": true,
      "description": "SonarQube - Análisis estático"
    }
  }
}
```

### Gestión en OpenCode

```bash
# Ver servidores MCP
opencode mcp list

# Autenticar servidor remoto (OAuth)
opencode mcp auth <nombre-servidor>

# Eliminar credenciales
opencode mcp logout <nombre-servidor>

# Debug de conexión
opencode mcp debug <nombre-servidor>
```

### Habilitar/Deshabilitar por Agente en OpenCode

```json
{
  "mcp": {
    "ado": {
      "type": "local",
      "command": ["npx", "-y", "@azure-devops/mcp@latest", "GestionRequerimientos"],
      "enabled": true
    }
  },
  "tools": {
    "ado*": false
  },
  "agent": {
    "mi-agente-ado": {
      "tools": {
        "ado*": true
      }
    }
  }
}
```

---

## Configuración para Claude Code

**Archivo:** `.mcp.json` (raíz del proyecto)

```json
{
  "mcpServers": {
    "ado": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp@latest", "GestionRequerimientos"]
    },
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "sonarqube": {
      "type": "stdio",
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "SONARQUBE_TOKEN", "-e", "SONARQUBE_URL", "docker.io/mcp/sonarqube:latest"],
      "env": {
        "SONARQUBE_TOKEN": "sqa_xxx",
        "SONARQUBE_URL": "http://host.docker.internal:9000"
      }
    }
  }
}
```

### Gestión en Claude Code

```bash
# Agregar servidor HTTP remoto
claude mcp add --transport http <nombre> <url>

# Agregar servidor stdio local
claude mcp add <nombre> -- <comando> [args...]

# Agregar servidor desde JSON
claude mcp add-json <nombre> '<json>'

# Listar servidores
claude mcp list

# Ver detalles de un servidor
claude mcp get <nombre>

# Eliminar servidor
claude mcp remove <nombre>

# Verificar dentro de sesión
/mcp

# Importar desde Claude Desktop
claude mcp add-from-claude-desktop

# Autenticar servidor OAuth
claude mcp login <nombre>

# Eliminar credenciales
claude mcp logout <nombre>
```

### Ámbitos en Claude Code

| Ámbito | Archivo | Compartido | Uso |
|--------|---------|------------|-----|
| `local` (default) | `~/.claude.json` | No | Servidores personales, privados |
| `project` | `.mcp.json` | Sí (git) | Servidores del equipo |
| `user` | `~/.claude.json` | No | Servidores en todos los proyectos |

```bash
# Agregar con ámbito específico
claude mcp add --scope project --transport http <nombre> <url>
claude mcp add --scope user --transport http <nombre> <url>
```

### Variables de Entorno en `.mcp.json`

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

---

## Servidores MCP Configurados

### ADO (Azure DevOps)

- **Paquete:** `@azure-devops/mcp@latest`
- **Organización:** `GestionRequerimientos`
- **Herramientas:** 90 tools en 9 categorías
- **Uso:** Skills ADO (orchestrator, ado-hu-publisher, ado-task-creator, ado-pr-creator, ado-pr-reviewer, ado-pipeline-analyzer, ado-profile-setup)

### Context7

- **Paquete:** `@upstash/context7-mcp@latest`
- **Uso:** Documentación actualizada de librerías y frameworks
- **Ejemplo:** `use context7 to search React docs`

### SonarQube

- **Imagen Docker:** `docker.io/mcp/sonarqube:latest`
- **Variables:** `SONARQUBE_TOKEN`, `SONARQUBE_URL`
- **Uso:** Análisis estático de código, quality gates, métricas

---

## Referencia: Patrones de Herramientas MCP

| Patrón | Significado |
|--------|-------------|
| `mcp__<server>` | Todas las herramientas de un servidor |
| `mcp__<server>__*` | Todas las herramientas de un servidor |
| `mcp__*` | Todas las herramientas MCP de cualquier servidor |
| `mcp__<server>__<tool>` | Herramienta específica |

---

## Troubleshooting

### OpenCode

```bash
# Verificar conexión
opencode mcp list

# Debug de servidor específico
opencode mcp debug <nombre>

# Verificar autenticación OAuth
opencode mcp auth list
```

### Claude Code

```bash
# Verificar conexión
claude mcp list

# Ver detalles de error
claude mcp get <nombre>

# Dentro de sesión
/mcp

# Restablecer aprobaciones de proyecto
claude mcp reset-project-choices
```

### Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `Failed to connect` | Servidor no responde | Verificar comando/URL, ejecutar manualmente |
| `Needs authentication` | OAuth requerido | Ejecutar `opencode mcp auth` o `/mcp` en Claude |
| `Connection timed out` | Timeout alcanzado | Aumentar `MCP_TIMEOUT` o `timeout` en config |
| `Server already exists` | Nombre duplicado | Eliminar primero o usar otro nombre |
| `No tools appear` | Falta variable env | Verificar `environment`/`env` en config |

---

## Fuentes

- [OpenCode MCP Servers](https://opencode.ai/docs/es/mcp-servers/)
- [Claude Code MCP Quickstart](https://code.claude.com/docs/es/mcp-quickstart)
- [Claude Code MCP Reference](https://code.claude.com/docs/es/mcp)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
