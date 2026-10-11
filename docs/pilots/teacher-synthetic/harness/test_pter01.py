"""Behavioral and mutation tests for the P-TER-01 preparation harness.

Each test works on a temporary copy of docs/pilots/teacher-synthetic, so the
committed fixtures and manifest are never modified. The hidden provisional key
is not in the repository; tests build a stand-in key from the frozen drafts.

Run: python3 -m unittest discover -s docs/pilots/teacher-synthetic/harness -v
"""
import contextlib
import csv
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]


class HarnessCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="pter01-"))
        self.root = self.tmp / "repo" / "docs" / "pilots" / "teacher-synthetic"
        shutil.copytree(SOURCE_ROOT, self.root, ignore=shutil.ignore_patterns("runs", "__pycache__", "manifest.json"))
        spec = importlib.util.spec_from_file_location(f"pter01_{id(self)}", self.root / "harness" / "pter01.py")
        self.h = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.h)
        self.key = self.tmp / "private" / "key.json"
        self.write_key()
        self.run_cli("freeze", "--key-file", str(self.key))
        self.runs = self.tmp / "runs"
        self.schedule = self.runs / "schedule.json"
        self.run_cli("schedule", "--run-id", "TEST", "--testers", "T01,T02,T03,T04", "--seed", "7",
                     "--out", str(self.schedule))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write_key(self):
        drafts = json.loads((self.root / "fixtures" / "drafts.fixture-adapter.v0.1.json").read_text())
        entries = [{"response_id": d["response_id"], "criterion_id": d["criterion_id"], "key_value": d["value"],
                    "key_span": d["span"], "seeded_error": None} for d in drafts["drafts"]]
        self.key.parent.mkdir(parents=True, exist_ok=True)
        self.key.write_text(json.dumps({"key_id": "KEY-TEST", "version": "0.0", "status": "TEST-ONLY",
                                        "nonce": "test-nonce-0123456789", "response_set_version": "0.1",
                                        "rubric_ref": "RUB-CER3@0.1", "entries": entries}))

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.h.main(list(argv))
        self.output = out.getvalue()
        return code

    def check(self, *extra):
        return self.run_cli("check", "--key", str(self.key), "--schedule", str(self.schedule), *extra)

    def build_run(self):
        packets = self.runs / "packets"
        for tester in ("T01", "T02", "T03", "T04"):
            for condition in ("manual", "assisted"):
                self.run_cli("packet", "--schedule", str(self.schedule), "--tester", tester,
                             "--condition", condition, "--out", str(packets))
        self.run_cli("blank-tables", "--schedule", str(self.schedule), "--out", str(self.runs / "outcomes"))
        return packets, self.runs / "outcomes"

    def edit_json(self, rel, change):
        path = self.root / rel
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data, indent=2) + "\n")

    def edit_rows(self, path, change):
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            columns, rows = reader.fieldnames, list(reader)
        change(rows)
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def assert_fails(self, code, fragment):
        self.assertEqual(code, 1, self.output)
        self.assertIn(fragment, self.output)


