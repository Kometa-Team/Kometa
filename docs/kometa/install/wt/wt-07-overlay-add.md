The default collection files include a set of overlays you can add to your posters.

We'll add resolution overlays to the movies in this library as an example.

Open the config file again and add the last three lines shown below:

```yaml
libraries:
  All The Movies:
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
      - file: config/Movies.yml
    remove_overlays: false            ## <<< ADD THIS LINE
    overlay_files:                         ## <<< ADD THIS LINE
      - default: resolution                   ## <<< ADD THIS LINE
```
