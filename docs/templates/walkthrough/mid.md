
<!--all-->
### Create a directory to quiet an error later

The default config file contains a reference to a directory that will show an error in the output later. 
That error can safely be ignored, but it causes some confusion with new users from time to time.

We'll create it here so the error doesn't show up later.

<!--all-->

<!-local-docker-->
=== ":fontawesome-brands-linux: Linux"

    [type this into your terminal]

    ```shell
    mkdir config/assets
    ```

=== ":fontawesome-brands-apple: macOS"

    [type this into your terminal]

    ```shell
    mkdir config/assets
    ```

=== ":fontawesome-brands-windows: Windows"

    [type this into your terminal]

    ```
    mkdir config\assets
    ```

<!-local-docker-->

<!--unraid-->
=== ":fontawesome-brands-linux: unRAID"

    [type this into your Kometa `>_Console`]

    ```
    mkdir config/assets
    ```

<!--unraid-->

<!--all-->
### Setting up the initial config file

Next you’ll set up the config file. This tells Kometa how to connect to Plex and a variety of other services.

Before you do this you’ll need:

1. TMDb API key. They’re free.
2. Plex URL and Token

There are a bunch of other services you *can* configure in the config file, but these two are the bare minimum.

#### Getting a TMDb API Key

Note that if you already have an API key, you can use that one. You don’t need another.

