"""Value types for the Lead Qualification + Enrollment Agent v1.

The five scored fields (intent, qualification, priority, missing_information,
next_action) are defined in docs/LEAD_QUALIFICATION_AGENT_V1_SPEC.md section 6.
This module is the single place those vocabularies are declared, so the engine,
the benchmark scorer and the tests cannot drift apart.
"""

from dataclasses import dataclass, field
from typing import List, Optional


class Intent:
    TUTORING_INQUIRY = "tutoring_inquiry"
    PRICING_INQUIRY = "pricing_inquiry"
    SCHEDULING_REQUEST = "scheduling_request"
    EXISTING_CUSTOMER = "existing_customer"
    JOB_APPLICATION = "job_application"
    SPAM = "spam"
    UNRELATED = "unrelated"
    UNCLEAR = "unclear"

    ALL = (
        TUTORING_INQUIRY,
        PRICING_INQUIRY,
        SCHEDULING_REQUEST,
        EXISTING_CUSTOMER,
        JOB_APPLICATION,
        SPAM,
        UNRELATED,
        UNCLEAR,
    )


class Qualification:
    QUALIFIED = "qualified"
    NEEDS_INFO = "needs_info"
    OUT_OF_SCOPE = "out_of_scope"
    NOT_A_LEAD = "not_a_lead"

    ALL = (QUALIFIED, NEEDS_INFO, OUT_OF_SCOPE, NOT_A_LEAD)


class Priority:
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    ALL = (URGENT, HIGH, MEDIUM, LOW)


class Field:
    """The six fields whose presence or absence the agent reports."""

    GRADE_LEVEL = "grade_level"
    SUBJECT = "subject"
    CONTACT_INFO = "contact_info"
    AVAILABILITY = "availability"
    START_TIMELINE = "start_timeline"
    LEARNING_GOAL = "learning_goal"

    # Order is fixed so that missing_information lists compare deterministically.
    ALL = (
        GRADE_LEVEL,
        SUBJECT,
        CONTACT_INFO,
        AVAILABILITY,
        START_TIMELINE,
        LEARNING_GOAL,
    )

    # Absence of any of these prevents a lead from being `qualified`.
    BLOCKING = (GRADE_LEVEL, SUBJECT, CONTACT_INFO)


class Action:
    ESCALATE_TO_HUMAN_NOW = "escalate_to_human_now"
    BOOK_CONSULTATION = "book_consultation"
    REQUEST_MISSING_INFO = "request_missing_info"
    SEND_PRICING_THEN_BOOK = "send_pricing_then_book"
    ROUTE_TO_SUPPORT = "route_to_support"
    ROUTE_TO_HIRING = "route_to_hiring"
    NURTURE_FOLLOWUP = "nurture_followup"
    DECLINE_AND_REFER = "decline_and_refer"
    ARCHIVE_NO_ACTION = "archive_no_action"

    ALL = (
        ESCALATE_TO_HUMAN_NOW,
        BOOK_CONSULTATION,
        REQUEST_MISSING_INFO,
        SEND_PRICING_THEN_BOOK,
        ROUTE_TO_SUPPORT,
        ROUTE_TO_HIRING,
        NURTURE_FOLLOWUP,
        DECLINE_AND_REFER,
        ARCHIVE_NO_ACTION,
    )


CHANNELS = (
    "web_form",
    "email",
    "sms",
    "voicemail_transcript",
    "facebook_message",
    "google_business_message",
)


@dataclass(frozen=True)
class Inquiry:
    """One inbound message. See spec section 3."""

    id: str
    channel: str
    received_at: str
    message: str
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    sender_phone: Optional[str] = None

    @classmethod
    def from_dict(cls, raw: dict) -> "Inquiry":
        missing = [k for k in ("id", "channel", "received_at", "message") if not raw.get(k)]
        if missing:
            raise ValueError(f"inquiry is missing required field(s): {', '.join(missing)}")
        if raw["channel"] not in CHANNELS:
            raise ValueError(f"unknown channel {raw['channel']!r}")
        return cls(
            id=raw["id"],
            channel=raw["channel"],
            received_at=raw["received_at"],
            message=raw["message"],
            sender_name=raw.get("sender_name"),
            sender_email=raw.get("sender_email"),
            sender_phone=raw.get("sender_phone"),
        )


@dataclass
class LeadDecision:
    """One decision record. See spec section 4."""

    id: str
    intent: str
    qualification: str
    priority: str
    missing_information: List[str]
    next_action: str
    response_draft: str = ""
    confidence: str = "high"
    rules_fired: List[str] = field(default_factory=list)

    def scored_fields(self) -> dict:
        """Only the five fields the benchmark grades."""
        return {
            "intent": self.intent,
            "qualification": self.qualification,
            "priority": self.priority,
            "missing_information": list(self.missing_information),
            "next_action": self.next_action,
        }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "intent": self.intent,
            "qualification": self.qualification,
            "priority": self.priority,
            "missing_information": list(self.missing_information),
            "next_action": self.next_action,
            "response_draft": self.response_draft,
            "confidence": self.confidence,
            "rules_fired": list(self.rules_fired),
        }
