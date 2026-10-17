# BARS deployment: security posture and runbook

Part 1 of 3. See also [BARS_ADAPTER_CONTRACT_SPEC.md](BARS_ADAPTER_CONTRACT_SPEC.md)
and [BARS_RELEASE_EVIDENCE_AND_ROLLBACK.md](BARS_RELEASE_EVIDENCE_AND_ROLLBACK.md).

This is a gate specification, not a readiness claim. It corrects the four BARS
deployment drafts that were reviewed outside this repository. Those drafts can
support implementation planning; they do not establish pilot readiness, and
nothing in this directory does either.

## Current disposition

| Item | Status |
| --- | --- |
| BARS pilot readiness | **NOT READY** |
| Every gate in this directory | `BLOCKED` or `NOT TESTED` |
| AEOS P0 security gate | Not recorded as `P0 VERIFIED` in this repository |
| Real student data in BARS | **Prohibited.** Synthetic data only |

## Provenance and what was not supplied

| Input | What it contains | Status |
| --- | --- | --- |
| BARS deployment ZIP | React/Vite application, `localStorage` persistence, AI proxy endpoints | Reviewed outside this repository; not committed |
| AEOS adapter | Referenced by the drafts | **Not supplied** |
| "21 adapter signatures" | Referenced by the drafts | **Not supplied, count unverified** |
| Candidate commit `7f3788…` | Referenced by the drafts | **UNVERIFIED.** It cannot be linked to the ZIP or the adapter, and it does not resolve in this repository |

A commit SHA is evidence only when `git cat-file -e <sha>^{commit}` succeeds in
the repository that holds the code being released. Until then, treat `7f3788…`
as a label, not a provenance anchor.

## Relationship to the AEOS P0 gate

The AEOS P0 gate (`docs/P0_MUTATION_VERIFICATION.md`,
`.github/agents/aeos-p0-security-completion.agent.md`) blocks product-module
expansion, BARS included, until a separate verifier records `P0 VERIFIED`.
This specification does not build BARS. It defines what BARS must prove
before it is deployed. If BARS reads or writes AEOS data through the adapter,
its deployment is **BLOCKED** until both gates pass: P0 and the gates in this
directory.

## Platform facts this specification relies on

Each row is labelled by how strongly it is established. Re-check every row
against the live Base44 page during Phase 0, because plan terms and platform
behaviour change.

| # | Fact | Strength | Source |
| --- | --- | --- | --- |
| F1 | Entity access rules are an `rls` object in the entity schema, with separate `create`, `read`, `update` and `delete` keys | Documented | Base44 entity security docs; Base44 CLI RLS reference |
| F2 | A role check is written `{"user_condition": {"role": "admin"}}`. `user_condition` supports equality only | Documented | Base44 CLI RLS reference |
| F3 | `{{user.email}}`, `{{user.data.<field>}}` and similar are **template values inside JSON rules**. They are not SQL, and SQL containing `{{user.role}}` is not executable PostgreSQL | Documented (template syntax); inference (not SQL) | Base44 CLI RLS reference |
| F4 | Service-role access (`base44.asServiceRole.*`) skips every access rule. A backend function that uses it must enforce its own authorization | Documented | Base44 entity security docs; Base44 SDK client reference |
| F5 | Anyone can call a backend function unless the app requires login or the function verifies the caller | Documented | Base44 security-scan docs |
| F6 | Base44's own service-role example checks only that a user is signed in (`auth.me()`). That is authentication, not authorization | Observed | Base44 SDK functions reference |
| F7 | Access-rule changes take effect immediately. Base44 recommends testing in Preview first | Documented | Base44 data-permissions docs |
| F8 | New private apps require the Starter plan or above. Free-plan private apps created before 2026-02-06 are grandfathered | Documented | Base44 billing and plans docs |
| F9 | Backend functions are a Builder-plan feature, and paid features such as backend functions stop working if a workspace drops to Free | Documented (stop on Free); Base44 blog (Builder tier) | Base44 billing docs; Base44 pricing blog |
| F10 | Regular users can read and update only their own User record | Documented | Base44 entity security docs |
| F11 | The SDK type for `auth.updateMe()` excludes only `id`, `created_date`, `updated_date`, `app_id` and `is_service`. It does **not** exclude `role` or custom fields | Observed in SDK reference. A client type proves nothing about server enforcement in either direction | Base44 SDK auth reference |
| F12 | Whether the server rejects a self-update to `role`, or to a custom field that an access rule reads | **NOT DOCUMENTED** | None. Must be tested (U1–U3) |

## Correction C1: replace the illustrative SQL with Base44 entity rules

The drafts' SQL is not how Base44 entities are protected, and the
`{{user.role}}` placeholder would fail as PostgreSQL. Express every BARS entity's
access as a Base44 `rls` object (F1–F3).

The containment-posture rule for a BARS entity looks like this:

```json
"rls": {
  "create": { "user_condition": { "role": "admin" } },
  "read":   { "user_condition": { "role": "admin" } },
  "update": { "user_condition": { "role": "admin" } },
  "delete": { "user_condition": { "role": "admin" } }
}
```

This example only illustrates the format. The authoritative rule is the one
exported from the deployed app and recorded, with its policy version, in an
evidence record (Part 3).

Entity rules do not protect anything reached through the service role (F4),
and backend functions are publicly callable by default (F5). Every BARS
backend function, including each AI proxy endpoint, must therefore do all of
the following:

1. Resolve the caller from the request and return `401` when there is none.
2. Check the caller's role and return `403` when it is not permitted. Signing in
   alone is not enough (F6).
3. Scope every service-role query to the caller's permitted records. Never
   accept a tenant, owner or role value from the request body as authority.
