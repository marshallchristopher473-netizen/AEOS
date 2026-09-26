# Lead Qualification + Enrollment Agent v1

Reads one inbound parent inquiry to a tutoring business and returns a structured
decision: **intent, qualification, priority, missing information, recommended
next action**, plus a response draft for a human to review.

**The agent never contacts anyone.** It reads a message and returns a record.

Standard library only. No dependencies, no API keys, no network, no cost.

---

## Quick start

```bash
# Score the agent against all 100 benchmark cases
python3 -m agents.lead_qualification.benchmark.run_benchmark

# ...with every failure printed
python3 -m agents.lead_qualification.benchmark.run_benchmark --failures

# One case, in Test / Expected / Agent / Result form
python3 -m agents.lead_qualification.benchmark.run_benchmark --case LQ-052

# 52 regression and invariant tests
python3 -m unittest discover -s agents/lead_qualification/tests -t .
```

Run from the repository root. The benchmark runner exits non-zero if any
development-split gate fails, so it can be used as a CI regression gate as is.

## Using it on one inquiry

```python
from agents.lead_qualification import analyze, Inquiry

decision = analyze(Inquiry(
    id="INQ-1",
    channel="web_form",
    received_at="2026-09-17T18:22:00",
    message="My son has his Algebra 1 final on Friday and he's at a 58. "
            "He's in 9th grade. Can anyone work with him before then?",
    sender_name="Dana Whitfield",
    sender_email="dana@example.com",
    sender_phone="555-0142",
))

decision.intent               # 'tutoring_inquiry'
decision.qualification        # 'qualified'
decision.priority             # 'urgent'
decision.missing_information  # ['availability']
decision.next_action          # 'escalate_to_human_now'
decision.rules_fired          # ['INT-09', 'QUAL-06', 'PRI-03', 'ACT-01']
decision.response_draft       # draft reply, for a human to review and send
```

`analyze_dict(raw)` takes and returns plain JSON for callers that prefer it.

---

## Current result

**98% of 100 benchmark cases correct across all five decision fields. Zero
catastrophic routing errors.** 95% on the 20 held-out cases no rule was tuned
against.

Full scorecard, method and limitations: [`docs/LEAD_AGENT_BENCHMARK_REPORT.md`](../../docs/LEAD_AGENT_BENCHMARK_REPORT.md).

---

## Files

| Path | Purpose |
| --- | --- |
| `schema.py` | The five scored vocabularies, `Inquiry`, `LeadDecision` |
| `profile.py` | The tutoring business the rules encode — grades, subjects, exclusions |
| `extract.py` | Field detection: grade, subject, contact, availability, timeline, goal, deadlines |
| `agent.py` | The rule engine. Every branch appends a rule ID to `rules_fired` |
| `responses.py` | Response-draft templates (not scored) |
| `benchmark/dataset.json` | 100 synthetic inquiries |
| `benchmark/answer_key.json` | Ground truth, one rationale per case |
| `benchmark/run_benchmark.py` | Scorer, report generator, CI gate |
| `tests/test_regressions.py` | One test class per entry in the failure log |
| `tests/test_invariants.py` | Safety properties and benchmark integrity |

## Documents

| Document | What it is |
| --- | --- |
| [Specification](../../docs/LEAD_QUALIFICATION_AGENT_V1_SPEC.md) | Frozen scope, the decision rubric, the validation gate |
| [Benchmark report](../../docs/LEAD_AGENT_BENCHMARK_REPORT.md) | Results, method, limitations |
| [Failure log](../../docs/LEAD_AGENT_FAILURE_LOG.md) | Every failure → root cause → rule change → test |
| [Pilot offer](../../docs/TUTORING_PILOT_OFFER.md) | The free shadow-mode audit used to reach Milestone C |

---

## Design notes

**Why rules and not an LLM.** Determinism is what makes a benchmark number
mean anything, and a zero-cost run is what lets the benchmark gate every
commit. Every decision is also traceable to a rule ID, so a failure can be
repaired rather than re-prompted. An LLM belongs in v2 for response phrasing
and as a fallback on low-confidence intents — behind this same benchmark.

**Why a dev/holdout split.** Cases LQ-001–080 are tuned against; LQ-081–100
are not. The gap between the two is the overfitting measurement. Correcting a
holdout answer after seeing engine output would destroy it — which is why one
known key inconsistency (LQ-092) is left standing and scored as a failure.
See failure log entry K-02.

**Privacy.** All 100 cases are synthetic. No real parent, student or family
data belongs in this repository. Phone numbers use the reserved 555-01xx range.

---

## Scope

Not in v1, on purpose: CRM, payments, SMS or email sending, calendar
integration, autonomous outbound contact, multi-turn conversation, follow-up
sequencing (Agent #2), no-show and dormant-lead recovery (Agent #3), and
multi-industry generalization. Each is gated on the milestone that would
justify it — see spec §9.

Longer term this engine is the prototype for an AEOS **Enrollment / Family
Intake** module. It stays a standalone commercial product until it has paying
customers, so that AEOS's current technical scope is not expanded on an
unvalidated assumption.
