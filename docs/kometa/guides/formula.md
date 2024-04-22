# Formula 1 Metadata Guide

This is a guide for setting up Formula 1 in Plex using the `f1_season` metadata attribute.

Most of this guide is taken from a reddit [post](https://www.reddit.com/r/PleX/comments/tdzp8x/formula_1_library_with_automatic_metadata/) written by /u/Toastjuh.

## Folder structure

Let's start with the basics:

* Every Formula 1 season will be a TV Show in Plex. Season 2001, Season 2002, etc.
* Every race will be a Season in Plex. Season 1 will be the Australian GP, Season 2 will be the Bahrain GP etc.
* Every session will be an Episode in Plex. Episode 1 will be Free Practice 1, Episode 2 will be Free Practice 2 etc.

The folder format is like this:
```
Formula                                   -> Library Folder
└── Season 2018                           -> Folder for each F1 Season
    ├── 01 - Australian GP                -> Folder for each Race in a season
    │   ├── 01x10 - Australian GP - Highlights.mkv
    │   ├── 01x01 - Australian GP - Free Practice 1.mkv
    │   ├── 01x02 - Australian GP - Free Practice 2.mkv
    │   ├── 01x03 - Australian GP - Free Practice 3.mkv
    │   ├── 01x04 - Australian GP - Pre-Qualifying Buildup.mkv
    │   ├── 01x05 - Australian GP - Qualifying Session.mkv
    │   ├── 01x06 - Australian GP - Post-Qualyfing Analysis.mkv
    │   ├── 01x07 - Australian GP - Pre-Race Buildup.mkv
    │   ├── 01x08 - Australian GP - Race Session.mkv
    │   ├── 01x09 - Australian GP - Post-Race Analysis.mkv
    │   └── 01x10 - Australian GP - Highlights.mkv
    └── 02 - Bahrein GP
        ├── 02x10 - Bahrein GP - Highlights.mkv
        ├── 02x01 - Bahrein GP - Free Practice 1.mkv
        ├── 02x02 - Bahrein GP - Free Practice 2.mkv
        ├── 02x03 - Bahrein GP - Free Practice 3.mkv
        ├── 02x04 - Bahrein GP - Pre-Qualifying Buildup.mkv
        ├── 02x05 - Bahrein GP - Qualifying Session.mkv
        ├── 02x06 - Bahrein GP - Post-Qualyfing Analysis.mkv
        ├── 02x07 - Bahrein GP - Pre-Race Buildup.mkv
        ├── 02x08 - Bahrein GP - Race Session.mkv
        ├── 02x09 - Bahrein GP - Post-Race Analysis.mkv
        └── 02x10 - Bahrein GP - Highlights.mkv
```

For weekends with a Sprint race (this example also includes Ted's Notebook segments), the format looks like this:
```
Formula                                   -> Library Folder
└── Season 2023                           -> Folder for each F1 Season
    └── 04 - Azerbaijan GP                -> Folder for each Race in a season
        ├── 04x01 - Azerbaijan GP - Pre-Qualifying Buildup.mkv
        ├── 04x02 - Azerbaijan GP - Qualifying Session.mkv
        ├── 04x03 - Azerbaijan GP - Post-Qualifying Analysis.mkv
        ├── 04x04 - Azerbaijan GP - Ted's Qualifying Notebook.mkv
        ├── 04x05 - Azerbaijan GP - Pre-Sprint Shootout Buildup.mkv
        ├── 04x06 - Azerbaijan GP - Sprint Shootout Session.mkv
        ├── 04x07 - Azerbaijan GP - Post-Sprint Shootout Analysis.mkv
        ├── 04x08 - Azerbaijan GP - Pre-Sprint Race Buildup.mkv
        ├── 04x09 - Azerbaijan GP - Sprint Race Session.mkv
        ├── 04x10 - Azerbaijan GP - Post-Sprint Race Analysis.mkv
        ├── 04x11 - Azerbaijan GP - Ted's Sprint Notebook.mkv
        ├── 04x12 - Azerbaijan GP - Pre-Race Buildup.mkv
        ├── 04x13 - Azerbaijan GP - Race Session.mkv
        ├── 04x14 - Azerbaijan GP - Post-Race Analysis.mkv
        └── 04x15 - Azerbaijan GP - Ted's Race Notebook.mkv
```

What matters for plex and for Kometa.

* Change the Plex Agent to "Personal Media Shows" for F1 libraries
* The show name can be whatever you want it to be but the pre created collection file will only work if you use just the year numbers.
* The season folder can be called whatever you want as long as plex scans it in with the Season Number matching the race number.
* The episodes must follow plex's naming convention to have them scanned in properly but in order for Kometa to update the metadata the files need to be specifically name like above.

## Collection File

```yaml
metadata:
  Season 2021:
    f1_season: 2021
    round_prefix: true
  Season 2020:
    f1_season: 2020
    round_prefix: true
```

* Add `round_prefix: true` to have the race number appended to the beginning of the Race Name.
* Add `shorten_gp: true` to shorten `Grand Prix` to `GP` in all titles.

Add an entry for every season you want to set the metadata for. The name needs to correspond with the name the season has in Plex!

The posters of races you can get from https://www.eventartworks.de/
