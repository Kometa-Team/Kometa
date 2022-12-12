If the default metadata files do not allow you to create the collections you want, you can define your own collections in your own metadata files to do whatever you like within the capabilities of PMM.  We will create a simple collection that will contain 20 comedy movies since 2012.

First, open the metadata file [this will create the file if it doesn't already exist]:

````{tab} Linux
<br/>
[type this into your terminal]

```
nano "config/Movies.yml"
```
<br/>
````
````{tab} OS X:
<br/>
[type this into your terminal]

```
nano "config/Movies.yml"
```
<br/>
````
````{tab} Windows:
<br/>
[type this into your terminal]

```
notepad "config\Movies.yml"
```
<br/>
````

In this file, add the following, exactly as it is shown here:

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

```{include} wt/wt-save.md
```

Next, add a reference to this file to your config file.

Open the config file again and add the last line shown below:

```yaml
libraries:
  Main Movies:                            ## <<< CHANGE THIS LINE
    metadata_path:
      - pmm: basic               # This is a file within the defaults folder in the Repository
      - pmm: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
      - file: config/Movies.yml
```

That line needs to match the path you used when you created the file a moment ago.