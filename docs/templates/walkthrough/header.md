<!--all-->
# SYSTEM_NAME Walkthrough

This article will walk you through getting Kometa set up and running RUN_TYPE. It will cover:

<!--all-->

<!--local-->
1. Retrieving the Kometa code
2. Installing requirements

<!--local-->

<!-docker-->
1. Installing Docker

<!-docker-->

<!--unraid-->
1. Installing Kometa unRAID app

<!--unraid-->

<!-docker-unraid-->
2. Retrieving the image

<!-docker-unraid-->

<!--all-->
3. Setting up the initial config file
4. Creating some sample collections using the defaults
5. Setting up a Collection File and creating a sample collection.
6. Adding some default overlays.

The specific steps you will be taking:

<!--all-->

<!--local-->
1. Verify that the version of Python installed is between 3.9 and 3.13.

<!--local-->

<!--all-->
2. Verify that APP_NAME is installed and install it if not
2. Use `RETRIEVE` to retrieve the Kometa Docker image

<!--all-->

<!-docker-unraid-->
3. Create a directory for your config files and learn how to tell Docker to use it

<!-docker-unraid-->

<!--local-->
3. Install requirements [extra bits of code required for Kometa]

<!--local-->

<!--all-->

4. Gather two things that Kometa requires:
    - TMDb API Key
    - Plex URL and Token
5. Then, iteratively:
    - use `RUN_NAME` to run the image
    - use a text editor to modify a couple of text files until you have a working config file and a single working Collection File.

Note that running a Python script is inherently a pretty technical process. If you are unable or unwilling to learn the rudiments of using
<!--all-->

<!--local-->
tools like python and git, you should probably strongly consider running Kometa in [Docker](docker.md).
That will eliminate the Python and git installs from this process and make it as simple as it can be.

<!--local-->

<!-docker-unraid-->
using Docker, this may not be the tool for you.

<!-docker-unraid-->

<!--all-->
If the idea of editing YAML files by hand is daunting, this may not be the tool for you. 
All the configuration of Kometa is done via YAML text files, so if you are unable or unwilling to learn how those work, you should stop here.

Finally, this walkthrough is intended to give you a basic grounding in how to get Kometa running. 
It doesn't cover how to create your own collections, or how to add overlays, or any of the myriad other things Kometa is capable of. 
It provides a simple "Getting Started" guide for those for whom the standard install instructions make no sense; presumably because you've never run FULL_NAME before.

## Prerequisites

???+ tip

    Nearly anywhere you see
    
    ```shell { .no-copy }
    something like this
    ```
    
    That’s a command you’re going to type or paste into your terminal (OSX or Linux) or Powershell (Windows). 
    In some cases it's displaying *output* from a command you've typed, but the difference should be apparent in context.

    Additionally, anywhere you see this icon:
   
    > :fontawesome-solid-circle-plus:
   
    That's a tooltip, you can press them to get more information.

???+ warning "Important"

<!--all-->

<!--unraid-->
    The unRAID app store leverages Docker containers. As such, we are tweaking the existing Docker container walkthrough to make it work on unRAID. 
    This walkthrough is going to be pretty pedantic.

<!--unraid-->

<!--all-->
    This walkthrough is going to be pretty pedantic. I’m assuming you’re reading it because you have no idea how to get a Docker container going, so I’m proceeding from the 
    assumption that you want to be walked through every little detail. You’re going to deliberately cause errors and then fix them as you go through it. 
    This is to help you understand what exactly is going on behind the scenes so that when you see these sorts of problems in the wild you will have some background to understand 
    what’s happening. If I only give you the happy path walkthrough, then when you make a typo later on you’ll have no idea where that typo might be or why it’s breaking things.
   
    I am assuming you do not have any of these tools already installed. When writing this up I started with a brand new Windows 10 install.

<!--all-->
   
<!--local-->
    This walkthrough involves typing commands into a command window. On Mac OS X or Linux, you can use your standard terminal window, 
    whether that's the builtin Terminal app or something like iTerm. On Windows, you should use PowerShell. There are other options for command windows in Windows, 
    but if you want this to work as written, which I assume is the case since you've read this far, you should use Powershell.

<!--local-->

<!-docker-unraid-->
    I'm also assuming you are doing this on a computer, not through a NAS interface or the like. You can do all this through something like the Synology NAS UI or Portainer or 
    the like, but those aren't documented here. This uses the docker command line because it works the same on all platforms.
   
    You may want to take an hour to get familiar with Docker fundamentals with the [official tutorial](https://www.docker.com/101-tutorial/).
   
    DO NOT MAKE ANY CHANGES BELOW if you want this to just work. Don't change the docker image [`linuxserver.io` will not work for this, for example]; don't change the paths, etc.

<!-docker-unraid-->

<!--local-->
???+ danger "Important"

    This walkthrough is assuming you are doing the entire process on the same platform; i.e. you're installing Kometa and editing its config files on a single 
    Linux, Windows, or OS X machine. It doesn't account for situations like running Kometa on a Linux machine while editing the config files on your Windows box.

<!--local-->

<!--all-->
### Prepare a small test library [optional]

While going through this process, Kometa is going to load the movies in your library, create some collections, and apply some overlays. 
If you have a large library, this will be very time-consuming.

For best results *with this walkthrough*, your test library will contain:

 - At least two comedy movies released since 2012.
 - At least two movies from the [IMDB top 250](https://www.imdb.com/chart/top/).
 - At least two movies from [IMDb's Popular list](https://www.imdb.com/chart/moviemeter).
 - At least two movies from [IMDb's Lowest Rated](https://www.imdb.com/chart/bottom).
 - A couple different resolutions among the movies.

For learning and testing, we will be taking advantage of the [`plex-test-libraries` repository](https://github.com/chazlarson/plex-test-libraries) 
which contains pre-made videos to use when following this guide.

Using the plex-test-libraries repository will ensure we have enough variety in media to populate the example collections that will be created. Running some of these default 
collections against a library of a few thousand movies can take hours, and for iterative testing it's useful to have something that will run in a few minutes or seconds.

Navigate to wherever you want to store these pre-made videos and then type:

```shell
git clone https://github.com/chazlarson/plex-test-libraries
cd plex-test-libraries
```

You should now see 2 folders, `test_tv_lib` and `test_movie_lib`. You will want to mount each of these to a library within Plex, as showcased here:

??? success "Test Plex Libraries (Click to Expand)"

    Library Name: `test_movie_lib`

    ![test_movie_lib](./../../../../assets/images/kometa/install/test_movie_lib.png){ width="600" }

    Library Name: `test_tv_lib`

    ![test_movie_lib](./../../../../assets/images/kometa/install/test_tv_lib.png){ width="600" }

<!--all-->

<!-local-docker-->
### Starting up your terminal.

Since most of this is typing commands into a terminal, you'll need to have a terminal open.

=== ":fontawesome-brands-linux: Linux"

    If your Linux system is remote to your computer, connect to it via SSH. That SSH session is the terminal you will be using, so leave it open.

    If you are running this on a desktop Linux machine, start up the Terminal application. 
    That window will be the terminal you will type commands into throughout this walkthrough, so leave it open.

=== ":fontawesome-brands-apple: macOS"

    Open the Terminal app; this window will be the place you type commands throughout this walkthrough, so leave it open. The Terminal app is in Applications -> Utilities.

    You can also use iTerm or some other terminal app if you wish. If you don't know what that means, use Terminal.

=== ":fontawesome-brands-windows: Windows"

    Use the Start menu to open PowerShell. This will be the window into which you type commands throughout this walkthrough, so leave it open.

<!-local-docker-->