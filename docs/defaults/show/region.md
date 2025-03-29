---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/region.md"
    replace='{
        "LIBRARY_TYPE": "Show",
        "FULL_TYPE": "TV Shows",
        "SHORT_TYPE": "show",
        "DYNAMIC_VALUE": "[2 digit ISO 3166-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes)",
        "|color-style|": "|sync_mode|color-style|"
    }'
    replace-tags='{"title-sub": "**[This file has a Movie Library Counterpart.](./../../movie/region)**"}'
    rewrite-relative-urls=false
%}

    === "Default `include`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        include: 
    {%    
      include-markdown "../../../defaults/show/region.yml" 
      comments=false
      start="include:\n"
      end="addons:"
    %}
        ```

    === "Default `addons`"
    
        {% include-markdown "../../templates/snippets/no-copy.md" rewrite-relative-urls=false %}
        addons: 
    {%    
      include-markdown "../../../defaults/show/region.yml" 
      comments=false
      start="addons:\n"
    %}
        ```
