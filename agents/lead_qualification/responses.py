"""Response drafts.

These are suggestions for a human to review and send. The agent never sends
anything — see spec section 2 ("explicitly out of scope").

Drafts are templates rather than generated text, deliberately: v1's evidence
claim is about the five deterministic decision fields, and a template keeps the
benchmark reproducible at zero cost. Replacing this module with an LLM call is
the first planned upgrade once a shadow pilot shows phrasing is the weak link
(spec section 9).
"""

from typing import List

from .profile import BUSINESS_NAME
from .schema import Action, Field, Inquiry, LeadDecision

FIELD_PROMPTS = {
    Field.GRADE_LEVEL: "what grade your child is in",
    Field.SUBJECT: "which subject they need help with",
    Field.CONTACT_INFO: "the best phone number or email to reach you",
    Field.AVAILABILITY: "which days and times generally work for you",
    Field.START_TIMELINE: "when you would like to begin",
    Field.LEARNING_GOAL: "what you would most like to see change",
}


def _greeting(inquiry: Inquiry) -> str:
    if inquiry.sender_name:
        first = inquiry.sender_name.split()[0].rstrip(".,")
        if first.lower() in ("dr", "mr", "mrs", "ms") and len(inquiry.sender_name.split()) > 1:
            first = inquiry.sender_name.split()[1]
        return f"Hi {first},"
    return "Hi there,"


def _ask_list(missing: List[str], limit: int = 3) -> str:
    prompts = [FIELD_PROMPTS[f] for f in missing if f in FIELD_PROMPTS][:limit]
    if not prompts:
        return ""
    if len(prompts) == 1:
        return prompts[0]
    return ", ".join(prompts[:-1]) + ", and " + prompts[-1]


def draft_response(inquiry: Inquiry, decision: LeadDecision) -> str:
    """Return a reply a human can review, edit and send."""
    greeting = _greeting(inquiry)
    action = decision.next_action

    if action == Action.ESCALATE_TO_HUMAN_NOW:
        return (
            f"{greeting} thank you for reaching out, and I can hear the time "
            f"pressure. I am flagging this for our director right now so we can "
            f"get you an answer today rather than tomorrow. "
            f"[INTERNAL: time-critical — a person must review and reply before "
            f"anything is sent.]"
        )

    if action == Action.BOOK_CONSULTATION:
        follow_up = _ask_list(decision.missing_information, limit=2)
        tail = f" It would also help to know {follow_up}." if follow_up else ""
        return (
            f"{greeting} thank you for reaching out to {BUSINESS_NAME}. Based on "
            f"what you have described, the next step is a short consultation so we "
            f"can match your child with the right tutor. Would either of the times "
            f"below work?{tail}\n\n"
            f"[INSERT TWO CONSULTATION TIMES]"
        )

    if action == Action.REQUEST_MISSING_INFO:
        asks = _ask_list(decision.missing_information)
        return (
            f"{greeting} thank you for reaching out to {BUSINESS_NAME}. I would "
            f"like to point you to the right tutor rather than a generic answer, "
            f"so could you tell me {asks}? Once I have that I can suggest a couple "
            f"of consultation times."
        )

    if action == Action.SEND_PRICING_THEN_BOOK:
        asks = _ask_list(decision.missing_information, limit=2)
        tail = f" If you can also tell me {asks}, I can be more specific." if asks else ""
        return (
            f"{greeting} happy to give you our rates up front.\n\n"
            f"[INSERT CURRENT RATE SHEET]\n\n"
            f"Most families start with a free consultation so we can confirm what "
            f"level of support is actually needed before committing to anything.{tail}"
        )

    if action == Action.ROUTE_TO_SUPPORT:
        return (
            f"{greeting} thank you for letting us know. I am passing this to the "
            f"team member who handles your account and you will hear back shortly. "
            f"[INTERNAL: existing family — route to client support, not to sales.]"
        )

    if action == Action.ROUTE_TO_HIRING:
        return (
            f"{greeting} thank you for your interest in tutoring with "
            f"{BUSINESS_NAME}. I am forwarding your note to the person who "
            f"handles hiring. [INTERNAL: applicant — route to hiring, do not "
            f"enter into the lead pipeline.]"
        )

    if action == Action.NURTURE_FOLLOWUP:
        return (
            f"{greeting} thank you for reaching out. It sounds like the timing is "
            f"a little further out, which is completely fine. I will make a note to "
            f"check back in closer to when you would like to start, and you are "
            f"welcome to reach out sooner if anything changes. "
            f"[INTERNAL: schedule a follow-up for the stated start window.]"
        )

    if action == Action.DECLINE_AND_REFER:
        return (
            f"{greeting} thank you for thinking of us. This one falls outside what "
            f"we take on, so I would rather tell you now than waste your time. "
            f"[INTERNAL: out of scope — decline politely; refer out only if we "
            f"have a genuine referral, and never for requests we decline on "
            f"academic-integrity grounds.]"
        )

    if action == Action.ARCHIVE_NO_ACTION:
        return "[INTERNAL: no reply needed — archive.]"

    return "[INTERNAL: no draft available for this action.]"
