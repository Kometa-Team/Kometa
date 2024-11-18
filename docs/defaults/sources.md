# Data sources

This page is a reference showing the sources of the data used in the defaults files.

For example, if you are wondering what list is used by the Christmas Collection, you can find that information here.

Nothing on this page is required for using the defaults files, but it can be useful for understanding where the data comes from.

Nothing on this page is useful for customizing the defaults.

Nothing here is a code example for end user use.  It all *looks* like code, since it is taken directly *from* the Kometa source code to ensure it is up-to-date and accurate, but it is not intended for end user use.

## I want to customize the defaults

You will want to start [here](./guide.md).

Each default has its own set of template variables, which are used to control the behavior of that default.  Those will be listed on the individual page for each default.

## I want to know what's behind the defaults

These are lists provided for reference to show what values will be in use if you do no customization.  **These do not 
show how to customize the defaults.**

Nothing here is a code example for end user use.  It all *looks* like code, since it is taken directly *from* the Kometa source code to ensure it is up-to-date and accurate, but it is not intended for end user use.

If you want to customize these values, refer to [this](#i-want-to-customize-the-defaults).

## Collections

### Seasonal Collections

The Seasonal collections are based on lists from a few different sources.

If you are interested in seeing the lists that are used for the seasonal collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Seasonal Collections; default section 000 (click to expand) <a class="headerlink" href="#seasonal" title="Permanent link">¶</a>"

    <div id="seasonal" />

    {%
       include-markdown "./sources/movie/seasonal.md"
    %}

### Basic Collections

The Basic collections are based on Smart Filters, not external lists.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### AniList Collections

The AniList collections use the [anilist builder](../files/builders/anilist.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### IMDB Collections

The IMDb collections use the [IMDb builder](../files/builders/imdb.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Letterboxd Collections

The Letterboxd collections use the [Letterboxd builder](../files/builders/letterboxd.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### MyAnimeList Collections

The MyAnimeList collections use the [MyAnimeList builder](../files/builders/myanimelist.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Other Chart Collections

The collections created here use a variety of sources.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

| Collection                          | Source                                                                                                                                  |
|:------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| `AniDB Popular`                     | ['anidb_popular' builder](../files/builders/anidb.md)                                                                                   |
| `Common Sense Selection`            | Sourced from mdblist:<br>`https://mdblist.com/lists/k0meta/cssfamiliesmovies` or<br>`https://mdblist.com/lists/k0meta/cssfamiliesshows` |
| `StevenLu's Popular Movies`         | [`stevenlu_popular` builder](../files/builders/stevenlu.md)                                                                             |
| `Top 10 Pirated Movies of the Week` | Sourced from mdblist:<br>`https://mdblist.com/lists/hdlists/top-ten-pirated-movies-of-the-week-torrent-freak-com/`                      |

### Tautulli Collections

The Tautulli collections use the [Tautulli builder](../files/builders/tautulli.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### TMDB Collections

The TMDB collections use the [TMDB builder](../files/builders/tmdb.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Trakt Collections

The Trakt collections use the [Trakt builder](../files/builders/trakt.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Streaming Services Collections

The Streaming Services collections use two builders to create the collections:

If you are not using `originals_only`, the collections are created using [`tmdb_discover`](../files/builders/tmdb.md).

If you are using `originals_only`, the collections are created using Kometa-maintained MDBLists.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Universes Collections

The Universe collections are based on either Trakt lists or MDB lists.

If you are interested in seeing the lists that are used for the universe collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Universes; default section 040 (click to expand) <a class="headerlink" href="#universe" title="Permanent link">¶</a>"

    <div id="universe" />

    {%
       include-markdown "./sources/both/universe.md"
    %}

### Network Collections

The Network collections use the [dynamic collections](../files/dynamic.md) system with a default include list and some default add-ons to consolidate some of the networks.

If you are interested in seeing the lists that are used for the network collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Networks; default section 050 (click to expand) <a class="headerlink" href="#network" title="Permanent link">¶</a>"

    <div id="network" />

    {%
       include-markdown "./sources/show/network.md"
    %}

### Genre Collections

The Genre collections use the [dynamic collections](../files/dynamic.md) system based on the genres found in your library and some default add-ons to consolidate some of the genres.

If you are interested in seeing the lists that are used for the genre collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Genres; default section 060 (click to expand) <a class="headerlink" href="#genre" title="Permanent link">¶</a>"

    <div id="genre" />

    {%
       include-markdown "./sources/both/genre.md"
    %}

### Studios Collections

The Studio collections use the [dynamic collections](../files/dynamic.md) system with a default include list and some default add-ons to consolidate some of the studios.

If you are interested in seeing the lists that are used for the studio collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Studios; default section 070 (click to expand) <a class="headerlink" href="#studio" title="Permanent link">¶</a>"

    <div id="studio" />

    {%
       include-markdown "./sources/both/studio.md"
    %}

### Countries Collections

The Country collections use the [dynamic collections](../files/dynamic.md) system with a default include list and some default add-ons to consolidate some of the countries.

If you are interested in seeing the lists that are used for the country collections, you can find them here.

The countries are stored differently for shows and movies, so there are different lists for each library type.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Countries; default section 080 (click to expand) <a class="headerlink" href="#country" title="Permanent link">¶</a>"

    <div id="country" />

    ??? example "Shows (click to expand) <a class="headerlink" href="#country-show" title="Permanent link">¶</a>"

        <div id="country-show" />

        {%
          include-markdown "./sources/show/country.md"
        %}

    ??? example "Movies (click to expand) <a class="headerlink" href="#country-movie" title="Permanent link">¶</a>"

        <div id="country-movie" />

        {%
          include-markdown "./sources/movie/country.md"
        %}

### Regions Collections

The Region collections use the [dynamic collections](../files/dynamic.md) system with a default include list and some default add-ons to consolidate some of the regions.

If you are interested in seeing the lists that are used for the region collections, you can find them here.

The regions are stored differently for shows and movies, so there are different lists for each library type.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Regions; default section 081 (click to expand) <a class="headerlink" href="#region" title="Permanent link">¶</a>"

    <div id="region" />

    ??? example "Shows (click to expand) <a class="headerlink" href="#region-show" title="Permanent link">¶</a>"

        <div id="region-show" />

        {%
          include-markdown "./sources/show/region.md"
        %}

    ??? example "Movies (click to expand) <a class="headerlink" href="#region-movie" title="Permanent link">¶</a>"

        <div id="region-movie" />

        {%
          include-markdown "./sources/movie/region.md"
        %}

### Continents Collections

The Continents collections use the [dynamic collections](../files/dynamic.md) system with some default add-ons to consolidate the countries into continents.

If you are interested in seeing the lists that are used for the continent collections, you can find them here.

The countries are stored differently for shows and movies, so there are different lists for each library type.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Continents; default section 082 (click to expand) <a class="headerlink" href="#continent" title="Permanent link">¶</a>"

    <div id="continent" />

    ??? example "Shows (click to expand) <a class="headerlink" href="#continent-show" title="Permanent link">¶</a>"

        <div id="continent-show" />

        {%
          include-markdown "./sources/show/continent.md"
        %}

    ??? example "Movies (click to expand) <a class="headerlink" href="#continent-movie" title="Permanent link">¶</a>"

        <div id="continent-movie" />

        {%
          include-markdown "./sources/movie/continent.md"
        %}

### Based On A ... Collections

The Based On A ... collections  are created using Kometa-maintained MDBLists.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Audio Languages Collections

The Audio Languages collections use smart filters based on a default list of target languages

If you are interested in seeing the lists that are used for the audio language collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Audio Language; default section 090 (click to expand) <a class="headerlink" href="#audio_language" title="Permanent link">¶</a>"

    <div id="audio_language" />

    {%
       include-markdown "./sources/both/audio_language.md"
    %}

### Subtitle Languages Collections

The Subtitle Languages collections use smart filters based on a default list of target languages

If you are interested in seeing the lists that are used for the subtitle language collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Subtitle Language; default section 095 (click to expand) <a class="headerlink" href="#subtitle_language" title="Permanent link">¶</a>"

    <div id="subtitle_language" />

    {%
       include-markdown "./sources/both/subtitle_language.md"
    %}

### Decades Collections

The Decades collections use the [dynamic collections](../files/dynamic.md) system based on the release dates of the items in your libraries.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Yearly Collections

The Yearly collections use the [dynamic collections](../files/dynamic.md) system based on the release dates of the items in your libraries.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Content Ratings Collections

The Content Rating collections all use the [dynamic collections](../files/dynamic.md) system based on the content ratings of the items in your libraries.  They each have a addons which combine all the ratings in your library into collections reflecting the desired system.

For example, if you use the US Content Ratings collection, it will create collections for each of the US content ratings, and map any non-US content ratings in your library into one of the US content ratings.

Content ratings for Movies and TV differ, so there are different lists for each library type.

??? example "US Content Ratings; default section 110 (click to expand) <a class="headerlink" href="#content_rating_us" title="Permanent link">¶</a>"

    <div id="content_rating_us" />

    ??? example "Shows (click to expand) <a class="headerlink" href="#content_rating_us-show" title="Permanent link">¶</a>"

        <div id="content_rating_us-show" />

        {%
          include-markdown "./sources/show/content_rating_us.md"
        %}

    ??? example "Movies (click to expand) <a class="headerlink" href="#content_rating_us-movie" title="Permanent link">¶</a>"

        <div id="content_rating_us-movie" />

        {%
          include-markdown "./sources/movie/content_rating_us.md"
        %}

??? example "UK Content Ratings; default section 110 (click to expand) <a class="headerlink" href="#content_rating_uk" title="Permanent link">¶</a>"

      <div id="content_rating_uk" />

      {%
        include-markdown "./sources/both/content_rating_uk.md"
      %}

??? example "German Content Ratings; default section 110 (click to expand) <a class="headerlink" href="#content_rating_de" title="Permanent link">¶</a>"

    <div id="content_rating_de" />

    {%
       include-markdown "./sources/both/content_rating_de.md"
    %}

??? example "MyAnimeList Content Ratings; default section 110 (click to expand) <a class="headerlink" href="#content_rating_mal" title="Permanent link">¶</a>"

    <div id="content_rating_mal" />

    {%
       include-markdown "./sources/both/content_rating_mal.md"
    %}

??? example "CommonSense Content Ratings; default section 110 (click to expand) <a class="headerlink" href="#content_rating_cs" title="Permanent link">¶</a>"

    <div id="content_rating_cs" />

    {%
       include-markdown "./sources/both/content_rating_cs.md"
    %}

### Resolution Collections

The Resolution collections use the [dynamic collections](../files/dynamic.md) system based on the resolution of the items in your libraries.

They use a default list of resolutions to create the collections, and some default addons to group resolutions together.

If you are interested in seeing the lists that are used for the universe collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Resolution; default section 120 (click to expand) <a class="headerlink" href="#resolution" title="Permanent link">¶</a>"

    <div id="resolution" />

    {%
       include-markdown "./sources/both/resolution.md"
    %}

### Aspect Ratios Collections

The Aspect Ratio collections use Plex searches and filters based on a fixed list of aspect ratios.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Awards Collections

All the Awards collections use the [IMDb Awards builder](../files/builders/imdb.md) to create the collections.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Actors/Directors/Producers/Writers Collections

All the Awards collections use the [dynamic collections](../files/dynamic.md) system based on the Actors/Directors/Producers/Writers in your library.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

### Franchises Collections

The Continents collections use the [dynamic collections](../files/dynamic.md) system with a default list of target franchises and some default add-ons to group shows and movies into those franchises.

If you are interested in seeing the lists that are used for the franchise collections, you can find them here.

The franchises are different for shows and movies, so there are different lists for each library type.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Franchises; NO default section (click to expand) <a class="headerlink" href="#franchise" title="Permanent link">¶</a>"

    <div id="franchise" />

    ??? example "Shows (click to expand) <a class="headerlink" href="#franchise-show" title="Permanent link">¶</a>"

        <div id="franchise-show" />

        {%
          include-markdown "./sources/show/franchise.md"
        %}

    ??? example "Movies (click to expand) <a class="headerlink" href="#franchise-movie" title="Permanent link">¶</a>"

        <div id="franchise-movie" />

        {%
          include-markdown "./sources/movie/franchise.md"
        %}

### Collectionless Collections

The Collectionless collections use the [`plex_collectionless` builder](../files/builders/plex.md) to create the collection.

Collections and their items are excluded from this collection based on a name prefix or the collection name.

If you are interested in seeing the default prefixes that are used for the collectionless collections, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Collectionless; no default section (click to expand) <a class="headerlink" href="#collectionless" title="Permanent link">¶</a>"

    <div id="collectionless" />

    {%
       include-markdown "./sources/both/collectionless.md"
    %}

## Overlays

Most overlays are based on Plex searches and filters; they typically assume TRaSH naming conventions.

### aspect Overlays

[`plex_search` builder](../files/builders/plex.md) with filters on a limited set of aspect ratios.

### audio_codec Overlays

[`plex_all` builder](../files/builders/plex.md) with filters on both audio channel name and filepath.

### Content Rating Overlays

All Content Rating overlays are based on Plex searches; they all search for a set of content ratings and map them into a single content rating as requested.

### direct_play Overlays

[`plex_search` builder](../files/builders/plex.md) for 4K items.

### episode_info Overlays

Applies to every episode in the library.

### language_count Overlays

[`plex_search` builder](../files/builders/plex.md) for items with any number or <3 audio tracks.

### languages Overlays

[`plex_search` builder](../files/builders/plex.md) on either audio or subtitle tracks names.

### mediastinger Overlays

[`plex_all` builder](../files/builders/plex.md) with filters on `tmdb_keyword: aftercreditsstinger, duringcreditsstinger`

### network Overlays

[`plex_search` builder](../files/builders/plex.md) on network name.  The list of networks is not exposed for customization using template variables.

### ratings Overlays

[`plex_search` builder](../files/builders/plex.md) on ratings as set on items in Plex.

### resolution Overlays

[`plex_search` builder](../files/builders/plex.md) on resolutions and editions as set on items in Plex.

### ribbon Overlays

For the most part, based on the [IMDb Award builder](../files/builders/imdb.md). 

### runtimes Overlays

Applies to every item in the library.

### status Overlays

Applies to every show in the library; uses the [`tmdb_status` builder](../files/builders/tmdb.md).

### streaming Overlays

The Streaming Services overlays use two builders:

If you are not using `originals_only`, the overlays are applied using [`tmdb_discover`](../files/builders/tmdb.md).

If you are using `originals_only`, the overlays are applied using Kometa-maintained MDBLists.

### studio Overlays

[`plex_search` builder](../files/builders/plex.md) on studio name.  The list of studio is not exposed for customization using template variables.

### versions Overlays

[`plex_search` builder](../files/builders/plex.md) for duplicate items or episodes.

### video_format Overlays

[`plex_all` builder](../files/builders/plex.md) with filters on filepath.

## Playlists

The default playlists are based on Trakt lists.

If you are interested in seeing the lists that are used for the default playlists, you can find them here.

These lists are provided for reference.

If you want to customize these collections, refer to [this](#i-want-to-customize-the-defaults).

??? example "Playlists (click to expand) <a class="headerlink" href="#playlist" title="Permanent link">¶</a>"

    <div id="playlist" />

    {%
       include-markdown "./sources/playlist.md"
    %}
