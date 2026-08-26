from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


ORG_A = "11111111-1111-4111-8111-111111111111"
ORG_B = "22222222-2222-4222-8222-222222222222"
USER_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
USER_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
STUDENT_A = "33333333-3333-4333-8333-333333333333"
STUDENT_B = "44444444-4444-4444-8444-444444444444"
ASSESSMENT_A = "55555555-5555-4555-8555-555555555555"
ASSESSMENT_B = "66666666-6666-4666-8666-666666666666"
PLAN_A = "77777777-7777-4777-8777-777777777777"
PLAN_B = "88888888-8888-4888-8888-888888888888"
SCHOOL_A = "99999999-9999-4999-8999-999999999999"
SCHOOL_B = "10101010-1010-4010-8010-101010101010"


@dataclass
class FakeResponse:
    data: List[Dict[str, Any]]


class FakeQuery:
    def __init__(self, client: "FakeClient", table: str):
        self.client = client
        self.table = table
        self.operation = "select"
        self.filters: Dict[str, Any] = {}
        self.payload: Optional[Dict[str, Any]] = None
        self.row_limit: Optional[int] = None

    def select(self, *_args, **_kwargs):
        self.operation = "select"
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = deepcopy(payload)
        return self

    def eq(self, column: str, value: Any):
        self.filters[column] = value
        return self

    def limit(self, value: int):
        self.row_limit = value
        return self

    def execute(self) -> FakeResponse:
        self.client.queries.append(
            {
                "table": self.table,
                "operation": self.operation,
                "filters": deepcopy(self.filters),
                "payload": deepcopy(self.payload),
            }
        )

        if self.operation == "insert":
            row = deepcopy(self.payload or {})
            row.setdefault("id", self.client.next_id())
            self.client.tables.setdefault(self.table, []).append(row)
            return FakeResponse([deepcopy(row)])

        rows = [
            deepcopy(row)
            for row in self.client.tables.get(self.table, [])
            if all(row.get(key) == value for key, value in self.filters.items())
        ]
        if self.row_limit is not None:
            rows = rows[: self.row_limit]
        return FakeResponse(rows)


class FakeClient:
    def __init__(self, tables: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self.tables = deepcopy(tables or {})
        self.queries: List[Dict[str, Any]] = []
        self._id_counter = 0

    def table(self, name: str) -> FakeQuery:
        return FakeQuery(self, name)

    def next_id(self) -> str:
        self._id_counter += 1
        return f"00000000-0000-4000-8000-{self._id_counter:012d}"


def seeded_tables() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "users": [
            {
                "id": USER_A,
                "organization_id": ORG_A,
                "auth_user_id": "auth-user-a",
                "email": "ignored-a@example.test",
                "role": "teacher",
                "status": "active",
            },
            {
                "id": USER_B,
                "organization_id": ORG_B,
                "auth_user_id": "auth-user-b",
                "email": "ignored-b@example.test",
                "role": "admin",
                "status": "active",
            },
        ],
        "schools": [
            {"id": SCHOOL_A, "organization_id": ORG_A, "name": "A School"},
            {"id": SCHOOL_B, "organization_id": ORG_B, "name": "B School"},
        ],
        "students": [
            {
                "id": STUDENT_A,
                "organization_id": ORG_A,
                "created_by": USER_A,
                "first_name": "Ava",
                "last_name": "Alpha",
                "iep_status": False,
            },
            {
                "id": STUDENT_B,
                "organization_id": ORG_B,
                "created_by": USER_B,
                "first_name": "Ben",
                "last_name": "Beta",
                "iep_status": True,
            },
        ],
        "assessments": [
            {
                "id": ASSESSMENT_A,
                "organization_id": ORG_A,
                "student_id": STUDENT_A,
                "created_by": USER_A,
                "title": "A Reading Screen",
                "assessment_type": "curriculum_based",
                "status": "draft",
            },
            {
                "id": ASSESSMENT_B,
                "organization_id": ORG_B,
                "student_id": STUDENT_B,
                "created_by": USER_B,
                "title": "B Reading Screen",
                "assessment_type": "curriculum_based",
                "status": "draft",
            },
        ],
        "intervention_plans": [
            {
                "id": PLAN_A,
                "organization_id": ORG_A,
                "student_id": STUDENT_A,
                "created_by": USER_A,
                "title": "A Reading Plan",
                "status": "draft",
                "priority": "medium",
            },
            {
                "id": PLAN_B,
                "organization_id": ORG_B,
                "student_id": STUDENT_B,
                "created_by": USER_B,
                "title": "B Reading Plan",
                "status": "active",
                "priority": "high",
            },
        ],
    }
