"""Regression tests: one per rule change in docs/LEAD_AGENT_FAILURE_LOG.md.

Each test names the failure-log entry it locks down and the benchmark cases
that exposed it. Standard-library unittest so it runs from a clean checkout;
pytest discovers these classes too.

    python3 -m unittest discover -s agents/lead_qualification/tests -t .
"""

import unittest

from agents.lead_qualification import analyze
from agents.lead_qualification import extract
from agents.lead_qualification.agent import _has_price_ask
from agents.lead_qualification.schema import (
    Field, Inquiry, Intent, Priority, Qualification)


def decide(message, channel="email", received_at="2026-09-17T12:00:00",
           email="parent@example.com", phone=None, name=None):
    return analyze(Inquiry(
        id="TEST", channel=channel, received_at=received_at, message=message,
        sender_name=name, sender_email=email, sender_phone=phone))


class TestR01BoundaryMatching(unittest.TestCase):
    """R-01: markers were matched as substrings, so 'your tutors' contained
    'our tutor' and 'dual-enrollment' contained 'enroll'.
    Exposed by LQ-053, LQ-055, LQ-059, LQ-083, LQ-099."""

    def test_your_tutors_is_not_an_existing_customer(self):
        d = decide("Are your tutors able to handle 9th grade geometry?")
        self.assertNotEqual(d.intent, Intent.EXISTING_CUSTOMER)

    def test_your_sessions_is_not_an_existing_customer(self):
        d = decide("Can you tell me how your sessions are structured?")
        self.assertNotEqual(d.intent, Intent.EXISTING_CUSTOMER)

    def test_our_tutor_still_is_an_existing_customer(self):
        d = decide("Our tutor mentioned my son is doing better this month.")
        self.assertEqual(d.intent, Intent.EXISTING_CUSTOMER)

    def test_dual_enrollment_is_not_a_buying_signal(self):
        d = decide("My son is in 10th grade and takes dual-enrollment College "
                   "Algebra. Is that something you tutor?")
        self.assertNotEqual(d.priority, Priority.HIGH)

    def test_ready_to_enroll_still_is_a_buying_signal(self):
        d = decide("My son is in 10th grade, needs geometry, and we are ready "
                   "to enroll.")
        self.assertEqual(d.priority, Priority.HIGH)


class TestR02ExcludedSubjectNeedsAsk(unittest.TestCase):
    """R-02: a bare mention of an excluded subject put a real lead out of
    scope. Exposed by LQ-020 ('my son's soccer team')."""

    def test_incidental_mention_stays_in_scope(self):
        d = decide("A friend from my son's soccer team recommended you. He is "
                   "in 8th grade and his science grades dropped from Bs to Ds.")
        self.assertEqual(d.qualification, Qualification.QUALIFIED)

    def test_actual_request_is_still_out_of_scope(self):
        d = decide("Do you teach piano? Looking for lessons for my 7 year old.")
        self.assertEqual(d.qualification, Qualification.OUT_OF_SCOPE)


class TestR03PriceAskOrdering(unittest.TestCase):
    """R-03: a bare price question named no child, so it fell through the
    tutoring-signal gate to `unclear`. Exposed by LQ-004, LQ-039, LQ-082."""

    def test_bare_price_question_is_a_pricing_inquiry(self):
        d = decide("how much do u charge per hour", channel="sms",
                   email=None, phone="555-0188")
        self.assertEqual(d.intent, Intent.PRICING_INQUIRY)

    def test_price_mention_without_a_question_is_not(self):
        d = decide("My granddaughter is in 5th grade and struggling with "
                   "fractions. We are on a fixed income so cost matters, but I "
                   "will find a way.")
        self.assertEqual(d.intent, Intent.TUTORING_INQUIRY)

    def test_off_topic_message_is_still_unrelated(self):
        d = decide("I think my car got towed from the lot on Fremont last "
                   "night and I am trying to find out who to call.")
        self.assertEqual(d.intent, Intent.UNRELATED)


