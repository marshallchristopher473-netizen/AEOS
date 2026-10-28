#!/usr/bin/env python3
"""Tests for the AEOS revenue tools.

Run standalone:
    python3 tools/revenue/test_revenue_tools.py

Or under pytest:
    pytest tools/revenue/test_revenue_tools.py
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_deck  # noqa: E402
import rate_report  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXAMPLE_LOG = os.path.join(
    REPO_ROOT, "docs", "revenue", "evidence", "time-and-income-log.example.csv"
)
LIVE_LOG = os.path.join(
    REPO_ROOT, "docs", "revenue", "evidence", "time-and-income-log.csv"
)
SAMPLE_DECK = os.path.join(
    REPO_ROOT, "docs", "revenue", "portfolio", "parent-night-reading-sample.json"
)


def _write_log(rows: str) -> str:
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8"
    )
    handle.write("date,experiment,category,activity,hours,amount_usd,notes\n")
    handle.write(rows)
    handle.close()
    return handle.name


# --------------------------------------------------------------------------
# rate_report
# --------------------------------------------------------------------------


def test_effective_rate_counts_every_hour():
    """$650 earned over 10 hours is $65/hr, including acquisition and admin."""
    path = _write_log(
        "2026-11-01,deck_sprint,acquisition,Outreach,2,,\n"
        "2026-11-02,deck_sprint,delivery,Build,7,,\n"
        "2026-11-03,deck_sprint,admin,Invoice,1,,\n"
        "2026-11-04,deck_sprint,income,Paid in full,,650,\n"
    )
    totals = rate_report.summarize(rate_report.read_log(path))
    sprint = totals["deck_sprint"]
    assert sprint.total_hours == 10.0
    assert sprint.net_income == 650.0
    assert sprint.effective_rate == 65.0
    os.unlink(path)


def test_fees_reduce_net_income():
    """A 25% platform fee on $60 leaves $45, not $60."""
    path = _write_log(
        "2026-11-05,tutoring,delivery,Session,1,,\n"
        "2026-11-05,tutoring,income,Payment,,60,\n"
        "2026-11-05,tutoring,fee,Platform fee,,15,\n"
    )
    tutoring = rate_report.summarize(rate_report.read_log(path))["tutoring"]
    assert tutoring.income == 60.0
    assert tutoring.fees == 15.0
    assert tutoring.net_income == 45.0
    assert tutoring.effective_rate == 45.0
    os.unlink(path)


def test_preparation_time_lowers_the_rate():
    """An hour of prep per hour of tutoring halves the real rate."""
    path = _write_log(
        "2026-11-05,tutoring,delivery,Session,1,,\n"
        "2026-11-05,tutoring,delivery,Prep,1,,\n"
        "2026-11-05,tutoring,income,Payment,,60,\n"
    )
    tutoring = rate_report.summarize(rate_report.read_log(path))["tutoring"]
    assert tutoring.effective_rate == 30.0
    os.unlink(path)


def test_hours_without_income_report_no_rate_not_a_crash():
    path = _write_log("2026-11-01,ai_eval,admin,Application,1.25,,\n")
    totals = rate_report.summarize(rate_report.read_log(path))["ai_eval"]
    assert totals.total_hours == 1.25
    assert totals.net_income == 0.0
    assert totals.effective_rate == 0.0
    assert rate_report._rate_text(totals) == "$0.00/hr"
    assert rate_report._verdict(totals, 50.0) == "UNPAID"
    os.unlink(path)


def test_experiment_with_no_hours_has_no_rate():
    path = _write_log("2026-11-01,coverage_pay,income,Recovered pay,,180,\n")
    totals = rate_report.summarize(rate_report.read_log(path))["coverage_pay"]
    assert totals.effective_rate is None
    assert rate_report._rate_text(totals) == "n/a"
    os.unlink(path)


def test_weekly_hours_group_by_iso_week():
    path = _write_log(
        "2026-11-02,deck_sprint,delivery,Monday,2,,\n"
        "2026-11-04,deck_sprint,delivery,Wednesday,3,,\n"
        "2026-11-10,deck_sprint,delivery,Next Monday,1,,\n"
    )
    weeks = rate_report.weekly_hours(rate_report.read_log(path))
    assert len(weeks) == 2
    assert weeks[dt.date(2026, 11, 2).isocalendar()[:2]] == 5.0
    os.unlink(path)


def test_money_rows_are_excluded_from_hours():
    path = _write_log(
        "2026-11-01,deck_sprint,delivery,Build,4,,\n"
        "2026-11-02,deck_sprint,income,Deposit,,325,\n"
    )
    weeks = rate_report.weekly_hours(rate_report.read_log(path))
    assert sum(weeks.values()) == 4.0
    os.unlink(path)


def test_bad_category_is_rejected_with_a_clear_message():
    path = _write_log("2026-11-01,deck_sprint,misc,Something,1,,\n")
    try:
        rate_report.read_log(path)
    except rate_report.LogError as exc:
        assert "category" in str(exc)
        assert "line 2" in str(exc)
    else:
        raise AssertionError("expected LogError for an unknown category")
    os.unlink(path)


def test_negative_amount_is_rejected():
    path = _write_log("2026-11-01,tutoring,fee,Platform fee,,-15,\n")
    try:
        rate_report.read_log(path)
    except rate_report.LogError as exc:
        assert "negative" in str(exc)
    else:
        raise AssertionError("expected LogError for a negative amount")
    os.unlink(path)


def test_work_row_without_hours_is_rejected():
    path = _write_log("2026-11-01,deck_sprint,delivery,Build,,,forgot the hours\n")
    try:
        rate_report.read_log(path)
    except rate_report.LogError as exc:
        assert "hours" in str(exc)
    else:
        raise AssertionError("expected LogError for a work row with no hours")
    os.unlink(path)


def test_bad_date_is_rejected():
    path = _write_log("11/01/2026,deck_sprint,delivery,Build,1,,\n")
    try:
        rate_report.read_log(path)
    except rate_report.LogError as exc:
        assert "YYYY-MM-DD" in str(exc)
    else:
        raise AssertionError("expected LogError for a malformed date")
    os.unlink(path)


def test_blank_rows_are_skipped():
    path = _write_log("2026-11-01,deck_sprint,delivery,Build,1,,\n,,,,,,\n")
    assert len(rate_report.read_log(path)) == 1
    os.unlink(path)


def test_empty_live_log_parses_and_reports():
    """The committed log starts empty; the tool must handle that, not crash."""
    entries = rate_report.read_log(LIVE_LOG)
    assert entries == []
    report = "\n".join(rate_report.build_report(entries, 50.0, 4.0))
    assert "log is empty" in report


def test_example_log_produces_a_full_report():
    entries = rate_report.read_log(EXAMPLE_LOG)
    report = "\n".join(rate_report.build_report(entries, 50.0, 4.0))
    assert "deck_sprint" in report
    assert "Weekly load" in report
    totals = rate_report.summarize(entries)
    assert totals["deck_sprint"].net_income == 650.0
    assert totals["tutoring"].net_income == 45.0


def test_below_target_is_flagged():
    path = _write_log(
        "2026-11-01,deck_sprint,delivery,Build,25,,\n"
        "2026-11-02,deck_sprint,income,Paid,,650,\n"
    )
    entries = rate_report.read_log(path)
    report = "\n".join(rate_report.build_report(entries, 50.0, 4.0))
    assert "BELOW TARGET" in report
    assert "below the $50.00 target" in report
    os.unlink(path)


def test_over_capacity_week_is_flagged():
    path = _write_log("2026-11-02,deck_sprint,delivery,Long day,9,,\n")
    report = "\n".join(rate_report.build_report(rate_report.read_log(path), 50.0, 4.0))
    assert "OVER CAPACITY" in report
    os.unlink(path)


def test_acquisition_heavy_work_is_called_out():
    path = _write_log(
        "2026-11-01,deck_sprint,acquisition,Outreach,8,,\n"
        "2026-11-02,deck_sprint,delivery,Build,2,,\n"
        "2026-11-03,deck_sprint,income,Paid,,650,\n"
    )
    report = "\n".join(rate_report.build_report(rate_report.read_log(path), 50.0, 4.0))
    assert "Acquisition is 80% of all hours" in report
    os.unlink(path)


def test_missing_log_file_is_a_clean_error():
    try:
        rate_report.read_log("/nonexistent/path/to/log.csv")
    except rate_report.LogError as exc:
        assert "no log file" in str(exc)
    else:
        raise AssertionError("expected LogError for a missing file")


# --------------------------------------------------------------------------
# build_deck
# --------------------------------------------------------------------------


def _deck(**overrides) -> dict:
    deck = {
        "meta": {
            "title": "Test deck",
            "audience": "Parents of grade 7 students",
            "desired_action": "Start the routine this week",
            "attribution": "Written by the author",
        },
        "slides": [
            {
                "layout": "title",
                "title": "Test deck",
                "notes": "Open by naming the problem the room already has, in plain words.",
            },
            {
                "layout": "content",
                "title": "A point",
                "bullets": ["Four nights a week.", "Twelve minutes."],
                "notes": "Explain why four beats seven, and say that missed nights are expected.",
            },
        ],
    }
    deck.update(overrides)
    return deck


def _write_deck(deck: dict) -> str:
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(deck, handle)
    handle.close()
    return handle.name


def test_a_complete_deck_passes_with_no_problems():
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(_deck())))
    assert problems == []


def test_heading_without_body_is_blocking():
    """The audit's central finding: headings with nothing under them."""
    deck = _deck()
    deck["slides"][1]["bullets"] = []
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert any("no body content" in p for p in problems)


