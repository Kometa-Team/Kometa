# Adapted from the Kometa include-markdown fork; see LICENSE and NOTICE in docs/docs-extension.
"""Utilities for string processing."""

from __future__ import annotations

import functools
import io
import os
import re
import stat
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from kometa_docs._include.cache import Cache
    from kometa_docs._include.directive import OrderOption


# Markdown regular expressions. Taken from the original Markdown.pl by John
# Gruber, and modified to work in Python

# Matches markdown links.
# e.g. [scikit-learn](https://github.com/scikit-learn/scikit-learn)
#
# The next Regex can raise a catastrophic backtracking, but with the current
# implementation of the plugin it is not very much likely to reach the case.
# Can be checked with dlint:
# python3 -m dlint.redos --pattern '\[(?:(?:\[[^\[\]]+\])*)?\]'
#
# In the original Markdown.pl, the nested brackets are enclosed by an atomic
# group (?>...), but atomic groups are not supported by Python in versions
# previous to Python3.11. Also, these nested brackets can be recursive in the
# Perl implementation but this doesn't seem possible in Python, the current
# implementation only reaches two levels.
MARKDOWN_LINK_REGEX = re.compile(
    r"""
        (                 # wrap whole match in $1
          (?<!!)          # don't match images - negative lookbehind
          \[
            (             # link text = $2
                (?:
                    [^\[\]]+  # not bracket
                    (?:
                        \[[^\[\]]+\]  # another level of nested bracket
                                      # with something inside
                        [^\[\]]*      # not bracket
                    )*
                )?        # allow for empty link text
            )
          \]
          \(             # literal paren
            \s*
            <?(.*?)>?    # href = $3
            \s*
            (            # $4
              (['"])     # quote char = $5
              (.*?)      # Title = $6
              \5         # matching quote
            )?           # title is optional
          \)
        )
    """,
    flags=re.VERBOSE,
)

# Matches markdown inline images.
# e.g. ![alt-text](path/to/image.png)
MARKDOWN_IMAGE_REGEX = re.compile(
    r"""
        (                # wrap whole match in $1
          !\[
            (.*?)        # alt text = $2
          \]
          \(             # literal paren
            [ \t]*
            <?(\S+?)>?   # src url = $3
            [ \t]*
            (            # $4
              (['"])     # quote char = $5
              (.*?)      # title = $6
              \5         # matching quote
              [ \t]*
            )?           # title is optional
          \)
        )
    """,
    flags=re.VERBOSE,
)

# Matches markdown link definitions.
# e.g. [scikit-learn]: https://github.com/scikit-learn/scikit-learn
MARKDOWN_LINK_DEFINITION_REGEX = re.compile(
    r"""
        ^[ ]{0,4}\[(.+)\]:   # id = $1
        [ \t]*
        \n?                # maybe *one* newline
        [ \t]*
        <?(\S+?)>?           # url = $2
        [ \t]*
        \n?                # maybe one newline
        [ \t]*
        (?:
            (?<=\s)          # lookbehind for whitespace
            ["(]
            (.+?)            # title = $3
            [")]
            [ \t]*
        )?                   # title is optional
        (?:\n+|\Z)
    """,
    flags=re.VERBOSE | re.MULTILINE,
)

# Matched html image and source definition.
# e.g. <img src="path/to/image.png" alt="alt-text">
# e.g. <source src="path/to/image.png" alt="alt-text">
MARKDOWN_HTML_IMAGE_REGEX = re.compile(
    r"""
        <(?:img|source)    # img or source
        (?:\s+             # More than one whitespace
            (?!src=)       # Not src=
            [\w-]+         # attribute name
            (?:\s*=\s*)?   # arbitrary whitespace (optional)
            (?:
                "[^"]*"    # Quoted value (double quote)
                |
                '[^']*'    # Quoted value (single quote)
            )?
        )*                 # Other attributes are repeated 0 or more times
        \s+                # More than one whitespace
        src=["'](\S+?)["'] # src = $1 (double quote or single quote)
    """,
    flags=re.VERBOSE | re.MULTILINE,
)

