---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/content_rating.md"
    replace='{
        "COLLECTION": "NZ Content Rating", 
        "CODE_NAME": "content_rating_nz",
        "SHORT_NAME": "New Zealand",
        "PLEX_NAME": "New Zealand",
        "LIBRARY_TYPE": "Movie, Show",
        "EXAMPLE_NAME": "G Movies",
        "EXAMPLE1": "G",
        "EXAMPLE2": "PG-13"
    }'
    rewrite-relative-urls=false
%}

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/both/content_rating_nz.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/both/content_rating_nz.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
