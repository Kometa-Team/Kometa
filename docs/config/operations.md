---
search:
  boost: 4
---
# Library Operations

There are a variety of Library Operations that can be utilized in a library.

Within each library, operations can be defined by using the `operations` attribute, as demonstrated below.

When not using a list under `operations` the whole operations value is one block.

???+ example

    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: imdb
        operations:
          mass_critic_rating_update: tmdb
          split_duplicates: true
    ```

## Operation Blocks

You can create individual blocks of operations by using a list under `operations` with each item in the list being a 
"block" that can be individually scheduled. 

???+ example

    ```yaml
    libraries:
      Movies:
        collection_files:
          - default: imdb
        operations:
          - schedule: weekly(friday)
            mass_critic_rating_update: tmdb
          - schedule: weekly(saturday)
            split_duplicates: true
    ```

## Operation Attributes

###### Assets For All

??? blank "`assets_for_all` - Used to search the asset directories for images for all items in the library.<a class="headerlink" href="#assets-for-all" title="Permanent link">¶</a>"

    <div id="assets-for-all" />Searches the asset directories for images for all items in the library.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `assets_for_all`
    
    **Accepted Values:** `true` or `false`

    ???+ example "Example"
 
        ```yaml
        libraries:
          Movies:
            operations:
              assets_for_all: false
        ```

###### Delete Collections

??? blank "`delete_collections` - Deletes collections based on a set of given attribute.<a class="headerlink" href="#delete-collections" title="Permanent link">¶</a>"

    <div id="delete-collections" />Deletes collections based on a set of given attributes. The Collection must match all
    set attributes to be deleted.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `delete_collections`
    
    **Accepted Values:** There are a few different options to determine how the `delete_collections` works.
    
    <table class="clearTable">
      <tr><td>`managed: true`</td><td>Collection must be Managed to be deleted<br>(collection has the `Kometa` label)</td></tr>
      <tr><td>`managed: false`</td><td>Collection must be Unmanaged to be deleted<br>(collection does not have the `Kometa` label)</td></tr>
      <tr><td>`configured: true`</td><td>Collection must be Configured to be deleted<br>(collection is in the config file of the specific Kometa run)</td></tr>
      <tr><td>`configured: false`</td><td>Collection must be Unconfigured to be deleted<br>(collection is not in the config file of the specific Kometa run)</td></tr>
      <tr><td>`less: ###`</td><td>Collection must contain less than the given number of items to be deleted.<br>### is a Number greater than 0<br>Optional value which if undefined means collections will be deleted regardless of how many items they have</td></tr>
    </table>

    **The collection does not need to be scheduled to be considered configured and only needs to be in the config file.**

    ???+ example "Example"

        Removes all Managed Collections (Collections with the `Kometa` Label) that are not configured in the Current Run.
    
        ```yaml
        libraries:
          Movies:
            operations:
              delete_collections:
                configured: false
                managed: true
        ```

###### Mass Genre Update

