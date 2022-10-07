# Audio Codec Default Overlay File

The `audio_codec` Overlay File is used to create an overlay based on the audio codec available on each item within your library.


Example Overlays Created:

![](../images/audio_codec_ov.png)

The below YAML in your config.yml will create the overlays:
```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: audio_codec
```

## Template Variables

Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

A key system is used to control each overlay that is created by the file. Each key refers to one overlay and is used to control multiple template variables.

Below are the keys and what they refer to:

| Key          | Audio Codec            |
|:-------------|:-----------------------|
| opus         | Opus                   |
| mp3          | MP3                    |
| digital      | Dolby Digital          |
| aac          | AAC                    |
| dts          | DTS                    |
| es           | DTS-ES                 |
| plus         | Dolby Digital+         |
| hra          | DTS-HD-HRA             |
| pcm          | PCM                    |
| flac         | FLAC                   |
| hd           | DTS-HD-MA              |
| truehd       | Dolby TrueHD           |
| plus-atmos   | Dolby Digital+ / E-AC3 |
| atmos        | Dolby Atmos            |
| x            | DTS-X                  |
| truehd-atmos | Dolby TrueHD Atmos     |



Further information on the universal template attributes and editing Overlay Files via template variables can be found [here]()

