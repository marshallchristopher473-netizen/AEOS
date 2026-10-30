"""Loopback-only browser fixture for the AI feedback panel.

Production routes, services, validation and schemas with synthetic sessions,
in-memory storage and a DETERMINISTIC FIXTURE provider (no network, no model).
Run explicitly with AEOS_SYNTHETIC_AI_FEEDBACK=1. Never deploy this server.
"""
import json
import os
from decimal import Decimal

from app.core.ai_feedback_settings import AiFeedbackSettings, get_ai_feedback_settings
from app.core.auth import get_current_user
from app.main import app
from app.services.ai_feedback.provider import ProviderCompletion, get_feedback_provider_factory
from app.services.ai_feedback.rubrics import load_registry
from app.services.supabase_service import get_supabase_admin_client
from tests import supabase_auth_fixture
from tests.fakes import ORG_A, ORG_B
from tests.review_fixture_server import database, synthetic_session

RUBRIC = load_registry()[("RUB-CER3", "0.1")]
SETTINGS = AiFeedbackSettings(
    enabled=True,
    model_id="deterministic-fixture",
    api_key="synthetic-fixture-key",
    input_usd_per_mtok=Decimal("4"),
    output_usd_per_mtok=Decimal("20"),
    organization_allowlist=frozenset({ORG_A, ORG_B}),
    approved_rubrics=frozenset({RUBRIC.approval_pin()}),
)


class DeterministicFixtureProvider:
    """Quotes the start of the response for C1 and C2 and abstains on C3."""

    name = "fixture"

    def check_model(self, model_id, required_output_tokens):
        return None

    def complete(self, *, user_content, **_kwargs):
        block = user_content.split("<untrusted_input_json>\n", 1)[1].split("\n</untrusted_input_json>", 1)[0]
        response = json.loads(block)["student_response"]
        quote = response[: min(len(response), 30)]
        if len(response.strip()) < 12:
            output = {
                "overall_abstention": "insufficient_response",
                "criteria": [
                    {"criterion_id": cid, "outcome": "abstain", "strength": None, "next_step": None,
                     "evidence_quotes": [], "abstention_reason": "insufficient_response"}
                    for cid in RUBRIC.criterion_ids
                ],
                "review_flags": ["very_short_response"],
            }
        else:
            output = {
                "overall_abstention": None,
                "criteria": [
                    {"criterion_id": "C1", "outcome": "feedback", "strength": "You open with a clear statement.",
                     "next_step": "Name the benefit in one precise phrase.", "evidence_quotes": [quote],
                     "abstention_reason": None},
                    {"criterion_id": "C2", "outcome": "feedback", "strength": None,
                     "next_step": "Quote a detail from the passage.", "evidence_quotes": ["invented passage detail"],
                     "abstention_reason": None},
                    {"criterion_id": "C3", "outcome": "abstain", "strength": None, "next_step": None,
                     "evidence_quotes": [], "abstention_reason": "not_assessable_from_response"},
                ],
                "review_flags": [],
            }
        return ProviderCompletion(
            text=json.dumps(output), response_model_id="deterministic-fixture",
            stop_reason="end_turn", input_tokens=900, output_tokens=200,
        )


if __name__ == "__main__":
    if os.environ.get("AEOS_SYNTHETIC_AI_FEEDBACK") != "1":
        raise SystemExit("This synthetic fixture requires AEOS_SYNTHETIC_AI_FEEDBACK=1")
    import uvicorn

    provider = DeterministicFixtureProvider()
    app.dependency_overrides[get_current_user] = synthetic_session
    app.dependency_overrides[get_supabase_admin_client] = lambda: database
    app.dependency_overrides[get_ai_feedback_settings] = lambda: SETTINGS
    app.dependency_overrides[get_feedback_provider_factory] = lambda: (lambda _settings: provider)
    supabase_auth_fixture.start_in_background()
    uvicorn.run(app, host="127.0.0.1", port=8000)
