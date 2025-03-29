{%
    include-markdown "./base/collection/header.md"
    replace='{
        "COLLECTION": "SEPARATOR Separator",
        "LIBRARY_TYPE": "Movie, Show",
        "DESCRIPTION": "create a separator collection for SEPARATORs"
    }'
%}
{% include-markdown "./../snippets/separator_line.md" %}

{% include-markdown "./base/mid.md" include-tags='all|movie|show' %}
    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: CODE_NAME
            template_variables:
              sep_style: purple #(1)!
    ```
    
    1. Use the purple [Separator Style](./../../defaults/separators.md#separator-styles)

{% include-markdown "./base/collection/variables_header.md" include-tags="separator" rewrite-relative-urls=false %}
{% include-markdown "./base/collection/shared.md" start="<!--separator-variables-->" rewrite-relative-urls=false %}