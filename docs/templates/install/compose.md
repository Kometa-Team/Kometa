## Install with Docker Compose {#compose-setup}

Install Docker with the Compose plugin, then verify it:

```shell
docker run --rm hello-world
docker compose version
```

Create a `kometa` directory in your home directory, then a `config` directory inside it. Open a terminal in `kometa`. Save this as `compose.yml` there:

```yaml
services:
  kometa:
    image: kometateam/kometa
    volumes:
      - ./config:/config:rw
    restart: unless-stopped
```

The `./config` directory on the host will persist configuration and logs. Complete the configuration below before starting a run. After the first successful run, `docker compose up -d` starts the scheduled service. Use `docker compose logs -f kometa` to follow it and `docker compose down` to stop it without deleting your configuration.
