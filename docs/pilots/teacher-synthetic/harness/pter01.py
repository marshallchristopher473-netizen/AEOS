"""P-TER-01 offline synthetic teacher ELA review: preparation harness.

Standard library only. No network, model provider, database, or school record
is used. Every command is deterministic for the same inputs, so any step can be
replayed from the committed fixtures plus the recorded seed.

Commands
  freeze        Hash the frozen fixtures and (optionally) bind protocol, codebook and key by hash.
  schedule      Build a seeded counterbalanced order (PROPOSED; protocol requirement unverified).
  packet        Write one tester-facing packet for one condition. Keys are never included.
  blank-tables  Write blank outcome tables, separately per condition, one row per scheduled task.
  check         Integrity check: version linkage, evidence spans, keys, packets, outcome tables.

Blank cells are missing outcomes. They are never imputed or coerced to zero.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

HARNESS_VERSION = "0.1"
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
MANIFEST = ROOT / "manifest.json"
FIXTURE_FILES = {
    "passage": "fixtures/passage.PSG-COOLROOF.v0.1.json",
    "rubric": "fixtures/rubric.RUB-CER3.v0.1.json",
    "responses": "fixtures/responses.v0.1.json",
    "drafts": "fixtures/drafts.fixture-adapter.v0.1.json",
    "harness": "harness/pter01.py",
}
CONDITIONS = ("manual", "assisted")
NOT_APPLICABLE = "not_applicable"
STATUS_VALUES = {"completed", "abandoned", "failed", "not_started"}
DECISIONS = {"accept", "revise", "reject"}
RATER_VALUES = {"yes", "no", "partial"}
# Fields that exist only in the hidden key. Their presence in a packet or table is a leak.
KEY_ONLY_TOKENS = ("key_value", "key_span", "seeded_error", "nonce", "profiles")

SESSION_COLUMNS = ["run_id", "manifest_sha256", "tester_id", "condition", "block_position", "response_set",
                   "setup_time_s", "session_status", "observer_id", "notes"]
TASK_COLUMNS = ["run_id", "manifest_sha256", "tester_id", "condition", "task_id", "sequence_position",
                "response_id", "response_set_version", "rubric_ref", "passage_ref", "adapter_ref",
                "task_status", "active_review_s", "pause_repair_s", "abandoned_stage", "failure_code",
                "failure_note"]
MANUAL_CRITERIA_COLUMNS = ["run_id", "tester_id", "condition", "task_id", "response_id", "criterion_id",
                           "final_value", "final_span_start", "final_span_end", "final_span_quote",
                           "rater_span_supports", "note"]
ASSISTED_CRITERIA_COLUMNS = ["run_id", "tester_id", "condition", "task_id", "response_id", "criterion_id",
                             "draft_id", "original_value", "original_span_start", "original_span_end",
                             "decision", "final_value", "final_span_start", "final_span_end",
                             "final_span_quote", "rater_span_supports", "note"]
CRITERIA_COLUMNS = {"manual": MANUAL_CRITERIA_COLUMNS, "assisted": ASSISTED_CRITERIA_COLUMNS}

DEFAULT_OPEN_ITEMS = [
    ("protocol-source", "Locate the authoritative P-TER-01 v0.2 packet and bind it by hash (freeze --protocol-file)."),
    ("codebook-source", "Locate the current Assessment Construct Codebook and bind it by hash (freeze --codebook-file)."),
    ("fixture-review", "Independent content review of the PROPOSED passage, rubric and responses (Grade 6-8 ELA)."),
    ("key-review", "Independent review of the PROVISIONAL key, including ambiguous items and seeded errors."),
    ("comparator-review", "Independent review that the manual comparator is a fair equivalent of the assisted task."),
    ("order-procedure", "Confirm whether the protocol requires randomization/counterbalancing and adopt or replace the proposed schedule."),
    ("thresholds", "Copy the protocol's measures and thresholds into the manifest as PROPOSALS; they are not validated cutoffs."),
    ("tester-notice", "Adult tester notice prepared, approved and delivered per protocol before any session."),
]


class IntegrityError(Exception):
    pass


# ---------------------------------------------------------------- utilities

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ref(obj: dict) -> str:
    return f"{obj['id']}@{obj['version']}"


def load_fixtures() -> dict:
    return {name: load_json(ROOT / rel) for name, rel in FIXTURE_FILES.items() if rel.endswith(".json")}


def response_texts(fixtures: dict) -> dict:
    return {item["id"]: item["text"] for item in fixtures["responses"]["items"]}


def span_problem(text: str, start, end, quote) -> str | None:
    """Return None for a valid span, otherwise the reason it is invalid."""
    if not isinstance(start, int) or not isinstance(end, int) or isinstance(start, bool) or isinstance(end, bool):
        return "offsets are not integers"
    if not 0 <= start < end <= len(text):
        return f"offsets {start}:{end} outside response length {len(text)}"
    if text[start:end] != quote:
        return f"quote does not match response text at {start}:{end}"
    return None


def inside_repository(path: Path) -> bool:
    resolved = path.resolve()
    repo_root = ROOT.parents[2]
    return resolved == repo_root or repo_root in resolved.parents


# ---------------------------------------------------------------- freeze

def bound_source(path: str | None, previous: dict, default: dict) -> dict:
    if path is None:
        return previous or default
    source = Path(path)
    return {**default, "status": "BOUND-BY-HASH", "sha256": sha256_file(source), "file_name": source.name}


def cmd_freeze(args) -> int:
    fixtures = load_fixtures()
    previous = load_json(MANIFEST) if MANIFEST.exists() else {}
    if args.key_file and inside_repository(Path(args.key_file)):
        raise IntegrityError("refusing to bind a key stored inside the public repository")
    key_entry = previous.get("key") or {"id": "KEY-PTER01-PROV", "status": "PROVISIONAL-UNREVIEWED",
                                        "visibility": "HIDDEN", "sha256": None}
    if args.key_file:
        key = load_json(Path(args.key_file))
        key_entry = {"id": key["key_id"], "version": key["version"], "status": key["status"],
                     "visibility": "HIDDEN: stored outside the public repository", "sha256": sha256_file(Path(args.key_file))}
    manifest = {
        "experiment": "P-TER-01 offline synthetic teacher ELA review",
        "manifest_version": HARNESS_VERSION,
        "scope": "Preparation only. Synthetic authored Grade 6-8 ELA responses. No participants, records, live model or billing.",
        "protocol": bound_source(args.protocol_file, previous.get("protocol"), {
            "id": "P-TER-01", "version": "0.2", "status": "SOURCE_NOT_LOCATED", "sha256": None, "file_name": None}),
        "codebook": bound_source(args.codebook_file, previous.get("codebook"), {
            "id": "ASSESSMENT-CONSTRUCT-CODEBOOK", "version": None, "status": "SOURCE_NOT_LOCATED", "sha256": None,
            "file_name": None}),
        "versions": {
            "passage_ref": ref(fixtures["passage"]),
            "rubric_ref": ref(fixtures["rubric"]),
            "response_set_version": fixtures["responses"]["set_version"],
            "adapter_ref": f"{fixtures['drafts']['adapter']['id']}@{fixtures['drafts']['adapter']['version']}",
            "harness_version": HARNESS_VERSION,
        },
        "files": {rel: sha256_file(ROOT / rel) for rel in FIXTURE_FILES.values()},
        "key": key_entry,
        "thresholds": previous.get("thresholds") or {
            "status": "UNBOUND",
            "note": "P-TER-01 v0.2 was not located. No threshold is computed or applied. When bound, values are proposals, not validated cutoffs.",
            "values": {}},
        "open_items": previous.get("open_items") or [
            {"id": item_id, "description": text, "status": "OPEN", "evidence": None}
            for item_id, text in DEFAULT_OPEN_ITEMS],
    }
    write_json(MANIFEST, manifest)
    print(f"manifest written: {MANIFEST.relative_to(ROOT)} sha256={sha256_file(MANIFEST)}")
    return 0


# ---------------------------------------------------------------- schedule

def cmd_schedule(args) -> int:
    fixtures = load_fixtures()
    testers = [t.strip() for t in args.testers.split(",") if t.strip()]
    if not testers or len(set(testers)) != len(testers):
        raise IntegrityError("tester ids must be non-empty and unique")
    sets = fixtures["responses"]["sets"]
    rng = random.Random(args.seed)
    order = testers[:]
    rng.shuffle(order)
    # Four arms: condition order x set-to-condition assignment. Balanced when the tester count is a multiple of 4.
    arms = [("manual", "assisted", "S1", "S2"), ("assisted", "manual", "S1", "S2"),
            ("manual", "assisted", "S2", "S1"), ("assisted", "manual", "S2", "S1")]
    assignments = []
    for index, tester in enumerate(order):
        first, second, first_set, second_set = arms[index % 4]
        position = 0
        blocks = []
        for block_position, (condition, set_id) in enumerate(((first, first_set), (second, second_set)), start=1):
            response_ids = sets[set_id][:]
            rng.shuffle(response_ids)
            tasks = []
            for response_id in response_ids:
                position += 1
                tasks.append({"task_id": f"{tester}-{condition[0].upper()}{position:02d}",
                              "sequence_position": position, "response_id": response_id})
            blocks.append({"block_position": block_position, "condition": condition, "response_set": set_id,
                           "tasks": tasks})
        assignments.append({"tester_id": tester, "arm": index % 4, "blocks": blocks})
    schedule = {
        "run_id": args.run_id,
        "status": "PROPOSED: protocol order/randomization requirement not verified (P-TER-01 v0.2 not located)",
        "seed": args.seed,
        "manifest_sha256": sha256_file(MANIFEST),
        "balanced": len(testers) % 4 == 0,
        "assignments": sorted(assignments, key=lambda a: a["tester_id"]),
    }
    write_json(Path(args.out), schedule)
    print(f"schedule written: {args.out} testers={len(testers)} balanced={schedule['balanced']}")
    return 0


# ---------------------------------------------------------------- packets

def find_assignment(schedule: dict, tester: str) -> dict:
    for assignment in schedule["assignments"]:
        if assignment["tester_id"] == tester:
            return assignment
    raise IntegrityError(f"tester {tester} is not in the schedule")


def cmd_packet(args) -> int:
    fixtures = load_fixtures()
    schedule = load_json(Path(args.schedule))
    block = next(b for b in find_assignment(schedule, args.tester)["blocks"] if b["condition"] == args.condition)
    texts = response_texts(fixtures)
    drafts = {(d["response_id"], d["criterion_id"]): d for d in fixtures["drafts"]["drafts"]}
    tasks = []
    for task in block["tasks"]:
        entry = {"task_id": task["task_id"], "sequence_position": task["sequence_position"],
                 "response_id": task["response_id"], "response_text": texts[task["response_id"]]}
        if args.condition == "assisted":
            entry["drafts"] = [{"draft_id": d["draft_id"], "criterion_id": d["criterion_id"], "value": d["value"],
                                "span": d["span"], "rationale": d["rationale"]}
                               for c in fixtures["rubric"]["criteria"]
                               for d in [drafts[(task["response_id"], c["id"])]]]
            entry["draft_notice"] = "AI-style draft from a frozen fixture adapter. It may be wrong. Accept, revise or reject each criterion."
        tasks.append(entry)
    packet = {
        "run_id": schedule["run_id"], "tester_id": args.tester, "condition": args.condition,
        "manifest_sha256": schedule["manifest_sha256"],
        "synthetic_notice": "All responses are authored synthetic examples, not student work.",
        "passage": {k: fixtures["passage"][k] for k in ("title", "prompt", "text")},
        "rubric": {k: fixtures["rubric"][k] for k in ("allowed_values", "value_notes", "not_scored", "criteria")},
        "tasks": tasks,
    }
    out = Path(args.out) / f"{args.tester}-{args.condition}.packet.json"
    write_json(out, packet)
    print(f"packet written: {out}")
    return 0


# ---------------------------------------------------------------- blank tables

def write_csv(path: Path, columns: list, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def cmd_blank_tables(args) -> int:
    fixtures = load_fixtures()
    manifest = load_json(MANIFEST)
    schedule = load_json(Path(args.schedule))
    versions = manifest["versions"]
    drafts = {(d["response_id"], d["criterion_id"]): d for d in fixtures["drafts"]["drafts"]}
    criteria = [c["id"] for c in fixtures["rubric"]["criteria"]]
    for condition in CONDITIONS:
        sessions, tasks, criterion_rows = [], [], []
        for assignment in schedule["assignments"]:
            for block in assignment["blocks"]:
                if block["condition"] != condition:
                    continue
                common = {"run_id": schedule["run_id"], "tester_id": assignment["tester_id"], "condition": condition}
                sessions.append({**common, "manifest_sha256": schedule["manifest_sha256"],
                                 "block_position": block["block_position"], "response_set": block["response_set"]})
                for task in block["tasks"]:
                    tasks.append({**common, "manifest_sha256": schedule["manifest_sha256"],
                                  "task_id": task["task_id"], "sequence_position": task["sequence_position"],
                                  "response_id": task["response_id"],
                                  "response_set_version": versions["response_set_version"],
                                  "rubric_ref": versions["rubric_ref"], "passage_ref": versions["passage_ref"],
                                  "adapter_ref": versions["adapter_ref"] if condition == "assisted" else NOT_APPLICABLE})
                    for criterion in criteria:
                        row = {**common, "task_id": task["task_id"], "response_id": task["response_id"],
                               "criterion_id": criterion}
                        if condition == "assisted":
                            draft = drafts[(task["response_id"], criterion)]
                            row.update({"draft_id": draft["draft_id"], "original_value": draft["value"],
                                        "original_span_start": draft["span"]["start"] if draft["span"] else NOT_APPLICABLE,
                                        "original_span_end": draft["span"]["end"] if draft["span"] else NOT_APPLICABLE})
                        criterion_rows.append(row)
        directory = Path(args.out) / condition
        write_csv(directory / "sessions.csv", SESSION_COLUMNS, sessions)
        write_csv(directory / "tasks.csv", TASK_COLUMNS, tasks)
        write_csv(directory / "criteria.csv", CRITERIA_COLUMNS[condition], criterion_rows)
        print(f"{condition}: sessions={len(sessions)} tasks={len(tasks)} criterion_rows={len(criterion_rows)} -> {directory}")
    return 0


# ---------------------------------------------------------------- check

class Report:
    def __init__(self):
        self.failures, self.notes = [], []

    def fail(self, area: str, message: str) -> None:
        self.failures.append(f"[{area}] {message}")

    def note(self, message: str) -> None:
        self.notes.append(message)


def check_manifest(report: Report, manifest: dict, fixtures: dict) -> None:
    for rel, expected in manifest["files"].items():
        path = ROOT / rel
        if not path.exists():
            report.fail("version", f"{rel} listed in manifest is missing")
        elif sha256_file(path) != expected:
            report.fail("version", f"{rel} changed after freeze (sha256 mismatch)")
    missing = set(FIXTURE_FILES.values()) - set(manifest["files"])
    for rel in sorted(missing):
        report.fail("version", f"{rel} is not frozen in the manifest")
    versions = manifest["versions"]
    responses, drafts = fixtures["responses"], fixtures["drafts"]
    expected_links = {
        "responses.passage_ref": (responses["passage_ref"], ref(fixtures["passage"])),
        "responses.rubric_ref": (responses["rubric_ref"], ref(fixtures["rubric"])),
        "drafts.rubric_ref": (drafts["rubric_ref"], ref(fixtures["rubric"])),
        "drafts.response_set_version": (drafts["response_set_version"], responses["set_version"]),
        "manifest.passage_ref": (versions["passage_ref"], ref(fixtures["passage"])),
        "manifest.rubric_ref": (versions["rubric_ref"], ref(fixtures["rubric"])),
        "manifest.response_set_version": (versions["response_set_version"], responses["set_version"]),
        "manifest.adapter_ref": (versions["adapter_ref"], f"{drafts['adapter']['id']}@{drafts['adapter']['version']}"),
    }
    for name, (actual, expected) in expected_links.items():
        if actual != expected:
            report.fail("version", f"{name} is {actual!r}; expected {expected!r}")


def check_fixture_evidence(report: Report, fixtures: dict) -> None:
    texts = response_texts(fixtures)
    allowed = set(fixtures["rubric"]["allowed_values"])
    criteria = {c["id"] for c in fixtures["rubric"]["criteria"]}
    set_members = [r for members in fixtures["responses"]["sets"].values() for r in members]
    if sorted(set_members) != sorted(texts):
        report.fail("fixture", "response sets do not partition the response items exactly")
    seen = set()
    for draft in fixtures["drafts"]["drafts"]:
        pair = (draft["response_id"], draft["criterion_id"])
        if pair in seen:
            report.fail("fixture", f"duplicate draft for {pair}")
        seen.add(pair)
        if draft["response_id"] not in texts or draft["criterion_id"] not in criteria:
            report.fail("fixture", f"{draft['draft_id']} references an unknown response or criterion")
            continue
        if draft["value"] not in allowed:
            report.fail("fixture", f"{draft['draft_id']} value {draft['value']!r} not allowed by rubric")
        report_span(report, "evidence", draft["draft_id"], draft["value"], draft["span"], texts[draft["response_id"]])
    expected = {(r, c) for r in texts for c in criteria}
    for pair in sorted(expected - seen):
        report.fail("fixture", f"no draft for {pair}")


def report_span(report: Report, area: str, label: str, value: str, span, text: str) -> None:
    if value in ("IE", "0"):
        if span is not None:
            report.fail(area, f"{label} cites a span for value {value}")
        return
    if span is None:
        report.fail(area, f"{label} has value {value} without an evidence span")
        return
    problem = span_problem(text, span.get("start"), span.get("end"), span.get("quote"))
    if problem:
        report.fail(area, f"{label} invalid evidence span: {problem}")


def check_key(report: Report, manifest: dict, fixtures: dict, key_path: Path) -> None:
    if inside_repository(key_path):
        report.fail("key", "key file is inside the public repository; move it to private storage")
    expected = manifest["key"].get("sha256")
    if expected is None:
        report.fail("key", "manifest has no key hash; run freeze --key-file")
    elif sha256_file(key_path) != expected:
        report.fail("key", "key file does not match the frozen key hash")
    key = load_json(key_path)
    texts = response_texts(fixtures)
    allowed = set(fixtures["rubric"]["allowed_values"])
    drafts = {(d["response_id"], d["criterion_id"]): d for d in fixtures["drafts"]["drafts"]}
    if key.get("response_set_version") != fixtures["responses"]["set_version"] or key.get("rubric_ref") != ref(fixtures["rubric"]):
        report.fail("version", "key is not linked to the frozen response set and rubric")
    seen = set()
    for entry in key["entries"]:
        pair = (entry["response_id"], entry["criterion_id"])
        seen.add(pair)
        if pair not in drafts:
            report.fail("key", f"key entry {pair} has no matching response/criterion")
            continue
        if entry["key_value"] not in allowed:
            report.fail("key", f"key entry {pair} value {entry['key_value']!r} not allowed")
        report_span(report, "evidence", f"key {pair}", entry["key_value"], entry["key_span"], texts[pair[0]])
        draft = drafts[pair]
        differs = draft["value"] != entry["key_value"] or draft["span"] != entry["key_span"]
        if differs != bool(entry.get("seeded_error")):
            report.fail("key", f"{pair}: seeded_error flag does not match draft/key difference")
    for pair in sorted(set(drafts) - seen):
        report.fail("key", f"key has no entry for {pair}")


def check_schedule(report: Report, schedule: dict, fixtures: dict) -> None:
    if schedule["manifest_sha256"] != sha256_file(MANIFEST):
        report.fail("version", "schedule was built from a different manifest")
    sets = fixtures["responses"]["sets"]
    for assignment in schedule["assignments"]:
        blocks = assignment["blocks"]
        if sorted(b["condition"] for b in blocks) != sorted(CONDITIONS):
            report.fail("schedule", f"{assignment['tester_id']} does not have exactly one block per condition")
        if sorted(b["response_set"] for b in blocks) != sorted(sets):
            report.fail("schedule", f"{assignment['tester_id']} does not see each response set exactly once")
        for block in blocks:
            if sorted(t["response_id"] for t in block["tasks"]) != sorted(sets[block["response_set"]]):
                report.fail("schedule", f"{assignment['tester_id']} {block['condition']} tasks do not match set {block['response_set']}")


def check_packets(report: Report, packet_dir: Path, key_path: Path | None) -> None:
    tokens = list(KEY_ONLY_TOKENS)
    if key_path:
        tokens.append(load_json(key_path)["nonce"])
    for path in sorted(packet_dir.glob("*.packet.json")):
        raw = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in raw:
                report.fail("hidden-key", f"{path.name} contains key-only content ({token[:12]}...)")
        packet = json.loads(raw)
        has_drafts = any("drafts" in task for task in packet["tasks"])
        if packet["condition"] == "manual" and has_drafts:
            report.fail("condition", f"{path.name} is a manual packet but contains drafts")
        if packet["condition"] == "assisted" and not has_drafts:
            report.fail("condition", f"{path.name} is an assisted packet without drafts")


def read_csv(path: Path, expected_columns: list, report: Report) -> list:
    if not path.exists():
        report.fail("table", f"{path} is missing")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_columns:
            report.fail("table", f"{path.name} columns do not match the {path.parent.name} template")
            return []
        return list(reader)


def number_problem(value: str) -> str | None:
    if value == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return "not a number"
    if number != number or number < 0 or number == float("inf"):
        return "must be a finite non-negative number"
    return None


def check_outcomes(report: Report, outcome_dir: Path, schedule: dict, manifest: dict, fixtures: dict) -> None:
    texts = response_texts(fixtures)
    allowed = set(fixtures["rubric"]["allowed_values"])
    criteria = [c["id"] for c in fixtures["rubric"]["criteria"]]
    drafts = {(d["response_id"], d["criterion_id"]): d for d in fixtures["drafts"]["drafts"]}
    versions = manifest["versions"]
    for condition in CONDITIONS:
        directory = outcome_dir / condition
        planned_tasks = {t["task_id"]: (a["tester_id"], t["response_id"])
                         for a in schedule["assignments"] for b in a["blocks"] if b["condition"] == condition
                         for t in b["tasks"]}
        planned_sessions = {a["tester_id"] for a in schedule["assignments"]}
        sessions = read_csv(directory / "sessions.csv", SESSION_COLUMNS, report)
        tasks = read_csv(directory / "tasks.csv", TASK_COLUMNS, report)
        rows = read_csv(directory / "criteria.csv", CRITERIA_COLUMNS[condition], report)
        for row in sessions:
            check_common(report, condition, row, schedule)
            if row["tester_id"] not in planned_sessions:
                report.fail("denominator", f"{condition} session for unscheduled tester {row['tester_id']}")
            if row["session_status"] not in STATUS_VALUES | {""}:
                report.fail("table", f"{condition} session {row['tester_id']} status {row['session_status']!r}")
            if number_problem(row["setup_time_s"]):
                report.fail("table", f"{condition} session {row['tester_id']} setup_time_s {number_problem(row['setup_time_s'])}")
        if len({r["tester_id"] for r in sessions}) != len(sessions):
            report.fail("denominator", f"{condition} sessions contain duplicate testers")
        task_status = {}
        for row in tasks:
            check_common(report, condition, row, schedule)
            task_id = row["task_id"]
            if task_id in task_status:
                report.fail("denominator", f"{condition} duplicate task row {task_id}")
            task_status[task_id] = row["task_status"]
            if planned_tasks.get(task_id) != (row["tester_id"], row["response_id"]):
                report.fail("denominator", f"{condition} task {task_id} does not match the schedule")
            expected_adapter = versions["adapter_ref"] if condition == "assisted" else NOT_APPLICABLE
            for column, expected in (("response_set_version", versions["response_set_version"]),
                                     ("rubric_ref", versions["rubric_ref"]), ("passage_ref", versions["passage_ref"]),
                                     ("adapter_ref", expected_adapter)):
                if row[column] != expected:
                    report.fail("version", f"{condition} task {task_id} {column}={row[column]!r}; expected {expected!r}")
            if row["task_status"] not in STATUS_VALUES | {""}:
                report.fail("table", f"{condition} task {task_id} status {row['task_status']!r}")
            for column in ("active_review_s", "pause_repair_s"):
                if number_problem(row[column]):
                    report.fail("table", f"{condition} task {task_id} {column} {number_problem(row[column])}")
        for task_id in sorted(set(planned_tasks) - set(task_status)):
            report.fail("denominator", f"{condition} scheduled task {task_id} has no row (missing rows hide the denominator)")
        seen = set()
        for row in rows:
            label = f"{condition} {row['task_id']} {row['criterion_id']}"
            pair = (row["task_id"], row["criterion_id"])
            if pair in seen:
                report.fail("denominator", f"{label} duplicate criterion row")
            seen.add(pair)
            if row["task_id"] not in planned_tasks or row["criterion_id"] not in criteria \
                    or planned_tasks[row["task_id"]] != (row["tester_id"], row["response_id"]):
                report.fail("denominator", f"{label} does not match the schedule")
                continue
            check_criterion_row(report, condition, label, row, texts[row["response_id"]], allowed,
                                drafts[(row["response_id"], row["criterion_id"])], task_status.get(row["task_id"], ""))
        for task_id in planned_tasks:
            for criterion in criteria:
                if (task_id, criterion) not in seen:
                    report.fail("denominator", f"{condition} {task_id} {criterion} has no criterion row")
        tally(report, condition, sessions, tasks, rows, len(planned_tasks), len(planned_sessions))


def check_common(report: Report, condition: str, row: dict, schedule: dict) -> None:
    if row["run_id"] != schedule["run_id"] or row["condition"] != condition:
        report.fail("version", f"{condition} row for {row.get('tester_id')} has run_id/condition not matching this run")
    if "manifest_sha256" in row and row["manifest_sha256"] != schedule["manifest_sha256"]:
        report.fail("version", f"{condition} row for {row.get('tester_id')} links to a different manifest")


def check_criterion_row(report, condition, label, row, text, allowed, draft, status) -> None:
    final = row["final_value"]
    if final not in allowed | {""}:
        report.fail("table", f"{label} final_value {final!r} not allowed")
    if row["rater_span_supports"] not in RATER_VALUES | {""}:
        report.fail("table", f"{label} rater_span_supports {row['rater_span_supports']!r}")
    span_cells = (row["final_span_start"], row["final_span_end"], row["final_span_quote"])
    final_span = None
    if any(span_cells):
        if not all(span_cells):
            report.fail("evidence", f"{label} partial evidence span (start, end and quote are all required)")
        else:
            try:
                final_span = {"start": int(span_cells[0]), "end": int(span_cells[1]), "quote": span_cells[2]}
            except ValueError:
                report.fail("evidence", f"{label} evidence span offsets are not integers")
            else:
                problem = span_problem(text, final_span["start"], final_span["end"], final_span["quote"])
                if problem:
                    report.fail("evidence", f"{label} invalid evidence span: {problem}")
                if final in ("0", "IE"):
                    report.fail("evidence", f"{label} cites a span for value {final}")
    if status == "not_started" and (final or any(span_cells) or row.get("decision")):
        report.fail("table", f"{label} has outcomes for a task marked not_started")
    if condition != "assisted":
        return
    draft_start = str(draft["span"]["start"]) if draft["span"] else NOT_APPLICABLE
    draft_end = str(draft["span"]["end"]) if draft["span"] else NOT_APPLICABLE
    if (row["draft_id"], row["original_value"], row["original_span_start"], row["original_span_end"]) != \
            (draft["draft_id"], draft["value"], draft_start, draft_end):
        report.fail("version", f"{label} original value/span does not match frozen draft {draft['draft_id']}")
    decision = row["decision"]
    if decision not in DECISIONS | {""}:
        report.fail("table", f"{label} decision {decision!r} not accept/revise/reject")
    if decision and final:
        # Blank span cells on accept/revise mean the draft's span stands; on reject nothing is inherited.
        if final_span is None and not any(span_cells) and decision in ("accept", "revise"):
            final_span = draft["span"]
        same = final == draft["value"] and final_span == draft["span"]
        if decision == "accept" and not same:
            report.fail("table", f"{label} accept recorded but final differs from the draft")
        if decision == "revise" and same:
            report.fail("table", f"{label} revise recorded but final equals the draft")


def tally(report, condition, sessions, tasks, rows, task_denominator, session_denominator) -> None:
    def count(values, options):
        counts = {option: sum(1 for v in values if v == option) for option in options}
        counts["missing"] = sum(1 for v in values if v == "")
        return counts

    status = count([t["task_status"] for t in tasks], sorted(STATUS_VALUES))
    present = {c: sum(1 for t in tasks if t[c] != "") for c in ("active_review_s", "pause_repair_s")}
    setup = sum(1 for s in sessions if s["setup_time_s"] != "")
    lines = [f"{condition}: task denominator n={task_denominator} (scheduled); session denominator n={session_denominator}",
             f"  task_status " + ", ".join(f"{k}={v}/{task_denominator}" for k, v in status.items()),
             f"  setup_time_s recorded {setup}/{session_denominator}; "
             + "; ".join(f"{k} recorded {v}/{task_denominator}" for k, v in present.items())]
    if condition == "assisted":
        decisions = count([r["decision"] for r in rows], sorted(DECISIONS))
        lines.append("  decisions " + ", ".join(f"{k}={v}/{len(rows)}" for k, v in decisions.items()))
    finals = sum(1 for r in rows if r["final_value"] != "")
    unsupported = sum(1 for r in rows if r["final_value"] in ("1", "2") and not r["final_span_quote"]
                      and r.get("decision", "") not in ("accept", "revise"))
    rated = count([r["rater_span_supports"] for r in rows], sorted(RATER_VALUES))
    lines.append(f"  final_value recorded {finals}/{len(rows)}; missing values stay missing (no imputation)")
    lines.append(f"  final 1/2 with no cited evidence span {unsupported}/{len(rows)}; independent rater span support "
                 + ", ".join(f"{k}={v}/{len(rows)}" for k, v in rated.items()))
    report.note("\n".join(lines))


def run_readiness(manifest: dict) -> list:
    blockers = []
    for source in ("protocol", "codebook"):
        if manifest[source]["status"] != "BOUND-BY-HASH":
            blockers.append(f"{source}: {manifest[source]['status']}")
    if manifest["key"].get("sha256") is None:
        blockers.append("key: not frozen by hash")
    if manifest["thresholds"]["status"] != "BOUND-AS-PROPOSALS":
        blockers.append(f"thresholds: {manifest['thresholds']['status']}")
    for item in manifest["open_items"]:
        if item["status"] != "RESOLVED" or not item.get("evidence"):
            blockers.append(f"{item['id']}: {item['status']}")
    return blockers


def cmd_check(args) -> int:
    report = Report()
    if not MANIFEST.exists():
        print("FAIL: manifest.json missing; run freeze")
        return 1
    manifest, fixtures = load_json(MANIFEST), load_fixtures()
    check_manifest(report, manifest, fixtures)
    check_fixture_evidence(report, fixtures)
    key_path = Path(args.key) if args.key else None
    if key_path:
        check_key(report, manifest, fixtures, key_path)
    schedule = load_json(Path(args.schedule)) if args.schedule else None
    if schedule:
        check_schedule(report, schedule, fixtures)
    if args.packets:
        check_packets(report, Path(args.packets), key_path)
    if args.outcomes:
        if schedule is None:
            report.fail("table", "--outcomes requires --schedule (the schedule is the denominator)")
        else:
            check_outcomes(report, Path(args.outcomes), schedule, manifest, fixtures)
    print(f"P-TER-01 preparation integrity check (harness {HARNESS_VERSION}); manifest sha256={sha256_file(MANIFEST)}")
    print("Checked: manifest hashes, version linkage, fixture evidence spans"
          + (", hidden key" if key_path else "") + (", schedule" if schedule else "")
          + (", tester packets" if args.packets else "") + (", outcome tables" if args.outcomes else ""))
    for note in report.notes:
        print(note)
    for failure in report.failures:
        print(f"FAIL {failure}")
    print(f"Preparation integrity: {'PASS' if not report.failures else 'FAIL'} ({len(report.failures)} failures)")
    blockers = run_readiness(manifest)
    print("Run readiness: " + ("READY" if not blockers else "BLOCKED"))
    for blocker in blockers:
        print(f"  BLOCKED {blocker}")
    if report.failures:
        return 1
    return 2 if args.require_run_ready and blockers else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--protocol-file")
    freeze.add_argument("--codebook-file")
    freeze.add_argument("--key-file")
    schedule = sub.add_parser("schedule")
    schedule.add_argument("--run-id", required=True)
    schedule.add_argument("--testers", required=True, help="comma-separated pseudonymous ids, e.g. T01,T02")
    schedule.add_argument("--seed", type=int, required=True)
    schedule.add_argument("--out", required=True)
    packet = sub.add_parser("packet")
    packet.add_argument("--schedule", required=True)
    packet.add_argument("--tester", required=True)
    packet.add_argument("--condition", choices=CONDITIONS, required=True)
    packet.add_argument("--out", required=True)
    tables = sub.add_parser("blank-tables")
    tables.add_argument("--schedule", required=True)
    tables.add_argument("--out", required=True)
    check = sub.add_parser("check")
    check.add_argument("--key")
    check.add_argument("--schedule")
    check.add_argument("--packets")
    check.add_argument("--outcomes")
    check.add_argument("--require-run-ready", action="store_true")
    args = parser.parse_args(argv)
    handlers = {"freeze": cmd_freeze, "schedule": cmd_schedule, "packet": cmd_packet,
                "blank-tables": cmd_blank_tables, "check": cmd_check}
    try:
        return handlers[args.command](args)
    except IntegrityError as error:
        print(f"FAIL {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
