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
    autoScroll: true,
    // Overlay state
    overlayFiles: [],
    loadedOverlays: [],
    selectedOverlays: [],
    overlayGroups: {},  // Group name -> list of overlay info
    activeGroupFilter: '',  // Current group filter
    activeTypeFilter: '',   // Current type filter
    currentPreviewImage: null,  // Current preview image data URI
    availableImages: {},  // Category -> list of image names
    // Poster source state
    posterSource: 'sample',  // sample, plex, tmdb
    selectedPoster: null,    // { source, rating_key, tmdb_id, title, media_type }
    mediaSourceStatus: { plex: false, tmdb: false }
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
    btnCancelRun: document.getElementById('btn-cancel-run'),
    logsRunStatus: document.getElementById('logs-run-status'),
    logsRunId: document.getElementById('logs-run-id'),
    logsRunDuration: document.getElementById('logs-run-duration'),

    // History
    historyList: document.getElementById('history-list'),

    // Overlays
    overlaySource: document.getElementById('overlay-source'),
    overlayList: document.getElementById('overlay-list'),
    selectedOverlayList: document.getElementById('selected-overlay-list'),
    previewCanvas: document.getElementById('preview-canvas'),
    canvasType: document.getElementById('canvas-type'),
    overlayDetails: document.getElementById('overlay-details'),
    detailName: document.getElementById('detail-name'),
    detailType: document.getElementById('detail-type'),
    detailPosition: document.getElementById('detail-position'),
    detailFilters: document.getElementById('detail-filters'),
    btnLoadOverlays: document.getElementById('btn-load-overlays'),
    btnGeneratePreview: document.getElementById('btn-generate-preview'),
    btnDownloadPreview: document.getElementById('btn-download-preview'),
    btnClearSelection: document.getElementById('btn-clear-selection'),
    // Overlay groups and filters
    overlayGroupsSection: document.getElementById('overlay-groups-section'),
    overlayGroups: document.getElementById('overlay-groups'),
    groupsCountBadge: document.getElementById('groups-count-badge'),
    overlaysCountBadge: document.getElementById('overlays-count-badge'),
    overlayFilterGroup: document.getElementById('overlay-filter-group'),
    overlayFilterType: document.getElementById('overlay-filter-type'),
    // Overlay images browser
    overlayImagesDetails: document.getElementById('overlay-images-details'),
    imagesCategorySelect: document.getElementById('images-category-select'),
    overlayImagesGrid: document.getElementById('overlay-images-grid'),
    imagesCountBadge: document.getElementById('images-count-badge'),

    // Template variables
    templateVarsDetails: document.getElementById('template-vars-details'),
    templateVarsBadge: document.getElementById('template-vars-badge'),
    templateVarsInput: document.getElementById('template-vars-input'),
    btnApplyTemplateVars: document.getElementById('btn-apply-template-vars'),
    presetBtns: document.querySelectorAll('.preset-btn'),

    // Poster source elements
    posterSourceTabs: document.querySelectorAll('.poster-tab'),
    posterSourceSample: document.getElementById('poster-source-sample'),
    posterSourcePlex: document.getElementById('poster-source-plex'),
    posterSourceTmdb: document.getElementById('poster-source-tmdb'),
    plexSearch: document.getElementById('plex-search'),
    tmdbSearch: document.getElementById('tmdb-search'),
    tmdbType: document.getElementById('tmdb-type'),
    btnSearchPlex: document.getElementById('btn-search-plex'),
    btnSearchTmdb: document.getElementById('btn-search-tmdb'),
    plexStatus: document.getElementById('plex-status'),
    tmdbStatus: document.getElementById('tmdb-status'),
    plexResults: document.getElementById('plex-results'),
    tmdbResults: document.getElementById('tmdb-results'),
    selectedPosterInfo: document.getElementById('selected-poster-info'),
    selectedPosterTitle: document.getElementById('selected-poster-title'),
    btnClearPoster: document.getElementById('btn-clear-poster')
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
    } else if (tabName === 'overlays') {
        loadOverlayFiles();
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

async function loadPlexLibraries() {
    try {
        const result = await api.get('/media/libraries');
        const libraries = result.libraries || [];

        // Clear and populate the dropdown
        elements.filterLibraries.innerHTML = '';

        if (libraries.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.disabled = true;
            option.textContent = 'No libraries found (check Plex connection)';
            elements.filterLibraries.appendChild(option);
        } else {
            // Add placeholder
            const placeholder = document.createElement('option');
            placeholder.value = '';
            placeholder.disabled = true;
            placeholder.textContent = '-- Select libraries (optional) --';
            elements.filterLibraries.appendChild(placeholder);

            // Add library options
            libraries.forEach(lib => {
                const option = document.createElement('option');
                option.value = lib.title;
                const typeLabel = lib.type === 'movie' ? 'Movies' : 'TV Shows';
                const countLabel = lib.count ? ` - ${lib.count} items` : '';
                option.textContent = `${lib.title} (${typeLabel}${countLabel})`;
                elements.filterLibraries.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load Plex libraries:', error);
        elements.filterLibraries.innerHTML = '<option value="" disabled>Failed to load libraries</option>';
    }
}

async function loadRunPlan() {
    // Load Plex libraries for the filter dropdown
    loadPlexLibraries();

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

    // Gather filters - get selected options from multi-select
    const libraries = Array.from(elements.filterLibraries.selectedOptions).map(opt => opt.value).filter(v => v);
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
    const isRunning = status.running || state.isRunning;
    const runId = status.run_id || state.currentRunId;

    if (isRunning) {
        // Run tab UI
        elements.btnStartRun.classList.add('hidden');
        elements.btnStopRun.classList.remove('hidden');
        elements.currentRunStatus.classList.remove('hidden');
        elements.currentRunId.textContent = runId;
        elements.currentRunStart.textContent = status.start_time ? new Date(status.start_time).toLocaleString() : new Date().toLocaleString();

        // Logs tab UI
        elements.btnCancelRun.classList.remove('hidden');
        elements.logsRunStatus.classList.remove('hidden');
        elements.logsRunId.textContent = runId;

        // Update duration if we have start time
        if (status.start_time) {
            const startTime = new Date(status.start_time);
            const now = new Date();
            const durationSec = Math.floor((now - startTime) / 1000);
            const mins = Math.floor(durationSec / 60);
            const secs = durationSec % 60;
            elements.logsRunDuration.textContent = `(${mins}m ${secs}s)`;
        }
    } else {
        // Run tab UI
        elements.btnStartRun.classList.remove('hidden');
        elements.btnStopRun.classList.add('hidden');
        elements.currentRunStatus.classList.add('hidden');

        // Logs tab UI
        elements.btnCancelRun.classList.add('hidden');
        elements.logsRunStatus.classList.add('hidden');
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
// Overlay Preview
// ============================================================================

async function loadOverlayFiles() {
    // Check media source status when loading overlay tab
    checkMediaSourceStatus();

    // Only load if not already loaded
    if (state.overlayFiles.length > 0) {
        return;
    }

    try {
        const result = await api.get('/overlays');

        // Combine default and custom overlay files
        state.overlayFiles = [];

        if (result.default && result.default.length > 0) {
            state.overlayFiles.push({ label: '-- Default Overlays --', disabled: true });
            state.overlayFiles.push(...result.default.map(f => ({
                path: f.path,
                name: f.name,
                type: 'default'
            })));
        }

        if (result.custom && result.custom.length > 0) {
            state.overlayFiles.push({ label: '-- Custom Overlays --', disabled: true });
            state.overlayFiles.push(...result.custom.map(f => ({
                path: f.path,
                name: f.name,
                type: 'custom'
            })));
        }

        // Populate dropdown
        elements.overlaySource.innerHTML = '<option value="">-- Select an overlay file --</option>';
        state.overlayFiles.forEach((file, index) => {
            if (file.disabled) {
                elements.overlaySource.innerHTML += `<option disabled>${file.label}</option>`;
            } else {
                elements.overlaySource.innerHTML += `<option value="${file.path}">${file.name}</option>`;
            }
        });

    } catch (error) {
        console.error('Failed to load overlay files:', error);
        elements.overlayList.innerHTML = `<p class="placeholder-text">Failed to load overlay files: ${error.message}</p>`;
    }
}

async function loadOverlaysFromFile() {
    const filePath = elements.overlaySource.value;
    if (!filePath) {
        elements.overlayList.innerHTML = '<p class="placeholder-text">Select an overlay file to see available overlays.</p>';
        return;
    }

    elements.overlayList.innerHTML = '<p class="placeholder-text">Loading overlays...</p>';

    try {
        // Build URL with optional template variables
        let url = `/overlays/parse?file_path=${encodeURIComponent(filePath)}`;

        // Parse and validate template variables if provided
        const templateVarsText = elements.templateVarsInput ? elements.templateVarsInput.value.trim() : '';
        if (templateVarsText) {
            try {
                // Validate JSON
                JSON.parse(templateVarsText);
                url += `&template_vars=${encodeURIComponent(templateVarsText)}`;
            } catch (jsonError) {
                console.warn('Invalid template variables JSON, ignoring:', jsonError);
            }
        }

        const result = await api.get(url);

        state.loadedOverlays = result.overlays || [];
        state.overlayGroups = result.groups || {};
        state.activeGroupFilter = '';
        state.activeTypeFilter = '';

        // Update template badge visibility
        if (elements.templateVarsBadge) {
            if (result.has_templates) {
                elements.templateVarsBadge.classList.remove('hidden');
                elements.templateVarsBadge.textContent = `Uses templates (${state.loadedOverlays.length} overlays)`;
            } else {
                elements.templateVarsBadge.classList.add('hidden');
            }
        }

        // Update overlays count badge
        if (elements.overlaysCountBadge) {
            elements.overlaysCountBadge.textContent = state.loadedOverlays.length;
        }

        if (state.loadedOverlays.length === 0) {
            elements.overlayList.innerHTML = '<p class="placeholder-text">No overlays found in this file.</p>';
            hideOverlayGroups();
            return;
        }

        // Render groups and overlay list
        renderOverlayGroups();
        populateGroupFilter();
        renderOverlayList();

    } catch (error) {
        console.error('Failed to parse overlay file:', error);
        elements.overlayList.innerHTML = `<p class="placeholder-text">Failed to parse file: ${error.message}</p>`;
    }
}

function renderOverlayGroups() {
    const groupNames = Object.keys(state.overlayGroups);

    if (groupNames.length === 0) {
        hideOverlayGroups();
        return;
    }

    // Show groups section
    if (elements.overlayGroupsSection) {
        elements.overlayGroupsSection.classList.remove('hidden');
    }

    // Update count badge
    if (elements.groupsCountBadge) {
        elements.groupsCountBadge.textContent = groupNames.length;
    }

    // Render group tags
    if (elements.overlayGroups) {
        elements.overlayGroups.innerHTML = groupNames.map(groupName => {
            const count = state.overlayGroups[groupName].length;
            const isActive = state.activeGroupFilter === groupName;
            return `
                <span class="overlay-group-tag ${isActive ? 'active' : ''}"
                      data-group="${groupName}"
                      onclick="filterByGroup('${groupName}')">
                    ${groupName}
                    <span class="group-count">${count}</span>
                </span>
            `;
        }).join('');
    }
}

function hideOverlayGroups() {
    if (elements.overlayGroupsSection) {
        elements.overlayGroupsSection.classList.add('hidden');
    }
}

function populateGroupFilter() {
    if (!elements.overlayFilterGroup) return;

    // Reset and populate group filter dropdown
    elements.overlayFilterGroup.innerHTML = '<option value="">All Groups</option>';
    const groupNames = Object.keys(state.overlayGroups);
    groupNames.forEach(groupName => {
        const option = document.createElement('option');
        option.value = groupName;
        option.textContent = `${groupName} (${state.overlayGroups[groupName].length})`;
        elements.overlayFilterGroup.appendChild(option);
    });

    // Add "No Group" option if there are ungrouped overlays
    const ungroupedCount = state.loadedOverlays.filter(o => !o.group).length;
    if (ungroupedCount > 0) {
        const option = document.createElement('option');
        option.value = '__none__';
        option.textContent = `No Group (${ungroupedCount})`;
        elements.overlayFilterGroup.appendChild(option);
    }
}

function filterByGroup(groupName) {
    // Toggle filter if clicking same group
    state.activeGroupFilter = state.activeGroupFilter === groupName ? '' : groupName;

    // Update dropdown to match
    if (elements.overlayFilterGroup) {
        elements.overlayFilterGroup.value = state.activeGroupFilter;
    }

    renderOverlayGroups();
    renderOverlayList();
}

function getFilteredOverlays() {
    return state.loadedOverlays.filter((overlay, index) => {
        // Apply group filter
        if (state.activeGroupFilter) {
            if (state.activeGroupFilter === '__none__') {
                if (overlay.group) return false;
            } else {
                if (overlay.group !== state.activeGroupFilter) return false;
            }
        }

        // Apply type filter
        if (state.activeTypeFilter) {
            if (overlay.type !== state.activeTypeFilter) return false;
        }

        return true;
    });
}

function renderOverlayList() {
    const filteredOverlays = getFilteredOverlays();

    if (filteredOverlays.length === 0) {
        elements.overlayList.innerHTML = '<p class="placeholder-text">No overlays match the current filters.</p>';
        return;
    }

    elements.overlayList.innerHTML = filteredOverlays.map((overlay) => {
        const originalIndex = state.loadedOverlays.indexOf(overlay);
        const isSelected = state.selectedOverlays.some(s => s.name === overlay.name);
        const overlayType = overlay.type || 'image';
        const position = overlay.horizontal_align && overlay.vertical_align
            ? `${overlay.vertical_align}-${overlay.horizontal_align}`
            : (overlay.horizontal_offset || overlay.vertical_offset ? 'custom' : 'default');

        // Add group indicator if grouped
        const groupBadge = overlay.group
            ? `<span class="overlay-group-indicator">${overlay.group}</span>`
            : '';

        return `
            <div class="overlay-item ${isSelected ? 'selected' : ''}"
                 data-index="${originalIndex}"
                 data-type="${overlayType}"
                 data-group="${overlay.group || ''}"
                 onclick="toggleOverlaySelection(${originalIndex})">
                <span class="overlay-name">${overlay.name}</span>
                <div class="overlay-meta">
                    <span class="overlay-type">${overlayType}</span>
                    ${groupBadge}
                </div>
                <span class="overlay-position">${position}</span>
            </div>
        `;
    }).join('');
}

function toggleOverlaySelection(index) {
    const overlay = state.loadedOverlays[index];
    if (!overlay) return;

    const existingIndex = state.selectedOverlays.findIndex(s => s.name === overlay.name);

    if (existingIndex >= 0) {
        // Remove from selection
        state.selectedOverlays.splice(existingIndex, 1);
    } else {
        // Add to selection
        state.selectedOverlays.push({ ...overlay });
    }

    // Update UI
    renderOverlayList();
    renderSelectedOverlays();
    showOverlayDetails(overlay);
}

function renderSelectedOverlays() {
    if (state.selectedOverlays.length === 0) {
        elements.selectedOverlayList.innerHTML = '<p class="placeholder-text">Click overlays above to add them to the preview.</p>';
        return;
    }

    elements.selectedOverlayList.innerHTML = state.selectedOverlays.map((overlay, index) => `
        <span class="selected-overlay-tag">
            ${overlay.name}
            <span class="remove-tag" onclick="event.stopPropagation(); removeSelectedOverlay(${index})">×</span>
        </span>
    `).join('');
}

function removeSelectedOverlay(index) {
    state.selectedOverlays.splice(index, 1);
    renderOverlayList();
    renderSelectedOverlays();
}

function clearOverlaySelection() {
    state.selectedOverlays = [];
    renderOverlayList();
    renderSelectedOverlays();
}

function showOverlayDetails(overlay) {
    if (!overlay) {
        elements.overlayDetails.classList.add('hidden');
        return;
    }

    elements.overlayDetails.classList.remove('hidden');
    elements.detailName.textContent = overlay.name || '-';

    // Determine type with more detail
    let type = overlay.type || 'image';
    if (overlay.type === 'text' && overlay.text_content) {
        type = `Text: "${overlay.text_content}"`;
    } else if (overlay.type === 'blur') {
        type = `Blur (${overlay.blur_amount || 50}%)`;
    } else if (overlay.type === 'backdrop') {
        type = 'Backdrop';
    } else if (overlay.default) {
        type = `Image: ${overlay.default}`;
    } else if (overlay.file) {
        type = `Image: ${overlay.file}`;
    }
    elements.detailType.textContent = type;

    // Position
    const hAlign = overlay.horizontal_align || 'center';
    const vAlign = overlay.vertical_align || 'top';
    const hOffset = overlay.horizontal_offset || 0;
    const vOffset = overlay.vertical_offset || 0;
    elements.detailPosition.textContent = `${vAlign}-${hAlign} (offset: ${hOffset}, ${vOffset})`;

    // Filters and group info
    const filters = [];
    if (overlay.group) filters.push(`Group: ${overlay.group}`);
    if (overlay.weight) filters.push(`Weight: ${overlay.weight}`);
    if (overlay.queue) filters.push(`Queue: ${overlay.queue}`);
    if (overlay.plex_all) filters.push('Plex All');
    if (overlay.builder_level) filters.push(`Level: ${overlay.builder_level}`);
    if (overlay.suppress_overlays) filters.push(`Suppresses: ${overlay.suppress_overlays}`);
    elements.detailFilters.textContent = filters.length > 0 ? filters.join(', ') : 'None';
}

async function generateOverlayPreview() {
    if (state.selectedOverlays.length === 0) {
        alert('Please select at least one overlay to preview.');
        return;
    }

    elements.previewCanvas.innerHTML = '<div class="canvas-placeholder"><p>Generating preview...</p></div>';

    try {
        // Build request with poster source info
        const requestData = {
            overlays: state.selectedOverlays,
            canvas_type: elements.canvasType.value
        };

        // Add poster source if selected
        if (state.selectedPoster) {
            requestData.poster_source = state.selectedPoster.source;
            if (state.selectedPoster.source === 'plex') {
                requestData.rating_key = state.selectedPoster.rating_key;
            } else if (state.selectedPoster.source === 'tmdb') {
                requestData.tmdb_id = state.selectedPoster.tmdb_id;
                requestData.media_type = state.selectedPoster.media_type;
            }
        }

        const result = await api.post('/overlays/preview', requestData);

        if (result.image) {
            elements.previewCanvas.innerHTML = `<img src="${result.image}" alt="Overlay Preview" id="preview-image">`;
            // Show download button
            if (elements.btnDownloadPreview) {
                elements.btnDownloadPreview.classList.remove('hidden');
                state.currentPreviewImage = result.image;
            }
        } else if (result.error) {
            elements.previewCanvas.innerHTML = `<div class="canvas-placeholder"><p>Error: ${result.error}</p></div>`;
            if (elements.btnDownloadPreview) {
                elements.btnDownloadPreview.classList.add('hidden');
            }
        }

    } catch (error) {
        console.error('Failed to generate preview:', error);
        elements.previewCanvas.innerHTML = `<div class="canvas-placeholder"><p>Failed to generate preview: ${error.message}</p></div>`;
        if (elements.btnDownloadPreview) {
            elements.btnDownloadPreview.classList.add('hidden');
        }
    }
}

function downloadPreview() {
    if (!state.currentPreviewImage) {
        alert('No preview image to download. Generate a preview first.');
        return;
    }

    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = state.currentPreviewImage;

    // Generate filename based on selected overlays
    const overlayNames = state.selectedOverlays.map(o => o.name).slice(0, 3).join('_');
    const timestamp = new Date().toISOString().slice(0, 10);
    link.download = `overlay_preview_${overlayNames}_${timestamp}.png`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ============================================================================
// Overlay Images Browser
// ============================================================================

async function loadOverlayImages() {
    try {
        const result = await api.get('/overlays/images');
        state.availableImages = result.images || {};

        // Count total images
        let totalCount = 0;
        Object.values(state.availableImages).forEach(images => {
            totalCount += images.length;
        });

        // Update badge
        if (elements.imagesCountBadge) {
            elements.imagesCountBadge.textContent = totalCount;
        }

        // Populate category dropdown
        populateImageCategories();

    } catch (error) {
        console.error('Failed to load overlay images:', error);
    }
}

function populateImageCategories() {
    if (!elements.imagesCategorySelect) return;

    elements.imagesCategorySelect.innerHTML = '<option value="">-- Select category --</option>';

    const categories = Object.keys(state.availableImages).sort();
    categories.forEach(category => {
        const count = state.availableImages[category].length;
        const option = document.createElement('option');
        option.value = category;
        option.textContent = `${category} (${count})`;
        elements.imagesCategorySelect.appendChild(option);
    });
}

function renderOverlayImages(category) {
    if (!elements.overlayImagesGrid) return;

    if (!category || !state.availableImages[category]) {
        elements.overlayImagesGrid.innerHTML = '<p class="placeholder-text">Select a category to view images.</p>';
        return;
    }

    const images = state.availableImages[category];
    if (images.length === 0) {
        elements.overlayImagesGrid.innerHTML = '<p class="placeholder-text">No images in this category.</p>';
        return;
    }

    elements.overlayImagesGrid.innerHTML = images.map(imagePath => {
        const imageName = imagePath.split('/').pop();
        // Build the image URL - images are served from static files
        const imageUrl = `/static/images/overlays/${imagePath}.png`;

        return `
            <div class="overlay-image-item" title="${imagePath}" onclick="copyImagePath('${imagePath}')">
                <img src="${imageUrl}" alt="${imageName}" onerror="this.parentElement.innerHTML='<div class=\\'image-placeholder\\'>?</div><span class=\\'image-name\\'>${imageName}</span>'">
                <span class="image-name">${imageName}</span>
            </div>
        `;
    }).join('');
}

function copyImagePath(imagePath) {
    // Copy the overlay image path to clipboard for use in config
    const fullPath = `default: ${imagePath}`;
    navigator.clipboard.writeText(fullPath).then(() => {
        // Show brief feedback
        alert(`Copied: ${fullPath}`);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// ============================================================================
// Poster Source Selection
// ============================================================================

async function checkMediaSourceStatus() {
    try {
        const status = await api.get('/media/status');
        state.mediaSourceStatus = {
            plex: status.plex?.available || false,
            tmdb: status.tmdb?.available || false
        };

        // Update status displays
        if (elements.plexStatus) {
            if (state.mediaSourceStatus.plex) {
                elements.plexStatus.className = 'source-status connected';
                elements.plexStatus.textContent = `Connected to Plex: ${status.plex.url}`;
            } else {
                elements.plexStatus.className = 'source-status disconnected';
                elements.plexStatus.textContent = 'Plex not configured. Add plex credentials to config.yml.';
            }
        }

        if (elements.tmdbStatus) {
            if (state.mediaSourceStatus.tmdb) {
                elements.tmdbStatus.className = 'source-status connected';
                elements.tmdbStatus.textContent = 'TMDb API configured';
            } else {
                elements.tmdbStatus.className = 'source-status disconnected';
                elements.tmdbStatus.textContent = 'TMDb not configured. Add tmdb apikey to config.yml.';
            }
        }
    } catch (error) {
        console.error('Failed to check media source status:', error);
    }
}

function switchPosterSource(source) {
    state.posterSource = source;

    // Update tabs
    elements.posterSourceTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.source === source);
    });

    // Update content panels
    if (elements.posterSourceSample) {
        elements.posterSourceSample.classList.toggle('active', source === 'sample');
        elements.posterSourceSample.classList.toggle('hidden', source !== 'sample');
    }
    if (elements.posterSourcePlex) {
        elements.posterSourcePlex.classList.toggle('active', source === 'plex');
        elements.posterSourcePlex.classList.toggle('hidden', source !== 'plex');
    }
    if (elements.posterSourceTmdb) {
        elements.posterSourceTmdb.classList.toggle('active', source === 'tmdb');
        elements.posterSourceTmdb.classList.toggle('hidden', source !== 'tmdb');
    }
}

async function searchPlex() {
    const query = elements.plexSearch?.value?.trim();
    if (!query) {
        elements.plexResults.innerHTML = '<p class="placeholder-text">Enter a title to search.</p>';
        return;
    }

    elements.plexResults.innerHTML = '<p class="placeholder-text">Searching...</p>';

    try {
        const result = await api.get(`/media/search?query=${encodeURIComponent(query)}&source=plex`);
        renderMediaResults(result.results, 'plex', elements.plexResults);
    } catch (error) {
        console.error('Plex search error:', error);
        elements.plexResults.innerHTML = `<p class="placeholder-text">Search failed: ${error.message}</p>`;
    }
}

async function searchTmdb() {
    const query = elements.tmdbSearch?.value?.trim();
    if (!query) {
        elements.tmdbResults.innerHTML = '<p class="placeholder-text">Enter a title to search.</p>';
        return;
    }

    const mediaType = elements.tmdbType?.value || 'movie';
    elements.tmdbResults.innerHTML = '<p class="placeholder-text">Searching...</p>';

    try {
        const result = await api.get(`/media/search?query=${encodeURIComponent(query)}&source=tmdb&media_type=${mediaType}`);
        renderMediaResults(result.results, 'tmdb', elements.tmdbResults);
    } catch (error) {
        console.error('TMDb search error:', error);
        elements.tmdbResults.innerHTML = `<p class="placeholder-text">Search failed: ${error.message}</p>`;
    }
}

function renderMediaResults(results, source, container) {
    if (!results || results.length === 0) {
        container.innerHTML = '<p class="placeholder-text">No results found.</p>';
        return;
    }

    container.innerHTML = results.map(item => {
        const title = item.title || item.name;
        const year = item.year || '';
        const isSelected = state.selectedPoster &&
            ((source === 'plex' && state.selectedPoster.rating_key === item.rating_key) ||
             (source === 'tmdb' && state.selectedPoster.tmdb_id === item.tmdb_id));

        // Build poster thumbnail URL
        let posterHtml;
        if (source === 'plex' && item.thumb_url) {
            posterHtml = `<img src="${item.thumb_url}" alt="${title}" loading="lazy">`;
        } else if (source === 'tmdb' && item.poster_url) {
            posterHtml = `<img src="${item.poster_url}" alt="${title}" loading="lazy">`;
        } else {
            posterHtml = '<span class="no-poster">?</span>';
        }

        const dataAttrs = source === 'plex'
            ? `data-rating-key="${item.rating_key}" data-title="${title}" data-type="${item.type}"`
            : `data-tmdb-id="${item.tmdb_id}" data-title="${title}" data-type="${item.type}"`;

        return `
            <div class="media-item ${isSelected ? 'selected' : ''}" ${dataAttrs} onclick="selectMediaItem(this, '${source}')">
                <div class="media-item-poster">${posterHtml}</div>
                <div class="media-item-info">
                    <div class="media-item-title" title="${title}">${title}</div>
                    <div class="media-item-year">${year}${item.type ? ` - ${item.type}` : ''}</div>
                </div>
            </div>
        `;
    }).join('');
}

function selectMediaItem(element, source) {
    const title = element.dataset.title;
    const mediaType = element.dataset.type || 'movie';

    if (source === 'plex') {
        state.selectedPoster = {
            source: 'plex',
            rating_key: element.dataset.ratingKey,
            title: title,
            media_type: mediaType
        };
    } else if (source === 'tmdb') {
        state.selectedPoster = {
            source: 'tmdb',
            tmdb_id: element.dataset.tmdbId,
            title: title,
            media_type: mediaType
        };
    }

    // Update UI
    updateSelectedPosterDisplay();

    // Highlight selected item
    document.querySelectorAll('.media-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
}

function updateSelectedPosterDisplay() {
    if (state.selectedPoster && elements.selectedPosterInfo) {
        elements.selectedPosterInfo.classList.remove('hidden');
        elements.selectedPosterTitle.textContent = `${state.selectedPoster.title} (${state.selectedPoster.source})`;
    } else if (elements.selectedPosterInfo) {
        elements.selectedPosterInfo.classList.add('hidden');
        elements.selectedPosterTitle.textContent = '';
    }
}

function clearSelectedPoster() {
    state.selectedPoster = null;
    updateSelectedPosterDisplay();

    // Remove selection highlighting
    document.querySelectorAll('.media-item').forEach(item => {
        item.classList.remove('selected');
    });
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
    document.getElementById('btn-upload-config').addEventListener('click', () => {
        document.getElementById('config-file-input').click();
    });
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
            } else if (option.dataset.source === 'upload') {
                // Trigger file upload dialog
                document.getElementById('config-file-input').click();
            } else {
                // Show empty editor with template
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

    // Config file upload handler
    const configFileInput = document.getElementById('config-file-input');
    if (configFileInput) {
        configFileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    document.getElementById('config-source-selector').style.display = 'none';
                    document.getElementById('config-editor-container').style.display = 'block';
                    elements.configEditor.value = event.target.result;
                    // Validate the uploaded config
                    validateConfig();
                };
                reader.onerror = () => {
                    showValidation({
                        valid: false,
                        errors: ['Failed to read the uploaded file'],
                        warnings: []
                    });
                };
                reader.readAsText(file);
            }
            // Reset the input so the same file can be uploaded again
            e.target.value = '';
        });
    }

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
    elements.btnCancelRun.addEventListener('click', stopRun);
    elements.autoScrollCheckbox.addEventListener('change', (e) => {
        state.autoScroll = e.target.checked;
    });

    // Overlays
    if (elements.btnLoadOverlays) {
        elements.btnLoadOverlays.addEventListener('click', loadOverlaysFromFile);
    }
    if (elements.overlaySource) {
        elements.overlaySource.addEventListener('change', loadOverlaysFromFile);
    }
    if (elements.btnGeneratePreview) {
        elements.btnGeneratePreview.addEventListener('click', generateOverlayPreview);
    }
    if (elements.btnDownloadPreview) {
        elements.btnDownloadPreview.addEventListener('click', downloadPreview);
    }
    if (elements.btnClearSelection) {
        elements.btnClearSelection.addEventListener('click', clearOverlaySelection);
    }

    // Overlay filters
    if (elements.overlayFilterGroup) {
        elements.overlayFilterGroup.addEventListener('change', (e) => {
            state.activeGroupFilter = e.target.value;
            renderOverlayGroups();
            renderOverlayList();
        });
    }
    if (elements.overlayFilterType) {
        elements.overlayFilterType.addEventListener('change', (e) => {
            state.activeTypeFilter = e.target.value;
            renderOverlayList();
        });
    }

    // Overlay images browser
    if (elements.imagesCategorySelect) {
        elements.imagesCategorySelect.addEventListener('change', (e) => {
            renderOverlayImages(e.target.value);
        });
    }
    if (elements.overlayImagesDetails) {
        elements.overlayImagesDetails.addEventListener('toggle', (e) => {
            // Load images when details is opened for the first time
            if (e.target.open && Object.keys(state.availableImages).length === 0) {
                loadOverlayImages();
            }
        });
    }

    // Template variables
    if (elements.btnApplyTemplateVars) {
        elements.btnApplyTemplateVars.addEventListener('click', loadOverlaysFromFile);
    }
    if (elements.presetBtns) {
        elements.presetBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const preset = btn.dataset.preset;
                if (preset && elements.templateVarsInput) {
                    // Merge with existing or set new
                    try {
                        const existing = elements.templateVarsInput.value.trim();
                        const existingObj = existing ? JSON.parse(existing) : {};
                        const presetObj = JSON.parse(preset);
                        const merged = { ...existingObj, ...presetObj };
                        elements.templateVarsInput.value = JSON.stringify(merged, null, 2);
                    } catch (e) {
                        elements.templateVarsInput.value = preset;
                    }
                }
            });
        });
    }

    // Poster source tabs
    elements.posterSourceTabs.forEach(tab => {
        tab.addEventListener('click', () => switchPosterSource(tab.dataset.source));
    });

    // Media search
    if (elements.btnSearchPlex) {
        elements.btnSearchPlex.addEventListener('click', searchPlex);
    }
    if (elements.plexSearch) {
        elements.plexSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchPlex();
        });
    }
    if (elements.btnSearchTmdb) {
        elements.btnSearchTmdb.addEventListener('click', searchTmdb);
    }
    if (elements.tmdbSearch) {
        elements.tmdbSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchTmdb();
        });
    }
    if (elements.btnClearPoster) {
        elements.btnClearPoster.addEventListener('click', clearSelectedPoster);
    }
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

// Make functions available globally for onclick handlers
window.restoreBackup = restoreBackup;
window.viewRunLogs = viewRunLogs;
window.toggleOverlaySelection = toggleOverlaySelection;
window.removeSelectedOverlay = removeSelectedOverlay;
window.selectMediaItem = selectMediaItem;
window.filterByGroup = filterByGroup;
window.copyImagePath = copyImagePath;
