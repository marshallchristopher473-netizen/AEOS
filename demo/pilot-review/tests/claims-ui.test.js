'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const Core = require('../pilot-core.js');
const Fx = require('../fixtures.js');

// Execute the unchanged UI entry point against a minimal test DOM.
// This is a renderer contract test, not a browser/layout/accessibility test.
class TestNode {
  constructor(tag, text = '') {
    this.tag = tag;
    this.text = text;
    this.children = [];
    this.attributes = {};
    this.events = {};
    this.style = {};
  }
  appendChild(node) { this.children.push(node); return node; }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(key, value) { this.attributes[key] = value; }
  addEventListener(type, handler) { this.events[type] = handler; }
  get textContent() { return this.text + this.children.map((c) => c.textContent).join(''); }
  set textContent(value) { this.text = value; this.children = []; }
}

function renderDemo() {
  const root = new TestNode('main');
  const document = {
    body: new TestNode('body'),
    visibilityState: 'visible',
    getElementById: (id) => id === 'app' ? root : null,
    createElement: (tag) => new TestNode(tag),
    createTextNode: (text) => new TestNode('#text', text),
    addEventListener() {},
  };
  const window = {
    AEOSPilotCore: Core,
    AEOSPilotFixtures: Fx,
    scrollY: 0,
    scrollTo() {},
    addEventListener() {},
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../app.js'), 'utf8'), {
    window, document, Node: TestNode, setInterval() {},
  }, { timeout: 1000 });
  return root;
}

function descendants(node) {
  return [node, ...node.children.flatMap(descendants)];
}

test('dashboard UI: runs with v2 timing and offers no manual-baseline comparison', () => {
  const root = renderDemo();
  const dashboardButton = descendants(root).find((n) => n.tag === 'button' && n.textContent === 'Dashboard');
  assert.ok(dashboardButton);
  dashboardButton.events.click();
  assert.match(root.textContent, /Median active demo interaction/);
  assert.match(root.textContent, /over prewritten mock suggestions/);
  assert.match(root.textContent, /No model runs/);
  assert.match(root.textContent, /does not measure grading duration, full task time or comparative time savings/);
  assert.doesNotMatch(root.textContent, /Observed pilot result|Manual baseline|manual median|difference of|vs assisted/i);
  assert.equal(descendants(root).some((n) => n.tag === 'input'), false);
  for (const label of ['Download JSON', 'Download CSV']) {
    assert.ok(descendants(root).some((n) => n.tag === 'button' && n.textContent === label));
  }
});

