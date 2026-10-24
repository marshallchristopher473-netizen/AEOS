"""Check substitution validity only; this does not execute or kill mutants."""
import ast
import importlib.util
from pathlib import Path
import shutil
import tempfile

root = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'aeos_mutation_anchors', root / 'backend/tests/security_mutations.py'
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
with tempfile.TemporaryDirectory() as temporary:
    for i, mutation in enumerate(harness.MUTATIONS):
        copy = Path(temporary) / str(i)
        target = copy / mutation.path
        target.parent.mkdir(parents=True)
        shutil.copyfile(root / mutation.path, target)
        mutation.apply(copy)
        if target.suffix == '.py':
            ast.parse(target.read_text())
print(f'{len(harness.MUTATIONS)} unique anchors substitute; Python targets parse. No mutation kill claim.')
