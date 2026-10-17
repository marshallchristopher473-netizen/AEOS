"""Executed proof for migration 006 against real PostgreSQL.

Covers what the in-memory fake cannot: RLS on the new tables, the append-only
trigger (with a negative control), audit rows written atomically with each
save, cross-organization integrity triggers, and the reservation function's
idempotency, limits and concurrency.

Synthetic rows only. Uses the session database and fixtures from
test_rls_enforcement.py, which applies migrations 001-006. Every test either
rolls back or deletes what it committed.
"""

import json
import threading
import uuid

import pytest

from tests.test_rls_enforcement import (  # noqa: F401 - fixtures are used by name
    ADMIN_A,
    ASSESSMENT_A,
    ASSESSMENT_B,
    DATABASE_URL,
    ORG_A,
    ORG_B,
    PEER_A,
    STUDENT_A,
    SUPPORT_A,
    USER_A,
    USER_B,
    admin_conn,
    as_org_a,
    as_org_a_support,
    as_org_b,
    migrated_database,
    psycopg,
)

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="AEOS_TEST_DATABASE_URL is not set; migration 006 tests require PostgreSQL",
)

SHA = "a" * 64
LIMITS = {
    "user_hourly_requests": 5,
    "org_daily_requests": 50,
    "user_daily_cost_microusd": 1_000,
    "org_daily_cost_microusd": 5_000,
}


def request_row(**changes):
    row = {
        "id": str(uuid.uuid4()),
        "organization_id": ORG_A,
        "assessment_id": ASSESSMENT_A,
        "student_id": STUDENT_A,
        "created_by": USER_A,
        "request_key": str(uuid.uuid4()),
        "input_sha256": SHA,
        "data_classification": "synthetic",
        "response_text": "Synthetic response about cool roofs.",
        "source_text": None,
        "rubric_id": "RUB-CER3",
        "rubric_version": "0.1",
        "rubric_sha256": SHA,
        "prompt_version": "aeos-ela-feedback-draft-v1",
        "provider": "anthropic",
        "model_id": "configured-model-under-test",
        "reserved_cost_microusd": 100,
    }
    row.update(changes)
    return row


def as_service_role(conn):
    conn.execute("SET LOCAL ROLE service_role")


def reserve(conn, limits=None, **changes):
    row = request_row(**changes)
    (result,) = conn.execute(
        "SELECT public.aeos_reserve_ai_feedback_request(%s::jsonb, %s::jsonb)",
        (json.dumps(row), json.dumps(LIMITS if limits is None else limits)),
    ).fetchone()
    return row, result


def insert_draft(conn, request_id, status="ready", actual_cost=10, org=ORG_A):
    draft_id = str(uuid.uuid4())
    reviewable = status in ("ready", "abstained")
    conn.execute(
        "INSERT INTO public.ai_feedback_drafts "
        "(id, organization_id, request_id, status, output, draft_text, error_code, actual_cost_microusd) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            draft_id, org, request_id, status,
            json.dumps({"criteria": []}) if reviewable else None,
            "Synthetic draft" if status == "ready" else None,
            None if reviewable else "provider_unavailable",
            actual_cost,
        ),
    )
    return draft_id


def insert_decision(conn, draft_id, decision="accepted", decided_by=USER_A, text="Synthetic draft", confirmed=True):
    decision_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO public.ai_feedback_decisions "
        "(id, organization_id, draft_id, decided_by, decision, approved_text, teacher_confirmed, "
        " decision_key, payload_sha256) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (decision_id, ORG_A, draft_id, decided_by, decision, text, confirmed, str(uuid.uuid4()), SHA),
    )
    return decision_id


@pytest.fixture
def service(migrated_database):
    """Service-role session. Always rolled back."""
    with psycopg.connect(migrated_database) as conn:
        conn.execute("SET lock_timeout = '10s'")
        as_service_role(conn)
        try:
            yield conn
        finally:
            conn.rollback()


@pytest.fixture
def committed_chain(admin_conn):
    """One committed request -> draft -> decision in organization A, removed
    afterwards (DELETE is allowed to the owner; only UPDATE is refused)."""
    row, result = reserve(admin_conn)
    assert result["outcome"] == "reserved"
    draft_id = insert_draft(admin_conn, row["id"])
    decision_id = insert_decision(admin_conn, draft_id)
    try:
        yield {"request_id": row["id"], "draft_id": draft_id, "decision_id": decision_id}
    finally:
        admin_conn.execute("DELETE FROM public.ai_feedback_requests WHERE id = %s", (row["id"],))
        admin_conn.execute(
            "DELETE FROM public.audit_logs WHERE entity_id = ANY(%s::uuid[])", ([draft_id, decision_id],)
        )


