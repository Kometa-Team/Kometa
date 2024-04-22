If the default collection files do not allow you to create the collections you want, you can define your own collections in your own collection files to do whatever you like within the capabilities of Kometa.  We will create a simple collection that will contain 20 comedy movies released since 2012.

First, open the collection file [this will create the file if it doesn't already exist]:

=== ":fontawesome-brands-linux: Linux"

    [type this into your terminal]
    
    ```
    nano "config/Movies.yml"
    ```

=== ":fontawesome-brands-apple: macOS"

    [type this into your terminal]
    
    ```
    nano "config/Movies.yml"
    ```

=== ":fontawesome-brands-windows: Windows"

    [type this into your terminal]
   
    ```
    notepad "config\Movies.yml"
    ```


In this file, add the following, exactly as it is shown here; remember that spacing is significant in YAML files:

```yaml
collections:
  Recent Comedy:
    plex_search:
      all:
        genre: Comedy
        year.gte: 2012
      limit: 20
```

Save the file:

{%
   include-markdown "./wt-save.md"
%}

Next, add a reference to this file to your config file.

Open the config file again and add the last line shown below:

```yaml
libraries:
  All The Movies:
    collection_files:
      - default: basic
      - default: imdb
      # see the wiki for how to use local files, folders, URLs, or files from git
      - file: config/Movies.yml     ## <<< ADD THIS LINE
```

That line needs to match the path you used when you created the file a moment ago.  If you are copy-pasting these commands, it does.
