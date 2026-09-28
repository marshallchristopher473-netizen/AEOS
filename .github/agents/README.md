# Agents

Agent definitions for this repository. Each file is a bounded, user-invocable agent with an explicit decision contract. No agent is permitted to report success on evidence it did not produce or reproduce.

## AEOS platform agents

| Agent | File | Role |
|---|---|---|
| AEOS P0 Security Completion | `aeos-p0-security-completion.agent.md` | Implements the authentication, tenant-isolation and RLS gate. Highest allowed conclusion is `P0 CANDIDATE READY FOR INDEPENDENT REVIEW`. |
| AEOS P0 Independent Verifier | `aeos-p0-independent-verifier.agent.md` | Independently reproduces and attacks the candidate. Owns the `P0 VERIFIED` / `P0 REJECTED` / `P0 BLOCKED` decision. |

Separation of duties is deliberate: the agent that builds the security gate may not be the agent that certifies it.

## Executive Presentation Strategy agents

The Executive Presentation Strategy practice sells and delivers $5K–$15K decision decks. These agents encode its sales motion and its five-stage delivery method so that engagements are repeatable rather than re-improvised.

### Sales motion

| Agent | File | Role |
|---|---|---|
| EPS Prospect Audit | `eps-prospect-audit.agent.md` | Builds the three-slide outbound audit from public evidence only. Earns a diagnostic call, not a redesign. |
| EPS Discovery and Qualification | `eps-discovery-qualification.agent.md` | Runs the seven discovery questions, tests Stake / Authority / Material / Timing, produces the diagnosis the prospect must confirm. |
| EPS Scoping and Proposal | `eps-scoping-proposal.agent.md` | Prices the six complexity drivers, anchors three levels, recommends one, reduces scope before discounting. |

### Delivery — the five-stage method

| Stage | Agent | File |
|---|---|---|
| 01 Diagnose, 02 Architect | EPS Narrative Architect | `eps-narrative-architect.agent.md` |
| 03 Prove | EPS Evidence Integrity | `eps-evidence-integrity.agent.md` |
| 04 Design | EPS Deck Builder | `eps-deck-builder.agent.md` |
| 05 Rehearse | EPS Rehearsal | `eps-rehearsal.agent.md` |

## Gate sequence

The delivery agents are gated. Each refuses to run until the prior gate clears.

```
Narrative Architect  ──▶ NARRATIVE MAP READY
        │
        ▼
Evidence Integrity   ──▶ EVIDENCE CLEARED ──┐ (REJECTED / BLOCKED stops here)
        │                                   │
        ▼                                   │
Deck Builder         ──▶ DECK READY FOR REHEARSAL
        │
        ▼
Rehearsal            ──▶ DELIVERY READY
```

Two properties are load-bearing:

1. **Evidence Integrity is read-only and cannot repair the narrative.** It classifies every claim as hypothesis, prototype, internal test, pilot result, validated evidence, illustrative, or marketing claim, and hands failures back as a bounded remediation list. It mirrors the P0 verifier pattern above — the agent that certifies a claim is not the agent that wrote it.

2. **No agent may upgrade a claim's class to meet a deadline.** An internal test presented in the language of validated evidence is the failure mode these agents exist to prevent, because the presenter is the one who has to defend it in the room.

## Conventions

- Filename: `<slug>.agent.md`.
- Frontmatter: `name`, `description`, `tools`, `disable-model-invocation`, `user-invocable`.
- Every agent defines a closed decision contract. Hedged outcomes such as "mostly verified" or "cleared with exceptions" are prohibited by design.
- Every agent ends by specifying a required report and an exact next action.
