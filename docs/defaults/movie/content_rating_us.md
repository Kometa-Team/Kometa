---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/content_rating.md"
    replace='{
        "LIBRARY_TYPE": "Movie",
        "Movies/Shows": "Movies",
        "movie|show": "movie",
        "COLLECTION": "US Content Rating", 
        "CODE_NAME": "content_rating_us",
        "SHORT_NAME": "US",
        "PLEX_NAME": "United States",
        "EXAMPLE_NAME": "R Movies",
        "EXAMPLE1": "R",
        "EXAMPLE2": "de/18"
    }'
    replace-tags='{
        "title-sub": "**[This file has a Show Library Counterpart.](./../../../../show/content_rating_us)**",
        "image": "![](../../../../assets/images/defaults/content_rating_us_movie.png)"
    }'
    rewrite-relative-urls=false
%}

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/movie/content_rating_us.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/movie/content_rating_us.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
