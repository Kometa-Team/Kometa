# Kometa documentation includes

This Python Markdown extension expands shared content directly in Zensical.
Its package directory, `docs/docs-extension/`, is excluded from the published site.
Install it from the repository root with `python -m pip install -r docs/requirements.txt`,
then run `python -m zensical serve` or `python -m zensical build --clean`.

`src/kometa_docs/__init__.py` integrates with Zensical's page context. The
`_include/` package provides include processing; its license and provenance are
in LICENSE and NOTICE. No MkDocs package or staging wrapper is used.

The `include` and `include-markdown` directives support replacements, tag selection,
start/end delimiters, nested includes, relative links, indentation, encodings,
and URL downloads. Missing sources and invalid directives fail with the original
page path. Remote content is fetched during builds and requires network access.

Local shared sources live in `docs/templates/`, excluded from publication.
Native watch entries cover templates and extension sources. Restart the development
server after changing extension code.

Do not enable Zensical's built-in include-markdown plugin alongside this extension:
its syntax does not support all the options these docs use. PyMdown Snippets
remains enabled separately.

Run the documentation tests and a clean build from the root README when changing
the extension. Zensical's context API is version-sensitive; validate upgrades
before changing its pinned version.