??? blank "`mass_genre_update` - Updates the genres of every item in the library.<a class="headerlink" href="#mass-genre-update" title="Permanent link">¶</a>"

    <div id="mass-genre-update" />Updates every item's genres in the library to the chosen site's genres.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `mass_genre_update`
    
    **Accepted Values:** Source or List of sources to use in that order

    <table class="clearTable">
      <tr><td>`tmdb`</td><td>Use TMDb for Genres</td></tr>
      <tr><td>`tvdb`</td><td>Use TVDb for Genres</td></tr>
      <tr><td>`imdb`</td><td>Use IMDb for Genres</td></tr>
      <tr><td>`omdb`</td><td>Use IMDb through OMDb for Genres</td></tr>
      <tr><td>`anidb`</td><td>Use AniDB Main Tags for Genres</td></tr>
      <tr><td>`anidb_3_0`</td><td>Use AniDB Main Tags and All 3 Star Tags and above for Genres</td></tr>
      <tr><td>`anidb_2_5`</td><td>Use AniDB Main Tags and All 2.5 Star Tags and above for Genres</td></tr>
      <tr><td>`anidb_2_0`</td><td>Use AniDB Main Tags and All 2 Star Tags and above for Genres</td></tr>
      <tr><td>`anidb_1_5`</td><td>Use AniDB Main Tags and All 1.5 Star Tags and above for Genres</td></tr>
      <tr><td>`anidb_1_0`</td><td>Use AniDB Main Tags and All 1 Star Tags and above for Genres</td></tr>
      <tr><td>`anidb_0_5`</td><td>Use AniDB Main Tags and All 0.5 Star Tags and above for Genres</td></tr>
      <tr><td>`mal`</td><td>Use MyAnimeList for Genres</td></tr>
      <tr><td>`lock`</td><td>Lock all Genre Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock all Genre Field</td></tr>
      <tr><td>`remove`</td><td>Remove all Genres and Lock all Field</td></tr>
      <tr><td>`reset`</td><td>Remove all Genres and Unlock all Field</td></tr>
      <tr><td colspan="2">List of Strings for Genres (<code>["String 1", "String 2"]</code>)</td></tr>
    </table>

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              mass_genre_update: 
                - imdb
                - tmdb
                - ["Unknown"]
        ```

###### Mass Content Rating Update

??? blank "`mass_content_rating_update` - Updates the content rating of every item in the library.<a class="headerlink" href="#mass-content-rating-update" title="Permanent link">¶</a>"

    <div id="mass-content-rating-update" />Updates every item's content rating in the library to the chosen site's 
    content rating.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `mass_content_rating_update`
    
    **Accepted Values:** Source or List of sources to use in that order
    
    ???+ tip "Note on `mdb` sources"

        MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed. As such, the data that Kometa applies using `mdb_` operations applies may not be the same as you see if you visit those third-party sources directly.

    <table class="clearTable">
      <tr><td>`mdb`</td><td>Use MDBList for Content Ratings</td></tr>
      <tr><td>`mdb_commonsense`</td><td>Use Common Sense Rating through MDBList for Content Ratings</td></tr>
      <tr><td>`mdb_commonsense0`</td><td>Use Common Sense Rating with Zero Padding through MDBList for Content Ratings</td></tr>
      <tr><td>`mdb_age_rating`</td><td>Use MDBList Age Rating for Content Ratings</td></tr>
      <tr><td>`mdb_age_rating0`</td><td>Use MDBList Age Rating with Zero Padding for Content Ratings</td></tr>
      <tr><td>`omdb`</td><td>Use IMDb through OMDb for Content Ratings</td></tr>
      <tr><td>`mal`</td><td>Use MyAnimeList for Content Ratings</td></tr>
      <tr><td>`lock`</td><td>Lock Content Rating Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock Content Rating Field</td></tr>
      <tr><td>`remove`</td><td>Remove Content Rating and Lock Field</td></tr>
      <tr><td>`reset`</td><td>Remove Content Rating and Unlock Field</td></tr>
      <tr><td colspan="2">Any String for Content Ratings</td></tr>
    </table>                                                      

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              mass_content_rating_update: 
                - mdb_commonsense
                - mdb_age_rating
                - NR
        ```

###### Mass Original Title Update

??? blank "`mass_original_title_update` - Updates the original title of every item in the library.<a class="headerlink" href="#mass-original-title-update" title="Permanent link">¶</a>"

    <div id="mass-original-title-update" />Updates every item's original title in the library to the chosen site's 
    original title.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `mass_original_title_update`
    
    **Accepted Values:** Source or List of sources to use in that order
    
    <table class="clearTable">
      <tr><td>`anidb`</td><td>Use AniDB Main Title for Original Titles</td></tr>
      <tr><td>`anidb_official`</td><td>Use AniDB Official Title based on the language attribute in the config file for Original Titles</td></tr>
      <tr><td>`mal`</td><td>Use MyAnimeList Main Title for Original Titles</td></tr>
      <tr><td>`mal_english`</td><td>Use MyAnimeList English Title for Original Titles</td></tr>
      <tr><td>`mal_japanese`</td><td>Use MyAnimeList Japanese Title for Original Titles</td></tr>
      <tr><td>`lock`</td><td>Lock Original Title Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock Original Title Field</td></tr>
      <tr><td>`remove`</td><td>Remove Original Title and Lock Field</td></tr>
      <tr><td>`reset`</td><td>Remove Original Title and Unlock Field</td></tr>
      <tr><td colspan="2">Any String for Original Titles</td></tr>
    </table>                                                      

    ???+ example "Example"

        ```yaml
        libraries:
          Anime:
            operations:
              mass_original_title_update: 
                - anidb_official
                - anidb
                - Unknown
        ```

