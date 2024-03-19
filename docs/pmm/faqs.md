---
search:
  boost: 4
---
# FAQ & Knowledgebase

This page aims to provide knowledge based on combined user experience, and to answer the frequent questions that we are asked in our [Discord Server](https://metamanager.wiki/en/latest/discord/).

If you have a question that is not answered here, try entering some keywords into the search bar above, or join our [Discord Server](https://metamanager.wiki/en/latest/discord/).

## Frequently Asked Questions

This section aims to answer the most commonly asked questions that users have.

### PMM Versions & Updating

The commands here should work in any terminal on the respective platforms, but that can't be guaranteed. If you know shortcuts for some of these things, go ahead and use them. For example, in many terminals, `cd ~/Plex-Meta-Manager` is the same as `cd /Users/YOUR_USERNAME/Plex-Meta-Manager`.  

Your PMM installation may not be located at the paths referenced below. These are the paths used in the walkthroughs in this documentation, so if you installed it somewhere else you will have to change the path[s] to reflect your system and the choices you made during installation.

??? question "How do I update to the latest version of Plex Meta Manager?"

    === ":fontawesome-brands-linux: Linux"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    
    === ":fontawesome-brands-apple: macOS"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-windows: Windows"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username and the drive letter if needed]

            C:
            cd C:\Users\YOUR_USERNAME\Plex-Meta-Manager
            git stash
            git stash clear
            git pull
            .\pmm-venv\Scripts\activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-docker: Docker"
    
        [type this into your terminal]

            docker pull meisnate12/plex-meta-manager:TAG_HERE

        replacing TAG_HERE with latest, develop, or nightly [whichever you are currently using]

        Then recreate your container via whatever means you used to create it [docker run, docker-compose, etc.].

        If you are using Docker on a NAS like Synology or UNRaid, they will provide some means of doing those two things.

??? question "How do I switch to the develop branch?"

    === ":fontawesome-brands-linux: Linux"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git checkout develop
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt


        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-apple: macOS"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git checkout develop
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-windows: Windows"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username and the drive letter if needed]

            C:
            cd C:\Users\YOUR_USERNAME\Plex-Meta-Manager
            git stash
            git stash clear
            git checkout develop
            git pull
            .\pmm-venv\Scripts\activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-docker: Docker"
    
        [type this into your terminal]

            docker pull meisnate12/plex-meta-manager:develop

        Then recreate your container via whatever means you used to create it [docker run, docker-compose, etc.], changing the image in the docker command or the `docker-compose.yml` to `meisnate12/plex-meta-manager:develop`.

        If you are using Docker on a NAS like Synology or UNRaid, they will provide some means of doing those two things.


??? question "How do I switch to the nightly branch"

    === ":fontawesome-brands-linux: Linux"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git checkout nightly
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-apple: macOS"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git checkout nightly
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-windows: Windows"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username and the drive letter if needed]

            C:
            cd C:\Users\YOUR_USERNAME\Plex-Meta-Manager
            git stash
            git stash clear
            git checkout nightly
            git pull
            .\pmm-venv\Scripts\activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-docker: Docker"
    
        [type this into your terminal]

            docker pull meisnate12/plex-meta-manager:nightly

        Then recreate your container via whatever means you used to create it [docker run, docker-compose, etc.], changing the image in the docker command or the `docker-compose.yml` to `meisnate12/plex-meta-manager:nightly`.

        If you are using Docker on a NAS like Synology or UNRaid, they will provide some means of doing those two things.

??? question "How do I switch back to the master branch?"

    === ":fontawesome-brands-linux: Linux"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git checkout master
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-apple: macOS"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username]

            cd /Users/YOUR_USERNAME/Plex-Meta-Manager
            git stash
            git stash clear
            git checkout master
            git pull
            source pmm-venv/bin/activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-windows: Windows"
    
        [type this into your terminal, changing `YOUR_USERNAME` to your username and the drive letter if needed]

            C:
            cd C:\Users\YOUR_USERNAME\Plex-Meta-Manager
            git stash
            git stash clear
            git checkout master
            git pull
            .\pmm-venv\Scripts\activate
            python -m pip install -r requirements.txt

        These two commands:

            git stash
            git stash clear

        Will reset any changes you have made to PMM-owned files [YOUR CONFIG FILES ARE NOT AFFECTED]. You shouldn't be doing this, so typically this will not lose any of your work. If you have done this, the assumption is that you know enough about `git` to know how to prevent that from happening.

    === ":fontawesome-brands-docker: Docker"
    
        [type this into your terminal]

            docker pull meisnate12/plex-meta-manager:latest

        Then recreate your container via whatever means you used to create it [docker run, docker-compose, etc.], changing the image in the docker command or the `docker-compose.yml` to `meisnate12/plex-meta-manager:latest`.

        If you are using Docker on a NAS like Synology or UNRaid, they will provide some means of doing those two things.

### Performance & Scheduling

??? question "Any tips on increasing PMM performance?"

    Use PMM Caching where possible, this allows PMM to temporarily store commonly-used information so that it can be retrieved more efficiently. There are [multiple things](https://metamanager.wiki/en/latest/search.html?q=cache&check_keywords=yes&area=default) that can be cached within PMM.
    
    Run PMM after PLEX Scheduled Tasks, as Plex's API tends to be slower at responding whilst it is performing the tasks. By default, PMM runs at 5AM to avoid the 3-5am window that Plex suggests for Scheduled Tasks.
    
    For users who are more technically advanced and happy to risk manipulating the Plex database, considering altering the [PRAGMA_CACHE settings](https://www.reddit.com/r/PleX/comments/ic3cjr/anyone_try_giving_sqlite3_more_cache_to_help/) within Plex.
    
    **Note:** you MUST use the version of sqlite3 tool that comes with your running version of PLEX or you will mess up your PLEX DB beyond repair. See [this article](https://support.plex.tv/articles/repair-a-corrupted-database/) on how to find the proper version for your setup.


??? question "Why does my PMM run take so long to complete?"

    Every time an item (media, collection, overlay) needs to be updated, PMM needs to send the request to Plex, and then receive confirmation back from Plex that the action has been completed. This can take anywhere from seconds to minutes depending on when Plex provides a response. Given that the typical run can update hundreds or even thousands of items, this can quickly add up to a lot of time. If "Mass Update" operations are used, then every single item in the library needs to go through this process, which can be lengthy. 
    
    Overlays can be particularly cumbersome as PMM needs to perform the following actions for each of the items that need to have an overlay applied:

    - Check which overlays are applicable (this will take more time depending on how many overlays you are applying)
        - Compare the current poster to confirm what overlays are already applied, if changes are needed then continue with the following steps
        - Grab source image from Plex and save it to disk
        - Draw each overlay image on top of the source image
        - save final image to disk
        - Tell Plex to apply new image to the item
        - Wait for Plex to respond confirming that the change has been made

    The above two points can be greatly exacerbated if PMM has to update every episode within a Show library rather than just the Shows themselves, as there can often be hundreds of thousands of episodes to be updated with mass operations or overlays.

    Additionally, some collections require a lot of computing resources to determine the critera of the collections that are to be made. This is commonly seen in the Defaults files for Actor/Director/Producer/Writer which need to get the crew information for each of the movies/shows within your library, and then calculate which ones appear the most to find out which are the most popular. The larger your library, the longer this process will take.


??? question "Can I schedule library operations and/or overlays to happen at a different time than collections?"

    Yes, the recommended approach is to set up a new library for the Operations/Overlays, mapping it back to the original library, and then scheduling the library, as outlined below
    
    ```yaml
    libraries:
      Movie Operations:           # NAME DOESN'T MATTER BUT MUST BE UNIQUE
        library_name: Movies      # THIS MUST MATCH A LIBRARY IN PLEX
        schedule: weekly(monday)
        operations:
          split_duplicates: true
        overlay_files:
          - pmm: resolution
    ```

### Errors & Issues

??? question "Why doesn't PMM let me enter my authentication information for Trakt/MAL?"

    PMM needs to run in an interactive mode which allows the user to enter information (such as the Trakt/MAL PIN) as part of the authentication process. This can prove troublesome in some environments, particularly NAS.
    
    Chazlarson has developed an online tool which will allow you to perform the authentication of both Trakt and MAL outside of PMM, and will then provide you the completed code block to paste into your config.yml.
    
    The scripts can be found here. Click the green play button, wait a little bit, then follow the prompts. 

    [MyAnimeList Authenticator](https://replit.com/@chazlarson/MALAuth)

    [Trakt Authenticator](https://replit.com/@chazlarson/TraktAuth)


??? question "Why am I seeing "(500) Internal Server Error" in my log files?"

    A 500 Internal Server Error happens when the server has an unexpected error when responding to an API request.
    
    There could be any number of reasons why this happens and it depends on what server PMM is talking to although it's most likely coming from your Plex Server.
    
    Most of the time these errors need to be resolved by changing something specific to your set up but some do come up that can be fixed (i.e. Plex throws one if you upload a photo larger than 10 MB)
    
    Many Appbox Setups will throw this error when too many requests are sent, or if the central metadata repository is not properly configured to allow users to upload custom posters.
    
    Take a look at the following logs:

    :one: Settings | Manage | Console -> then filter on Error and Warning to see what might be going on
    
    :two: Check the plex logs (container or other) for the "Busy DB Sleeping for 200ms)
    
    There is nothing that PMM or our support staff can really do to resolve a 500 error.

## Knowledgebase

This section aims to provide some insight as to articles/information that we feel is important to document as they may pop up infrequently but often enough to require entry here.

### PMM 1.20 Release Changes

With the release of PMM 1.20, several changes have been made. Please read the document below thoroughly!

??? blank "`metadata_path` and `overlay_path` are now legacy attributes (click to expand).<a class="headerlink" href="#metadata-overlay-path" title="Permanent link">¶</a>"

    <div id="metadata-overlay-path" />

    The attributes `metadata_path` and `overlay_path` are now legacy, and will likely produce an error `metadata attribute is required` when running PMM.

    We have new attributes: `collection_files`, `overlay_files` and `metadata_files` which you can read more about on the [Libraries Attributes page](../config/libraries.md#attributes)

    Whilst this error can be ignored, we strongly advise you to move over to the new attributes, which can be done following this guidance:

    :fontawesome-solid-1: If your YAML file creates collections or is a PMM Defaults Collection File then it belongs under `collection_files`. 
    
    :fontawesome-solid-2: If your YAML file creates overlays or is a PMM Defaults Overlay File then it belongs under `overlay_files`
    
    :fontawesome-solid-3: If your YAML file edits item metadata ([see this example](../files/metadata.md/#__tabbed_1_1)) then it belongs under `metadata_files`
    
    If your file creates collections AND edits item metadata, then it should go in both `collection_files` and `metadata_files`
    
    If you are unsure on the above, the majority of `metadata_path` files  will now fall under `collection_files`, and all `overlay_path` files will now fall under `overlay_files`.

    If you require any assistance with this, please visit our Discord Server where we can assist you.

    Below is an example of the new attributes in use:

    ```yaml
    libraries:
      Movies:
        collection_files: #(1)!
          - file: config/Movies.yml #(2)!
          - pmm: imdb #(2)!
        metadata_files: #(3)!
          - file: config/MetadataEdits.yml #(4)!
        overlay_files: #(5)!
          - file: config/Overlays.yml #(6)!
          - pmm: audio_codec #(6)!
    ```

    1.  This attribute used to be `metadata_path` and defines files that will relate to Collections
    2.  These files are placed within `collection_files` because they define how Collections are built/maintained.
    3.  This attribute used to be `metadata_path` and defines files that will relate to Metadata Edits
    4.  These files are placed within `metadata_files` because they define Metadata Edits rather than collections.
    5.  This attribute used to be `overlay_path` and defines files that will relate to Overlays
    6.  These files are placed within `overlay_files` because they define how Overlays are built/maintained.

??? blank "`remove_` `reset_` `reapply_` and `schedule_` attributes for `overlays` are now Library Attributes (click to expand).<a class="headerlink" href="#overlay-library-attributes" title="Permanent link">¶</a>"

    <div id="overlay-library-attributes" />

    The attributes `remove_overlays`, `reset_overlays`, `reapply_overlays` and `schedule_overlays` are now Library Attributes and are called at the library level rather than within `overlay_path`.

    This change has been made to make these attributes consistent with other attributes of a similar nature.

    Whilst the previous method still works, we strongly advise you to move over to the new attributes, which can be done by looking at the following sample YAML:

    ```yaml
    libraries:
      Movies:
        remove_overlays: false
        reapply_overlays: false #(1)!
        # reset_overlays: plex #(2)!
        schedule_overlays: daily
        overlay_files:
          - pmm: audio_codec
    ```

    1.  We strongly advise never setting this to `true` as it can cause [Image Bloat](scripts/image-cleanup.md)
    2.  This is purely an example, you do not need to specify `reset_overlays` or any of these attributes unless you specifically need to use them.

??? blank "`imdb_list` no longer works for Title or Keyword search URLs (click to expand).<a class="headerlink" href="#imdb-search" title="Permanent link">¶</a>"

    <div id="imdb-search" />

    As a result of IMDb changing their back-end code, `imdb_list` can no longer be used for URLs which start with `https://www.imdb.com/search/title/` or `https://www.imdb.com/search/keyword/`

    All URLs used with `imdb_list` **must** start with `https://www.imdb.com/list/`

    We have introduced the [IMDb Search Builder](../files/builders/imdb.md#imdb-search) which replaces the functionality that `search/title/` and `search/keyword/` used to provide.

    As an example, the `imdb_search` builder for `https://www.imdb.com/search/keyword/?keywords=christmas-movie` would be:

    ```yaml
    collections:
      Christmas Movies:
        imdb_search:
          keyword: christmas movie
    ```

    And the `imdb_search` builder for `https://www.imdb.com/search/title/?title_type=feature,tv_movie,tv_special,video&num_votes=100,&keywords=spy,espionage` would be:

    ```yaml
    collections:
      Spy Movies:
        imdb_search:
          type: movie, tv_movie, tv_special, video
          votes.gte: 100
          keyword.any: spy, espionage
    ```

??? blank "FlixPatrol Default Files and Builders have been removed (click to expand).<a class="headerlink" href="#flixpatrol" title="Permanent link">¶</a>"

    <div id="flixpatrol" />

    Due to FlixPatrol moving a lot of their data behind a paywall and them reworking their pages to remove IMDb IDs and 
    TMDb IDs the flixpatrol builders and default files have been removed. There currently are no plans to re-add them.

??? blank "PMM Default `other_award` replaced with individual Award files (click to expand).<a class="headerlink" href="#awards" title="Permanent link">¶</a>"

    <div id="awards" />

    The PMM Default file `other_award` is now deprecated and will no longer function.

    Individual PMM Default files have been introduced for several Awards, see the [Awards List](../defaults/collection_list.md#award-collections) for more information on the new options.