def test_missing_speaker_notes_are_blocking():
    deck = _deck()
    deck["slides"][1]["notes"] = ""
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert any("no speaker notes" in p for p in problems)


def test_overlong_slide_is_blocking():
    deck = _deck()
    deck["slides"][1]["bullets"] = ["word " * 45]
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert any("exceeds the 40-word limit" in p for p in problems)


def test_placeholders_are_blocking():
    deck = _deck()
    deck["slides"][1]["bullets"] = ["TODO: write this one"]
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert any("placeholder" in p for p in problems)


def test_unreplaced_bracket_is_blocking():
    deck = _deck()
    deck["slides"][1]["bullets"] = ["[CLIENT NAME]"]
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert any("unreplaced bracket" in p for p in problems)


def test_title_slide_needs_no_bullets():
    deck = _deck()
    assert "bullets" not in deck["slides"][0]
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert problems == []


def test_thin_notes_warn_but_do_not_block():
    deck = _deck()
    deck["slides"][1]["notes"] = "Say it."
    problems, warnings = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert problems == []
    assert any("would they let someone else deliver" in w for w in warnings)


def test_missing_attribution_warns():
    deck = _deck()
    deck["meta"]["attribution"] = ""
    _, warnings = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert any("attribution" in w for w in warnings)


