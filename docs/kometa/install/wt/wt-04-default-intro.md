Kometa provides an extensive collection of "default" collection files.

These files provide a simple way for you to create collections based on franchises or awards or actors, etc.

The default config links to two of them, these two lines in your config file:

```yaml
libraries:
  THE_NAME_OF_YOUR_MOVIE_LIBRARY:
    collection_files:
      - default: basic               # <<< THIS LINE
      - default: imdb                # <<< THIS LINE
playlist_files:
  - default: playlist
```

The first will create:

  - Newly Released
  - New Episodes [TV libraries only]

The second will create:

  - IMDb Popular
  - IMDb Top 250
  - IMDb Lowest Rated
