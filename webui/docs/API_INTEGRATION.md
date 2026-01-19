# Kometa Web UI - API Integration Guide

> **Version:** 1.0
> **Created:** January 2026
> **Purpose:** Document all frontend components requiring backend API integration

This document identifies all areas of the Kometa Web UI that use simulated data, localStorage, or placeholder functionality that need to be connected to real backend APIs.

---

## Table of Contents

1. [localStorage Usage](#localstorage-usage)
2. [Existing API Endpoints](#existing-api-endpoints)
3. [Required New API Endpoints](#required-new-api-endpoints)
4. [Module-by-Module Integration Guide](#module-by-module-integration-guide)

---

## localStorage Usage

The following localStorage keys are used for client-side state persistence. These could be migrated to backend storage for cross-device sync or kept as client-side preferences.

| Key | Purpose | Location | Migration Priority |
|-----|---------|----------|-------------------|
| `kometa-wizard-completed` | Tracks if setup wizard was completed | `setupWizard` module (line ~898) | Low - UI preference |
| `kometa-profiles` | Stores configuration profiles | `profileSwitcher` module (line ~973) | **High** - Should sync to backend |
| `kometa-current-profile` | Active profile name | `profileSwitcher` module (line ~992) | **High** - Should sync to backend |
| `kometa-selected-presets` | Selected overlay presets | `overlayGallery` module (line ~1393) | Medium - Could sync |
| `kometa-run-order` | Order of run operations | `scheduling` module (line ~1862) | **High** - Config setting |
| `kometa-collections` | User-created collections | `collectionBuilder` module (line ~2090) | **High** - Should save to YAML |
| `kometa-playlists` | User-created playlists | `playlistBuilder` module (line ~2555) | **High** - Should save to YAML |
| `kometa-data-mappings` | Genre/rating/studio mappings | `dataMappers` module (line ~2887) | **High** - Should save to YAML |
| `kometa-notifications` | Enabled notification events | `notifications` module (line ~3260) | **High** - Config setting |
| `kometa-edited-metadata` | Per-item metadata edits | `metadataEditor` module (line ~3635) | **High** - Should save to YAML |
| `kometa-advanced-ops` | Enabled advanced operations | `advancedOperations` module (line ~3765) | **High** - Config setting |
| `kometa-theme` | Light/dark theme preference | `theme` module (line ~4004) | Low - UI preference |

### Recommended Backend Endpoints for localStorage Migration

```
POST /api/user/preferences     - Save UI preferences (wizard, theme)
GET  /api/user/preferences     - Load UI preferences

POST /api/profiles             - Create/update configuration profile
GET  /api/profiles             - List all profiles
DELETE /api/profiles/{name}    - Delete a profile

POST /api/collections          - Save collection definitions to YAML
GET  /api/collections          - Load existing collections

POST /api/playlists            - Save playlist definitions to YAML
GET  /api/playlists            - Load existing playlists

POST /api/settings/mappings    - Save data mappings to config
GET  /api/settings/mappings    - Load data mappings

POST /api/settings/notifications - Save notification settings
GET  /api/settings/notifications - Load notification settings

POST /api/metadata             - Save metadata edits to YAML file
GET  /api/metadata/{library}   - Load metadata for library
```

---

## Existing API Endpoints

These endpoints are already being called by the frontend. Verify they exist and function correctly.

### Configuration

| Endpoint | Method | Purpose | File Location |
|----------|--------|---------|---------------|
| `/api/config` | GET | Load current configuration | line ~4301 |
| `/api/config` | POST | Save configuration | line ~4334 |
| `/api/config/validate` | POST | Validate YAML syntax | line ~4367 |
| `/api/config/backups` | GET | List config backups | line ~4408 |
| `/api/config/backup` | POST | Create new backup | line ~615 |
| `/api/config/restore/{name}` | POST | Restore from backup | line ~4437 |

### Connection Testing

| Endpoint | Method | Purpose | File Location |
|----------|--------|---------|---------------|
| `/api/test/plex` | POST | Test Plex connection | lines ~459, 760, 3899, 5728 |
| `/api/test/tmdb` | POST | Test TMDb connection | lines ~493, 791, 3930, 5765 |
| `/api/test/{service}` | POST | Generic service test | line ~5795 |

### Media & Libraries

| Endpoint | Method | Purpose | File Location |
|----------|--------|---------|---------------|
| `/api/media/libraries` | GET | Get Plex libraries | lines ~5935, 5982 |
| `/api/media/status` | GET | Get connection status | line ~6907 |
| `/api/media/search` | GET | Search Plex/TMDb | lines ~6977, 7006 |

### Run Management

| Endpoint | Method | Purpose | File Location |
|----------|--------|---------|---------------|
| `/api/run/plan` | GET | Get run preview/plan | line ~6023 |
| `/api/run` | POST | Start dry-run | line ~6164 |
| `/api/run/apply` | POST | Start actual run | line ~6171 |
| `/api/run/stop` | POST | Stop current run | line ~6196 |
| `/api/run/status` | GET | Get run status | line ~6244 |
| `/api/runs` | GET | Get run history | line ~6348 |
| `/api/logs/{runId}` | GET | Get logs for run | line ~6381 |

### Overlays

| Endpoint | Method | Purpose | File Location |
|----------|--------|---------|---------------|
| `/api/overlays` | GET | List overlay files | line ~6417 |
| `/api/overlays/preview` | POST | Generate overlay preview | lines ~6774, 7535, 8281, 8324 |
| `/api/overlays/images` | GET | Get available images | line ~6825 |
| `/api/overlays/parse` | GET | Parse overlay file | line ~7838 |

### Health

| Endpoint | Method | Purpose | File Location |
|----------|--------|---------|---------------|
| `/api/health` | GET | Server health check | line ~7368 |

---

## Required New API Endpoints

These endpoints need to be created to replace simulated/mock functionality.

### Notifications Module (Phase 7)

**Current:** Simulates webhook tests with random success/failure (line ~3223)

```javascript
// Current simulated implementation
async testWebhook(url, event) {
    // In a real implementation, this would make an API call
    // For now, we simulate success/failure
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.1) resolve({ success: true });
            else reject(new Error('Connection timeout'));
        }, 1000);
    });
}
```

**Required Endpoint:**
```
POST /api/webhooks/test
Body: {
    "url": "https://discord.com/api/webhooks/...",
    "event": "run_start",
    "service": "discord" | "slack" | "teams" | "custom"
}
Response: {
    "success": true,
    "message": "Test notification sent",
    "response_code": 200
}
```

### Metadata Editor Module (Phase 8)

**Current:** Uses hardcoded sample movie data (line ~3366)

```javascript
// Current simulated implementation
generateSampleMedia() {
    const titles = [
        'The Matrix', 'Inception', 'Interstellar', ...
    ];
    // Returns fake media items
}
```

**Required Endpoints:**
```
GET /api/metadata/browse/{library}
Query: ?page=1&per_page=24&search=&type=movie&sort=title
Response: {
    "items": [
        {
            "id": "plex-rating-key",
            "title": "The Matrix",
            "year": 1999,
            "type": "movie",
            "poster_url": "/api/media/poster/...",
            "rating": 8.7,
            "genres": ["Action", "Sci-Fi"]
        }
    ],
    "total": 1500,
    "page": 1,
    "total_pages": 63
}

GET /api/metadata/item/{id}
Response: {
    "id": "...",
    "title": "The Matrix",
    "sort_title": "Matrix, The",
    "year": 1999,
    "content_rating": "R",
    "summary": "...",
    "genres": ["Action", "Sci-Fi"],
    "labels": [],
    "studio": "Warner Bros.",
    "tagline": "...",
    "critic_rating": 9.0,
    "audience_rating": 8.7,
    "original_title": null
}

POST /api/metadata/item/{id}
Body: {
    "title": "The Matrix",
    "sort_title": "Matrix, The",
    ...
}

POST /api/metadata/generate-yaml
Body: {
    "library": "Movies",
    "items": [
        { "id": "...", "edits": {...} }
    ]
}
Response: {
    "yaml": "metadata:\n  \"The Matrix\":\n    sort_title: ..."
}
```

### Collection Builder Module (Phase 3)

**Current:** Stores in localStorage, generates YAML client-side

**Required Endpoints:**
```
GET /api/builders/sources
Response: {
    "sources": {
        "tmdb_popular": {
            "name": "TMDb Popular",
            "category": "charts",
            "fields": [...]
        },
        ...
    }
}

POST /api/collections/save
Body: {
    "library": "Movies",
    "collection": {
        "name": "Best of 2024",
        "builders": [...],
        "filters": [...],
        "settings": {...}
    }
}

GET /api/collections/{library}
Response: {
    "collections": [...]
}

POST /api/collections/preview
Body: { collection definition }
Response: {
    "yaml": "...",
    "estimated_items": 50
}
```

### Playlist Builder Module (Phase 4)

**Similar to Collection Builder**

```
POST /api/playlists/save
GET /api/playlists
POST /api/playlists/preview
```

### Data Mappers Module (Phase 6)

**Required Endpoints:**
```
GET /api/settings/mappers
Response: {
    "genre_mapper": {...},
    "content_rating_mapper": {...},
    "studio_mapper": {...}
}

POST /api/settings/mappers
Body: {
    "genre_mapper": {
        "Sci-Fi": "Science Fiction",
        "SciFi": "Science Fiction"
    },
    ...
}
```

### Advanced Operations Module (Phase 10)

**Required Endpoints:**
```
GET /api/operations/config
Response: {
    "enabled": ["remove_title_parentheses", "assets_for_all"],
    "settings": {
        "backup_path": "/config/backups",
        ...
    }
}

POST /api/operations/config
Body: {
    "enabled": [...],
    "settings": {...}
}

POST /api/operations/preview
Body: { operations config }
Response: {
    "yaml": "operations:\n  remove_title_parentheses: true\n  ..."
}
```

### Scheduling Module (Phase 1)

**Required Endpoints:**
```
GET /api/settings/schedule
Response: {
    "run_order": ["operations", "metadata", "collections", "overlays"],
    "global_schedule": "daily",
    "library_schedules": {
        "Movies": { "schedule": "weekly(sunday)", ... }
    }
}

POST /api/settings/schedule
Body: { schedule configuration }
```

---

## Module-by-Module Integration Guide

### 1. `notifications` Module (app.js line ~3078)

**Current State:** Fully client-side with simulated webhook testing

**Integration Tasks:**
- [ ] Create `POST /api/webhooks/test` endpoint
- [ ] Update `testWebhook()` to call real API
- [ ] Add `POST /api/settings/notifications` to persist settings
- [ ] Add `GET /api/settings/notifications` to load settings on init

**Code Changes Required:**
```javascript
// Replace simulation at line ~3223
async testWebhook(url, event) {
    const response = await api.post('/webhooks/test', {
        url,
        event,
        service: this.detectService(url)
    });
    return response;
}
```

### 2. `metadataEditor` Module (app.js line ~3290)

**Current State:** Uses fake sample data, localStorage for edits

**Integration Tasks:**
- [ ] Create `GET /api/metadata/browse/{library}` endpoint
- [ ] Create `GET /api/metadata/item/{id}` endpoint
- [ ] Create `POST /api/metadata/item/{id}` endpoint
- [ ] Create `POST /api/metadata/generate-yaml` endpoint
- [ ] Replace `generateSampleMedia()` with real API call
- [ ] Add real library selector population

**Code Changes Required:**
```javascript
// Replace at line ~3361
async loadLibrary() {
    if (!this.currentLibrary) {
        this.showEmptyState();
        return;
    }

    const grid = document.getElementById('media-grid');
    grid.innerHTML = '<div class="media-grid-loading">Loading media...</div>';

    try {
        const result = await api.get(`/metadata/browse/${this.currentLibrary}?page=${this.currentPage}&per_page=${this.itemsPerPage}`);
        this.mediaItems = result.items;
        this.totalPages = result.total_pages;
        this.renderMediaGrid();
    } catch (error) {
        grid.innerHTML = `<div class="media-grid-empty"><p>Failed to load: ${error.message}</p></div>`;
    }
}
```

### 3. `collectionBuilder` Module (app.js line ~2002)

**Current State:** localStorage storage, client-side YAML generation

**Integration Tasks:**
- [ ] Create collection CRUD endpoints
- [ ] Add library-based collection file management
- [ ] Replace `loadCollections()` with API call
- [ ] Replace `saveCollections()` with API call
- [ ] Add server-side YAML file saving

### 4. `playlistBuilder` Module (app.js line ~2538)

**Current State:** localStorage storage, client-side YAML generation

**Integration Tasks:**
- [ ] Create playlist CRUD endpoints
- [ ] Replace localStorage with API calls

### 5. `dataMappers` Module (app.js line ~2803)

**Current State:** localStorage storage

**Integration Tasks:**
- [ ] Create mapper settings endpoints
- [ ] Replace localStorage with API calls
- [ ] Add preset loading from server

### 6. `advancedOperations` Module (app.js line ~3658)

**Current State:** localStorage storage, client-side YAML generation

**Integration Tasks:**
- [ ] Create operations config endpoints
- [ ] Replace localStorage with API calls

### 7. `scheduling` Module (app.js line ~1523)

**Current State:** localStorage for run order

**Integration Tasks:**
- [ ] Create schedule settings endpoints
- [ ] Replace localStorage with API calls

### 8. `profileSwitcher` Module (app.js line ~920)

**Current State:** localStorage storage

**Integration Tasks:**
- [ ] Create profile management endpoints
- [ ] Support server-side profile storage
- [ ] Add profile import/export

---

## Priority Order for Implementation

### Phase 1: Critical (Affects Core Functionality)
1. Webhook testing endpoint (`/api/webhooks/test`)
2. Metadata browsing endpoints (`/api/metadata/*`)
3. Collection save endpoint (`/api/collections/save`)

### Phase 2: High (Improves User Experience)
4. Profile management endpoints
5. Data mapper persistence
6. Notification settings persistence
7. Scheduling settings persistence

### Phase 3: Medium (Nice to Have)
8. Playlist management endpoints
9. Advanced operations persistence
10. Run order persistence

### Phase 4: Low (UI Preferences)
11. Theme persistence (can stay localStorage)
12. Wizard completion (can stay localStorage)
13. Selected presets (can stay localStorage)

---

## Testing Checklist

For each API endpoint, verify:

- [ ] Endpoint responds with correct status codes
- [ ] Error handling returns useful messages
- [ ] Authentication/authorization works correctly
- [ ] Data validation is performed
- [ ] Frontend handles success/error states
- [ ] Loading states are shown during requests
- [ ] Data persists correctly after page reload

---

## Related Documents

- [Feature Roadmap](./FEATURE_ROADMAP.md) - Implementation phases
- [Style Guide](./STYLE_GUIDE.md) - UI component patterns
- [UI/UX Audit](./UI_UX_AUDIT.md) - UI analysis