###### Mass Studio Update

??? blank "`mass_studio_update` - Updates the studio of every item in the library.<a class="headerlink" href="#mass-studio-update" title="Permanent link">¶</a>"

    <div id="mass-studio-update" />Updates every item's studio in the library to the chosen site's studio.
    
    <hr style="margin: 0px;">
    
    **Attribute:** `mass_studio_update`
    
    **Accepted Values:** Source or List of sources to use in that order
    
    <table class="clearTable">
      <tr><td>`anidb`</td><td>Use AniDB Animation Work for Studio</td></tr>
      <tr><td>`mal`</td><td>Use MyAnimeList Studio for Studio</td></tr>
      <tr><td>`tmdb`</td><td>Use TMDb Studio for Studio</td></tr>
      <tr><td>`lock`</td><td>Lock Studio Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock Studio Field</td></tr>
      <tr><td>`remove`</td><td>Remove Studio and Lock Field</td></tr>
      <tr><td>`reset`</td><td>Remove Studio and Unlock Field</td></tr>
      <tr><td colspan="2">Any String for Studio</td></tr>
    </table>                                                      

    ???+ example "Example"

        ```yaml
        libraries:
          Anime:
            operations:
              mass_studio_update: 
                - mal
                - anidb
                - Unknown
        ```

###### Mass Originally Available Update

??? blank "`mass_originally_available_update` - Updates the originally available date of every item in the library.<a class="headerlink" href="#mass-originally-available-update" title="Permanent link">¶</a>"

    <div id="mass-originally-available-update" />Updates every item's originally available date in the library to the 
    chosen site's date.
    
    ???+ tip
    
        As plex does not allow this field to be empty, using `remove` or `reset` will set the date to the Plex default 
        date, which is `1969-12-31`

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_originally_available_update`
    
    **Accepted Values:** Source or List of sources to use in that order

    ???+ tip "Note on `mdb` sources"

        MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed. As such, the data that Kometa applies using `mdb_` operations applies may not be the same as you see if you visit those third-party sources directly.

    <table class="clearTable">
      <tr><td>`tmdb`</td><td>Use TMDb Release Date</td></tr>
      <tr><td>`tvdb`</td><td>Use TVDb Release Date</td></tr>
      <tr><td>`omdb`</td><td>Use IMDb Release Date through OMDb</td></tr>
      <tr><td>`mdb`</td><td>Use MDBList Release Date</td></tr>
      <tr><td>`mdb_digital`</td><td>Use MDBList Digital Release Date</td></tr>
      <tr><td>`anidb`</td><td>Use AniDB Release Date</td></tr>
      <tr><td>`mal`</td><td>Use MyAnimeList Release Date</td></tr>
      <tr><td>`lock`</td><td>Lock Originally Available Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock Originally Available Field</td></tr>
      <tr><td>`remove`</td><td>Remove Originally Available and Lock Field</td></tr>
      <tr><td>`reset`</td><td>Remove Originally Available and Unlock Field</td></tr>
      <tr><td colspan="2">Any String in the Format: YYYY-MM-DD for Originally Available (<code>2022-05-28</code>)</td></tr>
    </table>                                                      

    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              mass_originally_available_update: 
                - mdb_digital
                - mdb
                - 1900-01-01
        ```

###### Mass Added At Update

