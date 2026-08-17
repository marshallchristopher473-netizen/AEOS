# AGENTS

## Copilot cloud agent reliability defaults

- Do not use Auto model selection for delegated or child agents when an explicit model can be selected.
- Before invoking any delegated `task`, `general-purpose`, `explore`, `research`, `code-review`, or `security-review` agent, choose a model that is explicitly available in the current GitHub Copilot cloud-agent session.
- Prefer `GPT-5.6 Sol` for complex repository analysis when it is available; otherwise choose another model shown as available in the current session.
- Never hard-code or request a model that the current GitHub Copilot cloud-agent session does not expose.
- If no explicit child-agent model is available, do not fail the task and do not retry Auto repeatedly. Continue the work in the primary agent without delegation and report the limitation.
- Avoid unnecessary recursive delegation. Repository audits, build checks, and test inspection should run in the primary agent unless delegation materially improves the task.
