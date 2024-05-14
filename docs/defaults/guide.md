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

## Configurations

To run a default Kometa Collection or Overlay file you can simply add it to your `collection_files` (For Collection Files) 
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

## Customizing these defaults

Configs can be customized using the `template_variables` attribute when calling the file.

These template variables can be used to customize individual collections/overlays or the set as a whole.

A given default may have variables that are specific to it, and may also leverage a common set of shared template variables.  These lists are shown on each default file's wiki page.

## Customizing individual components

Each default file uses "keys" to refer to the collections and overlays that it creates, and you can use those keys to modify the behavior of individual collections or overlays created by the file.

For, example, the IMDB default creates three collections, each with their own "key":

| Collection          | Key       |
|:--------------------|:----------|
| `IMDb Popular`      | `popular` |
| `IMDb Top 250`      | `top`     |
| `IMDb Lowest Rated` | `lowest`  |

You use that key to customize the individual collection or overlay.

This example disables two keys, which will prevent those collections from being created. It also sets 
the visibility of one of the keys [`top`] so that it is visible on the library tab, the server owner's homescreen and shared 
user's homescreens (assuming the server owner and/or the shared users have the library pinned to their homescreen)

It also changes the resolution overlay to skip applying the overlay to 480p movies.

The template variables in this example happen to be all shared template variables.

```yaml
libraries:
  Movies:
    collection_files:
      - default: imdb
        template_variables:
          use_popular: false         # turn off the 'popular' key
          use_lowest: false          # turn off the 'lowest' key
          visible_library_top: true  # set visibilities for the 'top' key
          visible_home_top: true
          visible_shared_top: true
    overlay_files:
      - default: resolution
        template_variables:
          use_480p: false            # turn off the '480p' key
```

## Customizing the set as a whole

In addition to the keys, each default can be customized with other template variables that are not key-specific.

This example uses a file-specific variable to change the order of all the IMDB chart collections to alphabetical by title and a shared variable to schedule these IMDB collections to be run only on Wednesdays.

On the `resolution` overlay, it uses a file-specific variable to disable all the "edition" overlays and a shared variable to align the overlay on the right side of the poster.

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
          collection_order: alpha      # file-specific variable sets sort order
          schedule: weekly(wednesday)  # shared variable sets schedule
    overlay_files:
      - default: ribbon
        template_variables:
          use_480p: false
          use_edition: false           # file-specific variable hides editions
          horizontal_align: right      # shared variable sets alignment
```

All of the default files are customized in this basic fashion.

**NOTE: this `template_variable` system is specific to the defaults.  If and when you start creating your own [collection](../files/collections.md) or [overlay](../files/overlays.md) files, you cannot use this `template_variables` setup unless you specifically write your files to implement it.**

Each of these default files has a page on the wiki showing its keys, available `template_variables`, and default settings.  For example, the default overlay `default: resolution` has a page [here](overlays/resolution.md).

The shared template variables can be reviewed here for [Collections](collection_variables.md) and [Overlays](overlay_variables.md).  These are also linked from each default file's wiki page.  Keep in mind that *most*, but not all default files have access to the shared variables.  This will be noted on the individual files' page.

## Collection Defaults

See the [Collection Defaults](collections.md) Page for more information on the specifics of the Collection Defaults.

## Overlay Defaults

See the [Overlay Defaults](overlays.md) Page for more information on the specifics of the Overlay Defaults.

# Example config using the defaults

{%
   include-markdown "./example.md"
%}
