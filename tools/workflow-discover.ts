import { tool } from "@opencode-ai/plugin"
import { join } from "node:path"

export default tool({
  description: "List available workflows from .SAC/workflows/",
  args: {
    dir: tool.schema.string().optional().describe("Custom workflows directory path (default: .SAC/workflows/)"),
  },
  async execute(args, context) {
    const worktree = context.worktree || context.directory
    const scriptPath = join(worktree, ".opencode", "tools", "scripts", "workflow-discover.sh")

    try {
      const result = args.dir
        ? await Bun.$`bash ${scriptPath} ${args.dir}`.text()
        : await Bun.$`bash ${scriptPath}`.text()
      return result.trim()
    } catch (err) {
      return `Error: ${err instanceof Error ? err.message : String(err)}`
    }
  },
})