??? blank "`mass_added_at_update` - Updates the added at date of every item in the library.<a class="headerlink" href="#mass-added-at-update" title="Permanent link">¶</a>"

    <div id="mass-added-at-update" />Updates every item's added at date in the library to the chosen site's date.

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_added_at_update`
    
    **Accepted Values:** Source or List of sources to use in that order

    ???+ tip "Note on `mdb` sources"

        MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed. As such, the data that Kometa applies using `mdb_` operations applies may not be the same as you see if you visit those third-party sources directly.

    <table class="clearTable">
      <tr><td>`tmdb`</td><td>Use TMDb Release Date</td></tr>
      <tr><td>`tvdb`</td><td>Use TVDb Release Date</td></tr>
      <tr><td>`omdb`</td><td>Use IMDb Release Date through OMDb</td></tr>
      <tr><td>`mdb`</td><td>Use MDBList Release Date</td></tr>
      <tr><td>`mdb_digital`</td><td>Use MDBList Digital Release Date</td></tr>
      <tr><td>`anidb`</td><td>Use AniDB Release Date</td></tr>
      <tr><td>`mal`</td><td>Use MyAnimeList Release Date</td></tr>
      <tr><td>`lock`</td><td>Lock Added At Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock Added At Field</td></tr>
      <tr><td>`remove`</td><td>Remove Added At and Lock Field</td></tr>
      <tr><td>`reset`</td><td>Remove Added At and Unlock Field</td></tr>
      <tr><td colspan="2">Any String in the Format: YYYY-MM-DD for Added At (<code>2022-05-28</code>)</td></tr>
    </table>                                                      

    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              mass_added_at_update: 
                - mdb_digital
                - mdb
                - 1900-01-01
        ```

###### Mass Rating Update

??? blank "`mass_***_rating_update` - Updates the audience/critic/user rating of every item in the library.<a class="headerlink" href="#mass-star-rating-update" title="Permanent link">¶</a>"

    <div id="mass-star-rating-update" />Updates every item's audience/critic/user rating in the library to the chosen 
    site's rating.
    
    ???+ warning "Important Note"
        
        This does not affect the icons displayed in the Plex UI. This will place the number of your choice in the 
        relevant field in the Plex database. In other words, if Plex is configured to use Rotten Tomatoes ratings, then 
        no matter what happens with this mass rating update operation, the icons in the Plex UI will remain Rotten 
        Tomatoes. The human who decided to put TMDb ratings in the critic slot and Letterboxd ratings in the audience 
        slot is the only party who knows that the ratings are no longer Rotten Tomatoes. One primary use of this feature
        is to put ratings overlays on posters. More information on what Kometa can do with these ratings can be found 
        [here](../kometa/guides/ratings.md).

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_audience_rating_update`/`mass_critic_rating_update`/`mass_user_rating_update`
    
    **Accepted Values:** Source or List of sources to use in that order

    ???+ tip "Note on `mdb` sources"

        MDBList is not a live reflection of third-party sites such as CommonSense and Trakt. The data on MDBList is often days, weeks and months out of date as it is only periodically refreshed. As such, the data that Kometa applies using `mdb_` operations applies may not be the same as you see if you visit those third-party sources directly.

    <table class="clearTable">
      <tr><td>`tmdb`</td><td>Use TMDb Rating</td></tr>
      <tr><td>`imdb`</td><td>Use IMDb Rating</td></tr>
      <tr><td>`trakt_user`</td><td>Use Trakt User's Personal Rating</td></tr>
      <tr><td>`omdb`</td><td>Use IMDbRating through OMDb</td></tr>
      <tr><td>`mdb`</td><td>Use MDBList Score</td></tr>
      <tr><td>`mdb_average`</td><td>Use MDBList Average Score</td></tr>
      <tr><td>`mdb_imdb`</td><td>Use IMDb Rating through MDBList</td></tr>
      <tr><td>`mdb_metacritic`</td><td>Use Metacritic Rating through MDBList</td></tr>
      <tr><td>`mdb_metacriticuser`</td><td>Use Metacritic User Rating through MDBList</td></tr>
      <tr><td>`mdb_trakt`</td><td>Use Trakt Rating through MDBList</td></tr>
      <tr><td>`mdb_tomatoes`</td><td>Use Rotten Tomatoes Rating through MDBList</td></tr>
      <tr><td>`mdb_tomatoesaudience`</td><td>Use Rotten Tomatoes Audience Rating through MDBList</td></tr>
      <tr><td>`mdb_tmdb`</td><td>Use TMDb Rating through MDBList</td></tr>
      <tr><td>`mdb_letterboxd`</td><td>Use Letterboxd Rating through MDBList</td></tr>
      <tr><td>`mdb_myanimelist`</td><td>Use MyAnimeList Rating through MDBList</td></tr>
      <tr><td>`anidb_rating`</td><td>Use AniDB Rating</td></tr>
      <tr><td>`anidb_average`</td><td>Use AniDB Average</td></tr>
      <tr><td>`anidb_score`</td><td>Use AniDB Review Score</td></tr>
      <tr><td>`mal`</td><td>Use MyAnimeList Score</td></tr>
      <tr><td>`lock`</td><td>Lock Rating Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock Rating Field</td></tr>
      <tr><td>`remove`</td><td>Remove Rating and Lock Field</td></tr>
      <tr><td>`reset`</td><td>Remove Rating and Unlock Field</td></tr>
      <tr><td colspan="2">Any Number between 0.0-10.0 for Ratings</td></tr>
    </table>                                                      

    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              mass_audience_rating_update: 
                - mdb
                - mdb_average
                - 2.0
              mass_critic_rating_update:
                - imdb
                - omdb
                - 2.0
              mass_user_rating_update: 
                - trakt_user
                - 2.0
        ```

