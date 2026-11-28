# AEOS agent setup and pilot verification

## Scope

This runbook is for the public-code, synthetic-data development environment. Keep confidential and commercial material outside this public repository. Existing module instructions and CI remain authoritative. This PR does not activate any provider, install a GitHub App, store a credential, merge a pilot or establish release readiness.

## Claude Code in a GitHub Codespace

From the repository's Code > Codespaces menu, open a personal development Codespace with no production secrets. Use a feature branch instead of main. Follow the current [Claude Code quickstart](https://code.claude.com/docs/en/quickstart):

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
git status --short
claude
```

Complete the provider login in its official authentication flow. Ask Claude to plan before editing; approve only necessary commands. Start with the nearest module brief. Review diffs and independent test evidence before pushing.

For GitHub Actions, [the official integration guide](https://code.claude.com/docs/en/github-actions) describes /install-github-app and manual setup. Scope the app to this repository only. Do not enable public comment triggers or recurring paid automation for this initial pilot. The proposed Claude readiness-audit workflow is manual, owner-only, main-only and additionally disabled unless repository variable AEOS_ENABLE_CLAUDE_AUDIT equals true. It uses a read-only GitHub token and a bounded fixed prompt; it does not execute project code. Review the pinned third-party action, branch protections and credential handling before enabling it. Configure ANTHROPIC_API_KEY through Actions secrets (or adapt the action input to CLAUDE_CODE_OAUTH_TOKEN if using the subscription credential). Never paste keys in a prompt or source file. Run it once from Actions, inspect the logs and billing, and disable the variable if the experiment is complete. This workflow is an optional advisory report, not a required CI check.

## DeepSeek

Use DeepSeek for a second opinion on a sanitized, bounded code fixture; it is a different provider even if accessed from Claude Code. [Official integration](https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/) documents the compatible endpoint. In a **separate disposable environment**, with only a limited test DeepSeek key set as DEEPSEEK_API_KEY, run:

```bash
(
  unset ANTHROPIC_API_KEY
  export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
  export ANTHROPIC_AUTH_TOKEN="$DEEPSEEK_API_KEY"
  export ANTHROPIC_MODEL=deepseek-flash
  export ANTHROPIC_DEFAULT_OPUS_MODEL=deepseek-flash
  export ANTHROPIC_DEFAULT_SONNET_MODEL=deepseek-flash
  export ANTHROPIC_DEFAULT_HAIKU_MODEL=deepseek-flash
  export CLAUDE_CODE_SUBAGENT_MODEL=deepseek-flash
  claude
)
```

Check the provider/model, current pricing, and permission settings before sending any code. Do not use a provider-routed session for private files or secrets. The subshell prevents exports from changing the parent shell. Do not install these exports globally.

## DeepSeek Harness (experimental, separate from Claude Code)

Read [the upstream safety notice](https://github.com/deepseek-ai/deepseek-harness/blob/master/SAFETY.md) before running. It is a developer preview, not a security boundary. Use a disposable VM/container with no production credentials, Codespaces/GitHub write token, host filesystem mounts, private repository, or real records; provide only a scrubbed synthetic snapshot and a limited test API key. Do NOT expose its web service publicly. Review package version and dependencies before executing.

```bash
node --version
npm view @deepseek-ai/dsh version
# Substitute the specific reviewed version for VERSION below:
npx @deepseek-ai/dsh@VERSION web --no-open
```

Use the local/private port only (default 3080); select restrictive permissions and no unreviewed plugins. Treat the agent's output as a proposed patch. Transfer only reviewed text/diffs back into the main development environment. Do not give Harness direct commit/push privileges or any production data.

## One-ticket workflow

1. Inspect the current default branch, open PRs and nearest README before selecting a task. Existing completed work should not be rebuilt.
2. Record a baseline SHA, one issue, permitted paths, acceptance tests and stop criteria. If another PR owns the same work, review that PR rather than duplicate it.
3. Claude Code: plan, implement a minimal fix and run focused deterministic tests in a feature branch.
4. DeepSeek: critique the sanitized diff and design counterexamples without editing the primary working copy.
5. Harness: reproduce one claimed defect or test independently in a throwaway snapshot; manually review its suggested patch.
6. CI: run relevant suites, verify actual check runs on the exact candidate SHA, then inspect any failed/skipped checks. A human decides release.

## Existing check commands (run in disposable development only)

- Backend: `pip install -r backend/requirements-dev.txt`, then from backend `python -m pytest tests/ -v`. See existing CI for PostgreSQL RLS enforcement and M01–M18 mutation verification; a skipped DB test is not isolation evidence.
- Frontend: from frontend, `npm ci`, `npm run lint`, `npx tsc --noEmit`, `npm run build`, `npm audit --audit-level=high`.
- ELA pilot: from ela-pilot, `npm ci`, `npm test`, `npm run typecheck`, `npm run build`, `npm audit`. Read the module's own known risks and run with mock provider and synthetic data only. Do not expose the existing pilot to the network.
- Other pending modules: inspect the relevant PR's own instructions and tests; do not assume these are merged.

## Copyable bounded prompts

### Claude implementation
Read AGENTS.md, CLAUDE.md, the nearest module README and relevant current tests. Identify one actionable, reproducible blocker for the specified pilot. Before editing, report its location, baseline SHA, smallest fix, intended tests and files. Change only what this issue requires. Run actual focused tests and report commands, exit codes, skips, remaining risks. Do not merge or deploy.

### DeepSeek independent review
Review only the supplied sanitized diff and acceptance criteria. Attempt to disprove correctness: input validation, evidence provenance, permission checks, edge cases and false success. For every finding cite a path/line and reproducible case, distinguish confirmed from suspected, and propose a minimal regression test. Do not edit, call external tools, or invent results.

### Harness independent reproduction
Inspect this disposable synthetic snapshot. Reproduce one candidate defect using its smallest permitted deterministic test. No network, real records, production keys, plugins, push or deployment. Ask before running commands. Return the reproduction steps, observed output and a proposed patch or refutation. Stop after one finding or when blocked.

## Evidence record (blank)

- Issue / pilot:
- Baseline SHA / candidate SHA:
- Permission and synthetic-data check:
- Tool / provider / model / elapsed time / usage:
- Test command / exit / expected / observed:
- Reproducible finding / path / severity:
- Independent second check:
- Remaining blockers / human reviewer:
- Decision: HOLD / READY FOR REHEARSAL / READY FOR AUTHORIZED FEASIBILITY PILOT.
- Outcome evidence (separate from engineering verification):

Use one record per bounded task. A pass is not pilot efficacy, a paid customer or a validated outcome.
