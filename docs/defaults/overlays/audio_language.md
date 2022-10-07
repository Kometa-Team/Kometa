# Audio Language Default Overlay File

The `audio_language` Overlay File is used to create an overlay based on the number of audio languages available on each item within your library.

Example Overlays Created:

![](../images/audio_language_ov.png)

The below YAML in your config.yml will create the overlays:
```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: audio_language
```

## Template Variables

Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

A key system is used to control each overlay that is created by the file. Each key refers to one overlay and is used to control multiple template variables.

Below are the keys and what they refer to:

| Key   | Audio Languages                        |
|:------|:---------------------------------------|
| dual  | Dual Audio (i.e. 2 languages)          |
| multi | Multi Audio (i.e. 3 or more languages) |

Further information on the universal template attributes and editing Overlay Files via template variables can be found [here]()