###### Mass Episode Rating Update

??? blank "`mass_episode_***_rating_update` - Updates the audience/critic/user rating of every episode in the library.<a class="headerlink" href="#mass-episode-star-rating-update" title="Permanent link">¶</a>"

    <div id="mass-episode-star-rating-update" />Updates every item's episode's audience/critic/user rating in the 
    library to the chosen site's rating.
    
    ???+ warning "Important Note"
        
        This does not affect the icons displayed in the Plex UI. This will place the number of your choice in the 
        relevant field in the Plex database. In other words, if Plex is configured to use Rotten Tomatoes ratings, then 
        no matter what happens with this mass rating update operation, the icons in the Plex UI will remain Rotten 
        Tomatoes. The human who decided to put TMDb ratings in the critic slot and Letterboxd ratings in the audience 
        slot is the only party who knows that the ratings are no longer Rotten Tomatoes. One primary use of this feature
        is to put ratings overlays on posters.  More information on what Kometa can do with these ratings can be found 
        [here](../kometa/guides/ratings.md).

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_episode_audience_rating_update`/`mass_episode_critic_rating_update`/`mass_episode_user_rating_update`
    
    **Accepted Values:** Source or List of sources to use in that order
    
    <table class="clearTable">
      <tr><td>`tmdb`</td><td>Use TMDb Rating</td></tr>
      <tr><td>`imdb`</td><td>Use IMDb Rating</td></tr>
      <tr><td>`lock`</td><td>Lock Rating Field</td></tr>
      <tr><td>`unlock`</td><td>Unlock Rating Field</td></tr>
      <tr><td>`remove`</td><td>Remove Rating and Lock Field</td></tr>
      <tr><td>`reset`</td><td>Remove Rating and Unlock Field</td></tr>
      <tr><td colspan="2">Any Number between 0.0-10.0 for Ratings</td></tr>
    </table>                                                      

    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              mass_episode_audience_rating_update: 
                - tmdb
                - 2.0
              mass_episode_critic_rating_update: 
                - imdb
                - 2.0
        ```

###### Mass Poster Update

??? blank "`mass_poster_update` - Updates the poster of every item in the library.<a class="headerlink" href="#mass-poster-update" title="Permanent link">¶</a>"

    <div id="mas-_poster-update" />Updates every item's poster to the chosen sites poster. Will fall back to `plex` if 
    the given option fails. Assets will be used over anything else.
    
    ???+ warning
    
        When used in combination with Overlays, this could cause Kometa to reset the poster and then reapply all overlays 
        on each run, which will result in [image bloat](../kometa/scripts/imagemaid.md).

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_poster_update`
    
    **Accepted Values:**
    
    <table class="clearTable">
      <tr><td>`source`</td><td>Source of the poster update</td><td>`tmdb`, `plex`, `lock`, or `unlock`</td></tr>
      <tr><td>`seasons`</td><td>Update season posters while updating shows **Default:** `true`</td><td>`true` (default) or `false`</td></tr>
      <tr><td>`episodes`</td><td>Update episode posters while updating shows **Default:** `true`</td><td>`true` (default) or `false`</td></tr>
    </table>
    
    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              mass_poster_update:
                source: tmdb
                seasons: false
                episodes: false
        ```

