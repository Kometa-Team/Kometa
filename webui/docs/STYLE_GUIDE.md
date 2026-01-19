# Kometa Web UI - Design System Style Guide

> **Version:** 2.0
> **Last Updated:** January 2026
> **Status:** Complete Reference Document

This style guide defines the visual language, components, and patterns for the Kometa Web UI. All new features and modifications should follow these guidelines to ensure consistency.

---

## Table of Contents

1. [Design Principles](#1-design-principles)
2. [Spacing System](#2-spacing-system)
3. [Color System](#3-color-system)
4. [Typography](#4-typography)
5. [Border & Shadows](#5-borders--shadows)
6. [Buttons](#6-buttons)
7. [Form Controls](#7-form-controls)
8. [Cards & Containers](#8-cards--containers)
9. [Navigation](#9-navigation)
10. [Feedback & States](#10-feedback--states)
11. [Icons](#11-icons)
12. [Layout Patterns](#12-layout-patterns)
13. [Utility Classes](#13-utility-classes)
14. [Component Patterns](#14-component-patterns)
15. [Accessibility](#15-accessibility)
16. [Dashboard Components](#16-dashboard-components)
17. [Setup Wizard](#17-setup-wizard)
18. [Profile Switcher](#18-profile-switcher)
19. [Overlay Gallery](#19-overlay-gallery)
20. [Pre-flight Checklist](#20-pre-flight-checklist)
21. [YAML Preview Panel](#21-yaml-preview-panel)
22. [Keyboard Shortcuts](#22-keyboard-shortcuts)
23. [Animations](#23-animations)

---

## 1. Design Principles

### Core Values

1. **Clarity over cleverness** - Technical users need to understand what's happening
2. **Density with hierarchy** - Show relevant information without overwhelming
3. **Responsive feedback** - Every action should have visible confirmation
4. **Progressive disclosure** - Show essentials first, reveal advanced options on demand
5. **Consistency** - Same patterns for same behaviors across the UI

### Target Users

- Homelab enthusiasts running Plex
- Technical users comfortable with YAML configuration
- Users who value control and transparency over magic

### Anti-Patterns to Avoid

- Excessive animations or transitions (keep under 200ms)
- Hidden functionality without clear affordances
- Color-only status indicators (always pair with text/icon)
- Inline styles in HTML (use classes)
- Magic numbers in CSS (use variables)

---

## 2. Spacing System

Use a **4-point grid** for all spacing. This creates visual rhythm and consistency.

### Spacing Scale

```css
:root {
  /* Spacing tokens - 4pt grid */
  --space-0: 0;
  --space-1: 4px;    /* Tight: icon gaps, inline elements */
  --space-2: 8px;    /* Compact: input padding, small gaps */
  --space-3: 12px;   /* Default: form group spacing */
  --space-4: 16px;   /* Comfortable: card padding, section gaps */
  --space-5: 24px;   /* Spacious: section margins */
  --space-6: 32px;   /* Large: major section dividers */
  --space-8: 48px;   /* Extra large: page sections */
  --space-10: 64px;  /* Maximum: page margins */
}
```

### Usage Guidelines

| Context | Spacing Token | Pixels |
|---------|---------------|--------|
| Icon to text gap | `--space-1` | 4px |
| Input internal padding | `--space-2` | 8px |
| Form field to label | `--space-1` | 4px |
| Between form fields | `--space-3` | 12px |
| Card internal padding | `--space-4` to `--space-5` | 16-24px |
| Between cards | `--space-4` | 16px |
| Section margins | `--space-6` | 32px |
| Page top/bottom padding | `--space-8` | 48px |

### Examples

```css
/* Good - uses spacing tokens */
.form-group {
  margin-bottom: var(--space-3);
}

.card {
  padding: var(--space-5);
  margin-bottom: var(--space-4);
}

/* Bad - magic numbers */
.form-group {
  margin-bottom: 15px;
}

.card {
  padding: 22px;
}
```

---

## 3. Color System

### Base Palette

```css
:root {
  /* Brand */
  --color-primary: #e5a00d;        /* Kometa Gold - primary actions */
  --color-primary-hover: #f0b020;  /* Gold hover state */
  --color-primary-active: #cc8f0c; /* Gold active/pressed state */

  /* Backgrounds (dark theme - default) */
  --bg-base: #0d0d1a;              /* Deepest - code editors */
  --bg-primary: #1a1a2e;           /* Main app background */
  --bg-secondary: #16213e;         /* Cards, panels, elevated surfaces */
  --bg-tertiary: #0f3460;          /* Inputs, nested containers */
  --bg-elevated: #1e3a5f;          /* Hover states, active items */

  /* Borders */
  --border-default: #2a2a4e;       /* Default borders */
  --border-subtle: #1f1f3a;        /* Subtle dividers */
  --border-strong: #3a3a6e;        /* Emphasized borders */

  /* Text */
  --text-primary: #f0f0f0;         /* Headlines, primary content */
  --text-secondary: #b0b0b0;       /* Labels, descriptions */
  --text-muted: #707070;           /* Placeholders, disabled text */
  --text-inverse: #0d0d1a;         /* Text on light backgrounds */

  /* Semantic Colors */
  --color-success: #22c55e;        /* Success states, connected */
  --color-success-bg: rgba(34, 197, 94, 0.1);
  --color-warning: #f59e0b;        /* Warnings, attention needed */
  --color-warning-bg: rgba(245, 158, 11, 0.1);
  --color-error: #ef4444;          /* Errors, destructive actions */
  --color-error-bg: rgba(239, 68, 68, 0.1);
  --color-info: #3b82f6;           /* Informational, links */
  --color-info-bg: rgba(59, 130, 246, 0.1);
}
```

### Color Usage Rules

| Purpose | Color Token | Example |
|---------|-------------|---------|
| Primary CTA buttons | `--color-primary` | Save, Run, Apply |
| Links | `--color-info` | Documentation links |
| Success feedback | `--color-success` | "Connected", "Saved" |
| Warning messages | `--color-warning` | "Apply mode enabled" |
| Error states | `--color-error` | Validation errors |
| Destructive buttons | `--color-error` | Delete, Remove |
| Card backgrounds | `--bg-secondary` | Service cards |
| Input backgrounds | `--bg-tertiary` | Text inputs |

### Safety Mode Colors

```css
:root {
  /* Safety banner states */
  --safety-safe-bg: rgba(34, 197, 94, 0.15);
  --safety-safe-border: var(--color-success);
  --safety-safe-text: #4ade80;

  --safety-armed-bg: rgba(239, 68, 68, 0.15);
  --safety-armed-border: var(--color-error);
  --safety-armed-text: #f87171;
}
```

---

## 4. Typography

### Font Stack

```css
:root {
  /* Font families */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
               'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'SF Mono', 'Fira Code', 'Consolas', 'Monaco',
               'Andale Mono', monospace;
}
```

### Type Scale

```css
:root {
  /* Font sizes */
  --text-xs: 11px;    /* Badges, captions */
  --text-sm: 13px;    /* Helper text, metadata */
  --text-base: 14px;  /* Body text, form labels */
  --text-md: 16px;    /* Card titles, subtab labels */
  --text-lg: 18px;    /* Section headers */
  --text-xl: 24px;    /* Page titles */
  --text-2xl: 32px;   /* Hero titles (rarely used) */

  /* Font weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Typography Hierarchy

| Element | Size | Weight | Line Height | Color |
|---------|------|--------|-------------|-------|
| Page title (h1/h2) | `--text-xl` | `--font-semibold` | `--leading-tight` | `--text-primary` |
| Section header (h3) | `--text-lg` | `--font-semibold` | `--leading-tight` | `--text-primary` |
| Card title (h4) | `--text-md` | `--font-medium` | `--leading-normal` | `--text-primary` |
| Form label | `--text-base` | `--font-medium` | `--leading-normal` | `--text-secondary` |
| Body text | `--text-base` | `--font-normal` | `--leading-normal` | `--text-primary` |
| Helper text | `--text-sm` | `--font-normal` | `--leading-normal` | `--text-muted` |
| Badge text | `--text-xs` | `--font-medium` | `--leading-tight` | varies |
| Code/monospace | `--text-sm` | `--font-normal` | `--leading-relaxed` | `--text-primary` |

### CSS Examples

```css
.page-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  color: var(--text-primary);
  margin-bottom: var(--space-4);
}

.section-header {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-3);
}

.field-label {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  margin-bottom: var(--space-1);
}

.field-help {
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-top: var(--space-1);
}
```

---

## 5. Borders & Shadows

### Border Radius

```css
:root {
  --radius-sm: 4px;      /* Inputs, small buttons, badges */
  --radius-md: 8px;      /* Cards, modals, panels */
  --radius-lg: 12px;     /* Large cards, hero sections */
  --radius-xl: 16px;     /* Dialogs, floating panels */
  --radius-full: 9999px; /* Pills, circular buttons, avatars */
}
```

### Shadows

```css
:root {
  /* Elevation shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.25);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.4);

  /* Inset shadows */
  --shadow-inset: inset 0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-inset-lg: inset 0 2px 4px rgba(0, 0, 0, 0.3);

  /* Focus ring */
  --shadow-focus: 0 0 0 3px rgba(229, 160, 13, 0.3);
  --shadow-focus-error: 0 0 0 3px rgba(239, 68, 68, 0.3);
}
```

### Usage

| Component | Border Radius | Shadow |
|-----------|---------------|--------|
| Text input | `--radius-sm` | none (border only) |
| Button | `--radius-sm` | `--shadow-sm` |
| Card | `--radius-md` | `--shadow-sm` |
| Card (hover) | `--radius-md` | `--shadow-md` |
| Modal | `--radius-lg` | `--shadow-xl` |
| Badge/pill | `--radius-full` | none |
| Dropdown | `--radius-md` | `--shadow-lg` |

---

## 6. Buttons

### Button Variants

```css
/* Base button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: 1;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 150ms ease;
  min-height: 36px;
}

/* Primary - Main actions */
.btn-primary {
  background: var(--color-primary);
  color: var(--text-inverse);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn-primary:active {
  background: var(--color-primary-active);
  transform: translateY(1px);
}

/* Secondary - Supporting actions */
.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--border-default);
}

.btn-secondary:hover {
  background: var(--bg-elevated);
  border-color: var(--border-strong);
}

/* Ghost - Tertiary actions */
.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border-color: transparent;
}

.btn-ghost:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* Destructive - Dangerous actions */
.btn-destructive {
  background: var(--color-error);
  color: white;
  border-color: var(--color-error);
}

.btn-destructive:hover {
  background: #dc2626;
}
```

### Button Sizes

```css
.btn-sm {
  min-height: 28px;
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-sm);
}

.btn-md {
  min-height: 36px;
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
}

.btn-lg {
  min-height: 44px;
  padding: var(--space-3) var(--space-5);
  font-size: var(--text-md);
}
```

### Button States

```css
.btn:disabled,
.btn[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus);
}

.btn.loading {
  position: relative;
  color: transparent;
}

.btn.loading::after {
  content: "";
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
```

### Button Usage

| Action Type | Variant | Example |
|-------------|---------|---------|
| Primary CTA | `.btn-primary` | Save, Run, Apply |
| Secondary action | `.btn-secondary` | Test Connection, Reload |
| Tertiary/cancel | `.btn-ghost` | Cancel, Clear, Skip |
| Destructive | `.btn-destructive` | Delete, Remove |
| Icon-only | `.btn-ghost.btn-icon` | Close (X), Settings gear |

---

## 7. Form Controls

### Text Input

```css
.form-input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-base);
  font-family: var(--font-sans);
  color: var(--text-primary);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  transition: border-color 150ms ease, box-shadow 150ms ease;
  min-height: 40px;
}

.form-input:hover {
  border-color: var(--border-strong);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: var(--shadow-focus);
}

.form-input::placeholder {
  color: var(--text-muted);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--bg-secondary);
}
```

### Select

```css
.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,..."); /* Chevron icon */
  background-repeat: no-repeat;
  background-position: right var(--space-3) center;
  padding-right: var(--space-8);
}
```

### Checkbox

```css
.form-checkbox {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  cursor: pointer;
}

.form-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin: 0;
  accent-color: var(--color-primary);
  cursor: pointer;
}

.form-checkbox-label {
  font-size: var(--text-base);
  color: var(--text-primary);
  user-select: none;
}

.form-checkbox-description {
  font-size: var(--text-sm);
  color: var(--text-muted);
  margin-top: var(--space-1);
}
```

### Form Group

```css
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
}

.form-label .required {
  color: var(--color-error);
}

.form-hint {
  font-size: var(--text-sm);
  color: var(--text-muted);
}

.form-error {
  font-size: var(--text-sm);
  color: var(--color-error);
}
```

### Form Row

```css
.form-row {
  display: flex;
  gap: var(--space-4);
}

.form-row > .form-group {
  flex: 1;
}

.form-row > .form-group.flex-2 {
  flex: 2;
}

@media (max-width: 640px) {
  .form-row {
    flex-direction: column;
  }
}
```

### Validation States

```css
.form-group.has-error .form-input {
  border-color: var(--color-error);
  background: var(--color-error-bg);
}

.form-group.has-error .form-input:focus {
  box-shadow: var(--shadow-focus-error);
}

.form-group.has-success .form-input {
  border-color: var(--color-success);
}
```

---

## 8. Cards & Containers

### Base Card

```css
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  transition: box-shadow 150ms ease, border-color 150ms ease;
}

.card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--border-subtle);
}

.card-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.card-description {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-4);
}

.card-content {
  /* Form content goes here */
}

.card-footer {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-subtle);
}
```

### Service Card (for integrations)

```css
.service-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.service-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
}

.service-card-header h4 {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
  margin: 0;
}

.service-card-content {
  padding: var(--space-4);
}
```

### Info Box

```css
.info-box {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-info-bg);
  border-left: 3px solid var(--color-info);
  border-radius: var(--radius-sm);
}

.info-box.warning {
  background: var(--color-warning-bg);
  border-color: var(--color-warning);
}

.info-box.error {
  background: var(--color-error-bg);
  border-color: var(--color-error);
}

.info-box.success {
  background: var(--color-success-bg);
  border-color: var(--color-success);
}
```

---

## 9. Navigation

### Main Tab Navigation

```css
.nav-tabs {
  display: flex;
  gap: var(--space-1);
  padding: var(--space-2) var(--space-4);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-default);
}

.nav-tab {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
}

.nav-tab:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.nav-tab.active {
  color: var(--color-primary);
  background: var(--bg-tertiary);
}
```

### Sidebar Navigation (Recommended for Config)

```css
.sidebar-nav {
  width: 240px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-default);
  padding: var(--space-4) 0;
}

.sidebar-nav-group {
  margin-bottom: var(--space-4);
}

.sidebar-nav-group-title {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-base);
  color: var(--text-secondary);
  text-decoration: none;
  cursor: pointer;
  transition: all 150ms ease;
}

.sidebar-nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-tertiary);
}

