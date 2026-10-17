# BARS deployment: adapter contract specification

Part 2 of 3. See also
[BARS_SECURITY_POSTURE_AND_RUNBOOK.md](BARS_SECURITY_POSTURE_AND_RUNBOOK.md)
and [BARS_RELEASE_EVIDENCE_AND_ROLLBACK.md](BARS_RELEASE_EVIDENCE_AND_ROLLBACK.md).

The adapter is the code that lets BARS call AEOS. This document defines what
it must satisfy before any operation is enabled. The adapter source was not
supplied, so every operation is `NOT TESTED`.

## What the current stub does and does not establish

**It fails closed.** Every `call()` throws, so no live operation can run. That
is the correct default. Keep it until an operation is individually enabled
under the rule at the end of this document.

**It does not establish verification.**

- `VerifiedOperation` is a TypeScript interface. Interfaces are erased at
  compile time and do nothing at runtime. The name asserts a property that no
  code checks.
- A request or response typed as `unknown` (or `any`) undergoes no validation.
  Typing data as `unknown` is not validating it.
- The snippet neither implements nor lists 21 methods, so coverage of "21
  signatures" cannot be checked against it.

## Requirements

### R1. Exact signatures, extracted from the real adapter

Extract the operation list from the adapter source at a recorded commit SHA,
not from a prompt, summary or remembered count. The extraction determines the
count; do not assume it is 21.

Record each operation in this inventory:

| Field | Meaning |
| --- | --- |
| `operation` | Exact exported name |
| `source` | File path and line at the recorded SHA |
| `transport` | HTTP method and path, or SDK call |
| `request_schema` | Runtime schema identifier (R2) |
| `response_schema` | Runtime schema identifier (R2) |
| `auth` | Required caller identity and role |
| `tenant_scope` | How the tenant is derived server-side. Never from the request |
| `side_effects` | `read-only`, or what it writes |
| `replay_control` | R5 mechanism, or `N/A: read-only` |
| `concurrency` | R6 mechanism, or `N/A: no update` |
| `status` | `DISABLED` (default) or `ENABLED`, with an evidence record ID |

### R2. Runtime validation of requests and responses

- Validate the request against a runtime schema **before** any network call.
  Validate the response **before** returning it to the UI.
- Use one runtime validator for the whole adapter, for example Zod or
  JSON Schema with Ajv. Not both.
- An operation whose request or response schema is `unknown`, `any` or
  missing stays `DISABLED`.
- A validation failure returns `VALIDATION_FAILED` and causes no partial write.

### R3. Server-held credentials, and no silent demo fallback

- Service credentials live only in Base44 backend-function secrets or the AEOS
  server environment. Never in the browser bundle. In Vite, any `VITE_*`
  variable is compiled into client code, so no credential may use that prefix.
- A failed live operation returns an error to the user. It must **never**
  switch automatically to DEMO data. A silent fallback hides outages and lets
  an educator act on fabricated records as if they were real.
- Demo mode, if kept, is an explicit configuration chosen before the session
  starts. It must be visibly labelled on every screen and must not be able to
  reach live operations.

### R4. An evidence-backed decision for every contract item

Every requirement here (R1–R6) gets one decision per operation:

| Decision | When allowed | Evidence needed |
| --- | --- | --- |
| `IMPLEMENTED` | The control exists in code | Code path at the recorded SHA plus a passing A-series test record |
| `NOT APPLICABLE` | The control cannot apply to this operation | A written rationale, for example "read-only, so no replay control" |
| `DEFERRED` | Not built yet | The operation stays `DISABLED` |

A blank decision counts as `DEFERRED`.

### R5. Identifying a caller is not preventing replay

A reusable bearer token, API key, session ID, or a request ID that the server
never checks identifies the caller. It does not stop the same request from
being sent twice. Each mutating operation must name one replay control:

| Mechanism | What it requires |
| --- | --- |
| Idempotency key | Client-generated unique key. The server stores it under a uniqueness constraint with a defined retention period, and a repeat returns the original result without writing again |
| Signed nonce and timestamp | Request signature (for example HMAC) over the body, nonce and timestamp. The server rejects reuse of a nonce and timestamps outside a defined window |
| Natural idempotency | Repeating the request leaves the same state, for example setting a value rather than incrementing it. Must be shown by test A5 |

Read-only operations record `NOT APPLICABLE` with that rationale.

### R6. Defined concurrency behaviour

- Every mutable record carries a version, either an integer or a platform
  timestamp proven to change on every write.
- An update must include the version it expects.
- A version mismatch returns `CONFLICT` with the current version and **writes
  nothing**.
- On `CONFLICT`, the client reloads and shows the educator what changed. It
  never overwrites automatically. Last-write-wins is prohibited for official
  records.
- **Atomicity must be verified, not assumed.** If the platform offers no atomic
  compare-and-set, a read-then-write check inside a backend function leaves a
  race window. In that case, record the residual risk and the detection
  mechanism, such as a post-write version check plus an audit entry.

## Error contract

The adapter returns only these error codes. Each maps to an A-series test.

| Code | HTTP | Meaning |
| --- | --- | --- |
| `OPERATION_DISABLED` | 503 | The operation is not enabled. This is the stub's current behaviour |
| `UNAUTHENTICATED` | 401 | No verified caller |
| `FORBIDDEN` | 403 | The caller's role or tenant does not permit the operation |
| `VALIDATION_FAILED` | 400 or 502 | 400 for an invalid request. 502 for an invalid upstream response |
| `CONFLICT` | 409 | Stale version (R6). Nothing was written |
| `UPSTREAM_UNAVAILABLE` | 503 | The live call failed. No demo data substituted (R3) |

## Plan purchases are not controls

Builder or a higher plan may be needed for backend functions (Part 1, F9).
Buying a plan verifies none of R1–R6. Each control is established only by
code at a recorded SHA and a passing evidence record.

## Enablement rule

An operation moves from `DISABLED` to `ENABLED` only when all of the following
hold:

1. Its R1 inventory row is complete.
2. Each of R2–R6 has a decision under R4, with evidence for every
   `IMPLEMENTED` decision.
3. Tests A1–A6 (Part 3) pass for it, recorded against the exact candidate SHA,
   deployment and policy version.
4. Containment tests C1–C6 still pass after enabling it.

Enabling one operation never enables another.
