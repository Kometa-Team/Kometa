---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/content_rating.md"
    replace='{
        "COLLECTION": "UK Content Rating", 
        "CODE_NAME": "content_rating_uk",
        "SHORT_NAME": "UK",
        "PLEX_NAME": "United Kingdom",
        "LIBRARY_TYPE": "Movie, Show",
        "EXAMPLE_NAME": "15 Movies",
        "EXAMPLE1": "15",
        "EXAMPLE2": "de/15X"
    }'
    rewrite-relative-urls=false
%}

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/both/content_rating_uk.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/both/content_rating_uk.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
