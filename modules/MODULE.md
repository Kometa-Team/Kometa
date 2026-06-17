# modules/
<!-- Maintained by module-mapping. Derived block is auto-generated — do not hand-edit. -->

<!-- derived:start (generated 2026-06-09) -->
## Facts (auto-generated)
- Files:
    - anidb.py
    - anilist.py
    - apprise_notify.py
    - builder.py
    - cache.py
    - config.py
    - convert.py
    - ergast.py
    - github.py
    - gotify.py
    - icheckmovies.py
    - imdb.py
    - letterboxd.py
    - library.py
    - logs.py
    - mal.py
    - mdblist.py
    - meta.py
    - mojo.py
    - notifiarr.py
    - ntfy.py
    - omdb.py
    - operations.py
    - overlay.py
    - overlays.py
    - plex.py
    - poster.py
    - radarr.py
    - request.py
    - simkl.py
    - sonarr.py
    - stevenlu.py
    - tautulli.py
    - textfile.py
    - tmdb.py
    - trakt.py
    - tvdb.py
    - util.py
    - validator.py
    - webhooks.py
- Public API / entry points (best-effort):
    - class AniDB / AniDBObj / AniDBTitles
    - class AniList
    - class AppriseNotify
    - class BoxOfficeMojo
    - class Cache
    - class CollectionBuilder
    - class Component
    - class ConfigFile
    - class ConfigValidator
    - class Continue / Deleted / Failed / FilterFailed / LimitReached / NonExisting / NotFound / NotScheduled / NotScheduledRange / TimeoutExpired
    - class Convert
    - class DataFile / MetadataFile / OverlayFile / PlaylistFile / TextFile
    - class Ergast
    - class FileSetValidator
    - class GitHub
    - class Gotify / Notifiarr / Ntfy / Webhooks
    - class ICheckMovies
    - class ImageBase / ImageData / KometaImage
    - class IMDb
    - class Letterboxd
    - class Library
    - class MDBList / MDbObj
    - class MyAnimeList / MyAnimeListObj
    - class MyLogger
    - class OMDb / OMDbObj
    - class Operations
    - class Overlay / Overlays
    - class Plex
    - class Race / Radarr / Sonarr
    - class Requests
    - class Simkl
    - class StevenLu / Tautulli
    - class TMDb / TMDbCountry / TMDbEpisode / TMDbMovie / TMDBObj / TMDbSeason / TMDbShow
    - class Trakt
    - class TVDb / TVDbObj
    - class Version / YAML
- Depends on (internal): none (self-contained package; imported by kometa.py and tests/)
- Depends on (external): apprise, arrapi, dateutil (python-dateutil), lxml, num2words, pathvalidate, Pillow (PIL), plexapi, requests, ruamel.yaml, tenacity, tmdbapis
- Referenced by (fan-in):
    - kometa.py
    - tests/test_apprise_notify.py
    - tests/test_builder.py
    - tests/test_letterboxd.py
    - tests/test_simkl.py
    - tests/test_textfile.py
    - tests/test_tvdb.py
    - tests/test_validator.py
    - NOTE: high fan-in (8) — high blast radius on change
- Coupling points to check:
    - contains contract/flag/env reference: modules/plex.py
    - contains contract/flag/env reference: modules/poster.py
    - contains contract/flag/env reference: modules/util.py
    - contains contract/flag/env reference: modules/validator.py
    - verify consumers in other modules/areas are updated to match
- Governed by (business-logic doc): docs/ (user-facing documentation and config reference — see doc, not paraphrased here)
- Business-critical: yes — changes here require human review against the governing doc
- Possible duplicated rules: none detected
<!-- derived:end -->

<!-- narrative:start -->
## Notes (human-owned)
<!-- business-critical path (overlay) + fan-in 8 — document key interfaces, primary caller
     patterns, and change blast radius. Fill in intent, gotchas, and cross-repo couplings
     detection can't see. Leave this stub if not yet written; module-mapping will not overwrite it. -->
<!-- narrative:end -->
