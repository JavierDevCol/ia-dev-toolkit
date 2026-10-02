import test from "node:test"
import assert from "node:assert/strict"
import { execFileSync } from "node:child_process"
import path from "node:path"
import { fileURLToPath } from "node:url"

test("plugins/workflow-sac.ts parsea sin errores de sintaxis", () => {
  const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..")
  const entry = path.join(repoRoot, "plugins", "workflow-sac.ts")

  assert.doesNotThrow(() => {
    execFileSync(
      "npx",
      ["--yes", "esbuild", entry, "--bundle", "--platform=node", "--outfile=/dev/null", "--external:@opencode-ai/plugin"],
      { stdio: "pipe" }
    )
  })
})
