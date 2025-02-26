---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/content_rating.md"
    replace='{
        "COLLECTION": "MyAnimeList Content Rating", 
        "CODE_NAME": "content_rating_mal",
        "SHORT_NAME": "MyAnimeList",
        "LIBRARY_TYPE": "Movie, Show",
        "EXAMPLE_NAME": "PG-13 Shows",
        "EXAMPLE1": "PG-13",
        "EXAMPLE2": "G"
    }'
    replace-tags='{
        "rec-sub": "Recommendations: Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with 
`mal` to update Plex to the MyAnimeList Content Rating."
    }'
    rewrite-relative-urls=false
%}