/**
 * Kometa Web UI - Frontend Application
 *
 * A safe, read-only by default web interface for Kometa.
 */

// ============================================================================
// State Management
// ============================================================================

const state = {
    currentTab: 'config',
    runMode: 'dry-run',
    isRunning: false,
    currentRunId: null,
    applyEnabled: false,
    wsLogs: null,
    wsStatus: null,
    autoScroll: true
};

// ============================================================================
// DOM Elements
// ============================================================================

const elements = {
    // Safety banner
    safetyBanner: document.getElementById('safety-banner'),
    modeIndicator: document.getElementById('mode-indicator'),

    // Connection status
    connectionStatus: document.getElementById('connection-status'),

    // Navigation
    navTabs: document.querySelectorAll('.nav-tab'),
    tabContents: document.querySelectorAll('.tab-content'),

    // Config
    configEditor: document.getElementById('config-editor'),
    validationMessages: document.getElementById('validation-messages'),
    backupsList: document.getElementById('backups-list'),
    editorTabs: document.querySelectorAll('.editor-tab'),
    editorViews: document.querySelectorAll('.editor-view'),
    sourceOptions: document.querySelectorAll('.source-option'),

    // Run
    runModeOptions: document.querySelectorAll('.mode-option'),
    applyConfirmation: document.getElementById('apply-confirmation'),
    applyConfirmInput: document.getElementById('apply-confirm-input'),
    runPlan: document.getElementById('run-plan'),
    btnStartRun: document.getElementById('btn-start-run'),
    btnStopRun: document.getElementById('btn-stop-run'),
    currentRunStatus: document.getElementById('current-run-status'),
    currentRunId: document.getElementById('current-run-id'),
    currentRunStart: document.getElementById('current-run-start'),
    filterLibraries: document.getElementById('filter-libraries'),
    filterCollections: document.getElementById('filter-collections'),
    filterType: document.getElementById('filter-type'),

    // Logs
    logsOutput: document.getElementById('logs-output'),
    autoScrollCheckbox: document.getElementById('auto-scroll'),
    btnClearLogs: document.getElementById('btn-clear-logs'),

    // History
    historyList: document.getElementById('history-list')
};

// ============================================================================
// API Functions
// ============================================================================

