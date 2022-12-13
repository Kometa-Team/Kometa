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
   1. TMDb API Key
   2. Plex URL and Token
6. Then, iteratively:
   1. use `python` to run the script
   2. use a text editor to modify a couple of text files until you have a working config file and a single working metadata file.

Note that running a Python script is inherently a pretty technical process.  If you are unable or unwilling to learn the rudiments of using tools like python and git, you should probably strongly consider running PMM in [Docker](docker).  That will eliminate the Python and git installs from this process and make it as simple as it can be.

If the idea of editing YAML files by hand is daunting, this may not be the tool for you.  All the configuration of PMM is done via YAML text files, so if you are unable or unwilling to learn how those work, you should stop here.

Finally, this walkthrough is intended to give you a basic grounding in how to get the script running.  It doesn't cover how to create your own collections, or how to add overlays, or any of the myriad other things PMM is capable of.  It provides a simple "Getting Started" guide for those for whom the standard install instructions make no sense; presumably because you've never run a Python script before.

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

### Prepare a small test library [optional]

```{include} wt/wt-test-library.md
```

### Starting up your terminal.

Since most of this is typing commands into a terminal, you'll need to have a terminal open.


````{tab} Linux
If your Linux system is remote to your computer, connect to it via SSH.  That SSH session is the terminal you will be using, so leave it open.

If you are running this on a desktop Linux machine, start up the Terminal application.  That window will be the terminal you will type commands into throughout this walkthrough, so leave it open.
````
````{tab} OS X:
Open the Terminal app; this window will be the place you type commands throughout this walkthrough, so leave it open.  The Terminal app is in Applications -> Utilities.

You can also use iTerm or some other terminal app if you wish.  If you don't know what that means, use Terminal.
````
````{tab} Windows:
Use the Start menu to open PowerShell.  This will be the window into which you type commands throughout this walkthrough, so leave it open.
````

### Installing Python.

In order to run a Python script. the first thing you'll need is a Python interpreter.  This is typically already present on Linux and Mac, but will probably have to be installed on Windows.

First let's check if it's installed already [type this into your terminal]:

```
python3 --version
```

If this doesn't return `3.7.0` or higher, you'll need to get Python 3 installed.

