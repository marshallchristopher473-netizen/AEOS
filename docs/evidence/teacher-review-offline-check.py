"""Limited offline checks of production schemas, services, and actor dependencies.
No JWT, Supabase SDK, HTTP dispatch, live DB, or browser verification is claimed.
"""
import asyncio
import sys
import types
import unittest
from pathlib import Path
from uuid import UUID
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))
from fastapi import HTTPException
from pydantic import ValidationError
from tests.fakes import ASSESSMENT_A, ASSESSMENT_B, ASSESSMENT_RESULT_A, ORG_A, STUDENT_A, USER_A, FakeClient, seeded_tables

# Import-only placeholders for unavailable SDKs. They are never called.
async def unavailable_identity():
    raise RuntimeError('JWT verification is outside this offline check')
def unavailable_storage():
    raise RuntimeError('Supabase SDK is outside this offline check')
auth = types.ModuleType('app.core.auth')
auth.get_current_user = unavailable_identity
sys.modules['app.core.auth'] = auth
storage = types.ModuleType('app.services.supabase_service')
storage.get_supabase_admin_client = unavailable_storage
sys.modules['app.services.supabase_service'] = storage

from app.core.dependencies import get_db_user, get_current_actor, require_privileged_write
from app.models.schemas import AssessmentCreateRequest, AssessmentResultCreateRequest
from app.api.assessments import create_assessment, get_assessment
from app.api.assessment_results import create_assessment_result, list_assessment_results

class TeacherReviewChecks(unittest.TestCase):
    def setUp(self):
        self.db = FakeClient(seeded_tables())
        self.actor = self.resolve_actor('auth-user-a')

    def resolve_actor(self, subject):
        membership = asyncio.run(get_db_user(user_payload={'sub': subject}, client=self.db))
        return asyncio.run(get_current_actor(db_user=membership))

    def save(self, fields, actor=None):
        payload = AssessmentResultCreateRequest.model_validate(fields)
        trusted_actor = asyncio.run(require_privileged_write(actor or self.actor))
        return create_assessment_result(payload, trusted_actor, self.db)

    def test_create_review_and_reload_both_states(self):
        for state in ('draft', 'complete'):
            with self.subTest(state=state):
                trusted_actor = asyncio.run(require_privileged_write(self.actor))
                assessment = create_assessment(AssessmentCreateRequest(student_id=STUDENT_A, title='Synthetic intake', assessment_type='reading'), trusted_actor, self.db)
                self.assertEqual(UUID(assessment.id).version, 4)
                self.assertEqual(self.db.queries[-1]['payload']['id'], assessment.id)
                result = self.save({'assessment_id': assessment.id, 'score': 0, 'max_score': 10, 'summary': 'Synthetic findings', 'status': state})
                self.assertEqual(UUID(result.id).version, 4)
                self.assertEqual(self.db.queries[-1]['payload']['id'], result.id)
                self.assertEqual((result.organization_id, result.student_id, result.created_by), (ORG_A, STUDENT_A, USER_A))
                self.assertEqual(result.score, 0)
                self.assertEqual(result.status, state)
                loaded = list_assessment_results(assessment_id=assessment.id, actor=self.actor, client=self.db)
                self.assertEqual(loaded, [result])
                self.assertEqual(get_assessment(assessment.id, self.actor, self.db).status, 'draft')

    def test_cross_tenant_and_missing_assessment_denied(self):
        for assessment_id in (ASSESSMENT_B, 'missing-assessment'):
            with self.assertRaises(HTTPException) as failure:
                list_assessment_results(assessment_id=assessment_id, actor=self.actor, client=self.db)
            self.assertEqual(failure.exception.status_code, 404)
            with self.assertRaises(HTTPException) as failure:
                self.save({'assessment_id': assessment_id})
            self.assertEqual(failure.exception.status_code, 404)
        self.assertFalse(any(q['operation'] == 'insert' for q in self.db.queries))

    def test_filter_hides_other_assessments_in_same_tenant(self):
        self.db.tables['assessment_results'].append({**self.db.tables['assessment_results'][0], 'id': 'unrelated-result', 'assessment_id': 'other-assessment'})
        results = list_assessment_results(assessment_id=ASSESSMENT_A, actor=self.actor, client=self.db)
        self.assertEqual([r.id for r in results], [ASSESSMENT_RESULT_A])
        self.assertEqual(self.db.queries[-1]['filters'], {'organization_id': ORG_A})

    def test_support_cannot_save_but_can_read(self):
        actor = self.resolve_actor('auth-support-a')
        self.assertEqual(len(list_assessment_results(assessment_id=ASSESSMENT_A, actor=actor, client=self.db)), 1)
        with self.assertRaises(HTTPException) as failure:
            self.save({'assessment_id': ASSESSMENT_A}, actor)
        self.assertEqual(failure.exception.status_code, 403)
        self.assertFalse(any(q['operation'] == 'insert' for q in self.db.queries))

    def test_inactive_organization_cannot_review(self):
        self.db.tables['organizations'][0]['status'] = 'suspended'
        with self.assertRaises(HTTPException) as failure:
            self.resolve_actor('auth-user-a')
        self.assertEqual(failure.exception.status_code, 403)

    def test_invalid_scores_and_status_are_not_inserted(self):
        for fields in ({'score': -1}, {'max_score': 0}, {'max_score': 0.001}, {'score': 11, 'max_score': 10}, {'score': 10000}, {'max_score': 10000}, {'status': 'unsupported'}, {'score': float('inf')}, {'score': float('nan')}):
            with self.subTest(fields=fields):
                with self.assertRaises(ValidationError):
                    self.save({'assessment_id': ASSESSMENT_A, **fields})
        self.assertFalse(any(q['operation'] == 'insert' for q in self.db.queries))

    def test_client_authority_fields_are_rejected(self):
        for field in ('id', 'organization_id', 'created_by', 'student_id'):
            with self.assertRaises(ValidationError):
                self.save({'assessment_id': ASSESSMENT_A, field: 'spoofed'})

    def test_empty_assessment_review_collection(self):
        self.db.tables['assessment_results'] = []
        self.assertEqual(list_assessment_results(assessment_id=ASSESSMENT_A, actor=self.actor, client=self.db), [])

if __name__ == '__main__':
    unittest.main(verbosity=2)
