"""The v1 rule engine.

Implements the decision rubric in docs/LEAD_QUALIFICATION_AGENT_V1_SPEC.md
section 6. Every branch appends a rule ID to `rules_fired`, so any benchmark
failure can be traced to the exact rule that produced it.

Deterministic and dependency-free by design (spec section 2).
"""

import re
from typing import List, Optional, Tuple

from . import extract, profile
from .responses import draft_response
from .schema import Action, Field, Inquiry, LeadDecision, Priority, Qualification, Intent

# Messages shorter than this with no classifiable signal are `unclear`
# rather than `unrelated` — too thin to judge, so worth a reply.
UNCLEAR_WORD_LIMIT = 8

URGENT_DEADLINE_DAYS = 10
HIGH_DEADLINE_DAYS = 30


# --------------------------------------------------------------------------
# signal detection
# --------------------------------------------------------------------------

SPAM_MARKERS = (
    "seo", "page 1 of google", "ranking on page", "rank higher", "free audit",
    "lead generation", "verified database", "rate card", "portfolio",
    "offshore", "engineers available", "trading bot", "crypto", "forfeit",
    "claim your award", "click the secure link", "verify your banking",
    "grant", "guaranteed", "300% more", "limited spots", "no experience required",
    "could not be delivered", "update your address", "mailinator",
    "15 minute call", "free mockup", "i build sites", "we can build your",
    "million parent contacts", "sample list", "dear sir or madam",
)

JOB_MARKERS = (
    "are you hiring", "are u hiring", "accepting applications", "my resume",
    "attached my resume", "my cv", "send my cv", "job board", "job posting",
    "your posting", "tutoring work", "contract tutoring", "part-time tutoring work",
    "apply", "application materials", "looking for work", "seeking a position",
    "student teaching", "ive tutored", "i have tutored", "interested in working",
)

EXISTING_CUSTOMER_MARKERS = (
    "our session", "our sessions", "his session", "her session", "their session",
    "our standing", "our tutor", "we have been working with", "been working with",
    "we have been with you", "since last spring", "our next session",
    "last thursday's session", "make it up", "our monthly invoice",
    "receipts for our", "we got charged", "got charged twice", "charged twice",
    "cancel our sessions", "our card", "his tutor", "her tutor",
    "wont be able to make", "won't be able to make",
)

EXISTING_CUSTOMER_URGENT_MARKERS = (
    "charged twice", "double charged", "charged us twice", "overcharged",
    "refund", "billing error", "wrong amount",
    "cancel our sessions", "need to cancel", "want to cancel",
    "came home upset", "was upset", "complaint", "not trying",
    "inappropriate", "unsafe",
)

SCHEDULING_MARKERS = (
    "book a consultation", "book a consult", "schedule a consultation",
    "set up a consultation", "set up an initial consultation",
    "initial consultation", "the consultation i requested", "consultation i requested",
    "get something on the calendar", "on the calendar", "when we can meet",
    "reschedule", "move tomorrows", "move tomorrow's", "move our consult",
    "move the consult", "same time", "i filled out your form",
    "like to book", "would like to set up",
)

PRICE_TOKENS = (
    "how much", "rate", "rates", "cost", "price", "prices", "pricing",
    "charge", "charges", "fee", "fees", "package", "packages", "hourly",
    "sliding scale", "financial assistance", "price match", "cheapest",
    "pay as you go", "minimum commitment", "afford",
)

PRICE_QUESTION_LEAD_INS = (
    "like to know", "want to know", "need to understand", "tell me", "send me",
    "curious about", "wondering about", "understand the", "need to know",
)

BUYING_SIGNALS = (
    "how do i sign up", "next step to sign up", "ready to enroll", "want to enroll",
    "enrollment process", "whats the enrollment", "what's the enrollment",
    "send me whatever paperwork", "send me the contract", "sign up", "enroll",
)

START_NOW_SIGNALS = (
    "asap", "as soon as possible", "right away", "immediately",
    "start this week", "started this week", "begin this week",
    "start right away", "begin immediately", "get her started",
    "get him started", "get them started", "start as soon", "ideally this week",
    "want to get started", "ready to get started", "like to get started",
)

