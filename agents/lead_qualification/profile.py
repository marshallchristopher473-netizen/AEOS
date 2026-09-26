"""The tutoring business the v1 rules are written for.

Spec section 5. A different tutoring business changes this file, not the engine.
Turning this into per-tenant configuration data is explicitly deferred until a
second pilot business signs (spec section 9).
"""

BUSINESS_NAME = "Bright Path Tutoring"

# Canonical subject -> the words families actually use for it.
SUBJECT_KEYWORDS = {
    "math": [
        "math", "maths", "algebra", "pre-algebra", "prealgebra", "pre algebra",
        "geometry", "calculus", "trigonometry", "trig", "statistics", "arithmetic",
        "fractions", "multiplication", "division", "word problems", "computation",
        "number sense",
    ],
    "reading": [
        "reading", "phonics", "letter sounds", "decoding", "literacy",
        "comprehension", "dyslexia", "fluency", "sight words",
    ],
    "writing": [
        "writing", "essay", "essays", "paragraph", "composition", "grammar",
        "spelling",
    ],
    "english_language_arts": [
        "english", "ela", "language arts", "literature",
    ],
    "science": [
        "science", "biology", "chemistry", "physics", "stoichiometry",
        "earth science", "life science",
    ],
    "test_prep": [
        "sat", "act", "psat", "test prep", "college board",
    ],
    "study_skills": [
        "study skills", "studying", "organization", "organizational",
        "executive function", "time management", "homework habits",
        "getting started", "note taking", "test anxiety",
    ],
}

# Grades served, as integers. 0 is kindergarten.
GRADE_MIN = 0
GRADE_MAX = 12

# Ages that map onto K-12. Used when a family gives an age instead of a grade.
AGE_MIN = 5
AGE_MAX = 18

# Requests the business does not take, regardless of how well qualified they are.
EXCLUDED_SUBJECT_KEYWORDS = [
    "piano", "guitar", "violin", "music lesson", "voice lesson", "singing",
    "drivers ed", "driver's ed", "drivers education", "driver education",
    "behind-the-wheel", "behind the wheel", "road test",
    "swim", "soccer", "basketball", "karate", "dance lesson",
    "conversational italian", "conversational french", "conversational spanish",
    "italian", "french lessons",
]

# Signals that the learner is an adult or the material is past grade 12.
ADULT_LEARNER_KEYWORDS = [
    "adult student", "adult students", "adult learner", "adult learners",
    "adult language", "going back to school",
    "bar exam", "mcat", "lsat", "gmat", "nclex", "cpa exam", "praxis",
    "graduate-level", "graduate level", "grad school", "mba",
    "nursing prerequisites", "corporate finance",
]

POST_SECONDARY_KEYWORDS = [
    "college-level", "college level", "university course", "community college course",
]

# Requests the business refuses on academic-integrity grounds.
# Regular expressions, because the object of the verb varies ("do my son's
# chemistry homework", "do her weekly assignments").
INTEGRITY_VIOLATION_PATTERNS = [
    r"\bdo (?:my|his|her|the)\b[\w' ]{0,30}\b(?:homework|assignment|assignments|coursework)\b",
    r"\b(?:complete|finish|submit|turn in)\b[\w' ]{0,30}\b(?:assignments|submissions|homework)\b\s*(?:for (?:him|her|my))?",
    r"\bhandle the weekly submissions\b",
    r"\b(?:write|take)\b[\w' ]{0,25}\b(?:essay|paper|test|exam)\b[\w' ]{0,10}\bfor (?:him|her|my)\b",
]
