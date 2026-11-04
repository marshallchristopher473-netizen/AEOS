import Database from 'better-sqlite3';
import { readFileSync } from 'node:fs';
import { newId } from '../src/lib/ids';
import { runScoring } from '../src/lib/scoring';
import type { Rubric } from '../src/lib/rubric';

const db = new Database('./pilot.db');
db.exec(readFileSync(new URL('./schema.sql', import.meta.url), 'utf8'));

const rubric: Rubric = {
  id: 'rubric_arg_g8',
  name: 'Grade 8 — Argumentative Essay',
  criteria: [
    { id: 'claim',    label: 'Clear claim',        weight: 1, scale: { min: 1, max: 4 }, description: 'States a defensible position.' },
    { id: 'evidence', label: 'Use of evidence',    weight: 2, scale: { min: 1, max: 4 }, description: 'Quotes or cites textual evidence accurately.' },
    { id: 'reasoning',label: 'Reasoning',          weight: 2, scale: { min: 1, max: 4 }, description: 'Explains how evidence supports the claim.' },
    { id: 'structure',label: 'Organization',       weight: 1, scale: { min: 1, max: 4 }, description: 'Logical paragraphs and transitions.' },
  ],
};

const responses = [
  { pseudonym: 'S-014', subgroup: 'gen-ed', text: 'The author argues that homework harms students. She cites studies showing sleep loss. This evidence shows the claim is strong because sleep affects learning. In conclusion, schools should limit homework.' },
  { pseudonym: 'S-019', subgroup: 'EL',      text: 'I think the author is right. The article says students need rest. This means more homework is not good. My own experience is that I am tired.' },
  { pseudonym: 'S-021', subgroup: 'IEP',     text: 'Homework should be limited. The author gives a quote about stress. That quote shows why the claim matters. So the argument makes sense.' },
];

(async () => {
  db.prepare('INSERT INTO rubrics (id, name, definition_json, created_at) VALUES (?,?,?,?)')
    .run(rubric.id, rubric.name, JSON.stringify(rubric), new Date().toISOString());

  for (const r of responses) {
    const id = newId('resp');
    db.prepare('INSERT INTO responses (id, pseudonym, subgroup, prompt, text, created_at) VALUES (?,?,?,?,?,?)')
      .run(id, r.pseudonym, r.subgroup, 'Should schools limit homework?', r.text, new Date().toISOString());

    const run = await runScoring(r.text, rubric);
    db.prepare('INSERT INTO scoring_runs (id, response_id, rubric_id, model_version, prompt_version, output_json, created_at) VALUES (?,?,?,?,?,?,?)')
      .run(run.id, id, rubric.id, run.modelVersion, run.promptVersion, JSON.stringify(run.drafts), new Date().toISOString());
  }
  console.log('seeded');
})();
