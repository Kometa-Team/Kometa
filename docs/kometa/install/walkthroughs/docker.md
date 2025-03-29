---
hide:
  - toc
---
{%
    include-markdown "./../../../templates/walkthrough/header.md"
    include-tags='all|docker|local-docker|docker-unraid'
    replace='{
        "SYSTEM_NAME": "Docker",
        "RUN_TYPE": "via Docker",
        "APP_NAME": "Docker",
        "RETRIEVE": "docker",
        "RUN_NAME": "docker",
        "FULL_NAME": "a Docker container"
    }'
    rewrite-relative-urls=false
%}

### Installing Docker

To run Docker images, you need to have Docker installed. It is not typically installed on new Mac, Linux, or Windows machines.

The Docker install is discussed here: [Installing Docker](https://docs.docker.com/engine/install/)

Once you have Docker installed, test it at the command line with:

[type this into your terminal]
```shell
docker run --rm hello-world
```
You should see something that starts with:
```shell
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

If that doesn't work, stop here until you fix that. Diagnosing and repairing Docker install problems is out of the scope of this walkthrough.

---

{% include-markdown "./../../../templates/walkthrough/docker-image.md" %}

That means we can just jump right into running it. At the command prompt, type:

=== ":fontawesome-brands-docker: latest"

      ```shell
      docker run --rm kometateam/kometa --run
      ```

=== ":fontawesome-brands-docker: develop"

      ```shell
      docker run --rm kometateam/kometa:develop --run
      ```

=== ":fontawesome-brands-docker: nightly"

      ```shell
      docker run --rm kometateam/kometa:nightly --run
      ```

Use the branch reflecting the version of the wiki you are reading, as some functionality may be dependent on this. If you are reading the latest version of the wiki, 
use `latest` [or leave the tag off] as shown above. If you are reading the develop branch, use `develop`. If you are reading the nightly branch, use `nightly`.

This same thing holds for all future docker commands in this walkthrough.

This is going to fail with an error. That's expected.

You should see something like this:

```shell { .no-copy }
Unable to find image 'kometateam/kometa:latest' locally
latest: Pulling from kometateam/kometa
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
Status: Downloaded newer image for kometateam/kometa:latest
Config Error: config not found at //config
```

That error means you don’t have a config file, but we know that most everything is in place to run the image.

### Setting up a volume map

Kometa, inside that Docker container, can only see other things *inside the container*. We want to add our own files for config and metadata, 
so we need to set something up that lets Kometa see files we create *outside* the container. This is called a "volume map".

Go to your home directory and create a new directory:

[type this into your terminal]

```shell { .no-copy linenums="1"}
cd ~ #(1)!
mkdir kometa #(2)!
```

1. This changes to your home directory, which will be something like `/home/yourname` or `/Users/yourname` or `C:\Users\YourName` depending on the platform.
2. This creates a directory called "kometa"

cd into that directory and create another directory:

[type this into your terminal]

```shell { .no-copy linenums="1"}
cd ~/kometa #(1)!
mkdir config #(2)!
```

1. This navigates to the kometa folder within your home directory.
2. This creates a directory called "config"

get the full path:

[type this into your terminal]

```shell
pwd
```

This will display a full path:

=== ":fontawesome-brands-linux: Linux"

      ```shell { .no-copy }
      /home/YOURUSERNAME/kometa
      ```

=== ":fontawesome-brands-apple: macOS"

      ```shell { .no-copy }
      /Users/YOURUSERNAME/kometa
      ```

=== ":fontawesome-brands-windows: Windows"

      ```shell { .no-copy }
      C:\Users\YOURUSERNAME\kometa
      ```

Add "config" onto the end of that to get the host path to your config directory, for example:

=== ":fontawesome-brands-linux: Linux"

      ```shell { .no-copy }
      /home/YOURUSERNAME/kometa/config
      ```

=== ":fontawesome-brands-apple: macOS"
   
      ```shell { .no-copy }
      /Users/YOURUSERNAME/kometa/config
      ```

=== ":fontawesome-brands-windows: Windows"

      ```shell { .no-copy }
      C:\Users\YOURUSERNAME\kometa\config
      ```


You'll need to add this to the docker command every time you run it, like this:

=== ":fontawesome-brands-linux: Linux"

      ```shell
      docker run --rm -it -v "/home/YOURUSERNAME/kometa/config:/config:rw" kometateam/kometa --run
      ```

=== ":fontawesome-brands-apple: macOS"

      ```shell
      docker run --rm -it -v "/Users/YOURUSERNAME/kometa/config:/config:rw" kometateam/kometa --run
      ```

=== ":fontawesome-brands-windows: Windows"

      ```shell
      docker run --rm -it -v "C:\Users\YOURUSERNAME\kometa\config:/config:rw" kometateam/kometa --run
      ```

If you run that command now you should see something like this:

```bash { .no-copy }
$ docker run --rm -it -v "/Users/mroche/kometa/config:/config:rw" kometateam/kometa --run
Configuration File ('config.yml') has been downloaded from GitHub (Branch: 'master') and saved as '//config/config.yml'. Please update this file with your API keys and other required settings.
```

Note that I show the example path there.

??? question "Why did we create that `config`' directory?"

    This was done so that from here on in the instructions match between this walkthrough and the Local walkthrough, which insures consistency and reduces maintenance and 
    potential error. This is not required; you can put the config file anywhere you like, but you will need to adjust the paths in the commands you run in this walkthrough 
    to match where you put it. It's easier to have them match.


{%
    include-markdown "./../../../templates/walkthrough/mid.md"
    include-tags='all|docker|local-docker|docker-unraid'
    replace='{
        "INCLUDE_TAGS": "all|docker|local-docker|docker-unraid"
    }'
    rewrite-relative-urls=false
%}