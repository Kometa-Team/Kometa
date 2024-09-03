# File Blocks

When using Kometa, the structure of each library is made using File Blocks

???+ example "Example Library Structure"

    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: imdb
    ```

    In the above example, `collection_files` is the type of File, which tells Kometa that the entries that follow will 
    create/update collections and `- default:` is the type of Path, which Kometa that the file it is looking for is a 
    Kometa Defaults file.

    These ideas will be further outlined on this page.

## Files

{%    
  include-markdown "./file_types.md"
%}

## Blocks

Each time a file is called it's going to use what we call a "File Block". Each block must have the file location type 
and path and can have other attributes to add more control to that file. 

Every file block under the parent attribute begins with a `-`.

???+ example "Example Block"

    This example has 2 blocks each using location type `- default` with the path being `tmdb` and `imdb` respectively 
    under the parent attribute `collection_files`. 

    ```yaml
    libraries:
      Movies:
        collection_files:   # Parent Attribute
          - default: tmdb       # Block 1
          - default: imdb       # Block 2
    ```

### Location Types and Paths

There are multiple location types that can be used to call a file. They can either be on the local system, online at an 
url, part of the [Kometa Defaults](../defaults/guide.md), directly from the 
[Kometa Community Configs](https://github.com/Kometa-Team/Community-Configs) repository, or from another 
[`Custom Repository`](settings.md#custom-repo).

The location types are outlined as follows:

??? blank "`file` - Used to run a local file.<a class="headerlink" href="#file" title="Permanent link">¶</a>"

    <div id="file" />Used to run a file which is located within the system that Kometa is being run from.

    File locations need to be accessible to Kometa at those paths; this is typically only something you need to consider 
    when using Docker.
    
    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - file: config/path/to/file.yml
        ```

??? blank "`folder` - Used to run all local files in a directory.<a class="headerlink" href="#folder" title="Permanent link">¶</a>"

    <div id="folder" />Used to run all files located in a directory which is located within the system that Kometa is 
    being run from.

    Folder locations need to be accessible to Kometa at those paths; this is typically only something you need to 
    consider when using Docker.
    
    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - folder: config/path/to/folder
        ```

??? blank "`url` - Used to run a file hosted at a URL.<a class="headerlink" href="#url" title="Permanent link">¶</a>"

    <div id="url" />Used to run a file hosted publicly on the internet and accessible at a URL.

    This needs to point directly to the YAML file. A common error is using a gitHub link that points to the *page 
    displaying the YAML*. In gitHub, for instance, click on the "Raw" button and use *that* link.
    
    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - url: https://example.com/path/to/file.yml
        ```

??? blank "`default` - Used to run one of the built-in [Kometa Defaults](../defaults/guide.md) file.<a class="headerlink" href="#default" title="Permanent link">¶</a>"

    <div id="default" />Used to run a built-in Kometa Defaults file. The values you'd enter here are listed in the 
    [default usage guide](../defaults/guide.md).
    
    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - default: oscars
        ```

??? blank "`git` - Used to run a file hosted on the [Kometa Community Configs](https://github.com/Kometa-Team/Community-Configs) repository.<a class="headerlink" href="#git" title="Permanent link">¶</a>"

    <div id="git" />Used to run a file hosted on the 
    [Kometa User Configs](https://github.com/Kometa-Team/Community-Configs) repository.

    Note that you enter the bits of the items path relative to the top level of the repo [`meisnate12/People`] and you 
    don't need the `.yml` extension.
    
    ???+ example "Example"
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - git: meisnate12/People # this links to https://github.com/Kometa-Team/Community-Configs/blob/master/meisnate12/People.yml
        ```

??? blank "`repo` - Used to run a file hosted on a custom repository.<a class="headerlink" href="#repo" title="Permanent link">¶</a>"

    <div id="repo" />Used to run a file which is hosted on a repo specified by the user with the 
    [`custom_repo`](settings.md#custom-repo) Setting Attribute.

    Note that as with `git` you enter the bits of the items path relative to repo [`meisnate12/People`] and you don't 
    need the `.yml` extension.

    ???+ example "Example"

        This is assuming the `custom_repo` setting is 
        `https://github.com/Kometa-Team/Community-Configs/tree/master/meisnate12`.
        
        ```yaml
        libraries:
          Movies:
            collection_files:
              - repo: People
        ```

## Other Block Attributes

You can have some control of the files from inside your Configuration file by using these block attributes.

??? blank "`template_variables` - Used to define [Custom Template Variables](../files/templates.md#template-variables) for a file.<a class="headerlink" href="#template-variables" title="Permanent link">¶</a>"

    <div id="template-variables" />Passes all given [Template Variables](../files/templates.md#template-variables) to 
    every template in the file.

    **Note: the file has to be properly set up to use the variables.**

    <hr style="margin: 0px;">
    
    **Attribute:** `template_variables`
    
    **Accepted Values:** [Dictionary](../kometa/yaml.md#dictionaries) of values specified by each particular file.

    **Default Value:** `None`

    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            collection_files:
              - default: genre
                template_variables:
                  schedule_separator: never
                  collection_mode: hide
              - default: actor                  # Notice how the `-` starts this block
                template_variables:
                  schedule_separator: never
                  collection_mode: hide
        ```

        In this example there will be two template variables added to every template in the git file default: genre.  
        
        `schedule_separator` is set to `never` to not show a separator in this section and `collection_mode` is set to 
        `hide`.
        
        What these variables will do depends on how they're defined in the Collection File.

??? blank "`schedule` - Used to schedule when a file is run.<a class="headerlink" href="#schedule" title="Permanent link">¶</a>"

    <div id="schedule" />Used to schedule when this file is run using the [schedule options](schedule.md).

    ??? warning
    
        This does not work with Overlays as they cannot be scheduled individually. Use the 
        [`schedule_overlays` Library Attribute](libraries.md#schedule-overlays) to schedule Overlays.

    <hr style="margin: 0px;">
    
    **Attribute:** `schedule`
    
    **Accepted Values:** Any [schedule option](schedule.md)

    **Default Value:** `daily`

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            collection_files:
              - file: config/Movies.yml
                schedule: weekly(friday)
              - default: actors
                schedule: weekly(saturday)
        playlist_files:
          - file: config/Playlists.yml
            schedule: weekly(sunday)
        ```

??? blank "`asset_directory` - Used to define Asset Directories for a file.<a class="headerlink" href="#asset-directory" title="Permanent link">¶</a>"

    <div id="asset-directory" />Specify the directory where assets (posters, backgrounds, etc) are located for this 
    specific file.

    ???+ tip 
    
        Assets can be stored anywhere on the host system that Kometa has visibility of (i.e. if using docker, the 
        directory must be mounted/visible to the docker container).

    ??? warning
    
        Kometa will not create asset directories.  The directories that you specify have to exist already.

    <hr style="margin: 0px;">
    
    **Attribute:** `asset_directory`
    
    **Accepted Values:** Any directory

    **Default Value:** `[Directory containing YAML config]/assets`

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            collection_files:
              - file: config/Movies.yml
                asset_directory: <path_to_assets>/Movies
              - default: actors
                asset_directory: <path_to_assets>/people
            overlay_files:
              - default: imdb
        playlist_files:
          - file: config/Playlists.yml
            asset_directory:
              - <path_to_assets>/playlists1
              - <path_to_assets>/playlists2
        ```
