import pytest

from tests.fakes import ASSESSMENT_A, ASSESSMENT_RESULT_A, PLAN_A, STUDENT_A


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
        ("get", "/assessment-results", None),
        ("get", f"/assessment-results/{ASSESSMENT_RESULT_A}", None),
        (
            "post",
            "/assessment-results",
            {"assessment_id": ASSESSMENT_A, "score": 80, "max_score": 100},
        ),
        ("get", f"/ai-feedback/drafts?assessment_id={ASSESSMENT_A}", None),
        ("get", "/ai-feedback/drafts/00000000-0000-4000-8000-000000000001", None),
        (
            "post",
            "/ai-feedback/drafts",
            {
                "assessment_id": ASSESSMENT_A,
                "rubric_id": "RUB-CER3",
                "rubric_version": "0.1",
                "response_text": "Synthetic response.",
                "data_classification": "synthetic",
            },
        ),
        (
            "post",
            "/ai-feedback/drafts/00000000-0000-4000-8000-000000000001/decisions",
            {"decision": "rejected", "teacher_confirmed": True},
        ),
    ],
)
def test_every_business_route_requires_authentication(public_client, method, path, payload):
    response = public_client.request(method, path, json=payload)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
