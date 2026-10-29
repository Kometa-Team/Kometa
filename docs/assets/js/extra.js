// Shared page enhancements

document$.subscribe(function() {

  // Update scroller marquees
  const scrollers = document.querySelectorAll('.scroller');
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    // Scrolling disabled, delete all but the first image (first two for theme-specific imaging)
    scrollers.forEach(scroller => {
      const images = Array.from(scroller.querySelectorAll('.scroller__inner > *'));
      for (let i = 2; i < images.length; i++) {
        images[i].remove();
      }
    });
  } else {
    scrollers.forEach(scroller => {
      // If clones are present, skip (this function can be triggered >1 times as SPA)
      if (scroller.querySelector('[aria-hidden=true]')) { return; }

      // Enable animation attribute
      scroller.setAttribute('data-animated', true);

      const scrollerInner = scroller.querySelector('.scroller__inner');

      // Randomize order of images if it is randomized
      if (scroller.classList.contains('randomized')) {
        for (let i = scrollerInner.children.length; i >= 0; i--) {
          scrollerInner.appendChild(scrollerInner.children[Math.random() * i | 0]);
        }
      }

      const scrollerContent = Array.from(scrollerInner.children); // Do not use live children

      scrollerContent.forEach(item => {
        const newItem = item.cloneNode(true);
        newItem.setAttribute('aria-hidden', true);
        scrollerInner.appendChild(newItem);
      });
    });
  }
});

// Open operation details when navigating directly to an operation hash.
document$.subscribe(function() {
  if (window.operationAdmonitionHashHandler) {
    window.removeEventListener("hashchange", window.operationAdmonitionHashHandler);
    window.operationAdmonitionHashHandler = null;
  }

  const operationsPath = /\/config\/operations\/?$/;
  if (!operationsPath.test(window.location.pathname)) {
    return;
  }

  const operationHeadings = document.querySelectorAll("article h6[id]");

  operationHeadings.forEach(function(heading) {
    const details = heading.nextElementSibling;
    if (!details || details.tagName.toLowerCase() !== "details") {
      return;
    }

    details.dataset.operationAnchor = heading.id;

    const summary = details.querySelector(":scope > summary");
    if (!summary || summary.querySelector(".operation-admonition-link")) {
      return;
    }

    const link = document.createElement("a");
    link.className = "operation-admonition-link";
    link.href = "#" + heading.id;
    link.setAttribute("aria-label", "Link to this operation");
    link.textContent = "#";
    link.addEventListener("click", function(event) {
      event.stopPropagation();
      details.open = true;
    });
    summary.appendChild(link);
  });

  function openOperationFromHash() {
    const hash = decodeURIComponent(window.location.hash.slice(1));
    if (!hash) {
      return;
    }

    const heading = document.getElementById(hash);
    if (!heading) {
      return;
    }

    const details = heading.nextElementSibling;
    if (!details || details.tagName.toLowerCase() !== "details") {
      return;
    }

    details.open = true;
    window.requestAnimationFrame(function() {
      details.scrollIntoView({ block: "start" });
    });
  }

  openOperationFromHash();
  window.operationAdmonitionHashHandler = openOperationFromHash;
  window.addEventListener("hashchange", window.operationAdmonitionHashHandler);
});

// Add copy controls to individual navigation pages, excluding folders.
document$.subscribe(function() {
  document.querySelectorAll('.kometa-navigation .md-nav__item:not(.md-nav__item--nested) > a.md-nav__link[href], .kometa-navigation [data-kometa-home-link]').forEach(function(link) {
    const item = link.parentElement;
    if (item.querySelector(':scope > .kometa-nav-copy')) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'kometa-nav-copy';
    button.dataset.copyPermalink = 'true';
    button.dataset.copyUrl = link.href;
    button.dataset.copyLabel = 'Copy link to ' + link.textContent.trim();
    button.title = button.dataset.copyLabel;
    button.textContent = '\u00b6';
    item.classList.add('kometa-nav-page');
    item.appendChild(button);
  });
});

