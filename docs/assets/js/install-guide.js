// Filter server-rendered installation instructions; the complete guide works without JS.
(function () {
  "use strict";
  const environments = ["windows", "macos", "linux", "unraid", "qnap", "synology", "truenas", "kubernetes", "generic-docker"];
  const desktops = environments.slice(0, 3);
  let dispose = function () {};

  function initialize() {
    dispose();
    const form = document.getElementById("install-questionnaire");
    if (!form) return;
    const instructions = document.getElementById("install-instructions");
    const fields = Object.fromEntries(["env", "method", "launch", "version"].map(key => [key, document.getElementById("install-" + key)]));
    const summary = document.getElementById("install-summary");
    let state = {};
    let legacyRoute = "";

    function readLocation() {
      const params = new URLSearchParams(location.search);
      state = Object.fromEntries(Object.keys(fields).map(key => [key, params.get(key) || ""]));
      let hash = location.hash.slice(1);
      try { hash = decodeURIComponent(hash); } catch (_) { /* Ignore malformed legacy fragments. */ }
      legacyRoute = "";
      if (!params.has("env")) {
        legacyRoute = ["local", "docker", "compose", ...environments.slice(3)].find(route => hash === "path-" + route || hash.startsWith(route + "-")) || "";
        if (environments.includes(legacyRoute)) state.env = legacyRoute;
        if (["local", "docker", "compose"].includes(legacyRoute)) {
          state.method = legacyRoute === "local" ? "local" : "docker";
          state.launch = legacyRoute === "compose" ? "compose" : "run";
        }
      }
      normalize();
      render();
      const target = document.getElementById(hash);
      if (target && !target.closest("[hidden]")) {
        let parent = target.parentElement;
        while (parent) {
          if (parent.tagName === "DETAILS") parent.open = true;
          parent = parent.parentElement;
        }
        requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
      }
    }

    function normalize() {
      if (!environments.includes(state.env)) state.env = "";
      if (!["local", "docker"].includes(state.method)) state.method = "";
      if (!["run", "compose"].includes(state.launch)) state.launch = "";
      if (!["current", "legacy"].includes(state.version)) state.version = "";
      if (state.env && !desktops.includes(state.env)) state.method = state.launch = "";
      if (state.env === "generic-docker") {
        state.method = "docker";
        state.launch = "run";
      }
      if (state.method !== "docker") state.launch = "";
      if (!["qnap", "synology"].includes(state.env)) state.version = "";
    }

    function render() {
      const desktop = desktops.includes(state.env) || ["local", "docker", "compose"].includes(legacyRoute);
      const versioned = ["qnap", "synology"].includes(state.env);
      Object.keys(fields).forEach(key => { fields[key].value = state[key]; });
      document.getElementById("install-method-field").hidden = !desktop;
      document.getElementById("install-launch-field").hidden = !desktop || state.method !== "docker";
      document.getElementById("install-version-field").hidden = !versioned;
      fields.version.options[1].textContent = state.env === "synology" ? "DSM 7.2 (Container Manager)" : "Container Station 3.0.5.623";
      fields.version.options[2].textContent = "Older version (legacy screenshots)";
      const complete = state.env && (desktop ? state.method && (state.method !== "docker" || state.launch) : !versioned || state.version);
      const sharedAnchor = ["configuration", "minimal-configyml", "first-run", "examples", "maintenance"].includes(location.hash.slice(1));
      instructions.hidden = !complete && !legacyRoute && !sharedAnchor;
      instructions.querySelectorAll("[data-env], [data-method], [data-launch], [data-os], [data-version], [data-release]").forEach(block => {
        const matches = (key, value) => !block.dataset[key] || !value || block.dataset[key].split(" ").includes(value);
        const method = desktop || state.env === "generic-docker" ? state.method : "nas";
        block.hidden = !matches("env", state.env || "desktop") || !matches("method", method) || !matches("launch", state.launch)
          || !matches("os", state.env) || !matches("version", state.version)
          || !matches("release", /\/develop\//.test(location.pathname) ? "develop" : "latest");
      });
      const choices = Object.values(fields).filter(field => field.value).map(field => field.selectedOptions[0].textContent);
      summary.textContent = complete ? "Your walkthrough: " + choices.join(" · ") + ". Change any answer above to update it."
        : legacyRoute ? "Showing the linked installation path. Choose your environment above to tailor these instructions."
        : "Choose your environment and the options below it to show your walkthrough.";
      // Contents is generated from all static headings; remove entries for hidden variants.
      document.querySelectorAll(".md-nav--secondary a[href*='#']").forEach(link => {
        let id;
        try { id = decodeURIComponent(new URL(link.href).hash.slice(1)); } catch (_) { return; }
        const target = document.getElementById(id);
        const item = link.closest("li");
        if (target && item) item.hidden = !!target.closest("[hidden]");
      });
    }

    function changed(event) {
      if (!event.target.name) return;
      const key = event.target.name;
      state[key] = event.target.value;
      if (key === "env") {
        const previousMethod = legacyRoute ? state.method : "";
        const previousLaunch = legacyRoute ? state.launch : "";
        state.method = previousMethod;
        state.launch = previousLaunch;
        state.version = "";
      }
      if (key === "method") state.launch = "";
      legacyRoute = "";
      normalize();
      const url = new URL(location.href);
      Object.keys(fields).forEach(name => {
        if (state[name]) url.searchParams.set(name, state[name]);
        else url.searchParams.delete(name);
      });
      url.hash = "";
      history.pushState(null, "", url);
      render();
    }
    function reset() {
      fields.env.value = "";
      changed({ target: fields.env });
      fields.env.focus();
    }
    const preventSubmit = event => event.preventDefault();
    form.hidden = false;
    document.getElementById("install-fallback").hidden = true;
    form.addEventListener("change", changed);
    form.addEventListener("submit", preventSubmit);
    document.getElementById("install-reset").addEventListener("click", reset);
    window.addEventListener("popstate", readLocation);
    window.addEventListener("hashchange", readLocation);
    dispose = function () {
      form.removeEventListener("change", changed);
      form.removeEventListener("submit", preventSubmit);
      document.getElementById("install-reset")?.removeEventListener("click", reset);
      window.removeEventListener("popstate", readLocation);
      window.removeEventListener("hashchange", readLocation);
    };
    readLocation();
  }
  if (typeof document$ !== "undefined") document$.subscribe(initialize);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
  else initialize();
})();
