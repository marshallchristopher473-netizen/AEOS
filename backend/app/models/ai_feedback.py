"""Request, response and provider-output contracts for AI feedback drafting.

Reconstructed: the original module was never committed because the repository
root ``.gitignore`` rule ``models/`` ignored ``backend/app/models/``. This file
is rebuilt from every caller (routes, service, validation, tests, frontend
types and the documented contract examples); the tests are the authority.

Three distinct things are kept apart here and must not be conflated:

* A rubric value (``0``, ``1``, ``2``, ``IE``) is a teacher's scoring
  judgment. The AI never produces one; nothing in this module carries a score.
* ``outcome == "abstain"`` is the AI declining to draft feedback for one
  criterion. It is not a score, it is not ``0`` and it is not ``IE``.
* ``evidence_not_verified`` is set only by the server when a quote is not in
  the response. The model cannot claim it.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_RESPONSE_CHARS = 4000
MAX_SOURCE_CHARS = 6000
MAX_APPROVED_TEXT_CHARS = 6000
MAX_FEEDBACK_CHARS = 600
MAX_QUOTE_CHARS = 600
MAX_QUOTES_PER_CRITERION = 3
MAX_CRITERIA = 20

# Reasons the model may give for abstaining on one criterion.
ModelAbstentionReason = Literal["insufficient_response", "off_task", "not_assessable_from_response"]
# Reasons that may appear in a stored draft: the model's, plus the server's.
AbstentionReason = Literal[
    "insufficient_response", "off_task", "not_assessable_from_response", "evidence_not_verified"
]
# Whole-response abstention. Off-task responses are expressed per criterion
# (``off_task``) plus the ``off_topic`` flag, not as an overall abstention.
OverallAbstention = Literal["insufficient_response", "not_assessable_from_response"]
# Flags the model may raise. Server-only flags (``unverified_evidence_removed``,
# ``partial_abstention``) are added after validation.
ModelReviewFlag = Literal[
    "needs_teacher_judgment", "possible_embedded_instructions", "very_short_response", "off_topic"
]
DraftStatus = Literal["ready", "abstained", "rejected_output", "provider_error", "provider_refused"]
Decision = Literal["accepted", "revised", "rejected"]


def _blank_to_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return value if value.strip() else None


# ---------------------------------------------------------------------------
# Untrusted provider output.
# ---------------------------------------------------------------------------


class ProviderCriterionOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    criterion_id: str = Field(..., min_length=1, max_length=64)
    outcome: Literal["feedback", "abstain"]
    strength: Optional[str] = Field(default=None, max_length=MAX_FEEDBACK_CHARS)
    next_step: Optional[str] = Field(default=None, max_length=MAX_FEEDBACK_CHARS)
    evidence_quotes: List[str] = Field(default_factory=list, max_length=MAX_QUOTES_PER_CRITERION)
    abstention_reason: Optional[ModelAbstentionReason] = None

    @field_validator("evidence_quotes")
    @classmethod
    def _quotes_are_bounded(cls, quotes: List[str]) -> List[str]:
        if any(not quote or len(quote) > MAX_QUOTE_CHARS for quote in quotes):
            raise ValueError("evidence quotes must be non-empty and bounded")
        return quotes

    @model_validator(mode="after")
    def _shape_matches_outcome(self) -> "ProviderCriterionOutput":
        if self.outcome == "feedback":
            if not self.evidence_quotes:
                raise ValueError("feedback requires at least one evidence quote")
            if self.abstention_reason is not None:
                raise ValueError("feedback cannot carry an abstention reason")
            if _blank_to_none(self.strength) is None and _blank_to_none(self.next_step) is None:
                raise ValueError("feedback requires a strength or a next step")
        else:
            if self.abstention_reason is None:
                raise ValueError("an abstention requires a reason")
            if self.evidence_quotes or _blank_to_none(self.strength) or _blank_to_none(self.next_step):
                raise ValueError("an abstention carries no feedback or evidence")
        return self


class ProviderFeedbackOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    overall_abstention: Optional[OverallAbstention] = None
    criteria: List[ProviderCriterionOutput] = Field(..., min_length=1, max_length=MAX_CRITERIA)
    review_flags: List[ModelReviewFlag] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def _overall_abstention_is_consistent(self) -> "ProviderFeedbackOutput":
        if self.overall_abstention is not None and any(c.outcome != "abstain" for c in self.criteria):
            raise ValueError("an overall abstention requires every criterion to abstain")
        return self


def provider_output_json_schema(criterion_ids: List[str]) -> dict:
    """Structured-output schema sent to the provider.

    Kept to keywords that structured-output modes broadly support (types,
    enums, required, additionalProperties). It is a guide for the model only:
    ``ProviderFeedbackOutput`` and ``validate_provider_output`` are the
    authority, and every bound is re-checked there.
    """
    nullable_text = {"anyOf": [{"type": "string"}, {"type": "null"}]}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["overall_abstention", "criteria", "review_flags"],
        "properties": {
            "overall_abstention": {
                "anyOf": [
                    {"type": "string", "enum": list(OverallAbstention.__args__)},
                    {"type": "null"},
                ]
            },
            "criteria": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "criterion_id", "outcome", "strength", "next_step",
                        "evidence_quotes", "abstention_reason",
                    ],
                    "properties": {
                        "criterion_id": {"type": "string", "enum": list(criterion_ids)},
                        "outcome": {"type": "string", "enum": ["feedback", "abstain"]},
                        "strength": nullable_text,
                        "next_step": nullable_text,
                        "evidence_quotes": {"type": "array", "items": {"type": "string"}},
                        "abstention_reason": {
                            "anyOf": [
                                {"type": "string", "enum": list(ModelAbstentionReason.__args__)},
                                {"type": "null"},
                            ]
                        },
                    },
                },
            },
            "review_flags": {
                "type": "array",
                "items": {"type": "string", "enum": list(ModelReviewFlag.__args__)},
            },
        },
    }


# ---------------------------------------------------------------------------
# Server-validated draft content.
# ---------------------------------------------------------------------------


class EvidenceSpan(BaseModel):
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    quote: str


class CriterionFeedback(BaseModel):
    criterion_id: str
    criterion_name: str
    outcome: Literal["feedback", "abstain"]
    strength: Optional[str] = None
    next_step: Optional[str] = None
    evidence: List[EvidenceSpan] = Field(default_factory=list)
    abstention_reason: Optional[AbstentionReason] = None


class ValidatedFeedback(BaseModel):
    overall_abstention: Optional[OverallAbstention] = None
    criteria: List[CriterionFeedback]


# ---------------------------------------------------------------------------
# HTTP contracts.
# ---------------------------------------------------------------------------


class AiFeedbackDraftCreateRequest(BaseModel):
    """Organization, student, author, model and instructions are never
    accepted from the client; ``extra="forbid"`` rejects any attempt."""

    model_config = ConfigDict(extra="forbid")

    assessment_id: str = Field(..., min_length=1, max_length=64)
    rubric_id: str = Field(..., min_length=1, max_length=64)
    rubric_version: str = Field(..., min_length=1, max_length=32)
    response_text: str = Field(..., min_length=1, max_length=MAX_RESPONSE_CHARS)
    source_text: Optional[str] = Field(default=None, min_length=1, max_length=MAX_SOURCE_CHARS)
    data_classification: Literal["synthetic"]

    @field_validator("response_text")
    @classmethod
    def _response_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("response_text must contain non-whitespace text")
        return value


class AiFeedbackDecisionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Decision
    approved_text: Optional[str] = Field(default=None, min_length=1, max_length=MAX_APPROVED_TEXT_CHARS)
    review_flags_acknowledged: bool = False
    # Must be sent as an explicit true by a teacher action.
    teacher_confirmed: Literal[True]

    @model_validator(mode="after")
    def _text_matches_decision(self) -> "AiFeedbackDecisionCreateRequest":
        if self.decision == "rejected":
            if self.approved_text is not None:
                raise ValueError("a rejection carries no approved text")
        elif self.approved_text is None or not self.approved_text.strip():
            raise ValueError("accepted and revised decisions require approved text")
        return self


class AiFeedbackDecisionResponse(BaseModel):
    id: str
    organization_id: str
    draft_id: str
    decided_by: str
    decision: Decision
    approved_text: Optional[str] = None
    review_flags_acknowledged: bool
    teacher_confirmed: bool
    created_at: Optional[str] = None


class AiFeedbackDraftResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: str
    organization_id: str
    request_id: str
    assessment_id: str
    student_id: str
    requested_by: str
    status: DraftStatus
    feedback: Optional[ValidatedFeedback] = None
    draft_text: Optional[str] = None
    review_flags: List[str] = Field(default_factory=list)
    error_code: Optional[str] = None
    response_text: str
    provider: str
    model_id: str
    response_model_id: Optional[str] = None
    prompt_version: str
    rubric_id: str
    rubric_version: str
    rubric_sha256: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    actual_cost_microusd: int = 0
    data_classification: str
    decisions: List[AiFeedbackDecisionResponse] = Field(default_factory=list)
    current_decision: Optional[AiFeedbackDecisionResponse] = None
    created_at: Optional[str] = None
