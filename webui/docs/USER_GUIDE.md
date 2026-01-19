# Kometa Web UI - User Guide

> **Version:** 2.0
> **Last Updated:** January 2026

Welcome to the Kometa Web UI! This guide covers all the features available in the modernized interface.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Configuration](#configuration)
4. [Scheduling & Automation](#scheduling--automation)
5. [Collection Builder](#collection-builder)
6. [Playlist Builder](#playlist-builder)
7. [Data Mappers](#data-mappers)
8. [Metadata Editor](#metadata-editor)
9. [Advanced Operations](#advanced-operations)
10. [Notifications](#notifications)
11. [Overlay Preview](#overlay-preview)
12. [Running Kometa](#running-kometa)
13. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Getting Started

### First-Time Setup

When you first access the Web UI, a setup wizard will guide you through:

1. **Welcome** - Introduction to Kometa
2. **Plex Connection** - Enter your Plex URL and token
3. **TMDb API** - Add your TMDb API key
4. **Libraries** - Select which libraries to manage
5. **Complete** - Review and save your configuration

You can re-run the wizard at any time from **Settings > General**.

### Theme Selection

The UI supports both light and dark themes:
- Click the theme toggle in the header (sun/moon icon)
- Or press `T` to toggle themes
- Your preference is saved automatically

### Configuration Profiles

Create multiple configuration profiles for different environments:
1. Click the profile dropdown in the header
2. Select "New Profile"
3. Name it (e.g., "Production", "Testing")
4. Switch between profiles anytime

---

## Dashboard

The dashboard provides an at-a-glance overview of your Kometa setup:

### Status Cards
- **Libraries** - Number of configured Plex libraries
- **Collections** - Total collections across all libraries
- **Last Run** - When Kometa last executed
- **Next Run** - Scheduled next execution time

### Quick Actions
- **Run Now** - Start a Kometa run immediately
- **View Logs** - Jump to the logs panel
- **Edit Config** - Open the configuration editor

### Recent Activity
Shows the last 5 Kometa runs with status and duration.

---

## Configuration

### Navigation Sidebar

The configuration is organized into sections:

| Section | Purpose |
|---------|---------|
| **Connections** | Plex, TMDb, and other service credentials |
| **Settings** | Global Kometa settings |
| **Scheduling** | When and how Kometa runs |
| **Operations** | Mass metadata update operations |
| **Collections** | Visual collection builder |
| **Playlists** | Playlist configuration |
| **Arr Services** | Radarr/Sonarr integration |
| **Metadata** | Metadata source settings |
| **Lists** | External list integrations |
| **Notifications** | Webhook and notification setup |
| **Data Mappers** | Genre/rating/studio mapping |
| **Metadata Editor** | Per-item metadata editing |
| **Advanced Ops** | Advanced maintenance operations |
| **Raw YAML** | Direct YAML editing |

### Live YAML Preview

As you configure options in the visual editors, a live YAML preview shows the configuration that will be generated. Click "Copy" to copy the YAML to your clipboard.

### Validation

The UI validates your configuration in real-time:
- **Green** - Configuration is valid
- **Yellow** - Warnings (non-critical issues)
- **Red** - Errors that must be fixed

---

## Scheduling & Automation

### Global Schedule

Set when Kometa should run automatically:

1. Go to **Configuration > Scheduling**
2. Choose a schedule preset:
   - **Daily** - Run once per day at a specific time
   - **Weekly** - Run on specific days of the week
   - **Monthly** - Run on specific days of the month
   - **Range** - Run between specific dates
   - **Custom** - Write a custom cron expression

3. For weekly schedules, select which days to run
4. Set the run time

### Run Order

Drag and drop to reorder how Kometa processes tasks:
1. **Operations** - Mass metadata updates
2. **Metadata** - Process metadata files
3. **Collections** - Build and update collections
4. **Overlays** - Apply overlay images

### Library-Specific Schedules

Each library can have its own schedule that overrides the global settings.

---

## Collection Builder

Create collections visually without writing YAML.

### Creating a Collection

1. Go to **Configuration > Collections**
2. Click **+ New Collection**
3. Enter a collection name
4. Click **+ Add Builder** to add content sources

### Builder Sources

Choose from 20+ sources organized by category:

| Category | Sources |
|----------|---------|
| **Charts** | TMDb Popular, TMDb Top Rated, TMDb Trending, Trakt Trending |
| **Lists** | Trakt Lists, IMDb Lists, Letterboxd, MDBList |
| **Anime** | AniList, MyAnimeList, AniDB |
| **Awards** | Oscars, Emmys, Golden Globes |
| **Plex** | Plex Search, Plex All, Collectionless |
| **Streaming** | Netflix, Disney+, Prime Video, etc. |

### Adding Filters

Refine your collection with smart filters:
1. Click **+ Add Filter**
2. Choose a field (year, genre, rating, etc.)
3. Select an operator (is, contains, greater than, etc.)
4. Enter a value
5. Add multiple filters with AND/OR logic

### Collection Settings

Configure how the collection appears in Plex:
- **Sort Title** - Custom sort order
- **Collection Mode** - Show/hide in library
- **Sync Mode** - Sync (remove missing) or Append (only add)
- **Minimum Items** - Minimum items to keep collection

### YAML Preview

The collection builder shows live YAML output. Copy this to use in your collection files.

---

## Playlist Builder

Create playlists with similar features to collections.

### Creating a Playlist

1. Go to **Configuration > Playlists**
2. Click **+ New Playlist**
3. Configure:
   - **Name** - Playlist title
   - **Libraries** - Which libraries to include
   - **Sync Users** - Which Plex users see the playlist
   - **Builders** - Content sources (same as collections)

### User Sync

Select which Plex users should have access to the playlist:
- Check individual users
- Use "All Users" for everyone
- Exclude specific users if needed

---

## Data Mappers

Standardize metadata values across your library.

### Genre Mapper

Map variant genre names to consistent values:

```
Sci-Fi      →  Science Fiction
SciFi       →  Science Fiction
SF          →  Science Fiction
```

### Content Rating Mapper

Standardize content ratings:

```
gb/15       →  R
gb/12A      →  PG-13
gb/U        →  G
```

### Studio Mapper

Normalize studio names:

```
20th Century Fox  →  20th Century Studios
Fox               →  20th Century Studios
```

### Quick Presets

Apply common mappings instantly:
- **Sci-Fi Variants** - Standardize science fiction genres
- **UK to MPAA** - Convert UK ratings to US equivalents
- **AU to MPAA** - Convert Australian ratings
- **DE to MPAA** - Convert German ratings

---

## Metadata Editor

Browse and edit metadata for individual items in your library.

### Browsing Media

1. Go to **Configuration > Metadata Editor**
2. Select a library from the dropdown
3. Use the search box to find specific items
4. Filter by type (Movies, Shows, Collections)
5. Sort by title, date added, year, or rating

### Editing Metadata

Click any item to open the editor panel:

| Field | Description |
|-------|-------------|
| **Title** | Display title |
| **Sort Title** | Title used for sorting |
| **Year** | Release year |
| **Content Rating** | Age rating (PG, R, etc.) |
| **Summary** | Description/synopsis |
| **Genres** | Comma-separated list |
| **Labels** | Custom Plex labels |

### Advanced Fields

Expand "Advanced Metadata" for:
- Studio
- Tagline
- Critic Rating
- Audience Rating
- Original Title

### Generating YAML

Click **Generate YAML** to create a metadata file snippet for your changes. Copy this to your metadata YAML files.

---

## Advanced Operations

Bulk operations for library maintenance.

### Title Operations

| Operation | Description |
|-----------|-------------|
| **Remove Title Parentheses** | Strip (1999), (Remastered), etc. from titles |
| **Split Duplicates** | Separate incorrectly merged items |

### Music Library Operations

| Operation | Description |
|-----------|-------------|
| **Update Blank Track Titles** | Set track titles from filenames |
| **Remove Album Parentheses** | Clean album/track titles |

### Asset Operations

| Operation | Description |
|-----------|-------------|
| **Assets for All** | Apply poster/background assets to all items |
| **Delete Unmanaged** | Remove collections not managed by Kometa |

### Backup & Maintenance

| Operation | Description |
|-----------|-------------|
| **Metadata Backup** | Create YAML backup of all metadata |
| **Delete Small Collections** | Remove collections with few items |
| **Mass Date Update** | Bulk update release dates |

### Genre & Label Sync

| Operation | Description |
|-----------|-------------|
| **Mass Genre Update** | Sync genres from TMDb/TVDb/IMDb |
| **IMDb Parental Labels** | Add parental guidance labels |

---

## Notifications

Get notified about Kometa runs via webhooks.

### Quick Setup

Click a template to configure webhooks for:
- **Discord** - Discord channel webhooks
- **Slack** - Slack incoming webhooks
- **Teams** - Microsoft Teams webhooks
- **Custom** - Any webhook URL

### Event Types

Enable notifications for specific events:

| Event | Description |
|-------|-------------|
| **Run Started** | When Kometa begins execution |
| **Run Completed** | When Kometa finishes successfully |
| **Errors** | When errors occur during runs |
| **Collection Changes** | When collections are modified |
| **Deletions** | When collections are removed |
| **New Version** | When a Kometa update is available |

### Testing Webhooks

Click **Test** next to any webhook to send a test notification and verify it's working.

### Additional Services

Configure dedicated notification services:
- **Notifiarr** - Unified notification service
- **Gotify** - Self-hosted push notifications
- **ntfy** - Simple pub-sub notifications

---

## Overlay Preview

Preview how overlays will look on your media posters.

### Loading Overlays

1. Go to the **Overlays** tab
2. Select an overlay file from the dropdown
3. Browse available overlays
4. Click overlays to add them to the preview

### Preview Options

- **Canvas Type** - Poster (2:3) or Background (16:9)
- **Poster Source** - Sample images, Plex posters, or TMDb posters
- **Overlay Stacking** - Layer multiple overlays

### Generating Preview

Click **Generate Preview** to see how your selected overlays will appear on the chosen poster.

---

## Running Kometa

### Run Modes

| Mode | Description |
|------|-------------|
| **Dry Run** | Preview changes without applying them |
| **Full Run** | Apply all changes to your library |

### Starting a Run

1. Go to the **Run** tab
2. Select run mode (Dry Run recommended first)
3. Optionally filter by:
   - Specific libraries
   - Specific collections
   - Run type (collections, overlays, operations)
4. Click **Start Run**

### Monitoring Progress

- View real-time logs in the **Logs** tab
- See progress indicators for each phase
- Cancel runs if needed with **Stop Run**

### Run History

View past runs with:
- Start/end times
- Duration
- Status (success/failure/cancelled)
- Full logs for each run

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `T` | Toggle light/dark theme |
| `?` | Show keyboard shortcuts help |
| `Esc` | Close modals/dialogs |
| `Ctrl+S` | Save current configuration |
| `Ctrl+Z` | Undo last change (in YAML editor) |

---

## Troubleshooting

### Common Issues

**"Plex connection failed"**
- Verify your Plex URL is accessible
- Check your Plex token is valid
- Ensure the Plex server is running

**"TMDb API error"**
- Verify your TMDb API key
- Check your API rate limits

**"Configuration invalid"**
- Check the validation messages for specific errors
- Ensure all required fields are filled
- Verify YAML syntax is correct

### Getting Help

- [Kometa Wiki](https://kometa.wiki/) - Full documentation
- [GitHub Issues](https://github.com/Kometa-Team/Kometa/issues) - Report bugs
- [Discord Server](https://kometa.wiki/en/latest/discord/) - Community support

---

## Related Documentation

- [API Integration Guide](./API_INTEGRATION.md) - Backend API details
- [Style Guide](./STYLE_GUIDE.md) - UI component documentation
- [Feature Roadmap](./FEATURE_ROADMAP.md) - Implementation history