TABLES = ("ai_feedback_requests", "ai_feedback_drafts", "ai_feedback_decisions")


# ---------------------------------------------------------------------------
# RLS: tenant reads, no client writes.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("table", TABLES)
def test_members_read_their_organization_and_other_tenants_see_nothing(
    committed_chain, as_org_a, as_org_a_support, as_org_b, table
):
    own = as_org_a.execute(f"SELECT count(*) FROM public.{table}").fetchone()[0]
    support = as_org_a_support.execute(f"SELECT count(*) FROM public.{table}").fetchone()[0]
    foreign = as_org_b.execute(f"SELECT count(*) FROM public.{table}").fetchone()[0]
    for conn in (as_org_a, as_org_a_support, as_org_b):
        conn.rollback()
    assert own == 1 and support == 1
    assert foreign == 0


def test_rls_negative_control_foreign_rows_leak_without_the_policy(committed_chain, admin_conn, as_org_b):
    admin_conn.execute("ALTER TABLE public.ai_feedback_drafts DISABLE ROW LEVEL SECURITY")
    try:
        leaked = as_org_b.execute(
            "SELECT count(*) FROM public.ai_feedback_drafts WHERE organization_id = %s", (ORG_A,)
        ).fetchone()[0]
        as_org_b.rollback()
    finally:
        admin_conn.execute("ALTER TABLE public.ai_feedback_drafts ENABLE ROW LEVEL SECURITY")
    assert leaked == 1, "with RLS disabled the row must be visible, or the denial test proves nothing"


def test_teacher_cannot_write_any_feedback_table_directly(committed_chain, as_org_a):
    attempts = [
        ("INSERT INTO public.ai_feedback_requests SELECT * FROM jsonb_populate_record("
         "NULL::public.ai_feedback_requests, %s::jsonb)", (json.dumps({**request_row(), "created_at": "2026-01-01"}),)),
        ("INSERT INTO public.ai_feedback_drafts (id, organization_id, request_id, status, error_code) "
         "VALUES (gen_random_uuid(), %s, %s, 'provider_error', 'x')", (ORG_A, committed_chain["request_id"])),
        ("INSERT INTO public.ai_feedback_decisions (id, organization_id, draft_id, decided_by, decision, "
         "teacher_confirmed, decision_key, payload_sha256) VALUES (gen_random_uuid(), %s, %s, %s, 'rejected', "
         "true, gen_random_uuid(), %s)", (ORG_A, committed_chain["draft_id"], USER_A, SHA)),
    ]
    for sql, params in attempts:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            as_org_a.execute(sql, params)
        as_org_a.rollback()

    for table in TABLES:
        as_org_a.execute(f"DELETE FROM public.{table}")
        assert as_org_a.execute(f"SELECT count(*) FROM public.{table}").fetchone()[0] == 1
        as_org_a.rollback()


@pytest.mark.parametrize("role", ["anon", "authenticated"])
def test_client_roles_cannot_execute_the_reservation_function(migrated_database, role):
    with psycopg.connect(migrated_database) as conn:
        conn.execute(f"SET ROLE {role}")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            reserve(conn)


# ---------------------------------------------------------------------------
# Append-only.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("table", "column", "key"),
    [
        ("ai_feedback_requests", "response_text", "request_id"),
        ("ai_feedback_drafts", "draft_text", "draft_id"),
        ("ai_feedback_decisions", "approved_text", "decision_id"),
    ],
)
def test_no_role_can_update_feedback_rows(committed_chain, service, table, column, key):
    with pytest.raises(psycopg.errors.FeatureNotSupported):
        service.execute(f"UPDATE public.{table} SET {column} = 'tampered' WHERE id = %s", (committed_chain[key],))


def test_owner_cannot_rewrite_the_ai_draft_into_teacher_text(committed_chain, admin_conn):
    with pytest.raises(psycopg.errors.FeatureNotSupported):
        admin_conn.execute(
            "UPDATE public.ai_feedback_drafts SET draft_text = 'Teacher approved' WHERE id = %s",
            (committed_chain["draft_id"],),
        )