// Copy heading, page, and runtime-option links; open options reached through a direct link.
document$.subscribe(function() {
  document.querySelectorAll("[data-copy-permalink], article :is(h1, h2, h3, h4, h5, h6) a.headerlink").forEach(function(link) {
    if (link.dataset.copyBound) return;
    link.dataset.copyBound = "true";
    const label = link.dataset.copyLabel || "Copy direct link";
    link.setAttribute("aria-label", label);
    link.title = label;
    link.addEventListener("click", async function(event) {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      event.stopPropagation();
      let copied = false;
      try {
        await navigator.clipboard.writeText(link.dataset.copyUrl || link.href);
        copied = true;
      } catch (error) {
        const input = document.createElement("textarea");
        input.value = link.dataset.copyUrl || link.href;
        input.style.position = "fixed";
        input.style.opacity = "0";
        document.body.appendChild(input);
        input.select();
        try {
          copied = document.execCommand("copy");
        } catch (fallbackError) {
          copied = false;
        } finally {
          input.remove();
          link.focus({ preventScroll: true });
        }
      }
      const message = copied ? "Copied to clipboard" : "Could not copy link";
      if (window.alert$ && typeof window.alert$.next === "function") {
        window.alert$.next(message);
      } else {
        link.title = message;
      }
    });
  });

  if (window.runtimeOptionHashHandler) {
    window.removeEventListener("hashchange", window.runtimeOptionHashHandler);
  }
  function openRuntimeOption() {
    let id;
    try {
      id = decodeURIComponent(window.location.hash.slice(1));
    } catch (error) {
      return;
    }
    const target = document.getElementById(id);
    const details = target && target.closest("details");
    if (!details || !details.querySelector("[data-copy-permalink]")) return;
    details.open = true;
    window.requestAnimationFrame(function() {
      details.scrollIntoView({ block: "start" });
    });
  }
  window.runtimeOptionHashHandler = openRuntimeOption;
  window.addEventListener("hashchange", openRuntimeOption);
  openRuntimeOption();
});

document$.subscribe(function() {
  const ellipsisText = "Kometa Wiki";

  document.querySelectorAll('.md-header__topic:first-child .md-ellipsis, [data-kometa-site-title]').forEach(function(title) {
    title.textContent = ellipsisText;
  });

  document.querySelectorAll('[data-kometa-search]').forEach(function(button) {
    if (button.dataset.bound) return;
    button.dataset.bound = 'true';
    button.addEventListener('click', function() {
      const drawer = document.getElementById('__drawer');
      if (drawer && drawer.checked) {
        drawer.checked = false;
        drawer.dispatchEvent(new Event('change', { bubbles: true }));
      }
      const trigger = document.querySelector('.md-header .md-search__button') || document.querySelector('.md-header label[for="__search"]');
      if (trigger) trigger.click();
    });
  });
});

// Code panels: preserve authored titles and native copy controls.
let kometaCodeObservers = [];
document$.subscribe(function() {
  kometaCodeObservers.forEach(function(observer) { observer.disconnect(); });
  kometaCodeObservers = [];

  document.querySelectorAll('.md-typeset pre > code').forEach(function(code) {
    const pre = code.parentElement;
    let panel = pre.closest('.highlight');
    if (!panel) {
      panel = document.createElement('div');
      panel.className = 'highlight';
      pre.before(panel);
      panel.appendChild(pre);
    }
    if (panel.querySelector(':scope > .kometa-code-header')) return;

    const header = document.createElement('div');
    header.className = 'kometa-code-header';
    const title = panel.querySelector('.filename') || document.createElement('span');
    title.classList.add('kometa-code-title');
    if (!title.textContent.trim()) {
      const languageClass = [...panel.classList, ...code.classList].find(function(name) {
        return name.startsWith('language-');
      });
      title.textContent = languageClass ? languageClass.slice(9) : 'text';
    }
    header.appendChild(title);
    panel.prepend(header);
    panel.classList.add('kometa-code-panel');

    function placeControls() {
      const controls = pre.querySelector('.md-code__nav');
      if (controls) {
        header.appendChild(controls);
        return true;
      }
      return false;
    }
    // Native controls may be installed after this page subscription runs.
    if (!placeControls()) {
      const observer = new MutationObserver(function() {
        if (placeControls()) observer.disconnect();
      });
      observer.observe(pre, { childList: true });
      kometaCodeObservers.push(observer);
    }
  });
});

