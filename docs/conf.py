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
    'sphinx_copybutton'
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
html_logo = "pmm.png"
html_favicon = "pmm.png"

html_copy_source = False
html_show_sourcelink = False

# Theme options are theme-specific and customize the look and feel of a
# theme further.

html_theme_options = {
    # Navigation bar title. (Default: ``project`` value)
    #'navbar_title': "Demo",

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
            ("_menu", "Installation", [
                ("Installing Plex Meta Manager", "home/installation"),
                ("_divider", ),
                ("Local Walkthrough", "home/guides/local"),
                ("Docker Walkthrough", "home/guides/docker"),
                ("QNAP Walkthrough", "home/guides/qnap"),
                ("unRAID Walkthrough", "home/guides/unraid"),
                ("Kubernetes Walkthrough", "home/guides/kubernetes"),
                ("Docker images", "home/guides/alternative-docker"),
            ]),
            ("Run Commands & Environment Variables", "home/environmental"),
            ("_divider", ),
            ("Configuration File", "config/configuration"),
            ("Log Files", "home/logs"),
            ("Metadata Files", "metadata/metadata"),
            ("Overlay Files", "metadata/overlay"),
            ("Playlist Files", "metadata/playlist"),
            ("_divider", ),
            ("PMM Default Config Files", "home/guides/defaults"),
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
            ("_divider", ),
            ("Libraries/Playlists", "config/libraries"),
            ("Path Types", "config/paths"),
            ("Operations", "config/operations"),
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
        ("_menu", "Metadata", [
            ("Metadata Files", "metadata/metadata"),
            ("Overlay Files", "metadata/overlay"),
            ("Playlist Files", "metadata/playlist"),
            ("_divider", ),
            ("Templates", "metadata/templates"),
            ("Filters", "metadata/filters"),
            ("Dynamic Collections", "metadata/dynamic"),
            ("_menu", "Editing Media Metadata", [
                ("Editing Movie Metadata", "metadata/metadata/movie"),
                ("Editing TV Metadata", "metadata/metadata/show"),
                ("Editing Music Metadata", "metadata/metadata/music"),
            ]),
            ("_menu", "Metadata Builders", [
                ("Plex Builders", "metadata/builders/plex"),
                ("Smart Builders", "metadata/builders/smart"),
                ("TMDb Builders", "metadata/builders/tmdb"),
                ("TVDb Builders", "metadata/builders/tvdb"),
                ("IMDb Builders", "metadata/builders/imdb"),
                ("Trakt Builders", "metadata/builders/trakt"),
                ("Tautulli Builders", "metadata/builders/tautulli"),
                ("Radarr Builders", "metadata/builders/radarr"),
                ("Sonarr Builders", "metadata/builders/sonarr"),
                ("MdbList Builders", "metadata/builders/mdblist"),
                ("Letterboxd Builders", "metadata/builders/letterboxd"),
                ("ICheckMovies Builders", "metadata/builders/icheckmovies"),
                ("FlixPatrol Builders", "metadata/builders/flixpatrol"),
                ("Reciperr Builders", "metadata/builders/reciperr"),
                ("StevenLu Builders", "metadata/builders/stevenlu"),
                ("AniDB Builders", "metadata/builders/anidb"),
                ("AniList Builders", "metadata/builders/anilist"),
                ("MyAnimeList Builders", "metadata/builders/myanimelist"),
            ]),
            ("_menu", "Details", [
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
