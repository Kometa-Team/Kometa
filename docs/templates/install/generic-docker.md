### Before you start {#generic-docker-prerequisites}

Use this path if your platform is not listed or you already have Docker and want commands you can adapt to your host. You need a terminal, a working Docker installation, and a directory where you can save Kometa's configuration. Kometa connects to Plex over the network; you do not need to mount your media directories.

Verify Docker before continuing:

```shell
docker run --rm hello-world
```

If this fails, finish setting up Docker for your host first. Use the official `kometateam/kometa` image for the commands below. See [Docker images](images.md) for available tags; use `kometateam/kometa:develop` throughout if you are following the develop documentation.

### Prepare persistent storage {#generic-docker-storage}

Create a directory on your host for Kometa's configuration and logs. In every command below, replace `FULL_PATH_TO_CONFIG` with its absolute path, such as `/srv/kometa/config` or `C:\Kometa\config`.

```shell
docker run --rm -it -v "FULL_PATH_TO_CONFIG:/config:rw" kometateam/kometa --run
```

The first launch downloads a template `config.yml` if it is missing and asks you to edit it. Continue to [Configure Kometa](#configuration), then use [Run and verify](#first-run) to complete your first successful run.

The options mean:

- `-it` keeps the terminal interactive, which is useful for prompts such as MyAnimeList authentication.
- `-v "FULL_PATH_TO_CONFIG:/config:rw"` makes your host directory available at `/config` with write access. Keep the quotes, especially when the path contains spaces. Kometa reads `/config/config.yml` by default.
- `--run` starts Kometa immediately and exits when processing finishes. Place Kometa options after the image name.
- `--rm` removes the container when it exits. Your configuration and logs remain in the host directory.

### Choose how Kometa runs {#generic-docker-running}

After completing your first run, choose one of these commands. Each example uses the same persistent configuration directory.

**Wait in the foreground for the default daily run at 05:00:**

```shell
docker run --rm -it -v "FULL_PATH_TO_CONFIG:/config:rw" kometateam/kometa
```

**Keep a scheduled container running in the background:**

```shell
docker run -d --name kometa --restart unless-stopped -v "FULL_PATH_TO_CONFIG:/config:rw" kometateam/kometa
```

Use `docker logs -f kometa` to follow its output and `docker stop kometa` to stop it. Use `docker start kometa` to start it again. To change its settings or image, stop it and run `docker rm kometa` before recreating it with the updated command; keep the same configuration mount.

**Run daily at 17:00 in the background:**

```shell
docker run -d --name kometa --restart unless-stopped -v "FULL_PATH_TO_CONFIG:/config:rw" kometateam/kometa --times 17:00
```

These background examples are alternatives: use only one container for this configuration. Times use the container's timezone; add `-e TZ=Europe/London` before the image name, replacing the timezone with yours. See [commands and environment variables](../environmental.md) for other settings.

**Run immediately in the foreground, then remove the container:**

```shell
docker run --rm -it -v "FULL_PATH_TO_CONFIG:/config:rw" kometateam/kometa --run
```

Omit `--rm` if you want the stopped container to remain after that one-off run. For a regular installation where you prefer to save container settings in a file, select your host OS above and choose Docker Compose.
