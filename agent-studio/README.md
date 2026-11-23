# AEOS Agent Studio

Agent Studio is where AEOS workflows are specified before they are built, and
where the built versions live as importable, reusable artifacts.

## The rule

Every workflow is written as six fields, and only six fields, before any
implementation exists:

1. **Trigger** — the one event that starts it
2. **Inputs** — the exact fields, types and allowed values
3. **Decisions** — every branch, stated as a rule
4. **Actions** — what the system does, in order
5. **Human approvals** — what a person must decide, and what may never happen without them
6. **Outputs** — the artifacts produced, and the measurements they make possible

If a field cannot be written, the workflow is not understood well enough to build.

## The build order

```
non-AI version  →  it works  →  it is measured  →  only then add AI
```

The non-AI version is `form → n8n → spreadsheet → notification`. It is not a
throwaway prototype. It is the deterministic baseline that a later AI version has
to beat, on numbers that already exist because the baseline produced them.

A workflow that has not cleared its non-AI gate does not get a model.

## Workflows

| Workflow | Status | Gate |
|----------|--------|------|
| [`client-intake`](workflows/client-intake/) | non-AI built, awaiting first live run | acceptance cases in `test/acceptance-cases.md` |

## Layout

```
workflows/<name>/
  SPEC.md                  six fields, nothing else
  RUNBOOK.md               setup, verification, definition of done
  n8n/*.workflow.json      importable, credential-free
  spreadsheet/             the column contract
  test/acceptance-cases.md the gate
```
