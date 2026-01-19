# Kometa Web UI Migration Guide

## From Vanilla JavaScript to Vue 3 + TypeScript + Vite

**Document Version:** 1.0
**Target Audience:** Development Team
**Status:** Planning Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current Architecture](#current-architecture)
3. [Target Architecture](#target-architecture)
4. [Technology Decisions](#technology-decisions)
5. [Migration Phases](#migration-phases)
6. [Project Structure](#project-structure)
7. [Component Breakdown](#component-breakdown)
8. [State Management Strategy](#state-management-strategy)
9. [API Integration Patterns](#api-integration-patterns)
10. [Styling Migration](#styling-migration)
11. [Development Workflow](#development-workflow)
12. [Testing Strategy](#testing-strategy)
13. [Deployment Changes](#deployment-changes)
14. [Risk Assessment & Mitigation](#risk-assessment--mitigation)
15. [Appendices](#appendices)

---

## Executive Summary

### Objective

Migrate the Kometa Web UI from a vanilla JavaScript/Jinja2 architecture to a modern Vue 3 + TypeScript + Vite stack, improving maintainability, developer experience, and user experience while preserving all existing functionality.

### Key Benefits

| Benefit | Impact |
|---------|--------|
| **Type Safety** | Catch bugs at compile time, reduce runtime errors |
| **Component Reusability** | Build once, use everywhere |
| **Reactive State Management** | Automatic UI updates, no manual DOM manipulation |
| **Hot Module Replacement** | Instant feedback during development |
| **Better Testing** | Component-level unit tests, easier mocking |
| **Improved DX** | Better IDE support, autocomplete, refactoring tools |
| **Smaller Bundles** | Tree-shaking, code splitting, optimized builds |

### Migration Approach

**Incremental migration** - The new Vue application will be built alongside the existing code, allowing:
- Continuous deployment during migration
- Feature-by-feature migration
- Easy rollback if issues arise
- No "big bang" release

---

## Current Architecture

### Technology Stack

```
┌────────────────────────────────────────────────────────────┐
│                        Frontend                             │
├────────────────────────────────────────────────────────────┤
│  Jinja2 Templates (Server-Side Rendering)                  │
│  └── index.html (single page, ~500 lines)                  │
│                                                             │
│  Vanilla JavaScript                                         │
│  └── app.js (~1000 lines, monolithic)                      │
│  └── Manual DOM manipulation                                │
│  └── Global state object                                    │
│                                                             │
│  Pure CSS                                                   │
│  └── style.css (~2000 lines)                               │
│  └── Custom design system with CSS variables               │
├────────────────────────────────────────────────────────────┤
│                        Backend                              │
├────────────────────────────────────────────────────────────┤
│  FastAPI (Python 3.11)                                     │
│  └── REST API endpoints                                     │
│  └── WebSocket for real-time updates                       │
│  └── Static file serving                                    │
│  └── Jinja2 template rendering                             │
├────────────────────────────────────────────────────────────┤
│                        Database                             │
├────────────────────────────────────────────────────────────┤
│  SQLite (via aiosqlite)                                    │
│  └── Run history tracking                                   │
│  └── Direct SQL queries (no ORM)                           │
└────────────────────────────────────────────────────────────┘
```

### Current File Structure

```
webui/
├── backend/
│   ├── app.py                 # FastAPI application (1485 lines)
│   ├── config_manager.py      # YAML configuration handling
│   ├── run_manager.py         # Kometa execution management
│   ├── overlay_preview.py     # Overlay preview generation
│   ├── poster_fetcher.py      # Media poster fetching
│   ├── template_processor.py  # Template variable processing
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # All styles (monolithic)
│   │   └── js/
│   │       └── app.js         # All JavaScript (monolithic)
│   └── templates/
│       └── index.html         # Jinja2 template
├── Dockerfile
└── docker-compose.yml
```

### Current Pain Points

1. **No type safety** - Runtime errors from typos and incorrect data shapes
2. **Manual DOM updates** - Error-prone, verbose, hard to maintain
3. **Monolithic files** - Single 1000+ line JS file, hard to navigate
4. **Global state** - No clear data flow, side effects everywhere
5. **No component isolation** - CSS leaks, no encapsulation
6. **No build optimization** - Full files served, no tree-shaking
7. **Limited testing** - Manual testing only, no unit tests
8. **No HMR** - Full page reload on every change during development

---

## Target Architecture

### Technology Stack

```
┌────────────────────────────────────────────────────────────┐
│                        Frontend                             │
├────────────────────────────────────────────────────────────┤
│  Vue 3 (Composition API)                                   │
│  └── Single File Components (.vue)                         │
│  └── TypeScript for type safety                            │
│  └── Reactive state with automatic UI updates              │
│                                                             │
│  Vite (Build Tool)                                         │
│  └── Hot Module Replacement                                 │
│  └── TypeScript compilation                                 │
│  └── Production optimization                                │
│                                                             │
│  Pinia (UI State Management)                               │
│  └── Devtools integration                                   │
│  └── TypeScript-first design                               │
│                                                             │
│  TanStack Query (Server State)                             │
│  └── API response caching                                   │
│  └── Automatic refetching                                   │
│  └── Loading/error states                                   │
│                                                             │
│  Tailwind CSS                                              │
│  └── Utility-first styling                                 │
│  └── Design system via config                              │
│  └── Automatic purging of unused styles                    │
├────────────────────────────────────────────────────────────┤
│                        Backend                              │
├────────────────────────────────────────────────────────────┤
│  FastAPI (unchanged)                                       │
│  └── REST API endpoints                                     │
│  └── WebSocket for real-time updates                       │
│  └── Static file serving (built Vue app)                   │
│  └── Type generation for frontend                          │
├────────────────────────────────────────────────────────────┤
│                        Database                             │
├────────────────────────────────────────────────────────────┤
│  SQLite (unchanged)                                        │
│  └── Optional: SQLModel ORM                                │
│  └── Optional: Alembic migrations                          │
└────────────────────────────────────────────────────────────┘
```

### Target File Structure

```
webui/
├── backend/
│   ├── app.py
│   ├── config_manager.py
│   ├── run_manager.py
│   ├── overlay_preview.py
│   ├── poster_fetcher.py
│   ├── template_processor.py
│   ├── requirements.txt
│   └── schemas/                    # NEW: Pydantic schemas (for type generation)
│       ├── __init__.py
│       ├── config.py
│       ├── run.py
│       └── media.py
├── frontend/                       # NEW: Vue 3 application
│   ├── src/
│   │   ├── main.ts                 # Application entry point
│   │   ├── App.vue                 # Root component
│   │   ├── components/             # Reusable UI components
│   │   │   ├── common/
│   │   │   │   ├── Button.vue
│   │   │   │   ├── Card.vue
│   │   │   │   ├── Modal.vue
│   │   │   │   ├── Toast.vue
│   │   │   │   ├── Tabs.vue
│   │   │   │   └── LoadingSpinner.vue
│   │   │   ├── config/
│   │   │   │   ├── ConfigEditor.vue
│   │   │   │   ├── YamlEditor.vue
│   │   │   │   └── ConfigValidation.vue
│   │   │   ├── logs/
│   │   │   │   ├── LogViewer.vue
│   │   │   │   └── LogEntry.vue
│   │   │   ├── overlay/
│   │   │   │   ├── OverlayPreview.vue
│   │   │   │   └── OverlayControls.vue
│   │   │   ├── run/
│   │   │   │   ├── RunControls.vue
│   │   │   │   ├── RunHistory.vue
│   │   │   │   └── RunStatus.vue
│   │   │   └── media/
│   │   │       ├── MediaSearch.vue
│   │   │       └── MediaCard.vue
│   │   ├── composables/            # Reusable logic (hooks)
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useToast.ts
│   │   │   ├── useConfig.ts
│   │   │   └── useTheme.ts
│   │   ├── stores/                 # Pinia stores
│   │   │   ├── index.ts
│   │   │   ├── ui.ts               # UI state (modals, tabs, etc.)
│   │   │   ├── config.ts           # Configuration state
│   │   │   ├── run.ts              # Run execution state
│   │   │   └── logs.ts             # Log streaming state
│   │   ├── api/                    # API client layer
│   │   │   ├── client.ts           # Axios/fetch wrapper
│   │   │   ├── config.ts           # Config API calls
│   │   │   ├── run.ts              # Run API calls
│   │   │   ├── media.ts            # Media API calls
│   │   │   └── types.ts            # Auto-generated from Pydantic
│   │   ├── types/                  # TypeScript types
│   │   │   ├── index.ts
│   │   │   ├── config.ts
│   │   │   ├── run.ts
│   │   │   └── api.ts
│   │   └── assets/
│   │       └── styles/
│   │           ├── main.css        # Tailwind imports
│   │           └── variables.css   # CSS custom properties
│   ├── public/
│   │   └── favicon.ico
│   ├── index.html                  # Vite entry HTML
│   ├── vite.config.ts              # Vite configuration
│   ├── tailwind.config.js          # Tailwind configuration
│   ├── postcss.config.js           # PostCSS configuration
│   ├── tsconfig.json               # TypeScript configuration
│   ├── tsconfig.node.json          # Node TypeScript config
│   └── package.json                # Node dependencies
├── legacy/                         # OLD: Preserved for reference/rollback
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/index.html
├── docs/
│   ├── MIGRATION_GUIDE.md          # This document
│   ├── API_REFERENCE.md
│   └── COMPONENT_GUIDE.md
├── Dockerfile
└── docker-compose.yml
```

---

## Technology Decisions

### Why Vue 3 over React/Svelte?

| Criteria | Vue 3 | React | Svelte |
|----------|-------|-------|--------|
| Learning curve | Gentle | Moderate | Gentle |
| Template syntax | HTML-like (familiar) | JSX (new syntax) | HTML-like |
| Bundle size | ~33KB | ~42KB | ~2KB |
| TypeScript support | Excellent | Excellent | Good |
| Reactivity | Built-in, automatic | Manual (hooks) | Built-in |
| Ecosystem | Large | Largest | Growing |
| Two-way binding | Native (v-model) | Manual | Native |
| Migration from vanilla JS | Easiest | Moderate | Easy |

**Decision: Vue 3**
- HTML-like templates match existing Jinja2 mental model
- Built-in reactivity eliminates manual state management
- Excellent TypeScript integration
- Composition API allows gradual adoption
- `v-model` simplifies form handling (critical for config editor)

### Why Vite over Webpack?

| Criteria | Vite | Webpack |
|----------|------|---------|
| Dev server startup | <1 second | 10-30 seconds |
| HMR speed | Instant | 1-5 seconds |
| Configuration | Minimal | Complex |
| Build speed | Fast (esbuild) | Slower |
| Vue integration | First-class | Plugin required |

**Decision: Vite**
- Created by Vue author, perfect integration
- Near-instant development feedback
- Minimal configuration required
- Modern ES modules approach

### Why Tailwind CSS?

| Criteria | Tailwind | CSS Modules | Styled Components |
|----------|----------|-------------|-------------------|
| Learning curve | Moderate | Low | Moderate |
| Bundle size | Small (purged) | Minimal | Runtime overhead |
| Design consistency | Excellent | Manual | Manual |
| Responsive design | Built-in | Manual | Manual |
| Dark mode | Built-in | Manual | Manual |

**Decision: Tailwind CSS**
- Existing design tokens translate directly to Tailwind config
- Utility classes match component-based architecture
- Built-in responsive and dark mode support
- Automatic removal of unused styles

### Why Pinia + TanStack Query?

**Pinia** (UI State):
- Official Vue state management
- TypeScript-first design
- Vue Devtools integration
- Simple, intuitive API

**TanStack Query** (Server State):
- Automatic caching and invalidation
- Loading/error state management
- Background refetching
- WebSocket subscription support
- Reduces boilerplate for API calls

**Decision: Both**
- Pinia for client-only state (UI, preferences)
- TanStack Query for server state (config, runs, history)
- Clear separation of concerns

---

## Migration Phases

### Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Migration Timeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4       │
│  Setup      Core        Features    Polish      Cleanup         │
│                                                                  │
│  [Parallel development - existing UI remains functional]        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 0: Project Setup & Infrastructure

**Objective:** Establish the new frontend project structure alongside existing code.

#### Tasks

- [ ] **0.1** Initialize Vue 3 + Vite project in `frontend/` directory
- [ ] **0.2** Configure TypeScript with strict mode
- [ ] **0.3** Set up Tailwind CSS with existing design tokens
- [ ] **0.4** Configure Pinia and TanStack Query
- [ ] **0.5** Set up ESLint + Prettier for code consistency
- [ ] **0.6** Configure Vite proxy for API calls during development
- [ ] **0.7** Update Dockerfile for frontend build step
- [ ] **0.8** Set up type generation from Pydantic models
- [ ] **0.9** Create base component library (Button, Card, Modal, etc.)
- [ ] **0.10** Establish testing infrastructure (Vitest + Vue Test Utils)

#### Deliverables

1. Working Vue 3 development environment
2. Tailwind configured with Kometa design tokens
3. Type definitions generated from backend
4. Base component library
5. Updated Docker build process

#### Definition of Done

- `npm run dev` starts development server
- `npm run build` produces production build
- Base components render correctly
- API proxy connects to FastAPI backend
- Types match backend schemas

---

### Phase 1: Core Infrastructure & Layout

**Objective:** Build the application shell and core functionality.

#### Tasks

- [ ] **1.1** Create App.vue with main layout structure
- [ ] **1.2** Implement tab navigation system
- [ ] **1.3** Build Toast notification system
- [ ] **1.4** Create WebSocket composable for real-time updates
- [ ] **1.5** Implement API client with error handling
- [ ] **1.6** Set up Pinia stores (UI, config, run, logs)
- [ ] **1.7** Build responsive sidebar/navigation
- [ ] **1.8** Implement theme switching (dark/light mode)
- [ ] **1.9** Create loading states and skeleton components

#### Component Mapping

| Current (app.js) | New (Vue) |
|------------------|-----------|
| `initTabs()` | `<TabGroup>` component |
| `showToast()` | `useToast()` composable |
| `connectWebSocket()` | `useWebSocket()` composable |
| `state` object | Pinia stores |
| Manual DOM updates | Vue reactivity |

#### Deliverables

1. Functional application shell
2. Tab-based navigation
3. Toast notification system
4. WebSocket integration
5. Theme switching

#### Definition of Done

- Application renders with all tabs
- Toast notifications work
- WebSocket connects and receives updates
- Theme toggle works
- No console errors

---

### Phase 2: Feature Migration

**Objective:** Migrate all features from vanilla JS to Vue components.

#### Phase 2a: Configuration Editor

- [ ] **2a.1** Build YAML editor component with syntax highlighting
- [ ] **2a.2** Implement configuration validation display
- [ ] **2a.3** Create backup/restore functionality
- [ ] **2a.4** Build library configuration panels
- [ ] **2a.5** Implement save with confirmation

#### Phase 2b: Run Controls & Status

- [ ] **2b.1** Build run control panel (dry run, apply)
- [ ] **2b.2** Implement run options (libraries, collections, operations)
- [ ] **2b.3** Create real-time status display
- [ ] **2b.4** Build run history table with filtering
- [ ] **2b.5** Implement log viewer with live streaming

#### Phase 2c: Media & Overlays

- [ ] **2c.1** Build media search interface
- [ ] **2c.2** Create media card component
- [ ] **2c.3** Implement overlay preview system
- [ ] **2c.4** Build overlay configuration panel

#### Phase 2d: Settings & Connections

- [ ] **2d.1** Build connection testing interface
- [ ] **2d.2** Create settings management panel
- [ ] **2d.3** Implement password/authentication handling
- [ ] **2d.4** Build about/info section

#### Feature Parity Checklist

| Feature | Status | Component |
|---------|--------|-----------|
| Config viewing/editing | ⬜ | `ConfigEditor.vue` |
| Config validation | ⬜ | `ConfigValidation.vue` |
| Config backup/restore | ⬜ | `ConfigBackup.vue` |
| Dry run execution | ⬜ | `RunControls.vue` |
| Apply run execution | ⬜ | `RunControls.vue` |
| Run filtering (libraries) | ⬜ | `RunOptions.vue` |
| Run filtering (collections) | ⬜ | `RunOptions.vue` |
| Run status display | ⬜ | `RunStatus.vue` |
| Run history | ⬜ | `RunHistory.vue` |
| Live log streaming | ⬜ | `LogViewer.vue` |
| Media search | ⬜ | `MediaSearch.vue` |
| Overlay preview | ⬜ | `OverlayPreview.vue` |
| Connection testing | ⬜ | `ConnectionTest.vue` |
| Settings management | ⬜ | `Settings.vue` |
| Toast notifications | ⬜ | `Toast.vue` |
| Dark/light theme | ⬜ | Theme composable |

#### Deliverables

1. All features migrated to Vue components
2. Feature parity with existing UI
3. Improved UX where applicable

#### Definition of Done

- All checklist items marked complete
- No functionality regression
- All API endpoints integrated
- WebSocket features working

---

### Phase 3: Polish & Enhancement

**Objective:** Improve UX, accessibility, and performance.

#### Tasks

- [ ] **3.1** Implement keyboard navigation
- [ ] **3.2** Add ARIA labels and screen reader support
- [ ] **3.3** Optimize bundle size (code splitting)
- [ ] **3.4** Add loading skeletons for better perceived performance
- [ ] **3.5** Implement error boundaries
- [ ] **3.6** Add form validation with user-friendly messages
- [ ] **3.7** Implement undo/redo for config changes
- [ ] **3.8** Add confirmation dialogs for destructive actions
- [ ] **3.9** Performance profiling and optimization
- [ ] **3.10** Cross-browser testing

#### Deliverables

1. Accessible, keyboard-navigable UI
2. Optimized bundle size
3. Enhanced user experience
4. Comprehensive error handling

---

### Phase 4: Cleanup & Documentation

**Objective:** Remove legacy code and finalize documentation.

#### Tasks

- [ ] **4.1** Remove legacy JavaScript and CSS files
- [ ] **4.2** Update backend to serve Vue build only
- [ ] **4.3** Remove Jinja2 template dependencies
- [ ] **4.4** Update all documentation
- [ ] **4.5** Create component storybook/documentation
- [ ] **4.6** Write migration retrospective

#### Deliverables

1. Clean codebase with no legacy code
2. Updated documentation
3. Component documentation

---

## Component Breakdown

### Component Hierarchy

```
App.vue
├── TheHeader.vue
│   ├── Logo.vue
│   ├── ThemeToggle.vue
│   └── StatusIndicator.vue
├── TheSidebar.vue
│   └── NavItem.vue
├── MainContent.vue
│   ├── TabGroup.vue
│   │   └── TabPanel.vue
│   ├── ConfigTab/
│   │   ├── ConfigEditor.vue
│   │   │   ├── YamlEditor.vue
│   │   │   └── ConfigActions.vue
│   │   ├── ConfigValidation.vue
│   │   └── ConfigBackup.vue
│   ├── RunTab/
│   │   ├── RunControls.vue
│   │   │   ├── RunModeSelector.vue
│   │   │   ├── LibrarySelector.vue
│   │   │   ├── CollectionSelector.vue
│   │   │   └── OperationSelector.vue
│   │   ├── RunStatus.vue
│   │   └── RunHistory.vue
│   │       └── RunHistoryRow.vue
│   ├── LogsTab/
│   │   └── LogViewer.vue
│   │       ├── LogControls.vue
│   │       └── LogEntry.vue
│   ├── MediaTab/
│   │   ├── MediaSearch.vue
│   │   └── MediaGrid.vue
│   │       └── MediaCard.vue
│   ├── OverlayTab/
│   │   ├── OverlayPreview.vue
│   │   └── OverlayControls.vue
│   └── SettingsTab/
│       ├── ConnectionTest.vue
│       └── SettingsForm.vue
├── ToastContainer.vue
│   └── Toast.vue
└── ModalContainer.vue
    └── Modal.vue
```

### Component Specifications

#### Common Components

```typescript
// Button.vue
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: string;
}

// Card.vue
interface CardProps {
  title?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
}

// Modal.vue
interface ModalProps {
  open: boolean;
  title: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnOverlay?: boolean;
}

// Toast.vue
interface ToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  dismissible?: boolean;
}
```

#### Feature Components

```typescript
// ConfigEditor.vue
interface ConfigEditorProps {
  readonly?: boolean;
}
interface ConfigEditorEmits {
  (e: 'save', config: string): void;
  (e: 'validate'): void;
}

// RunControls.vue
interface RunControlsProps {
  applyEnabled: boolean;
  isRunning: boolean;
}
interface RunControlsEmits {
  (e: 'start', options: RunOptions): void;
  (e: 'stop'): void;
}

// LogViewer.vue
interface LogViewerProps {
  autoScroll?: boolean;
  maxLines?: number;
}
```

---

## State Management Strategy

### Store Structure

```typescript
// stores/ui.ts - UI-only state
interface UIState {
  activeTab: string;
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  modals: {
    confirm: { open: boolean; message: string; onConfirm: () => void };
    backup: { open: boolean };
  };
}

// stores/config.ts - Configuration state
interface ConfigState {
  raw: string;           // Raw YAML content
  parsed: object | null; // Parsed configuration
  validation: ValidationResult[];
  isDirty: boolean;
  lastSaved: Date | null;
}

// stores/run.ts - Run execution state
interface RunState {
  isRunning: boolean;
  currentRun: Run | null;
  progress: number;
  options: RunOptions;
}

// stores/logs.ts - Log streaming state
interface LogsState {
  entries: LogEntry[];
  connected: boolean;
  autoScroll: boolean;
  filter: string;
}
```

### TanStack Query Keys

```typescript
// api/queryKeys.ts
export const queryKeys = {
  config: {
    all: ['config'] as const,
    detail: () => [...queryKeys.config.all, 'detail'] as const,
    validation: () => [...queryKeys.config.all, 'validation'] as const,
    backups: () => [...queryKeys.config.all, 'backups'] as const,
  },
  runs: {
    all: ['runs'] as const,
    list: (filters: RunFilters) => [...queryKeys.runs.all, 'list', filters] as const,
    detail: (id: string) => [...queryKeys.runs.all, 'detail', id] as const,
  },
  media: {
    all: ['media'] as const,
    search: (query: string) => [...queryKeys.media.all, 'search', query] as const,
  },
  connections: {
    all: ['connections'] as const,
    test: (type: string) => [...queryKeys.connections.all, 'test', type] as const,
  },
};
```

---

## API Integration Patterns

### API Client Setup

```typescript
// api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const password = localStorage.getItem('kometa_password');
  if (password) {
    config.headers['X-Password'] = password;
  }
  return config;
});

// Response interceptor for errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const toast = useToast();
    if (error.response?.status === 401) {
      toast.error('Authentication required');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again.');
    }
    return Promise.reject(error);
  }
);
```

### Query Examples

```typescript
// api/config.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query';
import { apiClient } from './client';
import { queryKeys } from './queryKeys';

export function useConfig() {
  return useQuery({
    queryKey: queryKeys.config.detail(),
    queryFn: async () => {
      const { data } = await apiClient.get('/config');
      return data;
    },
  });
}

export function useSaveConfig() {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: async (config: string) => {
      const { data } = await apiClient.put('/config', { content: config });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.config.all });
      toast.success('Configuration saved');
    },
    onError: (error) => {
      toast.error(`Failed to save: ${error.message}`);
    },
  });
}
```

### WebSocket Integration

```typescript
// composables/useWebSocket.ts
import { ref, onMounted, onUnmounted } from 'vue';

export function useWebSocket(endpoint: string) {
  const socket = ref<WebSocket | null>(null);
  const connected = ref(false);
  const messages = ref<any[]>([]);

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}${endpoint}`;

    socket.value = new WebSocket(url);

    socket.value.onopen = () => {
      connected.value = true;
    };

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      messages.value.push(data);
    };

    socket.value.onclose = () => {
      connected.value = false;
      // Reconnect after delay
      setTimeout(connect, 3000);
    };
  };

  onMounted(connect);
  onUnmounted(() => socket.value?.close());

  return { connected, messages };
}
```

---

## Styling Migration

### Tailwind Configuration

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Kometa brand colors (from existing CSS variables)
        kometa: {
          gold: '#e5a00d',
          'gold-light': '#f5c842',
          'gold-dark': '#c4870a',
        },
        // Semantic colors
        surface: {
          DEFAULT: 'var(--surface-primary)',
          secondary: 'var(--surface-secondary)',
          tertiary: 'var(--surface-tertiary)',
        },
        border: {
          DEFAULT: 'var(--border-primary)',
          secondary: 'var(--border-secondary)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        // Match existing design system
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
      },
      spacing: {
        // 4pt grid system
        '0.5': '2px',
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
      },
      borderRadius: {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
        'glow': '0 0 20px rgba(229, 160, 13, 0.3)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### CSS Variable Bridge

```css
/* src/assets/styles/variables.css */
:root {
  /* Surface colors - Light theme */
  --surface-primary: #ffffff;
  --surface-secondary: #f8f9fa;
  --surface-tertiary: #f1f3f4;

  /* Border colors */
  --border-primary: #e0e0e0;
  --border-secondary: #eeeeee;

  /* Text colors */
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --text-tertiary: #999999;
}

.dark {
  /* Surface colors - Dark theme */
  --surface-primary: #1a1a1a;
  --surface-secondary: #242424;
  --surface-tertiary: #2d2d2d;

  /* Border colors */
  --border-primary: #333333;
  --border-secondary: #404040;

  /* Text colors */
  --text-primary: #ffffff;
  --text-secondary: #b3b3b3;
  --text-tertiary: #808080;
}
```

### Component Style Example

```vue
<!-- Before: Vanilla CSS -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">Content</div>
</div>

<!-- After: Tailwind -->
<div class="bg-surface rounded-lg border border-border shadow-sm">
  <div class="px-4 py-3 border-b border-border">
    <h3 class="text-lg font-semibold text-text-primary">Title</h3>
  </div>
  <div class="p-4">Content</div>
</div>
```

---

## Development Workflow

### Local Development

```bash
# Terminal 1: Backend
cd webui/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app:app --reload --port 8000

# Terminal 2: Frontend
cd webui/frontend
npm install
npm run dev  # Starts Vite dev server on port 5173
```

### Vite Proxy Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});
```

### Scripts

```json
// package.json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext .vue,.js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .vue,.js,.jsx,.ts,.tsx --fix",
    "format": "prettier --write src/",
    "type-check": "vue-tsc --noEmit",
    "generate-types": "python ../backend/scripts/generate_types.py"
  }
}
```

### Git Workflow

```bash
# Feature branch naming
git checkout -b feature/vue-migration-phase-1
git checkout -b feature/component-config-editor
git checkout -b fix/websocket-reconnection

# Commit message format
feat(config): add YAML syntax highlighting
fix(logs): resolve WebSocket reconnection issue
refactor(api): extract common error handling
test(run): add unit tests for RunControls
docs(readme): update development setup instructions
```

---

## Testing Strategy

### Test Structure

```
frontend/
├── src/
│   └── components/
│       └── Button.vue
├── tests/
│   ├── unit/
│   │   └── components/
│   │       └── Button.spec.ts
│   ├── integration/
│   │   └── ConfigEditor.spec.ts
│   └── e2e/
│       └── run-workflow.spec.ts
└── vitest.config.ts
```

### Unit Test Example

```typescript
// tests/unit/components/Button.spec.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Button from '@/components/common/Button.vue';

describe('Button', () => {
  it('renders with correct text', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Click me',
      },
    });
    expect(wrapper.text()).toBe('Click me');
  });

  it('emits click event', async () => {
    const wrapper = mount(Button);
    await wrapper.trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });

  it('is disabled when loading', () => {
    const wrapper = mount(Button, {
      props: { loading: true },
    });
    expect(wrapper.attributes('disabled')).toBeDefined();
  });

  it('applies variant classes', () => {
    const wrapper = mount(Button, {
      props: { variant: 'primary' },
    });
    expect(wrapper.classes()).toContain('bg-kometa-gold');
  });
});
```

### Integration Test Example

```typescript
// tests/integration/ConfigEditor.spec.ts
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import ConfigEditor from '@/components/config/ConfigEditor.vue';

describe('ConfigEditor', () => {
  it('loads and displays configuration', async () => {
    const wrapper = mount(ConfigEditor, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              config: {
                raw: 'libraries:\n  Movies:\n    plex: Movies',
              },
            },
          }),
        ],
      },
    });

    expect(wrapper.text()).toContain('libraries');
  });

  it('shows validation errors', async () => {
    const wrapper = mount(ConfigEditor, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              config: {
                validation: [{ level: 'error', message: 'Invalid YAML' }],
              },
            },
          }),
        ],
      },
    });

    expect(wrapper.find('.validation-error').exists()).toBe(true);
  });
});
```

### Test Coverage Goals

| Category | Target |
|----------|--------|
| Unit Tests | 80% |
| Integration Tests | Key workflows |
| E2E Tests | Critical paths |

---

## Deployment Changes

### Updated Dockerfile

```dockerfile
# Dockerfile
# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Build frontend
COPY frontend/ ./
RUN npm run build

# Stage 2: Build final image
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy Kometa requirements
COPY kometa-requirements.txt ./
RUN pip install --no-cache-dir -r kometa-requirements.txt

# Environment variables
ENV KOMETA_CONFIG_DIR=/config
ENV KOMETA_ROOT=/kometa
ENV KOMETA_UI_PORT=8080
ENV KOMETA_UI_HOST=0.0.0.0

EXPOSE 8080

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Updated FastAPI Static Serving

```python
# backend/app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

# API routes
app.include_router(api_router, prefix="/api")

# Serve Vue build
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_path.exists():
    app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve Vue SPA for all non-API routes"""
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_path / "index.html")
```

---

## Risk Assessment & Mitigation

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Learning curve slows development | Medium | Medium | Provide Vue 3 training resources, pair programming |
| Feature regression during migration | Medium | High | Comprehensive testing, feature flags, parallel deployment |
| Performance degradation | Low | Medium | Performance benchmarks, bundle analysis |
| Browser compatibility issues | Low | Low | Browserslist config, polyfills if needed |
| WebSocket migration issues | Medium | Medium | Thorough testing, connection monitoring |
| Build/deploy complexity | Low | Medium | CI/CD updates, Docker multi-stage builds |

### Rollback Plan

1. **During Migration (Phases 0-2)**
   - Legacy UI remains fully functional
   - Toggle between old/new UI via environment variable
   - No impact to users if Vue UI has issues

2. **After Migration (Phases 3-4)**
   - Legacy code preserved in `/legacy` directory
   - Can restore with single Dockerfile change
   - Database schema unchanged, no data migration needed

3. **Rollback Steps**
   ```bash
   # Immediate rollback
   docker-compose down
   git checkout main -- webui/Dockerfile
   docker-compose up -d --build
   ```

---

## Appendices

### Appendix A: Package.json Template

```json
{
  "name": "kometa-webui",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint . --ext .vue,.js,.jsx,.ts,.tsx",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "@tanstack/vue-query": "^5.17.0",
    "pinia": "^2.1.7",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "@vue/test-utils": "^2.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.1.0",
    "vue-tsc": "^1.8.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "@tailwindcss/forms": "^0.5.0",
    "@tailwindcss/typography": "^0.5.0",
    "eslint": "^8.56.0",
    "eslint-plugin-vue": "^9.19.0",
    "@typescript-eslint/eslint-plugin": "^6.16.0",
    "@typescript-eslint/parser": "^6.16.0",
    "prettier": "^3.1.0"
  }
}
```

### Appendix B: TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### Appendix C: ESLint Configuration

```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: ['vue', '@typescript-eslint'],
  rules: {
    'vue/multi-word-component-names': 'off',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
};
```

### Appendix D: Resources

#### Learning Resources
- [Vue 3 Documentation](https://vuejs.org/guide/introduction.html)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [TypeScript with Vue](https://vuejs.org/guide/typescript/overview.html)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [TanStack Query Vue](https://tanstack.com/query/latest/docs/vue/overview)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vite Documentation](https://vitejs.dev/guide/)

#### Reference Projects
- [Vue 3 Enterprise Boilerplate](https://github.com/chrisvfritz/vue-enterprise-boilerplate)
- [Vitesse - Opinionated Vue Starter](https://github.com/antfu/vitesse)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-XX-XX | Development Team | Initial draft |

---

**Questions or Feedback?**

Contact the development team for clarification on any section of this guide.
