# Kometa Web UI - Comprehensive UI/UX Audit

> **Date:** January 2026
> **Version:** 1.0
> **Status:** Planning Phase

## Executive Summary

The Kometa Web UI is a functional vanilla JS/HTML/CSS single-page application with ~12KB of frontend code. While it provides substantial functionality (configuration editing, overlay previews, run management), the UI suffers from **visual density overload, inconsistent spacing, and lack of visual hierarchy**. The good news: the existing CSS variables and component patterns provide a solid foundation for modernization without a full rewrite.

---

## 1. UI/UX Audit - Specific Problems

### 1.1 Navigation & Information Architecture

| Problem | Location | Impact |
|---------|----------|--------|
| **9 horizontal sub-tabs in Configuration** | `index.html:81-89` | Cognitive overload; tabs crowd on smaller screens |
| **No breadcrumb or contextual orientation** | All tabs | Users lose context in deeply nested forms |
| **History/Logs tabs are functionally similar** | Main nav | Could be consolidated or differentiated better |
| **"Advanced Options" hidden in collapsibles** | Overlays tab | Important features are too buried |

### 1.2 Spacing & Layout Inconsistencies

| Problem | CSS Location | Example |
|---------|--------------|---------|
| **Ad-hoc spacing scale** | Throughout | Uses 5/8/10/12/15/20/25/30px randomly |
| **Form rows have inconsistent gaps** | `.form-row` uses `gap: 10px` sometimes, `gap: 15px` other times | Jarring rhythm |
| **Section headers use mixed margins** | `.section-header`, `.form-section` | 15px vs 20px vs 25px |
| **Inline styles override classes** | `index.html:305` | `style="margin-bottom: 20px;"` instead of class |
| **Max-width varies** | `.overlays-panel: 1200px`, `.main-content: 1400px`, `.run-panel: 800px` | Inconsistent reading width |

### 1.3 Typography Issues

| Problem | Location | Impact |
|---------|----------|--------|
| **7+ font sizes with no clear hierarchy** | 11/12/13/14/16/18/24px | Unclear what's primary vs secondary |
| **Helper text inconsistent** | `.field-help`, `small`, `.checkbox-desc` | Three different patterns for same purpose |
| **Section headers inconsistent** | `h3`, `h4` used interchangeably | No clear visual hierarchy |
| **Uppercase labels vs sentence case mixed** | `.detail-label` (uppercase) vs regular labels | Inconsistent text treatment |

### 1.4 Form UX Problems

| Problem | Location | Severity |
|---------|----------|----------|
| **Settings tab shows 8 collapsible groups** | `index.html:399-797` | Overwhelming; no quick summary |
| **Arr Services shows too many fields at once** | `index.html:801-1055` | Dense form wall; ~30 inputs visible |
| **Checkbox rows misaligned** | `index.html:688-716` | Broken flexbox nesting |
| **Required field indicators inconsistent** | Some have `*`, some have badge, some nothing | Unclear which fields are mandatory |
| **Default values shown but not applied** | `.default-badge` shows "Default: 60" but field is empty | Confusing UX |

### 1.5 Visual Feedback & States

| Problem | Location | Impact |
|---------|----------|--------|
| **No toast/snackbar system visible** | N/A | Success/error feedback unclear |
| **"Loading..." plain text instead of skeletons** | `index.html:1469`, `index.html:324` | Feels dated |
| **Connection test results inline only** | `.test-result` | Easy to miss |
| **No visual confirmation after Save** | Save button | User unsure if action succeeded |
| **Empty states generic** | "Loading backups...", "No overlays selected" | Don't explain next steps |

### 1.6 Component Design Issues

| Problem | Location | Impact |
|---------|----------|--------|
| **Service cards lack visual grouping** | `.service-card` has no shadow or clear boundary | Blends into background |
| **Details/summary elements look like regular text** | `.settings-group` | Not obviously expandable |
| **Buttons have 3+ different sizing patterns** | `.btn`, `.btn-large`, `.btn-small`, `.btn-icon` | Inconsistent proportions |
| **Modal dialogs are very large (95vw)** | `.visual-editor-modal-content` | Overwhelming on large screens |

### 1.7 Accessibility Concerns

