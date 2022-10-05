# Direct Play Default Overlay File

The `- pmm: direct_play` Overlay File is used to create an overlay to indicate items that cannot be transcoded and instead only support Direct Play (i.e. if you use Tautulli to kill 4K transcoding)

Example Overlays Created:

![](../images/direct_play_ov.png)

The below YAML in your config.yml will create the overlays:
```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: direct_play
```

## Template Variables

This Overlay File has no individual template variables that can be set.

Further information on the universal template attributes and editing Overlay Files via template variables can be found [here]()


