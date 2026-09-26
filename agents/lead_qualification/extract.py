"""Field detection for the six fields in spec section 6.4, plus the supporting
signals (deadlines, buying signals, spam markers) the rule engine needs.

Everything here is pure text analysis over the standard library. No network
calls, no third-party dependencies, no model inference.
"""

import re
from datetime import date, datetime
from typing import List, Optional

from . import profile

# --------------------------------------------------------------------------
# small shared vocabularies
# --------------------------------------------------------------------------

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "a": 1, "an": 1, "couple": 2, "few": 3,
}

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday",
            "saturday", "sunday")

HIGH_SCHOOL_YEARS = {"freshman": 9, "sophomore": 10, "junior": 11, "senior": 12}

CHILD_REFERENCES = (
    "my son", "my daughter", "my child", "my kid", "my kids", "my children",
    "my twins", "my grandson", "my granddaughter", "my nephew", "my niece",
    "my student", "her son", "his son", "grader", "grade", "student", "students",
)

TUTORING_WORDS = (
    "tutor", "tutors", "tutoring", "tutored", "lesson", "lessons",
    "instruction", "teach", "help with", "helps with", "sessions",
)


def _norm(text: str) -> str:
    """Lowercase and collapse the punctuation that trips up literal matching."""
    lowered = text.lower()
    lowered = lowered.replace("’", "'").replace("‘", "'")
    lowered = lowered.replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", lowered)


def sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def word_count(text: str) -> int:
    return len(re.findall(r"[a-z0-9']+", _norm(text)))


# --------------------------------------------------------------------------
# grade level and age
# --------------------------------------------------------------------------

_GRADE_PATTERNS = (
    re.compile(r"\b(\d{1,2})\s*(?:st|nd|rd|th)\s*[- ]?\s*grade"),
    re.compile(r"\b(\d{1,2})\s*(?:st|nd|rd|th)\s*[- ]?\s*grader"),
    re.compile(r"\bgrade\s*(\d{1,2})\b"),
    re.compile(r"\bin\s+grade\s+(\d{1,2})\b"),
    # "she's in 11th", "he's in 4th" — the word "grade" is often dropped.
    re.compile(r"\bin\s+(\d{1,2})(?:st|nd|rd|th)\b"),
)

_AGE_PATTERNS = (
    re.compile(r"\b(\d{1,2})\s*[- ]?\s*year[- ]?old\b"),
    re.compile(r"\bis\s+(\d{1,2})\s+and\b"),
    re.compile(r"\bi\s*(?:a|')?m\s+(\d{1,2})\b"),
    re.compile(r"\bi\s+am\s+(\d{1,2})\b"),
)

_AGES_LIST = re.compile(r"\bages?\s+((?:\d{1,2}\s*(?:,|and|&)?\s*)+)")


def detect_grades(text: str) -> List[int]:
    """Every K-12 grade the message refers to, by grade number (0 = kindergarten)."""
    norm = _norm(text)
    grades: List[int] = []

    for pattern in _GRADE_PATTERNS:
        for match in pattern.finditer(norm):
            value = int(match.group(1))
            if profile.GRADE_MIN <= value <= profile.GRADE_MAX:
                grades.append(value)

    if re.search(r"\bkindergart(?:en|ner)\b", norm):
        grades.append(0)

    for word, year in HIGH_SCHOOL_YEARS.items():
        # "senior" also appears in "senior in elementary education" (a job
        # applicant), so require a schooling context nearby.
        if re.search(rf"\b(?:a|is a|my|hes a|he's a|shes a|she's a)\s+{word}\b", norm):
            if not re.search(rf"\b{word}\s+(?:in|at)\s+(?:elementary|early|secondary)?\s*education\b", norm):
                grades.append(year)

    for match in _AGES_LIST.finditer(norm):
        for raw in re.findall(r"\d{1,2}", match.group(1)):
            age = int(raw)
            if profile.AGE_MIN <= age <= profile.AGE_MAX:
                grades.append(age - 5)

    for pattern in _AGE_PATTERNS:
        for match in pattern.finditer(norm):
            age = int(match.group(1))
            if profile.AGE_MIN <= age <= profile.AGE_MAX:
                grades.append(age - 5)

    return sorted({g for g in grades if profile.GRADE_MIN <= g <= profile.GRADE_MAX})


