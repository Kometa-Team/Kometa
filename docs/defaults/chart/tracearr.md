---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Tracearr Chart",
        "CODE_NAME": "tracearr",
        "LIBRARY_TYPE": "Movie, Show",
        "DESCRIPTION": "create collections based on Tracearr watch history",
        "SECTION_NUMBER": "020"
    }'
    replace-tags='{"rec-sub": "Requirements: [Tracearr Authentication](../../config/tracearr.md)."}'
%}
| `Tracearr Popular`   | `popular`   | Collection of items watched by the most unique Tracearr users. |
| `Tracearr Watched`   | `watched`   | Collection of items with the most completed Tracearr sessions. |
| `Tracearr Trending`  | `trending`  | Collection of the most active items from the last seven days of Tracearr watch history. |
| `Tracearr Rewatched` | `rewatched` | Collection of items repeatedly played by the same Tracearr user. |
| `Tracearr Completed` | `completed` | Collection of the most recently completed items from Tracearr watch history. |
| `Tracearr Binged` | `binged` | Collection of shows with the most distinct completed episodes watched by a single Tracearr user. Show libraries only. |
| `Tracearr Most Transcoded` | `transcoded` | Collection of items with the most Tracearr sessions that required audio or video transcoding. |

{% include-markdown "./../../templates/snippets/white_style.md" replace='{"CODE_NAME": "tracearr"}' %}
{% include-markdown "./../../templates/defaults/base/mid.md" replace='{"CODE_NAME": "tracearr"}' include-tags='all|movie|show' %}

## Template Variables

Tracearr collections share the same base settings, and each collection can be customized individually by using the matching key suffix.

| Variable | Description |
|:---------|:------------|
| `list_days_<<key>>` | Number of days to look back in Tracearr history for the matching collection key. Default: `30`; `list_days_trending` defaults to `7`. |
| `list_size_<<key>>` | Maximum number of items to include in the matching collection. Default: `20` |

The `<<key>>` suffix matches the collection key from the table above, such as `popular`, `watched`, `trending`, `rewatched`, `completed`, `binged`, or `transcoded`.

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" exclude-tags="separator" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="white-style|limit|sync_mode|collection_order"
        rewrite-relative-urls=false
        replace='{"<!--limit-extra-->": "<br>**Default:** `100`", "COLLECTION_ORDER": "`custom`"}'
    %}

    {% include-markdown "./../../templates/variable_list.md" include-tags="sup1" rewrite-relative-urls=false %}

{% include-markdown "./../../templates/defaults/base/collection/shared.md" end="<!--separator-variables-->" %}
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Tracearr Chart Collections"

        The Tracearr Chart collections use [Tracearr Builders](../../../files/builders/tracearr/overview) to create the collections.