.sidebar-nav-item.active {
  color: var(--color-primary);
  background: var(--bg-tertiary);
  border-right: 2px solid var(--color-primary);
}
```

### Sub-tabs

```css
.subtabs {
  display: flex;
  gap: var(--space-1);
  padding: var(--space-2);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.subtab {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.subtab.active {
  color: var(--text-primary);
  background: var(--bg-secondary);
  box-shadow: var(--shadow-sm);
}
```

---

## 10. Feedback & States

### Toast Notifications

```css
.toast-container {
  position: fixed;
  bottom: var(--space-5);
  right: var(--space-5);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-left: 4px solid var(--color-info);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  animation: toast-in 200ms ease;
}

.toast.success { border-left-color: var(--color-success); }
.toast.warning { border-left-color: var(--color-warning); }
.toast.error { border-left-color: var(--color-error); }

.toast-message {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.toast-close {
  padding: var(--space-1);
  color: var(--text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

### Loading States

```css
/* Spinner */
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-default);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Skeleton loader */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-tertiary) 25%,
    var(--bg-elevated) 50%,
    var(--bg-tertiary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
}

.skeleton-text {
  height: 16px;
  width: 80%;
}

.skeleton-input {
  height: 40px;
}

.skeleton-card {
  height: 120px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Status Indicators

```css
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  border-radius: var(--radius-full);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.status-badge .status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.status-badge.connected {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status-badge.error {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.status-badge.warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}
```

### Empty States

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  text-align: center;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: var(--space-4);
  opacity: 0.5;
}

.empty-state h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.empty-state p {
  font-size: var(--text-base);
  color: var(--text-secondary);
  margin-bottom: var(--space-4);
  max-width: 400px;
}
```

---

## 11. Icons

### Icon Guidelines

1. **Use SVG icons** for scalability and color control
2. **Consistent sizing**: 16px (small), 20px (default), 24px (large)
3. **Use `currentColor`** for stroke/fill to inherit text color
4. **Avoid emoji** for primary UI elements (accessibility concerns)

### Icon Sizes

```css
.icon-sm { width: 16px; height: 16px; }
.icon-md { width: 20px; height: 20px; }
.icon-lg { width: 24px; height: 24px; }
```

### Recommended Icon Set

For consistency, prefer icons from:
- [Heroicons](https://heroicons.com/) (MIT license)
- [Lucide](https://lucide.dev/) (ISC license)

### Transitioning from Emoji

Current emoji usage should be replaced with SVG icons:

| Current | Replace With |
|---------|--------------|
| `📺` Plex | Server/monitor icon |
| `🎬` TMDb | Film icon |
| `📚` Libraries | Library/books icon |
| `⚙️` Settings | Cog/gear icon |
| `🔔` Notifications | Bell icon |
| `▶️` Run | Play icon |

---

## 12. Layout Patterns

### Content Width Containers

```css
.container {
  width: 100%;
  max-width: var(--container-width);
  margin: 0 auto;
  padding: 0 var(--space-4);
}

:root {
  --container-sm: 640px;   /* Narrow forms, modals */
  --container-md: 960px;   /* Standard content */
  --container-lg: 1200px;  /* Wide layouts */
  --container-xl: 1400px;  /* Full dashboards */
}
```

### Split Layout (Form + Preview)

```css
.split-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  min-height: 500px;
}

.split-layout-main {
  overflow-y: auto;
}

.split-layout-preview {
  position: sticky;
  top: var(--space-4);
  background: var(--bg-base);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
}

@media (max-width: 1024px) {
  .split-layout {
    grid-template-columns: 1fr;
  }
}
```

### Sidebar Layout

```css
.layout-with-sidebar {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .layout-with-sidebar {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: fixed;
    left: -240px;
    transition: left 200ms ease;
  }

  .sidebar.open {
    left: 0;
  }
}
```

---

## 13. Utility Classes

### Display

```css
.hidden { display: none; }
.block { display: block; }
.inline { display: inline; }
.inline-block { display: inline-block; }
.flex { display: flex; }
.inline-flex { display: inline-flex; }
.grid { display: grid; }
```

### Flexbox

```css
.flex-row { flex-direction: row; }
.flex-col { flex-direction: column; }
.items-start { align-items: flex-start; }
.items-center { align-items: center; }
.items-end { align-items: flex-end; }
.justify-start { justify-content: flex-start; }
.justify-center { justify-content: center; }
.justify-end { justify-content: flex-end; }
.justify-between { justify-content: space-between; }
.flex-1 { flex: 1; }
.flex-2 { flex: 2; }
.flex-wrap { flex-wrap: wrap; }
```

### Spacing

```css
.m-0 { margin: 0; }
.m-1 { margin: var(--space-1); }
.m-2 { margin: var(--space-2); }
.m-3 { margin: var(--space-3); }
.m-4 { margin: var(--space-4); }

.mt-0 { margin-top: 0; }
.mt-1 { margin-top: var(--space-1); }
/* ... etc for mb, ml, mr, mx, my */

.p-0 { padding: 0; }
.p-1 { padding: var(--space-1); }
/* ... etc */

.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-5 { gap: var(--space-5); }
```

### Typography

```css
.text-xs { font-size: var(--text-xs); }
.text-sm { font-size: var(--text-sm); }
.text-base { font-size: var(--text-base); }
.text-md { font-size: var(--text-md); }
.text-lg { font-size: var(--text-lg); }
.text-xl { font-size: var(--text-xl); }

.font-normal { font-weight: var(--font-normal); }
.font-medium { font-weight: var(--font-medium); }
.font-semibold { font-weight: var(--font-semibold); }
.font-bold { font-weight: var(--font-bold); }

.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-muted { color: var(--text-muted); }
.text-success { color: var(--color-success); }
.text-warning { color: var(--color-warning); }
.text-error { color: var(--color-error); }

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

### Width

```css
.w-full { width: 100%; }
.w-auto { width: auto; }
.max-w-sm { max-width: var(--container-sm); }
.max-w-md { max-width: var(--container-md); }
.max-w-lg { max-width: var(--container-lg); }
```

---

## 14. Component Patterns

### Standard Card with Header

```html
<div class="card">
  <div class="card-header">
    <div class="card-title">
      <svg class="icon-md"><!-- icon --></svg>
      <h3>Plex Configuration</h3>
    </div>
    <span class="status-badge connected">
      <span class="status-dot"></span>
      Connected
    </span>
  </div>
  <p class="card-description">
    Connect Kometa to your Plex Media Server.
  </p>
  <div class="card-content">
    <!-- Form content -->
  </div>
  <div class="card-footer">
    <button class="btn btn-secondary">Test Connection</button>
    <span class="test-result"></span>
  </div>
</div>
```

### Form Group with Validation

```html
<div class="form-group has-error">
  <label class="form-label" for="plex-url">
    Plex URL
    <span class="required">*</span>
    <button type="button" class="btn-icon" aria-label="Help">
      <svg class="icon-sm"><!-- help icon --></svg>
    </button>
  </label>
  <input
    type="text"
    id="plex-url"
    class="form-input"
    placeholder="http://192.168.1.100:32400"
    aria-describedby="plex-url-error"
  >
  <span class="form-error" id="plex-url-error">
    Please enter a valid URL
  </span>
</div>
```

### Checkbox Group

```html
<div class="checkbox-group">
  <label class="form-checkbox">
    <input type="checkbox" id="clean-bundles">
    <div>
      <span class="form-checkbox-label">Clean Bundles</span>
      <span class="form-checkbox-description">
        Remove unused bundle files from Plex
      </span>
    </div>
  </label>
</div>
```

### Empty State

```html
<div class="empty-state">
  <div class="empty-state-icon">
    <svg class="icon-lg"><!-- icon --></svg>
  </div>
  <h3>No libraries configured</h3>
  <p>Add your first library to start creating collections and applying overlays.</p>
  <button class="btn btn-primary">
    <svg class="icon-sm"><!-- plus icon --></svg>
    Add Library
  </button>
</div>
```

### Service Card

```html
<div class="service-card">
  <div class="service-card-header">
    <h4>
      <svg class="icon-md"><!-- radarr icon --></svg>
      Radarr
    </h4>
    <span class="status-badge">Not configured</span>
  </div>
  <div class="service-card-content">
    <p class="text-sm text-secondary mb-3">
      Add missing movies from collections to Radarr.
    </p>
    <!-- Form fields -->
    <div class="card-footer">
      <button class="btn btn-secondary">Test Connection</button>
    </div>
  </div>
</div>
```

---

## 15. Accessibility

### Focus Management

```css
/* Use focus-visible for keyboard navigation only */
:focus {
  outline: none;
}

:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus);
}

/* Skip link */
.skip-link {
  position: absolute;
  top: -100px;
  left: var(--space-4);
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary);
  color: var(--text-inverse);
  border-radius: var(--radius-sm);
  z-index: 9999;
}

.skip-link:focus {
  top: var(--space-4);
}
```

### ARIA Guidelines

1. **Labels**: All form inputs must have associated labels
2. **Descriptions**: Use `aria-describedby` for helper text and errors
3. **Live regions**: Use `aria-live="polite"` for toast notifications
4. **Expanded state**: Use `aria-expanded` for collapsible sections
5. **Current state**: Use `aria-current="page"` for active navigation

### Color Contrast

- Text on backgrounds must meet WCAG AA (4.5:1 for normal text)
- Current palette passes for primary text colors
- Never use color alone to convey information

### Keyboard Navigation

- All interactive elements must be keyboard accessible
- Tab order should follow visual order
- Escape key should close modals
- Enter/Space should activate buttons

---

## 16. Dashboard Components

The Dashboard tab is the landing page showing system status at a glance.

### Status Cards

```css
.dashboard-status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.status-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  transition: all 200ms ease;
}

.status-card:hover {
  border-color: var(--border-strong);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.status-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.status-card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  font-size: 20px;
}

.status-card-title {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-1);
}

.status-card-value {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

/* Status variants */
.status-card.connected .status-card-icon {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.status-card.error .status-card-icon {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.status-card.pending .status-card-icon {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}
```

### Library Cards

```css
.dashboard-libraries {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-3);
}

.library-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  text-align: center;
  transition: all 200ms ease;
}

.library-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.library-card-icon {
  font-size: 32px;
  margin-bottom: var(--space-2);
}

.library-card-name {
  font-weight: var(--font-medium);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.library-card-type {
  font-size: var(--text-sm);
  color: var(--text-muted);
}
```

### Quick Actions

```css
.dashboard-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
}

.dashboard-action-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
}

.dashboard-action-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--color-primary);
}

.dashboard-action-btn.primary {
  background: var(--color-primary);
  color: var(--text-inverse);
  border-color: var(--color-primary);
}
```

### Recent Activity Feed

```css
.activity-feed {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.activity-feed-header {
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
  font-weight: var(--font-semibold);
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: 14px;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-message {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.activity-time {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}
```

### HTML Pattern

```html
<div class="dashboard-status-cards">
  <div class="status-card connected">
    <div class="status-card-header">
      <span class="status-card-icon">P</span>
      <span class="status-badge connected">
        <span class="status-dot"></span>
        Connected
      </span>
    </div>
    <div class="status-card-title">Plex Server</div>
    <div class="status-card-value">Online</div>
  </div>
  <!-- More status cards -->
</div>
```

---

## 17. Setup Wizard

A 4-step guided wizard for first-time users.

### Wizard Modal

```css
.wizard-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 200ms ease;
}

.wizard-modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 300ms ease;
}

.wizard-header {
  padding: var(--space-4) var(--space-5);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
}

.wizard-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-1);
}

