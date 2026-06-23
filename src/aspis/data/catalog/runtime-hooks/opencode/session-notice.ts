import type { Plugin } from "@opencode-ai/plugin"

/**
 * ASPIS session notice.
 *
 * On a new session, surface any open findings by running the shared deterministic notice
 * (.aspis/scripts/hooks/session_start.py) and printing its output. Best-effort: it never throws,
 * so a session always starts; the agent's own prestart (`aspis preflight`) is the enforcement.
 */
export const SessionNotice: Plugin = async ({ $, directory }) => {
  return {
    "session.created": async () => {
      // Interpreter baked at export (sys.executable) — never an unresolved name. `${py}` is quoted.
      const py = "__ASPIS_PY__"
      const script = `${directory}/.aspis/scripts/hooks/session_start.py`
      const result = await $`${py} ${script}`.quiet().nothrow()
      const out = result.stdout.toString().trim()
      if (out) console.log(out)
    },
  }
}
