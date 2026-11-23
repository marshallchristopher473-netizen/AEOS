// Extracts the Code-node JS from both workflow JSON files and exercises the
// decision rules against the documented acceptance cases.
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const base = path.join(__dirname, '..', 'n8n');
const intake = JSON.parse(fs.readFileSync(path.join(base, '01-client-intake.workflow.json'), 'utf8'));
const sweep = JSON.parse(fs.readFileSync(path.join(base, '02-followup-sweep.workflow.json'), 'utf8'));
console.log('JSON parse: OK (both workflows)');

const rulesCode = intake.nodes.find((n) => n.id === 'apply-decision-rules').parameters.jsCode;
const sweepCode = sweep.nodes.find((n) => n.id === 'flag-overdue').parameters.jsCode;

function runNode(code, items, extra = {}) {
  const sandbox = {
    $input: { all: () => items.map((json) => ({ json })) },
    $execution: { id: '1001' },
    console,
    Date,
    Number,
    Math,
    ...extra,
  };
  return vm.runInNewContext(`(function(){${code}})()`, sandbox);
}

let failures = 0;
const check = (label, actual, expected) => {
  const ok = actual === expected;
  if (!ok) failures++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}  (got ${actual}, expected ${expected})`);
};

const form = (over) => ({
  'Full name': 'Dana Reyes',
  'Work email': 'dana@example.org',
  Phone: '555-0101',
  Organization: 'Riverbend School District',
  Role: 'District Administrator',
  'Students served': '2,000+',
  'What problem are you trying to solve?': 'Progress notes take all Friday.',
  Timeline: 'Immediately',
  'Budget authority': 'I control the budget',
  ...over,
});

console.log('\n-- D1 / D2 --');
const ac1 = runNode(rulesCode, [form()])[0].json;
check('AC-1 priority', ac1.priority, 'P1');
check('AC-1 SLA = +24h', Math.round((new Date(ac1.sla_due_at) - new Date(ac1.submitted_at)) / 3.6e6), 24);
check('AC-1 status', ac1.status, 'New');
check('AC-1 id shape', /^AEOS-1001-1$/.test(ac1.submission_id), true);
check('AC-1 maps problem_statement', ac1.problem_statement, 'Progress notes take all Friday.');

const ac2 = runNode(rulesCode, [form({ 'Budget authority': 'I do not control the budget' })])[0].json;
check('AC-2 priority', ac2.priority, 'P2');
check('AC-2 SLA = +72h', Math.round((new Date(ac2.sla_due_at) - new Date(ac2.submitted_at)) / 3.6e6), 72);

const ac3 = runNode(rulesCode, [form({ Timeline: 'Just exploring' })])[0].json;
check('AC-3 priority (both conditions required)', ac3.priority, 'P2');

const ac4 = runNode(rulesCode, [form({ Phone: undefined })])[0].json;
check('AC-4 empty phone', ac4.phone, '');

console.log('\n-- D3 --');
const yesterday = new Date(Date.now() - 36e5 * 30).toISOString();
const tomorrow = new Date(Date.now() + 36e5 * 30).toISOString();
const rows = [
  { submission_id: 'A', priority: 'P2', status: 'New', sla_due_at: yesterday, organization: 'Riverbend', full_name: 'Dana', work_email: 'd@e.org' },
  { submission_id: 'B', priority: 'P1', status: 'Qualified', sla_due_at: yesterday, organization: 'Riverbend', full_name: 'Dana', work_email: 'd@e.org' },
  { submission_id: 'C', priority: 'P1', status: 'New', sla_due_at: tomorrow, organization: 'Riverbend', full_name: 'Dana', work_email: 'd@e.org' },
  { submission_id: 'D', priority: 'P1', status: 'Contacted', sla_due_at: '', organization: 'Riverbend', full_name: 'Dana', work_email: 'd@e.org' },
];
const digest = runNode(sweepCode, rows);
check('AC-5 overdue count', digest[0].json.overdue_count, 1);
const ids = digest[0].json.digest.split('\n').map((l) => l.trim().split(' ').pop());
check('AC-5 lists the open overdue row', ids.includes('A'), true);
check('AC-5 excludes the closed row', ids.includes('B'), false);
check('AC-5 excludes the in-deadline row', ids.includes('C'), false);
check('AC-5 ignores unparseable sla_due_at', ids.includes('D'), false);
check('nothing overdue -> no items', runNode(sweepCode, [rows[2]]).length, 0);
check('empty sheet -> no items', runNode(sweepCode, []).length, 0);

console.log(failures === 0 ? '\nAll rule checks passed.' : `\n${failures} check(s) FAILED.`);
process.exit(failures === 0 ? 0 : 1);
