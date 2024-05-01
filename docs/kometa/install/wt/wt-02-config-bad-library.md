
---

Scroll down a bit and update the three things you just collected; Plex URL, Plex Token, and TMDb API Key.

```yaml
plex:                                           # Can be individually specified per library as well
  url: http://bing.bang.boing                <<< ENTER YOUR PLEX URL HERE
  token: XXXXXXXXXXXXXXXXXXXX                <<< ENTER YOUR PLEX TOKEN HERE
  timeout: 60
  db_cache:
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
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
    remove_overlays: false       # Set this to true to remove all overlays
    overlay_files:
      - default: ribbon              # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  TV Shows:
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
    remove_overlays: false       # Set this to true to remove all overlays
    overlay_files:
      - default: ribbon              # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  Anime:
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: anilist             # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  Music:
    collection_files:
      - file: config/Music.yml   # This is a local file THAT YOU MIGHT CREATE
playlist_files:
  - default: playlist                # This is a file within Kometa's defaults folder
  # see the wiki for how to use local files, folders, URLs, or files from git
```

You will ultimately need an entry here for each of the libraries on which you want Kometa to act.  Those top-level elements [Movies, TV Shows, Anime, Music] are names of libraries on your Plex server.

For now, delete the “TV Shows”, “Anime”, and "Music" sections from the config file and change the name of the “Movies” section to “Movies-NOSUCHLIBRARY":

The top bit of your config file should now look like this:

```yaml
libraries:
  Movies-NOSUCHLIBRARY:                         ## <<< CHANGE THIS LINE
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
playlist_files:
  - default: playlist                # This is a file within Kometa's defaults folder
  # see the wiki for how to use local files, folders, URLs, or files from git
```

This is intended to cause an error for illustration that you will then fix.

Be very careful with the indentation and ensure it looks exactly like the above; each line indented using two spaces, NOT TABS, with `playlist_files:` all the way over on the left.  Indentation is significant in YAML.