// Keep headers visible during page scrolling without changing horizontal table scrolling.
let kometaStickyTableCleanup = function() {};
document$.subscribe(function() {
  kometaStickyTableCleanup();
  const entries = [];
  let frame = 0;
  const header = document.querySelector('.md-header');

  document.querySelectorAll('article table:not([class])').forEach(function(table) {
    if (table.parentElement.closest('table') || !table.tHead || !table.tBodies.length) return;
    const overlay = document.createElement('div');
    overlay.className = 'md-typeset kometa-sticky-table-header';
    overlay.setAttribute('aria-hidden', 'true');
    overlay.hidden = true;
    const copy = document.createElement('table');
    const columns = document.createElement('colgroup');
    copy.appendChild(columns);
    overlay.appendChild(copy);
    document.body.appendChild(overlay);
    function refresh() {
      if (copy.tHead) copy.tHead.remove();
      const head = table.tHead.cloneNode(true);
      head.querySelectorAll('[id]').forEach(function(node) { node.removeAttribute('id'); });
      head.querySelectorAll('[tabindex], a, button, input, select, textarea').forEach(function(node) {
        node.setAttribute('tabindex', '-1');
      });
      Array.from(head.rows).forEach(function(row, rowIndex) {
        Array.from(row.cells).forEach(function(cell, index) {
          const original = table.tHead.rows[rowIndex].cells[index];
          const style = window.getComputedStyle(original);
          ['padding', 'fontSize', 'fontWeight', 'lineHeight', 'textAlign', 'whiteSpace'].forEach(function(property) {
            cell.style[property] = style[property];
          });
        });
      });
      copy.appendChild(head);
      columns.replaceChildren(...Array.from(table.tHead.rows[0].cells, function() {
        return document.createElement('col');
      }));
      schedule();
    }
    // Preserve mouse sorting; keyboard and screen-reader users retain the original header.
    overlay.addEventListener('click', function(event) {
      const cell = event.target.closest('th');
      if (cell) table.tHead.rows[cell.parentElement.sectionRowIndex].cells[cell.cellIndex].click();
    });
    table.addEventListener('afterSort', refresh);
    entries.push({ table, overlay, copy, columns, refresh });
    refresh();
  });

  function update() {
    frame = 0;
    const top = Math.max(0, header ? header.getBoundingClientRect().bottom : 0);
    entries.forEach(function(entry) {
      const { table, overlay, copy, columns } = entry;
      // Closed disclosures can retain table geometry even though their contents are hidden.
      if (table.closest('details:not([open])') || !table.getClientRects().length) {
        overlay.hidden = true;
        return;
      }
      const bounds = table.getBoundingClientRect();
      const head = table.tHead.getBoundingClientRect();
      const scroller = table.closest('.md-typeset__scrollwrap') || table.parentElement;
      const clip = scroller.getBoundingClientRect();
      const left = Math.max(0, bounds.left, clip.left);
      const right = Math.min(window.innerWidth, bounds.right, clip.right);
      const height = Math.min(head.height, bounds.bottom - top);
      overlay.hidden = !(head.top < top && height > 0 && right > left && bounds.width > 0);
      if (overlay.hidden) return;
      Object.assign(overlay.style, {
        top: top + 'px', left: left + 'px', width: (right - left) + 'px', height: height + 'px'
      });
      copy.style.width = Math.max(bounds.width, head.width) + 'px';
      copy.style.transform = 'translateX(' + (bounds.left - left - table.scrollLeft) + 'px)';
      Array.from(table.tHead.rows[0].cells).forEach(function(cell, index) {
        columns.children[index].style.width = cell.getBoundingClientRect().width + 'px';
      });
    });
  }
  function schedule() {
    if (!frame) frame = window.requestAnimationFrame(update);
  }
  const observer = new ResizeObserver(schedule);
  entries.forEach(function(entry) { observer.observe(entry.table); });
  if (header) observer.observe(header);
  document.addEventListener('scroll', schedule, { capture: true, passive: true });
  document.addEventListener('toggle', schedule, true);
  window.addEventListener('resize', schedule);
  schedule();
  kometaStickyTableCleanup = function() {
    window.cancelAnimationFrame(frame);
    observer.disconnect();
    document.removeEventListener('scroll', schedule, true);
    document.removeEventListener('toggle', schedule, true);
    window.removeEventListener('resize', schedule);
    entries.forEach(function(entry) {
      entry.table.removeEventListener('afterSort', entry.refresh);
      entry.overlay.remove();
    });
  };
});

// Table Sort
document$.subscribe(function() {
  var tables = document.querySelectorAll("article table:not([class])")
  tables.forEach(function(table) {
    new Tablesort(table)
  })
})

// Load and render the changelog on the Release Notes page.
document$.subscribe(function() {
  const container = document.getElementById("release-notes-content");
  if (!container || container.dataset.loaded === "true") return;
  container.dataset.loaded = "true";

  const source = document.getElementById("release-notes-source");
  const wikiVersion = location.pathname.match(/^\/en\/([^/]+)\//)?.[1];
  const branch = { latest: "master", develop: "develop", nightly: "nightly" }[wikiVersion] || "master";
  const categories = new Set(["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]);

  function addInlineText(parent, text) {
    const pieces = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g);
    pieces.forEach(function (piece) {
      if (piece.startsWith("`") && piece.endsWith("`")) {
        const code = document.createElement("code");
        code.textContent = piece.slice(1, -1);
        parent.appendChild(code);
      } else if (piece.startsWith("**") && piece.endsWith("**")) {
        const strong = document.createElement("strong");
        strong.textContent = piece.slice(2, -2);
        parent.appendChild(strong);
      } else if (piece.startsWith("*") && piece.endsWith("*")) {
        const emphasis = document.createElement("em");
        emphasis.textContent = piece.slice(1, -1);
        parent.appendChild(emphasis);
      } else {
        parent.appendChild(document.createTextNode(piece));
      }
    });
  }

  function render(markdown) {
    const versions = [];
    let version = null;
    let category = null;
    markdown.split(/\r?\n/).forEach(function (line) {
      if (line.startsWith("## ")) {
        version = { title: line.slice(3).trim(), sections: [] };
        versions.push(version);
        category = null;
      } else if (version && line.startsWith("### ")) {
        category = { title: line.slice(4).trim(), entries: [] };
        version.sections.push(category);
      } else if (category && /^[-*]\s+/.test(line)) {
        category.entries.push(line.replace(/^[-*]\s+/, "").trim());
      } else if (category && line.trim() && !line.startsWith("[")) {
        const lastEntry = category.entries.length - 1;
        if (lastEntry >= 0) category.entries[lastEntry] += " " + line.trim();
      }
    });

    const fragment = document.createDocumentFragment();
    versions.forEach(function (release, index) {
      if (branch === "master" && /^\[?unreleased\]?$/i.test(release.title)) return;
      if (/^\[?v?2\.3\.1(?:\]|\s|$)/i.test(release.title)) return;
      const details = document.createElement("details");
      details.className = "release-notes__release";
      details.open = index === 0;
      const summary = document.createElement("summary");
      summary.className = "release-notes__heading";
      const releaseMatch = release.title.match(/^\[?(v\d+[^\]]*)\]?\s+-\s+(\d{4}-\d{2}-\d{2})$/);
      if (releaseMatch) {
        const versionLabel = document.createElement("code");
        versionLabel.textContent = releaseMatch[1];
        summary.appendChild(versionLabel);
        const releaseDate = document.createElement("span");
        releaseDate.className = "release-notes__date";
        releaseDate.textContent = "  Released " + releaseMatch[2];
        summary.appendChild(releaseDate);
      } else {
        summary.textContent = release.title;
      }
      details.appendChild(summary);
      release.sections.forEach(function (section) {
        if (!categories.has(section.title) || section.entries.length === 0) return;
        const sectionElement = document.createElement("section");
        sectionElement.className = "release-notes__section";
        const heading = document.createElement("h3");
        heading.textContent = section.title;
        sectionElement.appendChild(heading);
        const list = document.createElement("ul");
        section.entries.forEach(function (entry) {
          const item = document.createElement("li");
          addInlineText(item, entry);
          list.appendChild(item);
        });
        sectionElement.appendChild(list);
        details.appendChild(sectionElement);
      });
      fragment.appendChild(details);
    });
    container.replaceChildren(fragment);
  }

  if (source) render(source.textContent);

});

/*!
 * tablesort v5.2.1 (2021-10-30)
 * http://tristen.ca/tablesort/demo/
 * Copyright (c) 2021 ; Licensed MIT
*/

!function(){function a(b,c){if(!(this instanceof a))return new a(b,c);if(!b||"TABLE"!==b.tagName)throw new Error("Element must be a table");this.init(b,c||{})}var b=[],c=function(a){var b;return window.CustomEvent&&"function"==typeof window.CustomEvent?b=new CustomEvent(a):(b=document.createEvent("CustomEvent"),b.initCustomEvent(a,!1,!1,void 0)),b},d=function(a,b){return a.getAttribute(b.sortAttribute||"data-sort")||a.textContent||a.innerText||""},e=function(a,b){return a=a.trim().toLowerCase(),b=b.trim().toLowerCase(),a===b?0:a<b?1:-1},f=function(a,b){return[].slice.call(a).find(function(a){return a.getAttribute("data-sort-column-key")===b})},g=function(a,b){return function(c,d){var e=a(c.td,d.td);return 0===e?b?d.index-c.index:c.index-d.index:e}};a.extend=function(a,c,d){if("function"!=typeof c||"function"!=typeof d)throw new Error("Pattern and sort must be a function");b.push({name:a,pattern:c,sort:d})},a.prototype={init:function(a,b){var c,d,e,f,g=this;if(g.table=a,g.thead=!1,g.options=b,a.rows&&a.rows.length>0)if(a.tHead&&a.tHead.rows.length>0){for(e=0;e<a.tHead.rows.length;e++)if("thead"===a.tHead.rows[e].getAttribute("data-sort-method")){c=a.tHead.rows[e];break}c||(c=a.tHead.rows[a.tHead.rows.length-1]),g.thead=!0}else c=a.rows[0];if(c){var h=function(){g.current&&g.current!==this&&g.current.removeAttribute("aria-sort"),g.current=this,g.sortTable(this)};for(e=0;e<c.cells.length;e++)f=c.cells[e],f.setAttribute("role","columnheader"),"none"!==f.getAttribute("data-sort-method")&&(f.tabindex=0,f.addEventListener("click",h,!1),null!==f.getAttribute("data-sort-default")&&(d=f));d&&(g.current=d,g.sortTable(d))}},sortTable:function(a,h){var i=this,j=a.getAttribute("data-sort-column-key"),k=a.cellIndex,l=e,m="",n=[],o=i.thead?0:1,p=a.getAttribute("data-sort-method"),q=a.getAttribute("aria-sort");if(i.table.dispatchEvent(c("beforeSort")),h||(q="ascending"===q?"descending":"descending"===q?"ascending":i.options.descending?"descending":"ascending",a.setAttribute("aria-sort",q)),!(i.table.rows.length<2)){if(!p){for(var r;n.length<3&&o<i.table.tBodies[0].rows.length;)r=j?f(i.table.tBodies[0].rows[o].cells,j):i.table.tBodies[0].rows[o].cells[k],m=r?d(r,i.options):"",m=m.trim(),m.length>0&&n.push(m),o++;if(!n)return}for(o=0;o<b.length;o++)if(m=b[o],p){if(m.name===p){l=m.sort;break}}else if(n.every(m.pattern)){l=m.sort;break}for(i.col=k,o=0;o<i.table.tBodies.length;o++){var s,t=[],u={},v=0,w=0;if(!(i.table.tBodies[o].rows.length<2)){for(s=0;s<i.table.tBodies[o].rows.length;s++){var r;m=i.table.tBodies[o].rows[s],"none"===m.getAttribute("data-sort-method")?u[v]=m:(r=j?f(m.cells,j):m.cells[i.col],t.push({tr:m,td:r?d(r,i.options):"",index:v})),v++}for("descending"===q?t.sort(g(l,!0)):(t.sort(g(l,!1)),t.reverse()),s=0;s<v;s++)u[s]?(m=u[s],w++):m=t[s-w].tr,i.table.tBodies[o].appendChild(m)}}i.table.dispatchEvent(c("afterSort"))}},refresh:function(){void 0!==this.current&&this.sortTable(this.current,!0)}},"undefined"!=typeof module&&module.exports?module.exports=a:window.Tablesort=a}();

document.addEventListener("DOMContentLoaded", function() {
    tippy('[data-tooltip]', {
      theme: 'material',
      allowHTML: true,
      interactive: true,
      content(reference) {
        const id = reference.getAttribute('data-tooltip-id');
        const tooltipContent = document.getElementById(id);
        return tooltipContent ? tooltipContent.innerHTML : '';
      }
    });
});