GO_ELSEWHERE_SIGNALS = (
    "nobody called me back", "no one called me back", "nobody has reached out",
    "no one has reached out", "nobody got back", "called three places",
    "called a few places", "rather know now", "same as the rest",
)

DEFERRAL_SIGNALS = (
    "next semester", "next year", "after the holidays", "maybe next month",
    "in the spring", "in the fall semester", "once we are settled",
    "start in november", "start in december", "start in january",
    "start in february", "would want to start in",
)

OFF_TOPIC_MARKERS = (
    "towed", "parking lot", "farmers market", "wrong number", "donation",
    "donations", "newsletter", "community list", "supply drive",
)


def _contains_any(norm: str, markers) -> Optional[str]:
    """Whole-phrase matching.

    Plain substring matching is not safe here: "one of your tutors" contains
    "our tutor", and "dual-enrollment" contains "enroll". Both turned ordinary
    inquiries into false existing-customer and buying signals, so every marker
    is anchored at both ends.
    """
    for marker in markers:
        if re.search(rf"(?<![a-z0-9]){re.escape(marker)}(?![a-z0-9])", norm):
            return marker
    return None


def _has_price_ask(message: str) -> bool:
    """A price *question*, not a passing mention of money.

    "What do you charge?" is a pricing inquiry. "We're on a fixed income, so
    cost matters" is a parent explaining their situation.
    """
    norm = extract._norm(message)
    for sentence in extract.sentences(norm):
        if not any(re.search(rf"(?<![a-z]){re.escape(t)}(?![a-z])", sentence)
                   for t in PRICE_TOKENS):
            continue
        if sentence.rstrip().endswith("?"):
            return True
        if re.match(r"^(what|whats|what's|how|do you|does it|is there|are there|any)\b",
                    sentence.strip()):
            return True
        if any(lead in sentence for lead in PRICE_QUESTION_LEAD_INS):
            return True
    return False


def _has_tutoring_signal(message: str) -> bool:
    norm = extract._norm(message)
    if any(word in norm for word in extract.TUTORING_WORDS):
        return True
    if any(ref in norm for ref in extract.CHILD_REFERENCES):
        return True
    return bool(extract.detect_grades(message))


# --------------------------------------------------------------------------
# intent
# --------------------------------------------------------------------------

def classify_intent(inquiry: Inquiry) -> Tuple[str, List[str]]:
    """Spec section 6.1, applied in the documented precedence order."""
    norm = extract._norm(inquiry.message)
    rules: List[str] = []

    if _contains_any(norm, EXISTING_CUSTOMER_MARKERS):
        rules.append("INT-01")
        return Intent.EXISTING_CUSTOMER, rules

    if _contains_any(norm, SCHEDULING_MARKERS):
        rules.append("INT-02")
        return Intent.SCHEDULING_REQUEST, rules

    if _contains_any(norm, JOB_MARKERS):
        rules.append("INT-03")
        return Intent.JOB_APPLICATION, rules

    if _contains_any(norm, SPAM_MARKERS):
        rules.append("INT-04")
        return Intent.SPAM, rules

    if re.search(r"https?://|hxxp://", norm) and not _has_tutoring_signal(inquiry.message):
        rules.append("INT-05")
        return Intent.SPAM, rules

    # Checked before the tutoring-signal gate: "how much do you charge per
    # hour?" names no child and no subject, but a price question put to a
    # tutoring business is a pricing inquiry, not an unclassifiable message.
    if _has_price_ask(inquiry.message):
        rules.append("INT-08")
        return Intent.PRICING_INQUIRY, rules

    if not _has_tutoring_signal(inquiry.message):
        if _contains_any(norm, OFF_TOPIC_MARKERS) or \
                extract.word_count(inquiry.message) >= UNCLEAR_WORD_LIMIT:
            rules.append("INT-06")
            return Intent.UNRELATED, rules
        rules.append("INT-07")
        return Intent.UNCLEAR, rules

    rules.append("INT-09")
    return Intent.TUTORING_INQUIRY, rules