class PreparationTests(HarnessCase):
    def test_complete_blank_run_passes_but_run_readiness_is_blocked(self):
        packets, outcomes = self.build_run()
        self.assertEqual(self.check("--packets", str(packets), "--outcomes", str(outcomes)), 0, self.output)
        self.assertIn("Preparation integrity: PASS", self.output)
        self.assertIn("BLOCKED protocol: SOURCE_NOT_LOCATED", self.output)
        self.assertIn("missing=20/20", self.output)
        self.assertEqual(self.check("--require-run-ready"), 2)

    def test_schedule_is_deterministic_and_counterbalanced(self):
        first = json.loads(self.schedule.read_text())
        self.run_cli("schedule", "--run-id", "TEST", "--testers", "T01,T02,T03,T04", "--seed", "7",
                     "--out", str(self.runs / "again.json"))
        self.assertEqual(first, json.loads((self.runs / "again.json").read_text()))
        arms = sorted(a["arm"] for a in first["assignments"])
        self.assertEqual(arms, [0, 1, 2, 3])
        firsts = [a["blocks"][0]["condition"] for a in first["assignments"]]
        self.assertEqual(sorted(firsts), ["assisted", "assisted", "manual", "manual"])

    def test_conditions_have_separate_table_structures(self):
        _, outcomes = self.build_run()
        manual = (outcomes / "manual" / "criteria.csv").read_text().splitlines()[0]
        self.assertNotIn("decision", manual)
        self.assertNotIn("original_value", manual)
        shutil.copy(outcomes / "assisted" / "criteria.csv", outcomes / "manual" / "criteria.csv")
        self.assert_fails(self.check("--outcomes", str(outcomes)), "columns do not match the manual template")

    def test_harness_has_no_network_or_provider_imports(self):
        source = (self.root / "harness" / "pter01.py").read_text()
        for module in ("socket", "urllib", "http.client", "requests", "anthropic", "openai"):
            self.assertNotIn(f"import {module}", source)


class VersionLinkageMutations(HarnessCase):
    def test_fixture_changed_after_freeze(self):
        self.edit_json("fixtures/responses.v0.1.json", lambda d: d["items"][0].update(text=d["items"][0]["text"] + " "))
        self.assert_fails(self.check(), "changed after freeze")

    def test_draft_linked_to_wrong_rubric_version(self):
        self.edit_json("fixtures/drafts.fixture-adapter.v0.1.json", lambda d: d.update(rubric_ref="RUB-CER3@9.9"))
        self.run_cli("freeze")
        self.assert_fails(self.run_cli("check"), "drafts.rubric_ref")

    def test_schedule_from_another_manifest(self):
        self.edit_json("fixtures/rubric.RUB-CER3.v0.1.json", lambda d: d.update(provenance="changed"))
        self.run_cli("freeze")
        self.assert_fails(self.check(), "schedule was built from a different manifest")

    def test_task_row_with_wrong_rubric_version(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "assisted" / "tasks.csv", lambda rows: rows[0].update(rubric_ref="RUB-CER3@0.0"))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "rubric_ref='RUB-CER3@0.0'")

    def test_original_value_not_matching_frozen_draft(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "assisted" / "criteria.csv", lambda rows: rows[0].update(original_value="IE"))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "does not match frozen draft")


class EvidenceMutations(HarnessCase):
    def test_shifted_draft_span(self):
        def shift(data):
            draft = next(d for d in data["drafts"] if d["span"])
            draft["span"]["start"] += 1
        self.edit_json("fixtures/drafts.fixture-adapter.v0.1.json", shift)
        self.run_cli("freeze")
        self.assert_fails(self.run_cli("check"), "invalid evidence span")

    def test_scored_draft_without_span(self):
        def drop(data):
            next(d for d in data["drafts"] if d["value"] == "2")["span"] = None
        self.edit_json("fixtures/drafts.fixture-adapter.v0.1.json", drop)
        self.run_cli("freeze")
        self.assert_fails(self.run_cli("check"), "without an evidence span")

    def test_teacher_span_out_of_bounds(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "manual" / "criteria.csv", lambda rows: rows[0].update(
            final_value="2", final_span_start="0", final_span_end="9999", final_span_quote="x"))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "invalid evidence span")

    def test_teacher_partial_span(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "manual" / "criteria.csv", lambda rows: rows[0].update(final_span_start="0"))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "partial evidence span")


