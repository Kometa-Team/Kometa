---
hide:
  - toc
---

# Plex Builders

Plex Builders utilize media that already exists within your Plex library to place them into a Collection.

Plex has two categories of Collections - Smart and Manual. The same search criteria can be used to build a Smart or Manual collection in most instances. 

To keep things simple we will use the term Smart Builders and Manual Builders, which refers to the criteria that is used to build the Collection.

Smart Builders use filters (rules) to build collections that match the criteria of the Builder. When new media is added to your library, or if metadata of any item in your library changes to match the Builder's rules, the media is automatically included in the collection without the need to run Kometa again. 

Manual (also known as Dumb or non-Smart) Builders are static in nature and will not dynamically update as new media is added/metadata criteria changes across your library - you will have to run Kometa any time you want the Builder to re-run.

Smart Builders are usually the recommended approach as they are lightweight and faster to process than Dumb Builders

## Understanding Smart vs Manual Collections

There are some key differences that you should understand before choosing if you want to use a Smart or Manual Builder, this table shows you the key differences between the Collections that are built from each type of Builder.

| Feature                                          | **Smart Collection**                                                                       | **Manual (Dumb) Collection**                                              |
|--------------------------------------------------|--------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| Automation                                       | Automatically includes or removes items as your library changes                            | Requires manual updates—items must be added or removed by hand            |
| Use Case                                         | Great for auto-generating groups like “Movies Released This Year” or “Top-Rated Thrillers” | Ideal for curated lists like “My Favorites” or “Family Movie Night Picks” |
| Customization                                    | Built using Plex’s filter system; limited to available filter options                      | Fully customizable—any item from the library can be included              |
| Accuracy                                         | Always reflects real-time library data based on filter criteria                            | Remains the same unless manually edited                                   |
| Icon                                             | Identified with a gear icon in the Plex UI (⚙️)                                            | No special icon—just a standard collection                                |
| Behavior After Library Scan                      | Automatically refreshes based on updated metadata                                          | No change unless edited manually                                          |
| Editing                                          | Filters can be edited to change which items are included                                   | Items must be individually added/removed                                  |
| Metadata Changes (via Refresh or Kometa updates) | Filters remain intact; collection contents may shift as metadata changes                   | Content stays fixed unless explicitly modified by scripts or user         |

There are some exceptions to the above when using a Smart Builder (namely when using a [Smart Label Definition](../../settings.md#smart-label-definitions)), but the above should offer a basic understanding of the key differences.

## Builder Attributes

The majority of Smart and Manual Builders utilize the same Builder Attributes. Any deviation from this will be highlighted against the specific Builder.

| Attribute  | Description & Values                                                                                                                                                                                                                               |
|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `limit`    | **Description:** The max number of item for the filter.<br>**Default:** `all`<br>**Values:** `all` or a number greater than 0                                                                                                                      |
| `sort_by`  | **Description:** This will control how the filter is sorted in your library. You can do a multi-level sort using a list.<br>**Default:** `random`<br>**Values:** Any sort options for your filter type in the [Sorts Options Table](#sort-options) |
| `validate` | **Description:** Determines if a collection will fail on a validation error<br>**Default:** `true`<br>**Values**: `true` or `false`                                                                                                                |

## Plex Builder Types

| Builder                                    | Description                                                                                                                                                  |             Works with Movies              |              Works with Shows              |    Works with Playlists and Custom Sort    |
|:-------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------:|:------------------------------------------:|:------------------------------------------:|
| [`smart_filter`](smart-filter.md)          | use Plex's [Advanced Filters](https://support.plex.tv/articles/201273953-collections/) to create a smart collection based on the filter parameters provided. | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`plex_all`](all.md)                       | Gets every movie/show in your library. Useful with [Filters](../../filters.md)                                                                               | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |
| [`plex_search`](search.md)                 | Gets every movie/show based on the search parameters provided                                                                                                | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`plex_watchlist`](watchlist.md)           | Gets every movie/show in your Watchlist.                                                                                                                     | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`plex_pilots`](pilots.md)                 | Gets the first episode of every show in your library                                                                                                         |  :fontawesome-solid-circle-xmark:{ .red }  | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |
| [`plex_collectionless`](collectionless.md) | Gets every movie/show that is not in a collection                                                                                                            | :fontawesome-solid-circle-check:{ .green } | :fontawesome-solid-circle-check:{ .green } |  :fontawesome-solid-circle-xmark:{ .red }  |


{%
    include-markdown "./search-options.md"
%}

{%
    include-markdown "./sort-options.md"
%}