.wizard-subtitle {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
```

### Step Progress

```css
.wizard-progress {
  display: flex;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-4);
  background: var(--bg-primary);
}

.wizard-step-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.wizard-step-dot {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  background: var(--bg-tertiary);
  color: var(--text-muted);
  border: 2px solid var(--border-default);
  transition: all 200ms ease;
}

.wizard-step-indicator.active .wizard-step-dot {
  background: var(--color-primary);
  color: var(--text-inverse);
  border-color: var(--color-primary);
}

.wizard-step-indicator.completed .wizard-step-dot {
  background: var(--color-success);
  color: white;
  border-color: var(--color-success);
}

.wizard-step-line {
  width: 40px;
  height: 2px;
  background: var(--border-default);
}

.wizard-step-indicator.completed + .wizard-step-line,
.wizard-step-line.completed {
  background: var(--color-success);
}
```

### Step Content

```css
.wizard-content {
  flex: 1;
  padding: var(--space-5);
  overflow-y: auto;
}

.wizard-step {
  display: none;
  animation: fadeIn 200ms ease;
}

.wizard-step.active {
  display: block;
}

.wizard-step h3 {
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-4);
}

.wizard-step .form-group {
  margin-bottom: var(--space-4);
}
```

### Wizard Footer

```css
.wizard-footer {
  display: flex;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-default);
}

