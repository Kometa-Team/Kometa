# NAS_TYPE Walkthrough

This is a quick walkthrough of setting up the Kometa Docker container in the CONTAINER UI.

The CONTAINER UI may differ from these screenshots, but the concepts are the same:

1. Create a container based on the `kometateam/kometa` image.
2. Set environment variables to control the container's behavior [optional].
3. Point the container to the directory where your configuration files are to be stored.

This walkthrough discusses **only** the steps required to set up a Kometa container on a NAS_TYPE NAS. It does not cover creating a config file for Kometa.

There are two walkthroughs for getting familiar with Kometa:

1. [Local Python script](../../kometa/install/local)
2. [Docker container](../../kometa/install/docker)

You should go through one of those prior to doing this container setup, as they will familiarize you with the tool and how it works, 
and will produce the `config.yml` you will need to use with this process.

## Detailed steps