###### Mass Background Update

??? blank "`mass_background_update` - Updates the background of every item in the library.<a class="headerlink" href="#mass-background-update" title="Permanent link">¶</a>"

    <div id="mass-background-update" />Updates every item's background to the chosen sites background. Will fall back to
    `plex` if the given option fails. Assets will be used over anything else.
    
    ???+ warning
    
        When used in combination with Overlays, this could cause Kometa to reset the background and then reapply all 
        overlays on each run, which will result in [image bloat](../kometa/scripts/imagemaid.md).

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_background_update`
    
    **Accepted Values:**
    
    <table class="clearTable">
      <tr><td>`source`</td><td>Source of the poster update</td><td>`tmdb`, `plex`, `lock`, or `unlock`</td></tr>
      <tr><td>`seasons`</td><td>Update season posters while updating shows **Default:** `true`</td><td>`true` (default) or `false`</td></tr>
      <tr><td>`episodes`</td><td>Update episode posters while updating shows **Default:** `true`</td><td>`true` (default) or `false`</td></tr>
    </table>
    
    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              mass_background_update:
                source: tmdb
                seasons: false
                episodes: false
        ```

###### Mass IMDb Parental Labels

??? blank "`mass_imdb_parental_labels` - Adds IMDb Parental labels of every item in the library.<a class="headerlink" href="#mass-imdb-parental-labels" title="Permanent link">¶</a>"

    <div id="mass-imdb-parental-labels" />Updates every item's labels in the library to match the IMDb Parental Guide.

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_imdb_parental_labels`
    
    **Accepted Values:**
    
    <table class="clearTable">
      <tr><td>`none`</td><td>Apply all Parental Labels with a value of `None`, `Mild`, `Moderate`, or `Severe`</td></tr>
      <tr><td>`mild`</td><td>Apply all Parental Labels with a value of `Mild`, `Moderate`, or `Severe`</td></tr>
      <tr><td>`moderate`</td><td>Apply all Parental Labels with a value of `Moderate` or `Severe`</td></tr>
      <tr><td>`severe`</td><td>Apply all Parental Labels with a value of `Severe`</td></tr>
    </table>
    
    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              mass_imdb_parental_labels: severe
        ```

###### Mass Collection Mode

??? blank "`mass_collection_mode` - Updates the Collection Mode of every item in the library.<a class="headerlink" href="#mass-collection-mode" title="Permanent link">¶</a>"

    <div id="mass-collection-mode" />Updates every Collection in your library to the specified Collection Mode.

    <hr style="margin: 0px;">
    
    **Attribute:** `mass_collection_mode`
    
    **Accepted Values:**
    
    <table class="clearTable">
      <tr><td>`default`</td><td>Library default</td></tr>
      <tr><td>`hide`</td><td>Hide Collection</td></tr>
      <tr><td>`hide_items`</td><td>Hide Items in this Collection</td></tr>
      <tr><td>`show_items`</td><td>Show this Collection and its Items</td></tr>
    </table>
    
    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              mass_collection_mode: hide
        ```

###### Update Blank Track Titles

??? blank "`update_blank_track_titles` - Updates blank track titles of every item in the library.<a class="headerlink" href="#update-blank-track-titles" title="Permanent link">¶</a>"

    <div id="update-blank-track-titles" />Search though every track in a music library and replace any blank track 
    titles with the tracks sort title.

    <hr style="margin: 0px;">
    
    **Attribute:** `update_blank_track_titles`
    
    **Accepted Values:** `true` or `false`
    
    ???+ example "Example"

        ```yaml
        libraries:
          Music:
            operations:
              update_blank_track_titles: true
        ```

###### Remove Title Parentheses

??? blank "`remove_title_parentheses` - Removes title parentheses of every item in the library.<a class="headerlink" href="#remove-title-parentheses" title="Permanent link">¶</a>"

    <div id="remove-title-parentheses" />Search through every title and remove all ending parentheses in an items title 
    if the title is not locked.

    <hr style="margin: 0px;">
    
    **Attribute:** `remove_title_parentheses`
    
    **Accepted Values:** `true` or `false`
    
    ???+ example "Example"

        ```yaml
        libraries:
          Music:
            operations:
              remove_title_parentheses: true
        ```

###### Split Duplicates

??? blank "`split_duplicates` - Splits all duplicate items found in this library.<a class="headerlink" href="#split-duplicates" title="Permanent link">¶</a>"

    <div id="split-duplicates" />Splits all duplicate items found in this library.

    <hr style="margin: 0px;">
    
    **Attribute:** `split_duplicates`
    
    **Accepted Values:** `true` or `false`
    
    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              split_duplicates: true
        ```