.wizard-footer .btn-group {
  display: flex;
  gap: var(--space-2);
}
```

### HTML Pattern

```html
<div class="wizard-overlay" id="setup-wizard">
  <div class="wizard-modal">
    <div class="wizard-header">
      <h2 class="wizard-title">Welcome to Kometa</h2>
      <p class="wizard-subtitle">Let's get you set up in just a few steps</p>
    </div>

    <div class="wizard-progress">
      <div class="wizard-step-indicator active">
        <span class="wizard-step-dot">1</span>
      </div>
      <div class="wizard-step-line"></div>
      <div class="wizard-step-indicator">
        <span class="wizard-step-dot">2</span>
      </div>
      <!-- More steps -->
    </div>

    <div class="wizard-content">
      <div class="wizard-step active" data-step="1">
        <h3>Connect to Plex</h3>
        <!-- Step content -->
      </div>
    </div>

    <div class="wizard-footer">
      <button class="btn btn-ghost">Skip Setup</button>
      <div class="btn-group">
        <button class="btn btn-secondary">Back</button>
        <button class="btn btn-primary">Next</button>
      </div>
    </div>
  </div>
</div>
```

---

## 18. Profile Switcher

Header dropdown for switching between configuration profiles.

### Profile Dropdown

```css
.profile-switcher {
  position: relative;
}

