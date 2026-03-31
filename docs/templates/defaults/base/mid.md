<!--all-->## Config

The below YAML in your config.yml will create the collections:

```yaml
libraries:
<!--all-->

<!--movie-->
  Movies:
<!--movie-->

<!--hide-->
    template_variables:
      collection_mode: hide_items
<!--hide-->

<!--movie-->
    collection_files:
      - default: CODE_NAME
<!--movie-->

<!--ratings-->
        template_variables:
          rating1: imdb
          rating2: mdb_tomatoesaudience
          rating3: tmdb
<!--ratings-->

<!--show-->
  TV Shows:
<!--show-->

<!--hide-->
    template_variables:
      collection_mode: hide_items
<!--hide-->

<!--show-->
    collection_files:
      - default: CODE_NAME
<!--show-->
  
<!--ratings-->
        template_variables:
          rating1: imdb
          rating2: mdb_tomatoesaudience
          rating3: tmdb
<!--ratings-->

<!--episode-->
      - default: CODE_NAME
        template_variables:
          builder_level: episode
<!--episode-->

<!--ratings-->
          rating1: tmdb
          rating2: imdb
<!--ratings-->

<!--season-->
      - default: CODE_NAME
        template_variables:
          builder_level: season
<!--season-->

      
<!--all-->
```

<!--vars-->

## Template Variables

Template Variables can be used to manipulate the file in various ways to slightly change how it works without having to make your own local copy.

Note that the `template_variables:` section only needs to be used if you do want to actually change how the defaults work. 
Any value not specified will use its default value if it has one if not it's just ignored.

??? example "Example Template Variable Amendments (Click to Expand)"

    The below is an example config.yml extract with some Template Variables added in to change how the file works.

    Click the :fontawesome-solid-circle-plus: icon to learn more
<!--all-->