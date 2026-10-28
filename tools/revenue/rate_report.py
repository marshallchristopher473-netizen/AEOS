#!/usr/bin/env python3
"""Report the effective hourly rate of each AEOS income experiment.

The point of this tool is to answer one question honestly: is the work paying?
An effective rate is net income divided by *every* hour spent, including the
acquisition and admin hours that are easy to forget and that quietly destroy an
hourly rate.

Usage:
    python3 tools/revenue/rate_report.py docs/revenue/evidence/time-and-income-log.csv
    python3 tools/revenue/rate_report.py <log.csv> --target-rate 50 --capacity-hours 4

Log format (docs/revenue/evidence/time-and-income-log.csv):
    date,experiment,category,activity,hours,amount_usd,notes

    category is one of:
      acquisition  hours spent finding and closing work
      delivery     hours spent doing the work
      admin        hours spent on invoicing, applications, handoff
      income       money received   (amount_usd, positive; leave hours blank)
      fee          money taken out  (amount_usd, positive; it is subtracted)

Amounts are always written as positive numbers. The category decides whether a
number is added or subtracted, so there are no minus signs to get wrong.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from dataclasses import dataclass, field

HOUR_CATEGORIES = ("acquisition", "delivery", "admin")
MONEY_CATEGORIES = ("income", "fee")
VALID_CATEGORIES = HOUR_CATEGORIES + MONEY_CATEGORIES

REQUIRED_COLUMNS = {
    "date",
    "experiment",
    "category",
    "activity",
    "hours",
    "amount_usd",
    "notes",
}


class LogError(ValueError):
    """Raised when the log file cannot be trusted as evidence."""


@dataclass
class Entry:
    date: dt.date
    experiment: str
    category: str
    activity: str
    hours: float
    amount_usd: float
    notes: str
    line_number: int


@dataclass
class Totals:
    experiment: str
    hours_by_category: dict[str, float] = field(
        default_factory=lambda: {c: 0.0 for c in HOUR_CATEGORIES}
    )
    income: float = 0.0
    fees: float = 0.0

    @property
    def total_hours(self) -> float:
        return sum(self.hours_by_category.values())

    @property
    def net_income(self) -> float:
        return self.income - self.fees

    @property
    def effective_rate(self) -> float | None:
        """Net income per hour worked, or None when no hours are logged yet."""
        if self.total_hours <= 0:
            return None
        return self.net_income / self.total_hours


def _parse_number(raw: str, field_name: str, line_number: int) -> float:
    text = (raw or "").strip()
    if not text:
        return 0.0
    cleaned = text.replace("$", "").replace(",", "")
    try:
        value = float(cleaned)
    except ValueError as exc:
        raise LogError(
            f"line {line_number}: {field_name} is {text!r}, which is not a number"
        ) from exc
    if value < 0:
        raise LogError(
            f"line {line_number}: {field_name} is negative ({value}). "
            "Write amounts as positive numbers and use the 'fee' category for money taken out."
        )
    return value


def parse_entries(rows, columns) -> list[Entry]:
    """Turn CSV rows into validated entries, or explain exactly what is wrong."""
    if columns is None:
        raise LogError("the log file is empty; it needs at least a header row")

    missing = REQUIRED_COLUMNS - set(columns)
    if missing:
        raise LogError(
            "the log is missing required column(s): " + ", ".join(sorted(missing))
        )

    entries: list[Entry] = []
    for offset, row in enumerate(rows):
        line_number = offset + 2  # +1 for the header, +1 for 1-based counting
        if not any((value or "").strip() for value in row.values()):
            continue

        category = (row.get("category") or "").strip().lower()
        if category not in VALID_CATEGORIES:
            raise LogError(
                f"line {line_number}: category is {category!r}; expected one of "
                + ", ".join(VALID_CATEGORIES)
            )

        experiment = (row.get("experiment") or "").strip()
        if not experiment:
            raise LogError(f"line {line_number}: experiment is blank")

        raw_date = (row.get("date") or "").strip()
        try:
            date = dt.date.fromisoformat(raw_date)
        except ValueError as exc:
            raise LogError(
                f"line {line_number}: date is {raw_date!r}; expected YYYY-MM-DD"
            ) from exc

        hours = _parse_number(row.get("hours", ""), "hours", line_number)
        amount = _parse_number(row.get("amount_usd", ""), "amount_usd", line_number)

        if category in HOUR_CATEGORIES and hours <= 0:
            raise LogError(
                f"line {line_number}: a {category} row needs hours greater than zero"
            )
        if category in MONEY_CATEGORIES and amount <= 0:
            raise LogError(
                f"line {line_number}: a {category} row needs amount_usd greater than zero"
            )

        entries.append(
            Entry(
                date=date,
                experiment=experiment,
                category=category,
                activity=(row.get("activity") or "").strip(),
                hours=hours,
                amount_usd=amount,
                notes=(row.get("notes") or "").strip(),
                line_number=line_number,
            )
        )
    return entries


def read_log(path: str) -> list[Entry]:
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return parse_entries(list(reader), reader.fieldnames)
    except FileNotFoundError as exc:
        raise LogError(f"no log file at {path}") from exc


def summarize(entries: list[Entry]) -> dict[str, Totals]:
    totals: dict[str, Totals] = {}
    for entry in entries:
        bucket = totals.setdefault(entry.experiment, Totals(experiment=entry.experiment))
        if entry.category in HOUR_CATEGORIES:
            bucket.hours_by_category[entry.category] += entry.hours
        elif entry.category == "income":
            bucket.income += entry.amount_usd
        elif entry.category == "fee":
            bucket.fees += entry.amount_usd
    return totals


def weekly_hours(entries: list[Entry]) -> dict[tuple[int, int], float]:
    """Hours worked per ISO week, for checking the capacity limit."""
    weeks: dict[tuple[int, int], float] = {}
    for entry in entries:
        if entry.category not in HOUR_CATEGORIES:
            continue
        iso = entry.date.isocalendar()
        key = (iso.year, iso.week)
        weeks[key] = weeks.get(key, 0.0) + entry.hours
    return weeks


def _rate_text(totals: Totals) -> str:
    rate = totals.effective_rate
    if rate is None:
        return "n/a"
    return f"${rate:,.2f}/hr"


def _verdict(totals: Totals, target_rate: float) -> str:
    rate = totals.effective_rate
    if rate is None:
        return "-"
    if totals.net_income <= 0:
        return "UNPAID"
    return "PASS" if rate >= target_rate else "BELOW TARGET"


def build_report(
    entries: list[Entry], target_rate: float, capacity_hours: float
) -> list[str]:
    lines: list[str] = []
    lines.append("AEOS revenue — effective rate report")
    lines.append("=" * 72)

    if not entries:
        lines.append("")
        lines.append("The log is empty. Nothing has been measured yet.")
        lines.append("Add one row per work session and per payment, then run this again.")
        return lines

    first = min(e.date for e in entries)
    last = max(e.date for e in entries)
    lines.append(f"Period: {first.isoformat()} to {last.isoformat()}")
    lines.append(f"Target rate: ${target_rate:,.2f}/hr")
    lines.append("")

    totals = summarize(entries)
    header = (
        f"{'experiment':<20}{'acq':>7}{'del':>7}{'adm':>7}"
        f"{'hours':>8}{'net $':>11}{'rate':>14}  verdict"
    )
    lines.append(header)
    lines.append("-" * 72)

    grand = Totals(experiment="ALL")
    for name in sorted(totals):
        item = totals[name]
        lines.append(
            f"{name[:19]:<20}"
            f"{item.hours_by_category['acquisition']:>7.2f}"
            f"{item.hours_by_category['delivery']:>7.2f}"
            f"{item.hours_by_category['admin']:>7.2f}"
            f"{item.total_hours:>8.2f}"
            f"{item.net_income:>11,.2f}"
            f"{_rate_text(item):>14}"
            f"  {_verdict(item, target_rate)}"
        )
        for category in HOUR_CATEGORIES:
            grand.hours_by_category[category] += item.hours_by_category[category]
        grand.income += item.income
        grand.fees += item.fees

    lines.append("-" * 72)
    lines.append(
        f"{'ALL':<20}"
        f"{grand.hours_by_category['acquisition']:>7.2f}"
        f"{grand.hours_by_category['delivery']:>7.2f}"
        f"{grand.hours_by_category['admin']:>7.2f}"
        f"{grand.total_hours:>8.2f}"
        f"{grand.net_income:>11,.2f}"
        f"{_rate_text(grand):>14}"
        f"  {_verdict(grand, target_rate)}"
    )

    if grand.fees > 0:
        lines.append("")
        lines.append(
            f"Gross income ${grand.income:,.2f} less fees ${grand.fees:,.2f} "
            f"= net ${grand.net_income:,.2f}."
        )

    weeks = weekly_hours(entries)
    if weeks:
        lines.append("")
        lines.append(f"Weekly load (capacity limit {capacity_hours:.1f} hrs/week)")
        lines.append("-" * 72)
        for (year, week) in sorted(weeks):
            hours = weeks[(year, week)]
            flag = "  OVER CAPACITY" if hours > capacity_hours else ""
            lines.append(f"  {year}-W{week:02d}  {hours:>6.2f} hrs{flag}")

    notes = _observations(totals, grand, target_rate)
    if notes:
        lines.append("")
        lines.append("Observations")
        lines.append("-" * 72)
        lines.extend(f"  - {note}" for note in notes)

    return lines


def _observations(
    totals: dict[str, Totals], grand: Totals, target_rate: float
) -> list[str]:
    notes: list[str] = []

    for name in sorted(totals):
        item = totals[name]
        if item.income > 0 and item.total_hours == 0:
            notes.append(
                f"{name}: income recorded but no hours. The rate cannot be trusted "
                "until the hours are logged."
            )
        if item.total_hours > 0 and item.income == 0:
            notes.append(
                f"{name}: {item.total_hours:.2f} hrs invested, no income yet. "
                "This is normal early; it stops being normal once a threshold date passes."
            )

    if grand.total_hours > 0 and grand.income > 0:
        acquisition_share = (
            grand.hours_by_category["acquisition"] / grand.total_hours * 100
        )
        if acquisition_share >= 40:
            notes.append(
                f"Acquisition is {acquisition_share:.0f}% of all hours. Selling, not "
                "delivery, is the cost driver here."
            )

    rate = grand.effective_rate
    if rate is not None and grand.income > 0 and rate < target_rate:
        shortfall_hours = grand.net_income / target_rate
        notes.append(
            f"Overall rate ${rate:,.2f}/hr is below the ${target_rate:,.2f} target. "
            f"The same income at target would have taken {shortfall_hours:.1f} hrs, "
            f"not {grand.total_hours:.1f}."
        )

    return notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report effective hourly rate per income experiment."
    )
    parser.add_argument("logfile", help="path to the time and income CSV log")
    parser.add_argument(
        "--target-rate",
        type=float,
        default=50.0,
        help="effective hourly rate that counts as a pass (default: 50)",
    )
    parser.add_argument(
        "--capacity-hours",
        type=float,
        default=4.0,
        help="weekly hour limit across all experiments (default: 4)",
    )
    args = parser.parse_args(argv)

    try:
        entries = read_log(args.logfile)
    except LogError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for line in build_report(entries, args.target_rate, args.capacity_hours):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