.profile-switcher-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 150ms ease;
}

.profile-switcher-btn:hover {
  background: var(--bg-elevated);
  border-color: var(--border-strong);
}

.profile-switcher-btn .profile-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.profile-switcher-btn .chevron {
  transition: transform 200ms ease;
}

.profile-switcher.open .profile-switcher-btn .chevron {
  transform: rotate(180deg);
}
```

### Dropdown Menu

```css
.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: var(--space-1);
  min-width: 200px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transition: all 200ms ease;
}

.profile-switcher.open .profile-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.profile-dropdown-header {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--border-subtle);
}

.profile-list {
  max-height: 200px;
  overflow-y: auto;
}

.profile-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: background 150ms ease;
}

.profile-item:hover {
  background: var(--bg-tertiary);
}

.profile-item.active {
  color: var(--color-primary);
  background: var(--bg-tertiary);
}

.profile-item.active::after {
  content: "✓";
  color: var(--color-success);
}

.profile-dropdown-footer {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--border-subtle);
}

.save-profile-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-2);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  background: transparent;
  border: 1px dashed var(--border-default);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 150ms ease;
}

.save-profile-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
}
```

### HTML Pattern

```html
<div class="profile-switcher">
  <button class="profile-switcher-btn">
    <span class="profile-name">Default Profile</span>
    <span class="chevron">▼</span>
  </button>
  <div class="profile-dropdown">
    <div class="profile-dropdown-header">Profiles</div>
    <div class="profile-list">
      <div class="profile-item active">Default Profile</div>
      <div class="profile-item">Production</div>
      <div class="profile-item">Testing</div>
    </div>
    <div class="profile-dropdown-footer">
      <button class="save-profile-btn">
        <span>+</span> Save Current as New
      </button>
    </div>
  </div>
