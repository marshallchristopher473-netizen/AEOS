"""Record command exits and elapsed time without changing their outcome."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

label, *command = sys.argv[1:]
directory = Path(os.environ.get('AEOS_EVIDENCE_DIR', '/tmp/aeos-command-evidence'))
directory.mkdir(parents=True, exist_ok=True)
started = datetime.now(timezone.utc).isoformat()
clock = time.monotonic()
result = subprocess.run(command, check=False)
record = {'label': label, 'command': command, 'cwd': os.getcwd(),
          'started_utc': started, 'seconds': round(time.monotonic() - clock, 3),
          'exit': result.returncode}
(directory / f'{label}.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record), file=sys.stderr, flush=True)
sys.exit(result.returncode)
