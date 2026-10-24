"""Server-owned rubric registry.

Rubrics are versioned JSON files shipped with the backend. A rubric is usable
only when a human approver has pinned its exact content hash in
``AEOS_AI_FEEDBACK_APPROVED_RUBRICS`` as ``<id>@<version>:<sha256>``. Editing a
rubric changes its hash, so an edited rubric is unusable until re-approved.
Clients choose a rubric by id and version; they never send rubric content.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, FrozenSet, Tuple

RUBRIC_DIR = Path(__file__).resolve().parent / "rubrics"
_FILE_PATTERN = re.compile(r"^(?P<id>[A-Z0-9-]{1,64})\.v(?P<version>[0-9][0-9.]{0,31})\.json$")


class RubricNotFound(Exception):
    pass


class RubricNotApproved(Exception):
    pass


@dataclass(frozen=True)
class RubricCriterion:
    id: str
    name: str
    levels: Tuple[Tuple[str, str], ...]


@dataclass(frozen=True)
class Rubric:
    id: str
    version: str
    sha256: str
    status: str
    criteria: Tuple[RubricCriterion, ...]
    not_scored: str

    @property
    def criterion_ids(self) -> Tuple[str, ...]:
        return tuple(criterion.id for criterion in self.criteria)

    def approval_pin(self) -> str:
        return f"{self.id}@{self.version}:{self.sha256}"


def canonical_sha256(document: dict) -> str:
    canonical = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _parse(path: Path) -> Rubric:
    document = json.loads(path.read_text(encoding="utf-8"))
    criteria = tuple(
        RubricCriterion(
            id=str(item["id"]),
            name=str(item["name"]),
            levels=tuple((str(key), str(value)) for key, value in item["levels"].items()),
        )
        for item in document["criteria"]
    )
    if not criteria or len({c.id for c in criteria}) != len(criteria):
        raise ValueError(f"rubric {path.name} must define unique criteria")
    return Rubric(
        id=str(document["id"]),
        version=str(document["version"]),
        sha256=canonical_sha256(document),
        status=str(document.get("status", "")),
        criteria=criteria,
        not_scored=str(document.get("not_scored", "")),
    )


@lru_cache(maxsize=1)
def load_registry() -> Dict[Tuple[str, str], Rubric]:
    registry: Dict[Tuple[str, str], Rubric] = {}
    for path in sorted(RUBRIC_DIR.glob("*.json")):
        match = _FILE_PATTERN.match(path.name)
        if not match:
            raise ValueError(f"unexpected rubric file name: {path.name}")
        rubric = _parse(path)
        if (rubric.id, rubric.version) != (match["id"], match["version"]):
            raise ValueError(f"rubric file name does not match its id/version: {path.name}")
        registry[(rubric.id, rubric.version)] = rubric
    return registry


def get_approved_rubric(
    rubric_id: str,
    version: str,
    approved_pins: FrozenSet[str],
    registry: Dict[Tuple[str, str], Rubric] | None = None,
) -> Rubric:
    rubric = (registry if registry is not None else load_registry()).get((rubric_id, version))
    if rubric is None:
        raise RubricNotFound()
    if rubric.approval_pin() not in approved_pins:
        raise RubricNotApproved()
    return rubric