###### Radarr Add All

??? blank "`radarr_add_all` - Adds every item in the library to Radarr.<a class="headerlink" href="#radarr-add-all" title="Permanent link">¶</a>"

    <div id="radarr-add-all" />Adds every item in the library to Radarr. 

    ???+ warning
    
        The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same 
        as your Radarr paths you can use the `plex_path` and `radarr_path` [Radarr](radarr.md) details to convert the 
        paths.

    <hr style="margin: 0px;">
    
    **Attribute:** `radarr_add_all`
    
    **Accepted Values:** `true` or `false`
    
    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              radarr_add_all: true
        ```

###### Radarr Remove By Tag

??? blank "`radarr_remove_by_tag` - Removes every item from Radarr with the Tags given.<a class="headerlink" href="#radarr-remove-by-tag" title="Permanent link">¶</a>"

    <div id="radarr-remove-by-tag" />Removes every item from Radarr with the Tags given.

    <hr style="margin: 0px;">
    
    **Attribute:** `radarr_remove_by_tag`
    
    **Accepted Values:** List or comma separated string of tags
    
    ???+ example "Example"

        ```yaml
        libraries:
          Movies:
            operations:
              radarr_remove_by_tag: mytag1, mytag2
        ```

###### Sonarr Add All

??? blank "`sonarr_add_all` - Adds every item in the library to Sonarr.<a class="headerlink" href="#sonarr-add-all" title="Permanent link">¶</a>"

    <div id="sonarr-add-all" />Adds every item in the library to Sonarr. 

    ???+ warning
    
        The existing paths in plex will be used as the root folder of each item, if the paths in Plex are not the same 
        as your Sonarr paths you can use the `plex_path` and `sonarr_path` [Sonarr](sonarr.md) details to convert the 
        paths.

    <hr style="margin: 0px;">
    
    **Attribute:** `sonarr_add_all`
    
    **Accepted Values:** `true` or `false`
    
    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              sonarr_add_all: true
        ```

###### Sonarr Remove By Tag

??? blank "`sonarr_remove_by_tag` - Removes every item from Sonarr with the Tags given.<a class="headerlink" href="#sonarr-remove-by-tag" title="Permanent link">¶</a>"

    <div id="sonarr-remove-by-tag" />Removes every item from Sonarr with the Tags given.

    <hr style="margin: 0px;">
    
    **Attribute:** `sonarr_remove_by_tag`
    
    **Accepted Values:** List or comma separated string of tags
    
    ???+ example "Example"

        ```yaml
        libraries:
          TV Shows:
            operations:
              sonarr_remove_by_tag: mytag1, mytag2
        ```

###### Genre Mapper

