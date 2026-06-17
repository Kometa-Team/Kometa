# json-schema/
<!-- Maintained by module-mapping. Derived block is auto-generated — do not hand-edit. -->

<!-- derived:start (generated 2026-06-09) -->
## Facts (auto-generated)
- Files:
    - collection-schema.json
    - config-schema.json
    - kitchen_sink_config.yml
    - metadata-schema.json
    - overlay-schema.json
    - playlist-schema.json
    - prototype_config.yml
    - README.md
- Public API / entry points (best-effort): (none detected — JSON/YAML, no export syntax)
- Depends on (internal): none
- Depends on (external): none (static schema files; consumed at runtime by modules/validator.py)
- Referenced by (fan-in):
    - kometa.py
- Coupling points to check:
    - contains contract/flag/env reference: collection-schema.json
    - contains contract/flag/env reference: config-schema.json
    - contains contract/flag/env reference: metadata-schema.json
    - contains contract/flag/env reference: overlay-schema.json
    - contains contract/flag/env reference: playlist-schema.json
    - these ARE the schema contracts — changes require matching updates in modules/validator.py and user YAML configs
- Governed by (business-logic doc): docs/ (config reference — see doc, not paraphrased here)
- Business-critical: no
- Possible duplicated rules: none detected
<!-- derived:end -->

<!-- narrative:start -->
## Notes (human-owned)
<!-- Fill in intent, gotchas, and cross-repo couplings detection can't see.
     Leave this stub if not yet written; module-mapping will not overwrite it. -->
<!-- narrative:end -->