def test_append_only_negative_control_update_succeeds_without_the_trigger(committed_chain, migrated_database):
    with psycopg.connect(migrated_database) as conn:
        try:
            conn.execute("ALTER TABLE public.ai_feedback_drafts DISABLE TRIGGER ai_feedback_drafts_append_only")
            updated = conn.execute(
                "UPDATE public.ai_feedback_drafts SET draft_text = 'tampered' WHERE id = %s",
                (committed_chain["draft_id"],),
            ).rowcount
        finally:
            conn.rollback()
    assert updated == 1, "without the trigger the update must succeed, or the trigger test proves nothing"


# ---------------------------------------------------------------------------
# Audit accountability.
# ---------------------------------------------------------------------------


def test_draft_and_decision_saves_write_audit_rows_without_student_text(committed_chain, admin_conn):
    rows = admin_conn.execute(
        "SELECT entity_type, action, performed_by::text, organization_id::text, metadata "
        "FROM public.audit_logs WHERE entity_id = ANY(%s::uuid[]) ORDER BY entity_type DESC",
        ([committed_chain["draft_id"], committed_chain["decision_id"]],),
    ).fetchall()

    assert [(r[0], r[1], r[2], r[3]) for r in rows] == [
        ("ai_feedback_draft", "ai_feedback.draft.ready", USER_A, ORG_A),
        ("ai_feedback_decision", "ai_feedback.decision.accepted", USER_A, ORG_A),
    ]
    draft_meta = rows[0][4]
    assert draft_meta["model_id"] == "configured-model-under-test"
    assert draft_meta["prompt_version"] == "aeos-ela-feedback-draft-v1"
    assert draft_meta["rubric_version"] == "0.1"
    assert "Synthetic response" not in json.dumps([r[4] for r in rows])


def test_a_save_fails_when_its_audit_row_cannot_be_written(service, admin_conn):
    row, result = reserve(service)
    assert result["outcome"] == "reserved"
    service.execute("RESET ROLE")
    service.execute(
        "ALTER TABLE public.audit_logs ADD CONSTRAINT probe_block_feedback_audit "
        "CHECK (entity_type <> 'ai_feedback_draft') NOT VALID"
    )
    as_service_role(service)
    with pytest.raises(psycopg.errors.CheckViolation):
        insert_draft(service, row["id"])
    service.rollback()
    assert admin_conn.execute(
        "SELECT count(*) FROM public.ai_feedback_drafts WHERE request_id = %s", (row["id"],)
    ).fetchone()[0] == 0


# ---------------------------------------------------------------------------
# Integrity and shape constraints.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "changes",
    [
        {"assessment_id": ASSESSMENT_B},
        {"organization_id": ORG_B},
        {"created_by": SUPPORT_A},
        {"created_by": USER_B},
    ],
)
def test_requests_must_stay_inside_one_organization_and_come_from_a_writer(service, changes):
    with pytest.raises(psycopg.errors.CheckViolation):
        reserve(service, **changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"data_classification": "real"},
        {"response_text": "x" * 4001},
        {"input_sha256": "not-a-hash"},
        {"reserved_cost_microusd": 0},
    ],
)
def test_request_shape_constraints(service, changes):
    with pytest.raises(psycopg.errors.CheckViolation):
        reserve(service, **changes)


def test_decisions_require_reviewable_drafts_writers_and_explicit_confirmation(service):
    ready_row, _ = reserve(service)
    ready = insert_draft(service, ready_row["id"], status="ready")
    abstained_row, _ = reserve(service)
    abstained = insert_draft(service, abstained_row["id"], status="abstained")
    failed_row, _ = reserve(service)
    failed = insert_draft(service, failed_row["id"], status="provider_error", actual_cost=0)

    cases = [
        lambda: insert_decision(service, failed, decision="rejected", text=None),
        lambda: insert_decision(service, abstained, decision="accepted"),
        lambda: insert_decision(service, ready, decided_by=SUPPORT_A),
        lambda: insert_decision(service, ready, confirmed=False),
        lambda: insert_decision(service, ready, decision="rejected", text="should be empty"),
        lambda: insert_decision(service, ready, decision="revised", text=None),
    ]
    for case in cases:
        service.execute("SAVEPOINT probe")
        with pytest.raises(psycopg.errors.CheckViolation):
            case()
        service.execute("ROLLBACK TO SAVEPOINT probe")

    insert_decision(service, abstained, decision="revised", text="Teacher's own text", decided_by=PEER_A)
    insert_decision(service, ready, decision="rejected", text=None, decided_by=ADMIN_A)


