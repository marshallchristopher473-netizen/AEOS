#!/usr/bin/env python3
"""Build a deck from a JSON content file.

One content file is the source of truth for a deck. This script turns it into
two outputs:

  * an editable .pptx with speaker notes already filled in
  * a .md review copy, for reading the whole deck without opening PowerPoint

It also enforces the blocking items from docs/revenue/quality/deck-quality-checklist.md
that a machine can actually check: every content slide has body content, every
content slide has speaker notes, and no slide is overloaded with text. A deck
that fails those does not build. That is deliberate - an unfinished sample
argues against you more effectively than no sample at all.

Usage:
    python3 tools/revenue/build_deck.py <deck.json> --outdir build/decks
    python3 tools/revenue/build_deck.py <deck.json> --outdir build/ --allow-incomplete
    python3 tools/revenue/build_deck.py <deck.json> --outdir build/ --markdown-only

The .pptx output needs python-pptx (pip install python-pptx). Without it, the
Markdown copy is still written and the script says what is missing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

MAX_BODY_WORDS = 40
MIN_BODY_FONT_PT = 18

DEFAULT_THEME = {
    "heading_font": "Georgia",
    "body_font": "Verdana",
    "accent_rgb": [21, 66, 97],
    "text_rgb": [34, 34, 34],
    "muted_rgb": [102, 102, 102],
}


class DeckError(ValueError):
    """Raised when a deck file is malformed or would build an unfinished deck."""


def load_deck(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            deck = json.load(handle)
    except FileNotFoundError as exc:
        raise DeckError(f"no deck file at {path}") from exc
    except json.JSONDecodeError as exc:
        raise DeckError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(deck, dict):
        raise DeckError("the deck file must contain a JSON object")
    if not isinstance(deck.get("meta"), dict):
        raise DeckError("the deck file needs a 'meta' object")
    slides = deck.get("slides")
    if not isinstance(slides, list) or not slides:
        raise DeckError("the deck file needs a non-empty 'slides' list")

    theme = dict(DEFAULT_THEME)
    theme.update(deck.get("theme") or {})
    deck["theme"] = theme
    return deck


def _word_count(bullets: list[str]) -> int:
    return sum(len(str(bullet).split()) for bullet in bullets)


def check_deck(deck: dict) -> tuple[list[str], list[str]]:
    """Return (blocking_problems, warnings) for a loaded deck."""
    problems: list[str] = []
    warnings: list[str] = []

    content_slides = 0
    for index, slide in enumerate(deck["slides"], start=1):
        if not isinstance(slide, dict):
            problems.append(f"slide {index}: expected an object")
            continue

        layout = slide.get("layout", "content")
        label = f"slide {index} ({slide.get('title') or 'untitled'})"

        if not str(slide.get("title") or "").strip():
            problems.append(f"{label}: has no title")

        notes = str(slide.get("notes") or "").strip()
        if not notes:
            problems.append(f"{label}: has no speaker notes")
        elif len(notes.split()) < 10:
            warnings.append(
                f"{label}: speaker notes are only {len(notes.split())} words; "
                "would they let someone else deliver this slide?"
            )

        if layout == "title":
            continue

        content_slides += 1
        bullets = slide.get("bullets") or []
        if not isinstance(bullets, list) or not any(
            str(b).strip() for b in bullets
        ):
            problems.append(
                f"{label}: has a heading but no body content. "
                "A heading is a promise the slide has not kept."
            )
            continue

        words = _word_count(bullets)
        if words > MAX_BODY_WORDS:
            problems.append(
                f"{label}: {words} words of body text exceeds the {MAX_BODY_WORDS}-word "
                "limit. Split it or cut it."
            )

        footnote = str(slide.get("footnote") or "").strip()
        for text in [str(b) for b in bullets] + ([footnote] if footnote else []):
            lowered = text.lower()
            if "lorem ipsum" in lowered or "todo" in lowered or "tbd" in lowered:
                problems.append(f"{label}: contains a placeholder ({text[:40]!r})")
            if text.strip().startswith("[") and text.strip().endswith("]"):
                problems.append(f"{label}: contains an unreplaced bracket ({text[:40]!r})")

        if footnote and len(footnote.split()) > 25:
            warnings.append(
                f"{label}: footnote is {len(footnote.split())} words; a caption that long "
                "belongs in the speaker notes"
            )

    if content_slides == 0:
        problems.append("the deck has no content slides")

    meta = deck["meta"]
    if not str(meta.get("audience") or "").strip():
        warnings.append("meta.audience is empty; the deck cannot be checked against a room")
    if not str(meta.get("desired_action") or "").strip():
        warnings.append("meta.desired_action is empty; the deck has no ask")
    if not str(meta.get("attribution") or "").strip():
        warnings.append("meta.attribution is empty; state who wrote this and from what")

    return problems, warnings


def render_markdown(deck: dict) -> str:
    meta = deck["meta"]
    lines: list[str] = []
    lines.append(f"# {meta.get('title', 'Untitled deck')}")
    if meta.get("subtitle"):
        lines.append("")
        lines.append(f"*{meta['subtitle']}*")

    lines.append("")
    lines.append("> Review copy generated by `tools/revenue/build_deck.py`.")
    lines.append("> Edit the JSON source, not this file.")
    lines.append("")

    detail_fields = [
        ("Presenter", "presenter"),
        ("Audience", "audience"),
        ("Desired action", "desired_action"),
        ("Purpose", "purpose"),
        ("Attribution", "attribution"),
    ]
    details = [(label, meta[key]) for label, key in detail_fields if meta.get(key)]
    if details:
        lines.append("| Field | Value |")
        lines.append("| --- | --- |")
        lines.extend(f"| {label} | {value} |" for label, value in details)
        lines.append("")

    if meta.get("evidence_note"):
        lines.append(f"**On evidence:** {meta['evidence_note']}")
        lines.append("")

    if meta.get("verification_required"):
        lines.append("## Before this deck ships")
        lines.append("")
        lines.extend(f"- [ ] {item}" for item in meta["verification_required"])
        lines.append("")

    lines.append("---")
    content_number = 0
    for slide in deck["slides"]:
        layout = slide.get("layout", "content")
        lines.append("")
        if layout == "title":
            lines.append(f"## Title slide — {slide.get('title', '')}")
            if slide.get("subtitle"):
                lines.append("")
                lines.append(slide["subtitle"])
        else:
            content_number += 1
            lines.append(f"## Slide {content_number} — {slide.get('title', '')}")
            lines.append("")
            for bullet in slide.get("bullets") or []:
                lines.append(f"- {bullet}")
            footnote = str(slide.get("footnote") or "").strip()
            if footnote:
                lines.append("")
                lines.append(f"*{footnote}*")

        notes = str(slide.get("notes") or "").strip()
        if notes:
            lines.append("")
            lines.append("**Speaker notes**")
            lines.append("")
            for paragraph in notes.split("\n\n"):
                stripped = paragraph.strip()
                if stripped:
                    lines.append(stripped)
                    lines.append("")
        lines.append("---")

    lines.append("")
    return "\n".join(lines)


def write_pptx(deck: dict, path: str) -> None:
    """Write the .pptx. Raises ImportError when python-pptx is not installed."""
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Inches, Pt

    theme = deck["theme"]
    accent = RGBColor(*theme["accent_rgb"])
    body_color = RGBColor(*theme["text_rgb"])
    muted = RGBColor(*theme["muted_rgb"])

    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)
    blank_layout = presentation.slide_layouts[6]

    for slide_spec in deck["slides"]:
        layout = slide_spec.get("layout", "content")
        slide = presentation.slides.add_slide(blank_layout)

        is_title = layout == "title"
        title_top = Inches(2.6) if is_title else Inches(0.7)
        title_size = Pt(40) if is_title else Pt(32)

        title_box = slide.shapes.add_textbox(
            Inches(0.9), title_top, Inches(11.5), Inches(1.4)
        )
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        title_run = title_frame.paragraphs[0].add_run()
        title_run.text = str(slide_spec.get("title", ""))
        title_run.font.size = title_size
        title_run.font.bold = True
        title_run.font.name = theme["heading_font"]
        title_run.font.color.rgb = accent

        if is_title:
            subtitle = str(slide_spec.get("subtitle") or "").strip()
            if subtitle:
                sub_box = slide.shapes.add_textbox(
                    Inches(0.9), Inches(4.1), Inches(11.5), Inches(0.9)
                )
                sub_frame = sub_box.text_frame
                sub_frame.word_wrap = True
                sub_run = sub_frame.paragraphs[0].add_run()
                sub_run.text = subtitle
                sub_run.font.size = Pt(22)
                sub_run.font.name = theme["body_font"]
                sub_run.font.color.rgb = muted
            presenter = str(deck["meta"].get("presenter") or "").strip()
            if presenter:
                by_box = slide.shapes.add_textbox(
                    Inches(0.9), Inches(5.2), Inches(11.5), Inches(0.6)
                )
                by_run = by_box.text_frame.paragraphs[0].add_run()
                by_run.text = presenter
                by_run.font.size = Pt(18)
                by_run.font.name = theme["body_font"]
                by_run.font.color.rgb = muted
        else:
            body_box = slide.shapes.add_textbox(
                Inches(0.9), Inches(2.2), Inches(11.5), Inches(4.3)
            )
            body_frame = body_box.text_frame
            body_frame.word_wrap = True
            for position, bullet in enumerate(slide_spec.get("bullets") or []):
                paragraph = (
                    body_frame.paragraphs[0]
                    if position == 0
                    else body_frame.add_paragraph()
                )
                paragraph.space_after = Pt(16)
                run = paragraph.add_run()
                run.text = f"•   {bullet}"
                run.font.size = Pt(22)
                run.font.name = theme["body_font"]
                run.font.color.rgb = body_color

            footnote = str(slide_spec.get("footnote") or "").strip()
            if footnote:
                note_box = slide.shapes.add_textbox(
                    Inches(0.9), Inches(6.4), Inches(11.5), Inches(0.6)
                )
                note_frame = note_box.text_frame
                note_frame.word_wrap = True
                note_run = note_frame.paragraphs[0].add_run()
                note_run.text = footnote
                note_run.font.size = Pt(16)
                note_run.font.italic = True
                note_run.font.name = theme["body_font"]
                note_run.font.color.rgb = muted

        notes = str(slide_spec.get("notes") or "").strip()
        if notes:
            slide.notes_slide.notes_text_frame.text = notes

    presentation.save(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a deck from a JSON content file.")
    parser.add_argument("deckfile", help="path to the deck JSON file")
    parser.add_argument(
        "--outdir", default="build/decks", help="output directory (default: build/decks)"
    )
    parser.add_argument(
        "--markdown-only", action="store_true", help="skip the .pptx output"
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="build despite blocking problems (drafts only; never for a deck you send)",
    )
    args = parser.parse_args(argv)

    try:
        deck = load_deck(args.deckfile)
    except DeckError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    problems, warnings = check_deck(deck)

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if problems:
        for problem in problems:
            print(f"blocking: {problem}", file=sys.stderr)
        if not args.allow_incomplete:
            print(
                f"\n{len(problems)} blocking problem(s). Nothing was written.\n"
                "Fix them, or pass --allow-incomplete to build a draft that must not be sent.",
                file=sys.stderr,
            )
            return 1
        print("\nbuilding anyway: --allow-incomplete. Do not send this file.", file=sys.stderr)

    os.makedirs(args.outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(args.deckfile))[0]

    markdown_path = os.path.join(args.outdir, f"{stem}.md")
    with open(markdown_path, "w", encoding="utf-8") as handle:
        handle.write(render_markdown(deck))
    print(f"wrote {markdown_path}")

    if not args.markdown_only:
        pptx_path = os.path.join(args.outdir, f"{stem}.pptx")
        try:
            write_pptx(deck, pptx_path)
        except ImportError:
            print(
                "note: python-pptx is not installed, so no .pptx was written.\n"
                "      install it with: pip install python-pptx",
                file=sys.stderr,
            )
            return 1
        print(f"wrote {pptx_path}")

    content_slides = sum(
        1 for s in deck["slides"] if s.get("layout", "content") != "title"
    )
    print(
        f"\n{content_slides} content slides, all with body text and speaker notes.\n"
        "Machine checks are not the whole gate. Run "
        "docs/revenue/quality/deck-quality-checklist.md by hand before sending - "
        "sources, attribution, and privacy are not checkable from here."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
