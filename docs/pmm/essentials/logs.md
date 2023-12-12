# Log files and where to find them

Plex-Meta-Manager's log files can be found in `config/logs`:

```
config/logs
├── Movies
│   ├── collections
│   │   ├── Action
│   │   │   ├── collection.log
│   │   │   └── collection.log.1
│   │   ├── Best of 2022
│   │   │   ├── collection.log
│   │   │   └── collection.log.1
│   │   ├── Top Rated
│   │   │   ├── collection.log
│   │   │   └── collection.log.1
│   │   └── Trending
│   │       ├── collection.log
│   │       └── collection.log.1
│   ├── library.log
│   └── library.log.1
├── TV
│   ├── collections
│   │   ├── Reality
│   │   │   ├── collection.log
│   │   │   └── collection.log.1
│   │   └── Game Shows
│   │       ├── collection.log
│   │       └── collection.log.1
│   ├── library.log
│   └── library.log.1
├── meta.log
├── meta.log.1
└── playlists
    ├── playlists.log
    └── playlists.log.1
```

You will find a `meta.log`, which the the full log of the entire run.

The subfolders provide more limited logs at the library, collection, and playlist levels.

As new log files are created, the old ones get a numeric suffix added: `meta.log.1`. The most recent is always the one without a number at the end.

These files will contain a great deal of detail about what exactly is happening and why.  Generally speaking, if you're having a problem with PMM the answer will be found here.  These logs can of course be quite technical, but often the error can be relatively clear:


Something's missing from the format of the file:
```
| Loading Collection File: config/TV Shows.yml                                                         |
|                                                                                                    |
| YAML Error: metadata, collections, or dynamic_collections attribute is required                    |
```

The problem in that case was:

```yaml
templates:
  Collection:
    cache_builders: 30
    sync_mode: sync
    sort_title: ZZZ-<<source>>-<<collection_name>>

collections:   <<< THIS LINE WAS MISSING
  Cached for 30 Days:
    template: {name: Collection, source: Looper}
    summary: ""
    trakt_list:
      - https://trakt.tv/users/kesleyalfa/lists/year-2011
```


YAML doesn't allow duplicate keys:
```
| Loading Collection File: config/Anime.yml                                                            |
|                                                                                                    |
| YAML Error: while constructing a mapping
|   in "<unicode string>", line 27, column 5:
|         mal_favorite: 50
|         ^ (line: 27)
| found duplicate key "collection_order" with value "custom" (original value: "custom")
|   in "<unicode string>", line 32, column 5:
|         collection_order: custom
|         ^ (line: 32)
```

The problem there was something like this:
```yaml
templates:
  Collection:
    cache_builders: 30
    sync_mode: sync
    sort_title: ZZZ-<<source>>-<<collection_name>>

collections:   <<< THIS LINE WAS MISSING
  Cached for 30 Days:
    template: {name: Collection, source: Looper}
    collection_order: custom                         <<<<  THIS KEY
    summary: ""
    collection_order: custom                         <<<<  DUPLICATED HERE
    trakt_list:
      - https://trakt.tv/users/kesleyalfa/lists/year-2011
```

File is not where PMM expects it:
```
| Loading Collection File: config/Movies.yml                                                           |
| YAML Error: File Error: File does not exist /Users/Lucky/Plex-Meta-Manager/config/Movies.yml       |
```

## Providing Log Files

You can drag-and-drop your meta.log file directly into Discord, you do not need to upload it to a third-party site unless it exceeds the 50mb size limit.

Please DO NOT manually extract, copy and paste text from your log files directly into Discord as the formatting can be difficult to read and can often redact parts of the log file that are important for full context.

