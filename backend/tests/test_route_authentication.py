import pytest

from tests.fakes import ASSESSMENT_A, PLAN_A, STUDENT_A


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("get", "/students", None),
        ("get", f"/students/{STUDENT_A}", None),
        ("post", "/students", {"first_name": "A", "last_name": "Student"}),
        ("get", "/assessments", None),
        ("get", f"/assessments/{ASSESSMENT_A}", None),
        (
            "post",
            "/assessments",
            {
                "student_id": STUDENT_A,
                "title": "Screen",
                "assessment_type": "curriculum_based",
            },
        ),
        ("get", "/intervention-plans", None),
        ("get", f"/intervention-plans/{PLAN_A}", None),
        (
            "post",
            "/intervention-plans",
            {"student_id": STUDENT_A, "title": "Plan"},
        ),
    ],
)
def test_every_business_route_requires_authentication(public_client, method, path, payload):
    response = public_client.request(method, path, json=payload)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