</div>
```

---

## 19. Overlay Gallery

Visual gallery showing available overlay presets.

### Gallery Grid

```css
.overlay-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-4);
  padding: var(--space-4);
}

.overlay-preset {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  text-align: center;
  cursor: pointer;
  transition: all 200ms ease;
}

.overlay-preset:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.overlay-preset.selected {
  border-color: var(--color-primary);
  background: rgba(229, 160, 13, 0.1);
}
```

### Preset Item

```css
.overlay-preset-preview {
  width: 100%;
  aspect-ratio: 2/3;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-2);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.overlay-preset-preview .overlay-badge {
  position: absolute;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

/* Overlay badge positions */
.overlay-badge.top-left {
  top: var(--space-2);
  left: var(--space-2);
}

.overlay-badge.top-right {
  top: var(--space-2);
  right: var(--space-2);
}

.overlay-badge.bottom-left {
  bottom: var(--space-2);
  left: var(--space-2);
}

.overlay-badge.bottom-right {
  bottom: var(--space-2);
  right: var(--space-2);
}

/* Overlay badge colors */
.overlay-badge.resolution {
  background: #3b82f6;
  color: white;
}

.overlay-badge.audio {
  background: #8b5cf6;
  color: white;
}

.overlay-badge.hdr {
  background: #f59e0b;
  color: black;
}

.overlay-badge.rating {
  background: #22c55e;
  color: white;
}

.overlay-badge.streaming {
  background: #ef4444;
  color: white;
}

.overlay-preset-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-primary);
}

