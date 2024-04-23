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

This should cover it:

## LinuxServer

The first image offered in unRAID for Kometa is the Linuxserver.io image [`linuxserver/kometa`]

This image is different to the official image [`kometateam/kometa`] in a couple ways that could cause issues for users who follow our installation guides.

If you use the LSIO image you should be aware of the following.

The LSIO image:

1. Advises and provides examples of absolute paths in the config, for example `/config/Movies.yml` and not `config/Movies.yml`, however, relative paths should still work as expected.

2. Resets ownership of entire `/config` dir on startup based on the values of the PUID/PGID environment variables. If not set, the ownership of the `/config` dir and its contents is set to 911:911, which can cause permissions issues.

Generally speaking, we suggest you use the official image instead of LSIO. We do not provide support for issues which relate to using third-party images [LSIO or other].

## Others

There are 8 other images listed at dockerhub aside from the official image and linuxserver.  None of them discuss how they are different beyond one noting it includes `curl`.

Unless you have some compelling reason to use one of those, you shouldn't.  You should stick with the official image.

If you choose to use another image than the default, you should be prepared for the possibility that published examples fail in various ways.