# --------------------------------------------------------------------------
# scope and qualification
# --------------------------------------------------------------------------

def _out_of_scope_reason(inquiry: Inquiry) -> Optional[str]:
    """Spec section 5 exclusions. Returns a short reason, or None if in scope."""
    norm = extract._norm(inquiry.message)

    for pattern in profile.INTEGRITY_VIOLATION_PATTERNS:
        if re.search(pattern, norm):
            return "academic_integrity"

    excluded = extract.detect_excluded_subject(inquiry.message)
    if excluded:
        return f"subject_not_offered:{excluded}"

    grades = extract.detect_grades(inquiry.message)
    if _contains_any(norm, profile.ADULT_LEARNER_KEYWORDS) or extract.detect_adult_age(inquiry.message):
        return "adult_learner"

    # "College-level" only puts a request out of scope when no K-12 student is
    # named. A 10th grader in dual-enrollment College Algebra is still K-12.
    if _contains_any(norm, profile.POST_SECONDARY_KEYWORDS) and not grades:
        return "post_secondary"

    return None


def qualify(inquiry: Inquiry, intent: str) -> Tuple[str, List[str], List[str]]:
    """Returns (qualification, missing_information, rules_fired)."""
    rules: List[str] = []

    if intent in (Intent.SPAM, Intent.UNRELATED, Intent.JOB_APPLICATION):
        rules.append("QUAL-01")
        return Qualification.NOT_A_LEAD, [], rules

    scope_reason = _out_of_scope_reason(inquiry)
    if scope_reason:
        rules.append("QUAL-02")
        return Qualification.OUT_OF_SCOPE, [], rules

    if intent == Intent.EXISTING_CUSTOMER:
        rules.append("QUAL-03")
        return Qualification.QUALIFIED, [], rules

    missing = detect_missing_information(inquiry)

    if intent == Intent.SCHEDULING_REQUEST:
        # A booked prospect is qualified by virtue of the booking, but the
        # record may still be thin, so missing fields are still reported.
        rules.append("QUAL-04")
        return Qualification.QUALIFIED, missing, rules

    blocking_missing = [f for f in missing if f in Field.BLOCKING]
    if blocking_missing:
        rules.append("QUAL-05")
        return Qualification.NEEDS_INFO, missing, rules

    rules.append("QUAL-06")
    return Qualification.QUALIFIED, missing, rules


def detect_missing_information(inquiry: Inquiry) -> List[str]:
    """Spec section 6.4, evaluated in the fixed field order."""
    has_deadline = extract.deadline_in_days(
        inquiry.message, inquiry.received_at) is not None
    present = {
        Field.GRADE_LEVEL: extract.has_grade_level(inquiry.message),
        Field.SUBJECT: extract.has_subject(inquiry.message),
        Field.CONTACT_INFO: extract.has_contact_info(
            inquiry.message, inquiry.sender_email, inquiry.sender_phone),
        Field.AVAILABILITY: extract.has_availability(inquiry.message),
        Field.START_TIMELINE: extract.has_start_timeline(inquiry.message),
        Field.LEARNING_GOAL: extract.has_learning_goal(inquiry.message, has_deadline),
    }
    return [name for name in Field.ALL if not present[name]]


# --------------------------------------------------------------------------
# priority
# --------------------------------------------------------------------------

