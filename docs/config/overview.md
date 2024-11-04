## General Overview

Kometa uses YAML files for its configuration.

There is one required YAML file (`config.yml`); any others are optional and would be used to define [collections](../files/collections.md), [overlays](../files/overlays.md), and [metadata changes](../files/metadata.md).  Files other than `config.yml` are not required for Kometa to function.

Typically, files other than `config.yml` will be referred to as "metadata files" or "external YAML files".  They are independent of each other; generally speaking, anything that is documented as part of `config.yml` cannot be used in a metadata file and vice versa.  

This page will discuss the `config.yml` file and its settings.  For information on metadata files, see the [Metadata Files](../files/overview.md) page.

## Config File

The `config.yml` file is used to define the settings that Kometa will use to connect to your Plex server, as well as required 
connection details needed to connect to Plex Media Server, Radarr, Sonarr, and other third-party services via API.  It is also used to define the libraries that Kometa will be working with and the settings that determine how Kometa behaves.

By default, and unless otherwise stated, Kometa looks for the configuration file at `config/config.yml`.

A template Configuration File can be found in the 
[GitHub Repo](https://github.com/Kometa-Team/Kometa/blob/master/config/config.yml.template).

This table outlines the third-party services that Kometa can make use of. Each service has specific 
requirements for setup that can be found by clicking the links within the table or in the sidebar.

| Attribute                                   | Required                                                              |
|:--------------------------------------------|:----------------------------------------------------------------------|
| [`libraries`](libraries.md)                 | :fontawesome-solid-circle-check:{ .green }                            |
| [`playlist_files`](../notused/playlists.md) | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`settings`](settings.md)                   | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`webhooks`](webhooks.md)                   | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`plex`](plex.md)                           | :fontawesome-solid-circle-check:{ .green } Either here or per library |
| [`tmdb`](tmdb.md)                           | :fontawesome-solid-circle-check:{ .green }                            |
| [`tautulli`](tautulli.md)                   | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`github`](github.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`omdb`](omdb.md)                           | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`mdblist`](mdblist.md)                     | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`notifiarr`](notifiarr.md)                 | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`gotify`](gotify.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`anidb`](anidb.md)                         | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`radarr`](radarr.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`sonarr`](sonarr.md)                       | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`trakt`](trakt.md)                         | :fontawesome-solid-circle-xmark:{ .red }                              |
| [`mal`](myanimelist.md)                     | :fontawesome-solid-circle-xmark:{ .red }                              |

## Configuration File Example

### Minimal Configuration File

The absolute minimum configuration file would look like this:

```yaml
libraries:                           # A CONFIG NEEDS AT LEAST ONE LIBRARY
  Movies:                            # This is the name of the library
    collection_files:                # A library needs at least one metadata section [collections, overlays, metadata, operations]
      - default: basic               # At least one metadata file is required [this is a random one for illustration]

plex:                                # There needs to be a plex section
  url: YOUR_PLEX_URL_GOES_HERE
  token: YOUR_TOKEN_GOES_HERE
                                     # There are other settings, but they all have defaults

tmdb:                                # There needs to be a tmdb section
  apikey: YOUR_TMDB_API_KEY_GOES_HERE
                                     # There are other settings, but they all have defaults
```

Typically, a configuration file will be much more complex than this, but this is the absolute minimum that is required for Kometa to function.

Kometa will fill in the defaults for any settings that are not explicitly defined in the configuration file.  Those defaults will then be inserted into the file and written back out, which means that the minimal config will become more complete as soon as Kometa is run.  This behavior [writing out the filled-in config] can be overridden with a [runtime flag](../kometa/environmental.md).

This example outlines what a "standard" config.yml file might look like when in use.  This example is the same file as is linked to above.

~~~yaml
{%    
  include-markdown "../../config/config.yml.template" 
  comments=false
%}
~~~

## Editing the Configuration File

YAML is a structured file format where things like indentation and spacing are important.  A large number of issues on the Discord are due to incorrect YAML formatting.  This is why it is important to use a good editor when working with YAML files.

Standard text editors (such as Notepad and TextEdit) often save text in a rich-text format which can result in text formatted in a way that Kometa cannot read. But not only that, they also make it very hard to visually distinguish the formatting, such as indentation.

YAML requires indents to be consistent, and does not allow tab characters. If you have one space too much, or too few, it is very hard to notice that with a editor like Notepad.

An editor that is more focused on editing code instead of text can automatically detect the .YML file format and adjust things to make it easier to work. They can also try to detect possible errors even before you actually run the .yml in Kometa.

### YAML Schema

Kometa has a schema file available that can be used to validate the configuration file in the editor.

If your editor supports it, you can use the schema file to validate the configuration file as you are editing it. This can save a lot of time and headaches.

Leverage the schema file by adding this line to the top of your config.yml file:
```
# yaml-language-server: $schema=https://raw.githubusercontent.com/Kometa-Team/Kometa/nightly/json-schema/config-schema.json
```

### Suggested Editors

Preferred:

[Visual Studio Code](https://code.visualstudio.com/) (Windows/Mac/Linux, Opensource & Free)

Additionally, install the indent-rainbow by oderwat extension and the YAML by Red Hat extension.

Other options:

[Notepad++](https://notepad-plus-plus.org/) (Windows only, Opensource & Free)

[Sublime Text](https://www.sublimetext.com/) (Windows/Mac/Linux, Paid)

[BBEdit](https://www.barebones.com/) (Mac only, Paid)

For further details and a short list of highly recommended extensions, you can also take a look [here](https://l33tlamer.github.io/yml-tips/).

Here is an example of how Visual Studio Code works with the recommended plugins and using our Kometa schema:

![](./images/VSCode.gif)