def test_malformed_json_is_a_clean_error():
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    )
    handle.write("{not json")
    handle.close()
    try:
        build_deck.load_deck(handle.name)
    except build_deck.DeckError as exc:
        assert "not valid JSON" in str(exc)
    else:
        raise AssertionError("expected DeckError for malformed JSON")
    os.unlink(handle.name)


def test_deck_without_slides_is_a_clean_error():
    try:
        build_deck.load_deck(_write_deck({"meta": {}, "slides": []}))
    except build_deck.DeckError as exc:
        assert "non-empty 'slides' list" in str(exc)
    else:
        raise AssertionError("expected DeckError for an empty deck")


def test_footnote_is_checked_for_placeholders():
    deck = _deck()
    deck["slides"][1]["footnote"] = "[SOURCE]"
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert any("unreplaced bracket" in p for p in problems)


def test_overlong_footnote_warns():
    deck = _deck()
    deck["slides"][1]["footnote"] = "word " * 30
    problems, warnings = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert problems == []
    assert any("footnote is 30 words" in w for w in warnings)


def test_footnote_does_not_count_toward_the_body_word_limit():
    deck = _deck()
    deck["slides"][1]["footnote"] = "word " * 20
    problems, _ = build_deck.check_deck(build_deck.load_deck(_write_deck(deck)))
    assert not any("40-word limit" in p for p in problems)


def test_footnote_appears_in_the_markdown():
    deck = _deck()
    deck["slides"][1]["footnote"] = "Composite example."
    markdown = build_deck.render_markdown(build_deck.load_deck(_write_deck(deck)))
    assert "*Composite example.*" in markdown


def test_sample_deck_labels_the_classroom_example_on_the_slide():
    """The deck's own pre-ship requirement: composite label on the slide, not just notes."""
    deck = build_deck.load_deck(SAMPLE_DECK)
    marcus = next(s for s in deck["slides"] if "Marcus" in s.get("title", ""))
    assert "composite" in str(marcus.get("footnote") or "").lower()


def test_theme_defaults_fill_in():
    deck = build_deck.load_deck(_write_deck(_deck()))
    assert deck["theme"]["heading_font"] == build_deck.DEFAULT_THEME["heading_font"]


def test_markdown_contains_every_slide_and_its_notes():
    markdown = build_deck.render_markdown(build_deck.load_deck(_write_deck(_deck())))
    assert "Slide 1 — A point" in markdown
    assert "Speaker notes" in markdown
    assert "Four nights a week." in markdown


def test_the_real_sample_deck_passes_every_blocking_check():
    """The committed portfolio sample must be shippable, not a draft."""
    deck = build_deck.load_deck(SAMPLE_DECK)
    problems, _ = build_deck.check_deck(deck)
    assert problems == [], f"sample deck has blocking problems: {problems}"
    content = [s for s in deck["slides"] if s.get("layout") != "title"]
    assert len(content) == 6
    assert all(str(s.get("notes") or "").strip() for s in deck["slides"])


def test_sample_deck_builds_a_pptx_with_notes():
    deck = build_deck.load_deck(SAMPLE_DECK)
    try:
        from pptx import Presentation
    except ImportError:
        print("  (skipped pptx test: python-pptx not installed)")
        return
    with tempfile.TemporaryDirectory() as outdir:
        path = os.path.join(outdir, "sample.pptx")
        build_deck.write_pptx(deck, path)
        assert os.path.getsize(path) > 0
        built = Presentation(path)
        assert len(built.slides) == len(deck["slides"])
        for slide in built.slides:
            assert slide.notes_slide.notes_text_frame.text.strip()


def _run() -> int:
    tests = [
        (name, value)
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    failures = []
    for name, test in tests:
        try:
            test()
            print(f"  pass  {name}")
        except Exception as exc:  # noqa: BLE001 - a test runner reports everything
            failures.append((name, exc))
            print(f"  FAIL  {name}: {exc}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run())
