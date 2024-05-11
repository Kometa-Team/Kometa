---
search:
  boost: 2
---
# Switching from PMM to Kometa

You're using PMM now and want to switch to Kometa? Here's what you have to do:

IMPORTANT:
I am assuming that your existing config file is working with a recent pre-rebrand PMM release.

## If you are using Git:

1. cd into the directory where you installed PlexMetaManager
2. retrieve the new code and reinstall requirements [see below].  This is the same thing you'd do with any upgrade.
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

1. change the image you are using from `meisnate12/plex-meta-manager` to `kometateam/kometa` You'll change this wherever it's specified in your situation, a docker run command, a docker compose file, some field in a NAS UI, wherever
2. If needed, rebuild the container however that happens in your context. `docker compose up -d`, clicking a button, whatever.
3. You're done.

## If you downloaded it as a zip file:

1. uncompress the zip file
2. cd into that directory and do the same setup you did initially (create a virtual environment, maybe, then install requirements. There's no way for me to know what you did when you set it up, so I can't give more specific instructions than that)
3. copy the config directory from your PMM dir into this directory.
4. change `plex_meta_manager.py` in any run command you use to `kometa.py`.  For example: `python kometa.py --run`.
5. You're done.

There are other things you can do if you wish:

1. change `- pmm:` in the `config.yml` file to `- default:`; the docs now use `- default:`, but either will work for the foreseeable future, so you do not **need** to do this. You may *want* to, and if so go ahead, but you do not *have* to.
2. change the name of any directories you are using to "kometa". The app does not care about that part of the path. It only cares about the contents of the config directory, but it can be located anywhere. You do not **have* to change `/some/path/to/Plex-Meta-Manager` to `/some/path/to/Kometa`. Again, you may *want* to, and if so go ahead, but you do not *have* to.

Neither of those two things are required.