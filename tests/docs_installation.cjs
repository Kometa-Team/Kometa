// Run the real questionnaire against the rendered document tree without a browser dependency.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const fixture = fs.readFileSync(process.argv[2], "utf8");
const script = fs.readFileSync(path.join(__dirname, "../docs/assets/js/install-guide.js"), "utf8");

function setup(query = "") {
  const nodes = [];
  function element(raw, parent) {
    const attrs = raw.attrs;
    const node = {
      parent, attrs, tagName: raw.tag, textContent: raw.text, value: "", name: attrs.name,
      href: attrs.href ? new URL(attrs.href, "http://localhost/kometa/install/").href : "",
      hidden: "hidden" in attrs, events: {}, dataset: {},
      addEventListener(key, callback) { this.events[key] = callback; },
      removeEventListener(key) { delete this.events[key]; },
      focus() {},
      scrollIntoView() {},
      closest(selector) {
        if (selector === "[hidden]") return this.hidden ? this : this.parent?.closest(selector);
        if (selector === "li") return this.tagName === "li" ? this : this.parent?.closest(selector);
        return null;
      },
      querySelectorAll() { return nodes.filter(candidate => Object.keys(candidate.dataset).length && candidate.ancestors.includes(this)); }
    };
    node.ancestors = parent ? [parent, ...parent.ancestors] : [];
    for (const [key, value] of Object.entries(attrs)) if (key.startsWith("data-")) node.dataset[key.slice(5)] = value;
    nodes.push(node);
    node.children = raw.children.map(child => element(child, node));
    if (raw.tag === "select") {
      node.options = node.children.filter(child => child.tagName === "option");
      Object.defineProperty(node, "selectedOptions", { get() { return node.options.filter(option => option.attrs.value === node.value); } });
    }
    return node;
  }
  element(JSON.parse(fixture), null);
  const ids = Object.fromEntries(nodes.filter(node => node.attrs.id).map(node => [node.attrs.id, node]));
  const listeners = {};
  const location = new URL("http://localhost/kometa/install/" + query);
  const history = [];
  const context = {
    URL, URLSearchParams, location, requestAnimationFrame: callback => callback(),
    history: { pushState(_, __, url) { history.push(location.href); location.href = url.href; } },
    window: { addEventListener(key, callback) { listeners[key] = callback; }, removeEventListener(key) { delete listeners[key]; } },
    document: { readyState: "complete", getElementById: id => ids[id], querySelectorAll: () => nodes.filter(node => node.tagName === "a" && node.attrs.href?.startsWith("#") && node.ancestors.some(parent => parent.attrs.class === "md-nav--secondary")) },
  };
  vm.runInNewContext(script, context);
  function change(key, value) {
    const field = ids["install-" + key]; field.value = value;
    ids["install-questionnaire"].events.change({ target: field });
  }
  const visiblePaths = () => nodes.filter(node => node.attrs.class === "install-path" && !node.closest("[hidden]")).map(node => node.children.find(child => child.attrs.id?.startsWith("path-"))?.attrs.id);
  return { ids, nodes, location, history, listeners, change, visiblePaths };
}

assert.equal(setup().ids["install-instructions"].hidden, true);
const generic = setup();
generic.change("env", "generic-docker");
assert.deepEqual(generic.visiblePaths(), ["path-generic-docker"]);
assert.equal(generic.ids["install-method-field"].hidden, true);
assert.equal(generic.ids["install-launch-field"].hidden, true);
assert.equal(generic.ids["configuration"].closest("[hidden]"), undefined);
assert.equal(generic.ids["install-summary"].textContent.includes("Unsure / Generic Docker"), true);
assert.deepEqual(setup(generic.location.search).visiblePaths(), ["path-generic-docker"]);
assert.deepEqual(setup("#path-generic-docker").visiblePaths(), ["path-generic-docker"]);
for (const node of generic.nodes.filter(node => node.dataset.os)) assert.ok(node.closest("[hidden]"));
generic.change("env", "linux");
assert.equal(generic.ids["install-instructions"].hidden, true);
generic.change("method", "docker");
assert.equal(generic.ids["install-launch-field"].hidden, false);
assert.ok(generic.nodes.some(node => node.attrs.class === "admonition tip" && node.ancestors.includes(generic.ids["install-launch-field"])));
generic.location.href = generic.history[1]; generic.listeners.popstate();
assert.deepEqual(generic.visiblePaths(), ["path-generic-docker"]);
generic.ids["install-reset"].events.click();
assert.equal(generic.ids["install-instructions"].hidden, true);
for (const env of ["windows", "macos", "linux"]) {
  for (const [method, launch, expected] of [["local", "", "local"], ["docker", "run", "docker"], ["docker", "compose", "compose"]]) {
    const app = setup(`?env=${env}&method=${method}&launch=${launch}`);
    assert.deepEqual(app.visiblePaths(), ["path-" + expected]);
    assert.equal(app.ids["configuration"].closest("[hidden]"), undefined);
    const contents = app.nodes.filter(node => node.tagName === "a" && node.ancestors.some(parent => parent.attrs.class === "md-nav--secondary"));
    for (const link of contents.filter(node => node.attrs.href.startsWith("#path-"))) {
      assert.equal(!!link.closest("[hidden]"), link.attrs.href !== "#path-" + expected);
    }
    assert.equal(contents.find(node => node.attrs.href === "#configuration").closest("[hidden]"), undefined);
    for (const node of app.nodes.filter(node => node.dataset.os)) {
      if (!node.closest("[hidden]")) assert.equal(node.dataset.os, env);
    }
    app.change("env", "synology");
    assert.equal(app.ids["install-instructions"].hidden, true);
    assert.equal(app.location.searchParams.has("method"), false);
    app.change("version", "current");
    assert.deepEqual(app.visiblePaths(), ["path-synology"]);
    app.location.href = app.history[0]; app.listeners.popstate();
    assert.deepEqual(app.visiblePaths(), ["path-" + expected]);
  }
}
for (const env of ["unraid", "qnap", "synology", "truenas", "kubernetes"]) {
  for (const version of ["current", "legacy"]) {
    const app = setup(`?env=${env}&version=${version}`);
    assert.deepEqual(app.visiblePaths(), ["path-" + env]);
    for (const node of app.nodes.filter(node => node.dataset.version)) {
      if (!node.closest("[hidden]")) assert.equal(node.dataset.version, version);
    }
  }
}
for (const route of ["local", "docker", "compose", "unraid", "qnap", "synology", "truenas", "kubernetes"]) {
  const app = setup("#path-" + route);
  assert.deepEqual(app.visiblePaths(), ["path-" + route]);
}
const old = setup("#local-setting-up-the-initial-config-file");
assert.deepEqual(old.visiblePaths(), ["path-local"]);
old.change("env", "windows");
assert.deepEqual(old.visiblePaths(), ["path-local"]);
const invalid = setup("?env=unknown&method=bogus&version=bogus");
assert.equal(invalid.ids["install-instructions"].hidden, true);
const reset = setup("?env=linux&method=local&unrelated=keep");
reset.ids["install-reset"].events.click();
assert.equal(reset.location.search, "?unrelated=keep");
assert.equal(reset.ids["install-instructions"].hidden, true);
console.log("Installation routes, variants, legacy links, history and reset passed");
