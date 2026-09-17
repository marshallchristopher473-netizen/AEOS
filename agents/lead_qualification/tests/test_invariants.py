"""Safety invariants and benchmark integrity.

These are the properties that must hold for every case, forever — the ones that
would make the agent unsafe to put in front of a real tutoring business if they
ever broke.

    python3 -m unittest discover -s agents/lead_qualification/tests -t .
"""

import json
import unittest
from pathlib import Path

from agents.lead_qualification import analyze
from agents.lead_qualification.benchmark.run_benchmark import (
    ANSWER_KEY_PATH, DATASET_PATH, GATES, SCORED_FIELDS,
    accuracy_by_split, gates_pass, run)
from agents.lead_qualification.schema import (
    Action, Field, Inquiry, Intent, Priority, Qualification)


class TestBenchmarkIntegrity(unittest.TestCase):
    def setUp(self):
        self.dataset = json.loads(DATASET_PATH.read_text())
        self.key = json.loads(ANSWER_KEY_PATH.read_text())

    def test_one_hundred_cases(self):
        self.assertEqual(len(self.dataset["cases"]), 100)

    def test_every_case_has_exactly_one_answer(self):
        case_ids = [c["id"] for c in self.dataset["cases"]]
        answer_ids = [a["id"] for a in self.key["answers"]]
        self.assertEqual(sorted(case_ids), sorted(answer_ids))
        self.assertEqual(len(set(answer_ids)), len(answer_ids))

    def test_split_sizes(self):
        splits = [c["split"] for c in self.dataset["cases"]]
        self.assertEqual(splits.count("development"), 80)
        self.assertEqual(splits.count("holdout"), 20)

    def test_answers_use_declared_vocabularies(self):
        for answer in self.key["answers"]:
            self.assertIn(answer["intent"], Intent.ALL, answer["id"])
            self.assertIn(answer["qualification"], Qualification.ALL, answer["id"])
            self.assertIn(answer["priority"], Priority.ALL, answer["id"])
            self.assertIn(answer["next_action"], Action.ALL, answer["id"])
            for name in answer["missing_information"]:
                self.assertIn(name, Field.ALL, answer["id"])

    def test_every_answer_carries_a_rationale(self):
        for answer in self.key["answers"]:
            self.assertTrue(answer.get("rationale", "").strip(), answer["id"])

    def test_dataset_is_declared_synthetic(self):
        self.assertTrue(self.dataset["synthetic"])


class TestSafetyInvariants(unittest.TestCase):
    """Run over all 100 cases."""

    @classmethod
    def setUpClass(cls):
        cls.payload = run()
        cls.results = cls.payload["results"]

    def test_no_case_is_both_not_a_lead_and_urgent(self):
        """Spam must never page a human, whatever urgency words it contains."""
        for r in self.results:
            if r["actual"]["qualification"] == Qualification.NOT_A_LEAD:
                self.assertNotEqual(r["actual"]["priority"], Priority.URGENT, r["id"])

    def test_every_urgent_case_escalates(self):
        for r in self.results:
            if r["actual"]["priority"] == Priority.URGENT:
                self.assertEqual(r["actual"]["next_action"],
                                 Action.ESCALATE_TO_HUMAN_NOW, r["id"])

    def test_no_true_urgent_case_is_ranked_low(self):
        for r in self.results:
            if r["expected"]["priority"] == Priority.URGENT:
                self.assertNotEqual(r["actual"]["priority"], Priority.LOW, r["id"])

    def test_zero_catastrophic_routing_errors(self):
        offenders = [r["id"] for r in self.results if r["catastrophic"]]
        self.assertEqual(offenders, [])

    def test_missing_information_is_suppressed_where_irrelevant(self):
        for r in self.results:
            actual = r["actual"]
            suppressed = (
                actual["qualification"] in (Qualification.NOT_A_LEAD,
                                            Qualification.OUT_OF_SCOPE)
                or actual["intent"] == Intent.EXISTING_CUSTOMER
            )
            if suppressed:
                self.assertEqual(actual["missing_information"], [], r["id"])

    def test_qualified_leads_have_no_blocking_gaps(self):
        for r in self.results:
            actual = r["actual"]
            if actual["qualification"] != Qualification.QUALIFIED:
                continue
            if actual["intent"] in (Intent.EXISTING_CUSTOMER,
                                    Intent.SCHEDULING_REQUEST):
                continue  # qualified by relationship, not by field completeness
            for name in Field.BLOCKING:
                self.assertNotIn(name, actual["missing_information"], r["id"])

    def test_outputs_use_declared_vocabularies(self):
        for r in self.results:
            actual = r["actual"]
            self.assertIn(actual["intent"], Intent.ALL, r["id"])
            self.assertIn(actual["qualification"], Qualification.ALL, r["id"])
            self.assertIn(actual["priority"], Priority.ALL, r["id"])
            self.assertIn(actual["next_action"], Action.ALL, r["id"])

    def test_missing_information_is_ordered_and_unique(self):
        for r in self.results:
            names = r["actual"]["missing_information"]
            self.assertEqual(len(set(names)), len(names), r["id"])
            self.assertEqual(names, [f for f in Field.ALL if f in names], r["id"])

    def test_every_decision_carries_an_audit_trail(self):
        for r in self.results:
            self.assertTrue(r["rules_fired"], r["id"])

    def test_agent_is_deterministic(self):
        case = self.payload["dataset"]["cases"][0]
        first = analyze(Inquiry.from_dict(case)).to_dict()
        second = analyze(Inquiry.from_dict(case)).to_dict()
        self.assertEqual(first, second)

    def test_every_decision_has_a_response_draft(self):
        for case in self.payload["dataset"]["cases"]:
            decision = analyze(Inquiry.from_dict(case))
            self.assertTrue(decision.response_draft.strip(), case["id"])


class TestValidationGate(unittest.TestCase):
    """The spec section 7 gate, enforced as a test so a regression fails CI."""

    @classmethod
    def setUpClass(cls):
        cls.table = accuracy_by_split(run()["results"])

    def test_development_split_clears_every_gate(self):
        for scored_field, threshold in GATES.items():
            self.assertGreaterEqual(
                self.table["development"][scored_field], threshold,
                f"{scored_field} below gate on the development split")

    def test_no_catastrophic_errors_anywhere(self):
        self.assertEqual(int(self.table["all"]["_catastrophic"]), 0)

    def test_gate_helper_agrees(self):
        self.assertTrue(gates_pass(self.table, "development"))

    def test_holdout_does_not_collapse(self):
        """Overfitting check: the holdout must stay within 15 points of dev."""
        for scored_field in SCORED_FIELDS:
            gap = self.table["development"][scored_field] - \
                self.table["holdout"][scored_field]
            self.assertLess(gap, 0.15, f"{scored_field} dev/holdout gap too wide")


class TestInputValidation(unittest.TestCase):
    def test_unknown_channel_is_rejected(self):
        with self.assertRaises(ValueError):
            Inquiry.from_dict({"id": "X", "channel": "carrier_pigeon",
                               "received_at": "2026-09-17T12:00:00",
                               "message": "hello"})

    def test_missing_required_field_is_rejected(self):
        with self.assertRaises(ValueError):
            Inquiry.from_dict({"id": "X", "channel": "email",
                               "received_at": "2026-09-17T12:00:00"})

    def test_empty_message_is_rejected(self):
        with self.assertRaises(ValueError):
            Inquiry.from_dict({"id": "X", "channel": "email",
                               "received_at": "2026-09-17T12:00:00",
                               "message": ""})


if __name__ == "__main__":
    unittest.main()
