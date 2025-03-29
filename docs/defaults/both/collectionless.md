---
hide:
  - toc
---
{%
    include-markdown "./../../templates/defaults/base/collection/header.md"
    replace='{
        "COLLECTION": "Collectionless", 
        "CODE_NAME": "collectionless",
        "LIBRARY_TYPE": "Movie, Show",
        "DESCRIPTION": "create a [Collectionless collection](../../files/builders/plex.md#plex-collectionless) to help Show/Hide Movies/Shows properly in your library"
    }'
    rewrite-relative-urls=false
    end="<!--rec-sub-->"
%}

Requirements: 

* This file needs to run last under `collection_files`.

* All other normal collections must use `collection_mode: hide_items`.

* Disable the `Minimum automatic collection size` option when using the `Plex Movie` Agent. (Use the [`franchise` Default](../movie/franchise.md) for automatic collections)

## Collection

| Collection       | Description                                                                                                                            |
|:-----------------|:---------------------------------------------------------------------------------------------------------------------------------------|
| `Collectionless` | [Collectionless collection](../../files/builders/plex.md#plex-collectionless) to help Show/Hide Movies/Shows properly in your library. |

{% include-markdown "./../../templates/defaults/base/mid.md" 
    replace='{"CODE_NAME": "collectionless"}'
    include-tags='all|movie|show|hide'
%}
    ```yaml
    libraries:
      Movies:
        template_variables:
          collection_mode: hide_items #(1)!
        collection_files:
          - default: collectionless
            template_variables:
              exclude:
                - Marvel Cinematic Universe #(2)!
              collection_order: release #(3)!
    ```

    1.  Sets the collection mode to "Hide items which are in collections" for any Collection that is processed as part of the Kometa run against this library.
    2.  Prevent media within the "Marvel Cinematic Universe" Collection from being considered for collectionless.
    3.  Sort the "Collectionless" Collection by release date

{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" end="<!--file-->" %}
{% include-markdown "./../../templates/snippets/no_shared_variables.md" %}
{% include-markdown "./../../templates/defaults/base/collection/variables_header.md" start="<!--file-header-->" %}
    {%
        include-markdown "./../../templates/variable_list.md"
        include-tags="collectionless"
        rewrite-relative-urls=false
    %}                                                                                                                                                                                                                                                                                                                                                                                                                             |
    
{% include-markdown "./../../templates/defaults/base/values.md" rewrite-relative-urls=false %}

    === "Collectionless Collection"

        The Collectionless collection use the [`plex_collectionless` Builder](../../../files/builders/plex#plex-collectionless) to create the collection.
        
        Collections and their items are excluded from this collection based on a name prefix or the collection name.