# Matched html anchor definition.
# e.g. <a href="https://example.com">example</a>
MARKDOWN_HTML_ANCHOR_DEFINITION_REGEX = re.compile(
    r"""
        <a
        (?:\s+             # More than one whitespace
            (?!href=)      # Not href=
            [\w-]+         # attribute name
            (?:\s*=\s*)?   # arbitrary whitespace (optional)
            (?:
                "[^"]*"    # Quoted value (double quote)
                |
                '[^']*'    # Quoted value (single quote)
            )?
        )*                 # Other attributes are repeated 0 or more times
        \s+                # More than one whitespace
        href=["'](\S+?)["']# href = $1 (double quote or single quote)
    """,
    flags=re.VERBOSE | re.MULTILINE,
)


def transform_p_by_p_skipping_codeblocks(  # noqa: PLR0912, PLR0915
    markdown: str,
    func: Callable[[str], str],
) -> str:
    """Apply a transformation paragraph by paragraph in a Markdown text.

    Apply a transformation paragraph by paragraph in a Markdown using a
    function. Skip indented and fenced codeblock lines, where the
    transformation is never applied.
    """
    # current fenced codeblock delimiter
    _current_fcodeblock_delimiter = ""

    # inside indented codeblock
    _maybe_icodeblock_lines: list[str] = []
    _previous_line_was_empty = False

    lines = []
    current_paragraph_lines: list[str] = []

    def process_current_paragraph() -> None:
        lines.extend(
            func(
                "".join(current_paragraph_lines),
            ).splitlines(keepends=True)
        )

    # The next implementation takes into account that indented code
    # blocks must be surrounded by newlines as per the CommonMark
    # specification. See https://spec.commonmark.org/0.28/#indented-code-blocks
    #
    # However, note that ambiguities with list items are not handled.

    for line in io.StringIO(markdown):
        if not _current_fcodeblock_delimiter:
            lstripped_line = line.lstrip()
            if lstripped_line.startswith(("```", "~~~")):
                _current_fcodeblock_delimiter = lstripped_line[:3]
                process_current_paragraph()
                current_paragraph_lines = []
                lines.append(line)
            elif line.startswith("    "):
                if not lstripped_line or _maybe_icodeblock_lines:
                    # maybe enter indented codeblock
                    _maybe_icodeblock_lines.append(line)
                else:
                    current_paragraph_lines.append(line)
            elif _maybe_icodeblock_lines:
                process_current_paragraph()
                current_paragraph_lines = []
                if not _previous_line_was_empty:
                    # wasn't an indented code block
                    current_paragraph_lines.extend(_maybe_icodeblock_lines)
                    _maybe_icodeblock_lines = []
                    current_paragraph_lines.append(line)
                    process_current_paragraph()
                    current_paragraph_lines = []
                else:
                    # exit indented codeblock
                    for line_ in _maybe_icodeblock_lines:
                        lines.append(line_)
                    _maybe_icodeblock_lines = []
                    lines.append(line)
            else:
                current_paragraph_lines.append(line)
            _previous_line_was_empty = not lstripped_line
        else:
            lines.append(line)
            lstripped_line = line.lstrip()
            if lstripped_line.startswith(_current_fcodeblock_delimiter):
                _current_fcodeblock_delimiter = ""
            _previous_line_was_empty = not lstripped_line

    if _maybe_icodeblock_lines:
        if not _previous_line_was_empty:
            # at EOF
            process_current_paragraph()
            current_paragraph_lines = []
            current_paragraph_lines.extend(_maybe_icodeblock_lines)
            process_current_paragraph()
            current_paragraph_lines = []
        else:
            process_current_paragraph()
            current_paragraph_lines = []
            for line_ in _maybe_icodeblock_lines:
                lines.append(line_)
    else:
        process_current_paragraph()

    return "".join(lines)


def transform_line_by_line_skipping_codeblocks(
    markdown: str,
    func: Callable[[str], str],
) -> str:
    """Apply a transformation line by line in a Markdown text using a function,.

    Skip fenced codeblock lines and empty lines, where the transformation
    is never applied.

    Indented codeblocks are not taken into account because in the practice
    this function is only used for transformations of heading prefixes. See
    the PR https://github.com/mondeja/mkdocs-include-markdown-plugin/pull/95
    to recover the implementation handling indented codeblocks.
    """
    # current fenced codeblock delimiter
    _current_fcodeblock_delimiter = ""

    lines = []
    for line in io.StringIO(markdown):
        lstripped_line = line.lstrip()
        if not _current_fcodeblock_delimiter:
            if lstripped_line.startswith("```"):
                _current_fcodeblock_delimiter = "```"
            elif lstripped_line.startswith("~~~"):
                _current_fcodeblock_delimiter = "~~~"
            else:
                line = func(line)  # noqa: PLW2901
        elif lstripped_line.startswith(_current_fcodeblock_delimiter):
            _current_fcodeblock_delimiter = ""
        lines.append(line)

    return "".join(lines)


