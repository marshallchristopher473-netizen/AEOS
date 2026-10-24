#!/usr/bin/env python3
"""Verify the frozen AEOS teacher ELA pilot packet v1.0.

Checks, in order:
  1. Every file in FREEZE_MANIFEST.sha256 matches its recorded SHA-256, and
     every file under frozen/ is listed.
  2. The synthetic-response hashes written into PACKET.md match the files.
  3. KEY-ELA-01 is internally consistent and quotes each response verbatim.
  4. The matched X/Y design holds: three responses per set, identical rubric
     profiles across pairs, and pair lengths within 10%.
  5. Every MockAssisted-ELA card differs from the key in exactly one way, and
     that way is the seeded error the register records for it.
  6. Seeded-error types come only from the approved list and are balanced.

Standard library only. Exit 0 when every check passes, 1 otherwise.

Usage: python3 -I docs/pilots/teacher-ela-v1/verify_packet.py
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT / "frozen"
DIMENSIONS = ("Claim", "Evidence", "Reasoning", "Conventions")
APPROVED_ERROR_TYPES = {
    "score mismatch",
    "unsupported evidence citation",
    "omitted rubric criterion",
    "incorrect evidence location",
}
SET_X = ("SYN-01", "SYN-02", "SYN-03")
SET_Y = ("SYN-04", "SYN-05", "SYN-06")
PAIRS = tuple(zip(SET_X, SET_Y))
EXPECTED_TOTALS = (12, 8, 5)
MAX_LENGTH_GAP = 0.10

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def locations(text: str) -> frozenset[int]:
    found = re.findall(r"¶(\d)", text)
    if not found:
        raise ValueError(f"no paragraph location in {text!r}")
    numbers = frozenset(int(n) for n in found)
    if not numbers <= {1, 2, 3, 4, 5}:
        raise ValueError(f"paragraph outside ¶1-¶5 in {text!r}")
    return numbers


def response_body(syn_id: str) -> str:
    text = (FROZEN / "responses" / f"{syn_id}.md").read_text(encoding="utf-8")
    parts = text.split("\n\n", 2)
    if len(parts) != 3 or parts[0] != f"# {syn_id}":
        raise ValueError(f"{syn_id}.md does not have the header/notice/body layout")
    return parts[2].strip()


def sections(text: str) -> dict[str, str]:
    chunks = re.split(r"^## (SYN-\d\d)\s*$", text, flags=re.M)
    return {chunks[i]: chunks[i + 1] for i in range(1, len(chunks), 2)}


def parse_key() -> dict[str, dict]:
    text = (FROZEN / "facilitator-only" / "KEY-ELA-01.md").read_text(encoding="utf-8")
    key: dict[str, dict] = {}
    for syn_id, body in sections(text).items():
        scores = {
            m[1]: int(m[2])
            for m in re.finditer(r"^\| (Claim|Evidence|Reasoning|Conventions) \| (\d) \|", body, re.M)
        }
        total = re.search(r"^\| \*\*Total\*\* \| \*\*(\d+)\*\* \|", body, re.M)
        items = []
        for m in re.finditer(r'^\| ([KX]\d) \| "(.+?)" \| (.+?) \| (.+?) \|$', body, re.M):
            status = m[3]
            items.append(
                {
                    "id": m[1],
                    "quote": m[2],
                    "inaccurate": status.startswith("inaccurate"),
                    "specific": "specific" in status,
                    "required": "required" in status or "must be marked" in status,
                    "accepted": [locations(alt) for alt in m[4].split(" or ")],
                }
            )
        key[syn_id] = {"scores": scores, "total": int(total[1]) if total else None, "items": items}
    return key


def parse_card(syn_id: str) -> dict:
    text = (FROZEN / "outputs" / f"{syn_id}.output.md").read_text(encoding="utf-8")
    scores = {
        m[1]: int(m[2])
        for m in re.finditer(r"^\| (Claim|Evidence|Reasoning|Conventions) \| (\d) \|", text, re.M)
    }
    total = re.search(r"^\| Suggested total \| (\d+) \|", text, re.M)
    rows = [
        {
            "row": m[1],
            "quote": m[2],
            "where": locations(m[3]),
            "inaccurate": m[4].startswith("inaccurate"),
            "specific": "specific" in m[4],
        }
        for m in re.finditer(r'^\| (E\d) \| "(.+?)" \| (.+?) \| (.+?) \|$', text, re.M)
    ]
    leaks = [w for w in ("seeded", "ERR-", "KEY-ELA") if w in text]
    return {"scores": scores, "total": int(total[1]) if total else None, "rows": rows, "leaks": leaks}


def parse_register() -> dict[str, dict]:
    text = (FROZEN / "facilitator-only" / "SEEDED-ERROR-REGISTER.v1.0.md").read_text(encoding="utf-8")
    register: dict[str, dict] = {}
    for m in re.finditer(r"^\| (ERR-\d\d) \| (SYN-\d\d) \| ([XY]) \| ([a-z ]+?) \| (.+?) \|", text, re.M):
        check(m[2] not in register, f"register lists {m[2]} more than once")
        register[m[2]] = {"error_id": m[1], "set": m[3], "type": m[4], "where": m[5]}
    return register


def card_discrepancies(syn_id: str, card: dict, expected: dict, body: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for dim in DIMENSIONS:
        if dim not in card["scores"]:
            found.append(("omitted rubric criterion", dim))
        elif card["scores"][dim] != expected["scores"][dim]:
            found.append(("score mismatch", dim))
    check(
        card["total"] == sum(card["scores"].values()),
        f"{syn_id} card: suggested total {card['total']} is not the sum of its shown scores",
    )
    matched_items = set()
    for row in card["rows"]:
        if row["quote"] not in body:
            found.append(("unsupported evidence citation", row["row"]))
            continue
        item = next((i for i in expected["items"] if i["quote"] == row["quote"]), None)
        if item is None:
            found.append(("evidence row not in key", row["row"]))
            continue
        matched_items.add(item["id"])
        if row["where"] not in item["accepted"]:
            found.append(("incorrect evidence location", row["row"]))
        if row["inaccurate"] != item["inaccurate"]:
            found.append(("credited status differs from key", row["row"]))
        if row["specific"] != item["specific"]:
            found.append(("label differs from key", row["row"]))
    for item in expected["items"]:
        if item["required"] and item["id"] not in matched_items:
            found.append(("required key item missing from card", item["id"]))
    return found


def main() -> int:
    # 1. Freeze manifest.
    manifest_path = ROOT / "FREEZE_MANIFEST.sha256"
    listed: set[Path] = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(maxsplit=1)
        path = ROOT / rel
        listed.add(path)
        check(path.is_file(), f"manifest lists missing file {rel}")
        if path.is_file():
            check(sha256(path) == digest, f"HASH MISMATCH: {rel}")
    for path in FROZEN.rglob("*"):
        if path.is_file():
            check(path in listed, f"frozen file not in manifest: {path.relative_to(ROOT)}")
    check(ROOT / "PACKET.md" in listed, "PACKET.md is not in the manifest")

    # 2. Register hashes inside PACKET.md.
    packet = (ROOT / "PACKET.md").read_text(encoding="utf-8")
    packet_rows = {
        f"SYN-{m[1]}": (m[2], m[3])
        for m in re.finditer(r"^\| SYN-(\d\d) \| `([0-9a-f]{64})` \| ([XY]) \|", packet, re.M)
    }
    check(sorted(packet_rows) == sorted(SET_X + SET_Y), f"PACKET.md register rows: {sorted(packet_rows)}")
    for syn_id, (digest, set_label) in packet_rows.items():
        check(digest == sha256(FROZEN / "responses" / f"{syn_id}.md"), f"PACKET.md hash for {syn_id} is stale")
        check(set_label == ("X" if syn_id in SET_X else "Y"), f"PACKET.md puts {syn_id} in set {set_label}")
    indexed = re.findall(r"`(frozen/[^`]+)` \| [^|]+ \| `([0-9a-f]{64})`", packet)
    check(len(indexed) >= 12, f"PACKET.md asset index lists only {len(indexed)} hashed files")
    for rel, digest in indexed:
        check((ROOT / rel).is_file() and digest == sha256(ROOT / rel), f"PACKET.md asset index hash for {rel} is stale")

    # 3. Key consistency.
    key = parse_key()
    check(sorted(key) == sorted(SET_X + SET_Y), f"key covers {sorted(key)}")
    bodies = {syn_id: response_body(syn_id) for syn_id in SET_X + SET_Y}
    for syn_id, entry in key.items():
        check(tuple(entry["scores"]) == DIMENSIONS, f"{syn_id} key dimensions: {tuple(entry['scores'])}")
        check(entry["total"] == sum(entry["scores"].values()), f"{syn_id} key total is not the sum")
        if entry["scores"]["Evidence"] > 1:
            check(not any(i["inaccurate"] for i in entry["items"]), f"{syn_id}: inaccurate detail but Evidence > 1")
        for item in entry["items"]:
            check(item["quote"] in bodies[syn_id], f"{syn_id} key {item['id']} is not verbatim in the response")

    # 4. Matched design.
    for (x_id, y_id), total in zip(PAIRS, EXPECTED_TOTALS):
        check(key[x_id]["scores"] == key[y_id]["scores"], f"{x_id}/{y_id} rubric profiles differ")
        check(key[x_id]["total"] == total, f"{x_id} total {key[x_id]['total']} != {total}")
        x_words, y_words = len(bodies[x_id].split()), len(bodies[y_id].split())
        gap = abs(x_words - y_words) / max(x_words, y_words)
        check(gap <= MAX_LENGTH_GAP, f"{x_id}/{y_id} length gap {gap:.0%} ({x_words} vs {y_words} words)")

    # 5 and 6. Cards against the key and the register.
    register = parse_register()
    check(sorted(register) == sorted(SET_X + SET_Y), f"register covers {sorted(register)}")
    for syn_id in SET_X + SET_Y:
        seeded = register.get(syn_id)
        if seeded is None:
            continue
        check(seeded["type"] in APPROVED_ERROR_TYPES, f"{syn_id}: unapproved error type {seeded['type']!r}")
        check(seeded["set"] == ("X" if syn_id in SET_X else "Y"), f"{syn_id}: register set is wrong")
        card = parse_card(syn_id)
        check(not card["leaks"], f"{syn_id} card mentions facilitator-only terms {card['leaks']}")
        found = card_discrepancies(syn_id, card, key[syn_id], bodies[syn_id])
        # A score mismatch on Evidence also shows up as relabelled rows; that is the same error.
        if seeded["type"] == "score mismatch" and "Evidence" in seeded["where"]:
            found = [d for d in found if d[0] != "label differs from key"]
        check(len(found) == 1, f"{syn_id} card: expected exactly one discrepancy, found {found}")
        if len(found) == 1:
            kind, where = found[0]
            check(kind == seeded["type"], f"{syn_id} card: discrepancy {kind!r} != register {seeded['type']!r}")
            if kind == "score mismatch":
                check(where in seeded["where"], f"{syn_id}: mismatch on {where}, register says {seeded['where']!r}")
    for set_ids, label in ((SET_X, "X"), (SET_Y, "Y")):
        types = [register[s]["type"] for s in set_ids if s in register]
        check(len(set(types)) == 3, f"set {label} error types are not three distinct types: {types}")
    all_types = sorted(r["type"] for r in register.values())
    check(
        all_types
        == sorted(["score mismatch"] * 2 + ["unsupported evidence citation"] * 2
                  + ["omitted rubric criterion", "incorrect evidence location"]),
        f"error-type mix is {all_types}",
    )

    if failures:
        print(f"FAIL: {len(failures)} check(s) failed")
        for message in failures:
            print(f"  - {message}")
        return 1
    print(f"PASS: {len(listed)} manifest files verified; design, key, cards, and register consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
