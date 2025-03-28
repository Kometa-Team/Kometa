---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/content_rating.md"
    replace='{
        "COLLECTION": "DE Content Rating", 
        "CODE_NAME": "content_rating_de",
        "SHORT_NAME": "German",
        "PLEX_NAME": "Germany",
        "LIBRARY_TYPE": "Movie, Show",
        "EXAMPLE_NAME": "BPjM Movies",
        "EXAMPLE1": "BPjM",
        "EXAMPLE2": "X"
    }'
    rewrite-relative-urls=false
%}

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/both/content_rating_de.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/both/content_rating_de.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
