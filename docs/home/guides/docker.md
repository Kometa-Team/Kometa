# Docker Walkthrough

This article will walk you through getting Plex-Meta-Manager [PMM] set up and running via Docker.  It will cover:

1. Installing Docker
2. Retrieving the image
3. Setting up the initial config file
4. Setting up a metadata file and creating a couple sample collections
5. Creating a docker container that will keep running in the background

## Prerequisites.

Anywhere you see

```
something like this
```

That’s a command you’re going to type or paste into your terminal (OSX or Linux) or Powershell (Windows).

IMPORTANT NOTE:
This walkthrough is going to be pretty pedantic.  I’m assuming you’re reading it because you have no idea how to get a Docker container going, so I’m proceeding from the assumption that you want to be walked through every little detail.   You’re going to deliberately cause errors and then fix them as you go through it.  This is to help you understand what exactly is going on behind the scenes so that when you see these sorts of problems in the wild you will have some background to understand what’s happening.  If I only give you the happy path walkthrough, then when you make a typo later on you’ll have no idea where that typo might be or why it’s breaking things.

I am assuming you do not have any of these tools already installed.  When writing this up I started with a brand new Windows 10 install.

I'm also assuming you are doing this on a computer, not through a NAS interface or the like.  You can do all this through something like the Synology NAS UI or Portainer or the like, but those aren't documented here.  This uses the docker command line because it works the same on all platforms.

