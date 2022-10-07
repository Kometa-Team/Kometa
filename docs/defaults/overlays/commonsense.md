# CommonSense Age Rating Default Overlay File

The `commonsense` Overlay File is used to create an overlay based on the CommonSense Age Rating on each item within your library.

Note that this file requires the `mass_content_rating: mdb_commonsense` operation to be set against your library so that the content ratings are taken from CommonSense.

Example Overlays Created:

![](../images/commonsense_ov.png)

The below YAML in your config.yml will create the overlays:
```yaml
libraries:
  Movies:
    overlay_path:
      - pmm: commonsense
```

## Template Variables

Template Variables can be used to manipulate the file from the default settings which are provided. 

Note that the `templates_variables:` section only needs to be used if you do NOT want to use the default settings.

A key system is used to control the overlays that is created by the file. Each key refers to one overlay and is used to control multiple template variables.

Below are the keys and what they refer to:

| Key   | Age Rating |
|:------|:-----------|
| nr    | Not Rated  |

Further information on the universal template attributes and editing Overlay Files via template variables can be found [here]()


