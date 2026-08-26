"""Minimal in-memory fake Supabase client for two-tenant route tests.

Implements only the subset of the real client's interface these routes
use: client.table(name).select("*").eq(col, val)...limit(n).execute() for
reads, and client.table(name).insert(payload).execute() for writes. Rows
are plain dicts stored per table, so tests can seed two (or more) tenants'
data and assert that queries scoped by organization_id only ever see the
right tenant's rows.

This is a test double for the external Supabase-client boundary, not a
mock of any function under test - route handlers and the tenant_scope
helpers run for real against it.
"""
import itertools
from typing import Any, Dict, Iterable, List

_id_counter = itertools.count(1)


class FakeResponse:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data


class _FakeQuery:
    def __init__(self, rows: List[Dict[str, Any]]):
        self._rows = rows
        self._filters: Dict[str, Any] = {}
        self._limit = None

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, column: str, value: Any):
        self._filters[column] = value
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def execute(self) -> FakeResponse:
        matched = [
            row for row in self._rows
            if all(row.get(k) == v for k, v in self._filters.items())
        ]
        if self._limit is not None:
            matched = matched[: self._limit]
        return FakeResponse(matched)


class _FakeInsert:
    def __init__(self, table_rows: List[Dict[str, Any]], payload: Dict[str, Any]):
        self._table_rows = table_rows
        self._payload = payload

    def execute(self) -> FakeResponse:
        row = dict(self._payload)
        row.setdefault("id", f"generated-id-{next(_id_counter)}")
        self._table_rows.append(row)
        return FakeResponse([row])


class _FakeTable:
    def __init__(self, rows: List[Dict[str, Any]]):
        self._rows = rows

    def select(self, *args, **kwargs) -> _FakeQuery:
        return _FakeQuery(self._rows)

    def insert(self, payload: Dict[str, Any]) -> _FakeInsert:
        return _FakeInsert(self._rows, payload)


class FakeSupabaseClient:
    def __init__(self):
        self._tables: Dict[str, List[Dict[str, Any]]] = {}

    def seed(self, table: str, rows: Iterable[Dict[str, Any]]) -> "FakeSupabaseClient":
        self._tables.setdefault(table, []).extend(rows)
        return self

    def rows(self, table: str) -> List[Dict[str, Any]]:
        return self._tables.setdefault(table, [])

    def table(self, name: str) -> _FakeTable:
        return _FakeTable(self._tables.setdefault(name, []))
