import type { Plugin } from "@opencode-ai/plugin"

/**
 * ASPIS runtime scope-guard.
 *
 * Blocks an out-of-scope Edit/Write before it runs by delegating to the shared
 * deterministic check (.aspis/scripts/hooks/runtime_guard.py) — the same scope
 * decision the git pre-commit uses. Throwing in tool.execute.before vetoes the call.
 */
export const ScopeGuard: Plugin = async ({ $, directory }) => {
  return {
    "tool.execute.before": async (input: any, output: any) => {
      const tool = String(input?.tool ?? "").toLowerCase()
      if (tool !== "edit" && tool !== "write") return

      const args = output?.args ?? {}
      const path = args.filePath ?? args.path ?? args.file_path
      if (!path) return

      const guard = `${directory}/.aspis/scripts/hooks/runtime_guard.py`
      const result = await $`python3 ${guard} ${path}`.quiet().nothrow()
      if (result.exitCode !== 0) {
        const reason = result.stderr.toString().trim()
        throw new Error(reason || `out of scope: ${path}`)
      }
    },
  }
}