def test_failed_draft_cannot_carry_output_and_ready_draft_needs_output(service):
    row, _ = reserve(service)
    service.execute("SAVEPOINT probe")
    with pytest.raises(psycopg.errors.CheckViolation):
        service.execute(
            "INSERT INTO public.ai_feedback_drafts (id, organization_id, request_id, status, output, error_code) "
            "VALUES (gen_random_uuid(), %s, %s, 'provider_error', '{}', 'x')", (ORG_A, row["id"]),
        )
    service.execute("ROLLBACK TO SAVEPOINT probe")
    with pytest.raises(psycopg.errors.CheckViolation):
        service.execute(
            "INSERT INTO public.ai_feedback_drafts (id, organization_id, request_id, status) "
            "VALUES (gen_random_uuid(), %s, %s, 'ready')", (ORG_A, row["id"]),
        )


def test_draft_cannot_point_at_another_organizations_request(service):
    row, _ = reserve(service)
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        insert_draft(service, row["id"], org=ORG_B)


# ---------------------------------------------------------------------------
# Reservation: idempotency, limits, budgets, concurrency.
# ---------------------------------------------------------------------------


def test_duplicate_key_returns_the_original_request(service):
    row, first = reserve(service)
    _, second = reserve(service, request_key=row["request_key"], id=str(uuid.uuid4()))

    assert first == {"outcome": "reserved", "request_id": row["id"]}
    assert second == {"outcome": "duplicate", "request_id": row["id"]}
    assert service.execute(
        "SELECT count(*) FROM public.ai_feedback_requests WHERE request_key = %s", (row["request_key"],)
    ).fetchone()[0] == 1


def test_user_hourly_and_org_daily_request_limits(service):
    limits = {**LIMITS, "user_hourly_requests": 2, "org_daily_requests": 3}
    outcomes = [reserve(service, limits=limits)[1]["outcome"] for _ in range(3)]
    peer = reserve(service, limits=limits, created_by=PEER_A)[1]["outcome"]
    over_org = reserve(service, limits=limits, created_by=ADMIN_A)[1]["outcome"]

    assert outcomes == ["reserved", "reserved", "user_rate_limited"]
    assert peer == "reserved"
    assert over_org == "org_rate_limited"


def test_budget_counts_reservations_until_actual_cost_is_recorded(service):
    limits = {**LIMITS, "user_daily_cost_microusd": 250}
    first, result = reserve(service, limits=limits, reserved_cost_microusd=200)
    assert result["outcome"] == "reserved"
    assert reserve(service, limits=limits, reserved_cost_microusd=100)[1]["outcome"] == "user_budget_exceeded"

    insert_draft(service, first["id"], actual_cost=40)  # the call cost far less than reserved
    assert reserve(service, limits=limits, reserved_cost_microusd=100)[1]["outcome"] == "reserved"


def test_org_budget_spans_users(service):
    limits = {**LIMITS, "org_daily_cost_microusd": 300}
    assert reserve(service, limits=limits, reserved_cost_microusd=200)[1]["outcome"] == "reserved"
    assert reserve(service, limits=limits, created_by=PEER_A, reserved_cost_microusd=200)[1]["outcome"] == "org_budget_exceeded"


@pytest.mark.parametrize("limits", [{}, {**LIMITS, "user_hourly_requests": 0}, {**LIMITS, "org_daily_cost_microusd": None}])
def test_missing_or_non_positive_limits_fail_closed(service, limits):
    with pytest.raises(psycopg.errors.InvalidParameterValue):
        reserve(service, limits=limits)


def test_concurrent_reservations_cannot_jointly_overspend(migrated_database, admin_conn):
    limits = {**LIMITS, "user_daily_cost_microusd": 150}
    first = psycopg.connect(migrated_database)
    second = psycopg.connect(migrated_database)
    reserved_ids = []
    try:
        as_service_role(first)
        as_service_role(second)
        row, result = reserve(first, limits=limits)  # holds the org lock until commit
        reserved_ids.append(row["id"])
        assert result["outcome"] == "reserved"

        outcome = {}

        def contender():
            contender_row, contender_result = reserve(second, limits=limits)
            reserved_ids.append(contender_row["id"])
            outcome.update(contender_result)
            second.commit()

        thread = threading.Thread(target=contender)
        thread.start()
        thread.join(timeout=1.0)
        assert thread.is_alive(), "the contender must wait for the organization lock"
        first.commit()
        thread.join(timeout=10)
        assert not thread.is_alive()
        assert outcome["outcome"] == "user_budget_exceeded"
    finally:
        first.close()
        second.close()
        admin_conn.execute(
            "DELETE FROM public.ai_feedback_requests WHERE id = ANY(%s::uuid[])", (reserved_ids,)
        )
