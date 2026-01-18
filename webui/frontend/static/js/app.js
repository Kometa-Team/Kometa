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
        // Load live preview with Dune poster (on first visit or refresh)
        if (window.livePreview) {
            window.livePreview.loadPreview();
        }
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

            // Sync forms and render libraries after loading config
            syncYamlToForms();
            renderLibrariesFromConfig();
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
// Config Editor - Sub-tab Management & Form Sync
// ============================================================================

// Track currently active config subtab
let currentConfigSubtab = 'plex';

// Parsed config object (synced between forms and YAML)
let parsedConfig = {};

// Flag to prevent infinite sync loops
let isSyncing = false;

/**
 * Initialize config subtabs
 */
function initConfigSubtabs() {
    const subtabs = document.querySelectorAll('.config-subtab');
    const panels = document.querySelectorAll('.subtab-panel');

    subtabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetSubtab = tab.dataset.subtab;

            // Sync current form to YAML before switching (unless going to YAML tab)
            if (currentConfigSubtab !== 'yaml' && targetSubtab === 'yaml') {
                syncFormsToYaml();
            }

            // Sync YAML to forms when leaving YAML tab
            if (currentConfigSubtab === 'yaml' && targetSubtab !== 'yaml') {
                syncYamlToForms();
            }

            // Update active states
            subtabs.forEach(t => t.classList.toggle('active', t === tab));
            panels.forEach(p => {
                const isActive = p.id === `subtab-${targetSubtab}`;
                p.classList.toggle('active', isActive);
                p.classList.toggle('hidden', !isActive);
            });

            currentConfigSubtab = targetSubtab;

            // Load libraries if switching to libraries tab
            if (targetSubtab === 'libraries') {
                renderLibrariesFromConfig();
            }
        });
    });

    // Initialize form field change handlers for real-time sync
    initFormFieldListeners();

    // Initialize range slider value display
    initRangeSliders();

    // Initialize sortable run order list
    initSortableRunOrder();
}

/**
 * Initialize form field listeners for real-time YAML sync
 */
function initFormFieldListeners() {
    const formFields = document.querySelectorAll('[data-config-path]');

    formFields.forEach(field => {
        const eventType = field.type === 'checkbox' ? 'change' : 'input';
        field.addEventListener(eventType, () => {
            if (!isSyncing) {
                syncFormsToYaml();
            }
        });
    });
}

/**
 * Initialize range sliders to show their current value
 */
function initRangeSliders() {
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        const valueDisplay = document.getElementById(`${input.id}-value`);
        if (valueDisplay) {
            input.addEventListener('input', () => {
                valueDisplay.textContent = input.value;
            });
        }
    });
}

/**
 * Initialize drag-and-drop sortable run order list
 */
