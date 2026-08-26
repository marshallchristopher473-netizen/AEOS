from tests.fakes import ORG_A, ORG_B, SCHOOL_B, STUDENT_A, STUDENT_B, USER_A


def test_student_collection_is_tenant_scoped(api_client, fake_db):
    response = api_client.get("/students")

    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [STUDENT_A]
    assert fake_db.queries[-1]["filters"] == {"organization_id": ORG_A}


def test_same_tenant_student_object_is_returned(api_client, fake_db):
    response = api_client.get(f"/students/{STUDENT_A}")

    assert response.status_code == 200
    assert response.json()["id"] == STUDENT_A
    assert fake_db.queries[-1]["filters"] == {
        "id": STUDENT_A,
        "organization_id": ORG_A,
    }


def test_cross_tenant_student_object_is_indistinguishable_from_missing(api_client, fake_db):
    response = api_client.get(f"/students/{STUDENT_B}")

    assert response.status_code == 404
    assert fake_db.queries[-1]["filters"] == {
        "id": STUDENT_B,
        "organization_id": ORG_A,
    }


def test_student_create_derives_tenant_and_actor_server_side(api_client, fake_db):
    response = api_client.post(
        "/students",
        json={
            "first_name": "Cara",
            "last_name": "Gamma",
            "student_number": "A-003",
        },
    )

    assert response.status_code == 201
    assert response.json()["organization_id"] == ORG_A
    assert response.json()["created_by"] == USER_A
    inserted = fake_db.queries[-1]["payload"]
    assert inserted["organization_id"] == ORG_A
    assert inserted["created_by"] == USER_A


def test_student_create_rejects_spoofed_tenant_and_actor_fields(api_client):
    response = api_client.post(
        "/students",
        json={
            "organization_id": ORG_B,
            "created_by": "attacker-user",
            "first_name": "Cara",
            "last_name": "Gamma",
        },
    )

    assert response.status_code == 422


def test_student_create_rejects_cross_tenant_school_id(api_client, fake_db):
    response = api_client.post(
        "/students",
        json={
            "school_id": SCHOOL_B,
            "first_name": "Cara",
            "last_name": "Gamma",
        },
    )

    assert response.status_code == 404
    assert fake_db.queries[-1]["filters"] == {
        "id": SCHOOL_B,
        "organization_id": ORG_A,
    }
