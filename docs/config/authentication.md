---
hide:
  - toc
---
# Trakt and MyAnimeList Authentication

When trying to authorize Trakt or MyAnimeList, Kometa needs to run in interactive mode so that you can enter details. 
This is problematic on some setups [namely docker] where entering interactive mode is not always simple.

These webapps allow you to authorize Trakt and MyAnimeList outside of a Kometa run. Once authorized, you will 
have a YAML block that you will copy into the config.yml, replacing the existing `trakt` and/or `myanimelist` sections.

Nothing is cached or retained.

The source code can be found [here](https://github.com/Kometa-Team/Kometa-Utilities).

## Usage

1. Choose the authentication you are interested in.
2. Follow the prompts
3. Copy and paste the result into your Kometa config.

## Running this Locally

For users who want full control over this and would prefer to run them locally, you can do so 
by following the instructions in the [repo](https://github.com/Kometa-Team/Kometa-Utilities).