def detect_adult_age(text: str) -> bool:
    """An explicitly stated age past the K-12 range, for the speaker themselves."""
    norm = _norm(text)
    for pattern in _AGE_PATTERNS:
        for match in pattern.finditer(norm):
            if int(match.group(1)) > profile.AGE_MAX:
                return True
    return False


def has_grade_level(text: str) -> bool:
    return bool(detect_grades(text))


# --------------------------------------------------------------------------
# subject
# --------------------------------------------------------------------------

def detect_subjects(text: str) -> List[str]:
    norm = _norm(text)
    found = []
    for canonical, keywords in profile.SUBJECT_KEYWORDS.items():
        for keyword in keywords:
            if re.search(rf"(?<![a-z]){re.escape(keyword)}(?![a-z])", norm):
                found.append(canonical)
                break
    return sorted(found)


def has_subject(text: str) -> bool:
    return bool(detect_subjects(text))


_ASK_CONTEXT = re.compile(
    r"\b(do you|does your|offer|offers|teach|teaches|lesson|lessons|tutor|tutors|"
    r"tutoring|instruction|looking for|need|needs|want|wants|learn|help with|"
    r"interested in|able to)\b")


def detect_excluded_subject(text: str) -> Optional[str]:
    """An excluded subject the sender is actually asking for.

    A bare mention is not a request: "a friend from my son's soccer team" names
    soccer but asks for nothing, so it must not put the inquiry out of scope.
    The keyword only counts inside a sentence that also asks for something.
    """
    norm = _norm(text)
    for sentence in sentences(norm):
        if not _ASK_CONTEXT.search(sentence):
            continue
        for keyword in profile.EXCLUDED_SUBJECT_KEYWORDS:
            if re.search(rf"(?<![a-z]){re.escape(keyword)}(?![a-z])", sentence):
                return keyword
    return None


# --------------------------------------------------------------------------
# contact information
# --------------------------------------------------------------------------

_EMAIL_IN_BODY = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_IN_BODY = re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]?\d{4}\b|\b\d{3}-\d{4}\b")


def has_contact_info(message: str, sender_email: Optional[str],
                     sender_phone: Optional[str]) -> bool:
    if sender_email and "@" in sender_email:
        return True
    if sender_phone and re.search(r"\d", sender_phone):
        return True
    return bool(_EMAIL_IN_BODY.search(message) or _PHONE_IN_BODY.search(message))


# --------------------------------------------------------------------------
# availability
# --------------------------------------------------------------------------

_PLURAL_TIME_OF_DAY = re.compile(
    r"\b(mornings|afternoons|evenings|weekends|weeknights|nights)\b")

_EXPLICIT_AVAILABILITY = re.compile(
    r"\b(after school|all day|any day|anytime|any time|any afternoon|any evening|"
    r"any morning|most days|every day|right after school|after \d{1,2}\s*(?:pm|am)?|"
    r"weekday evenings|home every afternoon)\b")

_AVAILABILITY_CONTEXT = re.compile(
    r"\b(available|availability|free|open|flexible|works? best|works? for us|"
    r"work for us|we can do|can do|could do|would work|easiest|are good for us|"
    r"is open|are open|see|meet|move|reschedule|switch|book|set up)\b")

_TIME_TOKEN = re.compile(
    r"\b(" + "|".join(WEEKDAYS) + r"|weekday|weekend|morning|afternoon|evening|"
    r"night|tonight|after school|\d{1,2}\s*(?:pm|am))\b")


def has_availability(text: str) -> bool:
    """Times the family can meet.

    A bare weekday is not availability — "his final is on Friday" names a
    deadline, not an opening. A weekday only counts when it sits in a sentence
    that also frames it as an opening.
    """
    norm = _norm(text)
    if _PLURAL_TIME_OF_DAY.search(norm) or _EXPLICIT_AVAILABILITY.search(norm):
        return True
    for sentence in sentences(norm):
        if _AVAILABILITY_CONTEXT.search(sentence) and _TIME_TOKEN.search(sentence):
            return True
    return False


