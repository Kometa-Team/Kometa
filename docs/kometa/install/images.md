# Docker Images

You should use the official docker image:

```
kometateam/kometa
```

All the examples in the wiki are assuming the use of this image, and many do not work with non-official Docker images due to differences in how the authors have chosen to construct their images.

One alternate image we see a lot is the Linuxserver image, due to its prominent placement in unRAID and linuxserver's general reputation.

## LXML Images

In March 2024, lxml, a prerequisite for operating Kometa, ceased support for older CPUs. This impedes users from running Kometa on unsupported hardware.

To address this issue, we have implemented 'lxml' variants for each Kometa branch (master, develop, and nightly). These variants resume compatibility with older hardware by freezing lxml on a previous version which has wider hardware support.

To transition to the lxml branch, simply prepend 'lxml-' to the branch name you are currently utilizing. For instance, `kometateam/kometa:lxml-master`, `kometateam/kometa:lxml-develop` and `kometateam/kometa:lxml-nightly`.

## LinuxServer

The first image offered in unRAID for Kometa is the Linuxserver.io image [`linuxserver/kometa`]

This image is different to the official image [kometateam/kometa] in a few ways that cause a variety of problems particularly for new users.

One typical error is something like:

```
Path does not exist: /run/s6/services/kometa/config/SOMETHING
```

The result is that the stock config file and a lot of the examples found in the wiki and config repo don't work.

If you use the LSIO image you should be aware of the following.

The LSIO image:

1. Requires absolute paths in the config. /config/Movies.yml, not config/Movies.yml. Because of this most of the examples in the wiki and config repo don't work as-is with lsio. Config files that work outside of docker often fail because of this with an error referring to `/run/s6/services/...`.

2. Only has `latest` version, no `develop` or `nightly`. If you want to switch to `develop` or `nightly` to try a new feature, they aren't available with LSIO image.

3. Doesn't support [runtime flags](../environmental.md), only ENV vars. This means that a command like:

   ```
   docker run -it --rm -v /opt/kometa/config:/config linuxserver/kometa --config config/config.yml -r --run-libraries "Movies - 4K DV"
   ```

   doesn't work with the LSIO image; it would have to be:

   ```
   docker run -it --rm -v /opt/kometa/config:/config -e KOMETA_CONFIG=/config/config.yml -e KOMETA_RUN=true -e KOMETA_LIBRARIES="Movies - 4K DV" linuxserver/kometa
   ```

4. Doesn't do manual runs correctly; they loop over and over. That command in the previous bullet point [which uses `KOMETA_RUN` to run it right now] will run over and over until you manually kill the container.  The same thing using the official image will run once and quit, as expected.

5. Resets ownership of entire config dir every run. In tests, the ownership of the config dir and its contents was set to 911:911 with each run.

Generally speaking, we suggest you use the official image instead of lsio.

## Others

There are 8 other images listed at dockerhub aside from the official image and linuxserver.  None of them discuss how they are different beyond one noting it includes `curl`.

Unless you have some compelling reason to use one of those, you shouldn't.  You should stick with the official image.

If you choose to use another image than the default, you should be prepared for the possibility that published examples fail in various ways.