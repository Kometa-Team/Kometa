---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/content_rating.md"
    replace='{
        "COLLECTION": "Common Sense Media Content Rating", 
        "CODE_NAME": "content_rating_cs",
        "SHORT_NAME": "Common Sense",
        "LIBRARY_TYPE": "Movie, Show",
        "EXAMPLE_NAME": "Age 5+ Movies",
        "EXAMPLE1": "5",
        "EXAMPLE2": "G"
    }'
    replace-tags='{
        "rec-sub": "Recommendation: Use the [Mass Content Rating Update Library Operation](../../config/operations.md#mass-content-rating-update) with either 
`mdb_commonsense` or `mdb_commonsense0` to update Plex to the Common Sense Rating."
    }'
    rewrite-relative-urls=false
%}

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/both/content_rating_cs.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/both/content_rating_cs.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
