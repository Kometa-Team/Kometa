# Local Walkthrough

This article will walk you through getting Plex-Meta-Manager [PMM] set up and running.  It will cover:

1. Retrieving the PMM code
2. Installing requirements
3. Setting up the initial config file
4. Setting up a metadata file and creating a couple sample collections.

## Prerequisites.

Nearly anywhere you see

```
something like this
```

That’s a command you’re going to type or paste into your terminal (OSX or Linux) or Powershell (Windows).  In some cases it's displaying *output* from a command you've typed, but the difference should be apparent in context.

IMPORTANT NOTE:
This walkthrough is going to be pretty pedantic.  I’m assuming you’re reading it because you have no idea how to get a Python script going, so I’m proceeding from the assumption that you want to be walked through every little detail.   You’re going to deliberately cause errors and then fix them as you go through it.  This is to help you understand what exactly is going on behind the scenes so that when you see these sorts of problems in the wild you will have some background to understand what’s happening.  If I only give you the happy path, then when you make a typo later on you’ll have no idea where that typo might be or why it’s breaking things.

I am assuming you do not have any of these tools already installed.  When writing this up I started with a brand new Windows 10 install.

<h4>If you are using Windows, do everything here in Powershell.  You don't need to run it as an Administrator.  Git, notably, installs its own command line interface.  Don't use that.  Do everything here in Powershell.</h4>

<h4>On OSX or Linux, you can use any terminal or shell.</h4>

### Installing Python.

<details>
  <summary>Linux</summary>
  <br />

  First let's check if it's installed already:

  ```
  python3 --version
  ```

  If this doesn't return `3.7.[something]` or higher, you'll need to get Python 3 installed. Describing this for any arbitrary linux is out of scope here, but if you're using Ubuntu, [this](https://techviewleo.com/how-to-install-python-on-ubuntu-linux/) might be useful.
</details>