````{tab} Linux
Describing a python install for any arbitrary linux is out of scope here, but if you're using Ubuntu, [this](https://techviewleo.com/how-to-install-python-on-ubuntu-linux/) might be useful.
````
````{tab} OS X:
Follow the instructions here: [Installing Python 3 on Mac OS X](https://docs.python-guide.org/starting/install3/osx/)
````
````{tab} Windows:
Go to http://www.python.org/download and download the next-to-latest minor version of Python for Windows in 32 or 64-bit as appropriate for your system [probably 64-bit].  As this is written, that's 3.10, while the latest is 3.11.

#### Why the next-to-latest?

There is one dependency [`lxml`] that lags behind new Python releases; this will cause a failure when installing requirements in a moment if the newest Python version is too new [at time of writing the current is 3.11, and the requirements install fails on the lxml library].  You can avoid this by using the next-to-latest release.  At some point this will no longer be a problem, but that is outside the control of PMM.

Once downloaded, run the installer.  Tick “Add to path” checkbox at the bottom and click “Install Now”.

For Windows 10, you will need to enable scripts in PowerShell.  Follow the instructions [here](https://windowsloop.com/enable-powershell-scripts-execution-windows-10) to do so.  If you skip this step you're going to hit a hard stop in a moment.
````

---

### Installing git

To copy the Plex-Meta-Manager code to your machine, we'll be using git.  This may be installed on Mac or Linux, and probably isn't in Windows.

First let's check if it's installed already [type this into your terminal]:

```
git --version
```

If this doesn't return a version number, you'll need to get git installed.

````{tab} Linux
The git install is discussed here: [Download for Linux and Unix](https://git-scm.com/download/linux)
````
````{tab} OS X:
The git install is discussed here: [Git - Downloading Package](https://git-scm.com/download/mac)
````
````{tab} Windows:
Download the installer from [here](https://git-scm.com/download/windows)

Run the install; you can probably just accept the defaults and click through except for the step that asks you to choose an editor; you probably want to choose something other than the default there:

![Git Install](git-install.png)

This install comes with its own command line interface.  **Do not use this interface in this walkthrough**.  Continue to do everything here in Powershell.
````

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

**IMPORTANT: In the future, when you want to run PMM at the command line, you have to be in this directory.**

When you open a command window to run PMM, the first step will always be:

```
cd ~
cd Plex-Meta-Manager
```

There are parts of the code that are assuming and expecting that you will be in this directory when you run PMM [the fonts used in overlays are one example].  Be sure that you are always in this directory when you run PMM.

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

````{tab} Linux
[type this into your terminal]

```
python3 -m venv pmm-venv
```

If you see an error like:

```
Error: Command '['/home/mroche/Plex-Meta-Manager/pmm-venv/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']' returned non-zero exit status 1.
```
You probably need to make sure the Python 3.9-specific virtualenv support library is installed:

[type this into your terminal]

```
sudo apt-get install python3.9-venv
```

Then try the original venv command above again.
````
````{tab} OS X:
[type this into your terminal]

```
python3 -m venv pmm-venv
```

````
````{tab} Windows:
[type this into your terminal]

```
python -m venv pmm-venv
```

If you see:

```
Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.
```

You apparently didn't check the “Add to path” checkbox above under [installing Python](#installing-python).  "Repair" your Python install and check "add python to environment variables".
````

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

That will create the virtual environment, and then you need to activate it:

````{tab} Linux
[type this into your terminal]

```
source pmm-venv/bin/activate
```
````
````{tab} OS X:
[type this into your terminal]

```
source pmm-venv/bin/activate
```
````
````{tab} Windows:
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

Once you have done that, try the activation step again.
````

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

An advantage of doing this in a virtual environment is that in the event something goes wrong with this part of the setup, you can delete that pmm-venv directory and do the setup again.

**IMPORTANT: In the future, when you want to run the script, you will need to do this "activation" step every time.  Not the venv creation, just the activation**:

````{tab} Linux
[type this into your terminal]

```
source pmm-venv/bin/activate
```
````
````{tab} OS X:
[type this into your terminal]

```
source pmm-venv/bin/activate
```
````
````{tab} Windows:
[type this into your terminal]

```
.\pmm-venv\Scripts\activate
```
````

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
  <summary>`Encountered error while trying to install package.`</summary>
  <br />

  If you see an error that ends in something like this:

```
   ...
   building 'lxml.etree' extension
   error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
   [end of output]

   note: This error originates from a subprocess, and is likely not a problem with pip.
   error: legacy-install-failure

   × Encountered error while trying to install package.
   ╰─> lxml
```
  You've hit the error we were referring to above with the Python version being too recent.  Probably you are running Python 3.11 in late 2022 or Python 3.12 shortly after its release.  Deactivate and delete the virtual environment and create one based on the previous Python release [which may involve removing Python and reinstalling the older version depending on platform], then try this step again.

</details>

<details>
  <summary>What did that do?</summary>
  <br />

  This told Python to use the `pip` module to install some libraries that PMM needs.

</details>

Let’s make sure it’s working so far.

```{include} wt/wt-run-shell.md
```

This is going to fail with an error, which you will then fix.

You should see something like this:

```
Config Error: config not found at /Users/mroche/Plex-Meta-Manager/config
```

That error means you don’t have a config file, but we at least know that the requirements are in place and the script can run.

### Create a directory to quiet an error later

The default config file contains a reference to a directory that will show an error in the output later.  That error can safely be ignored, but it causes some confusion with new users from time to time.

We'll create it here so the error doesn't show up later.

````{tab} Linux
[type this into your terminal]

```
mkdir config/assets
```
````
````{tab} OS X:
[type this into your terminal]

```
mkdir config/assets
```
````
````{tab} Windows:
[type this into your terminal]

```
mkdir config\assets
```
````

### Setting up the initial config file

```{include} wt/wt-01-basic-config.md
```

#### Editing the config template

First, make a copy of the template.  This is going to create a copy of the base template that you can then edit.  You only need to do this once.

````{tab} Linux
[type this into your terminal]

```
cp config/config.yml.template config/config.yml
```
````
````{tab} OS X:
[type this into your terminal]

```
cp config/config.yml.template config/config.yml
```
````
````{tab} Windows:
[type this into your terminal]

```
copy .\config\config.yml.template .\config\config.yml
```
````

Now open the copy in an editor:

```{include} wt/wt-editor.md
```

```{include} wt/wt-02-config-bad-library.md
```

#### Testing the config file

Save the file:

```{include} wt/wt-save.md
```

Then run the script again:

```{include} wt/wt-run-shell.md
```

```{include} wt/wt-03-lib-err-and-fix.md
```


### Creating a few sample collections.

```{include} wt/wt-04-default-intro.md
```

So let's run the script and see this happen:


```{include} wt/wt-run-shell.md
```

```{include} wt/wt-04b-default-after.md
```

### Setting up a metadata file and creating a sample collection.

```{include} wt/wt-05-local-file.md
```

Save the file:

```{include} wt/wt-save.md
```

Then run the script again:

```{include} wt/wt-run-shell.md
```

```{include} wt/wt-06-local-after.md
```

### Adding Overlays to movies.

```{include} wt/wt-07-overlay-add.md
```

Save the file:

```{include} wt/wt-save.md
```

Then run the script again:

```{include} wt/wt-run-shell.md
```

```{include} wt/wt-08-overlay-after.md
```

```{include} wt/wt-09-next-steps.md
```

When you are done, deactivate the virtual environment:

[type this into your terminal]

```
deactivate
```

## Other Topics

### Scheduling

```{include} wt/wt-10-scheduling.md
```

### I want to update to the latest version of PMM

````{tab} Linux
[type this into your terminal]

```
cd ~/Plex-Meta-Manager
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} OS X:
[type this into your terminal]

```
cd ~/Plex-Meta-Manager
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} Windows:
[type this into your terminal]

```
cd ~\Plex-Meta-Manager
git pull
.\pmm-venv\Scripts\activate
python -m pip install -r requirements.txt
```
````

### I want to use the develop branch

````{tab} Linux
[type this into your terminal]

```
cd ~/Plex-Meta-Manager
git checkout develop
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} OS X:
[type this into your terminal]

```
cd ~/Plex-Meta-Manager
git checkout develop
git pull
source pmm-venv/bin/activate
python -m pip install -r requirements.txt
```
````
````{tab} Windows:
[type this into your terminal]

```
cd ~/Plex-Meta-Manager
git checkout develop
git pull
.\pmm-venv\Scripts\activate
python -m pip install -r requirements.txt
```
````

### I want to use the nightly branch

Follow the instructions for the `develop` branch above, subsituting `nightly` for `develop`

### I want to use the master branch

Follow the instructions for the `develop` branch above, subsituting `master` for `develop`

The reinstall of requirements every time is probably overkill, but it's harmless and ensures that you always get any new versions or new requirements.

