# AGENTS

## Copilot cloud agent defaults

- Do not use Auto model selection for delegated/child agents.
- When invoking a delegated `task`/`general-purpose`/`explore`/`research`/`code-review`/`security-review` agent, always pass an explicit `model` value.
- Prefer `gpt-5.3-codex` for delegated agents unless a task explicitly needs a different model.
