# Standalone browser acceptance — pilot review demo

This records the browser check that `tests/browser-acceptance.mjs` performs, and
the result of the run at the source below. It is a bounded check of the demo's
own behaviour. It is **not** an AEOS P0 approval, a hosted-security sign-off, a
P-TER-01 study approval, or evidence about grading time, workload or learning.

## What was checked

| Source | `e6f2de5c3329c47f34face0732e714817cde3af1` (PR #64) |
| --- | --- |
| Tree | `1cdae845a24d34146a4b636bb350010ea47655b8` |
| Runner | Chromium via Playwright, Node v22.23.4 |
| Surfaces | `file://` (offline, as the ZIP is opened) and a local same-origin HTTP host |
| Result | **46/46 checks passed on each surface, 0 failed** |

The five runtime files were taken straight from the commit and hash-matched
before the run:

| File | SHA-256 |
| --- | --- |
| index.html | `66c23f8f973f93245070628eb68df3740ddaeff39562959b89ef64074fc0da3e` |
| styles.css | `ebc155c08745a9934c8ab2a4258942e67862992d6dbf3af6cb2ae9a9652c7067` |
| fixtures.js | `c64acba581a14c65033012e432ccc8c008f07d6ebc1d8cf4798d4b5b535f0fe0` |
| pilot-core.js | `372f256bcd9aa1e04f0bba3368bc2c2e730d9273e830eca279e5bcc77e4f765a` |
| app.js | `12581483ab9ecafd738d945e96322e1787e958c6108e9aa305128e7a97335fec` |

## The checks

**Standalone document integrity.** The page boots with no uncaught errors and
no console errors. The CSP meta tag is byte-identical to the reviewed policy.
Zero scripts appear before the CSP meta tag, there are exactly three
first-party scripts and no inline script. This is the specific condition the
earlier AppDeploy host failed, so it is asserted rather than assumed.

**Containment.** Every network request is compared against the page's own
origin. The page may load its own five assets and nothing else, on either
surface. No third-party request is permitted at any point in the session.

**Evidence gates.** Accept stays disabled on R-001 until every evidence quote
has been located, then unlocks and records the AI score unchanged.

**Unscored criteria stay unscored.** R-004 (blank) and R-006 (off-topic) have
four null criteria; R-005 (insufficient) has exactly one, `conventions` — the
case repaired at this commit. On all three, the score select, Revise and Accept
are disabled for every null criterion, while R-005's three scored criteria stay
operable, so the guard is shown to be targeted rather than a blanket lockout.
The UI is then bypassed: a script drives `setCriterionAction` with every score
0–4 against every null criterion in the fixture set, and all 45 attempts are
denied with no numeric value reaching `finalScore`.

**Decision gates.** Before inspection, all three final decisions are blocked.
After flagging each criterion, REJECT alone unlocks on R-004 and ACCEPT/REVISE
stay blocked. Submitting with no reason is refused and records nothing. A
reasoned REJECT records no numeric scores.

**Invalid evidence.** R-010's bad link is surfaced explicitly; Accept and Revise
are blocked until it is rejected, and rejecting it does not silently re-enable
accepting the AI score.

**Prompt injection.** R-007 shows the warning stating the text was treated as
student writing and not followed, and its mock suggestion is not full credit.

**Exports.** JSON carries exactly the 21-field allowlist, the schema id and both
caveats. CSV is long-form `metric,value` with the identical field set. Neither
export contains a response ID, pseudonym or any response text. A zero-review
export reports unmeasured interaction timing as `null` in JSON and blank — not
`0` — in CSV.

**Reload.** Reloading resets the queue to 0 of 12, every response to NOT
STARTED, and the audit log to a single SESSION_STARTED entry.

**Keyboard and 390px.** Controls are in the tab order and Tab lands on a real
control. At a 390px viewport there is no document-level horizontal overflow and
no visible control is under 28px tall.

## Running it

```bash
node demo/pilot-review/tests/browser-acceptance.mjs            # offline file://
node demo/pilot-review/tests/browser-acceptance.mjs <url>      # a hosted surface
```

It needs Playwright with a Chromium build available; it resolves Playwright
through CJS so an install outside the repo is found without a hardcoded path.
It exits non-zero if any check fails.

The file is deliberately **not** named `*.test.js`. The `pilot-demo` CI job runs
`node --test demo/pilot-review/tests/*.test.js` with no browser available, and
this check must not be swept into that glob.

## What this does not establish

- It says nothing about any **hosted** surface other than the one passed to it.
  Running it against a URL checks that URL at that moment; it does not transfer
  to another host, another deployment or a later version.
- Active exfiltration probing, CSP violation reporting and interception of
  blocked requests were not performed. Containment here is observational: no
  request was made, rather than proof that none could be.
- No screen-reader, Firefox, WebKit or real mobile-hardware pass is claimed. The
  run is Chromium only.
- The demo remains synthetic, memory-only and mock-evaluated. Passing every
  check means the review workflow behaves as reviewed. It is not evidence that
  the workflow helps any teacher.

## Cosmetic observation, not a gate

In a full-page capture the sticky decision bar overlays the card behind it. In
normal scrolled use it sits at the bottom of the viewport as intended. Worth a
look when the layout is next touched; it blocks nothing and no check depends on
it.
