---
applyTo: "frontend/**"
---

# Frontend instructions

## Current, verified state

- `frontend/src/lib/api.ts` is the shared API helper: reads a bearer token from `localStorage` (`aeos_access_token`) and attaches it to requests. Several pages bypass it and call `http://127.0.0.1:8000` directly with a hardcoded URL instead of using this helper or `NEXT_PUBLIC_API_URL` — both patterns currently coexist.
- `frontend/src/app/assessments/new/page.tsx` currently renders editable `<input>` fields for `organization_id` and `created_by` and submits them directly to the backend. This is exactly the pattern to remove, not preserve.
- No `package.json` `test` script exists. `npm run lint` cannot run non-interactively (no committed ESLint config). `npm run build` works.

## Rules

1. **Never collect `organization_id`, `created_by`, `user_id`, `owner_id`, or any other identity/tenant field from a form input, hidden field, or client-side default.** These must be derived server-side once the backend enforces `get_current_actor` (see `.github/instructions/backend-security.instructions.md`). Once the backend stops accepting these fields, remove the corresponding inputs here — don't leave dead UI that implies the user controls tenant/ownership.
2. **Use `frontend/src/lib/api.ts`'s `apiFetch` for all backend calls.** Do not add another hardcoded `http://127.0.0.1:8000` call site; if you find one, migrate it to `apiFetch` as part of the same change rather than adding to the inconsistency.
3. **Do not silently "fix" the credential storage model (`localStorage` bearer token) as a side effect of an unrelated change.** It's a known, flagged gap (XSS could exfiltrate the token); changing it is a deliberate security decision that needs its own review, not a drive-by edit.
4. Adding a real, non-interactive ESLint config (so `scripts/verify_frontend.sh` can eventually run lint) is a legitimate, narrowly-scoped improvement — but treat it as its own change, not bundled silently into an unrelated PR.
