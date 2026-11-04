PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS rubrics (
  id              TEXT PRIMARY KEY,
  name            TEXT NOT NULL,
  definition_json TEXT NOT NULL,
  created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS responses (
  id         TEXT PRIMARY KEY,
  pseudonym  TEXT NOT NULL,
  subgroup   TEXT,                 -- de-identified cohort: EL | IEP | gen-ed
  prompt     TEXT NOT NULL,
  text       TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scoring_runs (
  id             TEXT PRIMARY KEY,
  response_id    TEXT NOT NULL REFERENCES responses(id),
  rubric_id      TEXT NOT NULL REFERENCES rubrics(id),
  model_version  TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  output_json    TEXT NOT NULL,    -- ScoreDraft[]
  created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decisions (
  id             TEXT PRIMARY KEY,
  response_id    TEXT NOT NULL REFERENCES responses(id),
  scoring_run_id TEXT NOT NULL REFERENCES scoring_runs(id),
  criterion_id   TEXT NOT NULL,
  ai_score       INTEGER NOT NULL,
  final_score    INTEGER NOT NULL,
  action         TEXT NOT NULL CHECK (action IN ('accept','revise','reject','flag')),
  reviewer       TEXT NOT NULL,
  started_at     TEXT NOT NULL,
  decided_at     TEXT NOT NULL,
  note           TEXT,
  UNIQUE(response_id, criterion_id, reviewer)
);

CREATE TABLE IF NOT EXISTS calibration_sessions (
  id            TEXT PRIMARY KEY,
  reviewer      TEXT NOT NULL,
  response_id   TEXT NOT NULL REFERENCES responses(id),
  manual_score  INTEGER NOT NULL,
  ai_score      INTEGER,
  revealed_at   TEXT,
  created_at    TEXT NOT NULL
);

-- Append-only, hash-chained audit log.
CREATE TABLE IF NOT EXISTS audit_log (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  ts        TEXT NOT NULL,
  actor     TEXT NOT NULL,
  action    TEXT NOT NULL,
  payload   TEXT NOT NULL,
  prev_hash TEXT NOT NULL,
  hash      TEXT NOT NULL UNIQUE
);

CREATE TRIGGER IF NOT EXISTS audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;

CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
BEFORE DELETE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;

CREATE INDEX IF NOT EXISTS idx_audit_action_ts ON audit_log(action, ts);
CREATE INDEX IF NOT EXISTS idx_decisions_response ON decisions(response_id);
