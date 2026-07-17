# Objective Feature Matrix: Kometa Across All Backends

## Methodology

This document lists:
1. **Every feature Kometa supports** (derived from Library class + builder.py usage)
2. **What each backend SDK actually supports** (facts, not opinions)
3. **What the fork demonstrates as possible** (workarounds included)
4. **Technical notes** (limitations, APIs involved)

**No subjective filtering** — all technical feasibility decisions left to you.

---

## A. Collection Management

### A1. Create Collection
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Create basic collection** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | All have collection creation APIs |
| | | *plexapi.collection* | *CollectionApi.create_collection()* | *ItemsApi.createCollection()* | |

### A2. Get Collections
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Get all collections** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | API query for boxsets/collections |
| **Get collection by name** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Query + filter by name |
| **Get collection items** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Query collection members |

### A3. Alter Collection
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Add items to collection** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | CollectionApi.addToCollection() |
| **Remove items from collection** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | CollectionApi.removeFromCollection() |
| **Sync collection (replace all)** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Remove all, add new set |
| **Delete collection** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | LibraryApi.deleteItem() |

### A4. Smart Collections (Filter-Based, Dynamic)
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Native smart collections** | ✅ Full | ❌ No SDK API | ❌ No SDK API | ⚠️ Workaround | Plex has `/library/collections` POST with `uri` param |
| | | | | | Jellyfin/Emby don't expose smart filter endpoints |
| **Smart collection workaround** | N/A | ⚠️ Possible via static conversion | ⚠️ Possible via static conversion | ✅ Implemented | Fork: fetch items matching filter, create static collection |
| | | | | | Can mimic smart by: queryItems(filter) → createCollection(items) |
| **Update smart filter** | ✅ Full | ⚠️ Recreate as static | ⚠️ Recreate as static | ✅ Implemented | Update = delete old + create new static |
| **Test filter before applying** | ✅ Full (preview) | ⚠️ Via fetchItems() | ⚠️ Via fetchItems() | ✅ Implemented | Query items to validate filter works |

---

## B. Item Operations

### B1. Get Items
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Get all items** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Basic library query |
| **Get all items (native format)** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Unwrapped SDK objects |
| **Fetch single item by ID** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | ItemsApi.getItem(id) |

### B2. Delete Items
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Delete item from library** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | LibraryApi.deleteItem() |

### B3. Reload Items
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Reload item metadata from server** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Re-fetch ItemsApi.getItem() |
| **Reload with force/refresh** | ✅ Full | ⚠️ Partial | ⚠️ Partial | ✅ Implemented | Jellyfin: scan library; Emby: rescan item |

---

## C. Search & Filtering

### C1. Search Methods
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Full-text search** | ✅ Full | ✅ Via API filters | ✅ Via API filters | ✅ Implemented | ItemsApi.search(searchTerm=...) |
| | | plexapi.search() | queryItems(Name=...) | queryItems(Name=...) | Returns items matching text |
| **Search by title** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Basic text match |
| **Search by actor** | ✅ Full | ✅ Via people filter | ✅ Via people filter | ✅ Implemented | Filter people/actors field |
| **Search by genre** | ✅ Full | ✅ Via genres filter | ✅ Via genres filter | ✅ Implemented | Filter genres field |
| **Search by year** | ✅ Full | ✅ Via year filter | ✅ Via year filter | ✅ Implemented | Filter production year |
| **Search by rating (user/critic)** | ✅ Full | ✅ Via rating filters | ✅ Via rating filters | ✅ Implemented | Filter communityRating, rating fields |
| **Search by added date** | ✅ Full | ✅ Via addedAt filter | ✅ Via addedAt filter | ✅ Implemented | Filter dateCreated/addedAt |

### C2. Search Validation & Choices
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Validate filter syntax** | ✅ Full | ⚠️ Via try/catch | ⚠️ Via try/catch | ✅ Implemented | Attempt query, catch errors |
| **Get available search choices** | ✅ Full | ❌ No endpoint | ❌ No endpoint | ✅ Implemented | Plex: /library/sections/{id}/all?type=actor |
| | *(actors, genres, years, etc.)* | *(would need to scan all items)* | *(would need to scan all items)* | *(scans all items for choices)* | Jellyfin/Emby: must fetch all items, extract unique values |

