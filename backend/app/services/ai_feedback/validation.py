"""Validate untrusted provider output before anything is stored or shown.

Order of checks:
  1. The text must be one JSON object (``malformed_output`` otherwise).
  2. It must satisfy ProviderFeedbackOutput strictly (``schema_violation``).
  3. It must cover every rubric criterion exactly once (``criteria_mismatch``).
  4. Model-authored feedback must not contain prohibited inferences or scoring
     language (``prohibited_inference``). The whole output is rejected: a
     draft that contains one is not safe to show even after redaction.
  5. Every evidence quote must occur verbatim in the student response. The
     server computes offsets. A criterion with any unverifiable quote becomes
     an abstention (``evidence_not_verified``) and the draft is flagged.

Steps 1-4 reject the output; the request is recorded as ``rejected_output``.
"""

import json
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from pydantic import ValidationError

from app.models.ai_feedback import (
    CriterionFeedback,
    EvidenceSpan,
    ProviderFeedbackOutput,
    ValidatedFeedback,
)
from app.services.ai_feedback.rubrics import Rubric

# A quote shorter than this could match almost any response by accident, so it
# cannot count as evidence unless it is the whole response.
MIN_QUOTE_CHARS = 8
VERY_SHORT_RESPONSE_CHARS = 40

# Applied to model-authored text only (strength, next_step), never to quoted
# student text: a student may legitimately write about any topic.
_PROHIBITED_PATTERNS: Tuple[Tuple[str, re.Pattern], ...] = tuple(
    (label, re.compile(pattern, flags))
    for label, pattern, flags in (
        ("condition", r"\b(adhd|attention[- ]deficit|hyperactiv\w*|dyslex\w*|dysgraph\w*|dyscalcul\w*|autis\w*|asperger\w*)\b", re.I),
        ("condition", r"\b(disabilit\w*|disabled|disorder\w*|impairment\w*|diagnos\w*|neurodiverg\w*|neurotypical)\b", re.I),
        ("placement", r"\b(special education|sped|iep|individualized education|504 plan|section 504|eligib\w*|referr(al|ed) for)\b", re.I),
        ("ability", r"\b(iq|intelligen\w*|gifted|cognitive (abilit\w*|deficit\w*|delay\w*|profile)|processing (deficit|speed|disorder)|low[- ]ability|high[- ]ability)\b", re.I),
        ("level", r"\b(reading age|reading level|lexile|grade[- ]level|grade equivalent|below grade|above grade|on grade|at grade)\b", re.I),
        ("mastery", r"\b(master(y|ed|s)?|proficien\w*|meets? (the )?standards?|exceeds? (the )?standards?|standards?[- ](aligned|compliant|compliance|mastery)|common core|ccss)\b", re.I),
        ("standard_code", r"\b(RL|RI|RF|W|SL|L)\.\d{1,2}\.\d{1,2}[a-z]?\b", 0),
        ("scoring", r"\b(score[sd]?|scoring|full (marks|points|credit)|rubric (value|level|score)|level\s*[0-9]|\d+\s*/\s*\d+\s*(points?)?|\d+\s+points?)\b", re.I),
    )
)


class OutputRejected(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ValidationOutcome:
    status: str  # "ready" or "abstained"
    feedback: ValidatedFeedback
    draft_text: Optional[str]
    review_flags: List[str]


def find_prohibited_language(text: str) -> Optional[str]:
    for label, pattern in _PROHIBITED_PATTERNS:
        if pattern.search(text):
            return label
    return None


def _locate(quote: str, response_text: str) -> Optional[EvidenceSpan]:
    if len(quote.strip()) < MIN_QUOTE_CHARS and quote != response_text:
        return None
    start = response_text.find(quote)
    if start < 0:
        return None
    return EvidenceSpan(start=start, end=start + len(quote), quote=quote)


def render_draft_text(feedback: ValidatedFeedback) -> Optional[str]:
    sections = []
    for criterion in feedback.criteria:
        if criterion.outcome != "feedback":
            continue
        lines = [f"{criterion.criterion_name}:"]
        if criterion.strength:
            lines.append(f"Strength: {criterion.strength.strip()}")
        if criterion.next_step:
            lines.append(f"Next step: {criterion.next_step.strip()}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections) if sections else None


def validate_provider_output(
    raw_text: str,
    rubric: Rubric,
    response_text: str,
    input_flags: List[str],
) -> ValidationOutcome:
    try:
        document = json.loads(raw_text)
    except (TypeError, ValueError):
        raise OutputRejected("malformed_output")
    if not isinstance(document, dict):
        raise OutputRejected("malformed_output")

    try:
        parsed = ProviderFeedbackOutput.model_validate(document)
    except ValidationError:
        raise OutputRejected("schema_violation")

    returned_ids = [criterion.criterion_id for criterion in parsed.criteria]
    if sorted(returned_ids) != sorted(rubric.criterion_ids) or len(set(returned_ids)) != len(returned_ids):
        raise OutputRejected("criteria_mismatch")

    for criterion in parsed.criteria:
        for text in (criterion.strength, criterion.next_step):
            if text and find_prohibited_language(text):
                raise OutputRejected("prohibited_inference")

    names = {criterion.id: criterion.name for criterion in rubric.criteria}
    by_id = {criterion.criterion_id: criterion for criterion in parsed.criteria}
    flags = set(input_flags) | set(parsed.review_flags)
    validated: List[CriterionFeedback] = []

    # Rubric order, not model order, so drafts read consistently.
    for criterion_id in rubric.criterion_ids:
        item = by_id[criterion_id]
        if item.outcome == "abstain":
            validated.append(
                CriterionFeedback(
                    criterion_id=criterion_id,
                    criterion_name=names[criterion_id],
                    outcome="abstain",
                    abstention_reason=item.abstention_reason,
                )
            )
            continue

        spans = [_locate(quote, response_text) for quote in item.evidence_quotes]
        if any(span is None for span in spans):
            flags.add("unverified_evidence_removed")
            validated.append(
                CriterionFeedback(
                    criterion_id=criterion_id,
                    criterion_name=names[criterion_id],
                    outcome="abstain",
                    abstention_reason="evidence_not_verified",
                )
            )
            continue

        validated.append(
            CriterionFeedback(
                criterion_id=criterion_id,
                criterion_name=names[criterion_id],
                outcome="feedback",
                strength=(item.strength or "").strip() or None,
                next_step=(item.next_step or "").strip() or None,
                evidence=spans,
            )
        )

    feedback = ValidatedFeedback(overall_abstention=parsed.overall_abstention, criteria=validated)
    abstained = [criterion for criterion in validated if criterion.outcome == "abstain"]
    if len(response_text.strip()) < VERY_SHORT_RESPONSE_CHARS:
        flags.add("very_short_response")
    if abstained and len(abstained) < len(validated):
        flags.add("partial_abstention")

    status = "abstained" if len(abstained) == len(validated) else "ready"
    return ValidationOutcome(
        status=status,
        feedback=feedback,
        draft_text=render_draft_text(feedback) if status == "ready" else None,
        review_flags=sorted(flags),
    )
