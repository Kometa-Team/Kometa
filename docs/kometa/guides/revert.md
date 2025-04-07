---
search:
  boost: 2
hide:
  - tags
  - toc
tags:
  - undo
  - revert
  - backup
---
# Reverting what Kometa has done

There is no global "undo everything Kometa ever did" *after the fact* since no history is kept.

The only "totally undo everything Kometa has ever done to this Plex server" process is to restore your Plex appdata from the backup you took prior to using Kometa. 

## Collections

You can delete the collections that Kometa has created either by telling Kometa to do so or manually in the UI.

If Kometa has deleted collections that you created outside of Kometa [something you would have explicitly told it to do], they cannot be restored.

## Playlists

You can delete the playlists that Kometa created manually in the UI.

## Overlays

You can tell Kometa to remove overlays, which will restore the clean posters that the overlays were applied to.

## Metadata

If you have not created a metadata backup in advance, there is probably no way to restore things that Kometa has changed.

Kometa can make a [metadata backup](../../config/operations.md#metadata-backup) for you. This backup is a YAML file that contains things like ratings, titles, summaries, etc. 
You can use this backup to revert changes that Kometa has made.

Chazlarson has created a [metadata backup script](https://github.com/chazlarson/Media-Scripts/blob/main/Kometa/README.md#metadata-extractorpy) that backs up more metadata than Kometa does, 
including artwork. This script can be used to create a backup that can be used to revert changes that Kometa has made.

Both of these backups are only useful if you have created them before you need them.

The remarks that follow apply in the absence of a metadata backup.

### Posters and Backgrounds

If you have used Kometa to set artwork based on URLs or local files, there is no way to restore what was there before Kometa changed it. No history of what was there before is kept.

### Mass updates

If you have made mass updates to things like genres, ratings, and the like, what was there before is gone for good *unless* what was there is the default Plex value. 
You can generally use Kometa to reset those values and let Plex fill them back in.

This is not always the case, however. If you had assigned user ratings to everything prior to using Kometa and then you told 
Kometa to update the user rating with some other rating [say TMDB or the like], all your user ratings are lost with no backup.

### Other Metadata

If you have used Kometa to change titles, summaries, years, artwork, etc. with a Metadata File[all things you would have explicitly told it to do] 
there is no way to restore what was there before Kometa changed it.