4. Deny by default. An unrecognized operation or input shape is rejected.
5. Keep provider API keys in Base44 secrets, read server-side only.
6. Send no student-identifying data to an AI provider unless a data processing
   agreement covering that provider exists. Until then, synthetic data only.

## Correction C2: check the visibility entitlement before Phase 1

The drafts assumed that "set the app private" is available on the Free plan.
It is not, for new apps (F8). Phase 0 must establish the following before any
configuration step:

- the workspace plan, recorded with its date;
- if the app relies on the grandfathering exception, its creation date, which
  must be before 2026-02-06;
- that the private or workspace-only visibility control is actually present and
  applied, shown by a non-member failing to load the app (test C6);
- if backend functions are required, that the plan includes them (F9).

If private visibility is unavailable, Phase 1 is **BLOCKED**. A public app on an
unlisted URL is not a substitute.

## Correction C3: reclassify the `updateMe` finding

Change the finding from "exploit" to **unverified authorization risk**.

Updating one's own profile is documented behaviour (F10). The security question
is narrower: can an ordinary user change a field that grants privilege? Nothing
reviewed establishes the claimed exploit, and nothing establishes that buying
Builder or above resolves it. The SDK type leaves the question open (F11, F12).
The risk becomes severe if tenant membership is stored on the User record and
an access rule reads it through `{{user.data.<field>}}`. A self-edit to that
field would then move a user into another tenant.

Resolve it by test, not by plan purchase:

| ID | Actor | Action | Expected |
| --- | --- | --- | --- |
| U1 | ordinary `user` | `updateMe({ role: "admin" })` | rejected, or no persisted change **and** no new access |
| U2 | ordinary `user` | `updateMe({ <tenant field>: <other tenant> })` | rejected, or no persisted change **and** no new access |
| U3 | ordinary `user` | `updateMe` on every other custom field that any `rls` rule reads | rejected, or no persisted change **and** no new access |

"No new access" is checked by repeating the denied read after the update
attempt. U1–U3 must `PASS` before any rule in BARS depends on a user-editable
attribute.

## Correction C4: separate containment from tenant isolation

Admin-only access proves that ordinary users are excluded. It does not prove
that teachers in different organizations are isolated from each other. These
are two postures with different evidence:

| | Posture A: containment | Posture B: tenant isolation |
| --- | --- | --- |
| Purpose | Internal testing by named operators | Ordinary teachers from more than one organization |
| Who is `admin` | Named operators only | Named operators only |
| Teacher role | No teacher access | `user` role, tenant-scoped rules |
| Data | Synthetic only | Synthetic only until a separate data gate exists |
| Proves | Anonymous and non-admin users are denied | A user in one tenant cannot read or change another tenant's records, in both directions |
| Does not prove | Isolation between organizations | Anything about real student data handling |
| Tests | C1–C6, U1–U3 | C1–C6, U1–U3, T1–T6 |

**Making every pilot teacher an admin is prohibited.** It dissolves posture A,
because every admin sees every record in every organization, and it can never
satisfy posture B.

**Decision rule.** For a first pilot with a single organization, the smallest
safe option is one Base44 app per organization. Isolation is then structural,
and posture B is not needed until a second organization joins the same app.
Choosing a shared multi-organization app commits the release to the full T1–T6
matrix.

## Corrected runbook order

Each phase stays `BLOCKED` until its exit criterion is backed by evidence
records (Part 3) for the exact candidate SHA, deployment and policy version.

| Phase | Work | Exit criterion |
| --- | --- | --- |
| 0. Prerequisites and entitlement | Record the candidate SHA and confirm it resolves. Record the plan and visibility entitlement (C2). Confirm P0 status. Prepare the synthetic dataset and synthetic test identities. Capture the rollback bundle for the current state | All Phase 0 items recorded. Any gap means the release is `BLOCKED` |
| 1. Containment configuration | Private visibility. Require login. Admin-only `rls` on every entity (C1). Authorization in every backend function (C1). Remove service-role use that does not need it | Configuration exported and recorded as a policy version |
| 2. Containment verification | Run C1–C6 and U1–U3 in Preview, then against the deployment | All `PASS` |
| 3. Adapter enablement | Enable adapter operations one at a time under Part 2 | Each enabled operation has its R1–R6 decisions and A1–A6 evidence |
| 4. Tenant isolation verification | Only for posture B. Run T1–T6 with two tenants and ordinary users | All `PASS`, both directions |
| 5. Release decision | Sign-off under Part 3 | Reviewer decision recorded |

## Open risks outside the three corrections

- **`localStorage` persistence.** Data written there stays on the device,
  unaudited and readable by anyone at a shared school computer. Keep it
  synthetic. Move it server-side before any real data gate is considered.
- **Two backends.** BARS on Base44 beside AEOS on FastAPI and Supabase
  duplicates authentication, authorization and audit. Revisit this at the BARS
  validation milestone. It does not block a synthetic-data internal test.

## Sources

Checked 2026-10-17. `docs.base44.com` could not be fetched directly from the
build environment. The rows above are corroborated by search results quoting
these pages and by the Base44 SDK and CLI reference. Re-read each page at
Phase 0.

- Base44 entity security: <https://docs.base44.com/developers/backend/resources/entities/security>
- Base44 data permissions: <https://docs.base44.com/Setting-up-your-app/Managing-security-settings>
- Base44 RLS examples: <https://docs.base44.com/developers/skills/base44-cli/references/rls-examples>
- Base44 security scan: <https://docs.base44.com/Guides/Using-security-check>
- Base44 billing and plans: <https://docs.base44.com/Account-and-billing/Billing-and-plans>
- Base44 pricing: <https://base44.com/pricing>
- Base44 pricing blog (Builder features): <https://base44.com/blog/how-much-does-base44-cost>
