"""Manual genuine-provider smoke check for AI feedback drafting.

NOT collected by pytest and NOT run in CI: it spends real money (one request,
bounded by the configured max output tokens). It sends ONE synthetic response
(fixture R01) with the synthetic passage through the production adapter,
prompt and validator. No database, no student data.

    cd backend
    export AEOS_AI_FEEDBACK_SMOKE=1
    export AEOS_AI_FEEDBACK_MODEL=<id confirmed in your provider console>
    export AEOS_AI_FEEDBACK_API_KEY=<server-side key>
    export AEOS_AI_FEEDBACK_INPUT_USD_PER_MTOK=<current price>
    export AEOS_AI_FEEDBACK_OUTPUT_USD_PER_MTOK=<current price>
    python -m tests.ai_feedback_provider_smoke

Exit codes: 0 the pipeline completed (any draft status, including
rejected_output, is a recorded result); 1 provider error; 2 BLOCKED (not
configured). Output is JSON without the key. A passing smoke check shows
connectivity and contract handling only, not feedback quality or accuracy.
"""

import json
import os
import sys
from pathlib import Path

from app.core.ai_feedback_settings import load_ai_feedback_settings
from app.models.ai_feedback import provider_output_json_schema
from app.services.ai_feedback.prompt import (
    PROMPT_VERSION,
    SYSTEM_INSTRUCTIONS,
    build_user_content,
    has_embedded_instructions,
)
from app.services.ai_feedback.provider import AnthropicFeedbackProvider, ProviderError
from app.services.ai_feedback.rubrics import load_registry
from app.services.ai_feedback.service import actual_microusd, reservation_microusd
from app.services.ai_feedback.validation import OutputRejected, validate_provider_output

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ai_feedback" / "synthetic_ela.json"


def main() -> int:
    settings = load_ai_feedback_settings()
    problems = [p for p in settings.configuration_errors() if p != "AEOS_AI_FEEDBACK_ENABLED"]
    if os.environ.get("AEOS_AI_FEEDBACK_SMOKE") != "1" or problems:
        print(json.dumps({"result": "BLOCKED", "missing_or_invalid": problems or ["AEOS_AI_FEEDBACK_SMOKE"]}))
        return 2

    fixture = json.loads(FIXTURE.read_text())
    response_text = fixture["responses"]["R01"]["text"]
    passage = fixture["passage"]["text"]
    rubric = load_registry()[("RUB-CER3", "0.1")]
    provider = AnthropicFeedbackProvider(settings)
    record = {"provider": provider.name, "model_id": settings.model_id, "prompt_version": PROMPT_VERSION,
              "rubric": rubric.approval_pin(), "data": "synthetic fixture R01"}
    try:
        provider.check_model(settings.model_id, settings.max_output_tokens)
        record["model_check"] = "available, structured output supported"
        user_content = build_user_content(rubric, response_text, passage)
        schema = provider_output_json_schema(list(rubric.criterion_ids))
        record["reserved_cost_microusd"] = reservation_microusd(
            settings, SYSTEM_INSTRUCTIONS, user_content, json.dumps(schema)
        )
        completion = provider.complete(
            model_id=settings.model_id, system=SYSTEM_INSTRUCTIONS, user_content=user_content,
            output_schema=schema, max_output_tokens=settings.max_output_tokens,
        )
    except ProviderError as exc:
        record.update(result="PROVIDER_ERROR", error_code=exc.code)
        print(json.dumps(record, indent=1))
        return 1

    record.update(
        response_model_id=completion.response_model_id, stop_reason=completion.stop_reason,
        input_tokens=completion.input_tokens, output_tokens=completion.output_tokens,
        actual_cost_microusd=actual_microusd(settings, completion.input_tokens, completion.output_tokens),
    )
    flags = ["possible_embedded_instructions"] if has_embedded_instructions(response_text, passage) else []
    try:
        if completion.stop_reason != "end_turn" or completion.text is None:
            raise OutputRejected(f"stop_reason_{completion.stop_reason}")
        outcome = validate_provider_output(completion.text, rubric, response_text, flags)
        record.update(result="COMPLETED", draft_status=outcome.status, review_flags=outcome.review_flags,
                      criteria=[(c.criterion_id, c.outcome, c.abstention_reason) for c in outcome.feedback.criteria],
                      draft_text=outcome.draft_text)
    except OutputRejected as exc:
        record.update(result="COMPLETED", draft_status="rejected_output", error_code=exc.code)
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
