// Exercise sticky-header geometry and lifecycle without a browser dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../docs/assets/js/extra.js'), 'utf8');
const code = source.slice(source.indexOf('// Keep headers visible'), source.indexOf('// Table Sort'));
const rect = { top: 100, bottom: 900, left: 200, right: 1000, width: 800 };
const headRect = { top: 100, height: 40, width: 800 };
const clip = { left: 200, right: 1000 };
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.style = {}; this.events = {}; this.attributes = {}; }
  appendChild(node) {
    this.children.push(node); node.parentElement = this;
    if (node.tag === 'thead') this.tHead = node;
  }
  replaceChildren(...nodes) { this.children = nodes; }
  setAttribute(key, value) { this.attributes[key] = value; }
  querySelectorAll() { return []; }
  addEventListener(name, callback) { this.events[name] = callback; }
  removeEventListener(name) { delete this.events[name]; }
  remove() {
    this.removed = true;
    if (this.parentElement?.tHead === this) this.parentElement.tHead = null;
  }
}
function head() {
  const node = new Element('thead');
  node.rows = [{ cells: [200, 300, 300].map(width => ({ style: {}, getBoundingClientRect: () => ({ width }), click() { this.clicked = true; } })) }];
  node.getBoundingClientRect = () => headRect;
  node.cloneNode = head;
  return node;
}
const table = new Element('table');
table.tHead = head(); table.tBodies = [{}]; table.scrollLeft = 0;
table.parentElement = { closest: () => null, getBoundingClientRect: () => clip };
let closedDisclosure = false, rendered = true;
table.closest = selector => selector === 'details:not([open])'
  ? (closedDisclosure ? {} : null) : table.parentElement;
table.getClientRects = () => rendered ? [rect] : [];
table.getBoundingClientRect = () => rect;
const nested = { parentElement: { closest: () => table } };
const body = new Element('body');
const document = new Element('document');
document.body = body;
document.createElement = tag => new Element(tag);
document.querySelector = () => ({ getBoundingClientRect: () => ({ bottom: 60 }) });
document.querySelectorAll = () => [table, nested];
const window = new Element('window');
window.innerWidth = 1200;
window.getComputedStyle = () => ({ padding: '10px', fontSize: '14px' });
let pending, subscription, disconnected = 0;
window.requestAnimationFrame = callback => { pending = callback; return 1; };
window.cancelAnimationFrame = () => { pending = null; };
const flush = () => { const callback = pending; pending = null; callback(); };
vm.runInNewContext(code, { document, window, document$: { subscribe(callback) { subscription = callback; } },
  ResizeObserver: class { observe() {} disconnect() { disconnected++; } } });
subscription(); flush();
assert.equal(body.children.length, 1, 'Nested tables must not receive sticky copies');
const overlay = body.children[0];
assert.equal(overlay.hidden, true, 'Header is initially in its normal position');
headRect.top = 10; rect.top = 10;
document.events.scroll(); flush();
assert.equal(overlay.hidden, false);
assert.equal(overlay.style.top, '60px', 'Header sits beneath the site header');
assert.equal(overlay.style.width, '800px');
closedDisclosure = true;
document.events.toggle(); flush();
assert.equal(overlay.hidden, true, 'Closed admonitions must hide headers even with retained geometry');
closedDisclosure = false;
document.events.toggle(); flush();
assert.equal(overlay.hidden, false, 'Opening an admonition restores eligible headers');
rendered = false;
document.events.scroll(); flush();
assert.equal(overlay.hidden, true, 'Tables without rendered boxes must not show headers');
rendered = true;
document.events.scroll(); flush();
const copy = overlay.children[0];
assert.equal(copy.children[0].children[1].style.width, '300px');
rect.left = 100; rect.right = 900;
document.events.scroll(); flush();
assert.equal(copy.style.transform, 'translateX(-100px)', 'Track wrapper horizontal scrolling');
table.scrollLeft = 50;
document.events.scroll(); flush();
assert.equal(copy.style.transform, 'translateX(-150px)', 'Track table horizontal scrolling');
overlay.events.click({ target: { closest: () => ({ cellIndex: 1, parentElement: { sectionRowIndex: 0 } }) } });
assert.equal(table.tHead.rows[0].cells[1].clicked, true, 'Forward sorting to the original header');
rect.bottom = 80;
document.events.scroll(); flush();
assert.equal(overlay.style.height, '20px', 'Clip the header at the table end');
rect.bottom = 50;
document.events.scroll(); flush();
assert.equal(overlay.hidden, true);
subscription(); flush();
assert.equal(overlay.removed, true, 'Remove old header copies on navigation');
assert.equal(disconnected, 1, 'Disconnect old resize observers');
console.log('Sticky table headers: geometry, horizontal scrolling, sorting, nesting, and navigation passed.');
