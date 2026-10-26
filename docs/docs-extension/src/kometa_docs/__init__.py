"""Render Kometa includes directly inside Zensical's Markdown pipeline."""

from pathlib import Path

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from zensical.extensions.context import ContextPreprocessor

from ._include.directive import create_include_tag
from ._include.event import Settings, get_file_content
from ._include.files_watcher import FilesWatcher


class IncludeRenderer:
    """Expand the existing syntax against the original source page."""

    def __init__(self, docs_dir=None):
        self.docs_dir = Path(docs_dir if docs_dir is not None else Path.cwd() / "docs").resolve()
        self.watcher = FilesWatcher()

    def render(self, path, content=None):
        path = Path(path).resolve()
        try:
            return get_file_content(
                content if content is not None else path.read_text(encoding="utf-8"),
                str(path),
                str(self.docs_dir),
                {name: create_include_tag("{%", "%}", name) for name in ("include", "include-markdown")},
                {
                    "encoding": "utf-8",
                    "preserve-includer-indent": True,
                    "dedent": False,
                    "trailing-newlines": True,
                    "comments": False,
                    "rewrite-relative-urls": True,
                    "heading-offset": 0,
                    "recursive": True,
                    "start": None,
                    "end": None,
                    "replace": None,
                    "replace-tags": None,
                    "exclude-tags": None,
                    "include-tags": None,
                    "order": "alpha-path",
                },
                Settings(exclude=[], include_from_url=True),
                files_watcher=self.watcher,
            )
        except Exception as exc:
            raise ValueError(f"Include expansion failed in {path}: {exc}") from exc

    @property
    def dependencies(self):
        return {Path(path).resolve() for path in self.watcher.included_files}


class IncludePreprocessor(Preprocessor):
    def run(self, lines):
        content = "\n".join(lines)
        if "{%" not in content:
            return lines
        context = ContextPreprocessor.from_markdown(self.md)
        if context is None:
            raise ValueError("Kometa includes require Zensical's page context")
        docs_dir = Path(context.config["docs_dir"])
        path = Path(context.page.path)
        if not path.is_absolute():
            path = docs_dir / path
        return IncludeRenderer(docs_dir).render(path, content).split("\n")


class IncludeExtension(Extension):
    def extendMarkdown(self, md):
        # Expand before whitespace normalization, fenced blocks, and Snippets,
        # matching the previous before-Markdown preprocessing order.
        md.preprocessors.register(IncludePreprocessor(md), "kometa_include", 110)


def makeExtension(**kwargs):
    return IncludeExtension(**kwargs)