def rewrite_relative_urls(
    markdown: str,
    source_path: str,
    destination_path: str,
) -> str:
    """Rewrite relative URLs in a Markdown text.

    Rewrites markdown so that relative links that were written at
    ``source_path`` will still work when inserted into a file at
    ``destination_path``.
    """

    def rewrite_url(url: str) -> str:
        if is_url(url) or is_absolute_path(url) or is_anchor(url):
            return url

        new_path = os.path.relpath(
            os.path.join(os.path.dirname(source_path), url),
            os.path.dirname(destination_path),
        )

        # ensure forward slashes are used, on Windows
        new_path = new_path.replace("\\", "/").replace("//", "/")

        try:
            if url[-1] == "/":
                # the above operation removes a trailing slash,
                # so add it back if it was present in the input
                new_path += "/"
        except IndexError:  # pragma: no cover
            pass

        return new_path

    def found_href(m: re.Match[str], url_group_index: int = -1) -> str:
        match_start, match_end = m.span(0)
        href = m[url_group_index]
        href_start, href_end = m.span(url_group_index)
        rewritten_url = rewrite_url(href)
        return m.string[match_start:href_start] + rewritten_url + m.string[href_end:match_end]

    found_href_url_group_index_3 = functools.partial(
        found_href,
        url_group_index=3,
    )

    def transform(paragraph: str) -> str:
        paragraph = MARKDOWN_LINK_REGEX.sub(
            found_href_url_group_index_3,
            paragraph,
        )
        paragraph = MARKDOWN_IMAGE_REGEX.sub(
            found_href_url_group_index_3,
            paragraph,
        )
        paragraph = MARKDOWN_LINK_DEFINITION_REGEX.sub(
            functools.partial(found_href, url_group_index=2),
            paragraph,
        )
        paragraph = MARKDOWN_HTML_IMAGE_REGEX.sub(
            functools.partial(found_href, url_group_index=1),
            paragraph,
        )
        return MARKDOWN_HTML_ANCHOR_DEFINITION_REGEX.sub(
            functools.partial(found_href, url_group_index=1),
            paragraph,
        )

    return transform_p_by_p_skipping_codeblocks(
        markdown,
        transform,
    )


def interpret_escapes(value: str) -> str:
    """Interpret Python literal escapes in a string.

    Replaces any standard escape sequences in value with their usual
    meanings as in ordinary Python string literals.
    """
    return value.encode("latin-1", "backslashreplace").decode("unicode_escape")


def filter_inclusions(  # noqa: PLR0912
    start: str | None,
    end: str | None,
    text_to_include: str,
) -> tuple[str, bool, bool]:
    """Filter inclusions in a text.

    Manages inclusions from files using ``start`` and ``end`` directive
    arguments.
    """
    expected_start_not_found, expected_end_not_found = (False, False)
    new_text_to_include = ""

    if start is not None and end is None:
        start = interpret_escapes(start)
        if start not in text_to_include:
            expected_start_not_found = True
        else:
            new_text_to_include = text_to_include.split(
                start,
                maxsplit=1,
            )[1]
    elif start is None and end is not None:
        end = interpret_escapes(end)
        if end not in text_to_include:
            expected_end_not_found = True
            new_text_to_include = text_to_include
        else:
            new_text_to_include = text_to_include.split(
                end,
                maxsplit=1,
            )[0]
    elif start is not None and end is not None:
        start, end = interpret_escapes(start), interpret_escapes(end)
        if start not in text_to_include:
            expected_start_not_found = True
        if end not in text_to_include:
            expected_end_not_found = True

        start_split = text_to_include.split(start)
        text_parts = start_split[1:] if len(start_split) > 1 else [text_to_include]

        for start_text in text_parts:
            for i, end_text in enumerate(start_text.split(end)):
                if not i % 2:
                    new_text_to_include += end_text
    else:  # pragma: no cover
        new_text_to_include = text_to_include

    return (
        new_text_to_include,
        expected_start_not_found,
        expected_end_not_found,
    )