const api = {
    async get(endpoint) {
        const response = await fetch(`/api${endpoint}`);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Request failed: ${response.status}`);
        }
        return response.json();
    },

    async post(endpoint, data = {}) {
        const response = await fetch(`/api${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Request failed: ${response.status}`);
        }
        return response.json();
    }
};

// ============================================================================
// Tab Navigation
// ============================================================================

function switchTab(tabName) {
    state.currentTab = tabName;

    // Update nav tabs
    elements.navTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Update tab contents
    elements.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
        content.classList.toggle('hidden', content.id !== `tab-${tabName}`);
    });

    // Load tab-specific data
    if (tabName === 'run') {
        loadRunPlan();
    } else if (tabName === 'history') {
        loadRunHistory();
    }
}

// ============================================================================
// Configuration Management
// ============================================================================

async function loadConfig() {
    try {
        const result = await api.get('/config');

        if (result.exists) {
            elements.configEditor.value = result.content;

            // Hide source selector once loaded
            document.getElementById('config-source-selector').style.display = 'none';
            document.getElementById('config-editor-container').style.display = 'block';

            if (result.validation) {
                showValidation(result.validation);
            }
        } else {
            // Show source selector
            document.getElementById('config-source-selector').style.display = 'block';
            document.getElementById('config-editor-container').style.display = 'none';
        }
    } catch (error) {
        showValidation({
            valid: false,
            errors: [`Failed to load config: ${error.message}`],
            warnings: []
        });
    }
}

async function saveConfig() {
    try {
        const content = elements.configEditor.value;
        const result = await api.post('/config', { content });

        showValidation({
            valid: true,
            errors: [],
            warnings: result.validation?.warnings || [],
            message: `Config saved successfully. Backup created: ${result.backup_path || 'N/A'}`
        });

        // Reload backups list
        loadBackups();
    } catch (error) {
        showValidation({
            valid: false,
            errors: [error.message],
            warnings: []
        });
    }
}

async function validateConfig() {
    try {
        const content = elements.configEditor.value;
        const result = await api.post('/config/validate', { content });
        showValidation(result);
    } catch (error) {
        showValidation({
            valid: false,
            errors: [error.message],
            warnings: []
        });
    }
}

function showValidation(result) {
    const el = elements.validationMessages;
    el.innerHTML = '';
    el.classList.remove('hidden', 'error', 'warning', 'success');

    if (result.valid) {
        el.classList.add('success');
        if (result.message) {
            el.innerHTML = `<strong>✓ ${result.message}</strong>`;
        } else {
            el.innerHTML = '<strong>✓ Configuration is valid</strong>';
        }

        if (result.warnings && result.warnings.length > 0) {
            el.classList.remove('success');
            el.classList.add('warning');
            el.innerHTML += '<ul>' + result.warnings.map(w => `<li>${w}</li>`).join('') + '</ul>';
        }
    } else {
        el.classList.add('error');
        el.innerHTML = '<strong>✗ Configuration has errors</strong>';

        if (result.errors && result.errors.length > 0) {
            el.innerHTML += '<ul>' + result.errors.map(e => `<li>${e}</li>`).join('') + '</ul>';
        }
    }
}

async function loadBackups() {
    try {
        const result = await api.get('/config/backups');

        if (result.backups.length === 0) {
            elements.backupsList.innerHTML = '<p class="loading">No backups available</p>';
            return;
        }

        elements.backupsList.innerHTML = result.backups.map(backup => `
            <div class="backup-item">
                <div class="backup-info">
                    <span class="backup-name">${backup.name}</span>
                    <span class="backup-date">${new Date(backup.created).toLocaleString()}</span>
                </div>
                <button class="btn btn-secondary" onclick="restoreBackup('${backup.name}')">
                    Restore
                </button>
            </div>
        `).join('');
    } catch (error) {
        elements.backupsList.innerHTML = `<p class="loading">Failed to load backups: ${error.message}</p>`;
    }
}

async function restoreBackup(backupName) {
    if (!confirm(`Restore configuration from ${backupName}? Current config will be backed up first.`)) {
        return;
    }

    try {
        await api.post(`/config/restore/${backupName}`);
        await loadConfig();
        showValidation({
            valid: true,
            errors: [],
            warnings: [],
            message: `Restored from ${backupName}`
        });
    } catch (error) {
        showValidation({
            valid: false,
            errors: [error.message],
            warnings: []
        });
    }
}

// ============================================================================
// Run Management
// ============================================================================

async function loadRunPlan() {
    try {
        const plan = await api.get('/run/plan');
        state.applyEnabled = plan.apply_enabled;

        let html = '';

        if (!plan.valid) {
            html = `<div class="plan-loading">${plan.warnings.join(', ')}</div>`;
        } else {
            // Libraries
            if (plan.libraries && plan.libraries.length > 0) {
                html += `
                    <div class="plan-section">
                        <div class="plan-section-title">Libraries</div>
                        <ul class="plan-list">
                            ${plan.libraries.map(lib => `<li>${lib.name} (${lib.files.length} files)</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            // Collection files
            if (plan.collection_files && plan.collection_files.length > 0) {
                html += `
                    <div class="plan-section">
                        <div class="plan-section-title">Collection Files</div>
                        <ul class="plan-list">
                            ${plan.collection_files.slice(0, 5).map(f => `<li>${f}</li>`).join('')}
                            ${plan.collection_files.length > 5 ? `<li>...and ${plan.collection_files.length - 5} more</li>` : ''}
                        </ul>
                    </div>
                `;
            }

            // Integrations
            const configuredIntegrations = Object.entries(plan.integrations || {})
                .filter(([_, v]) => v.configured)
                .map(([k, _]) => k);

            if (configuredIntegrations.length > 0) {
                html += `
                    <div class="plan-section">
                        <div class="plan-section-title">Integrations</div>
                        <ul class="plan-list">
                            ${configuredIntegrations.map(i => `<li>${i.charAt(0).toUpperCase() + i.slice(1)}: Configured</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            // Paths
            if (plan.paths) {
                html += `
                    <div class="plan-section">
                        <div class="plan-section-title">Paths</div>
                        <ul class="plan-list">
                            ${Object.entries(plan.paths).map(([k, v]) => `<li>${k}: ${v}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        }

        elements.runPlan.innerHTML = `<h3>Run Plan Preview</h3>${html}`;

        // Update apply mode availability
        updateRunModeUI();

    } catch (error) {
        elements.runPlan.innerHTML = `<h3>Run Plan Preview</h3><div class="plan-loading">Failed to load: ${error.message}</div>`;
    }
}

function updateRunModeUI() {
    const applyOption = document.querySelector('.mode-option[data-mode="apply"]');
    const applyRadio = document.getElementById('mode-apply');

    if (!state.applyEnabled) {
        applyOption.classList.add('disabled');
        applyRadio.disabled = true;
    } else {
        applyOption.classList.remove('disabled');
        applyRadio.disabled = false;
    }
}

function setRunMode(mode) {
    state.runMode = mode;

    // Update UI
    elements.runModeOptions.forEach(option => {
        option.classList.toggle('selected', option.dataset.mode === mode);
    });

    // Update radio buttons
    document.getElementById('mode-dry-run').checked = mode === 'dry-run';
    document.getElementById('mode-apply').checked = mode === 'apply';

    // Show/hide apply confirmation
    elements.applyConfirmation.classList.toggle('hidden', mode !== 'apply');

    // Update button text
    elements.btnStartRun.textContent = mode === 'dry-run' ? 'Start Dry Run' : 'Start Apply Run';

    // Update safety banner
    updateSafetyBanner();
}

function updateSafetyBanner() {
    if (state.runMode === 'apply') {
        elements.safetyBanner.classList.remove('safe');
        elements.safetyBanner.classList.add('armed');
        elements.modeIndicator.textContent = 'APPLY MODE - ARMED';
        elements.safetyBanner.querySelector('.mode-description').textContent = 'Changes WILL be made to Plex';
    } else {
        elements.safetyBanner.classList.remove('armed');
        elements.safetyBanner.classList.add('safe');
        elements.modeIndicator.textContent = 'DRY RUN MODE';
        elements.safetyBanner.querySelector('.mode-description').textContent = 'No changes will be made to Plex';
    }
}

async function startRun() {
    const isDryRun = state.runMode === 'dry-run';

    // For apply mode, verify confirmation
    if (!isDryRun) {
        const confirmation = elements.applyConfirmInput.value;
        if (confirmation !== 'APPLY CHANGES') {
            alert('Please type "APPLY CHANGES" to confirm apply mode.');
            return;
        }
    }

    // Gather filters
    const libraries = elements.filterLibraries.value.split('|').filter(l => l.trim());
    const collections = elements.filterCollections.value.split('|').filter(c => c.trim());
    const runType = elements.filterType.value || null;

    try {
        let result;
        if (isDryRun) {
            result = await api.post('/run', {
                dry_run: true,
                libraries: libraries.length > 0 ? libraries : null,
                collections: collections.length > 0 ? collections : null,
                run_type: runType
            });
        } else {
            result = await api.post('/run/apply', {
                confirmation: 'APPLY CHANGES',
                dry_run: false,
                libraries: libraries.length > 0 ? libraries : null,
                collections: collections.length > 0 ? collections : null,
                run_type: runType
            });
        }

        state.isRunning = true;
        state.currentRunId = result.run_id;

        updateRunStatusUI(result);
        connectLogWebSocket();

        // Switch to logs tab
        switchTab('logs');

    } catch (error) {
        alert(`Failed to start run: ${error.message}`);
    }
}

async function stopRun() {
    try {
        await api.post('/run/stop');
        state.isRunning = false;
        updateRunStatusUI({ running: false });
    } catch (error) {
        alert(`Failed to stop run: ${error.message}`);
    }
}

function updateRunStatusUI(status) {
    if (status.running || state.isRunning) {
        elements.btnStartRun.classList.add('hidden');
        elements.btnStopRun.classList.remove('hidden');
        elements.currentRunStatus.classList.remove('hidden');
        elements.currentRunId.textContent = status.run_id || state.currentRunId;
        elements.currentRunStart.textContent = status.start_time ? new Date(status.start_time).toLocaleString() : new Date().toLocaleString();
    } else {
        elements.btnStartRun.classList.remove('hidden');
        elements.btnStopRun.classList.add('hidden');
        elements.currentRunStatus.classList.add('hidden');
    }
}

async function checkRunStatus() {
    try {
        const status = await api.get('/run/status');
        state.isRunning = status.running;
        if (status.running) {
            state.currentRunId = status.run_id;
        }
        updateRunStatusUI(status);
    } catch (error) {
        console.error('Failed to check run status:', error);
    }
}

// ============================================================================
// WebSocket Connections
// ============================================================================

function connectLogWebSocket() {
    if (state.wsLogs) {
        state.wsLogs.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    state.wsLogs = new WebSocket(`${protocol}//${window.location.host}/ws/logs`);

    state.wsLogs.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
            appendLog(data.data);
        }
    };

    state.wsLogs.onclose = () => {
        state.isRunning = false;
        updateRunStatusUI({ running: false });
    };

    state.wsLogs.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function connectStatusWebSocket() {
    if (state.wsStatus) {
        state.wsStatus.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    state.wsStatus = new WebSocket(`${protocol}//${window.location.host}/ws/status`);

    state.wsStatus.onmessage = (event) => {
        const status = JSON.parse(event.data);
        state.isRunning = status.running;
        updateRunStatusUI(status);
        updateConnectionStatus(true);
    };

    state.wsStatus.onclose = () => {
        updateConnectionStatus(false);
        // Reconnect after a delay
        setTimeout(connectStatusWebSocket, 5000);
    };

    state.wsStatus.onerror = () => {
        updateConnectionStatus(false);
    };
}

function updateConnectionStatus(connected) {
    const statusDot = elements.connectionStatus.querySelector('.status-dot');
    const statusText = elements.connectionStatus.querySelector('.status-text');

    if (connected) {
        statusDot.classList.add('connected');
        statusDot.classList.remove('disconnected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusDot.classList.add('disconnected');
        statusText.textContent = 'Disconnected';
    }
}

// ============================================================================
// Logs
// ============================================================================

function appendLog(line) {
    const el = elements.logsOutput;
    el.textContent += line + '\n';

    if (state.autoScroll) {
        el.scrollTop = el.scrollHeight;
    }
}

function clearLogs() {
    elements.logsOutput.textContent = 'Logs cleared.\n';
}

// ============================================================================
// Run History
// ============================================================================

async function loadRunHistory() {
    try {
        const result = await api.get('/runs?limit=50');

        if (result.runs.length === 0) {
            elements.historyList.innerHTML = '<p class="loading">No runs recorded yet</p>';
            return;
        }

        elements.historyList.innerHTML = result.runs.map(run => `
            <div class="history-item" onclick="viewRunLogs('${run.id}')">
                <div class="history-info">
                    <span class="history-id">${run.id}</span>
                    <span class="history-time">
                        ${new Date(run.start_time).toLocaleString()}
                        ${run.duration_seconds ? ` (${formatDuration(run.duration_seconds)})` : ''}
                    </span>
                </div>
                <div class="history-meta">
                    <span class="history-badge ${run.dry_run ? 'dry-run' : 'apply'}">
                        ${run.dry_run ? 'Dry Run' : 'Apply'}
                    </span>
                    <span class="history-status ${run.status}">
                        ${run.status.charAt(0).toUpperCase() + run.status.slice(1)}
                    </span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        elements.historyList.innerHTML = `<p class="loading">Failed to load history: ${error.message}</p>`;
    }
}

async function viewRunLogs(runId) {
    try {
        const result = await api.get(`/logs/${runId}`);
        elements.logsOutput.textContent = result.logs.join('\n');
        switchTab('logs');
    } catch (error) {
        alert(`Failed to load logs: ${error.message}`);
    }
}

function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    } else if (seconds < 3600) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}m ${secs}s`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    }
}

// ============================================================================
// Event Listeners
// ============================================================================

function initEventListeners() {
    // Navigation
    elements.navTabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Config actions
    document.getElementById('btn-load-config').addEventListener('click', loadConfig);
    document.getElementById('btn-validate').addEventListener('click', validateConfig);
    document.getElementById('btn-save-config').addEventListener('click', saveConfig);

    // Editor tabs
    elements.editorTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            elements.editorTabs.forEach(t => t.classList.toggle('active', t === tab));
            elements.editorViews.forEach(v => {
                v.classList.toggle('active', v.id === `view-${tab.dataset.view}`);
                v.classList.toggle('hidden', v.id !== `view-${tab.dataset.view}`);
            });
        });
    });

    // Source options
    elements.sourceOptions.forEach(option => {
        option.addEventListener('click', () => {
            elements.sourceOptions.forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');

            if (option.dataset.source === 'existing') {
                loadConfig();
            } else {
                // Show empty editor
                document.getElementById('config-source-selector').style.display = 'none';
                document.getElementById('config-editor-container').style.display = 'block';
                elements.configEditor.value = `# Kometa Configuration
# See https://kometa.wiki for full documentation

plex:
  url: http://plex:32400
  token: YOUR_PLEX_TOKEN

tmdb:
  apikey: YOUR_TMDB_API_KEY

libraries:
  Movies:
    collection_files:
      - file: config/Movies.yml
`;
            }
        });
    });

    // Run mode
    elements.runModeOptions.forEach(option => {
        option.addEventListener('click', () => {
            if (!option.classList.contains('disabled')) {
                setRunMode(option.dataset.mode);
            }
        });
    });

    // Run actions
    elements.btnStartRun.addEventListener('click', startRun);
    elements.btnStopRun.addEventListener('click', stopRun);

    // Logs
    elements.btnClearLogs.addEventListener('click', clearLogs);
    elements.autoScrollCheckbox.addEventListener('change', (e) => {
        state.autoScroll = e.target.checked;
    });
}

// ============================================================================
// Initialization
// ============================================================================

async function init() {
    initEventListeners();

    // Load initial data
    await loadConfig();
    await loadBackups();
    await checkRunStatus();

    // Connect WebSocket for status updates
    connectStatusWebSocket();

    // Check for apply mode from server
    try {
        const health = await api.get('/health');
        state.applyEnabled = health.apply_enabled;
        updateRunModeUI();
    } catch (error) {
        console.error('Failed to check health:', error);
    }
}

// Start the app
document.addEventListener('DOMContentLoaded', init);

// Make restoreBackup available globally for onclick
window.restoreBackup = restoreBackup;
window.viewRunLogs = viewRunLogs;