.overlay-preset-desc {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: var(--space-1);
}
```

### HTML Pattern

```html
<div class="overlay-gallery">
  <div class="overlay-preset" data-preset="4k-badge">
    <div class="overlay-preset-preview">
      <span class="overlay-badge resolution top-left">4K</span>
    </div>
    <div class="overlay-preset-name">4K Resolution</div>
    <div class="overlay-preset-desc">Shows 4K badge on media</div>
  </div>

  <div class="overlay-preset" data-preset="hdr">
    <div class="overlay-preset-preview">
      <span class="overlay-badge hdr top-right">HDR</span>
    </div>
    <div class="overlay-preset-name">HDR Format</div>
    <div class="overlay-preset-desc">Dolby Vision, HDR10+</div>
  </div>

  <!-- More presets -->
</div>
```

---

## 20. Pre-flight Checklist

Run tab checklist verifying configuration before running Kometa.

### Checklist Container

```css
.preflight-checklist {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.preflight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
}

.preflight-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-weight: var(--font-semibold);
}

.preflight-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
}

.preflight-status.ready {
  color: var(--color-success);
}

.preflight-status.issues {
  color: var(--color-warning);
}
```

### Checklist Items

```css
.preflight-items {
  padding: var(--space-3) var(--space-4);
}

.preflight-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-subtle);
}

.preflight-item:last-child {
  border-bottom: none;
}

.preflight-item-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  font-size: 14px;
}

.preflight-item.pass .preflight-item-icon {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.preflight-item.fail .preflight-item-icon {
  background: var(--color-error-bg);
  color: var(--color-error);
}

.preflight-item.warning .preflight-item-icon {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

.preflight-item.checking .preflight-item-icon {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.preflight-item-content {
  flex: 1;
}

.preflight-item-label {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.preflight-item-detail {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

.preflight-item-action {
  font-size: var(--text-xs);
  color: var(--color-info);
  cursor: pointer;
}

.preflight-item-action:hover {
  text-decoration: underline;
}
```

### HTML Pattern

```html
<div class="preflight-checklist">
  <div class="preflight-header">
    <div class="preflight-title">
      <span>Pre-flight Checklist</span>
    </div>
    <div class="preflight-status ready">
      <span>All checks passed</span>
    </div>
  </div>

  <div class="preflight-items">
    <div class="preflight-item pass">
      <div class="preflight-item-icon">✓</div>
      <div class="preflight-item-content">
        <div class="preflight-item-label">Configuration Loaded</div>
        <div class="preflight-item-detail">config.yml valid and loaded</div>
      </div>
    </div>

    <div class="preflight-item pass">
      <div class="preflight-item-icon">✓</div>
      <div class="preflight-item-content">
        <div class="preflight-item-label">Plex Connection</div>
        <div class="preflight-item-detail">Connected to Plex server</div>
      </div>
    </div>

    <div class="preflight-item fail">
      <div class="preflight-item-icon">✗</div>
      <div class="preflight-item-content">
        <div class="preflight-item-label">TMDb API</div>
        <div class="preflight-item-detail">API key not configured</div>
      </div>
      <span class="preflight-item-action">Configure →</span>
    </div>
  </div>
</div>
```

---

## 21. YAML Preview Panel

Split-pane view showing real-time YAML output.

### Split Layout

```css
.config-split-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  height: calc(100vh - 200px);
}

.config-split-view.preview-collapsed {
  grid-template-columns: 1fr;
}

@media (max-width: 1024px) {
  .config-split-view {
    grid-template-columns: 1fr;
  }

  .yaml-preview-panel {
    display: none;
  }

  .yaml-preview-panel.mobile-visible {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 1000;
  }
}
```

### Preview Panel

```css
.yaml-preview-panel {
  background: var(--bg-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.yaml-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) var(--space-3);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
}

.yaml-preview-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
}

.yaml-preview-actions {
  display: flex;
  gap: var(--space-1);
}

.yaml-preview-content {
  flex: 1;
  overflow: auto;
  padding: var(--space-3);
}

.yaml-preview-content pre {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: var(--text-primary);
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}
```

### YAML Syntax Highlighting

```css
.yaml-key {
  color: #7dd3fc; /* Light blue */
}

.yaml-string {
  color: #86efac; /* Light green */
}

.yaml-number {
  color: #fca5a5; /* Light red */
}

.yaml-boolean {
  color: #c4b5fd; /* Light purple */
}

.yaml-comment {
  color: var(--text-muted);
  font-style: italic;
}

.yaml-null {
  color: #f59e0b;
}
```

### Toggle Button

```css
.yaml-preview-toggle {
  position: fixed;
  bottom: var(--space-5);
  left: var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  z-index: 100;
}

.yaml-preview-toggle:hover {
  background: var(--bg-elevated);
  border-color: var(--color-primary);
}
```

---

## 22. Keyboard Shortcuts

System for handling keyboard shortcuts throughout the app.

### Shortcuts Modal

```css
.shortcuts-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fadeIn 150ms ease;
}

.shortcuts-modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  animation: slideUp 200ms ease;
}

.shortcuts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-default);
}

