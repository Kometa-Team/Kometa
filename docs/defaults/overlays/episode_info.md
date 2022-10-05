# Episode Info Default Overlay File

The `- pmm: episode_info` Overlay File is used to create an overlay based on the episode numbering within a given series in your library.

Note that this file should only be used against show libraries and is not expected to work against movie libraries. 

Example Overlays Created:

![](../images/episode_info_ov.png)

The below YAML in your config.yml will create the overlays:
```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: episode_info
```

## Template Variables

This Overlay File has no individual template variables that can be set.

Further information on the universal template attributes and editing Overlay Files via template variables can be found [here]()

