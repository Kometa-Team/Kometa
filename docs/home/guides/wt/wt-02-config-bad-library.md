
---

Scroll down a bit and update the three things you just collected; Plex URL, Plex Token, and TMDb API Key.

```yaml
plex:                                           # Can be individually specified per library as well
  url: http://bing.bang.boing                <<< ENTER YOUR PLEX URL HERE
  token: XXXXXXXXXXXXXXXXXXXX                <<< ENTER YOUR PLEX TOKEN HERE
  timeout: 60
  clean_bundles: false
  empty_trash: false
  optimize: false
tmdb:
  apikey: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   <<< ENTER YOUR TMDb API KEY HERE
  language: en
```

Now scroll up and look at the top section:

```yaml
## This file is a template remove the .template to use the file

libraries:                       # This is called out once within the config.yml file
  Movies:                        # Each library must match the Plex library name
    metadata_path:
      - pmm: basic               # This is a file within the defaults folder in the Repository
      - pmm: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
    overlay_path:
      - remove_overlays: false   # Set this to true to remove all overlays
      - pmm: ribbon              # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  TV Shows:
    metadata_path:
      - pmm: basic               # This is a file within the defaults folder in the Repository
      - pmm: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
    overlay_path:
      - remove_overlays: false   # Set this to true to remove all overlays
      - pmm: ribbon              # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  Anime:
    metadata_path:
      - pmm: basic               # This is a file within the defaults folder in the Repository
      - pmm: anilist             # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  Music:
    metadata_path:
      - file: config/Music.yml   # This is a local file THAT YOU MIGHT CREATE
```

You will ultimately need an entry here for each of the libraries on which you want PMM to act.  Those top-level elements [Movies, TV Shows, Anime, Music] are names of libraries on your Plex server.

For now, delete the “TV Shows”, “Anime”, and "Music" sections and change the name of the “Movies” section to “Movies-NOSUCHLIBRARY":

```yaml
libraries:
  Movies-NOSUCHLIBRARY:                         ## <<< CHANGE THIS LINE
    metadata_path:
      - pmm: basic               # This is a file within the defaults folder in the Repository
      - pmm: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
```

This is intended to cause an error for illustration that you will then fix.