.shortcuts-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
}

.shortcuts-content {
  padding: var(--space-4);
  overflow-y: auto;
  max-height: 60vh;
}
```

### Shortcut List

```css
.shortcuts-group {
  margin-bottom: var(--space-4);
}

.shortcuts-group:last-child {
  margin-bottom: 0;
}

.shortcuts-group-title {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-subtle);
}

.shortcut-item:last-child {
  border-bottom: none;
}

.shortcut-description {
  font-size: var(--text-sm);
  color: var(--text-primary);
}

.shortcut-keys {
  display: flex;
  gap: var(--space-1);
}

.shortcut-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  padding: var(--space-1) var(--space-2);
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--text-primary);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  box-shadow: 0 2px 0 var(--border-default);
}
```

### HTML Pattern

```html
<div class="shortcuts-modal-overlay" id="shortcuts-modal">
  <div class="shortcuts-modal">
    <div class="shortcuts-header">
      <h3 class="shortcuts-title">Keyboard Shortcuts</h3>
      <button class="btn btn-ghost btn-icon" onclick="keyboard.hideShortcuts()">✕</button>
    </div>
    <div class="shortcuts-content">
      <div class="shortcuts-group">
        <div class="shortcuts-group-title">General</div>
        <div class="shortcut-item">
          <span class="shortcut-description">Save configuration</span>
          <div class="shortcut-keys">
            <span class="shortcut-key">Ctrl</span>
            <span class="shortcut-key">S</span>
          </div>
        </div>
        <div class="shortcut-item">
          <span class="shortcut-description">Toggle YAML preview</span>
          <div class="shortcut-keys">
            <span class="shortcut-key">Ctrl</span>
            <span class="shortcut-key">P</span>
          </div>
        </div>
      </div>

      <div class="shortcuts-group">
        <div class="shortcuts-group-title">Navigation</div>
        <div class="shortcut-item">
          <span class="shortcut-description">Go to Dashboard</span>
          <div class="shortcut-keys">
            <span class="shortcut-key">Ctrl</span>
            <span class="shortcut-key">1</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

## 23. Animations

Micro-animations for improved user feedback.

### Standard Durations

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --duration-slower: 500ms;
}
```

### Easing Functions

```css
:root {
  --ease-default: ease;
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### Common Animations

```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Fade out */
@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* Slide up */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Slide down */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale in */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Shimmer (for skeletons) */
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Shake (for errors) */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-4px); }
  40%, 80% { transform: translateX(4px); }
}
```

### Interactive States

```css
/* Button press effect */
.btn:active {
  transform: translateY(1px);
  transition: transform 50ms ease;
}

/* Card hover lift */
.card:hover {
  transform: translateY(-2px);
  transition: transform var(--duration-normal) var(--ease-out);
}

/* Input focus glow */
.form-input:focus {
  box-shadow: var(--shadow-focus);
  transition: box-shadow var(--duration-fast) ease;
}

/* Link underline animation */
.animated-link {
  position: relative;
}

.animated-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: currentColor;
  transition: width var(--duration-normal) var(--ease-out);
}

.animated-link:hover::after {
  width: 100%;
}
```

### Reduced Motion

```css
/* Respect user preference for reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01 | Initial style guide |
| 2.0 | 2026-01 | Added Dashboard, Setup Wizard, Profile Switcher, Overlay Gallery, Pre-flight Checklist, YAML Preview, Keyboard Shortcuts, and Animations sections |

---

## Related Documents

- [UI/UX Audit](./UI_UX_AUDIT.md) - Problem identification and roadmap
- [DESIGN_NOTES.md](../DESIGN_NOTES.md) - Architecture documentation
