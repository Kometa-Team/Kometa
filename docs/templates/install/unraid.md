### Prerequisites {#unraid-prerequisites}

You need access to your Plex server, permission to create and edit configuration files, and a terminal. Follow the platform steps below, then continue to the shared configuration and first-run instructions.

### Installing Community Applications in unRAID {#unraid-installing-community-applications-in-unraid}

Thankfully, getting Kometa working on unRAID is a fairly simple task. unRAID works mostly with docker containers, so the pre-built container available on docker hub works
perfectly with a little configuration. To install a container from docker hub, you will need community applications - a very popular plugin for unRAID servers.
If you don't already have this installed, you can install it [here](https://forums.unraid.net/topic/38582-plug-in-community-applications/)

### Installing Kometa in unRAID {#unraid-installing-kometa-in-unraid}

1. Head to the `Apps` tab of unRAID (Community Applications), and search `kometa` in the upper left search box. There will be a couple of results shown,
   but you should ignore them ([Why?](images.md)) and use the official image.

   ![unraid-options](../../assets/images/kometa/install/unraid-options.png)

2. Click the `Install` button on the Template from Sohjiro's Repository Tools.

3. Choose which branch you want to run `latest` or `develop`.

4. Set the `Console shell command:` to `Bash`

5. Verify that the `Container Path: /config` path for the unRAID app is `/mnt/user/appdata/Kometa/config`

   ![unraid-appdata](../../assets/images/kometa/install/unraid-appdata.png)

#### Important note on Docker images {#unraid-important-note-on-docker-images}

This tutorial uses the official image, and you should, too. Don't change `kometateam/kometa` to the `linuxserver.io` image or any other. 
Other images may have [idiosyncrasies](images.md) that will prevent this walkthrough from working. 
The official image *will* behave exactly as documented below. Others very possibly won't.

The great thing about Docker is that all the setup you'd have to do to run Kometa is already done inside the docker image.


Hit `Apply`, and allow unRAID to download the image and build the container.

First let's start the container. Oops! The container won't start? This is going to fail with an error. That's expected.

You should see something like this in the unRAID logs for the container:

```shell { .no-copy }
Config Error: config not found at //config
```
We need to have a file called `config.yml` in the correct directory for Kometa to start.
Open up an unRAID terminal session by clicking on the terminal icon `>_` in the top right of unRAID.


<div class="install-variant" data-os="unraid" markdown="1">

[type this into your unRAID terminal]
```shell
mkdir /mnt/user/appdata/Kometa/config
touch /mnt/user/appdata/Kometa/config/config.yml
```


</div>

You can now close the unRAID terminal and start the Kometa container.

**_From this point forward, you can Console `>_Console` into the running container as it will stay running_**

Open a Console by left-clicking on the running Kometa Container and selecting `>_Console`.
This will open up an interactive session within the container to be able to run the commands we want.

![](../../assets/images/kometa/install/unraid-console.png)