Go to [https://www.themoviedb.org/](https://www.themoviedb.org/). 
Log into your account [or create one if you don’t have one already], then go to “Settings” under your account menu.

![profile-menu](./../../../assets/images/kometa/install/tmdb-profile-menu.jpg)

In the sidebar menu on the left, select “API”.

![sidebar](./../../../assets/images/kometa/install/tmdb-sidebar.jpg)

Click to generate a new API key under "Request an API Key". If there is already one there, copy it and go to the next step.

There will be a form to fill out; the answers are arbitrary. The URL can be your personal website, or probably even google.com or the like.

Once you’ve done that there should be an API Key available on this screen. If you see v3 and v4, you want the v3 key.

![apikey](./../../../assets/images/kometa/install/tmdb-apikey.jpg)

Copy that value, you’ll need it for the config file.

#### Getting a Plex URL and Token

The Plex URL is whatever URL you’d use **from this machine** to connect directly to your Plex server [i.e. NOT app.plex.tv].

As with the TMDb API Key, if you already have a Plex Token, you can use that one.

This article will describe how to get a token: [Finding an authentication token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

#### Editing the config file

<!--all-->

<!-local-docker-->
Open the config file in an editor:

=== ":fontawesome-brands-linux: Linux"

      [type this into your terminal]
   
      ```shell
      nano config/config.yml
      ```
    
      I’m using `nano` here mostly because it’s simpler than any other editor on Linux.
    
      You can use any other text editor you wish, provided it saves files as PLAIN TEXT. `vi`, `emacs`, etc.

=== ":fontawesome-brands-apple: macOS"

      [type this into your terminal]
    
      ```shell
      nano config/config.yml
      ```
    
      I’m using `nano` here simply because it’s built into OSX. You can use any other text editor you wish, provided it saves files as PLAIN TEXT. BBedit, TextMate, VSCode, etc.
    
      A common mistake is using TextEdit.app, which saves files as RTF by default.

=== ":fontawesome-brands-windows: Windows"

      [type this into your terminal]

      ```shell
      notepad .\config\config.yml
      ```
      I’m using `notepad` here simply because it’s built into Windows. You can use any other text editor you wish, provided it saves files as PLAIN TEXT.
    
From here on in, when this walkthrough says "open the config file", I mean this `nano` or `notepad` command.

??? info ":fontawesome-brands-linux: What if I see an error?"

    If you see something like:
    ```shell { .no-copy }
    $ nano config/config.yml
    zsh: command not found: nano
    ```
    You need to switch to another editor like `vi` or `emacs`, or install `nano`, which you would do with `sudo apt install nano`

<!-local-docker-->

<!--unraid-->
First, make a copy of the template:

=== ":fontawesome-brands-linux: unRAID"

    Get a copy of the template to edit [type this into your Kometa `>_Console`]:
    ```shell
    curl -fLvo config/config.yml https://raw.githubusercontent.com/Kometa-Team/Kometa/master/config/config.yml.template
    ```

Now open the copy in an editor on the machine of your choice:

=== ":fontawesome-brands-linux: unRAID"

    [type this into your Kometa `>_Console`]
    
    ```shell
    nano config/config.yml
    ```
    
    I’m using `nano` here mostly because it’s simpler than any other editor on Linux.

    You can use any other text editor you wish, provided it saves files as PLAIN TEXT. `vi`, `emacs`, etc.

From here on in, when this walkthrough says "open the config file", I mean this `nano` or `notepad` command. **Don't copy the template again**.

<!--unraid-->

<!--all-->

---

Scroll down a bit and update the three things you just collected; Plex URL, Plex Token, and TMDb API Key.

```yaml
plex:                                           # Can be individually specified per library as well
  url: http://bing.bang.boing                <<< ENTER YOUR PLEX URL HERE
  token: XXXXXXXXXXXXXXXXXXXX                <<< ENTER YOUR PLEX TOKEN HERE
  timeout: 60
  db_cache:
  clean_bundles: false
  empty_trash: false
  optimize: false
tmdb:
  apikey: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   <<< ENTER YOUR TMDb API KEY HERE
  language: en
```

Now scroll up and look at the top section:

```yaml
## This file is a template remove the .template to use the file

libraries:                       # This is called out once within the config.yml file
  Movies:                        # Each library must match the Plex library name
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
    remove_overlays: false       # Set this to true to remove all overlays
    overlay_files:
      - default: ribbon              # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  TV Shows:
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
    remove_overlays: false       # Set this to true to remove all overlays
    overlay_files:
      - default: ribbon              # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  Anime:
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: anilist             # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
  Music:
    collection_files:
      - file: config/Music.yml   # This is a local file THAT YOU MIGHT CREATE
playlist_files:
  - default: playlist                # This is a file within Kometa's defaults folder
  # see the wiki for how to use local files, folders, URLs, or files from git
```

You will ultimately need an entry here for each of the libraries on which you want Kometa to act. 
Those top-level elements [Movies, TV Shows, Anime, Music] are names of libraries on your Plex server.

For now, follow these steps:

- Delete the "TV Shows", "Anime" and "Music" sections from the config file
- Delete the "remove_overlays" line
- Delete the "overlay_files" section
- Delete the "playlist_files" section
- Rename "Movies" to "Movies-NOSUCHLIBRARY"

The top bit of your config file should now look like this:

```yaml
libraries:
  Movies-NOSUCHLIBRARY:                        # Each library must match the Plex library name
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
```

???+ warning

    If the top bit of your config file does not look like this, make the necessary adjustments. 

    You should not have any `overlay_files` or `playlist_files` at this stage, if you do then remove them.

This is intended to cause an error for illustration that you will then fix.

**Be very careful with the indentation and ensure it looks exactly like the above; each line indented using two spaces, NOT TABS, indentation is significant in YAML.**

#### Testing the config file

Save the file:

<!--all-->

<!-local-docker-->
=== ":fontawesome-brands-linux: Linux"

    If you're using `nano`, type control-`x`, then `y`, then the enter key.

=== ":fontawesome-brands-apple: macOS"

    If you're using `nano`, type control-`x`, then `y`, then the enter key.

=== ":fontawesome-brands-windows: Windows"

    If you're using `notepad`, type control-`s` or choose `Save` from the `File` menu.

<!-local-docker-->

<!--unraid-->
=== ":fontawesome-brands-linux: unRAID"

    If you're using `nano`, type control-`x`, then `y`, then the enter key.

<!--unraid-->

<!--all-->

{% include-markdown "./run.md" include-tags='INCLUDE_TAGS' %}

I’ve removed some of the lines for space, but have left the important bits:

```shell { .no-copy }
...
|                                            Starting Run|
...
| Locating config...
|
| Using /Users/mroche/Kometa/config/config.yml as config
...
| Connecting to TMDb...
| TMDb Connection Successful
...
| Connecting to Plex Libraries...
...
| Connecting to Movies-NOSUCHLIBRARY Library...                                                      |
...
| Plex Error: Plex Library Movies-NOSUCHLIBRARY not found                                            |
| Movies-NOSUCHLIBRARY Library Connection Failed                                                     |
|====================================================================================================|
| Plex Error: No Plex libraries were connected to                                                    |
...
```

You can see there that Kometa found its config file, was able to connect to TMDb, was able to connect to Plex, and then failed trying to read the “Movies-NOSUCHLIBRARY" library, which of course doesn’t exist.

Open the config file again and change "Movies-NOSUCHLIBRARY" to reflect *your own* Movie library in Plex.

Since we're using the `plex-test-libraries` media, our Movie library is called “test_movie_lib", so mine looks like this:

```yaml
libraries:
  test_movie_lib:                            ## <<< CHANGE THIS LINE
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
```

At this point, the top bit of your config file should look like this:

```yaml
libraries:
  THE_NAME_OF_YOUR_MOVIE_LIBRARY:         ## <<< CHANGE THIS LINE
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
```

Where `THE_NAME_OF_YOUR_MOVIE_LIBRARY` has been replaced by the name of your movie library as shown in Plex ["test_movie_lib" here]:

![movie-lib-name](./../../../assets/images/kometa/install/movie-lib-name.png)

### Creating a few sample collections

Kometa provides an extensive collection of "default" collection, overlay and playlist files.

These files provide a simple way for you to create collections/overlays/playlists based on franchises or awards or actors, etc.

The config we are working on links to two Defaults Collection Files, these lines in your config file:

```yaml
libraries:
  test_movie_lib:
    collection_files:
      - default: basic               # <<< DEFAULTS COLLECTION FILE
      - default: imdb                # <<< DEFAULTS COLLECTION FILE
```

Collections that will be created include:

  - Newly Released
  - New Episodes [TV libraries only]
  - IMDb Popular
  - IMDb Top 250
  - IMDb Lowest Rated

{% include-markdown "./run.md" include-tags='INCLUDE_TAGS' %}

<!--all-->

Depending on the size of the library, this may take a while.

As it builds the collections, you should see a fair amount of logging about which movies are being added and which ones aren’t found. 
Once it completes, go to Plex, go to your Movies library, and click “Collections” at the top.

On my test library, this created four collections. You may see fewer depending on what specific movies are in that library.

![default-collections](./../../../assets/images/kometa/install/default-collections.png)

Perhaps you can do everything you want in terms of collections [award collections, actor collections, genre collections, franchise collections, etc] with the defaults. 
You can investigate what they can provide under the "Defaults" heading at the top of this wiki.

### Setting up a collection file and creating a sample collection

<!--unraid-->
If the default collection files do not allow you to create the collections you want, you can define your own collections in your own collection files to do whatever
you like within the capabilities of Kometa. We will create a simple collection that will contain 20 comedy movies released since 2012.

First, open the Collection File [this will create the file if it doesn't already exist]:

=== ":fontawesome-brands-linux: unRAID"

    [type this into your Kometa `>_Console`]
    
    ```shell
    nano "config/Movies.yml"
    ```

In this file, add the following, exactly as it is shown here; remember that spacing is significant in YAML files:

```yaml
collections:
  Recent Comedy:
    plex_search:
      all:
        genre: Comedy
        year.gte: 2012
      limit: 20
```

{% include-markdown "./save.md" include-tags='INCLUDE_TAGS' %}

Next, add a reference to this file to your config file.

Open the config file again and add the last line shown below:

```yaml
libraries:
  test_movie_lib:
    collection_files:
      - default: basic
      - default: imdb
      # see the wiki for how to use local files, folders, URLs, or files from git
      - file: config/Movies.yml     ## <<< ADD THIS LINE
```

That line needs to match the path you used when you created the file a moment ago. If you are copy-pasting these commands, it does.

<!--unraid-->

<!--local-docker-->
If the default collection files do not allow you to create the collections you want, you can define your own collections in your own collection files to do 
whatever you like within the capabilities of Kometa. We will create a simple collection that will contain 20 comedy movies released since 2012.

First, open the Collection File [this will create the file if it doesn't already exist]:

=== ":fontawesome-brands-linux: Linux"

    [type this into your terminal]
    
    ```shell
    nano "config/Movies.yml"
    ```

=== ":fontawesome-brands-apple: macOS"

    [type this into your terminal]
    
    ```shell
    nano "config/Movies.yml"
    ```

=== ":fontawesome-brands-windows: Windows"

    [type this into your terminal]
   
    ```shell
    notepad "config\Movies.yml"
    ```

In this file, add the following, exactly as it is shown here; remember that spacing is significant in YAML files:

```yaml
collections:
  Recent Comedy:
    plex_search:
      all:
        genre: Comedy
        year.gte: 2012
      limit: 20
```

{% include-markdown "./save.md" include-tags='INCLUDE_TAGS' %}

Next, add a reference to this file to your config file.

Open the config file again and add the last line shown below:

```yaml
libraries:
  test_movie_lib:
    collection_files:
      - default: basic
      - default: imdb
      # see the wiki for how to use local files, folders, URLs, or files from git
      - file: config/Movies.yml     ## <<< ADD THIS LINE
```

That line needs to match the path you used when you created the file a moment ago. If you are copy-pasting these commands, it does.

<!--local-docker-->
<!--all-->
{% include-markdown "./save.md" include-tags='INCLUDE_TAGS' %}

{% include-markdown "./run.md" include-tags='INCLUDE_TAGS' %}

You should see that the Collection File gets loaded:

```shell { .no-copy }
| Loading Collection File: config/Movies.yml
| Collection File Loaded Successfully
```

As it builds the collection, you should see a fair amount of logging about which movies are being added and which ones aren’t found. 
Once it completes, go to Plex, go to your Movies library, and click “Collections” at the top.

You should see the new collection:

![finished-collections](./../../../assets/images/kometa/install/finished-collections.png)

When you click into each, you’ll see the movies that Kometa added to each collection.

Each time you run the script, new movies that match the collection definitions will be added. 
For example, if you don’t have “The ShawShank Redemption” now, when you download it and run Kometa again it will be added to the IMDB 250 collection.

### Adding Overlays to movies

The default collection files include a set of overlays you can add to your posters.

We'll add resolution overlays to the movies in this library as an example.

Open the config file again and add the last three lines shown below:

```yaml
libraries:
  test_movie_lib:
    collection_files:
      - default: basic               # This is a file within the defaults folder in the Repository
      - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
      - file: config/Movies.yml
    remove_overlays: false            ## <<< ADD THIS LINE
    overlay_files:                         ## <<< ADD THIS LINE
      - default: resolution                   ## <<< ADD THIS LINE
```

{% include-markdown "./save.md" include-tags='INCLUDE_TAGS' %}

{% include-markdown "./run.md" include-tags='INCLUDE_TAGS' %}

While it runs this time you should see the previous collections go by pretty quickly, since they aren't changing, 
and then a lot of logging as Kometa decides which overlays apply to which movies.

This may take quite a while depending on the size of this library.

Eventually, you'll see it start applying overlays to all your movies:

```shell { .no-copy }
|=========================================================|
|    Applying Overlays for the test_movie_lib Library     |
|=========================================================|
|                                                         |
| 10 Cloverfield Lane         | Overlays Applied: 4K-HDR  |
| 10 Minutes Gone             | Overlays Applied: 4K-HDR  |
| 10 Things I Hate About You  | Overlays Applied: 4K-HDR  |
| 12 Mighty Orphans           | Overlays Applied: 4K-HDR  |
| 12 Monkeys                  | Overlays Applied: 4K-DV   |
| 12 Strong                   | Overlays Applied: 4K-HDR  |
...
```

When it finishes, go to the Library tab in this library in Plex:

![overlaid-posters](./../../../assets/images/kometa/install/overlaid-posters.png)

### What comes next:

If you want to remove those overlays, open the config file, change the value of `remove_overlays` to `true`, and rerun Kometa.

```yaml
    remove_overlays: true
    overlay_files:
      - default: resolution
```

If you want to remove those collections, open the config file, remove or comment out [add `#` to the beginning] any or all of those lines under `collection_files`, 
and delete the collections manually from Plex.

```yaml
libraries:
  test_movie_lib:
    collection_files:
      # - default: basic               # This is a file within the defaults folder in the Repository
      # - default: imdb                # This is a file within the defaults folder in the Repository
      # see the wiki for how to use local files, folders, URLs, or files from git
      # - file: config/Movies.yml
    remove_overlays: false
    overlay_files:
      - default: resolution
```

Edit `Movies.yml` to reflect the actions you want Kometa to perform on *your* libraries.

TV Shows and other libraries work the same way as you've seen above. Create a section under `libraries:` in the config.yml, 
refer to default files or create a Collection File, define collections, run the script.

Investigate the rest of the wiki to learn about everything Kometa can do for you.

### Runtime and Environment Flags

The command in this walkthrough will run all collections and libraries immediately. If you want to modify that behavior to run just one or some collections, 
or just one library, or just overlays or the like, review the [Run Commands & Environment Variables](../../environmental.md).

### Creating Collections, Overlays, Playlists, etc.

These things are all generally defined in collection files that are referred to in the config file. 
The starting point for creating these files is [here](../../../files/collections.md).

<!--all-->

<!--local-->
When you are done, deactivate the virtual environment:

[type this into your terminal]

```shell
deactivate
```

<!--local-->

<!--all-->
## Other Topics

### Scheduling

The commands you've been using in this walkthrough run Kometa immediately then quit.

Kometa also features multiple layers of scheduling, which you can leverage to control when various activities take place.

 - You can run Kometa in the background, telling it to wake up and process your libraries at fixed times during the day. The default behavior in this regard is to wake up at 5AM and process the config. If you leave the `-r` off the commands you have been using in this walkthrough, that's what will happen.

   You can control when Kometa wakes up with the [time-to-run](./../../../environmental#all-available-runtime-flagsenvironment-variables) env-var/runtime flag.

 - You can skip using that internal schedule and just do manual runs as you have been doing throughout this walkthrough using standard tools available in your OS.

   Details on setting this up are found [here](../../guides/scheduling.md).

 - In addition, individual items *within* the configuration can be scheduled to take place at certain times *provided Kometa is running at that time*. For example, you can tell Kometa only to apply overlays on Tuesdays or the like. You can then schedule manual runs every day at noon and overlays will only get processed when it runs on Tuesday. This sort of schedule *will not* make Kometa start up if it is not already running. If you don't arrange for Kometa to be run on Tuesday, your overlays would never be processed in this example.

   Details on this level of scheduling are found [here](../../../config/schedule.md)

<!--all-->

<!--local-->
### I want to update to the latest version of the current Kometa branch

=== ":fontawesome-brands-linux: Linux"

    [type this into your terminal]

    ```shell
    cd ~/Kometa
    git pull
    source kometa-venv/bin/activate
    python -m pip install -r requirements.txt
    ```

=== ":fontawesome-brands-apple: macOS"

    [type this into your terminal]

    ```shell
    cd ~/Kometa
    git pull
    source kometa-venv/bin/activate
    python -m pip install -r requirements.txt
    ```

=== ":fontawesome-brands-windows: Windows"

    [type this into your terminal]

    ```
    cd ~\Kometa
    git pull
    .\kometa-venv\Scripts\activate
    python -m pip install -r requirements.txt
    ```

<!--local-->

<!--all-->
{% include-markdown "./branch.md" include-tags='INCLUDE_TAGS' replace='{"BRANCH": "develop", "NAME": "develop"}' %}

{% include-markdown "./branch.md" include-tags='INCLUDE_TAGS' replace='{"BRANCH": "nightly", "NAME": "nightly"}' %}

<!--all-->

<!--local-->
{% include-markdown "./branch.md" include-tags='INCLUDE_TAGS' replace='{"BRANCH": "master", "NAME": "master"}' %}

<!--local-->

<!--docker-unraid-->
{% include-markdown "./branch.md" include-tags='INCLUDE_TAGS' replace='{"BRANCH": "latest", "NAME": "master"}' %}

<!--docker-unraid-->
