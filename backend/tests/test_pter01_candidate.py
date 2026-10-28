"""Guards for the P-TER-01 attendance candidate and the PR #32 fixtures.

The candidate task and rubric are UNAPPROVED. These tests hold them to that
state: they keep the candidate out of the server rubric registry, keep the
feature flag off and the approval pins empty, and prove the existing
engineering fixtures are unchanged. All text involved is synthetic.
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

from app.core.ai_feedback_settings import load_ai_feedback_settings
from app.services.ai_feedback import rubrics as rubrics_module
from app.services.ai_feedback.prompt import has_embedded_instructions
from app.services.ai_feedback.rubrics import RubricNotFound, canonical_sha256, get_approved_rubric, load_registry

REPO = Path(__file__).resolve().parents[2]
PILOT = REPO / "docs" / "pilots" / "p-ter-01"
CANDIDATE_DIR = PILOT / "candidates" / "attendance"
TASK_PATH = CANDIDATE_DIR / "task.TASK-ATTEND.v0.3.candidate.json"
RUBRIC_PATH = CANDIDATE_DIR / "rubric.RUB-ATTEND3.v0.3.candidate.json"
MANIFEST = json.loads((PILOT / "manifest.json").read_text(encoding="utf-8"))
TASK = json.loads(TASK_PATH.read_text(encoding="utf-8"))
RUBRIC = json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))

AI_FEEDBACK_ENV = (
    "AEOS_AI_FEEDBACK_ENABLED",
    "AEOS_AI_FEEDBACK_APPROVED_RUBRICS",
    "AEOS_AI_FEEDBACK_ORG_ALLOWLIST",
)


def _sha256(path: Path) -> str:
    # Normalize CRLF so a Windows autocrlf checkout does not fail the guard.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


# ---------------------------------------------------------------------------
# Unapproved and unloadable.
# ---------------------------------------------------------------------------


def test_candidate_is_outside_the_server_registry():
    assert rubrics_module.RUBRIC_DIR not in CANDIDATE_DIR.parents
    assert set(load_registry()) == {("RUB-CER3", "0.1")}, (
        "Adding a rubric to the server registry is an approval step: update this test only "
        "together with a completed REVIEW_WORKSHEET.md Part F."
    )


def test_candidate_cannot_be_used_even_with_a_pin_for_its_hash():
    candidate = rubrics_module._parse(RUBRIC_PATH)
    with pytest.raises(RubricNotFound):
        get_approved_rubric(candidate.id, candidate.version, frozenset({candidate.approval_pin()}))


def test_candidate_status_is_unapproved_everywhere():
    assert TASK["status"] == RUBRIC["status"] == MANIFEST["candidates"]["status"] == "CANDIDATE-UNAPPROVED"
    assert MANIFEST["candidates"]["in_server_registry"] is False
    assert MANIFEST["protocol"]["status"] == "SOURCE_NOT_LOCATED" and MANIFEST["protocol"]["sha256"] is None
    assert all(item["status"] == "OPEN" and item["evidence"] is None for item in MANIFEST["open_items"])


def test_feature_flag_defaults_off_and_approval_pins_are_empty(monkeypatch):
    for name in AI_FEEDBACK_ENV:
        monkeypatch.delenv(name, raising=False)
    settings = load_ai_feedback_settings()
    assert settings.enabled is False
    assert settings.approved_rubrics == frozenset()
    assert MANIFEST["feature_flag_default"] == {"AEOS_AI_FEEDBACK_ENABLED": False}
    assert MANIFEST["approval_pins"] == []


def test_env_example_ships_the_flag_off_and_no_pins():
    lines = (REPO / "backend" / ".env.example").read_text(encoding="utf-8").splitlines()
    assert "AEOS_AI_FEEDBACK_ENABLED=false" in lines
    assert "AEOS_AI_FEEDBACK_APPROVED_RUBRICS=" in lines


# ---------------------------------------------------------------------------
# Preserved engineering fixtures and frozen candidate files.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("relative", sorted(MANIFEST["preserved_engineering_fixtures"]))
def test_engineering_fixtures_are_unchanged(relative):
    assert _sha256(REPO / relative) == MANIFEST["preserved_engineering_fixtures"][relative]


def test_rub_cer3_pin_hash_is_unchanged():
    assert load_registry()[("RUB-CER3", "0.1")].sha256 == (
        "8f7584b2ec1aa21cfc351e64b9907687b0e1c40570b452f8385f582741103861"
    )


@pytest.mark.parametrize("relative", sorted(MANIFEST["files"]))
def test_candidate_files_match_the_manifest(relative):
    assert _sha256(PILOT / relative) == MANIFEST["files"][relative]


# ---------------------------------------------------------------------------
# Candidate shape, including the 0 / IE / abstention boundary.
# ---------------------------------------------------------------------------


def test_candidate_rubric_parses_with_the_server_parser():
    candidate = rubrics_module._parse(RUBRIC_PATH)
    assert (candidate.id, candidate.version) == ("RUB-ATTEND3", "0.3")
    assert candidate.criterion_ids == ("C1", "C2", "C3")
    assert candidate.sha256 == canonical_sha256(RUBRIC)


def test_candidate_rubric_defines_values_and_keeps_abstention_out_of_them():
    assert RUBRIC["allowed_values"] == ["0", "1", "2", "IE"]
    assert set(RUBRIC["value_definitions"]) == set(RUBRIC["allowed_values"])
    for criterion in RUBRIC["criteria"]:
        # IE is a response-level judgment of sufficiency, not a criterion level.
        assert set(criterion["levels"]) == {"0", "1", "2"}
    assert "never counted as 0" in RUBRIC["value_definitions"]["IE"]
    assert set(RUBRIC["not_values"]) == {"blank", "ai_abstention"}
    assert "never sets or implies 0 or IE" in RUBRIC["not_values"]["ai_abstention"]


def test_boundary_document_defines_every_rule_the_worksheet_asks_about():
    boundaries = (PILOT / "SCORING_BOUNDARIES.md").read_text(encoding="utf-8")
    worksheet = (PILOT / "REVIEW_WORKSHEET.md").read_text(encoding="utf-8")
    defined = set(re.findall(r"^\| (B\d+|A\d) \|", boundaries, re.M)) | set(re.findall(r"^- \*\*(A\d)\.\*\*", boundaries, re.M))
    asked = set(re.findall(r"^\| (B\d+|A\d) ", worksheet, re.M))
    assert {f"B{n}" for n in range(1, 11)} | {"A1", "A2", "A3", "A4"} == defined == asked


def test_task_is_synthetic_blind_and_within_request_limits():
    assert TASK["data_classification"] == RUBRIC["data_classification"] == "synthetic"
    assert TASK["rubric_ref"] == f"{RUBRIC['id']}@{RUBRIC['version']}"
    assert RUBRIC["task_ref"] == f"{TASK['id']}@{TASK['version']}"
    assert len(TASK["passage"]["text"]) <= 6000
    ids = [response["id"] for response in TASK["responses"]]
    assert len(ids) == len(set(ids)) == 8
    for response in TASK["responses"]:
        # Blind set: no profile, intended value or key field is committed.
        assert set(response) == {"id", "text"}
        assert 1 <= len(response["text"]) <= 4000 and response["text"].strip()


def test_candidate_set_exercises_the_injection_heuristic_exactly_once():
    flagged = [r["id"] for r in TASK["responses"] if has_embedded_instructions(r["text"])]
    assert len(flagged) == 1
    assert not has_embedded_instructions(TASK["passage"]["text"], TASK["passage"]["prompt"])