You may want to take an hour to get familiar with Docker fundamentals with the [official tutorial](https://www.docker.com/101-tutorial/).

### Installing Docker.

The Docker install is discussed here: [Installing Docker](https://docs.docker.com/engine/install/)

Once you have Docker installed, test it at the command line with:

```
docker run --rm hello-world
```

You should see something that starts with:

```
Hello from Docker!
This message shows that your installation appears to be working correctly.

...
```

---

The great thing about Docker is that all the setup you'd have to do to run PMM is already done inside docker image.


That means we can just jump right into running it.  At the command prompt, type:

```
docker run --rm meisnate12/plex-meta-manager --run

```

[This is going to fail with an error, don’t panic]

You should see something like this:

```
Unable to find image 'meisnate12/plex-meta-manager:latest' locally
latest: Pulling from meisnate12/plex-meta-manager
7d63c13d9b9b: Already exists
6ad2a11ca37b: Already exists
8076cdef4689: Pull complete
0ba90f5a7dd0: Pull complete
27c191df269f: Pull complete
c75e4c0924fa: Pull complete
ed6716577767: Pull complete
0547721ab7a3: Pull complete
ea4d35bce959: Pull complete
Digest: sha256:472be179a75259e07e68a3da365851b58c2f98383e02ac815804299da6f99824
Status: Downloaded newer image for meisnate12/plex-meta-manager:latest
Config Error: config not found at //config
```

That error means you don’t have a config file, but we know that most everything is in place to run the image.

### Setting up a volume map

PMM, inside that Docker container, can only see other things *inside the container*.  We want to add our own files for config and metadata, so we need to set something up that lets PMM see files we create *outside* the container.  This is called a "volume map".

Go to your home directory and create a new directory:

```
cd ~
mkdir plex-meta-manager
```

cd into that directory:

```
cd ~/plex-meta-manager
```

get the full path:

```
pwd
```

This will display a full path:
<details>
  <summary>OS X</summary>
  <br />

  ```
  /Users/YOURUSERNAME/plex-meta-manager
  ```
</details>

<details>
  <summary>Linux</summary>
  <br />

  ```
  /home/YOURUSERNAME/plex-meta-manager
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  C:\Users\YOURUSERNAME\plex-meta-manager
  ```
</details>

You'll need to add this to the docker command every time you run it:

```
docker run --rm -it -v "PMM_PATH_GOES_HERE:/config:rw" meisnate12/plex-meta-manager
```
as an example:

```
docker run --rm -it -v "/Users/mroche/plex-meta-manager:/config:rw" meisnate12/plex-meta-manager
```


If you run that command now it will display a similar error to before, but without all the image loading:

```
 $ docker run --rm -it -v "/Users/mroche/plex-meta-manager:/config:rw" meisnate12/plex-meta-manager --run
Config Error: config not found at //config
```

Note that I show the example path there.

### Setting up the initial config file

Next you’ll set up the config file.  ThIs tells PMM how to connect to Plex and a variety of other services.

Before you do this you’ll need:

1. TMDb API key.  They’re free.
1. Plex URL and Token

There are a bunch of other services you *can* configure in the config file, but these two are the bare minimum.

#### Getting a TMDb API Key

Note that if you already have an API key, you can use that one.  You don’t need another.

Go to https://www.themoviedb.org/.  Log into your account [or create one if you don’t have one already], then go to “Settings” under your account menu.

In the sidebar menu on the left, select “API”.

Click to generate a new API key under "Request an API Key".  If there is already one there, copy it and go to the next step.

There will be a form to fill out; the answers are arbitrary.  The URL can be your personal website, or probably even google.com or the like.

Once you’ve done that there should be an API Key available on this screen.

Copy that value, you’ll need it for the config file.

#### Getting a Plex URL and Token

The Plex URL is whatever URL you’d use **from this machine** to connect directly to your Plex server [i.e. NOT app.plex.tv].

As with the TMDb API Key, if you already have a Plex Token, you can use that one.

This article will describe how to get a token: [Finding an authentication token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)


#### Editing the config template

First, make a copy of the template, then open the copy in an editor:

<details>
  <summary>OS X/Linux</summary>
  <br />

  Get a copy of the template to edit:
  ```
  curl -fLvo config.yml https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager/master/config/config.yml.template
  ```

  Open it in an editor:
  ```
  nano config.yml
  ```

  I’m using `nano` here simply because it’s built into OSX.  On Linux you may need to install `nano`, or you can use any other text editor you wish provided it saves files as PLAIN TEXT.
</details>

<details>
  <summary>Windows</summary>
  <br />

  Download the file `https://raw.githubusercontent.com/meisnate12/Plex-Meta-Manager/master/config/config.yml.template` using a web browser or whatever means and save it in this directory as `config.yml`

  ```
  notepad config.yml
  ```
  I’m using `notepad` here simply because it’s built into Windows.  You can use any other text editor provided it saves files as PLAIN TEXT.

</details>

From here on in, when I say "open the config file", I mean the `nano` or `notepad` command.  You don't want to download the template again.

---

Scroll down a bit and update the three things you just collected; Plex URL, Plex Token, and TMDb API Key.

```
plex:                                           # Can be individually specified per library as well
  url: http://bing.bang.boing                <<< ENTER YOUR PLEX URL
  token: XXXXXXXXXXXXXXXXXXXX                <<< ENTER YOUR PLEX TOKEN
  timeout: 60
  clean_bundles: false
  empty_trash: false
  optimize: false
tmdb:
  apikey: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX   <<< ENTER YOUR TMDb API
  language: en
```

Now scroll up and look at the top section:

```
libraries:                                      # Library mappings must have a colon (:) placed after them
  Movies:
    metadata_path:
      - file: config/Movies.yml                 # You have to create this file the other is online
      - git: meisnate12/MovieCharts
  TV Shows:
    metadata_path:
      - file: config/TV Shows.yml               # You have to create this file the other is online
      - git: meisnate12/ShowCharts
  Anime:
    metadata_path:
      - file: config/Anime.yml                  # You have to create this file the other is online
      - git: meisnate12/AnimeCharts
```


You need an entry here for each of the libraries on which you want PMM to act.  Those top-level elements [Movies, TV Shows, Anime] are names of libraries on your Plex server.

Delete the “TV Shows” and “Anime” sections and change the name of the “Movies” section to something that is NOT included in your Plex.  I’m using “Movies-HIDDEN":

```
libraries:                                      # Library mappings must have a colon (:) placed after them
  Movies-HIDDEN:
    metadata_path:
      - file: config/Movies.yml                 # You have to create this file the other are online
      - git: meisnate12/MovieCharts
```


This is intended to cause an error, so bear with me.

#### Testing the config file

Save the file:

<details>
  <summary>OS X/Linux</summary>
  <br />

  If you're using `nano`, type control-`x`, then `y`, then the enter key.

</details>

<details>
  <summary>Windows</summary>
  <br />

  If you're using `notepad`, type alt-`s` of choose `Save` from the `File` menu.

</details>

Then run the script again:

```
docker run --rm -it -v "PMM_PATH_GOES_HERE:/config:rw" meisnate12/plex-meta-manager --run
```

I’ve removed some of the lines for space, but have left the important bits:

```
...
|                                            Starting Run|
...
| Locating config...
|
| Using /Users/mroche/Plex-Meta-Manager/config/config.yml as config
...
| Connecting to TMDb...
| TMDb Connection Successful
...
| Connecting to Plex Libraries...
...
| Connecting to Movies-HIDDEN Library...                                                             |
...
| Plex Error: Plex Library Movies-HIDDEN not found                                                   |
| Movies-HIDDEN Library Connection Failed                                                            |
|====================================================================================================|
| Plex Error: No Plex libraries were connected to                                                    |
...
```

You can see there that PMM found its config file, was able to connect to TMDb, was able to connect to Plex, and then failed trying to read the “Movies-HIDDEN” library, which of course doesn’t exist.

Open the config file again and change "Movies-HIDDEN" [or whatever you used in the previous step] to reflect your Plex.  Also fix the name of the config file to match the library.  Then delete any lines that start with “git”.  Those are all sets of collections, and we just want to create a few as examples.

My Movies library is called “Main Movies", so mine looks like this:

```
libraries:                                      # Library mappings must have a colon (:) placed after them
  Main Movies:
    metadata_path:
      - file: config/Main Movies.yml                 # You have to create this file the other are online
```

NOTE: the matching naming of Library and YML is not actually required, I'm doing it here for clarity.

Save the file:

<details>
  <summary>OS X/Linux</summary>
  <br />

  If you're using `nano`, type control-`x`, then `y`, then the enter key.

</details>

<details>
  <summary>Windows</summary>
  <br />

  If you're using `notepad`, type alt-`s` of choose `Save` from the `File` menu.

</details>

Then run the script again:

```
docker run --rm -it -v "PMM_PATH_GOES_HERE:/config:rw" meisnate12/plex-meta-manager --run
```

Now you’ll see some more activity in the Plex connection section:

```
$ docker run --rm -it -v "/Users/mroche/plex-meta-manager:/config:rw" meisnate12/plex-meta-manager --run
...
| Connecting to Plex Libraries...
...
| Connecting to Main Movies Library...
...
| Loading Metadata File: config/Main Movies.yml
|
| YAML Error: File Error: File does not exist config/Main Movies.yml
...
| Metadata File Error: No valid metadata files found
|
| Main Movies Library Connection Failed
...
```

We can see there that it connected to the Plex Library, failed to find a metadata file, and then quit.

So far so good.

### Setting up a metadata file and creating a few sample collections.

Now we have to set up that metadata file that PMM just complained about.

This metadata file contains definitions of the actions you want PMM to take.  You can find lots of examples [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs):

For now we’re going to create a few collections so you can watch the process work, then you’re on your own to create whatever others you want.

First, open the metadata file [this will create the file if it doesn't already exist]:

<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  nano "Main Movies.yml"
  ```

</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  notepad "Main Movies.yml"
  ```

</details>

[of course, that should be the file name you just entered in config.yml, if you changed it from the default]

In this file, add the following, exactly as it is shown here:

```
templates:
  Actor:
    actor: tmdb
    tmdb_person: <<person>>
    tmdb_actor_details: <<person>>
    sort_title: +_<<collection_name>>
    sync_mode: sync
    collection_order: release
    collection_mode: hide
collections:
  Bill Murray:
    template: {name:  Actor, person: 1532}
  Best of the 1980s:
    tmdb_discover:
      primary_release_date.gte: 01/01/1980
      primary_release_date.lte: 12/31/1989
      with_original_language: en
      sort_by: popularity.desc
      limit: 100
    summary: A collection of the Top Content of the 1980s
  Vulture’s 101 Best Movie Endings:
    letterboxd_list: https://letterboxd.com/brianformo/list/vultures-101-best-movie-endings/
```

I chose a letterboxd list for the last one since trakt requires authentication and again, I didn’t want to complicate this walkthrough.

This is going to create three collections.  One contains movies that feature Bill Murray.  One is up to 100 movies that came out in the 1980s sorted by popularity.  The last are movies that appear on a list of good endings according to Vulture.

The first one is based on a template, so if you wanted to create a collection for another actor you just have to copy and edit those two lines [the ID comes from TMDb].  All the other config details come from the template.

```
   Amy Adams:
     template: {name:  Actor, person: 9273}
```

Save the file:

<details>
  <summary>OS X/Linux</summary>
  <br />

  If you're using `nano`, type control-`x`, then `y`, then the enter key.

</details>

<details>
  <summary>Windows</summary>
  <br />

  If you're using `notepad`, type alt-`s` of choose `Save` from the `File` menu.

</details>

Then run the script again:

```
docker run --rm -it -v "PMM_PATH_GOES_HERE:/config:rw" meisnate12/plex-meta-manager --run
```

This time you should see that the metadata file gets loaded:

```
| Loading Metadata File: config/Main Movies.yml
| Metadata File Loaded Successfully
```

And this time it will catalog all your movies.  This could take a while depending on how many movies are in that library.

Once this mapping is complete it will move on to build those three collections.

As it builds the collections, you should see a fair amount of logging about which movies are being added and which ones aren’t found.  Once it completes, go to Plex, go to your Movies library, and click “Collections” at the top.

You should see the three new collections:

![Finished Collections](finished.png)

When you click into each, you’ll see the movies that PMM added to each collection.

Each time you run the script, new movies that match the collection definition will be added.  For example, if you don’t have “The Razors’ Edge” now, when you download it and run PMM again it will be added to the Bill Murray collection.

If you download any of the missing 22 movies on the Vulture list, running PMM would add them to that collection.  And so on.

### What comes next:

Delete these three collections if you want, from both Plex and the metadata file. If you add that “git” line you removed back into the config file:

```
      - git: meisnate12/MovieCharts
```

then run PMM again, the script will add a whole bunch of new collections [which are defined in that file] you may be interested in.

That line is a link into the github repo of examples I referred to above, so you can review what it contains there.  You can also add others from that repo using this same pattern.

If you prefer to create your own, do that in the metadata file.

TV Shows and other libraries work the same way.  Create a `Libraries:` section in the config.yml, create a metadata file, define collections, run the script.

Investigate the rest of the wiki to learn about everything else Plex-Meta-Manager can do for you.

### Running the container in the background:

The docker commands in this article are creating and deleting containers.

However, you probably ultimately want a container that runs all the time, even after reboots, and wakes up to do its thing.

This would be the minimal case:

```
docker run -d \
  --restart=unless-stopped \
  -v PMM_PATH_GOES_HERE:/config:rw \
  meisnate12/plex-meta-manager
```

That will create a container that will run in the background until you explicitly stop it, surviving reboots, and waking up every morning at 3AM to process collections.

There are of course other flags you can add, which are discussed elsewhere in the wiki, but this is the minimal command to create this container.