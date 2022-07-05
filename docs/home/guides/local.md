# Local Walkthrough

This article will walk you through getting Plex-Meta-Manager [PMM] set up and running.  It will cover:

1. Retrieving the PMM code
2. Installing requirements
3. Setting up the initial config file
4. Setting up a metadata file and creating a couple sample collections.

The specific steps you will be taking:
1. Verify that Python 3.7 or better is installed and install it if not
2. Verify that the Git tools are installed and install them if not
3. Use `git` to retrieve the code
4. Install requirements [extra bits of code required for PMM]
5. Gather two things that the script requires:
   1. TMDB API Key
   2. Plex URL and Token
6. Then, iteratively:
   1. use `python` to run the script
   2. use a text editor to modify a couple of text files until you have a working config file and a single working metadata file.

## Prerequisites.

Nearly anywhere you see

```
something like this
```

That’s a command you’re going to type or paste into your terminal (OSX or Linux) or Powershell (Windows).  In some cases it's displaying *output* from a command you've typed, but the difference should be apparent in context.

IMPORTANT NOTE:
This walkthrough is going to be pretty pedantic.  I’m assuming you’re reading it because you have no idea how to get a Python script going, so I’m proceeding from the assumption that you want to be walked through every little detail.   You’re going to deliberately cause errors and then fix them as you go through it.  This is to help you understand what exactly is going on behind the scenes so that when you see these sorts of problems in the wild you will have some background to understand what’s happening.  If I only give you the happy path, then when you make a typo later on you’ll have no idea where that typo might be or why it’s breaking things.

I am assuming you do not have any of these tools already installed.  When writing this up I started with a brand new Windows 10 install.

This walkthrough involves typing commands into a command window.  On Mac OS X or Linux, you can use your standard terminal window, whether that's the builtin Terminal app or something like iTerm.  On Windows, you should use PowerShell.  There are other options for command windows in Windows, but if you want this to work as written, which I assume is the case since you've read this far, you should use Powershell.

IMPORTANT:
This walkthrough is assuming you are doing the entire process on the same platform; i.e. you're installing PMM and editing its config files on a single Linux, Windows, or OS X machine.  It doesn't account for situations like running PMM on a Linux machine while editing the config files on your Windows box.

### Starting up your terminal.

Since most of this is typing commands into a terminal, you'll need to have a terminal open.

<details>
  <summary>Linux</summary>
  <br />
  If your Linux system is remote to your computer, connect to it via SSH.  That SSH session is the terminal you will be using, so leave it open.

  If you are running this on a desktop Linux machine, start up the Terminal application.  That window will be the terminal you will type commands into, so leave it open.
</details>

<details>
  <summary>OS X</summary>
  <br />
  Open the Terminal app; this window will be the place you type commands, so leave it open.  THe Terminal app is in Applications -> Utilities.

  You can also use iTerm or some other terminal app if you wish.  If you don't know what that is, use Terminal.
</details>

<details>
  <summary>Windows</summary>
  <br />
  Use the Start menu to open PowerShell.  This will be the window into which you type commands, so leave it open.
</details>


### Installing Python.

In order to run a Python script. the first thing you'll need is a Python interpreter.  THis is typically already present on Linux and Mac, but will probably have to be installed on Windows.

First let's check if it's installed already [type this into your terminal]:

```
python3 --version
```

If this doesn't return `3.7.0` or higher, you'll need to get Python 3 installed.

<details>
  <summary>Linux</summary>
  <br />
  Describing a python install for any arbitrary linux is out of scope here, but if you're using Ubuntu, [this](https://techviewleo.com/how-to-install-python-on-ubuntu-linux/) might be useful.
</details>

