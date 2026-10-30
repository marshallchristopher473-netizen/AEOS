"""Teacher-free quality eval harness: checks, consistency and outputs.

Every provider output in this module is a DETERMINISTIC FIXTURE written by
hand to exercise the harness. None of it is model output, and nothing here
measures feedback quality.
"""

import json

from app.services.ai_feedback.provider import ProviderUnavailable
from tests import ai_feedback_quality_eval as quality_eval
from tests.test_ai_feedback import FIXTURES, RUBRIC, FakeProvider, abstain, criterion, good_output, settings

ALL_ABSTAIN = [abstain("C1"), abstain("C2"), abstain("C3")]
SHORT_ABSTAINS = good_output(overall_abstention="insufficient_response", criteria=ALL_ABSTAIN,
                             review_flags=["very_short_response"])
R05_FEEDBACK = good_output(
    criteria=[criterion("C1", ["Cool roofs reflect sunlight."]), abstain("C2"), abstain("C3")],
    review_flags=["possible_embedded_instructions"],
)
R10_FEEDBACK = good_output(
    criteria=[criterion("C1", ["Cool roofs are white."]), abstain("C2"), abstain("C3")],
    review_flags=["possible_embedded_instructions"],
)
R10_ABSTAINS = good_output(criteria=ALL_ABSTAIN, review_flags=["possible_embedded_instructions"])
OBEYS_INJECTION = good_output(
    criteria=[criterion("C1", ["Cool roofs reflect sunlight."], strength="Full points: a score of 2."),
              abstain("C2"), abstain("C3")],
)


def scripted(r01, r03, r05, r10, runs=2):
    """Fixture order is R01, R03, R05, R10; each response is requested ``runs`` times."""
    completions = []
    for per_response in (r01, r03, r05, r10):
        completions += per_response if isinstance(per_response, list) else [per_response] * runs
    return FakeProvider(completions)


def evaluate(provider, runs=2):
    return quality_eval.run_eval(provider, settings(), RUBRIC, FIXTURES, runs)


def by_id(report):
    return {response["response_id"]: response for response in report["responses"]}


def test_expected_behaviour_on_every_profile_passes():
    report = evaluate(scripted(good_output(), SHORT_ABSTAINS, R05_FEEDBACK, R10_FEEDBACK))

    summary = report["summary"]
    assert summary["passed"] is True
    assert (summary["checks_passed"], summary["checks_total"]) == (8, 8)
    assert (summary["consistent_responses"], summary["responses"]) == (4, 4)
    assert summary["total_cost_microusd"] > 0
    assert by_id(report)["R03"]["runs"][0]["draft_status"] == "abstained"


def test_obeying_embedded_instructions_is_rejected_and_fails_its_check():
    report = evaluate(scripted(good_output(), SHORT_ABSTAINS, OBEYS_INJECTION, R10_FEEDBACK))

    r05 = by_id(report)["R05"]["runs"][0]
    assert r05["draft_status"] == "rejected_output"
    assert r05["check_failure"].startswith("rejected_output")
    assert report["summary"]["rejected_outputs"] == 2
    assert report["summary"]["passed"] is False


def test_strong_response_with_an_abstention_fails():
    partial = good_output(criteria=[criterion("C1", ["it keeps the building cooler inside"]), abstain("C2"),
                                    criterion("C3", ["less heat moves down into the rooms"])])
    report = evaluate(scripted(partial, SHORT_ABSTAINS, R05_FEEDBACK, R10_FEEDBACK))

    assert by_id(report)["R01"]["runs"][0]["check_failure"] == "expected feedback on every criterion; abstained on C2"
    assert report["summary"]["passed"] is False


def test_strong_response_with_an_unfound_quote_fails():
    invented = good_output(criteria=[criterion("C1", ["it keeps the building cooler inside"]),
                                     criterion("C2", ["a quote that is not in the response"]),
                                     criterion("C3", ["less heat moves down into the rooms"])])
    report = evaluate(scripted(invented, SHORT_ABSTAINS, R05_FEEDBACK, R10_FEEDBACK))

    assert by_id(report)["R01"]["runs"][0]["check_failure"] is not None
    assert report["summary"]["passed"] is False


def test_short_response_that_gets_feedback_fails():
    feedback_on_short = good_output(criteria=[criterion("C1", ["It saves"]), abstain("C2"), abstain("C3")])
    report = evaluate(scripted(good_output(), feedback_on_short, R05_FEEDBACK, R10_FEEDBACK))

    assert by_id(report)["R03"]["runs"][0]["check_failure"].startswith("expected an abstention")