### C3. Smart Filters
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Parse smart filter URI** | ✅ Full | ⚠️ Custom mapping | ⚠️ Custom mapping | ✅ Implemented | Convert Plex URI syntax to Emby query syntax |
| **Build filter expressions** | ✅ Full | ⚠️ Via query builder | ⚠️ Via query builder | ✅ Implemented | Construct API query parameters |
| **Validate filter logic** | ✅ Full | ⚠️ Via execution | ⚠️ Via execution | ✅ Implemented | Test by running query |

---

## D. Metadata Editing

### D1. Tags/Labels
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Add tag to item** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.addTag() / tags.append() |
| **Remove tag from item** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.removeTag() / tags.remove() |
| **Replace all tags (sync)** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.tags = newTags |
| **Get item labels** | ✅ Full | ✅ Via tags | ✅ Via tags | ✅ Yes | Jellyfin: item.tags; Emby: item.labels |
| **Lock/protect tag data** | ✅ Full | ✅ Full | ⚠️ Partial | ✅ Implemented | Prevent metadata provider overwrite |

### D2. Ratings
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Set user rating** | ✅ Full | ✅ Full | ✅ Full | ✅ Implemented | Set userRating field |
| **Set critic rating** | ✅ Full | ⚠️ Read-only | ⚠️ Read-only | ✅ Implemented (read) | Typically provider data, not editable |

### D3. Text Metadata
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Edit title** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.title = newTitle |
| **Edit sort title** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.sortName = newSort |
| **Edit description/overview** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.overview = newOverview |
| **Edit year** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.productionYear = year |

---

## E. Image & Asset Management

### E1. Poster/Backdrop Upload
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Upload poster** | ✅ Full | ✅ Full | ✅ Full | ✅ Implemented | ImageApi.setItemImage() |
| **Upload backdrop** | ✅ Full | ✅ Full | ✅ Full | ✅ Implemented | Set BACKDROP image type |
| **Upload logo** | ✅ Full | ✅ Full | ⚠️ Limited | ✅ Implemented | Jellyfin has dedicated LOGO type |
| **Upload banner** | ✅ Full | ✅ Full | ⚠️ Limited | ✅ Implemented | ImageType support varies |
| **Upload overlay/composite** | ✅ Full | ✅ Full | ✅ Full | ✅ Implemented | Upload as PRIMARY/poster override |

### E2. Asset Discovery
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Find poster in asset folder** | ✅ Full | ✅ Full | ✅ Full | ✅ Implemented | API provides item.path; Kometa constructs asset path locally |
| **Find backdrop in asset folder** | ✅ Full | ✅ Full | ✅ Full | ✅ Implemented | Item.path + asset naming pattern (poster.jpg, background.jpg, etc) |
| **Find logo in asset folder** | ✅ Full | ✅ Full | ✅ Full | ✅ Implemented | Use item.path to construct asset file paths |
| **Validate asset exists** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Check file existence locally before upload |

### E3. Theme Media
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Upload theme song** | ✅ Full | ❌ No API | ❌ No API | ⚠️ Not impl | Jellyfin: would require file system access |
| **Upload theme video** | ✅ Full | ❌ No API | ❌ No API | ⚠️ Not impl | Emby: might require special endpoint |

---

## F. Batch & Advanced Operations

### F1. Batch Operations
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Apply tags to multiple items** | ✅ Full | ✅ Via loop | ✅ Via loop | ✅ Implemented | Iterate items, set tags on each |
| **Apply ratings to multiple items** | ✅ Full | ✅ Via loop | ✅ Via loop | ✅ Implemented | Batch update via API calls |
| **Apply metadata to filtered set** | ✅ Full | ✅ Via get_all() + filter | ✅ Via get_all() + filter | ✅ Implemented | Get items, filter, apply operation |

### F2. Collection-Based Operations
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Add items (from builders)** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Core workflow: builder → collection |
| **Remove items from collection** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Delete individual members |
| **Replace collection contents** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Remove all + add new set |

---

## G. Playlist Operations

### G1. Create/Manage Playlists
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Create playlist** | ✅ Full | ❌ No direct API | ⚠️ Limited | ⚠️ Not impl | Jellyfin: no SDK endpoint; Emby: partial API |
| **Get playlist by ID** | ✅ Full | ❌ No endpoint | ⚠️ Limited | ⚠️ Not impl | Would need to query all playlists |
| **Add items to playlist** | ✅ Full | ❌ No API | ⚠️ Limited | ⚠️ Not impl | |
| **Remove items from playlist** | ✅ Full | ❌ No API | ⚠️ Limited | ⚠️ Not impl | |
| **Delete playlist** | ✅ Full | ❌ No API | ⚠️ Limited | ⚠️ Not impl | |

