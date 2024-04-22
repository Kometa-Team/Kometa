# Defaults Usage Guide

Kometa includes a pre-created set of Collection Files and Overlay Files which can be found in the "defaults" folder in 
the root of your Kometa installation directory.

These files offer an easy-to-use and customizable set of Collections and Overlays that the user can achieve without 
having to worry about creating the files that make the collections and overlays possible.

All Collections come with a matching poster to make a clean, consistent set of collections in your library. These files 
are stored in the [Kometa Images](https://github.com/Kometa-Team/Default-Images) Repository and each poster is downloaded straight to your Plex Collection when 
you run Kometa.

Credits to Sohjiro, Bullmoose20, Yozora, Cpt Kuesel, and anon_fawkes for helping drive this entire Default Set of 
Configs through the concept, design and implementation.

Special thanks to Magic815 for the overlay image inspiration and base template.

Please consider [donating](https://github.com/sponsors/meisnate12) towards the project.

## Collection Defaults

See the [Collection Defaults](collections.md) Page for more information on the specifics of the Collection Defaults.

## Overlay Defaults

See the [Overlay Defaults](overlays.md) Page for more information on the specifics of the Overlay Defaults.

## Configurations

To run a default KometCollection or Overlay file you can simply add it to your `collection_files` (For Collection Files) 
or `overlay_files` (For Overlay Files) using `default` like so:

```yaml
libraries:
  Movies:
    collection_files:
    - default: actor
    - default: genre
    overlay_files:
    - default: ribbon
    - default: ratings
```

## Customizing Configs

Configs can be customized using the `template_variables` attribute when calling the file. These `template_variables` 
will be given to every template call in the file which allows them to affect how that file runs.

For collections, this example disables two keys, which will prevent those collections from being created. It also sets 
the visibility of one of the keys so that it is visible on the library tab, the server owner's homescreen and shared 
user's homescreens (assuming they server owner and/or the shared users have the library pinned to their homescreen)

For overlays, this example changes the ratings overlay to apply to episodes rather than shows.

```yaml
libraries:
  TV Shows:
    collection_files:
      - default: imdb
        template_variables:
          use_popular: false
          use_lowest: false
          visible_library_top: true
          visible_home_top: true
          visible_shared_top: true
    overlay_files:
      - default: ratings
        template_variables:
          builder_level: episode
```

Each file has a page on the wiki showing the available `template_variables` for each file. For example the default 
`default: ratings` has a page [here](overlays/ratings.md).

**In addition to the defined `template_variables` almost all default Collection and Overlay files have access to their 
respective [Collection](collection_variables.md)/[Overlay](overlay_variables.md) Shared Variables.**

{%
   include-markdown "./example.md"
%}