# --------------------------------------------------------------------------
# start timeline
# --------------------------------------------------------------------------

_START_TIMELINE = re.compile(
    r"\b(asap|as soon as possible|right away|immediately|"
    r"tonight|tomorrow|next month|start(?:ing)? (?:in|on|next|this)|"
    r"begin(?:ning)? (?:in|on|next|this)|want to (?:start|begin)|"
    r"ready to (?:start|begin|enroll)|get (?:him|her|them) started|"
    r"before (?:then|that meeting|the meeting|that)|in the next (?:couple|few|two|\d+)|"
    r"starting whenever|whenever you have room)\b")

# Week-scale phrases are ambiguous on their own: "I called three places this
# week" is a complaint about the past, not a start date. They only count as a
# start timeline alongside a verb about beginning or meeting.
_WEEK_SCALE = re.compile(r"\b(this week|next week|this weekend)\b")
_FORWARD_VERB = re.compile(
    r"\b(start|started|starting|begin|beginning|see|meet|session|sessions|"
    r"tutor|tutoring|want|need|hoping|hope|enroll|sign up|available)\b")


def has_start_timeline(text: str) -> bool:
    norm = _norm(text)
    if _START_TIMELINE.search(norm):
        return True
    for sentence in sentences(norm):
        if _WEEK_SCALE.search(sentence) and _FORWARD_VERB.search(sentence):
            return True
    # "start in November", "begin in January" etc.
    if re.search(r"\b(start|begin|starting|beginning)\b[\w ]{0,15}\b(" +
                 "|".join(MONTHS) + r")\b", norm):
        return True
    return False


# --------------------------------------------------------------------------
# learning goal
# --------------------------------------------------------------------------

_NAMED_SKILL_GAPS = (
    "fractions", "letter sounds", "word problems", "stoichiometry", "phonics",
    "decoding", "comprehension", "paragraph", "essay", "spelling", "grammar",
    "organization", "getting started", "test anxiety", "multiplication",
    "sight words", "placement", "retention", "handwriting", "fluency",
    "dyslexia", "orton-gillingham",
)

_PERFORMANCE_STATE = re.compile(
    r"\b(failing|fail|flunking|an? [fd]\b|dropped from|grades? (?:dropped|fell|slipped)|"
    r"sitting at a \d{1,3}|currently at a \d{1,3}|\b[a-d]s to [a-f]s\b|"
    r"behind (?:in|on)|two years ahead|below grade level|not passing)\b")

# "ready for high school level math", "reading at a 2nd grade level" — a stated
# level is a performance state in the same way a letter grade is.
_LEVEL_STATEMENT = re.compile(
    r"\b(?:ready for|working at|reading at|performing at|at|below|above)\s+"
    r"(?:an?\s+)?(?:high school|middle school|elementary|grade \d{1,2}|\d{1,2}(?:st|nd|rd|th) grade)"
    r"[\w ]{0,10}\blevel\b")

_STATED_OUTCOME = re.compile(
    r"\b(goal is|target is|aim is|want(?:s)? (?:him|her|them) to|"
    r"get (?:him|her|them) back to|back to an? [a-c]\b|raise (?:his|her|their)|"
    r"raising (?:his|her|their)|improve (?:his|her|their)|catch(?:ing)? up|"
    r"pass (?:both|the|his|her)|\d{2,3} points|score by)\b")


def has_learning_goal(text: str, has_deadline: bool = False) -> bool:
    """A stated outcome, a named skill gap, or a specific performance state.

    Generic distress ("she's struggling") deliberately does not count — see
    spec section 6.4.

    A named, dated academic event also counts: a parent who says "her final is
    Friday" or "the IEP meeting is the 24th" has told the business exactly what
    the work is for, even without naming a target grade.
    """
    if has_deadline:
        return True
    norm = _norm(text)
    if _PERFORMANCE_STATE.search(norm) or _STATED_OUTCOME.search(norm) \
            or _LEVEL_STATEMENT.search(norm):
        return True
    return any(gap in norm for gap in _NAMED_SKILL_GAPS)


