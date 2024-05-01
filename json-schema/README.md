JSON schemas for Kometa YAML files

How to:

Add this as the first line in your `config.yml`:
```
# yaml-language-server: $schema=https://raw.githubusercontent.com/Kometa-Team/Kometa/nightly/json-schema/config-schema.json
```
[change `nightly` to `develop`, or `master` if you wish]

Then open your config file in an editor that supports the use of JSON schema.

For example, VS Code with the Red Hat YAML extension.

This will give you context-sensitive hints and auto-complete for much of the Kometa `config.yml`

![image](https://github.com/Kometa-Team/Kometa/assets/3865541/62133e59-ed12-4764-a4da-23595824d4da)

![image](https://github.com/Kometa-Team/Kometa/assets/3865541/06fbca9b-f0ad-4c20-8cf0-12d6c259c838)

limitations:

- template variables not cased for specific default file
- template variables with keys are wildcarded
- "position" attribute has no validation
- "streaming" default has no validation
- search has no validation; just accepts string
- schedule has no validation; just accepts string

TODO:
"list of coordinates"

- schema for collection yaml
- schema for metadata yaml
- schema for overlay yaml
- schema for template yaml

Notes:
