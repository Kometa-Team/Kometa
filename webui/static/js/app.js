/* Kometa WebUI – client-side logic */

// ─── State ────────────────────────────────────────────────────────────────
let isRunning = false;
let sseSource = null;

// ─── DOM refs ─────────────────────────────────────────────────────────────
const $  = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

const statusDot   = $('#status-dot');
const statusText  = $('#status-text');
const btnRun      = $('#btn-run');
const btnStop     = $('#btn-stop');
const logOutput   = $('#log-output');
const logContainer= $('#log-container');
const cmdPreview  = $('#cmd-preview');
const configSelect= $('#config-select');
const historyList = $('#history-list');
const autoscroll  = $('#autoscroll');

// ─── Init ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadConfigs();
  refreshStatus();
  connectSSE();
  bindEvents();
  updatePreview();
  setInterval(refreshStatus, 5000);
});

// ─── SSE log stream ───────────────────────────────────────────────────────
function connectSSE() {
  if (sseSource) sseSource.close();
  sseSource = new EventSource('/api/logs/stream');
  sseSource.onmessage = (e) => {
    const line = JSON.parse(e.data);
    appendLog(line);
  };
  sseSource.onerror = () => {
    // SSE reconnects automatically; do nothing
  };
}

// ─── Log rendering ────────────────────────────────────────────────────────
function appendLog(line) {
  const el = document.createElement('span');
  el.className = 'log-line ' + classifyLine(line);
  el.textContent = line + '\n';
  logOutput.appendChild(el);

  // Trim to last 3000 visual lines to avoid DOM bloat
  const children = logOutput.children;
  while (children.length > 3000) {
    logOutput.removeChild(children[0]);
  }

  if (autoscroll.checked) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }
}

function classifyLine(line) {
  const l = line.toLowerCase();
  if (l.includes('[webui]'))                return 'webui';
  if (l.includes('critical'))               return 'critical';
  if (l.includes(' | error   |') || l.includes('error'))   return 'error';
  if (l.includes(' | warning |') || l.includes('warning')) return 'warning';
  if (l.includes(' | debug   |'))           return 'debug';
  if (l.includes('processed') || l.includes('complete') || l.includes('finished')) return 'success';
  return 'info';
}

// ─── Status polling ───────────────────────────────────────────────────────
async function refreshStatus() {
  try {
    const data = await fetchJSON('/api/status');
    setRunning(data.running);
    renderHistory(data.history || []);
  } catch (_) { /* network error, ignore */ }
}

function setRunning(running) {
  isRunning = running;
  if (running) {
    statusDot.className  = 'dot running';
    statusText.textContent = 'Running…';
    btnRun.disabled  = true;
    btnStop.disabled = false;
  } else {
    statusDot.className  = 'dot idle';
    statusText.textContent = 'Idle';
    btnRun.disabled  = false;
    btnStop.disabled = true;
  }
}

// ─── Config list ─────────────────────────────────────────────────────────
async function loadConfigs() {
  try {
    const configs = await fetchJSON('/api/configs');
    const current = configSelect.value;
    // Keep the default option, replace the rest
    while (configSelect.options.length > 1) configSelect.remove(1);
    configs.forEach(c => {
      const opt = new Option(c.label, c.value);
      configSelect.appendChild(opt);
    });
    if (current) configSelect.value = current;
  } catch (_) {}
}

// ─── Run / Stop ───────────────────────────────────────────────────────────
async function startRun() {
  const payload = buildPayload();
  logOutput.innerHTML = '';  // clear for new run

  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      appendLog(`[WebUI] Error: ${data.error}`);
      return;
    }
    setRunning(true);
  } catch (e) {
    appendLog(`[WebUI] Network error: ${e}`);
  }
}

async function stopRun() {
  try {
    const res = await fetch('/api/stop', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) appendLog(`[WebUI] Stop error: ${data.error}`);
  } catch (e) {
    appendLog(`[WebUI] Network error: ${e}`);
  }
}

// ─── Payload builder ─────────────────────────────────────────────────────
function buildPayload() {
  return {
    config:              configSelect.value,
    run:                 $('#opt-run').checked,
    test:                $('#opt-test').checked,
    ignore_schedules:    $('#opt-ignore-schedules').checked,
    times:               $('#opt-times').value.trim(),
    resume:              $('#opt-resume').value.trim(),
    collections_only:    $('#opt-collections-only').checked,
    metadata_only:       $('#opt-metadata-only').checked,
    overlays_only:       $('#opt-overlays-only').checked,
    playlists_only:      $('#opt-playlists-only').checked,
    operations_only:     $('#opt-operations-only').checked,
    run_libraries:       $('#opt-run-libraries').value.trim(),
    run_collections:     $('#opt-run-collections').value.trim(),
    run_files:           $('#opt-run-files').value.trim(),
    debug:               $('#opt-debug').checked,
    trace:               $('#opt-trace').checked,
    delete_collections:  $('#opt-delete-collections').checked,
    delete_labels:       $('#opt-delete-labels').checked,
    no_verify_ssl:       $('#opt-no-verify-ssl').checked,
    no_countdown:        $('#opt-no-countdown').checked,
    timeout:             $('#opt-timeout').value.trim(),
    width:               $('#opt-width').value.trim(),
  };
}

// ─── Command preview ─────────────────────────────────────────────────────
function updatePreview() {
  const p = buildPayload();
  const parts = ['python kometa.py'];

  if (p.config)              parts.push(`--config "${p.config}"`);
  if (p.run)                 parts.push('--run');
  if (p.test)                parts.push('--tests');
  if (p.ignore_schedules)    parts.push('--ignore-schedules');
  if (p.times)               parts.push(`--times ${p.times}`);
  if (p.resume)              parts.push(`--resume "${p.resume}"`);
  if (p.collections_only)    parts.push('--collections-only');
  if (p.metadata_only)       parts.push('--metadata-only');
  if (p.overlays_only)       parts.push('--overlays-only');
  if (p.playlists_only)      parts.push('--playlists-only');
  if (p.operations_only)     parts.push('--operations-only');
  if (p.run_libraries)       parts.push(`--run-libraries "${p.run_libraries}"`);
  if (p.run_collections)     parts.push(`--run-collections "${p.run_collections}"`);
  if (p.run_files)           parts.push(`--run-files "${p.run_files}"`);
  if (p.debug)               parts.push('--debug');
  if (p.trace)               parts.push('--trace');
  if (p.delete_collections)  parts.push('--delete-collections');
  if (p.delete_labels)       parts.push('--delete-labels');
  if (p.no_verify_ssl)       parts.push('--no-verify-ssl');
  if (p.no_countdown)        parts.push('--no-countdown');
  if (p.timeout)             parts.push(`--timeout ${p.timeout}`);
  if (p.width)               parts.push(`--width ${p.width}`);

  cmdPreview.textContent = parts.join(' \\\n  ');
}

// ─── History rendering ────────────────────────────────────────────────────
function renderHistory(history) {
  if (!history.length) {
    historyList.innerHTML = '<p class="dim">No runs yet.</p>';
    return;
  }
  historyList.innerHTML = history.map(h => {
    const ok = h.exit_code === 0;
    const startStr = h.start ? new Date(h.start).toLocaleString() : '?';
    const argsStr  = (h.args || []).join(' ') || '(no args)';
    return `
      <div class="history-item">
        <span class="${ok ? 'exit-ok' : 'exit-err'}">${ok ? '✓' : '✗'} ${h.exit_code}</span>
        <span class="h-time">${startStr}</span>
        <span class="h-args" title="${escHtml(argsStr)}">${escHtml(argsStr)}</span>
      </div>`;
  }).join('');
}

// ─── Event bindings ───────────────────────────────────────────────────────
function bindEvents() {
  btnRun.addEventListener('click', startRun);
  btnStop.addEventListener('click', stopRun);

  $('#refresh-configs').addEventListener('click', loadConfigs);

  $('#btn-clear-logs').addEventListener('click', () => {
    logOutput.innerHTML = '';
  });

  $('#btn-copy-logs').addEventListener('click', () => {
    const text = $$('.log-line').map(el => el.textContent).join('');
    navigator.clipboard.writeText(text).catch(() => {});
  });

  // Mutual exclusivity: scope checkboxes (at most one active)
  const scopeBoxes = ['opt-collections-only', 'opt-metadata-only', 'opt-overlays-only', 'opt-playlists-only', 'opt-operations-only'];
  scopeBoxes.forEach(id => {
    $(`#${id}`).addEventListener('change', (e) => {
      if (e.target.checked) {
        scopeBoxes.filter(x => x !== id).forEach(x => { $(`#${x}`).checked = false; });
      }
      updatePreview();
    });
  });

  // Preview update on any input change
  $$('input, select').forEach(el => {
    el.addEventListener('change', updatePreview);
    el.addEventListener('input',  updatePreview);
  });

  // Hide schedule times when run-once is on (schedule is irrelevant)
  $('#opt-run').addEventListener('change', updatePreview);
}

// ─── Utilities ────────────────────────────────────────────────────────────
async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
