"""Score the agent against the 100-case benchmark and emit the report.

    python3 -m agents.lead_qualification.benchmark.run_benchmark            # summary
    python3 -m agents.lead_qualification.benchmark.run_benchmark --failures # + failures
    python3 -m agents.lead_qualification.benchmark.run_benchmark --markdown REPORT.md

Standard library only, so it runs from a clean checkout and can serve as a
regression gate in CI. Exit code is 0 when every gate in spec section 7 passes
on the development split, 1 otherwise.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from .. import analyze
from ..schema import Inquiry, Priority, Qualification

BENCHMARK_DIR = Path(__file__).resolve().parent
DATASET_PATH = BENCHMARK_DIR / "dataset.json"
ANSWER_KEY_PATH = BENCHMARK_DIR / "answer_key.json"

SCORED_FIELDS = ("intent", "qualification", "priority",
                 "missing_information", "next_action")

FIELD_LABELS = {
    "intent": "Intent classification",
    "qualification": "Qualification",
    "priority": "Priority",
    "missing_information": "Missing-information detection",
    "next_action": "Recommended-action",
}

# Spec section 7.
GATES = {
    "intent": 0.90,
    "qualification": 0.90,
    "priority": 0.90,
    "missing_information": 0.85,
    "next_action": 0.90,
}

MISSING_INFO_FIELDS = ("grade_level", "subject", "contact_info",
                       "availability", "start_timeline", "learning_goal")


def load_benchmark():
    dataset = json.loads(DATASET_PATH.read_text())
    key = json.loads(ANSWER_KEY_PATH.read_text())
    answers = {a["id"]: a for a in key["answers"]}

    cases = dataset["cases"]
    missing_answers = [c["id"] for c in cases if c["id"] not in answers]
    if missing_answers:
        raise SystemExit(f"No answer key entry for: {', '.join(missing_answers)}")
    orphan_answers = [i for i in answers if i not in {c["id"] for c in cases}]
    if orphan_answers:
        raise SystemExit(f"Answer key entry with no case: {', '.join(orphan_answers)}")
    return dataset, cases, answers


def is_catastrophic(expected: dict, actual: dict) -> bool:
    """Spec section 6.3: the two routing errors that must never happen."""
    if expected["priority"] == Priority.URGENT and actual["priority"] == Priority.LOW:
        return True
    if expected["qualification"] == Qualification.NOT_A_LEAD and \
            actual["priority"] == Priority.URGENT:
        return True
    return False


def run() -> dict:
    dataset, cases, answers = load_benchmark()

    results = []
    for case in cases:
        decision = analyze(Inquiry.from_dict(case))
        expected = answers[case["id"]]
        actual = decision.scored_fields()

        comparisons = {}
        for scored_field in SCORED_FIELDS:
            want, got = expected[scored_field], actual[scored_field]
            if scored_field == "missing_information":
                comparisons[scored_field] = sorted(want) == sorted(got)
            else:
                comparisons[scored_field] = want == got

        results.append({
            "id": case["id"],
            "category": case["category"],
            "split": case["split"],
            "message": case["message"],
            "expected": expected,
            "actual": actual,
            "comparisons": comparisons,
            "catastrophic": is_catastrophic(expected, actual),
            "rules_fired": decision.rules_fired,
        })

    return {"dataset": dataset, "results": results}


def accuracy_by_split(results: List[dict]) -> Dict[str, Dict[str, float]]:
    table: Dict[str, Dict[str, float]] = {}
    for split in ("development", "holdout", "all"):
        subset = [r for r in results if split == "all" or r["split"] == split]
        if not subset:
            continue
        table[split] = {
            scored_field: sum(r["comparisons"][scored_field] for r in subset) / len(subset)
            for scored_field in SCORED_FIELDS
        }
        table[split]["_n"] = len(subset)
        table[split]["_all_five"] = sum(
            all(r["comparisons"].values()) for r in subset) / len(subset)
        table[split]["_catastrophic"] = sum(r["catastrophic"] for r in subset)
    return table


def per_field_missing_info(results: List[dict]) -> Dict[str, Dict[str, float]]:
    """Precision and recall for each of the six detected fields.

    A field is a 'positive' when the agent reports it missing.
    """
    stats = {}
    for name in MISSING_INFO_FIELDS:
        tp = fp = fn = 0
        for r in results:
            # Cases where the whole list is suppressed carry no signal here.
            if not r["expected"]["missing_information"] and \
                    not r["actual"]["missing_information"]:
                continue
            want = name in r["expected"]["missing_information"]
            got = name in r["actual"]["missing_information"]
            if want and got:
                tp += 1
            elif got and not want:
                fp += 1
            elif want and not got:
                fn += 1
        precision = tp / (tp + fp) if (tp + fp) else 1.0
        recall = tp / (tp + fn) if (tp + fn) else 1.0
        stats[name] = {"precision": precision, "recall": recall,
                       "tp": tp, "fp": fp, "fn": fn}
    return stats


def confusion(results: List[dict], scored_field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for r in results:
        if r["comparisons"][scored_field]:
            continue
        want, got = r["expected"][scored_field], r["actual"][scored_field]
        if scored_field == "missing_information":
            want, got = ",".join(sorted(want)) or "-", ",".join(sorted(got)) or "-"
        counts[f"{want} -> {got}"] = counts.get(f"{want} -> {got}", 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def gates_pass(table: Dict[str, Dict[str, float]], split: str = "development") -> bool:
    scores = table[split]
    if scores["_catastrophic"]:
        return False
    return all(scores[f] >= threshold for f, threshold in GATES.items())


def _pct(value: float) -> str:
    return f"{value * 100:.0f}%"


def print_summary(payload: dict, show_failures: bool) -> None:
    results = payload["results"]
    table = accuracy_by_split(results)

    print(f"\nLead Qualification Agent v1 — benchmark ({len(results)} cases)\n")
    header = f"{'Metric':<32}{'Dev':>8}{'Holdout':>10}{'All':>8}{'Gate':>8}"
    print(header)
    print("-" * len(header))
    for scored_field in SCORED_FIELDS:
        print(f"{FIELD_LABELS[scored_field]:<32}"
              f"{_pct(table['development'][scored_field]):>8}"
              f"{_pct(table['holdout'][scored_field]):>10}"
              f"{_pct(table['all'][scored_field]):>8}"
              f"{_pct(GATES[scored_field]):>8}")
    print("-" * len(header))
    print(f"{'All five fields correct':<32}"
          f"{_pct(table['development']['_all_five']):>8}"
          f"{_pct(table['holdout']['_all_five']):>10}"
          f"{_pct(table['all']['_all_five']):>8}"
          f"{'-':>8}")
    print(f"{'Catastrophic routing errors':<32}"
          f"{int(table['development']['_catastrophic']):>8}"
          f"{int(table['holdout']['_catastrophic']):>10}"
          f"{int(table['all']['_catastrophic']):>8}"
          f"{0:>8}")

    print("\nDevelopment-split gates: "
          f"{'PASS' if gates_pass(table, 'development') else 'FAIL'}")

    if show_failures:
        print("\nFailures:\n")
        for r in results:
            wrong = [f for f in SCORED_FIELDS if not r["comparisons"][f]]
            if not wrong:
                continue
            flag = "  [CATASTROPHIC]" if r["catastrophic"] else ""
            print(f"{r['id']} ({r['category']}, {r['split']}){flag}")
            for scored_field in wrong:
                print(f"    {scored_field}: expected {r['expected'][scored_field]!r} "
                      f"got {r['actual'][scored_field]!r}")
            print(f"    rules: {', '.join(r['rules_fired'])}")
            print()


def markdown_table(payload: dict) -> str:
    results = payload["results"]
    table = accuracy_by_split(results)
    lines = []

    lines.append("| Metric | Development (80) | Holdout (20) | All (100) | Gate | Result |")
    lines.append("| --- | ---: | ---: | ---: | ---: | :---: |")
    for scored_field in SCORED_FIELDS:
        passed = table["development"][scored_field] >= GATES[scored_field]
        lines.append(
            f"| {FIELD_LABELS[scored_field]} | {_pct(table['development'][scored_field])} "
            f"| {_pct(table['holdout'][scored_field])} | {_pct(table['all'][scored_field])} "
            f"| {_pct(GATES[scored_field])} | {'PASS' if passed else 'FAIL'} |")
    cata = int(table["development"]["_catastrophic"])
    lines.append(
        f"| Catastrophic routing errors | {cata} "
        f"| {int(table['holdout']['_catastrophic'])} "
        f"| {int(table['all']['_catastrophic'])} | 0 | "
        f"{'PASS' if cata == 0 else 'FAIL'} |")
    lines.append(
        f"| All five fields correct | {_pct(table['development']['_all_five'])} "
        f"| {_pct(table['holdout']['_all_five'])} "
        f"| {_pct(table['all']['_all_five'])} | — | — |")
    return "\n".join(lines)


def case_table(payload: dict, case_id: str) -> str:
    """The per-case table from the brief: Test | Expected | Agent | Result."""
    result = next(r for r in payload["results"] if r["id"] == case_id)
    rows = ["| Test | Expected | Agent | Result |", "| --- | --- | --- | :---: |"]
    for scored_field in SCORED_FIELDS:
        want, got = result["expected"][scored_field], result["actual"][scored_field]
        if scored_field == "missing_information":
            want = ", ".join(want) or "none"
            got = ", ".join(got) or "none"
        rows.append(f"| {FIELD_LABELS[scored_field]} | {want} | {got} | "
                    f"{'PASS' if result['comparisons'][scored_field] else 'FAIL'} |")
    return "\n".join(rows)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--failures", action="store_true",
                        help="print every failing case with expected vs actual")
    parser.add_argument("--markdown", metavar="PATH",
                        help="write the scoring tables to a markdown file")
    parser.add_argument("--json", metavar="PATH",
                        help="write full per-case results as JSON")
    parser.add_argument("--case", metavar="ID",
                        help="print the per-case table for one case id")
    args = parser.parse_args(argv)

    payload = run()

    if args.case:
        print(case_table(payload, args.case))
        return 0

    print_summary(payload, show_failures=args.failures)

    if args.markdown:
        Path(args.markdown).write_text(markdown_table(payload) + "\n")
        print(f"\nWrote {args.markdown}")

    if args.json:
        Path(args.json).write_text(json.dumps(payload["results"], indent=2) + "\n")
        print(f"Wrote {args.json}")

    table = accuracy_by_split(payload["results"])
    return 0 if gates_pass(table, "development") else 1


if __name__ == "__main__":
    sys.exit(main())
