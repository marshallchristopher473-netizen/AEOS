import Database from 'better-sqlite3';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

/**
 * Single SQLite file for the whole pilot (see brief: "No multi-tenant. Single
 * SQLite file."). The connection is cached on `globalThis` so Next.js dev-mode
 * hot reloads do not open a new file handle on every request.
 */

const DEFAULT_DB_PATH = './pilot.db';

function schemaPath(): string {
  // __dirname is not defined in ESM; derive it from import.meta.url.
  const here = dirname(fileURLToPath(import.meta.url));
  return resolve(here, 'schema.sql');
}

export function dbPath(): string {
  return process.env.PILOT_DB_PATH ?? DEFAULT_DB_PATH;
}

/** Apply schema.sql to a connection. Idempotent (every statement is IF NOT EXISTS). */
export function applySchema(db: Database.Database): void {
  db.exec(readFileSync(schemaPath(), 'utf8'));
}

/**
 * Open a database connection and ensure the schema is present.
 * Exported separately from `getDb()` so tests can open throwaway databases.
 */
export function openDb(path: string): Database.Database {
  const db = new Database(path);
  db.pragma('foreign_keys = ON');
  applySchema(db);
  return db;
}

type GlobalWithDb = typeof globalThis & { __pilotDb?: Database.Database };

export function getDb(): Database.Database {
  const g = globalThis as GlobalWithDb;
  if (!g.__pilotDb) {
    g.__pilotDb = openDb(dbPath());
  }
  return g.__pilotDb;
}

export function closeDb(): void {
  const g = globalThis as GlobalWithDb;
  g.__pilotDb?.close();
  g.__pilotDb = undefined;
}
