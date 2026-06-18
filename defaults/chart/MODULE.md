# defaults/chart/
<!-- Maintained by module-mapping. Derived block is auto-generated — do not hand-edit. -->

<!-- derived:start (generated 2026-06-09) -->
## Facts (auto-generated)
- Files:
    - anilist.yml
    - basic.yml
    - imdb.yml
    - letterboxd.yml
    - myanimelist.yml
    - other_chart.yml
    - separator_chart.yml
    - simkl.yml
    - tautulli.yml
    - tmdb.yml
    - trakt.yml
- Public API / entry points (best-effort): (none — YAML collection/overlay definitions)
- Depends on (internal): defaults/templates.yml; runtime data from modules/imdb.py, modules/mojo.py, and other source modules
- Depends on (external): none (static YAML)
- Referenced by (fan-in):
    - modules/builder.py
    - modules/imdb.py
    - modules/mojo.py
- Coupling points to check: none detected (still confirm cross-repo consumers manually)
- Governed by (business-logic doc): docs/ (defaults documentation — see doc, not paraphrased here)
- Business-critical: yes — changes here require human review against the governing doc
- Possible duplicated rules: none detected
<!-- derived:end -->

<!-- narrative:start -->
## Notes (human-owned)
<!-- business-critical path (overlay: defaults/) — document what chart sources are supported
     (IMDb, Trakt, TMDb, AniList, etc.), refresh cadence, and user override patterns.
     Fill in intent, gotchas, and cross-repo couplings detection can't see.
     Leave this stub if not yet written; module-mapping will not overwrite it. -->
<!-- narrative:end -->