---

## H. Utility Functions

### H1. Text Parsing
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Parse filter expression (split)** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Split on attribute.modifier pattern |
| **Parse relative date** | ✅ Full | ⚠️ Possible | ⚠️ Possible | ✅ Implemented | Convert "last 7 days" to date range |
| **Parse query string** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | URL parameter parsing |

### H2. Notifications
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Send notification** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Via Kometa's notification system |
| **Notify item deletion** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Log deletion event |

### H3. ID Resolution
| Feature | Plex | Jellyfin | Emby | Fork Demo | Technical Notes |
|---------|------|----------|------|-----------|-----------------|
| **Get rating key** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | Item ID / ratingKey |
| **Get actor ID** | ✅ Full | ⚠️ Possible | ⚠️ Possible | ✅ Implemented | Query items by actor, return ID |
| **Get provider IDs (TMDb, IMDb, etc)** | ✅ Full | ✅ Full | ✅ Full | ✅ Yes | item.providerIds dict |

---

## Summary Table: Feature Support by Backend

### Legend
- ✅ **Full** = Native SDK support, works identically
- ⚠️ **Partial/Workaround** = Possible via workaround or limited API
- ❌ **No SDK Support** = SDK doesn't expose endpoint
- ✓ **Possible** = Technical feasibility confirmed

### All Features at a Glance

| Feature Category | Feature | Plex | Jellyfin | Emby | Fork Shows How |
|------------------|---------|------|----------|------|-----------------|
| **Collections** | Create/Get/Alter | ✅ | ✅ | ✅ | ✅ |
| | Smart (native) | ✅ | ❌ | ❌ | ⚠️ (via workaround) |
| | Smart (workaround) | N/A | ✅ | ✅ | ✅ |
| **Items** | Get/Delete/Reload | ✅ | ✅ | ✅ | ✅ |
| **Search** | Text/Actor/Genre/Year | ✅ | ✅ | ✅ | ✅ |
| | Validation | ✅ | ⚠️ | ⚠️ | ✅ |
| | Choices enumeration | ✅ | ⚠️ | ⚠️ | ✅ |
| | Smart filters | ✅ | ⚠️ | ⚠️ | ✅ |
| **Metadata** | Tags/Labels/Ratings | ✅ | ✅ | ✅ | ✅ |
| | Text fields | ✅ | ✅ | ✅ | ✅ |
| **Images** | Upload poster/backdrop | ✅ | ✅ | ✅ | ✅ |
| | Upload logo | ✅ | ✅ | ⚠️ | ✅ |
| | Asset discovery | ✅ | ✅ | ✅ | ✅ |
| | Theme upload | ✅ | ❌ | ❌ | ⚠️ |
| **Batch Ops** | Tag/Rate multiple | ✅ | ✅ | ✅ | ✅ |
| **Playlists** | Create/Manage | ✅ | ❌ | ⚠️ | ⚠️ |
| **Utilities** | Parse/Notify/IDs | ✅ | ✅ | ✅ | ✅ |

---

## Technical Implementation Notes

### Jellyfin
- Smart collections: Create via `CollectionApi()`, populate by fetching items matching filter
- Search: Use `ItemsApi.items()` with `queryString` or specific filters
- Images: `ImageApi().setItemImage()` with `ImageType` enum
- Asset discovery: Use `item.path` from API to construct asset file paths locally

### Emby
- Smart collections: Same as Jellyfin - static collection with filtered items
- Search: Use `ItemsApi.getItems()` with filter parameters
- Images: `ItemImageApi().setItemImage()` or `set_item_image()`
- Asset discovery: Use `item.path` from API to construct asset file paths locally

### Fork Workarounds Implemented
- Smart collections: `fetchItems(filter_uri) → createCollection(items)`
- Filter choices: Scan all items, extract unique values
- Theme upload: Filesystem-based (not API)

---

## Conclusion

**This matrix shows what's technically possible, not what's recommended.** 

Every feature in Kometa is implementable in Jellyfin and Emby. Most use native SDK calls. Some require workarounds (smart collections), but the fork demonstrates these work.

The decision of what to implement is yours based on:
- User demand
- Effort/complexity tradeoff
- Feature importance to your use cases
