# PR #23 dependency security review

## Source and scope

Inventory recovered from PR #23 head
`38199ec5cb10c7e695dab3af835e649a7936b280`, its installed lockfile, and
[CI run 37206075011](https://github.com/marshallchristopher473-netizen/AEOS/actions/runs/37206075011)
on 2026-10-04. `npm audit --audit-level=low` exited 1 with **7 affected
packages: 6 high, 1 critical**. These are package totals, not seven distinct
advisories. All dependencies, including development dependencies, are audited.
This is the reported npm gate inventory, not an independent audit of Python,
containers, hosted authentication, or all application code.

## Every reported affected package

Paths below are relative to `frontend/`. The brace-expansion advisories apply
to all five installed copies. The four dependent findings inherit the braces
advisory; they do not have independent advisories or independent patched
versions in this audit.

| Affected package | Installed version before fix | Advisory | Installed dependency path | Patched version / disposition |
| --- | --- | --- | --- | --- |
| `brace-expansion` | `1.1.18` (four copies), `5.0.9` (one copy) | GHSA-q2hr-2g5m-vwhr; GHSA-qhr7-859c-m2p7; GHSA-6j4f-fj2g-mc7p | All five paths and consumers below | `1.1.21` and `5.0.12` cover all three advisories; applied |
| `braces` | `3.0.3` | GHSA-vfj7-8cjw-p6xm | `node_modules/braces`; config → Next ESLint plugin → fast-glob → micromatch → braces | No published patched version; remains blocked |
| `micromatch` | `4.0.8` | Inherits GHSA-vfj7-8cjw-p6xm through braces | `node_modules/micromatch`; config → Next ESLint plugin → fast-glob → micromatch | No compatible audit-clearing patched dependency chain established; unchanged |
| `fast-glob` | `3.3.1` | Inherits GHSA-vfj7-8cjw-p6xm through micromatch → braces | `node_modules/fast-glob`; config → Next ESLint plugin → fast-glob | No compatible audit-clearing patched dependency chain established; unchanged |
| `@next/eslint-plugin-next` | `16.3.4` | Inherits GHSA-vfj7-8cjw-p6xm through fast-glob → micromatch → braces | `node_modules/@next/eslint-plugin-next`; eslint-config-next → plugin | No compatible audit-clearing patched dependency chain established; unchanged |
| `eslint-config-next` | `16.3.4` | Inherits GHSA-vfj7-8cjw-p6xm through plugin → fast-glob → micromatch → braces | `node_modules/eslint-config-next`; direct development dependency | Audit suggests `14.2.35` as a breaking downgrade, not a compatible patch; not applied |
| `next` | `16.3.4` | GHSA-vcvr-r3jv-pc5j | `node_modules/next`; direct runtime dependency | `16.3.6`; applied |

Here “config” is `eslint-config-next@16.3.4`. The complete versioned chain for
the remaining advisory is:

`eslint-config-next@16.3.4 → @next/eslint-plugin-next@16.3.4 → fast-glob@3.3.1 → micromatch@4.0.8 → braces@3.0.3`.

## Advisory-specific patch evidence

The aggregate audit marks brace-expansion high because two of its three
advisories are high. The quadratic-time advisory itself is moderate.

| Advisory and severity | Affected versions relevant to installed copies | First patched versions on those lines | Selected fix |
| --- | --- | --- | --- |
| [GHSA-q2hr-2g5m-vwhr](https://github.com/advisories/GHSA-q2hr-2g5m-vwhr), moderate: quadratic rewrite CPU denial of service | `<1.1.21`; `>=4.0.0 <5.0.12` | `1.1.21`; `5.0.12` | Both installed lines updated to these versions |
| [GHSA-qhr7-859c-m2p7](https://github.com/advisories/GHSA-qhr7-859c-m2p7), high: nested-group recursion stack exhaustion | `<1.1.20`; `>=4.0.0 <5.0.11` | `1.1.20`; `5.0.11` | Superseded by `1.1.21`; `5.0.12` to cover all findings |
| [GHSA-6j4f-fj2g-mc7p](https://github.com/advisories/GHSA-6j4f-fj2g-mc7p), high: parseCommaParts recursion stack exhaustion | `<1.1.19`; `>=4.0.0 <5.0.10` | `1.1.19`; `5.0.10` | Superseded by `1.1.21`; `5.0.12` to cover all findings |
| [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), high: braces AST walker stack exhaustion | Advisory: `<=3.0.3`; npm audit reports `*` because no safe release is known | None; registry latest is `3.0.3` at review time | Unresolved, including the four dependent packages |
| [GHSA-vcvr-r3jv-pc5j](https://github.com/advisories/GHSA-vcvr-r3jv-pc5j), critical: Node.js next/og ImageResponse remote code execution | `>=16.2.0 <16.3.6` | `16.3.6` | `16.3.6` |

## Every brace-expansion installation and dependency path

### `node_modules/@eslint/config-array/node_modules/brace-expansion`

- `eslint@9.39.5 → @eslint/config-array@0.21.2 → minimatch@3.1.5 → brace-expansion@1.1.18`

### `node_modules/@eslint/eslintrc/node_modules/brace-expansion`

- `eslint@9.39.5 → @eslint/eslintrc@3.3.7 → minimatch@3.1.5 → brace-expansion@1.1.18`

### `node_modules/eslint/node_modules/brace-expansion`

- `eslint@9.39.5 → minimatch@3.1.5 → brace-expansion@1.1.18`

### `node_modules/eslint-config-next/node_modules/brace-expansion`

- `eslint-config-next@16.3.4 → eslint-plugin-import@2.32.0 → minimatch@3.1.5 → brace-expansion@1.1.18`
- `eslint-config-next@16.3.4 → eslint-plugin-jsx-a11y@6.10.2 → minimatch@3.1.5 → brace-expansion@1.1.18`
- `eslint-config-next@16.3.4 → eslint-plugin-react@7.37.5 → minimatch@3.1.5 → brace-expansion@1.1.18`

### `node_modules/brace-expansion`

- `eslint-config-next@16.3.4 → typescript-eslint@8.69.0 → @typescript-eslint/eslint-plugin@8.69.0 → @typescript-eslint/type-utils@8.69.0 → @typescript-eslint/typescript-estree@8.69.0 → minimatch@10.2.6 → brace-expansion@5.0.9`
- `eslint-config-next@16.3.4 → typescript-eslint@8.69.0 → @typescript-eslint/eslint-plugin@8.69.0 → @typescript-eslint/type-utils@8.69.0 → @typescript-eslint/utils@8.69.0 → @typescript-eslint/typescript-estree@8.69.0 → minimatch@10.2.6 → brace-expansion@5.0.9`
- `eslint-config-next@16.3.4 → typescript-eslint@8.69.0 → @typescript-eslint/eslint-plugin@8.69.0 → @typescript-eslint/utils@8.69.0 → @typescript-eslint/typescript-estree@8.69.0 → minimatch@10.2.6 → brace-expansion@5.0.9`
- `eslint-config-next@16.3.4 → typescript-eslint@8.69.0 → @typescript-eslint/parser@8.69.0 → @typescript-eslint/typescript-estree@8.69.0 → minimatch@10.2.6 → brace-expansion@5.0.9`
- `eslint-config-next@16.3.4 → typescript-eslint@8.69.0 → @typescript-eslint/typescript-estree@8.69.0 → minimatch@10.2.6 → brace-expansion@5.0.9`
- `eslint-config-next@16.3.4 → typescript-eslint@8.69.0 → @typescript-eslint/utils@8.69.0 → @typescript-eslint/typescript-estree@8.69.0 → minimatch@10.2.6 → brace-expansion@5.0.9`

## Minimal compatible repair

Only Next.js and its version-coupled `@next/env` / eight platform SWC packages
move from `16.3.4` to `16.3.6`, and the five brace-expansion installations move
to the smallest releases covering all reported advisories on their existing
major lines. The manifest raises the Next.js lower bound to `^16.3.6`.
There are no changes to React, Supabase, ESLint configuration, the PostCSS
override, backend requirements, review UI/API code, shared services, or migrations.
No force upgrade, major downgrade, dependency exclusion, audit threshold change,
`continue-on-error`, or vulnerability suppression is used.

Local npm registry access was unavailable. Exact published registry metadata
was retrieved for each changed package, and its version, tarball URL, integrity,
and dependency metadata were used for the bounded lockfile update. The final
candidate must pass `npm ci` integrity and manifest/lockfile validation and
`npm ls --all` on the GitHub runner; a manually edited lockfile alone is not
verification. The workflow retains raw `npm audit --json` as an artifact and
uses bash pipefail so its nonzero exit still fails the job.

The unpatched braces chain remains a merge blocker. Removing lint coverage,
replacing the glob implementation with an API-incompatible override, using an
unpublished fork, or downgrading the Next.js ESLint configuration to 14.x would
exceed this compatible dependency repair. A supported upstream fix or a separately
reviewed tooling migration is needed to clear it.

Registry inspection also confirms `@next/eslint-plugin-next@16.3.6` still
requires `fast-glob@3.3.1`; simply matching the ESLint package version to the
Next.js patch would retain the vulnerable chain. Latest `micromatch@4.0.8`
still requires `braces@^3.0.3`, and latest `fast-glob@3.3.3` still requires
`micromatch@^4.0.8`. These unrelated updates would not resolve this advisory.

## Follow-up: scoped glob replacement for the braces chain

This is the separately reviewed tooling change referred to above. Registry
state rechecked 2026-10-04: `braces@3.0.3` is still latest and the advisory
range is `<=3.0.3`; `@next/eslint-plugin-next` still requires `fast-glob@3.3.1`
at `16.3.8` (latest) and `16.4.0-canary.59`. No upstream repair exists.

**Exposure before the change.** The chain is development-only:
`npm audit --omit=dev` reports 0 findings, and the Next.js runtime vendors
`picomatch`, not braces. The plugin's only fast-glob call is `globSync` in
`dist/utils/get-root-dirs.js`, reached only when ESLint `settings.next.rootDir`
is set. AEOS does not set it, so braces never executed during lint.

**Change.** `frontend/package.json` adds one scoped override:
`"@next/eslint-plugin-next": { "fast-glob": "npm:tinyglobby@0.2.17" }`.
`tinyglobby@0.2.17` was already installed through `eslint-config-next`
(`eslint-import-resolver-typescript` and `@typescript-eslint/typescript-estree`);
the aliased copy has the same integrity hash. The lockfile, regenerated by
`npm install`, removes 16 packages (`braces`, `micromatch`, `fast-glob`,
`fill-range`, `to-regex-range`, `is-number`, `merge2`, a nested `glob-parent`,
a nested `picomatch@2`, the three `@nodelib/*` walkers, and their four queue
helpers) and adds only that aliased entry.
Next.js, ESLint, every lint rule, and the audit gate are unchanged.

**Known divergence.** tinyglobby is not a drop-in fast-glob. With
`onlyDirectories: true` it also returns subdirectories of a directory pattern
(`src/` → `src` plus every directory below it) and includes the base of `**`
patterns. That matters only when `settings.next.rootDir` is set. A shim that
disables directory expansion still diverges on `**`, so none was added.

**Guards** (`frontend/tests/lint-glob-override.test.mjs`, run in CI):

1. The plugin's `fast-glob` resolves to tinyglobby, and every `fast-glob`
   member the plugin references is a function it provides. The test fails with
   "remove the package.json override" once the plugin stops requiring fast-glob.
2. The effective ESLint config leaves `settings.next.rootDir` unset.
3. `@next/next/no-html-link-for-pages`, the only rule that uses the glob,
   still reports a raw `<a href="/students">` in an app route.

Each guard was shown to fail under a deliberate break: rootDir set, a fast-glob
member the override lacks, the plugin dropping fast-glob, the rule disabled,
and the override removed.

**Removal condition.** Delete the override when `@next/eslint-plugin-next`
stops depending on fast-glob, or when a braces release outside the advisory
range is published and reaches this tree, and re-run the audit.

## Verification and limits

The final PR description records the full head SHA and corresponding Actions
run. GitHub checks out a PR merge commit; its tree must match the final candidate
tree before attributing the results to that head. Consult that run's raw audit
artifact and step logs for the measured remaining findings and functional results.
No future CI result is claimed here before execution.

Required checks are `npm ci`, full dependency audit, `npm ls --all`, API contracts,
lint, type check, production build, and Chrome save/reload, denied-write retention,
and cross-tenant denial against the existing synthetic backend. The separate
backend suite and real PostgreSQL RLS/mutation jobs exercise authorization and
tenant isolation. Browser sessions and persistence are synthetic; these checks
do not establish hosted Supabase readiness or production JWT verification.
PR #23 remains draft; no merge or deployment is authorized by these results.
