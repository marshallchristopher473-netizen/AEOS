# AGENTS

## Copilot cloud agent reliability defaults

- Do not use Auto model selection for delegated or child agents when an explicit model can be selected.
- Before invoking any delegated `task`, `general-purpose`, `explore`, `research`, `code-review`, or `security-review` agent, choose a model that is explicitly available in the current GitHub Copilot cloud-agent session.
- Prefer `GPT-5.6 Sol` for complex repository analysis when it is available; otherwise choose another model shown as available in the current session.
- Never hard-code or request a model that the current GitHub Copilot cloud-agent session does not expose.
- If no explicit child-agent model is available, do not fail the task and do not retry Auto repeatedly. Continue the work in the primary agent without delegation and report the limitation.
- Avoid unnecessary recursive delegation. Repository audits, build checks, and test inspection should run in the primary agent unless delegation materially improves the task.

## AEOS canonical workstation

Codespaces built from this repository's `.devcontainer/devcontainer.json` are the canonical AEOS engineering environment — not an ad hoc terminal. Any agent working in this repo (Copilot, Claude, or otherwise) should:

- Read `.github/copilot-instructions.md` first for architecture, current P0 gate status, and which build/test scripts to use.
- Follow the path-specific instructions in `.github/instructions/` when touching `backend/app/**`, `backend/supabase/**`, or `frontend/**`.
- Use `.github/prompts/p0-security.prompt.md` as the starting workflow for any P0 security task.
- Prefer `scripts/verify_environment.sh`, `scripts/verify_backend.sh`, `scripts/verify_frontend.sh`, and `scripts/verify_p0_security.sh` over improvised commands — they're the versions actually verified to work against this repo.
- Never treat a prior commit message, PR title, or audit document as evidence on its own. Confirm against `git log`/`git cat-file` and the actual source before relying on it — this repository's history includes claimed commits and completed controls that did not exist when checked.
- P0 Security gates all feature work. See `.github/copilot-instructions.md` for the current list of frozen product areas.
