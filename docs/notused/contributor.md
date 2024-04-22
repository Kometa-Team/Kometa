# Contributor Guide

## How to set up a local Wiki Server

1. In addition to your normal `python -m pip install -r requirements.txt` to install requirements you'll also need to install the docs `requirements.txt` by running `python -m pip install -r docs/requirements.txt`.
2. Run `docs\make.bat html` from the main Kometa directory to build the html wiki files.
3. Run `sphinx-reload docs` to boot up the Reloading Server at `http://localhost:5500`
4. Now you can make changes inside the docs folder to update the Wiki and when you want to see the changes just run `docs\make.bat html` again and then refresh that page.