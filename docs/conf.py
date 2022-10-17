# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import datetime
import sys
from os.path import abspath, dirname

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
import sphinx_bootstrap_theme

path = dirname(abspath(__file__))
sys.path.append(path)


# -- Project information -----------------------------------------------------

project = "Plex Meta Manager Wiki"
author = "Nathan Taggart"
copyright = f"{datetime.datetime.now().year}"

# The full version, including alpha/beta/rc tags
with open("../VERSION") as f:
    release = f.readline()


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'myst_parser',
    'sphinx_inline_tabs',
    'sphinx_copybutton',
    'sphinx_reredirects'
]

source_suffix = ['.rst', '.md']
myst_heading_anchors = 4

# -- Napoleon Settings -----------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
autodoc_member_order = 'bysource'
add_module_names = False

master_doc = 'index'

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "nature"
html_theme = "bootstrap"
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
# (Optional) Logo. Should be small enough to fit the navbar (ideally 24x24).
# Path should be relative to the ``_static`` files directory.
html_logo = "_static/logo-white.png"
html_favicon = "_static/favicon.png"

html_copy_source = False
html_show_sourcelink = False

# Redirect URLs
# "<source>": "<target>"
redirects = {
     "redact": "https://regex101.com/r/DMo1DQ/latest"
}

# Theme options are theme-specific and customize the look and feel of a
# theme further.

