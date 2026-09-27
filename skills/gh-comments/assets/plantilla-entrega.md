### {Emoji} ENTREGA: `{RELEASE | FEATURE | FIX | HOTFIX}` v`{versión}`
- **📦 REPO:** `{owner}/{repo}`
- **📅 FECHA:** `{YYYY-MM-DD}`
- **🌿 RAMA:** `{rama_origen}`

---

#### 📋 DESCRIPCIÓN
{Breve descripción de lo que se entrega}

#### 🔄 CAMBIOS
• `{feat|fix|chore}`: {descripción del cambio}
• `{feat|fix|chore}`: {descripción del cambio}

#### 📦 ENTREGABLES
• **`release-notes.md`** ➔ `{ruta}/entrega_release/{repo}/{version}/`
• **`CONFIG-ENTORNO-PR`** ➔ `{ruta}/entrega_release/{repo}/{version}/`

#### ⚠️ ACCIONES REQUERIDAS
1. Crear PR de `{rama}` ➔ `develop`
2. Mergear PR a `develop`
3. Taggear `v{versión}`
4. Desplegar en **DES**
5. Configurar variables/secrets según **`CONFIG-ENTORNO-PR`**

> ⚠️ **NOTAS ADICIONALES**
> {Notas adicionales si aplica. Si no hay notas, eliminar este bloque}
