---
search:
  boost: 2
---
# Switching from Plex-Meta-Manager to Kometa

You're using Plex-Meta-Manager now and need to switch to Kometa? Here's what you have to do:

???+ danger "Important"

    These instructions are assuming that your existing config file is working with a recent [say 1.19 or newer] pre-rebrand Plex-Meta-Manager release.

## If you are using Git:

1. cd into the directory where you installed Plex-Meta-Manager
2. retrieve the new code and reinstall requirements [see below for commands].  This is the same thing you'd do with any upgrade.
3. change `plex_meta_manager.py` in any run command you use to `kometa.py`.  For example: `python kometa.py --run`.
4. You're done.

The commands you need for step 2 are:

```
    git stash
    git stash clear
    git pull
    # activate your venv here if you use one and it is not already active
    python -m pip install -r requirements.txt
```

## If you are using Docker:

1. change the image you are using from `meisnate12/plex-meta-manager:SOME_TAG` to `kometateam/kometa`,   You'll change this wherever it's specified in your situation, a `docker run` command, a docker compose file, some field in a NAS UI, wherever.
2. If needed, rebuild the container however that happens in your context. `docker compose up -d`, clicking a button, whatever.
3. You're done.

## If you downloaded it as a zip file:

1. uncompress the zip file
2. cd into that directory and do the same setup you did initially (create a virtual environment, maybe, then install requirements. There's no way for us to know what you did when you set it up, so we can't give more specific instructions than that)
3. copy the config directory from your Plex-Meta-Manager dir into this directory.
4. change `plex_meta_manager.py` in any run command you use to `kometa.py`.  For example: `python kometa.py --run`.
5. You're done.

## Other things you can do if you wish:

Neither of these two things are required.

1. change `- pmm:` in the `config.yml` file to `- default:`; the docs now use `- default:`, but either will work for the foreseeable future, so you do not **need** to do this. You may *want* to, and if so go ahead, but you do not *have* to.
2. change the name of any directories you are using to "kometa". The app does not care about that part of the path. It only cares about the contents of the config directory, but it can be located anywhere. You do not **have* to change `/some/path/to/Plex-Meta-Manager` to `/some/path/to/Kometa`. Again, you may *want* to, and if so go ahead, but you do not *have* to.

For example, this:
```yaml
libraries:
  Movies:
    remove_overlays: false
    collection_files:
      - pmm: basic
      - pmm: imdb
```
Could, but does not have to, become:
```yaml
libraries:
  Movies:
    remove_overlays: false
    collection_files:
      - default: basic
      - default: imdb
```
