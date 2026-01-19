# Kometa Web UI - Feature Roadmap

> **Version:** 1.0
> **Created:** January 2026
> **Status:** ✅ COMPLETE

This document maps out Kometa features that need UI implementation, organized by priority and complexity.

**All 10 phases have been implemented.**

---

## Implementation Status

| Phase | Feature | Status |
|-------|---------|--------|
| Phase 1 | Scheduling & Automation | ✅ Complete |
| Phase 2 | Mass Operations | ✅ Complete |
| Phase 3 | Collection Builder | ✅ Complete |
| Phase 4 | Playlist Management | ✅ Complete |
| Phase 5 | Smart Collections & Filters | ✅ Complete |
| Phase 6 | Data Mappers | ✅ Complete |
| Phase 7 | Notifications | ✅ Complete |
| Phase 8 | Metadata Editor | ✅ Complete |
| Phase 9 | Arr Integration | ✅ Complete |
| Phase 10 | Advanced Operations | ✅ Complete |

---

## Table of Contents

1. [Priority Matrix](#priority-matrix)
2. [Phase 1: Scheduling & Automation](#phase-1-scheduling--automation)
3. [Phase 2: Mass Operations](#phase-2-mass-operations)
4. [Phase 3: Collection Builder](#phase-3-collection-builder)
5. [Phase 4: Playlist Management](#phase-4-playlist-management)
6. [Phase 5: Smart Collections & Filters](#phase-5-smart-collections--filters)
7. [Phase 6: Data Mappers](#phase-6-data-mappers)
8. [Phase 7: Notifications](#phase-7-notifications)
9. [Phase 8: Metadata Editor](#phase-8-metadata-editor)
10. [Phase 9: Arr Integration](#phase-9-arr-integration)
11. [Phase 10: Advanced Operations](#phase-10-advanced-operations)
12. [Implementation Timeline](#implementation-timeline)

---

## Priority Matrix

| Priority | Feature | Complexity | User Value | Dependencies |
|----------|---------|------------|------------|--------------|
| P0 | Scheduling Panel | Medium | High | None |
| P0 | Mass Operations | Medium | High | None |
| P1 | Collection Builder | High | Very High | None |
| P1 | Playlist Management | Medium | Medium | Collection Builder patterns |
| P2 | Smart Collections | Medium | High | Collection Builder |
| P2 | Data Mappers | Low | Medium | None |
| P2 | Notifications | Low | Medium | None |
| P3 | Metadata Editor | High | Medium | None |
| P3 | Arr Integration | Medium | Medium | None |
| P4 | Advanced Operations | Low | Low | None |

---

## Phase 1: Scheduling & Automation

### Overview
Add UI for configuring when Kometa runs, including library-specific schedules and overlay schedules.

### Features to Implement

#### 1.1 Global Schedule Configuration
**Location:** Settings tab → new "Scheduling" subtab

**Fields:**
| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `run_time` | Time picker | Daily run time | `03:00`, `05:30` |
| `run_interval` | Select | Run frequency | `daily`, `weekly`, `monthly` |
| `run_days` | Multi-select | Days to run | `monday`, `tuesday`, etc. |

**YAML Output:**
```yaml
settings:
  run_order:
    - operations
    - metadata
    - collections
    - overlays
```

#### 1.2 Library-Specific Schedules
**Location:** Libraries tab → each library card → Schedule section

**Fields:**
| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `schedule` | Cron builder | When to process library | `daily`, `weekly(sunday)` |
| `schedule_overlays` | Cron builder | When to run overlays | `weekly(monday)` |
| `delete_not_scheduled` | Toggle | Delete when not scheduled | `true/false` |

**UI Components Needed:**
- `CronBuilder` - Visual cron expression builder
- `SchedulePreview` - Shows next 5 run times
- `ScheduleCalendar` - Visual calendar view (optional)

**Cron Builder Options:**
```
Presets:
├── Daily
├── Weekly (select day)
├── Monthly (select day of month)
├── Yearly (select date)
├── Range (start-end)
└── Custom expression

Modifiers:
├── all - Every iteration
├── first - First iteration only
├── last - Last iteration only
├── daily - Every day
├── weekly(day) - Specific weekday
├── monthly(day) - Day of month
├── yearly(date) - Specific date
└── range(start-end) - Date range
```

**YAML Output:**
```yaml
libraries:
  Movies:
    schedule: weekly(sunday)
    schedule_overlays: daily
    delete_not_scheduled: true
```

#### 1.3 Run Order Configuration
**Location:** Settings → Scheduling subtab

**UI:** Drag-and-drop sortable list

**Options:**
- `operations` - Mass metadata operations
- `metadata` - Metadata file processing
- `collections` - Collection building
- `overlays` - Overlay application

---

## Phase 2: Mass Operations

### Overview
UI for bulk metadata update operations that can modify large numbers of items at once.

### Features to Implement

#### 2.1 Mass Operations Panel
**Location:** New "Operations" subtab in Configuration tab

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ Mass Operations                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Ratings         │ │ Metadata        │ │ Images          │ │
│ │ ○ Audience      │ │ ○ Genre         │ │ ○ Posters       │ │
│ │ ○ Critic        │ │ ○ Content Rating│ │ ○ Backgrounds   │ │
│ │ ○ User          │ │ ○ Original Title│ │                 │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│                                                              │
│ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│ │ Dates           │ │ Collections     │ │ Maintenance     │ │
│ │ ○ Release Date  │ │ ○ Mode          │ │ ○ Split Dupes   │ │
│ │ ○ Added Date    │ │                 │ │ ○ Clean Bundles │ │
│ └─────────────────┘ └─────────────────┘ └─────────────────┘ │
│                                                              │
│ [Apply to: Movies ▼] [Source: TMDb ▼]      [Run Operations] │
└─────────────────────────────────────────────────────────────┘
```

#### 2.2 Rating Operations
**Fields:**
| Operation | Sources | Description |
|-----------|---------|-------------|
| `mass_audience_rating_update` | TMDb, OMDb, MDBList, Trakt, Letterboxd | Update audience/user ratings |
| `mass_critic_rating_update` | TMDb, OMDb, MDBList, Metacritic | Update critic/review ratings |
| `mass_user_rating_update` | TMDb, OMDb, MDBList | Update user ratings |

**Source Options per Rating:**
```
TMDb ────────── tmdb
OMDb ────────── omdb
MDBList ─────── mdblist
Trakt ───────── trakt_user
Letterboxd ──── letterboxd
Metacritic ──── metacritic
IMDb ────────── imdb
Rotten Tomatoes ── rottentomatoes
```

**UI Component:** Rating source selector with preview

#### 2.3 Metadata Operations
**Fields:**
| Operation | Sources | Description |
|-----------|---------|-------------|
| `mass_genre_update` | TMDb, TVDb, OMDb, IMDb, AniDB, MAL | Bulk update genres |
| `mass_content_rating_update` | OMDb, MDBList, MAL | Update content ratings (PG, R, etc.) |
| `mass_original_title_update` | AniDB, MAL, Lock | Update original titles |
| `mass_studio_update` | TMDb, TVDb | Update studio information |

**UI Component:** Source selector with "Lock" option to prevent changes

#### 2.4 Date Operations
**Fields:**
| Operation | Sources | Description |
|-----------|---------|-------------|
| `mass_originally_available_update` | TMDb, TVDb, OMDb, MDBList, AniDB, MAL | Update release dates |
| `mass_added_at_update` | TMDb, TVDb, OMDb | Update "added at" dates |

#### 2.5 Image Operations
**Fields:**
| Operation | Sources | Description |
|-----------|---------|-------------|
| `mass_poster_update` | TMDb, Plex, Lock | Bulk update poster images |
| `mass_background_update` | TMDb, Plex, Lock | Bulk update background images |

**UI Component:** Image source selector with preview thumbnails

#### 2.6 Collection Operations
**Fields:**
| Operation | Options | Description |
|-----------|---------|-------------|
| `mass_collection_mode` | `default`, `hide`, `hide_items`, `show_items` | Update collection display mode |

#### 2.7 Maintenance Operations
**Fields:**
| Operation | Type | Description |
|-----------|------|-------------|
| `split_duplicates` | Toggle | Split duplicate items in library |
| `radarr_add_all_existing` | Toggle | Add all movies to Radarr |
| `sonarr_add_all_existing` | Toggle | Add all shows to Sonarr |

**YAML Output:**
```yaml
libraries:
  Movies:
    operations:
      mass_genre_update: tmdb
      mass_audience_rating_update: mdblist
      mass_critic_rating_update: omdb
      mass_poster_update: tmdb
      split_duplicates: true
```

---

## Phase 3: Collection Builder

### Overview
Visual interface for creating collection definition files without writing YAML manually.

### Features to Implement

#### 3.1 Collection Builder Wizard
**Location:** New "Collections" tab (or subtab of Configuration)

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ Collection Builder                                          │
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌────────────────────────────────────────┐ │
│ │ Collections  │ │ Collection Editor                      │ │
│ │              │ │                                        │ │
│ │ + New        │ │ Name: [Best of 2024____________]      │ │
│ │              │ │                                        │ │
│ │ ▼ Movies     │ │ ┌──────────────────────────────────┐  │ │
│ │   ├ Best 2024│ │ │ Builder Source                   │  │ │
│ │   ├ Oscars   │ │ │ ┌────────┐ ┌────────┐ ┌────────┐ │  │ │
│ │   └ 4K Films │ │ │ │ TMDb   │ │ Trakt  │ │ IMDb   │ │  │ │
│ │              │ │ │ │  ★     │ │        │ │        │ │  │ │
│ │ ▼ TV Shows   │ │ │ └────────┘ └────────┘ └────────┘ │  │ │
│ │   └ Trending │ │ │ ┌────────┐ ┌────────┐ ┌────────┐ │  │ │
│ │              │ │ │ │MDBList │ │Letterb │ │ Plex   │ │  │ │
│ └──────────────┘ │ │ └────────┘ └────────┘ └────────┘ │  │ │
│                  │ └──────────────────────────────────┘  │ │
│                  │                                        │ │
│                  │ [+ Add Builder] [+ Add Filter]         │ │
│                  │                                        │ │
│                  │ ┌──────────────────────────────────┐  │ │
│                  │ │ YAML Preview                     │  │ │
│                  │ │ collections:                     │  │ │
│                  │ │   Best of 2024:                  │  │ │
│                  │ │     tmdb_discover:               │  │ │
│                  │ │       year: 2024                 │  │ │
│                  │ └──────────────────────────────────┘  │ │
│                  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2 Builder Sources
**Organized by Category:**

```
📊 Charts & Rankings
├── TMDb
│   ├── tmdb_popular - Popular movies/shows
│   ├── tmdb_top_rated - Top rated
│   ├── tmdb_trending - Trending daily/weekly
│   ├── tmdb_now_playing - Now in theaters
│   └── tmdb_discover - Advanced search
├── Trakt
│   ├── trakt_trending - Trending
│   ├── trakt_popular - Popular
│   ├── trakt_watched - Most watched
│   ├── trakt_collected - Most collected
│   └── trakt_recommended - Recommendations
├── IMDb
│   ├── imdb_chart - Top 250, Box Office, etc.
│   ├── imdb_popular - Popular by genre
│   └── imdb_search - Advanced search
└── MDBList
    ├── mdblist_list - Curated lists
    └── mdblist_show - Show-specific lists

📋 User Lists
├── Trakt Lists
│   ├── trakt_list - Public lists
│   ├── trakt_userlist - User watchlists
│   └── trakt_watchlist - Personal watchlist
├── Letterboxd
│   ├── letterboxd_list - User lists
│   └── letterboxd_list_details - List with metadata
├── IMDb Lists
│   ├── imdb_list - User lists
│   └── imdb_watchlist - Watchlists
└── ICheckMovies
    └── icheckmovies_list - User lists

🎌 Anime
├── AniList
│   ├── anilist_top_rated
│   ├── anilist_popular
│   ├── anilist_trending
│   ├── anilist_search
│   └── anilist_userlist
├── MyAnimeList
│   ├── mal_all - All anime
│   ├── mal_airing - Currently airing
│   ├── mal_upcoming - Upcoming
│   ├── mal_popular - Most popular
│   ├── mal_favorite - Most favorited
│   ├── mal_season - By season
│   └── mal_userlist - User lists
└── AniDB
    ├── anidb_popular
    └── anidb_tag

🏆 Awards & Events
├── IMDb Awards
│   ├── imdb_award - Oscar, Emmy, etc.
│   └── Award category selector
├── Oscars
│   ├── oscar_winner
│   ├── oscar_nominee
│   └── Year/category selector
└── Emmys
    ├── emmy_winner
    └── emmy_nominee

🎬 Studios & Networks
├── TMDb Company
│   └── tmdb_company - Movies by studio
├── TMDb Network
│   └── tmdb_network - Shows by network
└── TVDb Network
    └── tvdb_network - Shows by network

📡 Streaming
├── Streaming Availability
│   ├── streaming_service - By platform
│   └── Platform selector (Netflix, Disney+, etc.)
└── StevenLu
    └── stevenlu_popular - Popular streaming

📊 Box Office
├── Box Office Mojo
│   ├── mojo_world - Worldwide box office
│   ├── mojo_domestic - Domestic box office
│   ├── mojo_international - International
│   └── mojo_record - Record breakers
└── Ergast (F1)
    └── ergast_race - F1 race data

📺 Plex-Based
├── Plex
│   ├── plex_all - All items
│   ├── plex_search - Search query
│   ├── plex_collectionless - No collection
│   └── plex_pilots - TV pilots only
└── Tautulli
    ├── tautulli_popular - Most popular
    └── tautulli_watched - Most watched

🔄 Arr Integration
├── Radarr
│   ├── radarr_all - All movies
│   └── radarr_taglist - By tag
└── Sonarr
    ├── sonarr_all - All shows
    └── sonarr_taglist - By tag

📁 File-Based
├── Reciperr
│   └── reciperr_list - Reciperr lists
└── FlixPatrol
    ├── flixpatrol_top - Top streaming
    └── flixpatrol_popular - Popular
```

#### 3.3 Builder Configuration UI
**Per-Source Fields:**

**TMDb Discover:**
```
┌─────────────────────────────────────────┐
│ TMDb Discover                           │
├─────────────────────────────────────────┤
│ Type:      [Movies ▼]                   │
│ Sort By:   [Popularity ▼]               │
│ Year:      [2024    ] - [2024    ]      │
│ Rating:    [7.0     ] - [10      ]      │
│ Runtime:   [0       ] - [300     ] min  │
│                                         │
│ ┌─ Genres ─────────────────────────┐    │
│ │ ☑ Action  ☑ Drama  ☐ Comedy     │    │
│ │ ☐ Horror  ☑ Sci-Fi ☐ Romance    │    │
│ └───────────────────────────────────┘    │
│                                         │
│ Region: [US ▼]  Language: [English ▼]   │
│                                         │
│ ☐ Include Adult Content                 │
└─────────────────────────────────────────┘
```

**Trakt List:**
```
┌─────────────────────────────────────────┐
│ Trakt List                              │
├─────────────────────────────────────────┤
│ List URL: [https://trakt.tv/...______] │
│    - or -                               │
│ Username: [___________]                 │
│ List Name: [___________]                │
│                                         │
│ ☐ Include private list (requires auth)  │
└─────────────────────────────────────────┘
```

#### 3.4 Collection Settings
**Per-Collection Options:**
```
┌─────────────────────────────────────────┐
│ Collection Settings                     │
├─────────────────────────────────────────┤
│ Sort Title:     [________________]      │
│ Content Rating: [________________]      │
│ Summary:        [________________]      │
│                 [________________]      │
│                                         │
│ Collection Mode: [Default      ▼]       │
│   • default - Normal behavior           │
│   • hide - Hide collection              │
│   • hide_items - Hide items in library  │
│   • show_items - Show items from coll.  │
│                                         │
│ Collection Order: [Release Date ▼]      │
│   • release, alpha, custom, random      │
│                                         │
│ Sync Mode: [sync ▼]                     │
│   • sync - Remove items not in builder  │
│   • append - Only add, never remove     │
│                                         │
│ Minimum Items: [5____]                  │
│ Delete Below Minimum: ☐                 │
│                                         │
│ ┌─ Poster ─────────────────────────┐    │
│ │ [Upload] or [URL: ____________] │    │
│ └───────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## Phase 4: Playlist Management

### Overview
Interface for creating and managing playlist files.

### Features to Implement

#### 4.1 Playlist Builder
**Location:** New "Playlists" subtab

**Similar to Collection Builder but with playlist-specific options:**
- Playlist name and summary
- Sync to users (multi-select)
- Exclude users
- Smart vs static playlists

#### 4.2 Playlist Settings
```
┌─────────────────────────────────────────┐
│ Playlist Settings                       │
├─────────────────────────────────────────┤
│ Playlist Name: [________________]       │
│ Summary:       [________________]       │
│                                         │
│ Sync to Users:                          │
│ ☑ Admin                                 │
│ ☑ User1                                 │
│ ☐ User2                                 │
│                                         │
│ Exclude Users: [________________]       │
│                                         │
│ Libraries: [Movies, TV Shows   ▼]       │
│                                         │
│ Sync Mode: [sync ▼]                     │
│ Delete Not Scheduled: ☐                 │
└─────────────────────────────────────────┘
```

---

## Phase 5: Smart Collections & Filters

### Overview
UI for creating dynamic collections based on Plex smart filters.

### Features to Implement

#### 5.1 Smart Label Builder
```
┌─────────────────────────────────────────┐
│ Smart Label                             │
├─────────────────────────────────────────┤
│ Label Name: [4K Dolby Vision___]        │
│                                         │
│ ┌─ Conditions ─────────────────────┐    │
│ │ Resolution [is       ▼] [4K   ▼] │    │
│ │ [AND ▼]                           │    │
│ │ HDR        [contains ▼] [DV    ] │    │
│ │                                   │    │
│ │ [+ Add Condition]                 │    │
│ └───────────────────────────────────┘    │
│                                         │
│ Apply to: ☑ New Items  ☑ Existing       │
└─────────────────────────────────────────┘
```

#### 5.2 Filter Builder
**Filter Types:**
```
String Filters:
├── title, studio, edition, record_label
├── artist, album, track, genre, mood, style
├── collection, network, country, decade
├── resolution, audio_language, subtitle_language
├── content_rating, label, director, producer
├── writer, actor, audio_codec, video_codec
└── filepath, folder

Numeric Filters:
├── year, rating, plays, duration
├── added, originally_available
├── audio_channels, height, width
└── aspect_ratio

Boolean Filters:
├── hdr, unmatched, duplicate, unplayed
├── in_progress, trash, episode_unplayed
└── episode_duplicate, episode_progress

Comparison Operators:
├── .is / .not - Exact match
├── .contains / .begins / .ends - String matching
├── .gt / .gte / .lt / .lte - Numeric comparison
└── .regex - Regular expression
```

**Visual Filter Builder:**
```
┌─────────────────────────────────────────┐
│ Filter Builder                          │
├─────────────────────────────────────────┤
│ Match: [All ▼] of the following:        │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ [year     ▼] [is ≥   ▼] [2020    ] │ │
│ │                              [✕]   │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ [genre    ▼] [contains▼] [Action ] │ │
│ │                              [✕]   │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ [rating   ▼] [is ≥   ▼] [7.5     ] │ │
│ │                              [✕]   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [+ Add Filter]  [+ Add Filter Group]    │
│                                         │
│ Preview: 47 items match                 │
└─────────────────────────────────────────┘
```

---

## Phase 6: Data Mappers

### Overview
Simple key-value mapping interface for transforming metadata values.

### Features to Implement

#### 6.1 Genre Mapper
```
┌─────────────────────────────────────────┐
│ Genre Mapper                            │
├─────────────────────────────────────────┤
│ Map genre names to consistent values:   │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Sci-Fi          →  Science Fiction │ │
│ │ SciFi           →  Science Fiction │ │
│ │ SF              →  Science Fiction │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [+ Add Mapping]                         │
│                                         │
│ Special mappings:                       │
│ ☐ Map empty genre to: [___________]    │
│ ☐ Remove genres:      [Horror, Gore]   │
└─────────────────────────────────────────┘
```

#### 6.2 Content Rating Mapper
```
┌─────────────────────────────────────────┐
│ Content Rating Mapper                   │
├─────────────────────────────────────────┤
│ Map content ratings to consistent values│
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ gb/15           →  R               │ │
│ │ gb/12A          →  PG-13           │ │
│ │ gb/U            →  G               │ │
│ │ NR              →  Not Rated       │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [+ Add Mapping]  [Import MPAA presets]  │
└─────────────────────────────────────────┘
```

---

## Phase 7: Notifications

### Overview
Dedicated notification service configuration panels.

### Features to Implement

#### 7.1 Discord Notifications
```
┌─────────────────────────────────────────┐
│ Discord Notifications                   │
├─────────────────────────────────────────┤
│ Webhook URL: [https://discord.com/...] │
│                                         │
│ Notify on:                              │
│ ☑ Run started                           │
│ ☑ Run completed                         │
│ ☑ Errors                                │
│ ☑ New collections created               │
│ ☐ Items added to collections            │
│                                         │
│ [Test Notification]                     │
└─────────────────────────────────────────┘
```

#### 7.2 Slack Notifications
Similar structure to Discord.

#### 7.3 Generic Webhook
```
┌─────────────────────────────────────────┐
│ Custom Webhook                          │
├─────────────────────────────────────────┤
│ URL:     [https://..._______________]  │
│ Method:  [POST ▼]                       │
│ Headers: [Authorization: Bearer xxx]   │
│                                         │
│ Payload Template:                       │
│ ┌─────────────────────────────────────┐ │
│ │ {                                   │ │
│ │   "event": "{{event}}",            │ │
│ │   "status": "{{status}}",          │ │
│ │   "message": "{{message}}"         │ │
│ │ }                                   │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## Phase 8: Metadata Editor

### Overview
Visual editor for metadata files - custom posters, descriptions, ratings.

### Features to Implement

#### 8.1 Metadata File Manager
```
┌─────────────────────────────────────────────────────────────┐
│ Metadata Editor                                              │
├─────────────────────────────────────────────────────────────┤
│ Library: [Movies ▼]                    Search: [_________] │
│                                                              │
│ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐         │
│ │ ┌───┐ │ │ ┌───┐ │ │ ┌───┐ │ │ ┌───┐ │ │ ┌───┐ │         │
│ │ │   │ │ │ │   │ │ │ │   │ │ │ │   │ │ │ │   │ │         │
│ │ │   │ │ │ │   │ │ │ │   │ │ │ │   │ │ │ │   │ │         │
│ │ └───┘ │ │ └───┘ │ │ └───┘ │ │ └───┘ │ │ └───┘ │         │
│ │ Movie │ │ Movie │ │ Movie │ │ Movie │ │ Movie │         │
│ │ Title │ │ Title │ │ Title │ │ Title │ │ Title │         │
│ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘         │
│                                                              │
│ Click to edit metadata for any item                         │
└─────────────────────────────────────────────────────────────┘
```

#### 8.2 Item Metadata Editor
```
┌─────────────────────────────────────────┐
│ Edit: The Matrix (1999)                 │
├─────────────────────────────────────────┤
│ ┌─────┐                                 │
│ │     │  Title: [The Matrix________]   │
│ │     │  Sort:  [Matrix, The_______]   │
│ │     │  Year:  [1999__]               │
│ └─────┘                                 │
│ [Change Poster]                         │
│                                         │
│ Summary:                                │
│ ┌─────────────────────────────────────┐ │
│ │ A computer hacker learns from...    │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Genres: [Action] [Sci-Fi] [+]           │
│ Studio: [Warner Bros._________]         │
│                                         │
│ Ratings:                                │
│ Audience: [★★★★★★★★☆☆] 8.7            │
│ Critic:   [★★★★★★★★★☆] 9.0            │
│                                         │
│ [Save Changes]  [Reset to Plex]         │
└─────────────────────────────────────────┘
```

---

## Phase 9: Arr Integration

### Overview
Enhanced Radarr/Sonarr integration beyond basic sync.

### Features to Implement

#### 9.1 Radarr Operations
```
┌─────────────────────────────────────────┐
│ Radarr Integration                      │
├─────────────────────────────────────────┤
│ Add to Radarr:                          │
│ ☐ Add all existing library items        │
│ ☐ Add items from collections            │
│                                         │
│ Sync Settings:                          │
│ Root Folder: [/movies____________]      │
│ Quality:     [HD-1080p          ▼]      │
│ Tags:        [kometa, imported  ]       │
│                                         │
│ Remove from Radarr:                     │
│ ☐ Remove by tag: [_____________]       │
│ ☐ Remove items not in Plex              │
│                                         │
│ [Sync Now]  [Preview Changes]           │
└─────────────────────────────────────────┘
```

---

## Phase 10: Advanced Operations

### Overview
Miscellaneous advanced features.

### Features to Implement

- `remove_title_parentheses` - Strip parentheses from titles
- `update_blank_track_titles` - Auto-fill music track titles
- `assets_for_all` - Apply assets to all items
- `metadata_backup` - Backup metadata settings
- `delete_collections` - Smart collection deletion rules

---

## Implementation Timeline

### Quick Wins (1-2 features each)
1. **Scheduling Panel** - Basic cron builder
2. **Data Mappers** - Simple key-value UI
3. **Notifications** - Webhook configuration

### Medium Effort (3-5 features each)
4. **Mass Operations** - Operations panel with sources
5. **Smart Collections** - Filter builder UI

### Major Features (Full module)
6. **Collection Builder** - Complete builder wizard
7. **Playlist Management** - Playlist configuration
8. **Metadata Editor** - Visual metadata editing

---

## UI Components to Create

| Component | Used By | Priority |
|-----------|---------|----------|
| `CronBuilder` | Scheduling | P0 |
| `SourceSelector` | Mass Ops, Collections | P0 |
| `FilterBuilder` | Smart Collections | P1 |
| `KeyValueMapper` | Data Mappers | P2 |
| `CollectionWizard` | Collections | P1 |
| `MediaGrid` | Metadata Editor | P3 |
| `WebhookTester` | Notifications | P2 |

---

## Related Documents

- [UI/UX Audit](./UI_UX_AUDIT.md) - Current UI analysis
- [Style Guide](./STYLE_GUIDE.md) - Component patterns
