# Add ready flag to workflow frontmatter

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `ready: true` to the frontmatter of all workflow files.

**Architecture:** Direct, surgical edits to the frontmatter sections of each `workflow.md` file, appending `ready: true` after the existing description field.

**Tech Stack:** Markdown files.

**Spec:** User request.

## Global Constraints

- Do not change any other content in the files.
- Only modify the `workflow.md` files listed in the task.

---

### Task 1: Modify `workflows/definir-vision-producto/workflow.md`

**Files:**
- Modify: `workflows/definir-vision-producto/workflow.md:1-4`

**Interfaces:**
- Consumes: N/A
- Produces: N/A

- [ ] **Step 1: Read the file**
  Read the file to confirm its current content and frontmatter structure.

- [ ] **Step 2: Apply the edit**
  Edit the file to add `ready: true` after the `description:` line in the frontmatter.

  **Current content (lines 1-4):**
  ```yaml
  ---
  name: definir-vision-producto
  description: Descubre y estructura la visión estratégica de una idea de negocio, delimitando el MVP, los actores y los requerimientos de alto nivel.
  ---
  ```

  **Target content (lines 1-5):**
  ```yaml
  ---
  name: definir-vision-producto
  description: Descubre y estructura la visión estratégica de una idea de negocio, delimitando el MVP, los actores y los requerimientos de alto nivel.
  ready: true
  ---
  ```

- [ ] **Step 3: Commit**
  ```bash
  git add workflows/definir-vision-producto/workflow.md
  git commit -m "feat: add ready flag to definir-vision-producto workflow"
  ```

---

### Task 2: Modify `workflows/definir-arquitectura-solucion/workflow.md`

**Files:**
- Modify: `workflows/definir-arquitectura-solucion/workflow.md:1-4`

**Interfaces:**
- Consumes: N/A
- Produces: N/A

- [ ] **Step 1: Read the file**
  Read the file to confirm its current content and frontmatter structure.

- [ ] **Step 2: Apply the edit**
  Edit the file to add `ready: true` after the `description:` line in the frontmatter.

  **Current content (lines 1-4):**
  ```yaml
  ---
  name: definir-arquitectura-solucion
  description: Diseña colaborativamente la arquitectura integral del proyecto (Cloud, software, datos, seguridad, DevOps) proponiendo opciones técnicas en cada fase para validación antes de formalizar los ADRs.
  ---
  ```

  **Target content (lines 1-5):**
  ```yaml
  ---
  name: definir-arquitectura-solucion
  description: Diseña colaborativamente la arquitectura integral del proyecto (Cloud, software, datos, seguridad, DevOps) proponiendo opciones técnicas en cada fase para validación antes de formalizar los ADRs.
  ready: true
  ---
  ```

- [ ] **Step 3: Commit**
  ```bash
  git add workflows/definir-arquitectura-solucion/workflow.md
  git commit -m "feat: add ready flag to definir-arquitectura-solucion workflow"
  ```

---

### Task 3: Modify `workflows/gestionar-backlog-roadmap/workflow.md`

**Files:**
- Modify: `workflows/gestionar-backlog-roadmap/workflow.md:1-4`

**Interfaces:**
- Consumes: N/A
- Produces: N/A

- [ ] **Step 1: Read the file**
  Read the file to confirm its current content and frontmatter structure.

- [ ] **Step 2: Apply the edit**
  Edit the file to add `ready: true` after the `description:` line in the frontmatter.

  **Current content (lines 1-4):**
  ```yaml
  ---
  name: gestionar-backlog-roadmap
  description: [Needs to be read from file]
  ---
  ```

  **Target content (lines 1-5):**
  ```yaml
  ---
  name: gestionar-backlog-roadmap
  description: [Needs to be read from file]
  ready: true
  ---
  ```

- [ ] **Step 3: Commit**
  ```bash
  git add workflows/gestionar-backlog-roadmap/workflow.md
  git commit -m "feat: add ready flag to gestionar-backlog-roadmap workflow"
  ```