def _transform_negative_offset_func_factory(
    offset: int,
) -> Callable[[str], str]:
    abs_offset = abs(offset)

    def transform(line: str) -> str:
        try:
            if line[0] != "#":
                return line
        except IndexError:  # pragma: no cover
            # Note for pragma: all lines include a newline
            # so this exception is never raised in tests.
            return line
        stripped_line = line.lstrip("#")
        new_n_headings = max(len(line) - len(stripped_line) - abs_offset, 1)
        return "#" * new_n_headings + stripped_line

    return transform


def _transform_positive_offset_func_factory(
    offset: int,
) -> Callable[[str], str]:
    heading_prefix = "#" * offset

    def transform(line: str) -> str:
        try:
            if line[0] != "#":
                return line
        except IndexError:  # pragma: no cover
            return line
        return heading_prefix + line

    return transform


def increase_headings_offset(markdown: str, offset: int = 0) -> str:
    """Increases the headings depth of a snippet of Makdown content."""
    if not offset:  # pragma: no cover
        return markdown
    return transform_line_by_line_skipping_codeblocks(
        markdown,
        _transform_positive_offset_func_factory(offset) if offset > 0 else _transform_negative_offset_func_factory(offset),
    )


def rstrip_trailing_newlines(content: str) -> str:
    """Removes trailing newlines from a string."""
    while content.endswith(("\n", "\r")):
        content = content.rstrip("\r\n")
    return content


def replace_text(content: str, replacements: dict):
    for old_text, new_text in replacements.items():
        content = content.replace(old_text, new_text)
    return content


def replace_tags(content: str, replacements: dict):
    for tag, new_text in replacements.items():
        content = re.sub(rf"<!--{tag}-->.*?<!--{tag}-->", new_text, content, flags=re.DOTALL)
    return content


def exclude_tags(content: str, exclude_list: list):
    for exclude in exclude_list:
        content = re.sub(rf"<!--{exclude}-->.*?<!--{exclude}-->", "", content, flags=re.DOTALL)
    return content


def include_tags(content: str, include_list: list):
    final_content = ""
    while "<!--" in content:
        result = re.search(r"(<!--.*?-->)(.*)", content, flags=re.DOTALL)
        end = result.group(1)
        content = result.group(2)
        result = re.search(rf"(.*?){end}(.*)", content, flags=re.DOTALL)
        if not result:
            continue
        include = result.group(1)
        content = result.group(2)
        if end[4:-3] in include_list:
            if final_content:
                final_content += "\n"
            final_content += include.removeprefix("\n").removesuffix("\n")
    return final_content


def filter_paths(
    filepaths: Iterator[str] | list[str],
    ignore_paths: list[str],
) -> list[str]:
    """Filters a list of paths removing those defined in other list of paths.

    The paths to filter can be defined in the list of paths to ignore in
    several forms:

    - The same string.
    - Only the file name.
    - Only their direct directory name.
    - Their direct directory full path.

    Args:
        filepaths (list): Set of source paths to filter.
        ignore_paths (list): Paths that are ignored.

    Returns:
        list: Non filtered paths ordered alphabetically.
    """
    result = []
    for filepath in filepaths:
        # ignore by filepath
        if filepath in ignore_paths:
            continue

        # ignore by dirpath (relative or absolute)
        fp_split = filepath.split(os.sep)
        fp_split.pop()
        if (os.sep).join(fp_split) in ignore_paths:
            continue

        # ignore if is a directory
        try:
            if not stat.S_ISDIR(os.stat(filepath).st_mode):
                result.append(filepath)
        except (FileNotFoundError, OSError):  # pragma: no cover
            continue
    return result


