# defaults/movie/
<!-- Maintained by module-mapping. Derived block is auto-generated — do not hand-edit. -->

<!-- derived:start (generated 2026-06-09) -->
## Facts (auto-generated)
- Files:
    - content_rating_us.yml
    - continent.yml
    - country.yml
    - decade.yml
    - director.yml
    - franchise.yml
    - producer.yml
    - region.yml
    - seasonal.yml
    - writer.yml
- Public API / entry points (best-effort): (none — YAML collection/overlay definitions)
- Depends on (internal): defaults/templates.yml; runtime data from modules/letterboxd.py, modules/radarr.py, modules/tvdb.py
- Depends on (external): none (static YAML)
- Referenced by (fan-in):
    - modules/builder.py
    - modules/letterboxd.py
    - modules/radarr.py
    - modules/tvdb.py
    - modules/webhooks.py
    - tests/test_textfile.py
- Coupling points to check: none detected (still confirm cross-repo consumers manually)
- Governed by (business-logic doc): docs/ (defaults documentation — see doc, not paraphrased here)
- Business-critical: yes — changes here require human review against the governing doc
- Possible duplicated rules: none detected
<!-- derived:end -->

<!-- narrative:start -->
## Notes (human-owned)
<!-- business-critical path (overlay: defaults/) — document movie-only collection types,
     Radarr integration points, and user override patterns.
     Fill in intent, gotchas, and cross-repo couplings detection can't see.
     Leave this stub if not yet written; module-mapping will not overwrite it. -->
<!-- narrative:end -->