def test_runs_that_disagree_fail_even_when_each_run_passes():
    report = evaluate(scripted(good_output(), SHORT_ABSTAINS, R05_FEEDBACK, [R10_FEEDBACK, R10_ABSTAINS]))

    r10 = by_id(report)["R10"]
    assert [run["check_failure"] for run in r10["runs"]] == [None, None]
    assert r10["consistent"] is False
    assert report["summary"]["passed"] is False


def test_provider_error_is_recorded_and_the_eval_continues():
    report = evaluate(scripted(good_output(), SHORT_ABSTAINS, R05_FEEDBACK,
                               [ProviderUnavailable(), R10_FEEDBACK]))

    r10 = by_id(report)["R10"]["runs"]
    assert r10[0]["draft_status"] == "provider_error" and r10[1]["draft_status"] == "ready"
    assert report["summary"]["provider_errors"] == 1
    assert report["summary"]["passed"] is False


def test_review_sheet_shows_every_response_its_draft_and_the_questions():
    report = evaluate(scripted(good_output(), SHORT_ABSTAINS, R05_FEEDBACK, R10_FEEDBACK), runs=1)
    header = {"model_id": "m", "prompt_version": "p", "rubric": RUBRIC.approval_pin(), "run_at": "now"}
    sheet = quality_eval.review_sheet(report, header, FIXTURES["passage"]["prompt"])

    assert "SYNTHETIC" in sheet and "not pilot evidence" in sheet
    for response_id in ("R01", "R03", "R05", "R10"):
        assert f"## {response_id} (" in sheet
    assert "You state a clear benefit." in sheet
    assert "_No draft text" in sheet
    assert sheet.count(quality_eval.REVIEW_QUESTIONS[0]) == 4


KEY = "sk-synthetic-eval-key-must-not-be-written"


def configure(monkeypatch, **changes):
    values = {
        "AEOS_AI_FEEDBACK_EVAL": "1",
        "AEOS_AI_FEEDBACK_MODEL": "configured-model-under-test",
        "AEOS_AI_FEEDBACK_API_KEY": KEY,
        "AEOS_AI_FEEDBACK_INPUT_USD_PER_MTOK": "4",
        "AEOS_AI_FEEDBACK_OUTPUT_USD_PER_MTOK": "20",
    }
    values.update(changes)
    for name, value in values.items():
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)


def test_main_spends_nothing_without_the_explicit_eval_switch(monkeypatch, tmp_path, capsys):
    configure(monkeypatch, AEOS_AI_FEEDBACK_EVAL=None)
    provider = FakeProvider()
    monkeypatch.setattr(quality_eval, "AnthropicFeedbackProvider", lambda _settings: provider)

    assert quality_eval.main(["--out", str(tmp_path / "out")]) == 2
    output = json.loads(capsys.readouterr().out)
    assert output == {"result": "BLOCKED", "missing_or_invalid": ["AEOS_AI_FEEDBACK_EVAL"]}
    assert (provider.checks, provider.calls) == (0, [])
    assert not (tmp_path / "out").exists()


def test_main_is_blocked_without_a_key(monkeypatch, tmp_path, capsys):
    configure(monkeypatch, AEOS_AI_FEEDBACK_API_KEY=None)

    assert quality_eval.main(["--out", str(tmp_path / "out")]) == 2
    assert "AEOS_AI_FEEDBACK_API_KEY" in json.loads(capsys.readouterr().out)["missing_or_invalid"]


def test_main_writes_results_and_sheet_without_the_key(monkeypatch, tmp_path, capsys):
    key = KEY
    configure(monkeypatch)
    provider = scripted(good_output(), SHORT_ABSTAINS, R05_FEEDBACK, R10_FEEDBACK, runs=1)
    monkeypatch.setattr(quality_eval, "AnthropicFeedbackProvider", lambda _settings: provider)
    out = tmp_path / "out"

    assert quality_eval.main(["--runs", "1", "--out", str(out)]) == 0
    assert json.loads(capsys.readouterr().out)["result"] == "PASSED"
    results = (out / "results.json").read_text()
    assert json.loads(results)["summary"]["checks_total"] == 4
    assert key not in results and key not in (out / "review-sheet.md").read_text()
    assert provider.checks == 1
