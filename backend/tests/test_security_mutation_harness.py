"""Infrastructure failures must never be counted as security mutation kills."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'aeos_security_mutations', Path(__file__).with_name('security_mutations.py')
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class TestMutationEvidence(unittest.TestCase):
    def run_contract(self, subset, full):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'source'
            (root / 'backend').mkdir(parents=True)
            (root / 'backend/control.py').write_text('guard = True\n')
            output = Path(temporary) / 'matrix.json'
            mutation = harness.Mutation(
                'probe', 'probe', 'probe', 'backend/control.py',
                'guard = True', 'guard = False', ('tests/',), False,
            )
            with patch.object(harness, 'REPO_ROOT', root), \
                    patch.object(harness, 'MUTATIONS', [mutation]), \
                    patch.object(harness, '_precheck', return_value=(True, 'valid')), \
                    patch.object(harness, '_run_suite', side_effect=[subset, full]), \
                    patch.dict(os.environ, {'AEOS_TEST_DATABASE_URL': 'synthetic'}), \
                    contextlib.redirect_stdout(io.StringIO()):
                code = harness.main(['--json', str(output)])
            return code, json.loads(output.read_text())

    def test_subset_assertion_plus_setup_error_is_invalid(self):
        code, report = self.run_contract(
            (1, '1 failed, 1 error', ['FAILED assertion'], ['ERROR setup']),
            (1, '1 failed', ['FAILED assertion'], []),
        )
        self.assertEqual(code, 1)
        self.assertEqual(report['totals']['invalid'], 1)
        self.assertEqual(report['totals']['killed'], 0)

    def test_full_suite_collection_failure_is_invalid(self):
        code, report = self.run_contract(
            (1, '1 failed', ['FAILED assertion'], []),
            (2, '1 error', [], ['ERROR collection']),
        )
        self.assertEqual(code, 1)
        self.assertEqual(report['totals']['invalid'], 1)
        self.assertEqual(report['mutations'][0]['full_suite_exit'], 2)

    def test_subset_failure_absent_from_full_suite_is_not_a_kill(self):
        code, report = self.run_contract(
            (1, '1 failed', ['FAILED assertion'], []), (0, '1 passed', [], []),
        )
        self.assertEqual(code, 1)
        self.assertEqual(report['totals']['survived'], 1)
        self.assertEqual(report['totals']['killed'], 0)

    def test_database_runs_require_rls(self):
        completed = type('Completed', (), {'stdout': '1 passed', 'returncode': 0})()
        with patch.object(harness.subprocess, 'run', return_value=completed) as run:
            harness._run_suite(Path('/tmp/synthetic'), ('tests/',), 'synthetic')
        self.assertEqual(run.call_args.kwargs['env']['AEOS_REQUIRE_RLS_TESTS'], '1')

    def test_missing_pytest_exit_is_invalid(self):
        code, report = self.run_contract((1, '', [], []), (1, '', [], []))
        self.assertEqual(code, 1)
        self.assertEqual(report['totals']['invalid'], 1)
        self.assertEqual(report['totals']['survived'], 0)
