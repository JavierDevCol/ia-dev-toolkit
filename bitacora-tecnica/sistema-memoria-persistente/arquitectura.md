# Arquitectura: Autoaprendizaje v3 (SQLite-backed)

> **Estado:** Diseño final (simplificado)
> **Fecha:** 2026-08-30
> **Autor:** Javier García + OpenCode
> **Versión:** 3.0

---

## 1. Propuesta

Reemplazar la skill `autoaprendizaje` (flat files) con un sistema persistente basado en SQLite. Integración en **2 capas** sin archivos intermedios:

```
AGENTS.md → memory_tool.py → SQLite
```

### Evolución del diseño

| Versión | Complejidad | Problema |
|---------|-------------|----------|
| v1 | 5 capas (skill + MCP + MEMORY_SAC.md + tool + BD) | Over-engineered |
| v2 | 4 capas (skill + MEMORY_SAC.md + tool + BD) | Archivos intermedios innecesarios |
| **v3** | **2 capas (AGENTS.md + tool + BD)** | **Simplificado** |

---

## 2. Arquitectura final

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENTE (Mimo)                             │
│                                                              │
│  ┌──────────────┐                                           │
│  │  AGENTS.md    │  "Usa memory_tool.py para memoria"       │
│  │  (siempre)    │                                           │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────────────────────────────┐                   │
│  │     memory_tool.py                    │                   │
│  │  ┌────────────────────────────────┐  │                   │
│  │  │ --read   (consultar)           │  │                   │
│  │  │ --write  (guardar/actualizar)  │  │                   │
│  │  │ --search (búsqueda libre)      │  │                   │
│  │  │ --apply  (incrementar counter) │  │                   │
│  │  │ --decay  (confidence decay)    │  │                   │
│  │  │ --help   (documentación)       │  │                   │
│  │  └────────────────────────────────┘  │                   │
│  └──────────────────┬───────────────────┘                   │
│                     │                                        │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   SQLite Database                            │
│  ~/.squad-skills/memory.db                                   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    MEMORIA                            │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  AUDIT_LOG                            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Protegido: permisos 600, cifrado opcional                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Schema de base de datos

### 3.1 Tabla MEMORIA

```sql
CREATE TABLE MEMORIA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN (
        'user', 'personality', 'rule', 'feedback', 'project', 'reference'
    )),
    category TEXT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    metadata JSON,
    confidence REAL DEFAULT 1.0,
    times_applied INTEGER DEFAULT 0,
    last_applied_at DATETIME,
    source TEXT DEFAULT 'explicit' CHECK(source IN (
        'explicit', 'inferred', 'feedback'
    )),
    trigger_condition TEXT,
    scope TEXT DEFAULT 'global' CHECK(scope IN (
        'global', 'project', 'folder'
    )),
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    active INTEGER DEFAULT 1
);

CREATE UNIQUE INDEX idx_memoria_type_key ON MEMORIA(type, key);
CREATE INDEX idx_memoria_type ON MEMORIA(type);
CREATE INDEX idx_memoria_category ON MEMORIA(category);
CREATE INDEX idx_memoria_active ON MEMORIA(active);
```

### 3.2 Tabla AUDIT_LOG

```sql
CREATE TABLE AUDIT_LOG (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER,
    operation TEXT NOT NULL CHECK(operation IN ('INSERT', 'UPDATE', 'SOFT_DELETE')),
    old_value TEXT,
    new_value TEXT,
    agent_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_memory_id ON AUDIT_LOG(memory_id);
```

### 3.3 Tabla SCHEMA_VERSION

```sql
CREATE TABLE SCHEMA_VERSION (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. memory_tool.py

### 4.1 Comandos

```bash
# Consultar
python tools/memory_tool.py read --type rule --category git
python tools/memory_tool.py read --type feedback
python tools/memory_tool.py read --type user

# Escribir (upsert)
python tools/memory_tool.py write \
  --type feedback \
  --key "no_entendido_sin_preview" \
  --value "Nunca decir entendido sin mostrar preview" \
  --category comunicacion \
  --source feedback

# Búsqueda libre
python tools/memory_tool.py search --query "python"

# Aplicar learning (incrementar counter)
python tools/memory_tool.py apply --id 42

# Confidence decay
python tools/memory_tool.py decay --days 30

# Ver ayuda (reemplaza MEMORY_SAC.md)
python tools/memory_tool.py help
```

### 4.2 Interfaz Python

```python
class MemoryTool:
    def __init__(self, db_path="~/.squad-skills/memory.db"):
        self.db_path = expanduser(db_path)
    
    def read(self, type=None, category=None, key=None, limit=50) -> list[dict]
    def search(self, query: str, limit=20) -> list[dict]
    def get_by_key(self, type: str, key: str) -> dict | None
    def write(self, type, key, value, category=None, metadata=None,
              confidence=1.0, source='explicit', trigger_condition=None,
              scope='global', expires_at=None) -> int
    def delete(self, memory_id: int) -> bool
    def apply(self, memory_id: int) -> None
    def decay(self, days_threshold=30) -> int
    def expire(self) -> int
    def stats(self) -> dict
    def help(self) -> str
```

---

## 5. Integración con AGENTS.md

```markdown
## 🧠 Memoria Persistente

Usa `python tools/memory_tool.py` para gestionar memoria:
- **Leer**: `memory_tool.py read --type {user|personality|rule|feedback}`
- **Escribir**: `memory_tool.py write --type {type} --key {key} --value {value}`
- **Buscar**: `memory_tool.py search --query {texto}`
- **Ayuda**: `memory_tool.py help`

Al inicio de sesión: ejecutar `memory_tool.py read --type rule` para cargar reglas.
Al detectar insatisfacción: ejecutar `memory_tool.py write ...`
```

---

## 6. Confidence Decay

```python
def decay(self, days_threshold=30):
    # Decrementar confidence por falta de uso
    self.execute("""
        UPDATE MEMORIA 
        SET confidence = MAX(0, confidence - 0.01 * ?)
        WHERE active = 1 
        AND last_applied_at < datetime('now', ? || ' days')
    """, (days_threshold, -days_threshold))
    
    # Desactivar confidence muy baja
    self.execute("""
        UPDATE MEMORIA SET active = 0 
        WHERE confidence < 0.1 AND active = 1
    """)
```

---

## 7. Protección

| Medida | Implementación |
|--------|---------------|
| Permisos | `chmod 600 memory.db` |
| Cifrado | SQLCipher (opcional) |
| Audit | Tabla AUDIT_LOG |
| Soft delete | Campo `active = 0` |
| PII filter | Regex antes de guardar |

### Reglas

```markdown
1. NUNCA guardar: JWTs, contraseñas, API keys, IPs, emails
2. SIEMPRE usar soft delete
3. SIEMPRE registrar en AUDIT_LOG
4. Si hay duda → NO guardar
```

---

## 8. Próximos pasos

1. [ ] Implementar `memory_tool.py` con SQLite
2. [ ] Agregar referencia en `AGENTS.md`
3. [ ] Implementar confidence decay
4. [ ] Implementar PII filter
5. [ ] Testing con subagentes
6. [ ] Agregar cifrado SQLCipher (opcional)