def prioritize(inquiry: Inquiry, intent: str, qualification: str) -> Tuple[str, List[str]]:
    """Spec section 6.3, evaluated top-down."""
    norm = extract._norm(inquiry.message)
    rules: List[str] = []

    # Checked first so that no spam, job application, unrelated message or
    # out-of-scope request can ever be escalated by urgency language it
    # happens to contain ("URGENT: your package could not be delivered").
    if qualification in (Qualification.NOT_A_LEAD, Qualification.OUT_OF_SCOPE):
        rules.append("PRI-01")
        return Priority.LOW, rules

    if intent == Intent.EXISTING_CUSTOMER and _contains_any(norm, EXISTING_CUSTOMER_URGENT_MARKERS):
        rules.append("PRI-02")
        return Priority.URGENT, rules

    days = extract.deadline_in_days(inquiry.message, inquiry.received_at)
    if days is not None and days <= URGENT_DEADLINE_DAYS:
        rules.append("PRI-03")
        return Priority.URGENT, rules

    if days is not None and days <= HIGH_DEADLINE_DAYS:
        rules.append("PRI-04")
        return Priority.HIGH, rules

    if intent == Intent.EXISTING_CUSTOMER:
        rules.append("PRI-05")
        return Priority.HIGH, rules

    if intent == Intent.SCHEDULING_REQUEST:
        rules.append("PRI-06")
        return Priority.HIGH, rules

    if _contains_any(norm, GO_ELSEWHERE_SIGNALS):
        rules.append("PRI-07")
        return Priority.HIGH, rules

    if _contains_any(norm, BUYING_SIGNALS) or _contains_any(norm, START_NOW_SIGNALS):
        rules.append("PRI-08")
        return Priority.HIGH, rules

    if _contains_any(norm, DEFERRAL_SIGNALS):
        rules.append("PRI-09")
        return Priority.LOW, rules

    if intent == Intent.PRICING_INQUIRY:
        rules.append("PRI-10")
        return Priority.LOW, rules

    rules.append("PRI-11")
    return Priority.MEDIUM, rules


# --------------------------------------------------------------------------
# next action
# --------------------------------------------------------------------------

def choose_action(inquiry: Inquiry, intent: str, qualification: str,
                  priority: str) -> Tuple[str, List[str]]:
    """Spec section 6.5, including its precedence rules."""
    norm = extract._norm(inquiry.message)
    rules: List[str] = []

    if priority == Priority.URGENT:
        rules.append("ACT-01")
        return Action.ESCALATE_TO_HUMAN_NOW, rules

    if intent == Intent.JOB_APPLICATION:
        rules.append("ACT-02")
        return Action.ROUTE_TO_HIRING, rules

    if qualification == Qualification.NOT_A_LEAD:
        rules.append("ACT-03")
        return Action.ARCHIVE_NO_ACTION, rules

    if qualification == Qualification.OUT_OF_SCOPE:
        rules.append("ACT-04")
        return Action.DECLINE_AND_REFER, rules

    if intent == Intent.EXISTING_CUSTOMER:
        rules.append("ACT-05")
        return Action.ROUTE_TO_SUPPORT, rules

    # Precedence rule 2: answer the price question even when the record is thin.
    if intent == Intent.PRICING_INQUIRY:
        rules.append("ACT-06")
        return Action.SEND_PRICING_THEN_BOOK, rules

    if _contains_any(norm, DEFERRAL_SIGNALS):
        rules.append("ACT-07")
        return Action.NURTURE_FOLLOWUP, rules

    if qualification == Qualification.NEEDS_INFO:
        rules.append("ACT-08")
        return Action.REQUEST_MISSING_INFO, rules

    rules.append("ACT-09")
    return Action.BOOK_CONSULTATION, rules


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def analyze(inquiry: Inquiry) -> LeadDecision:
    """Read one inquiry, return one decision record. Sends nothing."""
    intent, intent_rules = classify_intent(inquiry)
    qualification, missing, qual_rules = qualify(inquiry, intent)
    priority, priority_rules = prioritize(inquiry, intent, qualification)
    action, action_rules = choose_action(inquiry, intent, qualification, priority)

    rules = intent_rules + qual_rules + priority_rules + action_rules

    decision = LeadDecision(
        id=inquiry.id,
        intent=intent,
        qualification=qualification,
        priority=priority,
        missing_information=missing,
        next_action=action,
        confidence="low" if intent == Intent.UNCLEAR else "high",
        rules_fired=rules,
    )
    decision.response_draft = draft_response(inquiry, decision)
    return decision


def analyze_dict(raw: dict) -> dict:
    """Convenience wrapper for callers working in plain JSON."""
    return analyze(Inquiry.from_dict(raw)).to_dict()