html_theme_options = {
    # Tab name for entire site. (Default: "Site")
    'navbar_site_name': "Table of Contents",

    # A list of tuples containing pages or urls to link to.
    # Valid tuples should be in the following forms:
    #    (name, page)                 # a link to a page
    #    (name, "/aa/bb", 1)          # a link to an arbitrary relative url
    #    (name, "http://example.com", True) # arbitrary absolute url
    # Note the "1" or "True" value above as the third argument to indicate
    # an arbitrary url.
    'navbar_links': [
        ("_menu", "Essentials", [
            ("Plex Meta Manager", "index"),
            ("_divider", ),
            ("_menu", "Installation", "home/installation", [
                ("Installing Plex Meta Manager", "home/installation"),
                ("_divider", ),
                ("Local Walkthrough", "home/guides/local"),
                ("Docker Walkthrough", "home/guides/docker"),
                ("_divider", ),
                ("unRAID Walkthrough", "home/guides/unraid"),
                ("Kubernetes Walkthrough", "home/guides/kubernetes"),
                ("QNAP Walkthrough", "home/guides/qnap"),
                ("Synology Walkthrough", "home/guides/synology"),
            ]),
            ("Docker Images", "home/guides/alternative-docker"),
            ("Log Files", "home/logs"),
            ("Run Commands & Environment Variables", "home/environmental"),
            ("Knowledgebase/FAQ", "home/kb"),
            ("_divider", ),
            ("Scheduling Guide", "home/guides/scheduling"),
            ("Image Asset Directory Guide", "home/guides/assets"),
            ("Formula 1 Metadata Guide", "home/guides/formula"),
            ("_divider", ),
            ("User Configs Repository", "https://github.com/meisnate12/Plex-Meta-Manager-Configs", True),
            ("Discord Server", "https://discord.gg/NfH6mGFuAB", True),
            ("Sponsor", "https://github.com/sponsors/meisnate12", True),
            ("Acknowledgements", "home/acknowledgements"),
        ]),
        ("_menu", "Config", [
            ("Configuration File", "config/configuration"),
            ("Redacting Your Config", "redact"),
            ("_divider", ),
            ("Libraries/Playlists", "config/libraries"),
            ("Path Types", "config/paths"),
            ("Operations", "config/operations"),
            ("_menu", "Operations", "config/operations", [
                ("Assets For All", "config/operations.html#assets-for-all"),
                ("Delete Collections With Less", "config/operations.html#delete-collections-with-less"),
                ("Delete Unmanaged Collections", "config/operations.html#delete-unmanaged-collections"),
                ("Mass Genre Update", "config/operations.html#mass-genre-update"),
                ("Mass Content Rating Update", "config/operations.html#mass-content-rating-update"),
                ("Mass Original Title Update", "config/operations.html#mass-original-title-update"),
                ("Mass Originally Available Update", "config/operations.html#mass-originally-available-update"),
                ("Mass * Rating Update", "config/operations.html#mass--rating-update"),
                ("Mass Episode * Rating Update", "config/operations.html#mass-episode--rating-update"),
                ("Mass IMDb Parental Labels", "config/operations.html#mass-imdb-parental-labels"),
                ("Mass Collection Mode", "config/operations.html#mass-collection-mode"),
                ("Update Blank Track Titles", "config/operations.html#update-blank-track-titles"),
                ("Remove Title Parentheses", "config/operations.html#remove-title-parentheses"),
                ("Split Duplicates", "config/operations.html#split-duplicates"),
                ("Radarr Add All", "config/operations.html#radarr-add-all"),
                ("Radarr Remove By Tag", "config/operations.html#radarr-remove-by-tag"),
                ("Sonarr Add All", "config/operations.html#sonarr-add-all"),
                ("Sonarr Remove By Tag", "config/operations.html#sonarr-remove-by-tag"),
                ("Genre Mapper", "config/operations.html#genre-mapper"),
                ("Content Rating Mapper", "config/operations.html#content-rating-mapper"),
                ("Metadata Backup", "config/operations.html#metadata-backup"),
            ]),
            ("Settings", "config/settings"),
            ("Webhooks", "config/webhooks"),
            ("_divider", ),
            ("Plex", "config/plex"),
            ("Tautulli", "config/tautulli"),
            ("Radarr", "config/radarr"),
            ("Sonarr", "config/sonarr"),
            ("_divider", ),
            ("TMDb", "config/tmdb"),
            ("Trakt", "config/trakt"),
            ("MdbList", "config/mdblist"),
            ("OMDb", "config/omdb"),
            ("AniDB", "config/anidb"),
            ("MyAnimeList", "config/myanimelist"),
            ("Notifiarr", "config/notifiarr"),
        ]),
        ("_menu", "Defaults", [
            ("Defaults Usage Guide", "defaults/guide"),
            ("Defaults Files", "defaults/files"),
            ("_divider", ),
            ("_menu", "Collections", "defaults/variables", [
                ("Collections", "defaults/defaults"),
                ("Shared Variables", "defaults/variables"),
                ("_divider", ),
                ("Separators", "defaults/separators"),
                ("_menu", "Award", "#", [
                    ("Awards Separator", "defaults/award/separator"),
                    ("_divider",),
                    ("Academy Awards (Oscars)", "defaults/award/oscars"),
                    ("British Academy of Film Awards", "defaults/award/bafta"),
                    ("Cannes File Festival Awards", "defaults/award/cannes"),
                    ("Critics Choice Awards", "defaults/award/choice"),
                    ("Emmy Awards", "defaults/award/emmy"),
                    ("Golden Globe Awards", "defaults/award/golden"),
                    ("Independent Spirit Awards", "defaults/award/spirit"),
                    ("Sundance File Festival Awards", "defaults/award/sundance"),
                    ("Other Awards", "defaults/award/other"),
                ]),
                ("_menu", "Chart", "#", [
                    ("Chart Separator", "defaults/chart/separator"),
                    ("_divider",),
                    ("Basic Charts", "defaults/chart/basic"),
                    ("AniList Charts", "defaults/chart/anilist"),
                    ("Flixpatrol Charts", "defaults/chart/flixpatrol"),
                    ("IMDb Charts", "defaults/chart/imdb"),
                    ("MyAnimeList Charts", "defaults/chart/myanimelist"),
                    ("Tautulli Charts", "defaults/chart/tautulli"),
                    ("TMDb Charts", "defaults/chart/tmdb"),
                    ("Trakt Charts", "defaults/chart/trakt"),
                    ("Other Charts", "defaults/chart/other"),
                ]),
                ("_menu", "Movie", "#", [
                    ("Actors", "defaults/both/actor"),
                    ("Audio Languages", "defaults/both/audio_language"),
                    ("Content Ratings (US)", "defaults/movie/content_rating_us"),
                    ("Content Ratings (UK)", "defaults/both/content_rating_uk"),
                    ("Countries", "defaults/movie/country"),
                    ("Decades", "defaults/movie/decade"),
                    ("Directors", "defaults/movie/director"),
                    ("Franchises", "defaults/movie/franchise"),
                    ("Genres", "defaults/both/genre"),
                    ("Producers", "defaults/movie/producer"),
                    ("Resolutions", "defaults/both/resolution"),
                    ("Resolution Standards", "defaults/both/resolution_standards"),
                    ("Seasonal", "defaults/movie/seasonal"),
                    ("Streaming", "defaults/both/streaming"),
                    ("Studios", "defaults/both/studio"),
                    ("Subtitle Languages", "defaults/both/subtitle_language"),
                    ("Universes", "defaults/movie/universe"),
                    ("Writers", "defaults/movie/writer"),
                    ("Years", "defaults/both/year"),
                ]),
                ("_menu", "Show", "#", [
                    ("Actors", "defaults/both/actor"),
                    ("Audio Languages", "defaults/both/audio_language"),
                    ("Content Ratings (US)", "defaults/show/content_rating_us"),
                    ("Content Ratings (UK)", "defaults/both/content_rating_uk"),
                    ("Countries", "defaults/show/country"),
                    ("Decades", "defaults/show/decade"),
                    ("Franchises", "defaults/show/franchise"),
                    ("Genres", "defaults/both/genre"),
                    ("Networks", "defaults/show/network"),
                    ("Resolutions", "defaults/both/resolution"),
                    ("Resolution Standards", "defaults/both/resolution_standards"),
                    ("Streaming", "defaults/both/streaming"),
                    ("Studios", "defaults/both/studio"),
                    ("Subtitle Languages", "defaults/both/subtitle_language"),
                    ("Years", "defaults/both/year"),
                ]),
            ]),
            ("Playlists", "defaults/playlist"),
            ("_menu", "Overlays", "defaults/overlays/defaults", [
                ("Overlays", "defaults/overlays/defaults"),
                ("Shared Variables", "defaults/overlays/variables"),
                ("_divider", ),
                ("Audio Codec", "defaults/overlays/audio_codec"),
                ("Audio Languages", "defaults/overlays/audio_language"),
                ("Common Sense Age Ratings", "defaults/overlays/commonsense"),
                ("Direct Play Only", "defaults/overlays/direct_play"),
                ("Episode Info", "defaults/overlays/episode_info"),
                ("MediaStinger", "defaults/overlays/mediastinger"),
                ("Ratings", "defaults/overlays/ratings"),
                ("Resolution/Edition", "defaults/overlays/resolution"),
                ("Ribbon", "defaults/overlays/ribbon"),
                ("Runtimes", "defaults/overlays/runtimes"),
                ("Status", "defaults/overlays/status"),
                ("Streaming", "defaults/overlays/streaming"),
                ("Versions", "defaults/overlays/versions"),
                ("Video Format", "defaults/overlays/video_format"),
            ]),
        ]),
        ("_menu", "Files", [
            ("Metadata Files", "metadata/metadata"),
            ("Overlay Files", "metadata/overlay"),
            ("Playlist Files", "metadata/playlist"),
            ("_divider", ),
            ("Templates", "metadata/templates"),
            ("Filters", "metadata/filters"),
            ("Dynamic Collections", "metadata/dynamic"),
            ("_menu", "Editing Media Metadata", "#", [
                ("Editing Movie Metadata", "metadata/metadata/movie"),
                ("Editing TV Metadata", "metadata/metadata/show"),
                ("Editing Music Metadata", "metadata/metadata/music"),
            ]),
            ("_menu", "Builders", "#", [
                ("_menu", "Plex Builders", "metadata/builders/plex", [
                    ("Plex All", "metadata/builders/plex.html#plex-all"),
                    ("Plex Watchlist", "metadata/builders/plex.html#plex-watchlist"),
                    ("Plex Pilots", "metadata/builders/plex.html#plex-pilots"),
                    ("Plex Collectionless", "metadata/builders/plex.html#plex-collectionless"),
                    ("Plex Search", "metadata/builders/plex.html#plex-search"),
                ]),
                ("_menu", "Smart Builders", "metadata/builders/smart", [
                    ("Smart Label", "metadata/builders/smart.html#smart-label"),
                    ("Smart Filter", "metadata/builders/smart.html#smart-filter"),
                ]),
                ("_menu", "TMDb Builders", "metadata/builders/tmdb", [
                    ("TMDb Collection", "metadata/builders/tmdb.html#tmdb-collection"),
                    ("TMDb List", "metadata/builders/tmdb.html#tmdb-list"),
                    ("TMDb Actor", "metadata/builders/tmdb.html#tmdb-actor"),
                    ("TMDb Crew", "metadata/builders/tmdb.html#tmdb-crew"),
                    ("TMDb Director", "metadata/builders/tmdb.html#tmdb-director"),
                    ("TMDb Producer", "metadata/builders/tmdb.html#tmdb-producer"),
                    ("TMDb Writer", "metadata/builders/tmdb.html#tmdb-writer"),
                    ("TMDb Movie", "metadata/builders/tmdb.html#tmdb-movie"),
                    ("TMDb Show", "metadata/builders/tmdb.html#tmdb-show"),
                    ("TMDb Company", "metadata/builders/tmdb.html#tmdb-company"),
                    ("TMDb Network", "metadata/builders/tmdb.html#tmdb-network"),
                    ("TMDb Keyword", "metadata/builders/tmdb.html#tmdb-keyword"),
                    ("TMDb Popular", "metadata/builders/tmdb.html#tmdb-popular"),
                    ("TMDb Now Playing", "metadata/builders/tmdb.html#tmdb-now-playing"),
                    ("TMDb Top Rated", "metadata/builders/tmdb.html#tmdb-top-rated"),
                    ("TMDb Upcoming", "metadata/builders/tmdb.html#tmdb-upcoming"),
                    ("TMDb Airing Today", "metadata/builders/tmdb.html#tmdb-airing-today"),
                    ("TMDb On the Air", "metadata/builders/tmdb.html#tmdb-on-the-air"),
                    ("TMDb Trending Daily", "metadata/builders/tmdb.html#tmdb-trending-daily"),
                    ("TMDb Trending Weekly", "metadata/builders/tmdb.html#tmdb-trending-weekly"),
                    ("TMDb Discover", "metadata/builders/tmdb.html#tmdb-discover"),
                ]),
                ("_menu", "TVDb Builders", "metadata/builders/tvdb", [
                    ("TVDb List", "metadata/builders/tvdb.html#tvdb-list"),
                    ("TVDb Movie", "metadata/builders/tvdb.html#tvdb-movie"),
                    ("TVDb Show", "metadata/builders/tvdb.html#tvdb-show"),
                ]),
                ("_menu", "IMDb Builders", "metadata/builders/imdb", [
                    ("IMDb ID", "metadata/builders/imdb.html#imdb-id"),
                    ("IMDb Chart", "metadata/builders/imdb.html#imdb-chart"),
                    ("IMDb List", "metadata/builders/imdb.html#imdb-list"),
                    ("IMDb Watchlist", "metadata/builders/imdb.html#imdb-watchlist"),
                ]),
                ("_menu", "Trakt Builders", "metadata/builders/trakt", [
                    ("Trakt List", "metadata/builders/trakt.html#trakt-list"),
                    ("Trakt Chart", "metadata/builders/trakt.html#trakt-chart"),
                    ("Trakt Userlist", "metadata/builders/trakt.html#trakt-userlist"),
                    ("Trakt Recommendations", "metadata/builders/trakt.html#trakt-recommendations"),
                    ("Trakt Box Office", "metadata/builders/trakt.html#trakt-box-office"),
                ]),
                ("_menu", "Tautulli Builders", "metadata/builders/tautulli", [
                    ("Tautulli Popular/Watched", "metadata/builders/tautulli.html#tautulli-popular-watched"),
                ]),
                ("_menu", "Radarr Builders", "metadata/builders/radarr", [
                    ("Radarr All", "metadata/builders/radarr.html#radarr-all"),
                    ("Radarr Taglist", "metadata/builders/radarr.html#radarr-taglist"),
                ]),
                ("_menu", "Sonarr Builders", "metadata/builders/sonarr", [
                    ("Sonarr All", "metadata/builders/sonarr.html#sonarr-all"),
                    ("Sonarr Taglist", "metadata/builders/sonarr.html#sonarr-taglist"),
                ]),
                ("_menu", "MdbList Builders", "metadata/builders/mdblist", [
                    ("MdbList List", "metadata/builders/mdblist.html#mdblist-list"),
                ]),
                ("_menu", "Letterboxd Builders", "metadata/builders/letterboxd", [
                    ("Letterboxd List", "metadata/builders/letterboxd.html#letterboxd-list"),
                ]),
                ("_menu", "ICheckMovies Builders", "metadata/builders/icheckmovies", [
                    ("ICheckMovies List", "metadata/builders/icheckmovies.html#icheckmovies-list"),
                ]),
                ("_menu", "FlixPatrol Builders", "metadata/builders/flixpatrol", [
                    ("FlixPatrol Top Platform", "metadata/builders/flixpatrol.html#flixpatrol-top"),
                    ("FlixPatrol Popular", "metadata/builders/flixpatrol.html#flixpatrol-popular"),
                    ("FlixPatrol demographicURLTop Platform", "metadata/builders/flixpatrol.html#flixpatrol-url"),
                ]),
                ("_menu", "Reciperr Builders", "metadata/builders/reciperr", [
                    ("Reciperr List", "metadata/builders/reciperr.html#reciperr-list"),
                ]),
                ("_menu", "StevenLu Builders", "metadata/builders/stevenlu", [
                    ("StevenLu List", "metadata/builders/stevenlu.html#stevenlu-s-popular-movies-list"),
                ]),
                ("_menu", "AniDB Builders", "metadata/builders/anidb", [
                    ("AniDB ID", "metadata/builders/anidb.html#anidb-id"),
                    ("AniDB Relation", "metadata/builders/anidb.html#anidb-relation"),
                    ("AniDB Popular", "metadata/builders/anidb.html#anidb-popular"),
                    ("AniDB Tag", "metadata/builders/anidb.html#anidb-tag"),
                ]),
                ("_menu", "AniList Builders", "metadata/builders/anilist", [
                    ("AniList Top Rated", "metadata/builders/anilist.html#anilist-top-rated"),
                    ("AniList Anilist Popular", "metadata/builders/anilist.html#anilist-anilist-popular"),
                    ("AniList Trending", "metadata/builders/anilist.html#anilist-trending"),
                    ("AniList Relations", "metadata/builders/anilist.html#anilist-relations"),
                    ("AniList Studio", "metadata/builders/anilist.html#anilist-studio"),
                    ("AniList ID", "metadata/builders/anilist.html#anilist-id"),
                    ("AniList UserList", "metadata/builders/anilist.html#anilist-userlist"),
                    ("AniList Search", "metadata/builders/anilist.html#anilist-search"),
                ]),
                ("_menu", "MyAnimeList Builders", "metadata/builders/myanimelist", [
                    ("MyAnimeList Search", "metadata/builders/myanimelist.html#myanimelist-search"),
                    ("MyAnimeList Top All", "metadata/builders/myanimelist.html#myanimelist-top-all"),
                    ("MyAnimeList Top Airing", "metadata/builders/myanimelist.html#myanimelist-top-airing"),
                    ("MyAnimeList Top Upcoming", "metadata/builders/myanimelist.html#myanimelist-top-upcoming"),
                    ("MyAnimeList Top TV Series", "metadata/builders/myanimelist.html#myanimelist-top-tv-series"),
                    ("MyAnimeList Top Movies", "metadata/builders/myanimelist.html#myanimelist-top-movies"),
                    ("MyAnimeList Top OVA Series", "metadata/builders/myanimelist.html#myanimelist-top-ova-series"),
                    ("MyAnimeList Top Specials", "metadata/builders/myanimelist.html#myanimelist-top-specials"),
                    ("MyAnimeList Most Popular", "metadata/builders/myanimelist.html#myanimelist-most-popular"),
                    ("MyAnimeList Most Favorited", "metadata/builders/myanimelist.html#myanimelist-most-favorited"),
                    ("MyAnimeList Suggested", "metadata/builders/myanimelist.html#myanimelist-suggested"),
                    ("MyAnimeList ID", "metadata/builders/myanimelist.html#myanimelist-id"),
                    ("MyAnimeList UserList", "metadata/builders/myanimelist.html#myanimelist-userlist"),
                    ("MyAnimeList Seasonal", "metadata/builders/myanimelist.html#myanimelist-seasonal"),
                ]),
            ]),
            ("_menu", "Details", "#", [
                ("Setting Details", "metadata/details/setting"),
                ("Schedule Details", "metadata/details/schedule"),
                ("Metadata Details", "metadata/details/metadata"),
                ("Radarr/Sonarr Details", "metadata/details/arr"),
            ])
        ]),
        ("&#10084", "https://github.com/sponsors/meisnate12", True),
    ],

    # Render the next and previous page links in navbar. (Default: true)
    'navbar_sidebarrel': False,

    # Render the current pages TOC in the navbar. (Default: true)
    'navbar_pagenav': False,

    # Tab name for the current pages TOC. (Default: "Page")
    'navbar_pagenav_name': "Sections",

    # Global TOC depth for "site" navbar tab. (Default: 1)
    # Switching to -1 shows all levels.
    'globaltoc_depth': 2,

    # Include hidden TOCs in Site navbar?
    #
    # Note: If this is "false", you cannot have mixed ``:hidden:`` and
    # non-hidden ``toctree`` directives in the same page, or else the build
    # will break.
    #
    # Values: "true" (default) or "false"
    'globaltoc_includehidden': "true",

    # HTML navbar class (Default: "navbar") to attach to <div> element.
    # For black navbar, do "navbar navbar-inverse"
    'navbar_class': "navbar navbar-inverse",

    # Fix navigation bar to top of page?
    # Values: "true" (default) or "false"
    'navbar_fixed_top': "true",

    # Location of link to source.
    # Options are "nav" (default), "footer" or anything else to exclude.
    'source_link_position': "nav",

    # Bootswatch (http://bootswatch.com/) theme.
    #
    # Options are nothing (default) or the name of a valid theme
    # such as "cosmo" or "sandstone".
    #
    # The set of valid themes depend on the version of Bootstrap
    # that's used (the next config option).
    #
    # Currently, the supported themes are:
    # - Bootstrap 2: https://bootswatch.com/2
    # - Bootstrap 3: https://bootswatch.com/3
    'bootswatch_theme': "darkly",

    # Choose Bootstrap version.
    # Values: "3" (default) or "2" (in quotes)
    'bootstrap_version': "3",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["custom.css"]

def setup(app):
    app.add_css_file("custom.css")
