---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/content_rating.md"
    replace='{
        "LIBRARY_TYPE": "Show",
        "Movies/Shows": "Shows",
        "movie|show": "show",
        "Movies:": "Shows:",
        "COLLECTION": "US Content Rating", 
        "CODE_NAME": "content_rating_us",
        "SHORT_NAME": "US",
        "PLEX_NAME": "United States",
        "EXAMPLE_NAME": "TV-14 Shows",
        "EXAMPLE1": "TV-14",
        "EXAMPLE2": "de/18"
    }'
    replace-tags='{
        "title-sub": "**[This file has a Movie Library Counterpart.](./../../../../movie/content_rating_us)**",
        "image": "![](../../../../assets/images/defaults/content_rating_us_show.png)"
    }'
    rewrite-relative-urls=false
%}

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/show/content_rating_us.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/show/content_rating_us.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