??? blank "`genre_mapper` - Maps genres in your library to be changed to other genres.<a class="headerlink" href="#genre-mapper" title="Permanent link">¶</a>"

    <div id="genre-mapper" />Maps genres in your library to be changed to other genres.

    <hr style="margin: 0px;">
    
    **Attribute:** `genre_mapper`
    
    **Accepted Values:** Each attribute under `genre_mapper` is a separate mapping and has two parts.
    
    <table class="clearTable">
      <tr><td>`key`</td><td>Genre you want mapped to the value</td><td>`Action/Adventure, Action & Adventure` in the example below</td></tr>
      <tr><td>`value`</td><td>What the genre will end up as</td><td>`Action` in the example below</td></tr>
    </table>

    ???+ example "Example"
    
        This example will change go through every item in your library and change the genre `Action/Adventure` or 
        `Action & Adventure` to `Action` and `Romantic Comedy` to `Comedy`.
    
        ```yaml
        libraries:
          Movies:
            # Metadata and Overlay files here
            operations:
              genre_mapper:
                "Action/Adventure": Action 
                "Action & Adventure": Action
                Romantic Comedy: Comedy
        ```
    
        To just Remove a Genre without replacing it just set the Genre to nothing like this.
    
        ```yaml
        libraries:
          Movies:
            # Metadata and Overlay files here
            operations:
              genre_mapper:
                "Action/Adventure": Action 
                "Action & Adventure": Action
                Romantic Comedy:
        ```
    
        The above example will change go through every item in your library and change the genre `Action/Adventure` or 
        `Action & Adventure` to `Action` and remove every instance of the Genre `Romantic Comedy`.

###### Content Rating Mapper

??? blank "`content_rating_mapper` - Maps content ratings in your library to be changed to other content ratings.<a class="headerlink" href="#content-rating-mapper" title="Permanent link">¶</a>"

    <div id="content-rating-mapper" />Maps content ratings in your library to be changed to other content ratings.

    <hr style="margin: 0px;">
    
    **Attribute:** `content_rating_mapper`
    
    **Accepted Values:** Each attribute under `content_rating_mapper` is a separate mapping and has two parts.
    
    <table class="clearTable">
      <tr><td>`key`</td><td>Content rating you want mapped to the value</td><td>`PG`, `PG-13` in the example below</td></tr>
      <tr><td>`value`</td><td>What the content rating will end up as</td><td>`Y-10` in the example below</td></tr>
    </table>

    ???+ example "Example"
    
        This example will change go through every item in your library and change the content rating `PG` or `PG-13` to 
        `Y-10` and `R` to `Y-17`.
        
        ```yaml
        libraries:
          Movies:
            # Metadata and Overlay files here
            operations:
              content_rating_mapper:
                PG: Y-10 
                "PG-13": Y-10
                R: Y-17
        ```
        
        To just Remove a content rating without replacing it just set the content rating to nothing like this.
        
        ```yaml
        libraries:
          Movies:
            # Metadata and Overlay files here
            operations:
              content_rating_mapper:
                PG: Y-10 
                "PG-13": Y-10
                R:
        ```
        
        The above example will change go through every item in your library and change the content rating `PG` or 
        `PG-13` to `Y-10` and remove every instance of the content rating `R`.

###### Metadata Backup

??? blank "`metadata_backup` - Creates/Maintains a Kometa Metadata File for the library.<a class="headerlink" href="#metadata-backup" title="Permanent link">¶</a>"

    <div id="metadata-backup" />Creates/Maintains a Kometa Metadata File with a full `metadata` mapping based
    on the library's items locked attributes.

    If you point to an existing Metadata File then Kometa will Sync the changes to the file, so you won't lose non plex 
    changes in the file.

    <hr style="margin: 0px;">
    
    **Attribute:** `metadata_backup`
    
    **Accepted Values:** There are a few different options to determine how the `metadata_backup` works.
    
    <table class="clearTable">
      <tr><td>`path`</td><td>Path to where the metadata will be saved/maintained<br>**Default:** `<<library_name>>_Metadata_Backup.yml in your config folder`<br>**Values:** Path to Metadata File</td></tr>
      <tr><td>`exclude`</td><td>Exclude all listed attributes from being saved in the collection file<br>**Values:** `Comma-separated string or list of attributes`</td></tr>
      <tr><td>`sync_tags`</td><td>All Tag Attributes will have the `.sync` option and blank attribute will be added to sync<br>**Default:** `false`<br>**Values:** `true` or `false`</td></tr>
      <tr><td>`add_blank_entries`</td><td>Will add a line for entries that have no metadata changes<br>**Default:** `true`<br>**Values:** `true` or `false`</td></tr>
    </table>

    ???+ example "Example"
    
        ```yaml
        libraries:
          Movies:
            operations:
              metadata_backup:
                path: config/Movie_Backup.yml
                sync_tags: true
                add_blank_entries: false
        ```