| Problem | Location | Impact |
|---------|----------|--------|
| **Tooltips hover-only** | `.tooltip-wrapper` | Not accessible on touch devices |
| **Color-only status indicators** | `.status-dot` | Colorblind users may miss state |
| **Focus styles not customized** | Default browser styles | Hard to see in dark theme |
| **Emoji used for section icons** | Various | Screen reader announces emoji names |

---

## 2. Prioritized Implementation Roadmap

### Phase 1: Quick Wins (Low Effort, High Impact)

| Task | File(s) | Impact |
|------|---------|--------|
| Standardize spacing with CSS variables | `style.css` | Critical |
| Add toast notification system | `style.css`, `app.js` | Critical |
| Replace "Loading..." with skeletons | `style.css` | High |
| Fix checkbox alignment issues | `index.html:688-716` | Medium |
| Add focus-visible styles | `style.css` | Medium |
| Remove inline styles, use classes | `index.html` | Medium |

### Phase 2: Structural Improvements (Medium Effort)

| Task | Impact |
|------|--------|
| Convert horizontal sub-tabs to sidebar navigation | Critical |
| Implement card-based section design | High |
| Add form validation with visual states | High |
| Create empty state components | Medium |
| Improve button consistency | Medium |

### Phase 3: Feature Enhancements (Higher Effort)

| Task | Impact |
|------|--------|
| Add live YAML preview panel (split view) | Critical |
| Add status dashboard landing page | High |
| Improve overlay preview with thumbnails | High |
| Add guided setup wizard | Medium |
| Add profile switching UI | Medium |

### Phase 4: Polish (After Fundamentals)

| Task | Impact |
|------|--------|
| Micro-animations (button press, card hover) | Low |
| Keyboard shortcuts | Low |
| Mobile responsive refinements | Low |
| Dark/light mode toggle | Low |

---

## 3. Tech Stack Recommendation

### Current Stack Assessment

| Aspect | Current | Verdict |
|--------|---------|---------|
| **Framework** | Vanilla JS | Keep - dependency-free is a feature |
| **CSS** | Custom with variables | Keep - good foundation |
| **Build** | None (static files) | Keep - simple deployment |
| **State** | Single `state` object | Works but fragile |
| **Components** | Inline HTML | Limited reusability |

### Recommendation: Stay with Vanilla + Add Minimal Tooling

A full framework rewrite is **not justified** for this use case. Instead:

**Add:**
1. CSS Custom Properties expansion (already started, just extend)
2. CSS logical properties for better RTL support
3. Utility classes for common patterns (`.flex`, `.gap-4`, etc.)
4. Web Components for reusable patterns (optional, native JS)

### Pragmatic Improvements (No Rewrite)

1. **Extract CSS into logical partials:**
   - `base.css` - variables, reset
   - `components.css` - buttons, cards, inputs
   - `layout.css` - grid, navigation
   - `pages.css` - page-specific styles

2. **Add utility classes** (see Style Guide)

3. **Refactor JS into modules** (if using ES modules or build step):
   - `state.js` - centralized state
   - `api.js` - API calls
   - `ui.js` - DOM manipulation helpers
   - `pages/config.js`, `pages/overlays.js`, etc.

---

## 4. Kometa-Specific Enhancements

### 4.1 Live YAML Preview Panel

Add a split-pane view for form editing:

```
+------------------------+------------------------+
|                        |  config.yml            |
|  [Visual Form]         |  -------------------   |
|                        |  plex:                 |
|  Plex URL: [_______]   |    url: http://...     |
|  Token: [_________]    |    token: ****         |
|                        |                        |
|  [x] Clean Bundles     |    clean_bundles: true |
|                        |                        |
+------------------------+------------------------+
```

### 4.2 Profile Switching & Status Visibility

Add a profile selector to the header with last run status.

### 4.3 Overlay Preview Improvements

- Add thumbnail previews to overlay cards
- Add "Quick Preview" on hover
- Inline mini-canvas in overlay selector

### 4.4 Clear "Run / Generate / Preview" Affordances

The Run tab needs clearer call-to-action with a checklist showing readiness.

### 4.5 Dashboard Overview

Add a quick-glance dashboard as the landing page showing:
- Connection status
- Last run summary
- Library overview cards
- Next scheduled run

---

## 5. Related Documents

- [Design System Style Guide](./STYLE_GUIDE.md) - CSS variables, components, patterns
- [DESIGN_NOTES.md](../DESIGN_NOTES.md) - Architecture documentation

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-01 | 1.0 | Initial audit completed |