class DecisionMutations(HarnessCase):
    def assisted_row(self, outcomes, change):
        def apply(rows):
            row = next(r for r in rows if r["original_span_start"] != "not_applicable")
            change(row)
        self.edit_rows(outcomes / "assisted" / "criteria.csv", apply)

    def test_valid_accept_and_reject_rows_pass(self):
        _, outcomes = self.build_run()
        self.assisted_row(outcomes, lambda r: r.update(decision="accept", final_value=r["original_value"]))
        self.edit_rows(outcomes / "assisted" / "criteria.csv", lambda rows: rows[-1].update(decision="reject", final_value="IE"))
        self.assertEqual(self.check("--outcomes", str(outcomes)), 0, self.output)
        self.assertIn("accept=1/60", self.output)
        self.assertIn("reject=1/60", self.output)

    def test_accept_with_changed_value(self):
        _, outcomes = self.build_run()
        self.assisted_row(outcomes, lambda r: r.update(decision="accept", final_value="IE"))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "accept recorded but final differs")

    def test_revise_without_change(self):
        _, outcomes = self.build_run()
        self.assisted_row(outcomes, lambda r: r.update(decision="revise", final_value=r["original_value"]))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "revise recorded but final equals")

    def test_unknown_decision(self):
        _, outcomes = self.build_run()
        self.assisted_row(outcomes, lambda r: r.update(decision="approve"))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "not accept/revise/reject")


class DenominatorAndMissingMutations(HarnessCase):
    def test_deleted_task_row(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "manual" / "tasks.csv", lambda rows: rows.pop())
        self.assert_fails(self.check("--outcomes", str(outcomes)), "has no row")

    def test_unscheduled_task_row(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "manual" / "tasks.csv", lambda rows: rows.append({**rows[0], "task_id": "T09-M01"}))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "does not match the schedule")

    def test_negative_and_non_numeric_times(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "manual" / "tasks.csv", lambda rows: rows[0].update(active_review_s="-3"))
        self.edit_rows(outcomes / "manual" / "sessions.csv", lambda rows: rows[0].update(setup_time_s="soon"))
        code = self.check("--outcomes", str(outcomes))
        self.assert_fails(code, "finite non-negative")
        self.assertIn("not a number", self.output)

    def test_outcomes_on_not_started_task(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "manual" / "tasks.csv", lambda rows: rows[0].update(task_status="not_started"))
        self.edit_rows(outcomes / "manual" / "criteria.csv", lambda rows: rows[0].update(final_value="1"))
        self.assert_fails(self.check("--outcomes", str(outcomes)), "marked not_started")

    def test_missing_outcomes_stay_missing(self):
        _, outcomes = self.build_run()
        self.edit_rows(outcomes / "manual" / "tasks.csv", lambda rows: rows[0].update(task_status="abandoned"))
        self.assertEqual(self.check("--outcomes", str(outcomes)), 0, self.output)
        self.assertIn("abandoned=1/20", self.output)
        self.assertIn("missing=19/20", self.output)
        self.assertIn("final_value recorded 0/60", self.output)


class HiddenKeyMutations(HarnessCase):
    def test_key_inside_repository_is_refused(self):
        inside = self.root / "key.json"
        shutil.copy(self.key, inside)
        self.assertEqual(self.run_cli("freeze", "--key-file", str(inside)), 1)
        self.assertIn("inside the public repository", self.output)

    def test_tampered_key(self):
        data = json.loads(self.key.read_text())
        data["entries"][0]["key_value"] = "0"
        self.key.write_text(json.dumps(data))
        self.assert_fails(self.check(), "does not match the frozen key hash")

    def test_packet_leaking_key_content(self):
        packets, _ = self.build_run()
        path = packets / "T01-manual.packet.json"
        data = json.loads(path.read_text())
        data["tasks"][0]["key_value"] = "2"
        path.write_text(json.dumps(data))
        self.assert_fails(self.check("--packets", str(packets)), "contains key-only content")

    def test_manual_packet_with_drafts(self):
        packets, _ = self.build_run()
        assisted = json.loads((packets / "T01-assisted.packet.json").read_text())
        assisted["condition"] = "manual"
        (packets / "T01-manual.packet.json").write_text(json.dumps(assisted))
        self.assert_fails(self.check("--packets", str(packets)), "manual packet but contains drafts")

    def test_packets_never_contain_key_values(self):
        packets, _ = self.build_run()
        for path in packets.glob("*.json"):
            self.assertNotIn("test-nonce-0123456789", path.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