function initSortableRunOrder() {
    const list = document.getElementById('settings-run-order');
    if (!list) return;

    let draggedItem = null;

    list.querySelectorAll('li').forEach(item => {
        item.setAttribute('draggable', 'true');

        item.addEventListener('dragstart', (e) => {
            draggedItem = item;
            item.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });

        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
            draggedItem = null;
            syncFormsToYaml();
        });

        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = getDragAfterElement(list, e.clientY);
            if (afterElement == null) {
                list.appendChild(draggedItem);
            } else {
                list.insertBefore(draggedItem, afterElement);
            }
        });
    });
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('li:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

/**
 * Parse YAML from the editor into parsedConfig object
 */
function parseYamlToConfig() {
    const yamlContent = elements.configEditor.value;
    if (!yamlContent.trim()) {
        parsedConfig = {};
        return;
    }

    try {
        // Use js-yaml if available, otherwise basic parsing
        if (typeof jsyaml !== 'undefined') {
            parsedConfig = jsyaml.load(yamlContent) || {};
        } else {
            // Basic YAML parsing fallback (limited)
            parsedConfig = basicYamlParse(yamlContent);
        }
    } catch (e) {
        console.warn('YAML parse error:', e);
        // Keep existing parsedConfig on error
    }
}

/**
 * Basic YAML parser for simple configs (fallback when js-yaml not available)
 */
function basicYamlParse(yaml) {
    const result = {};
    const lines = yaml.split('\n');
    const stack = [{ obj: result, indent: -1 }];

    for (const line of lines) {
        // Skip empty lines and comments
        if (!line.trim() || line.trim().startsWith('#')) continue;

        const indent = line.search(/\S/);
        const content = line.trim();

        // Pop stack to correct level
        while (stack.length > 1 && stack[stack.length - 1].indent >= indent) {
            stack.pop();
        }

        const parent = stack[stack.length - 1].obj;

        // Check for key: value
        const colonIndex = content.indexOf(':');
        if (colonIndex > 0) {
            const key = content.substring(0, colonIndex).trim();
            const value = content.substring(colonIndex + 1).trim();

            if (value === '' || value === '|' || value === '>') {
                // Nested object or multiline
                parent[key] = {};
                stack.push({ obj: parent[key], indent: indent });
            } else if (value === '[]') {
                parent[key] = [];
            } else if (value.startsWith('[') && value.endsWith(']')) {
                // Inline array
                parent[key] = value.slice(1, -1).split(',').map(s => s.trim().replace(/['"]/g, ''));
            } else if (value === 'true') {
                parent[key] = true;
            } else if (value === 'false') {
                parent[key] = false;
            } else if (!isNaN(value) && value !== '') {
                parent[key] = Number(value);
            } else {
                parent[key] = value.replace(/^['"]|['"]$/g, '');
            }
        } else if (content.startsWith('- ')) {
            // Array item
            const arrKey = Object.keys(parent).pop();
            if (arrKey && !Array.isArray(parent[arrKey])) {
                parent[arrKey] = [];
            }
            if (arrKey) {
                const itemValue = content.substring(2).trim();
                if (itemValue.includes(':')) {
                    // Object in array
                    const itemObj = {};
                    const [k, v] = itemValue.split(':').map(s => s.trim());
                    itemObj[k] = v.replace(/^['"]|['"]$/g, '');
                    parent[arrKey].push(itemObj);
                } else {
                    parent[arrKey].push(itemValue.replace(/^['"]|['"]$/g, ''));
                }
            }
        }
    }

    return result;
}

/**
 * Get nested value from object using dot notation path
 */
function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
        return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
}

/**
 * Set nested value in object using dot notation path
 */
function setNestedValue(obj, path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    const parent = keys.reduce((current, key) => {
        if (current[key] === undefined) {
            current[key] = {};
        }
        return current[key];
    }, obj);

    if (value === '' || value === undefined || value === null) {
        delete parent[lastKey];
    } else {
        parent[lastKey] = value;
    }
}

/**
 * Sync YAML editor content to form fields
 */
function syncYamlToForms() {
    if (isSyncing) return;
    isSyncing = true;

    try {
        parseYamlToConfig();

        const formFields = document.querySelectorAll('[data-config-path]');
        formFields.forEach(field => {
            const path = field.dataset.configPath;
            const value = getNestedValue(parsedConfig, path);

            if (field.type === 'checkbox') {
                field.checked = value === true;
            } else if (field.tagName === 'SELECT') {
                field.value = value !== undefined ? String(value) : '';
            } else if (field.type === 'number' || field.type === 'range') {
                field.value = value !== undefined ? value : field.defaultValue || '';
                // Update range slider display
                const valueDisplay = document.getElementById(`${field.id}-value`);
                if (valueDisplay) {
                    valueDisplay.textContent = field.value;
                }
            } else {
                // Text, password, textarea
                if (Array.isArray(value)) {
                    field.value = value.join(', ');
                } else {
                    field.value = value !== undefined ? String(value) : '';
                }
            }
        });

        // Update run order list
        updateRunOrderFromConfig();

        // Update service status badges
        updateServiceStatuses();

    } finally {
        isSyncing = false;
    }
}

/**
 * Sync form fields to YAML editor content
 */
function syncFormsToYaml() {
    if (isSyncing) return;
    isSyncing = true;

    try {
        parseYamlToConfig();

        const formFields = document.querySelectorAll('[data-config-path]');
        formFields.forEach(field => {
            const path = field.dataset.configPath;
            let value;

            if (field.type === 'checkbox') {
                value = field.checked;
            } else if (field.type === 'number' || field.type === 'range') {
                value = field.value !== '' ? Number(field.value) : undefined;
            } else {
                value = field.value.trim();
                // Convert comma-separated values to arrays for certain fields
                if (value && (path.includes('ignore_ids') || path.includes('exclude_users') ||
                    path.includes('sync_to_users') || path.includes('tag'))) {
                    value = value.split(',').map(s => s.trim()).filter(s => s);
                }
            }

            setNestedValue(parsedConfig, path, value);
        });

        // Get run order from sortable list
        const runOrderList = document.getElementById('settings-run-order');
        if (runOrderList) {
            const runOrder = Array.from(runOrderList.querySelectorAll('li'))
                .map(li => li.dataset.value);
            setNestedValue(parsedConfig, 'settings.run_order', runOrder);
        }

        // Clean up empty sections
        cleanEmptySections(parsedConfig);

        // Convert back to YAML
        const yamlContent = configToYaml(parsedConfig);
        elements.configEditor.value = yamlContent;

        // Update service status badges
        updateServiceStatuses();

    } finally {
        isSyncing = false;
    }
}

/**
 * Remove empty objects from config
 */
function cleanEmptySections(obj) {
    Object.keys(obj).forEach(key => {
        if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
            cleanEmptySections(obj[key]);
            if (Object.keys(obj[key]).length === 0) {
                delete obj[key];
            }
        }
    });
}

/**
 * Convert config object to YAML string
 */
function configToYaml(config, indent = 0) {
    let yaml = '';
    const spaces = '  '.repeat(indent);

    // Define preferred section order
    const sectionOrder = [
        'plex', 'tmdb', 'libraries', 'playlist_files', 'settings',
        'radarr', 'sonarr', 'tautulli', 'mdblist', 'omdb',
        'trakt', 'mal', 'anidb', 'github',
        'webhooks', 'notifiarr', 'gotify', 'ntfy'
    ];

    // Sort keys by preferred order, then alphabetically for unknown keys
    const sortedKeys = Object.keys(config).sort((a, b) => {
        const aIndex = sectionOrder.indexOf(a);
        const bIndex = sectionOrder.indexOf(b);
        if (aIndex === -1 && bIndex === -1) return a.localeCompare(b);
        if (aIndex === -1) return 1;
        if (bIndex === -1) return -1;
        return aIndex - bIndex;
    });

    for (const key of sortedKeys) {
        const value = config[key];

        if (value === undefined || value === null) continue;

        if (Array.isArray(value)) {
            yaml += `${spaces}${key}:\n`;
            value.forEach(item => {
                if (typeof item === 'object' && item !== null) {
                    // Object in array (like collection_files with file/template_variables)
                    const keys = Object.keys(item);
                    const firstKey = keys[0];
                    yaml += `${spaces}  - ${firstKey}: ${formatYamlValue(item[firstKey])}\n`;
                    keys.slice(1).forEach(subKey => {
                        const subValue = item[subKey];
                        if (typeof subValue === 'object' && subValue !== null && !Array.isArray(subValue)) {
                            // Nested object (like template_variables)
                            yaml += `${spaces}    ${subKey}:\n`;
                            Object.keys(subValue).forEach(nestedKey => {
                                yaml += `${spaces}      ${nestedKey}: ${formatYamlValue(subValue[nestedKey])}\n`;
                            });
                        } else if (Array.isArray(subValue)) {
                            yaml += `${spaces}    ${subKey}:\n`;
                            subValue.forEach(arrItem => {
                                yaml += `${spaces}      - ${formatYamlValue(arrItem)}\n`;
                            });
                        } else {
                            yaml += `${spaces}    ${subKey}: ${formatYamlValue(subValue)}\n`;
                        }
                    });
                } else {
                    yaml += `${spaces}  - ${formatYamlValue(item)}\n`;
                }
            });
        } else if (typeof value === 'object') {
            yaml += `${spaces}${key}:\n`;
            yaml += configToYaml(value, indent + 1);
        } else {
            yaml += `${spaces}${key}: ${formatYamlValue(value)}\n`;
        }
    }

    return yaml;
}

/**
 * Format a value for YAML output
 */
function formatYamlValue(value) {
    if (typeof value === 'boolean') {
        return value ? 'true' : 'false';
    } else if (typeof value === 'number') {
        return String(value);
    } else if (typeof value === 'string') {
        // Quote strings that need it
        if (value.includes(':') || value.includes('#') || value.includes('\n') ||
            value.startsWith(' ') || value.endsWith(' ') ||
            /^[0-9]/.test(value) && isNaN(value)) {
            return `"${value.replace(/"/g, '\\"')}"`;
        }
        return value || '""';
    }
    return String(value);
}

/**
 * Update run order list from config
 */
function updateRunOrderFromConfig() {
    const list = document.getElementById('settings-run-order');
    if (!list) return;

    const configOrder = getNestedValue(parsedConfig, 'settings.run_order');
    if (!Array.isArray(configOrder) || configOrder.length === 0) return;

    const items = Array.from(list.querySelectorAll('li'));
    const itemMap = {};
    items.forEach(item => {
        itemMap[item.dataset.value] = item;
    });

    // Reorder items according to config
    list.innerHTML = '';
    configOrder.forEach(value => {
        if (itemMap[value]) {
            list.appendChild(itemMap[value]);
        }
    });

    // Add any items not in config at the end
    items.forEach(item => {
        if (!configOrder.includes(item.dataset.value)) {
            list.appendChild(item);
        }
    });
}

/**
 * Update service status badges based on config
 */
function updateServiceStatuses() {
    const services = [
        { id: 'radarr', required: ['url', 'token'] },
        { id: 'sonarr', required: ['url', 'token'] },
        { id: 'tautulli', required: ['url', 'apikey'] },
        { id: 'mdblist', required: ['apikey'] },
        { id: 'omdb', required: ['apikey'] },
        { id: 'trakt', required: ['client_id', 'client_secret'] },
        { id: 'mal', required: ['client_id', 'client_secret'] },
        { id: 'anidb', required: ['client', 'version'] },
        { id: 'github', required: ['token'] },
        { id: 'notifiarr', required: ['apikey'] },
        { id: 'gotify', required: ['url', 'token'] },
        { id: 'ntfy', required: ['url', 'topic'] }
    ];

    services.forEach(service => {
        const statusEl = document.getElementById(`${service.id}-status`);
        if (!statusEl) return;

        const serviceConfig = parsedConfig[service.id] || {};
        const isConfigured = service.required.every(key =>
            serviceConfig[key] && String(serviceConfig[key]).trim() !== ''
        );

        statusEl.textContent = isConfigured ? 'Configured' : 'Not configured';
        statusEl.classList.toggle('configured', isConfigured);
    });
}

/**
 * Render libraries from config into the accordion
 */
function renderLibrariesFromConfig() {
    const container = document.getElementById('libraries-accordion');
    if (!container) return;

    parseYamlToConfig();
    const libraries = parsedConfig.libraries || {};

    if (Object.keys(libraries).length === 0) {
        container.innerHTML = '<p class="placeholder-text">No libraries configured. Click "Add Library" or "Refresh from Plex" to get started.</p>';
        return;
    }

    container.innerHTML = Object.entries(libraries).map(([name, config]) => {
        const collectionFiles = config?.collection_files || [];
        const overlayFiles = config?.overlay_files || [];
        const metadataFiles = config?.metadata_files || [];
        const operations = config?.operations || {};
        const schedule = config?.schedule || '';
        const scheduleOverlays = config?.schedule_overlays || '';
        const reportPath = config?.report_path || '';
        const hasOperations = Object.keys(operations).length > 0;

        // Determine library icon based on name
        const libraryIcon = getLibraryIcon(name);

        // Build badges
        const badges = [];
        if (collectionFiles.length > 0) badges.push(`<span class="library-badge collections">📁 ${collectionFiles.length} collections</span>`);
        if (overlayFiles.length > 0) badges.push(`<span class="library-badge overlays">🏷️ ${overlayFiles.length} overlays</span>`);
        if (metadataFiles.length > 0) badges.push(`<span class="library-badge metadata">📝 ${metadataFiles.length} metadata</span>`);
        if (hasOperations) badges.push(`<span class="library-badge operations">⚙️ operations</span>`);

        return `
            <div class="library-item" data-library="${name}">
                <div class="library-item-header" onclick="toggleLibraryItem(this.parentElement)">
                    <div class="library-item-header-left">
                        <span class="library-icon">${libraryIcon}</span>
                        <div class="library-info">
                            <span class="library-name">${name}</span>
                            <div class="library-stats">
                                ${schedule ? `<span class="library-stat"><span class="library-stat-icon">📅</span> ${schedule}</span>` : ''}
                                ${reportPath ? `<span class="library-stat"><span class="library-stat-icon">📊</span> reports enabled</span>` : ''}
                            </div>
                        </div>
                    </div>
                    <div class="library-badges">
                        ${badges.join('')}
                    </div>
                    <button class="library-item-expand">▼</button>
                </div>
                <div class="library-item-content">
                    <!-- Library Tabs -->
                    <div class="library-tabs">
                        <button class="library-tab active" onclick="switchLibraryTab(this, '${name}', 'files')">
                            <span class="library-tab-icon">📁</span> Files
                        </button>
                        <button class="library-tab" onclick="switchLibraryTab(this, '${name}', 'operations')">
                            <span class="library-tab-icon">⚙️</span> Operations
                        </button>
                        <button class="library-tab" onclick="switchLibraryTab(this, '${name}', 'settings')">
                            <span class="library-tab-icon">🔧</span> Settings
                        </button>
                    </div>

                    <!-- Files Tab Panel -->
                    <div class="library-tab-panel active" data-panel="${name}-files">
                        <div class="file-list-section">
                            <h5>📁 Collection Files</h5>
                            <div class="file-list">
                                ${renderFileList(collectionFiles, 'collection', name)}
                            </div>
                            <button class="add-file-btn" onclick="addFileToLibrary('${name}', 'collection_files')">+ Add Collection File</button>
                        </div>
                        <div class="file-list-section">
                            <h5>🏷️ Overlay Files</h5>
                            <div class="file-list">
                                ${renderFileList(overlayFiles, 'overlay', name)}
                            </div>
                            <button class="add-file-btn" onclick="addFileToLibrary('${name}', 'overlay_files')">+ Add Overlay File</button>
                        </div>
                        <div class="file-list-section">
                            <h5>📝 Metadata Files</h5>
                            <div class="file-list">
                                ${renderFileList(metadataFiles, 'metadata', name)}
                            </div>
                            <button class="add-file-btn" onclick="addFileToLibrary('${name}', 'metadata_files')">+ Add Metadata File</button>
                        </div>
                        ${config?.template_variables ? `
                        <div class="template-vars-section">
                            <h5>📋 Template Variables</h5>
                            <p class="field-help" style="margin-bottom: 8px;">JSON object passed to all templates in this library</p>
                            <textarea class="template-vars-editor"
                                data-library="${name}"
                                onchange="updateLibraryTemplateVars('${name}', this.value)"
                            >${JSON.stringify(config.template_variables, null, 2)}</textarea>
                        </div>
                        ` : ''}
                    </div>

                    <!-- Operations Tab Panel -->
                    <div class="library-tab-panel" data-panel="${name}-operations">
                        <p class="field-help info" style="margin-bottom: 12px;">Operations are batch actions performed on all items in the library. <a href="https://kometa.wiki/en/latest/config/operations/" target="_blank" class="inline-link">Learn more ↗</a></p>
                        ${hasOperations ? `
                        <div class="operations-list">
                            ${renderOperationsList(operations)}
                        </div>
                        ` : '<p class="placeholder-text" style="font-size: 12px;">No operations configured for this library.</p>'}
                        <div class="library-settings-grid" style="margin-top: 16px;">
                            <div class="library-setting-item">
                                <label>Schedule</label>
                                <input type="text" value="${schedule}" placeholder="daily" onchange="updateLibraryAttribute('${name}', 'schedule', this.value)">
                                <span class="field-help">e.g., daily, weekly(monday), monthly(1)</span>
                            </div>
                            <div class="library-setting-item">
                                <label>Schedule Overlays</label>
                                <input type="text" value="${scheduleOverlays}" placeholder="daily" onchange="updateLibraryAttribute('${name}', 'schedule_overlays', this.value)">
                                <span class="field-help">Separate schedule for overlay processing</span>
                            </div>
                            <div class="library-setting-item">
                                <label>Report Path</label>
                                <input type="text" value="${reportPath}" placeholder="config/reports/library.yml" onchange="updateLibraryAttribute('${name}', 'report_path', this.value)">
                                <span class="field-help">Path to save library report</span>
                            </div>
                        </div>
                    </div>

                    <!-- Settings Tab Panel -->
                    <div class="library-tab-panel" data-panel="${name}-settings">
                        <p class="field-help info" style="margin-bottom: 12px;">Override global settings for this library only. Leave blank to use global values.</p>
                        <div class="library-settings-grid">
                            ${renderLibrarySettingsOverrides(name, config?.settings || {})}
                        </div>
                        <div class="checkbox-with-desc" style="margin-top: 16px;">
                            <label class="checkbox-label">
                                <input type="checkbox" ${config?.remove_overlays ? 'checked' : ''} onchange="updateLibraryAttribute('${name}', 'remove_overlays', this.checked)">
                                Remove Overlays
                            </label>
                            <span class="checkbox-desc">Remove all overlays from this library (one-time operation)</span>
                        </div>
                        <div class="checkbox-with-desc" style="margin-top: 8px;">
                            <label class="checkbox-label">
                                <input type="checkbox" ${config?.reapply_overlays ? 'checked' : ''} onchange="updateLibraryAttribute('${name}', 'reapply_overlays', this.checked)">
                                Reapply Overlays
                            </label>
                            <span class="checkbox-desc">Reapply overlays to all items (useful after changes)</span>
                        </div>
                        <div class="library-setting-item" style="margin-top: 12px;">
                            <label>Reset Overlays</label>
                            <select onchange="updateLibraryAttribute('${name}', 'reset_overlays', this.value || null)">
                                <option value="">-- Don't reset --</option>
                                <option value="plex" ${config?.reset_overlays === 'plex' ? 'selected' : ''}>Plex (use current Plex images)</option>
                                <option value="tmdb" ${config?.reset_overlays === 'tmdb' ? 'selected' : ''}>TMDb (fetch fresh from TMDb)</option>
                            </select>
                            <span class="field-help">Reset base images before applying overlays</span>
                        </div>
                    </div>

                    <!-- Library Actions -->
                    <div class="library-actions">
                        <div class="library-quick-actions">
                            <button class="library-quick-action" onclick="addFileToLibrary('${name}', 'collection_files')">+ Collection</button>
                            <button class="library-quick-action" onclick="addFileToLibrary('${name}', 'overlay_files')">+ Overlay</button>
                        </div>
                        <button class="btn btn-danger" onclick="removeLibrary('${name}')">Remove Library</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Get appropriate icon for library based on name
 */
function getLibraryIcon(name) {
    const nameLower = name.toLowerCase();
    if (nameLower.includes('movie') || nameLower.includes('film')) return '🎬';
    if (nameLower.includes('tv') || nameLower.includes('show') || nameLower.includes('series')) return '📺';
    if (nameLower.includes('anime') || nameLower.includes('animation')) return '🎌';
    if (nameLower.includes('music') || nameLower.includes('audio')) return '🎵';
    if (nameLower.includes('documentary') || nameLower.includes('doc')) return '🎥';
    if (nameLower.includes('kids') || nameLower.includes('children') || nameLower.includes('family')) return '👶';
    return '📚';
}

/**
 * Render operations list
 */
function renderOperationsList(operations) {
    return Object.entries(operations).map(([key, value]) => {
        const displayValue = typeof value === 'boolean' ? (value ? '✓' : '✗') : value;
        return `<span class="operation-tag">${key}<span class="op-value">: ${displayValue}</span></span>`;
    }).join('');
}

/**
 * Render library settings overrides
 */
function renderLibrarySettingsOverrides(libraryName, settings) {
    const commonSettings = [
        { key: 'asset_directory', label: 'Asset Directory', type: 'text' },
        { key: 'sync_mode', label: 'Sync Mode', type: 'select', options: ['', 'append', 'sync'] },
        { key: 'minimum_items', label: 'Minimum Items', type: 'number' },
        { key: 'delete_below_minimum', label: 'Delete Below Minimum', type: 'checkbox' }
    ];

    return commonSettings.map(setting => {
        const value = settings[setting.key] || '';
        if (setting.type === 'checkbox') {
            return `
                <div class="library-setting-item">
                    <label class="checkbox-label">
                        <input type="checkbox" ${value ? 'checked' : ''} onchange="updateLibrarySetting('${libraryName}', '${setting.key}', this.checked)">
                        ${setting.label}
                    </label>
                </div>
            `;
        } else if (setting.type === 'select') {
            return `
                <div class="library-setting-item">
                    <label>${setting.label}</label>
                    <select onchange="updateLibrarySetting('${libraryName}', '${setting.key}', this.value || null)">
                        ${setting.options.map(opt => `<option value="${opt}" ${value === opt ? 'selected' : ''}>${opt || '-- Use global --'}</option>`).join('')}
                    </select>
                </div>
            `;
        } else {
            return `
                <div class="library-setting-item">
                    <label>${setting.label}</label>
                    <input type="${setting.type}" value="${value}" placeholder="Use global" onchange="updateLibrarySetting('${libraryName}', '${setting.key}', this.value || null)">
                </div>
            `;
        }
    }).join('');
}

/**
 * Switch between library tabs
 */
function switchLibraryTab(button, libraryName, tabName) {
    const libraryItem = button.closest('.library-item');

    // Update tab buttons
    libraryItem.querySelectorAll('.library-tab').forEach(tab => tab.classList.remove('active'));
    button.classList.add('active');

    // Update tab panels
    libraryItem.querySelectorAll('.library-tab-panel').forEach(panel => panel.classList.remove('active'));
    const targetPanel = libraryItem.querySelector(`[data-panel="${libraryName}-${tabName}"]`);
    if (targetPanel) targetPanel.classList.add('active');
}

/**
 * Update a library attribute
 */
function updateLibraryAttribute(libraryName, attribute, value) {
    if (!parsedConfig.libraries?.[libraryName]) return;

    if (value === null || value === '' || value === false) {
        delete parsedConfig.libraries[libraryName][attribute];
    } else {
        parsedConfig.libraries[libraryName][attribute] = value;
    }

    syncFormsToYaml();
}

/**
 * Update a library setting override
 */
function updateLibrarySetting(libraryName, settingKey, value) {
    if (!parsedConfig.libraries?.[libraryName]) return;

    if (!parsedConfig.libraries[libraryName].settings) {
        parsedConfig.libraries[libraryName].settings = {};
    }

    if (value === null || value === '') {
        delete parsedConfig.libraries[libraryName].settings[settingKey];
        // Clean up empty settings object
        if (Object.keys(parsedConfig.libraries[libraryName].settings).length === 0) {
            delete parsedConfig.libraries[libraryName].settings;
        }
    } else {
        parsedConfig.libraries[libraryName].settings[settingKey] = value;
    }

    syncFormsToYaml();
}

/**
 * Render file list items
 */
// Descriptions for default Kometa collection files
const defaultCollectionDescriptions = {
    'basic': 'Newly Released, New Episodes, and fundamental chart-based groupings',
    'tmdb': 'Popular, trending, and airing content from The Movie Database',
    'imdb': 'IMDb\'s top-rated and popular lists (Top 250, Popular, Lowest Rated)',
    'trakt': 'Trakt\'s trending and popular content rankings',
    'tautulli': 'Your Plex server\'s most-watched and popular items',
    'anilist': 'Anime-focused charts and seasonal rankings from AniList',
    'myanimelist': 'Anime popularity and top-rated series from MyAnimeList',
    'letterboxd': 'Film enthusiast rankings and curated lists from Letterboxd',
    'genre': 'Organizes items by categories (Action, Drama, Sci-Fi, etc.)',
    'franchise': 'Groups related film/show series together (Star Wars, MCU, etc.)',
    'universe': 'Collections for shared fictional universes (Marvel, DC, etc.)',
    'based': '"Based on a Book", "Based on a True Story" and similar groupings',
    'actor': 'Collections organized by popular cast members',
    'director': 'Film directors and their complete works',
    'studio': 'Production companies and studios',
    'network': 'Television networks (NBC, HBO, etc.) - shows only',
    'streaming': 'Streaming services (Netflix, Disney+, etc.)',
    'seasonal': 'Holiday and seasonal themes (Christmas, Halloween, etc.)',
    'decade': 'Organized by decades (80s, 90s, 2000s, 2010s, etc.)',
    'year': 'Annual "Best of" and yearly release collections',
    'content_rating_us': 'US content ratings (G, PG, PG-13, R, NC-17)',
    'content_rating_uk': 'UK content ratings (U, PG, 12, 15, 18)',
    'content_rating_de': 'German content ratings (FSK 0, 6, 12, 16, 18)',
    'award': 'Award-winning films and shows (Oscar, Emmy, etc.)',
    'flixpatrol': 'Top streaming charts from FlixPatrol',
    'other_chart': 'Miscellaneous chart collections',
    'separator': 'Visual separators between collection groups',
    'collectionless': 'Items not belonging to any collection'
};

// Descriptions for default Kometa overlay files
const defaultOverlayDescriptions = {
    'resolution': 'Displays quality badges (4K, 1080p, 720p, etc.)',
    'audio_codec': 'Shows audio format logos (Dolby Atmos, DTS:X, etc.)',
    'video_format': 'Labels like REMUX, Blu-Ray, HDTV, WEB-DL',
    'ratings': 'Adds IMDb, Rotten Tomatoes, Metacritic rating badges',
    'ribbon': 'Award ribbons (IMDb Top 250, RT Certified Fresh, etc.)',
    'streaming': 'Streaming service availability logos',
    'network': 'TV network logos (HBO, ABC, etc.)',
    'studio': 'Production studio logos',
    'status': 'Show status badges (Airing, Returning, Canceled, Ended)',
    'episode_info': 'Episode numbering on episode posters (S01E01)',
    'mediastinger': 'Indicates after/mid-credit scenes in movies',
    'content_rating_us': 'US content rating badges (G, PG, R, etc.)',
    'content_rating_uk': 'UK content rating badges (U, PG, 12, 15, 18)',
    'content_rating_de': 'German content rating badges (FSK)',
    'content_rating_au': 'Australian content rating badges',
    'content_rating_nz': 'New Zealand content rating badges',
    'commonsense': 'Common Sense Media age ratings (1+ to 18+)',
    'aspect_ratio': 'Video aspect ratio indicators',
    'language_count': 'Multi-audio/subtitle availability indicators',
    'languages': 'Flag-based audio/subtitle language indicators',
    'runtimes': 'Shows runtime duration on posters',
    'versions': 'Indicates multiple versions available',
    'direct_play': 'Labels "Direct Play Only" content',
    'separator': 'Visual separators between overlay groups'
};

// Descriptions for common template variables
const templateVariableDescriptions = {
    // Collection visibility & organization
    'use_separator': 'Show/hide visual separators between collection groups',
    'collection_section': 'Sort order position for this collection group (lower numbers appear first)',
    'collection_mode': 'How the collection appears: "default" (normal), "hide" (hidden in library), "hide_items" (hides items when in collection)',
    'collection_order': 'Sort order of items within collections: "custom", "alpha", "release", etc.',
    'sort_by': 'Sorting method for collection items (e.g., "release.desc", "title.asc", "rating.desc")',
    'minimum_items': 'Minimum number of items required to create the collection',
    'limit': 'Maximum number of items to include in the collection',

    // Visibility settings
    'visible_home': 'Pin collection to server owner\'s home screen',
    'visible_library': 'Show collection in the library tab',
    'visible_shared': 'Make collection visible on shared users\' home screens',
    'visible_home_top': 'Pin collection to the TOP of server owner\'s home screen',
    'visible_library_top': 'Show collection at the TOP of the library tab',
    'visible_shared_top': 'Pin collection to TOP of shared users\' home screens',

    // Sync & scheduling
    'sync_mode': 'How to sync: "sync" (add & remove), "append" (add only)',
    'schedule': 'When to run: "daily", "weekly(monday)", "monthly(1)", "yearly(01/01)", etc.',

    // Arr integration
    'radarr_add_missing': 'Automatically add missing movies to Radarr',
    'radarr_add_missing_popular': 'Add missing items from "Popular" list to Radarr',
    'radarr_add_missing_top': 'Add missing items from "Top" list to Radarr',
    'radarr_add_missing_trending': 'Add missing items from "Trending" list to Radarr',
    'radarr_add_missing_watched': 'Add missing items from "Watched" list to Radarr',
    'radarr_add_missing_lowest': 'Add missing items from "Lowest Rated" list to Radarr',
    'radarr_add_missing_episodes': 'Add missing episodes to Radarr',
    'radarr_add_missing_released': 'Add missing released items to Radarr',
    'sonarr_add_missing': 'Automatically add missing shows to Sonarr',
    'sonarr_add_missing_popular': 'Add missing items from "Popular" list to Sonarr',
    'sonarr_add_missing_top': 'Add missing items from "Top" list to Sonarr',
    'sonarr_add_missing_trending': 'Add missing items from "Trending" list to Sonarr',
    'sonarr_add_missing_watched': 'Add missing items from "Watched" list to Sonarr',

    // Use flags (enable/disable specific collections)
    'use_popular': 'Enable/disable the "Popular" collection',
    'use_top': 'Enable/disable the "Top Rated" collection',
    'use_trending': 'Enable/disable the "Trending" collection',
    'use_watched': 'Enable/disable the "Most Watched" collection',
    'use_lowest': 'Enable/disable the "Lowest Rated" collection',
    'use_released': 'Enable/disable the "Recently Released" collection',
    'use_episodes': 'Enable/disable episode-level collections',
    'use_edition': 'Enable/disable edition overlays (Director\'s Cut, Extended, etc.)',

    // Appearance
    'style': 'Visual style variant: "color" (colorful), "white" (monochrome), "standards" (standard badges)',
    'sep_style': 'Separator style: "orig", "blue", "green", "gray", "purple", "red", etc.',
    'name_format': 'Custom naming format for collections',
    'summary_format': 'Custom summary format for collections',
    'file_poster': 'Path to custom poster image file',
    'file_background': 'Path to custom background/art image file',
    'url_poster': 'URL to custom poster image',
    'url_background': 'URL to custom background image',

    // Overlay positioning
    'horizontal_align': 'Horizontal position: "left", "center", "right"',
    'vertical_align': 'Vertical position: "top", "center", "bottom"',
    'horizontal_offset': 'Pixels to offset horizontally from alignment edge',
    'vertical_offset': 'Pixels to offset vertically from alignment edge',
    'back_color': 'Background color for text overlays (hex or color name)',
    'back_width': 'Width of overlay background',
    'back_height': 'Height of overlay background',
    'font_size': 'Font size for text overlays',
    'font_color': 'Font color for text overlays',

    // Advanced
    'builder_level': 'Level to apply: "movie", "show", "season", "episode"',
    'language': 'Language code for collection names and summaries',
    'placeholder_imdb_id': 'IMDb ID to use for placeholder/separator posters',
    'originals_only': 'Only include original content (not remakes/reboots)',
    'delete_collections_named': 'List of collection names to delete before creating new ones',
    'ignore_ids': 'List of IDs to exclude from the collection',
    'ignore_imdb_ids': 'List of IMDb IDs to exclude',
    'item_radarr_tag': 'Tag to apply in Radarr for items in this collection',
    'item_sonarr_tag': 'Tag to apply in Sonarr for items in this collection'
};

function renderFileList(files, type, libraryName) {
    if (!files || files.length === 0) {
        return '<p class="placeholder-text" style="font-size: 12px; padding: 8px;">No files configured</p>';
    }

    const descriptions = type === 'overlay' ? defaultOverlayDescriptions : defaultCollectionDescriptions;

    return files.map((file, index) => {
        // Handle different file formats
        let displayName, isDefault, hasTemplateVars, templateVars;

        if (typeof file === 'string') {
            displayName = file;
            isDefault = false;
        } else if (file.default) {
            displayName = file.default;
            isDefault = true;
            templateVars = file.template_variables || {};
            hasTemplateVars = Object.keys(templateVars).length > 0;
        } else if (file.file) {
            displayName = file.file;
            isDefault = false;
            templateVars = file.template_variables || {};
            hasTemplateVars = Object.keys(templateVars).length > 0;
        } else {
            displayName = 'Unknown';
            isDefault = false;
        }

        // Get description for default files
        const description = isDefault ? (descriptions[displayName] || 'Kometa default file') : '';
        const varCount = hasTemplateVars ? Object.keys(templateVars).length : 0;
        const fileId = `file-${libraryName}-${type}-${index}`.replace(/[^a-zA-Z0-9-]/g, '_');

        // Render template variables display
        let varsHtml = '';
        if (hasTemplateVars) {
            varsHtml = `
                <div class="file-vars-panel" id="${fileId}-vars" style="display: none;">
                    <div class="file-vars-header">
                        <span>Template Variables</span>
                        <button class="btn-small" onclick="editFileTemplateVars('${libraryName}', '${type}_files', ${index})" title="Edit variables">Edit</button>
                    </div>
                    <div class="file-vars-grid">
                        ${Object.entries(templateVars).map(([key, value]) => {
                            const displayValue = typeof value === 'boolean' ? (value ? '✓ true' : '✗ false') :
                                                 typeof value === 'object' ? JSON.stringify(value) : String(value);
                            const valueClass = typeof value === 'boolean' ? (value ? 'var-true' : 'var-false') : '';
                            const varDescription = getVariableDescription(key);
                            return `
                                <div class="file-var-item" ${varDescription ? `title="${varDescription}"` : ''}>
                                    <span class="var-key">${key}</span>
                                    <span class="var-value ${valueClass}">${displayValue}</span>
                                    ${varDescription ? '<span class="var-help-icon">?</span>' : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }

        return `
            <div class="file-list-item ${isDefault ? 'is-default' : ''} ${hasTemplateVars ? 'has-vars' : ''}" data-file-id="${fileId}">
                <div class="file-item-row">
                    <div class="file-item-main">
                        <span class="file-type ${isDefault ? 'default' : ''}">${isDefault ? 'DEFAULT' : 'FILE'}</span>
                        <div class="file-info">
                            <span class="file-path">${displayName}</span>
                            ${description ? `<span class="file-description">${description}</span>` : ''}
                        </div>
                    </div>
                    <div class="file-item-actions">
                        ${hasTemplateVars ? `<button class="file-vars-badge" onclick="toggleFileVars('${fileId}')" title="Click to view ${varCount} template variables">${varCount} vars ▼</button>` : ''}
                        <button class="btn-remove" onclick="removeFileFromLibrary('${libraryName}', '${type}_files', ${index})" title="Remove this file">×</button>
                    </div>
                </div>
                ${varsHtml}
            </div>
        `;
    }).join('');
}

/**
 * Get description for a template variable
 */
function getVariableDescription(key) {
    // Direct match
    if (templateVariableDescriptions[key]) {
        return templateVariableDescriptions[key];
    }

    // Pattern matching for common prefixes
    if (key.startsWith('use_')) {
        return `Enable/disable the "${key.replace('use_', '').replace(/_/g, ' ')}" feature`;
    }
    if (key.startsWith('radarr_add_missing')) {
        return 'Add missing items to Radarr automatically';
    }
    if (key.startsWith('sonarr_add_missing')) {
        return 'Add missing items to Sonarr automatically';
    }
    if (key.startsWith('visible_')) {
        return 'Control visibility of this collection in Plex';
    }
    if (key.startsWith('collection_')) {
        return 'Collection display/organization setting';
    }

    return null; // No description available
}

/**
 * Toggle template variables panel visibility
 */
function toggleFileVars(fileId) {
    const panel = document.getElementById(`${fileId}-vars`);
    const badge = document.querySelector(`[data-file-id="${fileId}"] .file-vars-badge`);
    if (panel) {
        const isHidden = panel.style.display === 'none';
        panel.style.display = isHidden ? 'block' : 'none';
        if (badge) {
            const varCount = badge.textContent.match(/\d+/)?.[0] || '0';
            badge.innerHTML = `${varCount} vars ${isHidden ? '▲' : '▼'}`;
        }
    }
}

/**
 * Edit template variables for a file
 */
function editFileTemplateVars(libraryName, fileType, fileIndex) {
    const files = parsedConfig.libraries?.[libraryName]?.[fileType];
    if (!files || !files[fileIndex]) return;

    const file = files[fileIndex];
    const currentVars = file.template_variables || {};
    const varsJson = JSON.stringify(currentVars, null, 2);

    // Create a modal for editing
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content template-vars-modal">
            <div class="modal-header">
                <h3>Edit Template Variables</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
            </div>
            <div class="modal-body">
                <p class="field-help" style="margin-bottom: 12px;">
                    Edit the template variables as JSON. These override default values for this file.
                    <a href="https://kometa.wiki/en/latest/config/paths/#template-variables" target="_blank" class="inline-link">Learn more ↗</a>
                </p>
                <textarea id="template-vars-editor" class="template-vars-textarea">${varsJson}</textarea>
                <div id="template-vars-error" class="error-message" style="display: none;"></div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="saveFileTemplateVars('${libraryName}', '${fileType}', ${fileIndex})">Save Changes</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Focus the textarea
    setTimeout(() => document.getElementById('template-vars-editor')?.focus(), 100);
}

/**
 * Save template variables from modal
 */
function saveFileTemplateVars(libraryName, fileType, fileIndex) {
    const textarea = document.getElementById('template-vars-editor');
    const errorDiv = document.getElementById('template-vars-error');
    if (!textarea) return;

    try {
        const newVars = JSON.parse(textarea.value);

        // Update the config
        if (parsedConfig.libraries?.[libraryName]?.[fileType]?.[fileIndex]) {
            parsedConfig.libraries[libraryName][fileType][fileIndex].template_variables = newVars;
        }

        // Sync and refresh
        syncFormsToYaml();
        renderLibrariesFromConfig();

        // Close modal
        document.querySelector('.modal-overlay')?.remove();

    } catch (e) {
        if (errorDiv) {
            errorDiv.textContent = `Invalid JSON: ${e.message}`;
            errorDiv.style.display = 'block';
        }
    }
}

/**
 * Toggle library item expansion
 */
function toggleLibraryItem(item) {
    item.classList.toggle('expanded');
}

/**
 * Add file to library
 */
function addFileToLibrary(libraryName, fileType) {
    const filePath = prompt(`Enter ${fileType.replace('_files', '')} file path or "default:<name>":`);
    if (!filePath) return;

    if (!parsedConfig.libraries) parsedConfig.libraries = {};
    if (!parsedConfig.libraries[libraryName]) parsedConfig.libraries[libraryName] = {};
    if (!parsedConfig.libraries[libraryName][fileType]) parsedConfig.libraries[libraryName][fileType] = [];

    // Check if it's a default or file path
    if (filePath.startsWith('default:') || !filePath.includes('/')) {
        parsedConfig.libraries[libraryName][fileType].push(filePath);
    } else {
        parsedConfig.libraries[libraryName][fileType].push({ file: filePath });
    }

    syncFormsToYaml();
    renderLibrariesFromConfig();
}

/**
 * Remove file from library
 */
function removeFileFromLibrary(libraryName, fileType, index) {
    if (!parsedConfig.libraries?.[libraryName]?.[fileType]) return;

    parsedConfig.libraries[libraryName][fileType].splice(index, 1);

    // Clean up empty arrays
    if (parsedConfig.libraries[libraryName][fileType].length === 0) {
        delete parsedConfig.libraries[libraryName][fileType];
    }

    syncFormsToYaml();
    renderLibrariesFromConfig();
}

/**
 * Remove library
 */
function removeLibrary(libraryName) {
    if (!confirm(`Remove library "${libraryName}" from configuration?`)) return;

    if (parsedConfig.libraries?.[libraryName]) {
        delete parsedConfig.libraries[libraryName];
    }

    syncFormsToYaml();
    renderLibrariesFromConfig();
}

/**
 * Update library template variables
 */
function updateLibraryTemplateVars(libraryName, jsonValue) {
    try {
        const vars = JSON.parse(jsonValue);
        if (parsedConfig.libraries?.[libraryName]) {
            parsedConfig.libraries[libraryName].template_variables = vars;
            syncFormsToYaml();
        }
    } catch (e) {
        console.warn('Invalid JSON for template variables');
    }
}

// ============================================================================
// Connection Testing
// ============================================================================

/**
 * Test Plex connection
 */
async function testPlexConnection() {
    const resultEl = document.getElementById('plex-test-result');
    const url = document.getElementById('plex-url').value;
    const token = document.getElementById('plex-token').value;

    if (!url || !token) {
        resultEl.textContent = 'URL and Token are required';
        resultEl.className = 'test-result error';
        return;
    }

    resultEl.textContent = 'Testing...';
    resultEl.className = 'test-result loading';

    try {
        const result = await api.post('/test/plex', { url, token });
        if (result.success) {
            resultEl.textContent = `✓ Connected to ${result.server_name || 'Plex'}`;
            resultEl.className = 'test-result success';
        } else {
            resultEl.textContent = `✗ ${result.error || 'Connection failed'}`;
            resultEl.className = 'test-result error';
        }
    } catch (error) {
        resultEl.textContent = `✗ ${error.message}`;
        resultEl.className = 'test-result error';
    }
}

/**
 * Test TMDb API key
 */
async function testTmdbConnection() {
    const resultEl = document.getElementById('tmdb-test-result');
    const apikey = document.getElementById('tmdb-apikey').value;

    if (!apikey) {
        resultEl.textContent = 'API Key is required';
        resultEl.className = 'test-result error';
        return;
    }

    resultEl.textContent = 'Testing...';
    resultEl.className = 'test-result loading';

    try {
        const result = await api.post('/test/tmdb', { apikey });
        if (result.success) {
            resultEl.textContent = '✓ API key is valid';
            resultEl.className = 'test-result success';
        } else {
            resultEl.textContent = `✗ ${result.error || 'Invalid API key'}`;
            resultEl.className = 'test-result error';
        }
    } catch (error) {
        resultEl.textContent = `✗ ${error.message}`;
        resultEl.className = 'test-result error';
    }
}

/**
 * Generic service connection test
 */
async function testServiceConnection(serviceName, endpoint, params) {
    const resultEl = document.getElementById(`${serviceName}-test-result`);

    resultEl.textContent = 'Testing...';
    resultEl.className = 'test-result loading';

    try {
        const result = await api.post(`/test/${endpoint}`, params);
        if (result.success) {
            resultEl.textContent = `✓ ${result.message || 'Connection successful'}`;
            resultEl.className = 'test-result success';
        } else {
            resultEl.textContent = `✗ ${result.error || 'Connection failed'}`;
            resultEl.className = 'test-result error';
        }
    } catch (error) {
        resultEl.textContent = `✗ ${error.message}`;
        resultEl.className = 'test-result error';
    }
}

/**
 * Initialize connection test buttons
 */
function initConnectionTestButtons() {
    // Plex
    document.getElementById('btn-test-plex')?.addEventListener('click', testPlexConnection);

    // TMDb
    document.getElementById('btn-test-tmdb')?.addEventListener('click', testTmdbConnection);

    // Radarr
    document.getElementById('btn-test-radarr')?.addEventListener('click', () => {
        testServiceConnection('radarr', 'radarr', {
            url: document.getElementById('radarr-url').value,
            token: document.getElementById('radarr-token').value
        });
    });

    // Sonarr
    document.getElementById('btn-test-sonarr')?.addEventListener('click', () => {
        testServiceConnection('sonarr', 'sonarr', {
            url: document.getElementById('sonarr-url').value,
            token: document.getElementById('sonarr-token').value
        });
    });

    // Tautulli
    document.getElementById('btn-test-tautulli')?.addEventListener('click', () => {
        testServiceConnection('tautulli', 'tautulli', {
            url: document.getElementById('tautulli-url').value,
            apikey: document.getElementById('tautulli-apikey').value
        });
    });

    // MDBList
    document.getElementById('btn-test-mdblist')?.addEventListener('click', () => {
        testServiceConnection('mdblist', 'mdblist', {
            apikey: document.getElementById('mdblist-apikey').value
        });
    });

    // OMDb
    document.getElementById('btn-test-omdb')?.addEventListener('click', () => {
        testServiceConnection('omdb', 'omdb', {
            apikey: document.getElementById('omdb-apikey').value
        });
    });

    // Trakt
    document.getElementById('btn-test-trakt')?.addEventListener('click', () => {
        testServiceConnection('trakt', 'trakt', {
            client_id: document.getElementById('trakt-client-id').value,
            client_secret: document.getElementById('trakt-client-secret').value
        });
    });

    // MAL
    document.getElementById('btn-test-mal')?.addEventListener('click', () => {
        testServiceConnection('mal', 'mal', {
            client_id: document.getElementById('mal-client-id').value
        });
    });

    // AniDB
    document.getElementById('btn-test-anidb')?.addEventListener('click', () => {
        testServiceConnection('anidb', 'anidb', {
            client: document.getElementById('anidb-client').value,
            version: document.getElementById('anidb-version').value
        });
    });

    // GitHub
    document.getElementById('btn-test-github')?.addEventListener('click', () => {
        testServiceConnection('github', 'github', {
            token: document.getElementById('github-token').value
        });
    });

    // Notifiarr
    document.getElementById('btn-test-notifiarr')?.addEventListener('click', () => {
        testServiceConnection('notifiarr', 'notifiarr', {
            apikey: document.getElementById('notifiarr-apikey').value
        });
    });

    // Gotify
    document.getElementById('btn-test-gotify')?.addEventListener('click', () => {
        testServiceConnection('gotify', 'gotify', {
            url: document.getElementById('gotify-url').value,
            token: document.getElementById('gotify-token').value
        });
    });

    // ntfy
    document.getElementById('btn-test-ntfy')?.addEventListener('click', () => {
        testServiceConnection('ntfy', 'ntfy', {
            url: document.getElementById('ntfy-url').value,
            topic: document.getElementById('ntfy-topic').value
        });
    });
}

/**
 * Initialize Add Library button
 */
function initAddLibraryButton() {
    document.getElementById('btn-add-library')?.addEventListener('click', () => {
        const name = prompt('Enter library name (must match Plex library name):');
        if (!name) return;

        if (!parsedConfig.libraries) parsedConfig.libraries = {};
        if (parsedConfig.libraries[name]) {
            alert('Library already exists!');
            return;
        }

        parsedConfig.libraries[name] = {
            collection_files: []
        };

        syncFormsToYaml();
        renderLibrariesFromConfig();
    });

    document.getElementById('btn-refresh-libraries')?.addEventListener('click', async () => {
        try {
            const result = await api.get('/media/libraries');
            const libraries = result.libraries || [];

            if (libraries.length === 0) {
                alert('No libraries found. Make sure Plex is configured and connected.');
                return;
            }

            const existingLibs = Object.keys(parsedConfig.libraries || {});
            const newLibs = libraries.filter(lib => !existingLibs.includes(lib.title));

            if (newLibs.length === 0) {
                alert('All Plex libraries are already configured.');
                return;
            }

            const addLibs = confirm(`Found ${newLibs.length} new libraries:\n${newLibs.map(l => l.title).join('\n')}\n\nAdd them to config?`);
            if (!addLibs) return;

            if (!parsedConfig.libraries) parsedConfig.libraries = {};
            newLibs.forEach(lib => {
                parsedConfig.libraries[lib.title] = {
                    collection_files: []
                };
            });

            syncFormsToYaml();
            renderLibrariesFromConfig();
        } catch (error) {
            alert(`Failed to fetch libraries: ${error.message}`);
        }
    });
}

// Expose library functions to global scope
window.toggleLibraryItem = toggleLibraryItem;
window.addFileToLibrary = addFileToLibrary;
window.removeFileFromLibrary = removeFileFromLibrary;
window.removeLibrary = removeLibrary;
window.updateLibraryTemplateVars = updateLibraryTemplateVars;

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

        // Update live preview with loaded overlays
        if (window.livePreview) {
            window.livePreview.onOverlaysLoaded(state.loadedOverlays);
        }

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
        // Build the image URL - images are served from /overlay-images mount
        const imageUrl = `/overlay-images/${imagePath}.png`;

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
    // Check if Plex is configured
    if (!state.mediaSourceStatus.plex) {
        elements.plexResults.innerHTML = '<p class="placeholder-text">Plex not configured. Add plex credentials to config.yml and restart the server.</p>';
        return;
    }

    const query = elements.plexSearch?.value?.trim();
    if (!query) {
        elements.plexResults.innerHTML = '<p class="placeholder-text">Enter a title to search.</p>';
        return;
    }

    elements.plexResults.innerHTML = '<p class="placeholder-text">Searching...</p>';

    try {
        const result = await api.get(`/media/search?query=${encodeURIComponent(query)}&source=plex`);
        if (result.results && result.results.length > 0) {
            renderMediaResults(result.results, 'plex', elements.plexResults);
        } else {
            elements.plexResults.innerHTML = '<p class="placeholder-text">No results found. Try a different search term.</p>';
        }
    } catch (error) {
        console.error('Plex search error:', error);
        elements.plexResults.innerHTML = `<p class="placeholder-text">Search failed: ${error.message}</p>`;
    }
}

async function searchTmdb() {
    // Check if TMDb is configured
    if (!state.mediaSourceStatus.tmdb) {
        elements.tmdbResults.innerHTML = '<p class="placeholder-text">TMDb not configured. Add tmdb apikey to config.yml and restart the server.</p>';
        return;
    }

    const query = elements.tmdbSearch?.value?.trim();
    if (!query) {
        elements.tmdbResults.innerHTML = '<p class="placeholder-text">Enter a title to search.</p>';
        return;
    }

    const mediaType = elements.tmdbType?.value || 'movie';
    elements.tmdbResults.innerHTML = '<p class="placeholder-text">Searching...</p>';

    try {
        const result = await api.get(`/media/search?query=${encodeURIComponent(query)}&source=tmdb&media_type=${mediaType}`);
        if (result.results && result.results.length > 0) {
            renderMediaResults(result.results, 'tmdb', elements.tmdbResults);
        } else {
            elements.tmdbResults.innerHTML = '<p class="placeholder-text">No results found. Try a different search term.</p>';
        }
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

    // Source options
    elements.sourceOptions.forEach(option => {
        option.addEventListener('click', async () => {
            elements.sourceOptions.forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');

            if (option.dataset.source === 'existing') {
                await loadConfig();
                syncYamlToForms();
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
                syncYamlToForms();
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
                    // Validate the uploaded config and sync to forms
                    validateConfig();
                    syncYamlToForms();
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

    // Initialize config editor subtabs and form sync
    initConfigSubtabs();
    initConnectionTestButtons();
    initAddLibraryButton();

    // Load initial data
    await loadConfig();
    await loadBackups();
    await checkRunStatus();

    // Sync loaded config to forms
    syncYamlToForms();

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

// ============================================================================
// Live Preview Manager - Shows real-time overlay preview on the page
// ============================================================================

const livePreview = {
    // Default media for preview (Dune 2021)
    defaultMedia: {
        tmdb_id: '438631',
        title: 'Dune (2021)',
        media_type: 'movie'
    },

    // Current state
    isLoading: false,
    currentPosterUrl: null,
    selectedOverlays: [],  // User-selected overlays to display
    configuredOverlayTypes: [],  // Overlay types from config.yml
    availableOverlaysByType: {},  // Loaded overlays grouped by type

    // DOM Elements
    elements: {
        poster: null,
        loading: null,
        title: null,
        overlayCount: null,
        overlaysList: null,
        overlaysBadge: null
    },

    init() {
        // Get DOM elements
        this.elements.poster = document.getElementById('live-preview-poster');
        this.elements.loading = document.getElementById('live-preview-loading');
        this.elements.title = document.getElementById('preview-media-title');
        this.elements.overlayCount = document.getElementById('preview-overlay-count');
        this.elements.overlaysList = document.getElementById('active-overlays-list');
        this.elements.overlaysBadge = document.getElementById('active-overlays-badge');

        // Add event listeners for new buttons
        const btnRefresh = document.getElementById('btn-refresh-preview');
        const btnChangePoster = document.getElementById('btn-change-poster');

        if (btnRefresh) {
            btnRefresh.addEventListener('click', () => this.refreshPreview());
        }

        if (btnChangePoster) {
            btnChangePoster.addEventListener('click', () => this.showPosterPicker());
        }

        // Parse config to find configured overlay types
        this.parseConfigOverlays();

        console.log('Live preview initialized');
    },

    /**
     * Parse config.yml to find which overlay types are configured and their template variables
     */
    parseConfigOverlays() {
        const configEditor = document.getElementById('config-editor');
        if (!configEditor) return;

        const content = configEditor.value || '';
        this.configuredOverlayTypes = [];
        this.overlayTemplateVars = {};  // Store template variables per overlay type

        // Find overlay_files section
        const overlayMatch = content.match(/overlay_files:\s*\n([\s\S]*?)(?=\n[a-zA-Z]|\n\s*operations:|$)/);
        if (overlayMatch) {
            const overlaySection = overlayMatch[1];

            // Split into individual overlay entries
            const entries = overlaySection.split(/\n\s*- default:/);

            for (let i = 1; i < entries.length; i++) {
                const entry = entries[i];
                const typeMatch = entry.match(/^\s*(\w+)/);
                if (typeMatch) {
                    const overlayType = typeMatch[1];
                    this.configuredOverlayTypes.push(overlayType);

                    // Extract template_variables for this overlay
                    const varsMatch = entry.match(/template_variables:\s*\n([\s\S]*?)(?=\n\s*- default:|$)/);
                    if (varsMatch) {
                        const varsSection = varsMatch[1];
                        const vars = {};

                        // Parse each variable line
                        const varLines = varsSection.match(/^\s+(\w+):\s*(.+?)(?:\s*#.*)?$/gm);
                        if (varLines) {
                            varLines.forEach(line => {
                                const varMatch = line.match(/^\s+(\w+):\s*(.+?)(?:\s*#.*)?$/);
                                if (varMatch) {
                                    vars[varMatch[1]] = varMatch[2].trim();
                                }
                            });
                        }

                        this.overlayTemplateVars[overlayType] = vars;
                    }
                }
            }
        }

        console.log('Configured overlay types:', this.configuredOverlayTypes);
        console.log('Template variables:', this.overlayTemplateVars);
    },

    /**
     * Load the preview with Dune poster (no overlays by default)
     */
    async loadPreview() {
        if (!this.elements.poster) return;

        this.setLoading(true);

        try {
            // Only include user-selected overlays, not all loaded overlays
            const overlays = this.selectedOverlays || [];

            // Prepare request data
            const requestData = {
                overlays: overlays.map(o => ({
                    name: o.name,
                    type: o.type || 'image',
                    default: o.default || o.image_url,  // Use image_url for rating overlays
                    horizontal_offset: o.horizontal_offset,
                    vertical_offset: o.vertical_offset,
                    horizontal_align: o.horizontal_align,
                    vertical_align: o.vertical_align,
                    back_color: o.back_color,
                    back_width: o.back_width,
                    back_height: o.back_height,
                    back_padding: o.back_padding,
                    back_radius: o.back_radius,
                    font: o.font,
                    font_size: o.font_size,
                    font_color: o.font_color
                })),
                canvas_type: 'portrait',
                template_variables: {},
                poster_source: 'tmdb',
                tmdb_id: this.defaultMedia.tmdb_id,
                media_type: this.defaultMedia.media_type
            };

            const response = await fetch('/api/overlays/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.image) {
                this.showPreviewImage(result.image);
                this.currentPosterUrl = result.image;
            }

            // Update UI with selected overlay info
            this.updateOverlaysList();
            this.updateTitle(this.defaultMedia.title);

        } catch (error) {
            console.error('Failed to load preview:', error);
            this.showError('Failed to load preview');
        } finally {
            this.setLoading(false);
        }
    },

    /**
     * Show the preview image
     */
    showPreviewImage(imageData) {
        if (!this.elements.poster) return;

        // Clear loading indicator
        const loading = this.elements.loading;
        if (loading) loading.classList.add('hidden');

        // Remove existing image if any
        const existingImg = this.elements.poster.querySelector('img.poster-image');
        if (existingImg) existingImg.remove();

        // Create and add new image
        const img = document.createElement('img');
        img.className = 'poster-image';
        img.src = imageData;
        img.alt = 'Overlay Preview';
        this.elements.poster.appendChild(img);
    },

    /**
     * Update the overlays list in the sidebar - shows type selector and selected overlays
     */
    updateOverlaysList() {
        if (!this.elements.overlaysList) return;

        // Build the overlay type selector and selected overlays list
        let html = '';

        // Show configured overlay types from config.yml as buttons
        if (this.configuredOverlayTypes.length > 0) {
            html += '<div class="overlay-type-selector">';
            html += '<p class="selector-label">Add from config:</p>';
            html += '<div class="overlay-type-buttons">';
            this.configuredOverlayTypes.forEach(type => {
                const loaded = this.availableOverlaysByType[type];
                const loadedClass = loaded ? 'loaded' : '';
                html += `<button class="overlay-type-btn ${loadedClass}" onclick="livePreview.showOverlayPicker('${type}')" title="Click to select ${type} overlays">${type}</button>`;
            });
            html += '</div></div>';
        } else {
            html += '<p class="placeholder-text">No overlay types configured. Check your config.yml overlay_files section.</p>';
        }

        // Show selected overlays
        if (this.selectedOverlays.length > 0) {
            html += '<div class="selected-overlays-section">';
            html += '<p class="selector-label">Selected overlays:</p>';
            this.selectedOverlays.forEach((o, idx) => {
                html += `
                    <div class="active-overlay-item">
                        <div class="active-overlay-thumbnail">${this.generateThumbnail(o)}</div>
                        <span class="active-overlay-name" title="${o.name}">${o.name}</span>
                        <button class="overlay-remove-btn" onclick="livePreview.removeOverlay(${idx})" title="Remove">✕</button>
                    </div>
                `;
            });
            html += '</div>';
        }

        this.elements.overlaysList.innerHTML = html;

        // Update badges
        if (this.elements.overlaysBadge) {
            this.elements.overlaysBadge.textContent = this.selectedOverlays.length;
        }

        if (this.elements.overlayCount) {
            this.elements.overlayCount.textContent = `${this.selectedOverlays.length} overlay${this.selectedOverlays.length !== 1 ? 's' : ''} applied`;
        }
    },

    /**
     * Show overlay picker dialog for a specific type
     */
    async showOverlayPicker(overlayType) {
        // Special handling for ratings - show configured rating badges
        if (overlayType === 'ratings') {
            this.showRatingsPickerDialog();
            return;
        }

        // Load overlays for this type if not already loaded
        if (!this.availableOverlaysByType[overlayType]) {
            await this.loadOverlayType(overlayType);
        }

        const overlays = this.availableOverlaysByType[overlayType] || [];
        if (overlays.length === 0) {
            alert(`No overlays found for type: ${overlayType}`);
            return;
        }

        // Create picker dialog
        const existingDialog = document.getElementById('overlay-picker-dialog');
        if (existingDialog) existingDialog.remove();

        const dialog = document.createElement('div');
        dialog.id = 'overlay-picker-dialog';
        dialog.className = 'modal';
        dialog.innerHTML = `
            <div class="modal-content" style="max-width: 600px; max-height: 80vh;">
                <div class="modal-header">
                    <h3>Select ${overlayType} Overlay</h3>
                    <button class="btn btn-icon" onclick="document.getElementById('overlay-picker-dialog').remove()">✕</button>
                </div>
                <div class="modal-body" style="overflow-y: auto; max-height: 60vh; padding: 15px;">
                    <div class="overlay-picker-grid">
                        ${overlays.map((o, idx) => {
                            const isSelected = this.selectedOverlays.some(s => s.name === o.name);
                            return `
                                <div class="overlay-picker-item ${isSelected ? 'selected' : ''}" onclick="livePreview.toggleOverlayFromPicker('${overlayType}', ${idx})">
                                    <div class="picker-thumbnail">${this.generateThumbnail(o)}</div>
                                    <span class="picker-name">${o.name}</span>
                                    ${isSelected ? '<span class="picker-check">✓</span>' : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
                <div class="modal-footer" style="padding: 15px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; gap: 10px;">
                    <button class="btn btn-secondary" onclick="document.getElementById('overlay-picker-dialog').remove()">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    },

    /**
     * Show special picker for ratings overlay with 3 configured badges
     */
    showRatingsPickerDialog() {
        const vars = this.overlayTemplateVars['ratings'] || {};

        // Rating image name to display name mapping
        const ratingImageNames = {
            'rt_tomato': 'Rotten Tomatoes (Critics)',
            'rt_popcorn': 'Rotten Tomatoes (Audience)',
            'imdb': 'IMDb',
            'tmdb': 'TMDb',
            'trakt': 'Trakt',
            'letterboxd': 'Letterboxd',
            'metacritic': 'Metacritic',
            'anidb': 'AniDB',
            'mal': 'MyAnimeList',
            'mdb': 'MDBList',
            'star': 'Star Rating'
        };

        // Get configured ratings from template variables
        const rating1Image = vars['rating1_image'] || 'imdb';
        const rating2Image = vars['rating2_image'] || 'tmdb';
        const rating3Image = vars['rating3_image'] || 'trakt';
        const horizontalPos = vars['horizontal_position'] || 'left';

        // Check if ratings are already selected
        const hasRatings = this.selectedOverlays.some(o => o._isRating);

        const existingDialog = document.getElementById('overlay-picker-dialog');
        if (existingDialog) existingDialog.remove();

        const dialog = document.createElement('div');
        dialog.id = 'overlay-picker-dialog';
        dialog.className = 'modal';
        dialog.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3>Ratings Overlay</h3>
                    <button class="btn btn-icon" onclick="document.getElementById('overlay-picker-dialog').remove()">✕</button>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    <p style="color: var(--text-muted); margin-bottom: 15px;">Your config has 3 rating badges configured:</p>

                    <div class="ratings-config-preview">
                        <div class="rating-badge-preview">
                            <span class="rating-num">1</span>
                            <span class="rating-source">${ratingImageNames[rating1Image] || rating1Image}</span>
                        </div>
                        <div class="rating-badge-preview">
                            <span class="rating-num">2</span>
                            <span class="rating-source">${ratingImageNames[rating2Image] || rating2Image}</span>
                        </div>
                        <div class="rating-badge-preview">
                            <span class="rating-num">3</span>
                            <span class="rating-source">${ratingImageNames[rating3Image] || rating3Image}</span>
                        </div>
                    </div>

                    <p style="color: var(--text-muted); margin-top: 15px; font-size: 12px;">
                        Position: <strong>${horizontalPos}</strong> side, stacked vertically
                    </p>
                </div>
                <div class="modal-footer" style="padding: 15px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; gap: 10px;">
                    <button class="btn btn-secondary" onclick="document.getElementById('overlay-picker-dialog').remove()">Cancel</button>
                    <button class="btn ${hasRatings ? 'btn-danger' : 'btn-primary'}" onclick="livePreview.toggleRatingsOverlay()">
                        ${hasRatings ? 'Remove Ratings' : 'Add All 3 Ratings'}
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    },

    /**
     * Toggle all 3 rating overlays at once
     */
    toggleRatingsOverlay() {
        const hasRatings = this.selectedOverlays.some(o => o._isRating);

        if (hasRatings) {
            // Remove all rating overlays
            this.selectedOverlays = this.selectedOverlays.filter(o => !o._isRating);
        } else {
            // Add all 3 rating overlays based on config
            const vars = this.overlayTemplateVars['ratings'] || {};
            const horizontalPos = vars['horizontal_position'] || 'left';
            const horizontalAlign = horizontalPos === 'right' ? 'right' : 'left';

            // Vertical offsets for stacking (based on Kometa's default values)
            const verticalOffsets = [30, 235, 440];

            const ratingImages = [
                vars['rating1_image'] || 'imdb',
                vars['rating2_image'] || 'tmdb',
                vars['rating3_image'] || 'trakt'
            ];

            ratingImages.forEach((img, idx) => {
                const ratingImageFile = this.getRatingImageFile(img);
                this.selectedOverlays.push({
                    name: `Rating ${idx + 1} (${img})`,
                    _isRating: true,
                    _ratingNum: idx + 1,
                    type: 'image',
                    horizontal_align: horizontalAlign,
                    vertical_align: 'center',
                    horizontal_offset: 30,
                    vertical_offset: verticalOffsets[idx],
                    // Use 'default' with the relative path that backend expects
                    default: `rating/${ratingImageFile}`,
                    image_url: `/overlay-images/rating/${ratingImageFile}.png`
                });
            });
        }

        document.getElementById('overlay-picker-dialog')?.remove();
        this.updateOverlaysList();
        this.loadPreview();
    },

    /**
     * Get the rating image filename
     */
    getRatingImageFile(ratingImage) {
        const imageMap = {
            'rt_tomato': 'RT-Crit-Fresh',
            'rt_popcorn': 'RT-Aud-Fresh',
            'imdb': 'IMDb',
            'tmdb': 'TMDb',
            'trakt': 'Trakt',
            'letterboxd': 'Letterboxd',
            'metacritic': 'Metacritic',
            'anidb': 'AniDB',
            'mal': 'MAL',
            'mdb': 'MDBList',
            'star': 'Star'
        };
        return imageMap[ratingImage] || ratingImage;
    },

    /**
     * Load overlays for a specific type from the default overlay files
     */
    async loadOverlayType(overlayType) {
        try {
            const filePath = `/kometa/defaults/overlays/${overlayType}.yml`;
            const response = await fetch(`/api/overlays/parse?file_path=${encodeURIComponent(filePath)}`);
            const result = await response.json();
            this.availableOverlaysByType[overlayType] = result.overlays || [];
            this.updateOverlaysList();
        } catch (error) {
            console.error(`Failed to load overlay type ${overlayType}:`, error);
            this.availableOverlaysByType[overlayType] = [];
        }
    },

    /**
     * Toggle an overlay from the picker dialog
     */
    toggleOverlayFromPicker(overlayType, index) {
        const overlay = this.availableOverlaysByType[overlayType]?.[index];
        if (!overlay) return;

        const existingIdx = this.selectedOverlays.findIndex(o => o.name === overlay.name);
        if (existingIdx >= 0) {
            // Remove it
            this.selectedOverlays.splice(existingIdx, 1);
        } else {
            // Add it
            this.selectedOverlays.push({ ...overlay });
        }

        // Refresh the picker dialog to show updated selection
        this.showOverlayPicker(overlayType);

        // Update the sidebar and preview
        this.updateOverlaysList();
        this.loadPreview();
    },

    /**
     * Remove an overlay from selection
     */
    removeOverlay(index) {
        this.selectedOverlays.splice(index, 1);
        this.updateOverlaysList();
        this.loadPreview();
    },

    /**
     * Generate a tiny thumbnail for an overlay
     */
    generateThumbnail(overlay) {
        if (overlay.image_url) {
            return `<img src="${overlay.image_url}" style="width:100%;height:100%;object-fit:contain;">`;
        }

        // Generate text-based thumbnail
        const initial = (overlay.name || 'O').charAt(0).toUpperCase();
        return `<span>${initial}</span>`;
    },

    /**
     * Update the media title display
     */
    updateTitle(title) {
        if (this.elements.title) {
            this.elements.title.textContent = title;
        }
    },

    /**
     * Set loading state
     */
    setLoading(loading) {
        this.isLoading = loading;

        if (this.elements.loading) {
            if (loading) {
                this.elements.loading.classList.remove('hidden');
            } else {
                this.elements.loading.classList.add('hidden');
            }
        }
    },

    /**
     * Show error message in preview area
     */
    showError(message) {
        if (!this.elements.poster) return;

        this.elements.poster.innerHTML = `
            <div class="live-preview-error">
                <span>⚠️</span>
                <p>${message}</p>
            </div>
        `;
    },

    /**
     * Refresh the preview with current state
     */
    async refreshPreview() {
        this.parseConfigOverlays();  // Re-parse config in case it changed
        await this.loadPreview();
    },

    /**
     * Show poster picker (opens advanced section or a modal)
     */
    showPosterPicker() {
        // Open the advanced section and scroll to poster source
        const advancedDetails = document.getElementById('overlay-advanced-details');
        if (advancedDetails) {
            advancedDetails.open = true;

            // Scroll to poster source section
            const posterSection = document.querySelector('.poster-source-section');
            if (posterSection) {
                posterSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    },

    /**
     * Called when overlays are loaded from a config file (legacy - no longer auto-loads all)
     */
    onOverlaysLoaded(overlays) {
        // Don't auto-load all overlays anymore - just update the UI
        this.updateOverlaysList();
    }
};

// Initialize live preview on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    livePreview.init();
});

// Make it globally accessible
window.livePreview = livePreview;

// ============================================================================
// Visual Overlay Editor
// ============================================================================

const visualEditor = {
    // State
    isOpen: false,
    zoom: 1,
    snapToGrid: true,
    gridSize: 25,
    canvasWidth: 1000,
    canvasHeight: 1500,
    displayScale: 0.5,  // Display scale (canvas shows at 500x750 by default)
    selectedOverlayIndex: null,
    overlays: [],  // Working copy of overlays for editing
    undoStack: [],
    redoStack: [],
    isDragging: false,
    isResizing: false,
    dragStart: { x: 0, y: 0 },
    dragOffset: { x: 0, y: 0 },
    resizeHandle: null,
    resizeStart: { x: 0, y: 0, width: 0, height: 0 },

    // Elements (cached after init)
    elements: null,

    init() {
        this.cacheElements();
        this.bindEvents();
    },

    cacheElements() {
        this.elements = {
            modal: document.getElementById('visual-editor-modal'),
            canvas: document.getElementById('visual-canvas'),
            canvasPoster: document.getElementById('canvas-poster'),
            canvasWrapper: document.getElementById('visual-canvas-wrapper'),
            canvasGrid: document.getElementById('canvas-grid'),
            layersList: document.getElementById('layers-list'),
            propertiesContent: document.getElementById('properties-content'),
            yamlEditor: document.getElementById('yaml-editor'),
            yamlStatus: document.getElementById('yaml-status'),
            mousePosition: document.getElementById('mouse-position'),
            selectedOverlayInfo: document.getElementById('selected-overlay-info'),
            zoomLevel: document.getElementById('zoom-level'),
            canvasDimensions: document.getElementById('canvas-dimensions'),
            snapToGrid: document.getElementById('snap-to-grid'),
            gridSize: document.getElementById('grid-size'),
            addOverlayDialog: document.getElementById('add-overlay-dialog')
        };
    },

    bindEvents() {
        // Open/close editor
        const btnOpen = document.getElementById('btn-open-visual-editor');
        const btnClose = document.getElementById('btn-close-visual-editor');
        if (btnOpen) btnOpen.addEventListener('click', () => this.open());
        if (btnClose) btnClose.addEventListener('click', () => this.close());

        // Zoom controls
        const btnZoomIn = document.getElementById('btn-zoom-in');
        const btnZoomOut = document.getElementById('btn-zoom-out');
        const btnZoomFit = document.getElementById('btn-zoom-fit');
        if (btnZoomIn) btnZoomIn.addEventListener('click', () => this.setZoom(this.zoom + 0.1));
        if (btnZoomOut) btnZoomOut.addEventListener('click', () => this.setZoom(this.zoom - 0.1));
        if (btnZoomFit) btnZoomFit.addEventListener('click', () => this.fitToView());

        // Grid controls
        if (this.elements.snapToGrid) {
            this.elements.snapToGrid.addEventListener('change', (e) => {
                this.snapToGrid = e.target.checked;
                this.elements.canvasGrid.classList.toggle('hidden', !this.snapToGrid);
            });
        }
        if (this.elements.gridSize) {
            this.elements.gridSize.addEventListener('change', (e) => {
                this.gridSize = parseInt(e.target.value);
                this.updateGridDisplay();
            });
        }

        // Canvas mouse events
        if (this.elements.canvasWrapper) {
            this.elements.canvasWrapper.addEventListener('mousemove', (e) => this.onCanvasMouseMove(e));
            this.elements.canvasWrapper.addEventListener('mouseup', (e) => this.onCanvasMouseUp(e));
            this.elements.canvasWrapper.addEventListener('mouseleave', (e) => this.onCanvasMouseUp(e));
        }
        if (this.elements.canvasPoster) {
            this.elements.canvasPoster.addEventListener('click', (e) => this.onCanvasClick(e));
        }

        // YAML editor
        if (this.elements.yamlEditor) {
            this.elements.yamlEditor.addEventListener('input', () => this.onYamlInput());
        }

        // Copy and Apply YAML buttons
        const btnCopyYaml = document.getElementById('btn-copy-yaml');
        const btnApplyYaml = document.getElementById('btn-apply-yaml');
        if (btnCopyYaml) btnCopyYaml.addEventListener('click', () => this.copyYamlToClipboard());
        if (btnApplyYaml) btnApplyYaml.addEventListener('click', () => this.applyYamlChanges());

        // Undo/Redo
        const btnUndo = document.getElementById('btn-editor-undo');
        const btnRedo = document.getElementById('btn-editor-redo');
        if (btnUndo) btnUndo.addEventListener('click', () => this.undo());
        if (btnRedo) btnRedo.addEventListener('click', () => this.redo());

        // Add overlay buttons
        const btnAddOverlay = document.getElementById('btn-add-overlay');
        const btnAddOverlayLayer = document.getElementById('btn-add-overlay-layer');
        const btnCloseAddOverlay = document.getElementById('btn-close-add-overlay');
        if (btnAddOverlay) btnAddOverlay.addEventListener('click', () => this.openAddOverlayDialog());
        if (btnAddOverlayLayer) btnAddOverlayLayer.addEventListener('click', () => this.openAddOverlayDialog());
        if (btnCloseAddOverlay) btnCloseAddOverlay.addEventListener('click', () => this.closeAddOverlayDialog());

        // Add overlay type selection
        document.querySelectorAll('.add-overlay-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.selectOverlayType(e.currentTarget.dataset.type));
        });

        // Create overlay buttons
        const btnCreateImage = document.getElementById('btn-create-image-overlay');
        const btnCreateText = document.getElementById('btn-create-text-overlay');
        const btnCreateBackdrop = document.getElementById('btn-create-backdrop-overlay');
        if (btnCreateImage) btnCreateImage.addEventListener('click', () => this.createImageOverlay());
        if (btnCreateText) btnCreateText.addEventListener('click', () => this.createTextOverlay());
        if (btnCreateBackdrop) btnCreateBackdrop.addEventListener('click', () => this.createBackdropOverlay());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (!this.isOpen) return;
            if (e.key === 'Delete' && this.selectedOverlayIndex !== null) {
                this.deleteSelectedOverlay();
            }
            if (e.ctrlKey && e.key === 'z') {
                e.preventDefault();
                this.undo();
            }
            if (e.ctrlKey && e.key === 'y') {
                e.preventDefault();
                this.redo();
            }
        });

        // Export YAML button
        const btnExportYaml = document.getElementById('btn-export-yaml');
        if (btnExportYaml) btnExportYaml.addEventListener('click', () => this.exportYaml());

        // Load poster and import overlays buttons
        const btnLoadPoster = document.getElementById('btn-load-poster');
        const btnImportOverlays = document.getElementById('btn-import-overlays');
        if (btnLoadPoster) btnLoadPoster.addEventListener('click', () => this.fetchCleanPoster());
        if (btnImportOverlays) btnImportOverlays.addEventListener('click', () => this.showImportDialog());
    },

    open() {
        if (!this.elements.modal) return;

        // Load overlays: prefer selected overlays, fall back to loaded overlays from config
        if (state.selectedOverlays && state.selectedOverlays.length > 0) {
            this.overlays = JSON.parse(JSON.stringify(state.selectedOverlays));
        } else if (state.loadedOverlays && state.loadedOverlays.length > 0) {
            // Use all loaded overlays from the config file
            this.overlays = JSON.parse(JSON.stringify(state.loadedOverlays));
        } else {
            this.overlays = [];
        }

        this.selectedOverlayIndex = null;
        this.undoStack = [];
        this.redoStack = [];

        // Show modal
        this.elements.modal.classList.remove('hidden');
        this.isOpen = true;

        // Set canvas size based on selected canvas type
        const canvasType = elements.canvasType?.value || 'portrait';
        if (canvasType === 'portrait') {
            this.canvasWidth = 1000;
            this.canvasHeight = 1500;
        } else if (canvasType === 'landscape') {
            this.canvasWidth = 1920;
            this.canvasHeight = 1080;
        } else if (canvasType === 'square') {
            this.canvasWidth = 1000;
            this.canvasHeight = 1000;
        }

        // Update canvas display
        this.updateCanvasSize();
        this.fitToView();

        // Load poster background if available
        this.loadPosterBackground();

        // Render overlays and UI
        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();

        // Enable toolbar buttons
        const btnAddOverlay = document.getElementById('btn-add-overlay');
        const btnExportYaml = document.getElementById('btn-export-yaml');
        if (btnAddOverlay) btnAddOverlay.disabled = false;
        if (btnExportYaml) btnExportYaml.disabled = false;
    },

    close() {
        if (!this.elements.modal) return;
        this.elements.modal.classList.add('hidden');
        this.isOpen = false;

        // Sync changes back to selected overlays
        state.selectedOverlays = JSON.parse(JSON.stringify(this.overlays));
        renderSelectedOverlays();
    },

    updateCanvasSize() {
        if (!this.elements.canvasPoster) return;

        const displayWidth = this.canvasWidth * this.displayScale;
        const displayHeight = this.canvasHeight * this.displayScale;

        this.elements.canvasPoster.style.width = `${displayWidth}px`;
        this.elements.canvasPoster.style.height = `${displayHeight}px`;

        if (this.elements.canvasDimensions) {
            this.elements.canvasDimensions.textContent = `${this.canvasWidth} × ${this.canvasHeight}`;
        }

        this.updateGridDisplay();
    },

    updateGridDisplay() {
        if (!this.elements.canvasGrid) return;
        const gridSizeDisplay = this.gridSize * this.displayScale;
        this.elements.canvasGrid.style.backgroundSize = `${gridSizeDisplay}px ${gridSizeDisplay}px`;
    },

    setZoom(level) {
        this.zoom = Math.max(0.25, Math.min(2, level));
        if (this.elements.canvas) {
            this.elements.canvas.style.transform = `scale(${this.zoom})`;
        }
        if (this.elements.zoomLevel) {
            this.elements.zoomLevel.textContent = `${Math.round(this.zoom * 100)}%`;
        }
    },

    fitToView() {
        if (!this.elements.canvasWrapper || !this.elements.canvasPoster) return;

        const wrapperRect = this.elements.canvasWrapper.getBoundingClientRect();
        const posterWidth = this.canvasWidth * this.displayScale;
        const posterHeight = this.canvasHeight * this.displayScale;

        const scaleX = (wrapperRect.width - 40) / posterWidth;
        const scaleY = (wrapperRect.height - 40) / posterHeight;
        const fitZoom = Math.min(scaleX, scaleY, 1);

        this.setZoom(fitZoom);
    },

    loadPosterBackground() {
        if (!this.elements.canvasPoster) return;

        // Use current preview image if available (base64 data URL)
        if (state.currentPreviewImage) {
            this.elements.canvasPoster.style.backgroundImage = `url(${state.currentPreviewImage})`;
            return;
        }

        // Try to get poster from selected media item
        if (state.selectedPoster) {
            if (state.selectedPoster.thumb) {
                this.elements.canvasPoster.style.backgroundImage = `url(${state.selectedPoster.thumb})`;
                return;
            }
        }

        // Load default Dune poster from TMDb as fallback
        this.loadDefaultPoster();
    },

    /**
     * Load a default poster (Dune 2021) for the visual editor
     */
    async loadDefaultPoster() {
        if (!this.elements.canvasPoster) return;

        // Set a temporary gradient while loading
        this.elements.canvasPoster.style.backgroundImage = 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)';

        try {
            // Dune (2021) TMDb ID: 438631
            const requestData = {
                overlays: [],
                canvas_type: 'portrait',
                template_variables: {},
                poster_source: 'tmdb',
                tmdb_id: '438631',
                media_type: 'movie'
            };

            const response = await fetch('/api/overlays/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            if (result.image) {
                this.elements.canvasPoster.style.backgroundImage = `url(${result.image})`;
                // Store as default poster info
                this.defaultPosterLoaded = true;
            }
        } catch (error) {
            console.log('Could not load default poster:', error);
            // Keep the gradient background on error
        }
    },

    // Fetch a clean poster (without overlays) for the visual editor
    async fetchCleanPoster() {
        console.log('fetchCleanPoster called');
        console.log('state.selectedPoster:', state.selectedPoster);
        if (!state.selectedPoster) {
            alert('Please select a poster from the Poster Source section first');
            return;
        }

        try {
            const requestData = {
                overlays: [],  // No overlays - just the poster
                canvas_type: elements.canvasType?.value || 'portrait',
                template_variables: {}
            };

            if (state.selectedPoster.source === 'plex') {
                requestData.poster_source = 'plex';
                requestData.rating_key = state.selectedPoster.rating_key;
            } else if (state.selectedPoster.source === 'tmdb') {
                requestData.poster_source = 'tmdb';
                requestData.tmdb_id = state.selectedPoster.tmdb_id;
                requestData.media_type = state.selectedPoster.media_type;
            }

            const response = await fetch('/api/overlays/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            if (result.image) {
                this.elements.canvasPoster.style.backgroundImage = `url(${result.image})`;
                this.setYamlStatus('success', 'Poster loaded');
            }
        } catch (error) {
            console.error('Failed to load poster:', error);
            this.setYamlStatus('error', 'Failed to load poster');
        }
    },

    // Overlay rendering
    renderOverlays() {
        if (!this.elements.canvasPoster) return;

        // Clear existing overlay elements (but keep grid)
        const existingOverlays = this.elements.canvasPoster.querySelectorAll('.canvas-overlay');
        existingOverlays.forEach(el => el.remove());

        // Render each overlay (in order - first overlay is bottom layer, last is top)
        this.overlays.forEach((overlay, index) => {
            // Skip hidden overlays
            if (overlay._hidden) return;

            const el = this.createOverlayElement(overlay, index);
            // Set z-index based on position in array (later = higher)
            el.style.zIndex = index + 1;
            this.elements.canvasPoster.appendChild(el);
        });
    },

    createOverlayElement(overlay, index) {
        const el = document.createElement('div');
        el.className = 'canvas-overlay';
        el.dataset.index = index;

        if (index === this.selectedOverlayIndex) {
            el.classList.add('selected');
        }

        // Calculate position and size
        const pos = this.calculateOverlayPosition(overlay);
        el.style.left = `${pos.x * this.displayScale}px`;
        el.style.top = `${pos.y * this.displayScale}px`;
        el.style.width = `${pos.width * this.displayScale}px`;
        el.style.height = `${pos.height * this.displayScale}px`;

        // Set content based on type
        if (overlay.type === 'text') {
            el.innerHTML = `<span style="color: ${overlay.font_color || '#fff'}; font-size: ${(overlay.font_size || 50) * this.displayScale * 0.5}px;">${overlay.text_content || overlay.name}</span>`;
            el.style.display = 'flex';
            el.style.alignItems = 'center';
            el.style.justifyContent = 'center';
        } else if (overlay.type === 'backdrop') {
            el.style.backgroundColor = overlay.back_color || 'rgba(0,0,0,0.7)';
        } else {
            // Image overlay - show actual image from backend-provided URL
            const imgUrl = overlay.image_url || (overlay.default ? `/overlay-images/${overlay.default}.png` : null);
            if (imgUrl) {
                el.innerHTML = `<img src="${imgUrl}" style="width:100%;height:100%;object-fit:contain;" onerror="this.parentElement.innerHTML='<span style=\\'color:#888;font-size:11px;text-align:center;\\'>${overlay.name}</span>'; this.parentElement.style.backgroundColor='rgba(50,50,50,0.5)';">`;
                el.style.backgroundColor = 'transparent';
            } else {
                // Generate dynamic badge for overlays without pre-made images (like Edition overlays)
                // These are rendered as styled text on a background, similar to Kometa's dynamic generation
                const badgeHtml = this.generateDynamicBadge(overlay);
                el.innerHTML = badgeHtml;
                el.style.backgroundColor = 'transparent';
            }
            el.style.display = 'flex';
            el.style.alignItems = 'center';
            el.style.justifyContent = 'center';
        }

        // Add resize handles
        ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'].forEach(pos => {
            const handle = document.createElement('div');
            handle.className = `resize-handle ${pos}`;
            handle.dataset.handle = pos;
            el.appendChild(handle);
        });

        // Event listeners
        el.addEventListener('mousedown', (e) => this.onOverlayMouseDown(e, index));

        return el;
    },

    /**
     * Generate a dynamic badge for overlays without pre-made images.
     * Replicates Kometa's style for Edition overlays (Directors-Cut, etc.)
     * These use a semi-transparent background with styled text.
     */
    generateDynamicBadge(overlay) {
        // Get display text - clean up the name for display
        let displayText = overlay.display_name || overlay.name || 'Unknown';
        // Remove common suffixes for cleaner display
        displayText = displayText.replace(/-Dovetail$/, '').replace(/-/g, ' ');

        // Kometa edition badges use these default styles:
        // - Background: #00000099 (semi-transparent black)
        // - Text color: #FFFFFF
        // - Font: Inter-Medium style
        const backColor = overlay.back_color || 'rgba(0, 0, 0, 0.6)';
        const textColor = overlay.font_color || '#FFFFFF';
        const fontSize = Math.max(10, (overlay.font_size || 55) * this.displayScale * 0.22);
        const strokeWidth = overlay.stroke_width || 0;
        const strokeColor = overlay.stroke_color || '#000000';

        // Determine if this is a "dovetail" style (has the pointed edge)
        const isDovetail = (overlay.name || '').includes('Dovetail');

        // Build the badge HTML with inline SVG for the dovetail shape
        if (isDovetail) {
            // Dovetail style - pointed edge on the right
            return `
                <div style="
                    position: relative;
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                ">
                    <div style="
                        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                        border: 1px solid #e94560;
                        border-radius: 4px 0 0 4px;
                        padding: 4px 12px 4px 8px;
                        display: flex;
                        align-items: center;
                        height: 80%;
                        box-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                        clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%);
                    ">
                        <span style="
                            color: ${textColor};
                            font-size: ${fontSize}px;
                            font-weight: 600;
                            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                            white-space: nowrap;
                            letter-spacing: 0.5px;
                            ${strokeWidth > 0 ? `-webkit-text-stroke: ${strokeWidth}px ${strokeColor};` : ''}
                        ">${displayText}</span>
                    </div>
                </div>
            `;
        } else {
            // Standard rectangle badge
            return `
                <div style="
                    background: ${backColor};
                    border-radius: 4px;
                    padding: 6px 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 100%;
                    box-sizing: border-box;
                    box-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                ">
                    <span style="
                        color: ${textColor};
                        font-size: ${fontSize}px;
                        font-weight: 600;
                        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                        text-align: center;
                        ${strokeWidth > 0 ? `-webkit-text-stroke: ${strokeWidth}px ${strokeColor};` : ''}
                    ">${displayText}</span>
                </div>
            `;
        }
    },

    calculateOverlayPosition(overlay) {
        // Default size for overlays - use typical Kometa overlay sizes
        // Resolution overlays are typically ~208x53, ribbons vary
        let width = overlay.back_width || overlay.scale_width || 210;
        let height = overlay.back_height || overlay.scale_height || 55;

        // Calculate position based on alignment and offset
        const hAlign = overlay.horizontal_align || 'center';
        const vAlign = overlay.vertical_align || 'top';
        const hOffset = parseInt(overlay.horizontal_offset) || 0;
        const vOffset = parseInt(overlay.vertical_offset) || 0;

        let x = hOffset;
        let y = vOffset;

        // Horizontal alignment
        if (hAlign === 'center') {
            x = (this.canvasWidth - width) / 2 + hOffset;
        } else if (hAlign === 'right') {
            x = this.canvasWidth - width - hOffset;
        } else {
            x = hOffset;
        }

        // Vertical alignment
        if (vAlign === 'center') {
            y = (this.canvasHeight - height) / 2 + vOffset;
        } else if (vAlign === 'bottom') {
            y = this.canvasHeight - height - vOffset;
        } else {
            y = vOffset;
        }

        return { x, y, width, height };
    },

    // Mouse event handlers
    onOverlayMouseDown(e, index) {
        e.stopPropagation();

        // Check if clicking resize handle
        if (e.target.classList.contains('resize-handle')) {
            this.startResize(e, index, e.target.dataset.handle);
            return;
        }

        // Select overlay
        this.selectOverlay(index);

        // Start drag
        this.isDragging = true;
        const overlayEl = e.currentTarget;
        const rect = overlayEl.getBoundingClientRect();
        this.dragStart = { x: e.clientX, y: e.clientY };
        this.dragOffset = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };

        overlayEl.classList.add('dragging');
    },

    onCanvasMouseMove(e) {
        // Update mouse position display
        if (this.elements.mousePosition) {
            const rect = this.elements.canvasPoster?.getBoundingClientRect();
            if (rect) {
                const x = Math.round((e.clientX - rect.left) / this.displayScale / this.zoom);
                const y = Math.round((e.clientY - rect.top) / this.displayScale / this.zoom);
                this.elements.mousePosition.textContent = `X: ${x}, Y: ${y}`;
            }
        }

        if (this.isDragging && this.selectedOverlayIndex !== null) {
            this.handleDrag(e);
        }

        if (this.isResizing && this.selectedOverlayIndex !== null) {
            this.handleResize(e);
        }
    },

    onCanvasMouseUp(e) {
        if (this.isDragging) {
            this.isDragging = false;
            document.querySelectorAll('.canvas-overlay.dragging').forEach(el => {
                el.classList.remove('dragging');
            });
            this.generateYaml();
        }

        if (this.isResizing) {
            this.isResizing = false;
            this.generateYaml();
        }
    },

    onCanvasClick(e) {
        // Deselect if clicking on canvas background
        if (e.target === this.elements.canvasPoster || e.target === this.elements.canvasGrid) {
            this.selectOverlay(null);
        }
    },

    handleDrag(e) {
        if (this.selectedOverlayIndex === null) return;

        const overlay = this.overlays[this.selectedOverlayIndex];
        const posterRect = this.elements.canvasPoster.getBoundingClientRect();

        // Calculate new position in canvas coordinates
        let newX = (e.clientX - posterRect.left - this.dragOffset.x) / this.displayScale / this.zoom;
        let newY = (e.clientY - posterRect.top - this.dragOffset.y) / this.displayScale / this.zoom;

        // Snap to grid
        if (this.snapToGrid) {
            newX = Math.round(newX / this.gridSize) * this.gridSize;
            newY = Math.round(newY / this.gridSize) * this.gridSize;
        }

        // Update overlay position (store as offset from top-left for simplicity)
        overlay.horizontal_align = 'left';
        overlay.vertical_align = 'top';
        overlay.horizontal_offset = Math.max(0, Math.round(newX));
        overlay.vertical_offset = Math.max(0, Math.round(newY));

        // Update visual
        this.renderOverlays();
        this.renderProperties();
    },

    startResize(e, index, handle) {
        e.stopPropagation();
        this.isResizing = true;
        this.resizeHandle = handle;
        this.selectOverlay(index);

        const overlayEl = this.elements.canvasPoster.querySelector(`[data-index="${index}"]`);
        const rect = overlayEl.getBoundingClientRect();

        this.resizeStart = {
            x: e.clientX,
            y: e.clientY,
            width: rect.width / this.zoom,
            height: rect.height / this.zoom,
            left: rect.left,
            top: rect.top
        };
    },

    handleResize(e) {
        if (this.selectedOverlayIndex === null) return;

        const overlay = this.overlays[this.selectedOverlayIndex];
        const dx = (e.clientX - this.resizeStart.x) / this.zoom;
        const dy = (e.clientY - this.resizeStart.y) / this.zoom;

        let newWidth = this.resizeStart.width / this.displayScale;
        let newHeight = this.resizeStart.height / this.displayScale;

        // Adjust based on handle
        if (this.resizeHandle.includes('e')) newWidth += dx / this.displayScale;
        if (this.resizeHandle.includes('w')) newWidth -= dx / this.displayScale;
        if (this.resizeHandle.includes('s')) newHeight += dy / this.displayScale;
        if (this.resizeHandle.includes('n')) newHeight -= dy / this.displayScale;

        // Snap to grid
        if (this.snapToGrid) {
            newWidth = Math.round(newWidth / this.gridSize) * this.gridSize;
            newHeight = Math.round(newHeight / this.gridSize) * this.gridSize;
        }

        // Minimum size
        newWidth = Math.max(20, newWidth);
        newHeight = Math.max(20, newHeight);

        // Update overlay size
        overlay.back_width = Math.round(newWidth);
        overlay.back_height = Math.round(newHeight);

        // Update visual
        this.renderOverlays();
        this.renderProperties();
    },

    selectOverlay(index) {
        this.selectedOverlayIndex = index;

        // Update canvas overlay selection
        this.elements.canvasPoster?.querySelectorAll('.canvas-overlay').forEach((el, i) => {
            el.classList.toggle('selected', i === index);
        });

        // Update layers list selection
        this.renderLayersList();

        // Update properties panel
        this.renderProperties();

        // Update status
        if (this.elements.selectedOverlayInfo) {
            if (index !== null && this.overlays[index]) {
                this.elements.selectedOverlayInfo.textContent = `Selected: ${this.overlays[index].name}`;
            } else {
                this.elements.selectedOverlayInfo.textContent = 'No overlay selected';
            }
        }
    },

    // Layers list
    renderLayersList() {
        if (!this.elements.layersList) return;

        if (this.overlays.length === 0) {
            this.elements.layersList.innerHTML = '<p class="placeholder-text">No overlays loaded</p>';
            return;
        }

        // Render in reverse order so top layers appear first in the list
        const overlaysReversed = this.overlays.map((overlay, index) => ({ overlay, index })).reverse();

        this.elements.layersList.innerHTML = overlaysReversed.map(({ overlay, index }) => {
            const isSelected = index === this.selectedOverlayIndex;
            const isHidden = overlay._hidden;
            const isFirst = index === 0;
            const isLast = index === this.overlays.length - 1;

            // Generate thumbnail for the overlay
            const thumbnail = this.generateLayerThumbnail(overlay);

            return `
                <div class="layer-item ${isSelected ? 'selected' : ''} ${isHidden ? 'hidden-layer' : ''}" data-index="${index}" onclick="visualEditor.selectOverlay(${index})">
                    <span class="layer-visibility ${isHidden ? 'layer-hidden' : ''}" onclick="event.stopPropagation(); visualEditor.toggleLayerVisibility(${index})" title="${isHidden ? 'Show layer' : 'Hide layer'}">${isHidden ? '👁‍🗨' : '👁'}</span>
                    <span class="layer-thumbnail">${thumbnail}</span>
                    <span class="layer-name" title="${overlay.name}">${overlay.name}</span>
                    <span class="layer-type">${overlay.type || 'IMAGE'}</span>
                    <span class="layer-controls">
                        <button class="layer-btn" onclick="event.stopPropagation(); visualEditor.moveLayerUp(${index})" ${isLast ? 'disabled' : ''} title="Move to front">▲</button>
                        <button class="layer-btn" onclick="event.stopPropagation(); visualEditor.moveLayerDown(${index})" ${isFirst ? 'disabled' : ''} title="Move to back">▼</button>
                    </span>
                    <span class="layer-delete" onclick="event.stopPropagation(); visualEditor.deleteOverlay(${index})" title="Delete overlay">✕</span>
                </div>
            `;
        }).join('');
    },

    /**
     * Generate a thumbnail preview for an overlay in the layers list
     */
    generateLayerThumbnail(overlay) {
        // For overlays with image URLs, show the actual image
        const imgUrl = overlay.image_url || (overlay.default ? `/overlay-images/${overlay.default}.png` : null);

        if (imgUrl) {
            return `<img src="${imgUrl}" style="width:24px;height:24px;object-fit:contain;border-radius:2px;" onerror="this.style.display='none'">`;
        }

        // For text overlays
        if (overlay.type === 'text') {
            return `<span style="font-size:10px;background:#333;padding:2px 4px;border-radius:2px;">📝</span>`;
        }

        // For backdrop overlays
        if (overlay.type === 'backdrop') {
            const bgColor = overlay.back_color || '#333';
            return `<span style="display:inline-block;width:24px;height:16px;background:${bgColor};border-radius:2px;"></span>`;
        }

        // For dynamic overlays (no image file), generate a mini badge preview
        const isDovetail = (overlay.name || '').includes('Dovetail');
        const displayText = (overlay.display_name || overlay.name || '?').replace(/-Dovetail$/, '').replace(/-/g, ' ').substring(0, 3);

        if (isDovetail) {
            return `
                <span style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 28px;
                    height: 18px;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                    border: 1px solid #e94560;
                    border-radius: 2px 0 0 2px;
                    font-size: 7px;
                    color: #fff;
                    font-weight: bold;
                    clip-path: polygon(0 0, calc(100% - 5px) 0, 100% 50%, calc(100% - 5px) 100%, 0 100%);
                ">${displayText}</span>
            `;
        } else {
            return `
                <span style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 24px;
                    height: 16px;
                    background: rgba(0,0,0,0.6);
                    border-radius: 2px;
                    font-size: 7px;
                    color: #fff;
                    font-weight: bold;
                ">${displayText}</span>
            `;
        }
    },

    toggleLayerVisibility(index) {
        const overlay = this.overlays[index];
        overlay._hidden = !overlay._hidden;
        this.renderOverlays();
        this.renderLayersList();
    },

    /**
     * Move layer up in z-order (towards the front/top)
     */
    moveLayerUp(index) {
        if (index >= this.overlays.length - 1) return; // Already at top

        this.saveUndoState();

        // Swap with the layer above
        const temp = this.overlays[index];
        this.overlays[index] = this.overlays[index + 1];
        this.overlays[index + 1] = temp;

        // Update selection if needed
        if (this.selectedOverlayIndex === index) {
            this.selectedOverlayIndex = index + 1;
        } else if (this.selectedOverlayIndex === index + 1) {
            this.selectedOverlayIndex = index;
        }

        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
    },

    /**
     * Move layer down in z-order (towards the back/bottom)
     */
    moveLayerDown(index) {
        if (index <= 0) return; // Already at bottom

        this.saveUndoState();

        // Swap with the layer below
        const temp = this.overlays[index];
        this.overlays[index] = this.overlays[index - 1];
        this.overlays[index - 1] = temp;

        // Update selection if needed
        if (this.selectedOverlayIndex === index) {
            this.selectedOverlayIndex = index - 1;
        } else if (this.selectedOverlayIndex === index - 1) {
            this.selectedOverlayIndex = index;
        }

        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
    },

    /**
     * Move selected layer to front (top of z-order)
     */
    moveToFront() {
        if (this.selectedOverlayIndex === null || this.selectedOverlayIndex >= this.overlays.length - 1) return;

        this.saveUndoState();

        const overlay = this.overlays.splice(this.selectedOverlayIndex, 1)[0];
        this.overlays.push(overlay);
        this.selectedOverlayIndex = this.overlays.length - 1;

        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
    },

    /**
     * Move selected layer to back (bottom of z-order)
     */
    moveToBack() {
        if (this.selectedOverlayIndex === null || this.selectedOverlayIndex <= 0) return;

        this.saveUndoState();

        const overlay = this.overlays.splice(this.selectedOverlayIndex, 1)[0];
        this.overlays.unshift(overlay);
        this.selectedOverlayIndex = 0;

        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
    },

    deleteOverlay(index) {
        if (confirm(`Delete overlay "${this.overlays[index].name}"?`)) {
            this.saveUndoState();
            this.overlays.splice(index, 1);
            if (this.selectedOverlayIndex === index) {
                this.selectedOverlayIndex = null;
            } else if (this.selectedOverlayIndex > index) {
                this.selectedOverlayIndex--;
            }
            this.renderOverlays();
            this.renderLayersList();
            this.renderProperties();
            this.generateYaml();
        }
    },

    deleteSelectedOverlay() {
        if (this.selectedOverlayIndex !== null) {
            this.deleteOverlay(this.selectedOverlayIndex);
        }
    },

    // Properties panel
    renderProperties() {
        if (!this.elements.propertiesContent) return;

        if (this.selectedOverlayIndex === null) {
            this.elements.propertiesContent.innerHTML = '<p class="placeholder-text">Select an overlay to edit its properties</p>';
            return;
        }

        const overlay = this.overlays[this.selectedOverlayIndex];

        this.elements.propertiesContent.innerHTML = `
            <div class="property-row">
                <label>Name</label>
                <input type="text" value="${overlay.name}" onchange="visualEditor.updateProperty('name', this.value)">
            </div>
            <div class="property-row-inline">
                <div class="property-row">
                    <label>H Align</label>
                    <select onchange="visualEditor.updateProperty('horizontal_align', this.value)">
                        <option value="left" ${overlay.horizontal_align === 'left' ? 'selected' : ''}>Left</option>
                        <option value="center" ${overlay.horizontal_align === 'center' ? 'selected' : ''}>Center</option>
                        <option value="right" ${overlay.horizontal_align === 'right' ? 'selected' : ''}>Right</option>
                    </select>
                </div>
                <div class="property-row">
                    <label>V Align</label>
                    <select onchange="visualEditor.updateProperty('vertical_align', this.value)">
                        <option value="top" ${overlay.vertical_align === 'top' ? 'selected' : ''}>Top</option>
                        <option value="center" ${overlay.vertical_align === 'center' ? 'selected' : ''}>Center</option>
                        <option value="bottom" ${overlay.vertical_align === 'bottom' ? 'selected' : ''}>Bottom</option>
                    </select>
                </div>
            </div>
            <div class="property-row-inline">
                <div class="property-row">
                    <label>H Offset</label>
                    <input type="number" value="${overlay.horizontal_offset || 0}" onchange="visualEditor.updateProperty('horizontal_offset', parseInt(this.value))">
                </div>
                <div class="property-row">
                    <label>V Offset</label>
                    <input type="number" value="${overlay.vertical_offset || 0}" onchange="visualEditor.updateProperty('vertical_offset', parseInt(this.value))">
                </div>
            </div>
            <div class="property-row-inline">
                <div class="property-row">
                    <label>Width</label>
                    <input type="number" value="${overlay.back_width || 200}" onchange="visualEditor.updateProperty('back_width', parseInt(this.value))">
                </div>
                <div class="property-row">
                    <label>Height</label>
                    <input type="number" value="${overlay.back_height || 100}" onchange="visualEditor.updateProperty('back_height', parseInt(this.value))">
                </div>
            </div>
            ${overlay.type === 'text' ? `
                <div class="property-row">
                    <label>Text</label>
                    <input type="text" value="${overlay.text_content || ''}" onchange="visualEditor.updateProperty('text_content', this.value)">
                </div>
                <div class="property-row">
                    <label>Font Size</label>
                    <input type="number" value="${overlay.font_size || 50}" onchange="visualEditor.updateProperty('font_size', parseInt(this.value))">
                </div>
                <div class="property-row">
                    <label>Font Color</label>
                    <input type="color" value="${overlay.font_color || '#FFFFFF'}" onchange="visualEditor.updateProperty('font_color', this.value)">
                </div>
            ` : ''}
            ${overlay.type === 'backdrop' ? `
                <div class="property-row">
                    <label>Back Color</label>
                    <input type="text" value="${overlay.back_color || '#000000AA'}" onchange="visualEditor.updateProperty('back_color', this.value)">
                </div>
            ` : ''}
            <div class="property-row">
                <label>Group</label>
                <input type="text" value="${overlay.group || ''}" onchange="visualEditor.updateProperty('group', this.value)">
            </div>
            <div class="property-row">
                <label>Weight</label>
                <input type="number" value="${overlay.weight || ''}" onchange="visualEditor.updateProperty('weight', parseInt(this.value) || null)">
            </div>
        `;
    },

    updateProperty(prop, value) {
        if (this.selectedOverlayIndex === null) return;

        this.saveUndoState();
        this.overlays[this.selectedOverlayIndex][prop] = value;

        this.renderOverlays();
        this.generateYaml();
    },

    // YAML generation and parsing
    generateYaml() {
        if (!this.elements.yamlEditor) return;

        let yaml = 'overlays:\n';

        this.overlays.forEach(overlay => {
            yaml += `  ${overlay.name}:\n`;

            // Overlay image/text settings
            if (overlay.type === 'text') {
                yaml += `    overlay:\n`;
                yaml += `      name: text(${overlay.text_content || overlay.name})\n`;
                if (overlay.font) yaml += `      font: ${overlay.font}\n`;
                if (overlay.font_size) yaml += `      font_size: ${overlay.font_size}\n`;
                if (overlay.font_color) yaml += `      font_color: "${overlay.font_color}"\n`;
            } else if (overlay.type === 'backdrop') {
                yaml += `    overlay:\n`;
                yaml += `      name: backdrop\n`;
                if (overlay.back_color) yaml += `      back_color: "${overlay.back_color}"\n`;
                if (overlay.back_width) yaml += `      back_width: ${overlay.back_width}\n`;
                if (overlay.back_height) yaml += `      back_height: ${overlay.back_height}\n`;
            } else {
                yaml += `    overlay:\n`;
                yaml += `      name: ${overlay.name}\n`;
                if (overlay.default) yaml += `      default: ${overlay.default}\n`;
                if (overlay.file) yaml += `      file: ${overlay.file}\n`;
            }

            // Position settings
            if (overlay.horizontal_align) yaml += `      horizontal_align: ${overlay.horizontal_align}\n`;
            if (overlay.vertical_align) yaml += `      vertical_align: ${overlay.vertical_align}\n`;
            if (overlay.horizontal_offset) yaml += `      horizontal_offset: ${overlay.horizontal_offset}\n`;
            if (overlay.vertical_offset) yaml += `      vertical_offset: ${overlay.vertical_offset}\n`;

            // Group and weight
            if (overlay.group) yaml += `      group: ${overlay.group}\n`;
            if (overlay.weight) yaml += `      weight: ${overlay.weight}\n`;

            // Plex all filter (basic)
            yaml += `    plex_all: true\n`;
        });

        this.elements.yamlEditor.value = yaml;
        this.setYamlStatus('success', 'YAML updated');
    },

    onYamlInput() {
        // Debounce YAML parsing
        clearTimeout(this._yamlDebounce);
        this._yamlDebounce = setTimeout(() => this.parseYaml(), 500);
    },

    parseYaml() {
        // This is a simplified parser - in production you'd use a proper YAML library
        const yaml = this.elements.yamlEditor.value;
        // For now, just validate basic structure
        if (yaml.includes('overlays:')) {
            this.setYamlStatus('success', 'Valid YAML structure');
        } else {
            this.setYamlStatus('error', 'Invalid YAML structure');
        }
    },

    applyYamlChanges() {
        // In a full implementation, this would parse the YAML and update overlays
        this.setYamlStatus('success', 'Changes applied');
        this.renderOverlays();
        this.renderLayersList();
    },

    setYamlStatus(type, message) {
        if (!this.elements.yamlStatus) return;
        this.elements.yamlStatus.className = `yaml-status ${type}`;
        this.elements.yamlStatus.innerHTML = `<span class="status-text">${message}</span>`;
    },

    copyYamlToClipboard() {
        if (!this.elements.yamlEditor) return;
        navigator.clipboard.writeText(this.elements.yamlEditor.value).then(() => {
            this.setYamlStatus('success', 'Copied to clipboard!');
        });
    },

    exportYaml() {
        this.generateYaml();
        const yaml = this.elements.yamlEditor?.value || '';

        // Create download
        const blob = new Blob([yaml], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'overlays.yml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    // Undo/Redo
    saveUndoState() {
        this.undoStack.push(JSON.stringify(this.overlays));
        this.redoStack = [];
        this.updateUndoRedoButtons();
    },

    undo() {
        if (this.undoStack.length === 0) return;

        this.redoStack.push(JSON.stringify(this.overlays));
        this.overlays = JSON.parse(this.undoStack.pop());

        this.renderOverlays();
        this.renderLayersList();
        this.renderProperties();
        this.generateYaml();
        this.updateUndoRedoButtons();
    },

    redo() {
        if (this.redoStack.length === 0) return;

        this.undoStack.push(JSON.stringify(this.overlays));
        this.overlays = JSON.parse(this.redoStack.pop());

        this.renderOverlays();
        this.renderLayersList();
        this.renderProperties();
        this.generateYaml();
        this.updateUndoRedoButtons();
    },

    updateUndoRedoButtons() {
        const btnUndo = document.getElementById('btn-editor-undo');
        const btnRedo = document.getElementById('btn-editor-redo');
        if (btnUndo) btnUndo.disabled = this.undoStack.length === 0;
        if (btnRedo) btnRedo.disabled = this.redoStack.length === 0;
    },

    // Add overlay dialog
    openAddOverlayDialog() {
        if (this.elements.addOverlayDialog) {
            this.elements.addOverlayDialog.classList.remove('hidden');
            // Reset forms
            document.querySelectorAll('.add-overlay-form').forEach(f => f.classList.add('hidden'));
            document.querySelectorAll('.add-overlay-type-btn').forEach(b => b.classList.remove('active'));
        }
    },

    closeAddOverlayDialog() {
        if (this.elements.addOverlayDialog) {
            this.elements.addOverlayDialog.classList.add('hidden');
        }
    },

    selectOverlayType(type) {
        // Update button states
        document.querySelectorAll('.add-overlay-type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === type);
        });

        // Show appropriate form
        document.querySelectorAll('.add-overlay-form').forEach(f => f.classList.add('hidden'));
        const formId = `form-${type}-overlay`;
        const form = document.getElementById(formId);
        if (form) form.classList.remove('hidden');

        // Populate image dropdown if needed
        if (type === 'image') {
            this.populateImageDropdown();
        }
    },

    populateImageDropdown() {
        const select = document.getElementById('new-overlay-default');
        if (!select || Object.keys(state.availableImages).length === 0) return;

        select.innerHTML = '<option value="">-- Select image --</option>';
        Object.entries(state.availableImages).forEach(([category, images]) => {
            const group = document.createElement('optgroup');
            group.label = category;
            images.forEach(img => {
                const opt = document.createElement('option');
                opt.value = img;
                opt.textContent = img.split('/').pop();
                group.appendChild(opt);
            });
            select.appendChild(group);
        });
    },

    createImageOverlay() {
        const name = document.getElementById('new-overlay-name')?.value || 'New Overlay';
        const source = document.getElementById('new-overlay-image-source')?.value;
        const defaultImg = document.getElementById('new-overlay-default')?.value;
        const filePath = document.getElementById('new-overlay-file')?.value;

        this.saveUndoState();

        const newOverlay = {
            name: name,
            type: 'image',
            horizontal_align: 'center',
            vertical_align: 'top',
            horizontal_offset: 0,
            vertical_offset: 100,
            back_width: 200,
            back_height: 100
        };

        if (source === 'default' && defaultImg) {
            newOverlay.default = defaultImg;
        } else if (filePath) {
            newOverlay.file = filePath;
        }

        this.overlays.push(newOverlay);
        this.closeAddOverlayDialog();
        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
        this.selectOverlay(this.overlays.length - 1);
    },

    createTextOverlay() {
        const name = document.getElementById('new-text-name')?.value || 'Text Overlay';
        const text = document.getElementById('new-text-content')?.value || 'Sample Text';
        const font = document.getElementById('new-text-font')?.value;
        const size = parseInt(document.getElementById('new-text-size')?.value) || 50;
        const color = document.getElementById('new-text-color')?.value || '#FFFFFF';

        this.saveUndoState();

        const newOverlay = {
            name: name,
            type: 'text',
            text_content: text,
            font: font,
            font_size: size,
            font_color: color,
            horizontal_align: 'center',
            vertical_align: 'center',
            horizontal_offset: 0,
            vertical_offset: 0,
            back_width: 300,
            back_height: 80
        };

        this.overlays.push(newOverlay);
        this.closeAddOverlayDialog();
        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
        this.selectOverlay(this.overlays.length - 1);
    },

    createBackdropOverlay() {
        const name = document.getElementById('new-backdrop-name')?.value || 'Backdrop';
        const color = document.getElementById('new-backdrop-color')?.value || '#000000';
        const opacity = parseInt(document.getElementById('new-backdrop-opacity')?.value) || 70;
        const width = parseInt(document.getElementById('new-backdrop-width')?.value) || 200;
        const height = parseInt(document.getElementById('new-backdrop-height')?.value) || 60;

        // Convert hex color to rgba
        const r = parseInt(color.slice(1, 3), 16);
        const g = parseInt(color.slice(3, 5), 16);
        const b = parseInt(color.slice(5, 7), 16);
        const rgba = `rgba(${r},${g},${b},${opacity / 100})`;

        this.saveUndoState();

        const newOverlay = {
            name: name,
            type: 'backdrop',
            back_color: rgba,
            back_width: width,
            back_height: height,
            horizontal_align: 'center',
            vertical_align: 'bottom',
            horizontal_offset: 0,
            vertical_offset: 50
        };

        this.overlays.push(newOverlay);
        this.closeAddOverlayDialog();
        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
        this.selectOverlay(this.overlays.length - 1);
    },

    // Show import dialog - allows importing overlays from config
    showImportDialog() {
        if (!state.loadedOverlays || state.loadedOverlays.length === 0) {
            alert('No overlays found in config. Please load an overlay file first from the "Overlay Source" section on the Overlays page.');
            return;
        }

        // Create a simple selection dialog
        const existingDialog = document.getElementById('import-overlays-dialog');
        if (existingDialog) existingDialog.remove();

        // Get unique groups from loaded overlays
        const groups = [...new Set(state.loadedOverlays.map(o => o.group).filter(Boolean))].sort();

        const dialog = document.createElement('div');
        dialog.id = 'import-overlays-dialog';
        dialog.className = 'modal';
        dialog.innerHTML = `
            <div class="modal-content" style="max-height: 85vh; width: 700px; display: flex; flex-direction: column;">
                <div class="modal-header" style="flex-shrink: 0;">
                    <h3>Add Overlays from Config</h3>
                    <button class="btn btn-icon" onclick="document.getElementById('import-overlays-dialog').remove()" title="Close">✕</button>
                </div>
                <div style="padding: 15px; flex-shrink: 0; border-bottom: 1px solid var(--border-color);">
                    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                        <select id="import-group-filter" onchange="visualEditor.filterImportList()" style="padding: 6px 10px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-color);">
                            <option value="">All Groups (${state.loadedOverlays.length})</option>
                            ${groups.map(g => {
                                const count = state.loadedOverlays.filter(o => o.group === g).length;
                                return `<option value="${g}">${g} (${count})</option>`;
                            }).join('')}
                            <option value="__none__">No Group (${state.loadedOverlays.filter(o => !o.group).length})</option>
                        </select>
                        <input type="text" id="import-search" placeholder="Search overlays..." onkeyup="visualEditor.filterImportList()" style="padding: 6px 10px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-color); flex: 1; min-width: 150px;">
                        <button class="btn btn-small btn-secondary" onclick="visualEditor.selectAllImport(true)">Select All</button>
                        <button class="btn btn-small btn-secondary" onclick="visualEditor.selectAllImport(false)">Deselect All</button>
                    </div>
                </div>
                <div id="import-overlay-list" style="overflow-y: auto; flex: 1; padding: 15px; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px;">
                    ${this.renderImportOverlayItems(state.loadedOverlays)}
                </div>
                <div style="padding: 15px; border-top: 1px solid var(--border-color); display: flex; gap: 10px; justify-content: space-between; align-items: center; flex-shrink: 0;">
                    <span id="import-selection-count" style="color: var(--text-muted); font-size: 12px;">0 selected</span>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn btn-secondary" onclick="document.getElementById('import-overlays-dialog').remove()">Cancel</button>
                        <button class="btn btn-primary" onclick="visualEditor.importSelectedOverlays()">Add Selected</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);

        // Update selection count initially
        this.updateImportSelectionCount();
    },

    renderImportOverlayItems(overlays) {
        return overlays.map((o, i) => {
            const originalIndex = state.loadedOverlays.indexOf(o);
            const thumbnail = this.generateLayerThumbnail(o);
            const isAlreadyAdded = this.overlays.some(existing => existing.name === o.name);

            return `
                <label class="import-overlay-card ${isAlreadyAdded ? 'already-added' : ''}" data-index="${originalIndex}" data-group="${o.group || ''}" data-name="${o.name.toLowerCase()}">
                    <input type="checkbox" value="${originalIndex}" ${isAlreadyAdded ? 'disabled' : ''} onchange="visualEditor.updateImportSelectionCount()">
                    <div class="import-overlay-thumbnail">${thumbnail}</div>
                    <div class="import-overlay-info">
                        <span class="import-overlay-name" title="${o.name}">${o.name}</span>
                        <span class="import-overlay-meta">
                            <span class="import-overlay-type">${(o.type || 'image').toUpperCase()}</span>
                            ${o.group ? `<span class="import-overlay-group">${o.group}</span>` : ''}
                        </span>
                    </div>
                    ${isAlreadyAdded ? '<span class="import-overlay-badge">Added</span>' : ''}
                </label>
            `;
        }).join('');
    },

    filterImportList() {
        const groupFilter = document.getElementById('import-group-filter')?.value || '';
        const searchFilter = (document.getElementById('import-search')?.value || '').toLowerCase();
        const cards = document.querySelectorAll('.import-overlay-card');

        cards.forEach(card => {
            const group = card.dataset.group;
            const name = card.dataset.name;

            let show = true;

            // Apply group filter
            if (groupFilter) {
                if (groupFilter === '__none__') {
                    if (group) show = false;
                } else {
                    if (group !== groupFilter) show = false;
                }
            }

            // Apply search filter
            if (show && searchFilter) {
                if (!name.includes(searchFilter)) show = false;
            }

            card.style.display = show ? '' : 'none';
        });
    },

    selectAllImport(select) {
        const checkboxes = document.querySelectorAll('#import-overlay-list input[type="checkbox"]:not(:disabled)');
        checkboxes.forEach(cb => {
            // Only affect visible items
            if (cb.closest('.import-overlay-card').style.display !== 'none') {
                cb.checked = select;
            }
        });
        this.updateImportSelectionCount();
    },

    updateImportSelectionCount() {
        const checked = document.querySelectorAll('#import-overlay-list input[type="checkbox"]:checked').length;
        const countEl = document.getElementById('import-selection-count');
        if (countEl) {
            countEl.textContent = `${checked} selected`;
        }
    },

    importSelectedOverlays() {
        const checkboxes = document.querySelectorAll('#import-overlay-list input[type="checkbox"]:checked');
        const indices = Array.from(checkboxes).map(cb => parseInt(cb.value));

        if (indices.length === 0) {
            alert('Please select at least one overlay to add');
            return;
        }

        this.saveUndoState();

        // Import selected overlays
        const newOverlays = indices.map(i => JSON.parse(JSON.stringify(state.loadedOverlays[i])));

        // Add only overlays that don't exist by name
        let addedCount = 0;
        newOverlays.forEach(newOverlay => {
            if (!this.overlays.some(o => o.name === newOverlay.name)) {
                this.overlays.push(newOverlay);
                addedCount++;
            }
        });

        // Close dialog and refresh
        document.getElementById('import-overlays-dialog')?.remove();
        this.renderOverlays();
        this.renderLayersList();
        this.generateYaml();
        this.setYamlStatus('success', `Added ${addedCount} overlay${addedCount !== 1 ? 's' : ''}`);
    }
};

// Initialize visual editor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    visualEditor.init();
});

// Expose to global scope
window.visualEditor = visualEditor;

// Expose library functions to global scope for onclick handlers
window.switchLibraryTab = switchLibraryTab;
window.updateLibraryAttribute = updateLibraryAttribute;
window.updateLibrarySetting = updateLibrarySetting;
window.getLibraryIcon = getLibraryIcon;
window.toggleFileVars = toggleFileVars;
window.editFileTemplateVars = editFileTemplateVars;
window.saveFileTemplateVars = saveFileTemplateVars;