<details>
  <summary>OS X</summary>
  <br />
  Follow the instructions here: [Installing Python 3 on Mac OS X](https://docs.python-guide.org/starting/install3/osx/)
</details>

<details>
  <summary>Windows</summary>
  <br />
  Go to http://www.python.org/download and download the latest version of Python for Windows in 32 or 64-bit as appropriate for your system [probably 64-bit].  As this is written, that's 3.10.4.

  Once downloaded, run the installer.  Tick “Add to path” checkbox at the bottom and click “Install Now”.

  For Windows 10, you will need to enable scripts in PowerShell.  Follow the instructions [here](https://windowsloop.com/enable-powershell-scripts-execution-windows-10) to do so.  If you skip this step you're going to hit a hard stop in a little bit.

</details>

---

### Installing git

To copy the Plex-Meta-Manager code to your machine, we'll be using git.  This may be installed on Mac or Linux, and probably isn't in Windows.

First let's check if it's installed already [type this into your terminal]:

```
git --version
```

If this doesn't return a version number, you'll need to get git installed.

<details>
  <summary>Linux</summary>
  <br />

  The git install is discussed here: [Download for Linux and Unix](https://git-scm.com/download/linux)

</details>
<details>
  <summary>OS X</summary>
  <br />

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

Now we're going to use `git` to make a copy of the code on your local computer.

Clone the repo into your home directory and go into that directory [type this into your terminal]:

```
cd ~
git clone https://github.com/meisnate12/Plex-Meta-Manager
cd Plex-Meta-Manager
```

**NOTE: The rest of this walkthrough assumes you are staying in this directory in this terminal/Powershell window.**

<details>
  <summary>What did that do?</summary>
  <br />

  ```
  cd ~
  ```

  This changes to your home directory, which will be something like `/home/yourname` or `/Users/yourname` or `C:\Users\YourName` depending on the platform.

  ```
  git clone https://github.com/meisnate12/Plex-Meta-Manager
  ```

  This uses `git` to make a copy of (`clone`) the PMM code from where it is stored on `github`.

  ```
  cd Plex-Meta-Manager
  ```

  This moves into the directory that was created by the `clone` command.

</details>

Later on you can move it elsewhere if you want, but for now put it there.  This will ensure that everything to follow works just like it says here.  Presumably you’re reading this because the other docs are unclear to you.  Don’t make unilateral changes to my assumptions while doing this.

<details>
  <summary>Why use git instead of downloading the release ZIP?</summary>
  <br />

  Retrieving the code with `git` makes updating simpler.  When you want to update to the newest version, you can go into this directory and type:

  ```
  git pull
  ```

  No need to download a new ZIP, uncompress it, etc.

  Also, if you are asked to [or want to] switch to the latest develop or nightly code, you can do so with:

  ```
  git checkout develop
  ```

  ```
  git checkout nightly
  ```

</details>

---

### Setting up a virtual environment

This walkthrough is going to use a "virtual environment", since that provides a simple way to keep the requirements for a given thing self-contained; think of it as a "sandbox" for this script.  It also provides a clean way to recover from mistakes, and keeps the host system clean.

<details>
  <summary>OS X/Linux</summary>
  <br />
  [type this into your terminal]

  ```
  python3 -m venv pmm-venv
  ```

  If you see an error like:

  ```
  Error: Command '['/home/mroche/Plex-Meta-Manager/pmm-venv/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1.
  ```
  You probably need to make sure the Python 3.9-specific virtualenv support library is installed.

  On Linux [which is the one platform where this was seen at this point]:
  [type this into your terminal]

  ```
  sudo apt-get install python3.9-venv
  ```

</details>

<details>
  <summary>Windows</summary>
  <br />

  [type this into your terminal]

  ```
  python -m venv pmm-venv
  ```

  If you see:

  ```
  Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.
  ```

  You apparently didn't check the “Add to path” checkbox above under [installing Python](#installing-python).  "Repair" your Python install and check "add python to environment variables".
</details>

<details>
  <summary>What did that do?</summary>
  <br />

  ```
  python3 -m venv pmm-venv
  ```

  This tells Python3 to use the `venv` module to create a virtual environment called `pmm-venv`.  The only visible effect will be the creation of a `pmm-venv` directory.

</details>

That command will not produce any output if it works; it will display an error if a problem occurs.  If everything is fine, you will be looking at something like this:

```
> python -m venv pmm-venv
>
```

If you aren't looking at an error, you're ready to move on.

---

That will create the virtual environment, and then you need to activate it:
<details>
  <summary>OS X/Linux</summary>
  <br />
  [type this into your terminal]

  ```
  source pmm-venv/bin/activate
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />
  [type this into your terminal]

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

  You will need to take care of that before moving on.  Follow the instructions [here](https://windowsloop.com/enable-powershell-scripts-execution-windows-10).

</details>

That command will not produce any output if it works; it will display an error if a problem occurs.

You may see a change in your prompt, something like this:

```
➜  Plex-Meta-Manager git:(master) ✗ source pmm-venv/bin/activate
(pmm-venv) ➜  Plex-Meta-Manager git:(master) ✗
```

Note that the prompt now shows the name of the virtual environment.  You may not see this; it's dependent on *your* terminal configuration, not anything to do with Python or PMM.

<details>
  <summary>What did that do?</summary>
  <br />

  This tells Python to make the virtual environment "active", which means to use the copy of python that is available there, install all support libraries there, etc.  This keeps the PMM code and its runtime environment totally separate from your host machine's environment.

</details>

---

An advantage of doing this in a virutal environment is that in the event something goes wrong with this part of the setup, you can delete that pmm-venv directory and do the setup again.

**IMPORTANT: In the future, when you want to run the script, you will need to do this "activation" step every time.  Not the venv creation, just the activation**:

<details>
  <summary>OS X/Linux</summary>
  <br />
  [type this into your terminal]

  ```
  source pmm-venv/bin/activate
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />
  [type this into your terminal]

  ```
  .\pmm-venv\Scripts\activate
  ```
</details>


### Installing requirements

Plex-Meta-Manager, like every other Python script, depends on support libraries that manage things like connections to Plex, or getting things from the internet, or writing files and so on.

These support libraries are called “requirements”, and they are defined in that file called `requirements.txt`.  To install them, type the following command [type this into your terminal]:

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

<details>
  <summary>What did that do?</summary>
  <br />

  This told Python to use the `pip` module to install some libraries that PMM needs.

</details>

Let’s make sure it’s working so far.  [type this into your terminal]:

```
python plex_meta_manager.py -r
```

This is going to fail with an error, which you will then fix.

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
  [type this into your terminal]

  ```
  cp config/config.yml.template config/config.yml
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />
  [type this into your terminal]

  ```
  copy .\config\config.yml.template .\config\config.yml
  ```
</details>

---

Now open the copy in an editor:

<details>
  <summary>OS X/Linux</summary>
  <br />
  [type this into your terminal]

  ```
  nano config/config.yml
  ```

  I’m using `nano` here simply because it’s built into OSX.  On Linux you may need to install `nano`, or you can use any other text editor you wish, provided it saves files as PLAIN TEXT.
</details>

<details>
  <summary>Windows</summary>
  <br />
  [type this into your terminal]

  ```
  notepad .\config\config.yml
  ```
  I’m using `notepad` here simply because it’s built into Windows.  You can use any other text editor you wish, provided it saves files as PLAIN TEXT.

</details>

From here on in, when I say "open the config file", I mean this `nano` or `notepad` command.  **Don't copy the template again**.

---

Scroll down a bit and update the three things you just collected; Plex URL, Plex Token, and TMDb API Key.

```yaml
plex:                                           # Can be individually specified per library as well
  url: http://bing.bang.boing                <<< ENTER YOUR PLEX URL HERE
  token: XXXXXXXXXXXXXXXXXXXX                <<< ENTER YOUR PLEX TOKEN HERE
  timeout: 60
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

libraries:                                      # This is called out once within the config.yml file
  Movies:                                       # Each library must match the Plex library name
    metadata_path:
      - file: config/Movies.yml                 # This is a local file on the system
      - folder: config/Movies/                  # This is a local directory on the system
      - git: meisnate12/MovieCharts             # This is a file within the GitHub Repository
  TV Shows:
    metadata_path:
      - file: config/TVShows.yml
      - folder: config/TV Shows/
      - git: meisnate12/ShowCharts              # This points to the https://github.com/meisnate12/Plex-Meta-Manager-Configs Repository
  Anime:
    metadata_path:
      - file: config/Anime.yml
  Music:
    metadata_path:
      - file: config/Music.yml
```

You will ultimately need an entry here for each of the libraries on which you want PMM to act.  Those top-level elements [Movies, TV Shows, Anime, Music] are names of libraries on your Plex server.

For now, delete the “TV Shows”, “Anime”, and "Music" sections and change the name of the “Movies” section to “Movies-NOSUCHLIBRARY":

```yaml
libraries:
  Movies-NOSUCHLIBRARY:                         ## <<< CHANGE THIS LINE
    metadata_path:
      - file: config/Movies.yml
      - git: meisnate12/MovieCharts
```

This is intended to cause an error for illustration that you will then fix.

#### Testing the config file

Save the file [in nano that would be cntl-x, y, return], then run the script again:

[type this into your terminal]

```shell
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
| Connecting to Movies-NOSUCHLIBRARY Library...
| Plex Error: Plex Library Movies-NOSUCHLIBRARY not found
| Movies-NOSUCHLIBRARY Library Connection Failed
...
```

You can see there that PMM found its config file, was able to connect to TMDb, was able to connect to Plex, and then failed trying to read the “Movies-NOSUCHLIBRARY library, which of course doesn’t exist.

Open the config file again and change "Movies-NOSUCHLIBRARY" to reflect *your own* Plex.  Then delete any lines that start with “git”.  Those are all sets of collections, and we just want to create a few as examples.

My Movies library is called “Main Movies", so mine looks like this:

```yaml
libraries:
  Main Movies:                           ## <<< CHANGE THIS LINE
    metadata_path:
      - file: config/Movies.yml
```

Save the file and run the script again:

[type this into your terminal]

```
python plex_meta_manager.py -r
```

Now you’ll see some more activity in the Plex connection section:

```shell
$ python plex_meta_manager.py -r
...
| Connecting to Plex Libraries...
...
| Connecting to Main Movies Library...
...
| Loading Metadata File: config/Movies.yml
|
| YAML Error: File Error: File does not exist config/Movies.yml
...
| Metadata File Error: No valid metadata files found
|
| Main Movies Library Connection Failed
...
```

PMM may start cataloging your movies at this point; you cna hit control-C to stop that if it's happening.

We can see there that it connected to the Plex Library but failed to find that `Movies.yml` metadata file.

So far so good.

### Setting up a metadata file and creating a few sample collections.

Now we have to set up that metadata file that PMM just complained about.

This metadata file contains definitions of the actions you want PMM to take; these can be things like creating collections or playlists, adding overlays, changing things like posters, etc.  You can find lots of examples [here](https://github.com/meisnate12/Plex-Meta-Manager-Configs) and throughout the wiki.

For now we’re going to create a few collections so you can watch the process work, then you’re on your own to create whatever others you want.

First, open the metadata file [this will create the file if it doesn't already exist]:

<details>
  <summary>OS X/Linux</summary>
  <br />
  [type this into your terminal]

  ```
  nano "config/Movies.yml"
  ```

</details>

<details>
  <summary>Windows</summary>
  <br />
  [type this into your terminal]

  ```
  notepad "config\Movies.yml"
  ```

</details>

In this file, add the following, exactly as it is shown here:

```yaml
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

The first one is based on a template to illustrate that concept.  If you wanted to create a collection for another actor you just have to copy and edit those two lines [the ID comes from TMDb].  All the other config details come from the template.

Save the file and run the script again.

[type this into your terminal]

```
python plex_meta_manager.py -r
```

This time you should see that the metadata file gets loaded:

```
| Loading Metadata File: config/Movies.yml
| Metadata File Loaded Successfully
```

And this time it will catalog all your movies.  This could take a while depending on how many movies are in that library.  Don't cancel it this time.

Once this cataloging is complete it will move on to build those three collections.

As it builds the collections, you should see a fair amount of logging showing which movies are being added to each collection and which ones aren’t found.  Once it completes, go to Plex, go to your Movies library, and click “Collections” at the top.

![Finished Collections](finished.png)

When you click into each, you’ll see the movies that PMM added to each collection.

Each time you run the script, new movies that match the collection definition will be added.  For example, if you don’t have “The Razors’ Edge” now, when you download it and run PMM again it will be added to the Bill Murray collection.

If you download any of the missing 22 movies on the Vulture list, running PMM would add them to that collection.  And so on.

What comes next:

Delete these three collections if you want, from both Plex and the metadata file [`config/Movies.yml`].

Edit `Movies.yml` to reflect the actions you want PMM to perform on *your* libraries.

TV Shows and other libraries work the same way as you've seen above.  Create a section under `Libraries:` in the config.yml, create a metadata file, define collections, run the script.

Investigate the rest of the wiki to learn about everything Plex-Meta-Manager can do for you.

When you are done, deactivate the virtual environment:

[type this into your terminal]

```
deactivate
```

## Other Topics

### I want to update to the latest version of PMM

<details>
  <summary>OS X/Linux</summary>
  <br />

  [type this into your terminal]

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

  [type this into your terminal]

  ```
  cd C:\Users\mroche\Plex-Meta-Manager
  git pull
  .\pmm-venv\Scripts\activate
  python -m pip install -r requirements.txt
  ```
</details>

### I want to use the develop branch

<details>
  <summary>OS X/Linux</summary>
  <br />

  [type this into your terminal]

  ```
  cd /Users/mroche/Plex-Meta-Manager
  git checkout develop
  git pull
  source pmm-venv/bin/activate
  python -m pip install -r requirements.txt
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  [type this into your terminal]

  ```
  cd C:\Users\mroche\Plex-Meta-Manager
  git checkout develop
  git pull
  .\pmm-venv\Scripts\activate
  python -m pip install -r requirements.txt
  ```
</details>

### I want to use the nightly branch

<details>
  <summary>OS X/Linux</summary>
  <br />

  [type this into your terminal]

  ```
  cd /Users/mroche/Plex-Meta-Manager
  git checkout nightly
  git pull
  source pmm-venv/bin/activate
  python -m pip install -r requirements.txt
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  [type this into your terminal]

  ```
  cd C:\Users\mroche\Plex-Meta-Manager
  git checkout nightly
  git pull
  .\pmm-venv\Scripts\activate
  python -m pip install -r requirements.txt
  ```
</details>

### I want to use the master branch

<details>
  <summary>OS X/Linux</summary>
  <br />

  [type this into your terminal]

  ```
  cd /Users/mroche/Plex-Meta-Manager
  git checkout master
  git pull
  source pmm-venv/bin/activate
  python -m pip install -r requirements.txt
  ```
</details>

<details>
  <summary>Windows</summary>
  <br />

  [type this into your terminal]

  ```
  cd C:\Users\mroche\Plex-Meta-Manager
  git checkout master
  git pull
  .\pmm-venv\Scripts\activate
  python -m pip install -r requirements.txt
  ```
</details>

The reinstall of requirements every time is probably overkill, but it's harmless and ensures that you always get any new versions or new requirements.