# --------------------------------------------------------------------------
# deadlines
# --------------------------------------------------------------------------

DEADLINE_NOUNS = (
    "test", "exam", "final", "finals", "midterm", "quiz", "assessment",
    "benchmark", "report card", "report cards", "meeting", "review",
    "deadline", "due", "application", "sat", "act", "psat", "retention",
    "decision", "essay", "eligibility",
)

_IN_N_DAYS = re.compile(r"\b(?:in|within)\s+(\w+)\s+days?\b")
_N_DAYS_AWAY = re.compile(r"\b(\w+)\s+days?\s+(?:away|from now|out)\b")
_IN_N_WEEKS = re.compile(r"\b(?:in|within)\s+(\w+)\s+weeks?\b")
_N_WEEKS_AWAY = re.compile(r"\b(\w+)\s+weeks?\s+(?:away|from now|out)\b")
_THE_NTH = re.compile(r"\bthe\s+(\d{1,2})(?:st|nd|rd|th)\b")
_MONTH_DAY = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?\b")


def _as_number(token: str) -> Optional[int]:
    token = token.strip()
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def _received_date(received_at: str) -> date:
    return datetime.fromisoformat(received_at).date()


def _days_until_day_of_month(day: int, received: date) -> Optional[int]:
    if not 1 <= day <= 31:
        return None
    year, month = received.year, received.month
    if day < received.day:
        month += 1
        if month > 12:
            month, year = 1, year + 1
    try:
        target = date(year, month, day)
    except ValueError:
        return None
    return (target - received).days


def _days_until_month_day(month_name: str, day: int, received: date) -> Optional[int]:
    month = MONTHS[month_name]
    year = received.year
    try:
        target = date(year, month, day)
    except ValueError:
        return None
    if target < received:
        try:
            target = date(year + 1, month, day)
        except ValueError:
            return None
    return (target - received).days


def deadline_in_days(text: str, received_at: str) -> Optional[int]:
    """Days until the soonest deadline the message names, or None.

    A time expression only counts when a deadline noun appears in the same
    sentence: "his final is Friday" is a deadline, "we're free Friday" is not.
    """
    received = _received_date(received_at)
    norm = _norm(text)
    candidates: List[int] = []

    for sentence in sentences(norm):
        has_deadline_noun = any(
            re.search(rf"(?<![a-z]){re.escape(noun)}(?![a-z])", sentence)
            for noun in DEADLINE_NOUNS
        )
        if not has_deadline_noun:
            continue

        for pattern, multiplier in ((_IN_N_DAYS, 1), (_N_DAYS_AWAY, 1),
                                    (_IN_N_WEEKS, 7), (_N_WEEKS_AWAY, 7)):
            for match in pattern.finditer(sentence):
                value = _as_number(match.group(1))
                if value is not None:
                    candidates.append(value * multiplier)

        if re.search(r"\b(tonight|today)\b", sentence):
            candidates.append(0)
        if re.search(r"\btomorrow\b", sentence):
            candidates.append(1)
        if re.search(r"\bthis weekend\b", sentence):
            candidates.append(3)
        if re.search(r"\bthis week\b", sentence):
            candidates.append(5)
        if re.search(r"\bnext week\b", sentence):
            candidates.append(7)
        if re.search(r"\bnext month\b", sentence):
            candidates.append(30)

        for weekday in WEEKDAYS:
            if re.search(rf"\bnext {weekday}\b", sentence):
                candidates.append(8)
            elif re.search(rf"\b{weekday}\b", sentence):
                candidates.append(5)

        for match in _THE_NTH.finditer(sentence):
            days = _days_until_day_of_month(int(match.group(1)), received)
            if days is not None:
                candidates.append(days)

        for match in _MONTH_DAY.finditer(sentence):
            days = _days_until_month_day(match.group(1), int(match.group(2)), received)
            if days is not None:
                candidates.append(days)

    return min(candidates) if candidates else None