<details>
  <summary>OS X</summary>
  <br />
  First let's check if it's installed already:

  ```
  python3 --version
  ```

  If this doesn't return `3.7.[something]` or higher, you'll need to get Python 3 installed. 

  Follow the instructions here: [Installing Python 3 on Mac OS X](https://docs.python-guide.org/starting/install3/osx/)
</details>

<details>
  <summary>Windows</summary>
  <br />

  Go to http://www.python.org/download and download the latest version of Python for Windows in 32 or 64-bit as appropriate for your system.  As this is written, that's 3.10.4.

  Once downloaded, run the installer.  Tick “Add to path” checkbox at the bottom and click “Install Now”.

  For Windows 10, you will need to enable scripts in PowerShell.  Follow the instructions [here](https://windowsloop.com/enable-powershell-scripts-execution-windows-10) to do so.  If you skip this step you're going to hit a hard stop in a couple steps.

</details>

---

### Installing git

<details>
  <summary>Linux</summary>
  <br />
  First let's check if it's installed already:

  ```
  git --version
  ```

  If this doesn't return a version number, you'll need to get git installed.

  The git install is discussed here: [Download for Linux and Unix](https://git-scm.com/download/linux)

</details>
<details>
  <summary>OS X</summary>
  <br />

  First let's check if it's installed already:

  ```
  git --version
  ```

  If this doesn't return a version number, you'll need to get git installed.

  The git install is discussed here: [Git - Downloading Package](https://git-scm.com/download/mac)

</details>

<details>
  <summary>Windows</summary>
  <br />

  Download the installer from [here](https://git-scm.com/download/windows)

  Run the install; you can probably just accept the defaults and click through except for the step that asks you to choose an editor; you probably want to choose something other than the default there:

  ![Git Install](git-install.png)

  This install comes with its own command line interface.  **Do not use this interface in this walkthrough**.  Continue to do everything here in Powershell.

</details>

---

### Retrieving the Plex-Meta-Manager code

Clone the repo into your home directory:

```
cd ~
git clone https://github.com/meisnate12/Plex-Meta-Manager
```

Later on you can move it elsewhere if you want, but for now put it there.  This will ensure that everything to follow works just like it says here.  Presumably you’re reading this because the other docs are unclear to you.  Don’t make unilateral changes to my assumptions while doing this.

<details>
  <summary>Why use git instead of downloading the release ZIP?</summary>
  <br />

  Retrieving the code with `git` makes updating simpler.  When you want to update to the newest version, you can go into this directory and type:

  ```
  git pull
  ```

  No need to download a new ZIP, uncompress it, etc.

  Also, if you are asked to [or want to] switch to the latest develop code, you can do so with:

  ```
  git checkout develop
  ```

</details>

---

Now move into that directory:

```
cd ~/Plex-Meta-Manager
```

**NOTE: The rest of this walkthrough assumes you are staying in this directory.**

### Setting up a virtual environment

This walkthrough is going to use a "virtual environment", since that provides a simple way to keep the requirements for a given thing self-contained; think of it as a "sandbox" for this script.  It also provides a clean way to recover from mistakes, and keeps the host system clean.

<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  python3 -m venv pmm-venv
  ```

  If you see an error like:
  ```
  Error: Command '['/home/mroche/Plex-Meta-Manager/pmm-venv/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1.
  ```
  You probably need to make sure the Python 3.9-specific virtualenv support library is installed.

  On Linux [which is the one platform where this was seen at this point]:
  ```
  sudo apt-get install python3.9-venv
  ```

</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  python -m venv pmm-venv
  ```

  If you see:
  ```
  Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.
  ```
  You apparently didn't check the “Add to path” checkbox above under [installing Python](#installing-python).  "Repair" your Python install and check "add python to environment variables".
</details>

---

That will create the virtual environment, and then you need to activate it:
<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  source pmm-venv/bin/activate
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  .\pmm-venv\Scripts\activate
  ```
  If you see something like this:
  ```powershell
  .\pmm-venv\Scripts\activate : File C:\Users\mroche\Plex-Meta-Manager\pmm-venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink LinkID=135170.
  At line:1 char:1
  + .\pmm-venv\Scripts\activate
  + ~~~~~~~~~~~~~~~~~~~~~~~~~~~
      + CategoryInfo          : SecurityError: (:) [], PSSecurityException
      + FullyQualifiedErrorId : UnauthorizedAccess
  ```
  You apparently skipped the "enable scripts in Powershell" step above under [installing Python](#installing-python) for Windows.

  You will need to take care of that before moving on.

</details>

---

An advantage of doing this in a venv is that in the event something goes wrong, you can delete that pmm-venv directory and do the setup again.

**IMPORTANT: In the future, when you want to run the script, you will need to do this "activation" step every time.  Not the venv creation, just the activation**:

<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  source pmm-venv/bin/activate
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  .\pmm-venv\Scripts\activate
  ```
</details>


### Installing requirements

Plex-Meta-Manager, like every other Python script, depends on support libraries that manage things like connections to Plex, or getting things from the internet, or writing files and so on.

These support libraries are called “requirements”, and they are defined in that file called `requirements.txt`.  To install them, type the following command:

```
python -m pip install -r requirements.txt
```

You should see something like this [I’ve removed a few lines for space, and the specific versions may have changed since this was captured]:

```
Collecting PlexAPI==4.7.0
  Downloading PlexAPI-4.7.0-py3-none-any.whl (133 kB)
     |████████████████████████████████| 133 kB 821 kB/s
Collecting tmdbv3api==1.7.6
  Downloading tmdbv3api-1.7.6-py2.py3-none-any.whl (17 kB)
...
Installing collected packages: urllib3, idna, charset-normalizer, certifi, six, ruamel.yaml.clib, requests, tmdbv3api, schedule, ruamel.yaml, retrying, PlexAPI, pillow, pathvalidate, lxml, arrapi
    Running setup.py install for retrying ... done
    Running setup.py install for arrapi ... done
Successfully installed PlexAPI-4.7.0 arrapi-1.1.3 certifi-2021.10.8 charset-normalizer-2.0.7 idna-3.3 lxml-4.6.3 pathvalidate-2.4.1 pillow-8.3.2 requests-2.26.0 retrying-1.3.3 ruamel.yaml-0.17.10 ruamel.yaml.clib-0.2.6 schedule-1.1.0 six-1.16.0 tmdbv3api-1.7.6 urllib3-1.26.7
WARNING: You are using pip version 21.1.3; however, version 21.3 is available.
You should consider upgrading via the '/Users/mroche/Plex-Meta-Manager/pmm-venv/bin/python -m pip install --upgrade pip' command.
```

Don't worry about the WARNING about `pip version thus-and-such` if it comes up.

Let’s make sure it’s working so far.  At the command prompt, type:

```
python plex_meta_manager.py -r
```

[This is going to fail with an error, don’t panic]

You should see something like this:

```
Config Error: config not found at /Users/mroche/Plex-Meta-Manager/config
```

That error means you don’t have a config file, but we at least know that the requirements are in place and the script can run.

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

Click to generate a new API key under "Request an API Key".  If there is already one there, copy it and go to the [next step](#getting-a-plex-url-and-token).

There will be a form to fill out; the answers are arbitrary.  The URL can be your personal website, or probably even google.com or the like.

Once you’ve done that there should be an API Key available on this screen.

Copy that value, you’ll need it for the config file.

#### Getting a Plex URL and Token

The Plex URL is whatever URL you’d use **from this machine** to connect directly to your Plex server [i.e. NOT app.plex.tv].

As with the TMDb API Key, if you already have a Plex Token, you can use that one.

This article describes how to get a token: [Finding an authentication token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)


#### Editing the config template

First, make a copy of the template.  This is going to create a copy of the base template that you can then edit.  You only need to do this once.

<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  cp config/config.yml.template config/config.yml
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  copy .\config\config.yml.template .\config\config.yml
  ```
</details>

---

Now open the copy in an editor:

<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  nano config/config.yml
  ```

  I’m using `nano` here simply because it’s built into OSX.  On Linux you may need to install `nano`, or you can use any other text editor you wish provided it saves files as PLAIN TEXT.
</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  notepad .\config\config.yml
  ```
  I’m using `notepad` here simply because it’s built into Windows.  You can use any other text editor provided it saves files as PLAIN TEXT.

</details>

From here on in, when I say "open the config file", I mean this `nano` or `notepad` command.  **Don't copy the template again**.

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


You will ultimately need an entry here for each of the libraries on which you want PMM to act.  Those top-level elements [Movies, TV Shows, Anime] are names of libraries on your Plex server.

For now, delete the “TV Shows” and “Anime” sections and change the name of the “Movies” section to something that is NOT included in your Plex.  I’m using “Movies-HIDDEN":

```
libraries:                                      # Library mappings must have a colon (:) placed after them
  Movies-HIDDEN:
    metadata_path:
      - file: config/Movies.yml                 # You have to create this file the other are online
      - git: meisnate12/MovieCharts
```


This is intended to cause an error, so bear with me.

#### Testing the config file

Save the file [in nano that would be cntl-x, y, return], then run the script again:

```
python plex_meta_manager.py -r
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
| Connecting to Movies-HIDDEN Library...
| Plex Error: Plex Library Movies-HIDDEN not found
| Movies-HIDDEN Library Connection Failed
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

Save the file and run the script again:

```
python plex_meta_manager.py -r
```

Now you’ll see some more activity in the Plex connection section:

```
$ python plex_meta_manager.py -r
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

PMM may start cataloging your movies at this point; you cna hit control-C to stop that if it's happening.

We can see there that it connected to the Plex Library but failed to find that `Main Movies.yml` metadata file.

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
  nano "config\Main Movies.yml"
  ```

</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  notepad "config\Main Movies.yml"
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

Save the file and run the script again.

```
python plex_meta_manager.py -r
```

This time you should see that the metadata file gets loaded:

```
| Loading Metadata File: config/Movies.yml
| Metadata File Loaded Successfully
```

And this time it will catalog all your movies.  This could take a while depending on how many movies are in that library.

Once this cataloging is complete it will move on to build those three collections.

As it builds the collections, you should see a fair amount of logging about which movies are being added and which ones aren’t found.  Once it completes, go to Plex, go to your Movies library, and click “Collections” at the top.

![Finished Collections](finished.png)

When you click into each, you’ll see the movies that PMM added to each collection.

Each time you run the script, new movies that match the collection definition will be added.  For example, if you don’t have “The Razors’ Edge” now, when you download it and run PMM again it will be added to the Bill Murray collection.

If you download any of the missing 22 movies on the Vulture list, running PMM would add them to that collection.  And so on.

What comes next:

Delete these three collections if you want, from both Plex and the metadata file. If you add that “git” line you removed back into the config file:

```
      - git: meisnate12/MovieCharts
```

then run PMM again, the script will add a whole bunch of new collections [which are defined in that file] you may be interested in.

That line is a link into the github repo of examples I referred to above, so you can review what it contains there.  You can also add others from that repo using this same pattern.

If you prefer to create your own, do that in the metadata file.

TV Shows and other libraries work the same way.  Create a section under `Libraries:` in the config.yml, create a metadata file, define collections, run the script.

Investigate the rest of the wiki to learn about everything else Plex-Meta-Manager can do for you.

When you are done, deactivate the virtual environment:

```
deactivate
```

## Advanced Topics

### I want to use this in a context where I can't be manually activating/deactivating the virtual environment [scheduled. etc]

All you need do is point to the python executable inside the virtual env.  In our example, that means that if your scheduled job normally would be:
```
cd /Users/mroche/Plex-Meta-Manager
python plex_meta_manager.py -r
```
You would instead use:
```
cd /Users/mroche/Plex-Meta-Manager
pmm-venv/bin/python plex_meta_manager.py -r
```

On Windows that path is:
```
cd C:\Users\mroche\Plex-Meta-Manager
pmm-venv\Scripts\python.exe plex_meta_manager.py -r
```

### I want to update to the latest version of the code

<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  cd /Users/mroche/Plex-Meta-Manager
  git pull
  source pmm-venv/bin/activate
  python -m pip install -r requirements.txt
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  cd C:\Users\mroche\Plex-Meta-Manager
  git pull
  .\pmm-venv\Scripts\activate
  python -m pip install -r requirements.txt
  ```
</details>

You're set to go.

### I want to use the develop branch

<details>
  <summary>OS X/Linux</summary>
  <br />

  ```
  cd /Users/mroche/Plex-Meta-Manager
  git checkout develop
  source pmm-venv/bin/activate
  python -m pip install -r requirements.txt
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  ```
  cd C:\Users\mroche\Plex-Meta-Manager
  git checkout develop
  .\pmm-venv\Scripts\activate
  python -m pip install -r requirements.txt
  ```
</details>

You can switch back to the `master` branch by changing `develop` to `master`.

The reinstall of requirements every time is probably overkill, but it's harmless and ensures that you always get any new versions or new requirements.

