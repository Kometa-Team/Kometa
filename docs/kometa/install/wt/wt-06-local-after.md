You should see that the collection file gets loaded:

```
| Loading Collection File: config/Movies.yml
| Collection File Loaded Successfully
```

As it builds the collection, you should see a fair amount of logging about which movies are being added and which ones aren’t found.  Once it completes, go to Plex, go to your Movies library, and click “Collections” at the top.

You should see the new collection:

![Finished Collections](../images/wt-finished.png)

When you click into each, you’ll see the movies that Kometa added to each collection.

Each time you run the script, new movies that match the collection definitions will be added.  For example, if you don’t have “The ShawShank Redemption” now, when you download it and run Kometa again it will be added to the IMDB 250 collection.