def natural_sort_key(s: str) -> list[Any]:
    """Key function for natural sorting of strings."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)]


def sort_paths(paths: list[str], order: OrderOption) -> list[str]:
    """Sort a list of paths in-place according to an order option."""
    ascending, order_type, order_by = order

    if order_type == "random":
        import random  # noqa: PLC0415

        random.shuffle(paths)
        return paths

    key = None
    if order_type == "alpha":
        if order_by == "name":

            def key(p: str) -> str:  # noqa: F811 - selects the key for this ordering mode
                return os.path.basename(p)

        elif order_by == "extension":

            def key(p: str) -> str:
                return os.path.splitext(p)[1]

    elif order_type == "natural":
        if order_by == "extension":

            def key(p: str) -> tuple:  # type: ignore
                return (
                    natural_sort_key(os.path.splitext(p)[1]),
                    natural_sort_key(os.path.basename(p)),
                )

        elif order_by == "name":

            def key(p: str) -> str:
                return natural_sort_key(os.path.basename(p))  # type: ignore

        else:
            key = natural_sort_key  # type: ignore
    elif order_type == "size":

        def key(p: str) -> int:  # type: ignore
            return os.path.getsize(p)

        ascending = not ascending  # larger files first
    elif order_type == "mtime":

        def key(p: str) -> float:  # type: ignore
            return os.path.getmtime(p)

    elif order_type == "ctime":

        def key(p: str) -> float:  # type: ignore
            return os.path.getctime(p)

    elif order_type == "atime":

        def key(p: str) -> float:  # type: ignore
            return os.path.getatime(p)

    paths.sort(key=key, reverse=ascending)
    return paths


def _is_valid_url_scheme_char(c: str) -> bool:
    """Determine is a character is a valid URL scheme character.

    Valid characters are:

    ```
    abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-.
    ```
    """
    codepoint = ord(c)
    A = 65
    Z = 90
    a = 97
    z = 122
    zero = 48
    nine = 57
    dot = 46
    plus = 43
    minus = 45
    return A <= codepoint <= Z or a <= codepoint <= z or zero <= codepoint <= nine or codepoint in (plus, minus, dot)


def is_url(string: str) -> bool:
    """Determine if a string is an URL.

    The implementation has been adapted from `urllib.urlparse`.
    """
    i = string.find(":")
    if i <= 1:  # noqa: PLR2004 -> exclude C: or D: on Windows
        return False

    try:
        return all(_is_valid_url_scheme_char(string[j]) for j in range(i))
    except (IndexError, ValueError):  # pragma: no cover
        return False


def is_relative_path(string: str) -> bool:
    """Check if a string looks like a relative path."""
    try:
        return string[0] == "." and (string[1] == "/" or (string[1] == "." and string[2] == "/"))
    except IndexError:  # pragma: no cover
        return False


def is_absolute_path(string: str) -> bool:
    """Check if a string looks like an absolute path."""
    try:
        return string[0] == "/" or string[0] == os.sep
    except IndexError:  # pragma: no cover
        return False


def is_anchor(string: str) -> bool:
    """Check if a string looks like an anchor.

    An anchor is a string that starts with `#` and is not a relative path.
    """
    try:
        return string[0] == "#"
    except IndexError:  # pragma: no cover
        return False


def read_file(file_path: str, encoding: str) -> str:
    """Read a file and return its content."""
    f = open(file_path, encoding=encoding)  # noqa: SIM115
    content = f.read()
    f.close()
    return content


def read_url(
    url: str,
    http_cache: Cache | None,
    encoding: str = "utf-8",
) -> Any:
    """Read an HTTP location and return its content."""
    from urllib.request import Request, urlopen  # noqa: PLC0415

    if http_cache is not None:
        cached_content = http_cache.get_(url, encoding)
        if cached_content is not None:
            return cached_content
    with urlopen(Request(url)) as response:
        content = response.read().decode(encoding)
    if http_cache is not None:
        http_cache.set_(url, content, encoding)
    return content


def safe_os_path_relpath(path: str, start: str) -> str:
    """Return the relative path of a file from a start directory.

    Safe version of `os.path.relpath` that catches possible `ValueError`
    exceptions and returns the original path in case of error.
    On Windows, `ValueError` is raised when `path` and `start` are on
    different drives.
    """
    try:
        return os.path.relpath(path, start)
    except ValueError:  # pragma: no cover
        return path


def file_lineno_message(
    page_src_path: str | None,
    docs_dir: str,
    lineno: int,
) -> str:
    """Return a message with the file path and line number."""
    if page_src_path is None:  # pragma: no cover
        return f"generated page content (line {lineno})"
    return f"{safe_os_path_relpath(page_src_path, docs_dir)}" f":{lineno}"


def lineno_from_content_start(content: str, start: int) -> int:
    """Return the line number of the first line of ``start`` in ``content``."""
    return content[:start].count("\n") + 1