class TestR04DeadlineImpliesGoal(unittest.TestCase):
    """R-04: a named, dated academic event tells the business what the work is
    for. Exposed by LQ-007, LQ-011, LQ-061."""

    def test_named_exam_supplies_a_learning_goal(self):
        d = decide("My son is a junior and his SAT is in 9 days. He needs help "
                   "with the math section. He is free this weekend.",
                   channel="sms", email=None, phone="555-0177")
        self.assertNotIn(Field.LEARNING_GOAL, d.missing_information)

    def test_no_deadline_no_implied_goal(self):
        d = decide("My daughter is in 5th grade and needs math help.")
        self.assertIn(Field.LEARNING_GOAL, d.missing_information)


class TestR05LevelStatement(unittest.TestCase):
    """R-05: a stated working level is a performance state. Exposed by LQ-062."""

    def test_level_statement_is_a_goal(self):
        self.assertTrue(extract.has_learning_goal(
            "My 14 year old is ready for high school level math."))

    def test_generic_distress_is_not_a_goal(self):
        self.assertFalse(extract.has_learning_goal(
            "She is really struggling and I do not know what to do."))


class TestR06StartTimelineFalsePositives(unittest.TestCase):
    """R-06: week-scale phrases fired on past-tense and deadline text.
    Exposed by LQ-018, LQ-025, LQ-035, LQ-065."""

    def test_past_tense_this_week_is_not_a_start_timeline(self):
        self.assertFalse(extract.has_start_timeline(
            "I called three places this week and nobody called me back."))

    def test_forward_looking_this_week_is_a_start_timeline(self):
        self.assertTrue(extract.has_start_timeline(
            "We want to start this week if you have anyone."))

    def test_by_the_end_of_is_a_deadline_not_a_start(self):
        self.assertFalse(extract.has_start_timeline(
            "He is being considered for retention if his math does not come up "
            "by the end of the quarter."))

    def test_getting_started_difficulty_is_not_a_start_timeline(self):
        self.assertFalse(extract.has_start_timeline(
            "He is bright but cannot get started on anything."))


class TestR07GetStartedNotABuyingSignal(unittest.TestCase):
    """R-07: 'cannot get started on anything' described the child's executive
    function, not the parent's urgency. Exposed by LQ-018."""

    def test_child_cannot_get_started_is_not_high_priority(self):
        d = decide("My son is in 7th grade and has ADHD. He is bright but "
                   "cannot get started on anything. Is that something you help "
                   "with?")
        self.assertEqual(d.priority, Priority.MEDIUM)

    def test_parent_wants_to_get_started_is_high_priority(self):
        d = decide("My son is in 7th grade and needs math help. We want to get "
                   "started asap. Weekday evenings work for us.")
        self.assertEqual(d.priority, Priority.HIGH)


class TestR08GradeWithoutTheWordGrade(unittest.TestCase):
    """R-08: families drop the word 'grade'. Exposed by LQ-052."""

    def test_shes_in_11th(self):
        self.assertEqual(extract.detect_grades("shes in 11th"), [11])

    def test_ordinal_day_is_not_a_grade(self):
        self.assertEqual(extract.detect_grades("the meeting is on the 24th"), [])


class TestR09AvailabilityContext(unittest.TestCase):
    """R-09: offered meeting windows were missed while deadline weekdays were
    correctly ignored. Exposed by LQ-011, LQ-050, LQ-052."""

    def test_offered_window_counts(self):
        self.assertTrue(extract.has_availability(
            "Is there any chance someone could do a session tonight?"))

    def test_reschedule_proposal_counts(self):
        self.assertTrue(extract.has_availability(
            "Can we move tomorrows 4pm consult to Friday same time?"))

    def test_deadline_weekday_does_not_count(self):
        self.assertFalse(extract.has_availability(
            "My son has his Algebra 1 final on Friday."))

    def test_annual_meeting_weekday_does_not_count(self):
        self.assertFalse(extract.has_availability(
            "Her annual review meeting is next Wednesday."))


class TestPriceAskDetection(unittest.TestCase):
    def test_declarative_cost_mention_is_not_an_ask(self):
        self.assertFalse(_has_price_ask(
            "We are on a fixed income, so cost matters."))

    def test_stated_intent_to_know_rates_is_an_ask(self):
        self.assertTrue(_has_price_ask(
            "I would like to know what you offer and your rates."))


if __name__ == "__main__":
    unittest.main()
