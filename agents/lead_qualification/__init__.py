"""Lead Qualification + Enrollment Agent v1.

Reads one inbound parent inquiry and returns a structured decision:
intent, qualification, priority, missing information, recommended next action,
and a response draft for a human to review.

The agent never contacts anyone. See docs/LEAD_QUALIFICATION_AGENT_V1_SPEC.md.
"""

from .agent import analyze, analyze_dict
from .schema import (
    Action,
    Field,
    Inquiry,
    Intent,
    LeadDecision,
    Priority,
    Qualification,
)

__all__ = [
    "analyze",
    "analyze_dict",
    "Action",
    "Field",
    "Inquiry",
    "Intent",
    "LeadDecision",
    "Priority",
    "Qualification",
]

__version__ = "1.0.0"
