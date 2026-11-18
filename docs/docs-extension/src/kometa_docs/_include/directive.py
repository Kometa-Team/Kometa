# Adapted from the Kometa include-markdown fork; see LICENSE and NOTICE in docs/docs-extension.
"""Utilities related with the syntax of directives."""

from __future__ import annotations

import functools
import os
import re
import stat
import string
from dataclasses import dataclass
from typing import TYPE_CHECKING

from kometa_docs._include.logger import logger
from kometa_docs._include.process import (
    file_lineno_message,
    filter_paths,
    is_absolute_path,
    is_relative_path,
    is_url,
    sort_paths,
)
from wcmatch import glob

from .errors import IncludeError as PluginError


@dataclass
class DirectiveBoolArgument:  # noqa: D101
    value: bool
    regex: Callable[[], re.Pattern[str]]


if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable
    from typing import Callable, Literal, TypedDict

    DirectiveBoolArgumentsDict = dict[str, DirectiveBoolArgument]
    OrderOption = tuple[bool, str, str]

    DefaultValues = TypedDict(
        "DefaultValues",
        {
            "encoding": str,
            "preserve-includer-indent": bool,
            "dedent": bool,
            "trailing-newlines": bool,
            "comments": bool,
            "rewrite-relative-urls": bool,
            "heading-offset": int,
            "recursive": bool,
            "start": str | None,
            "end": str | None,
            "replace": dict | None,
            "replace-tags": dict | None,
            "exclude-tags": list | None,
            "include-tags": list | None,
            "order": str,
        },
    )


GLOB_FLAGS = glob.NEGATE | glob.EXTGLOB | glob.GLOBSTAR | glob.BRACE
RE_ESCAPED_PUNCTUATION = re.escape(string.punctuation)

DOUBLE_QUOTED_STR_RE = r'([^"]|(?<=\\)")+'
SINGLE_QUOTED_STR_RE = r"([^']|(?<=\\)')+"

# In the following regular expression, the substrings "\{%", "%\}"
# will be replaced by custom opening and closing tags in the `on_config`
# plugin event if required.
INCLUDE_TAG_RE = (
    r"""
    (?P<_includer_indent>[ \t\w\\.]*?)\{%
    \s*
    include
    \s+
    (?:"(?P<double_quoted_filename>"""
    + DOUBLE_QUOTED_STR_RE
    + r""")")?(?:'(?P<single_quoted_filename>"""
    + SINGLE_QUOTED_STR_RE
    + r""")')?
    (?P<arguments>.*?)
    \s*
    %\}
"""
)  # noqa: E501

TRUE_FALSE_STR_BOOL = {
    "true": True,
    "false": False,
}

TRUE_FALSE_BOOL_STR = {
    True: "true",
    False: "false",
}


@functools.lru_cache
def arg(arg: str) -> re.Pattern[str]:
    """Return a compiled regexp to match a boolean argument."""
    return re.compile(rf"{arg}=([{RE_ESCAPED_PUNCTUATION}\w]*)")


@functools.lru_cache
def str_arg(arg: str) -> re.Pattern[str]:
    """Return a compiled regexp to match a string argument."""
    return re.compile(
        rf'{arg}=(?:"({DOUBLE_QUOTED_STR_RE})")?' rf"(?:'({SINGLE_QUOTED_STR_RE})')?",
    )


ARGUMENT_REGEXES = {
    # str
    "start": functools.partial(str_arg, "start"),
    "end": functools.partial(str_arg, "end"),
    "exclude": functools.partial(str_arg, "exclude"),
    "encoding": functools.partial(str_arg, "encoding"),
    "replace": functools.partial(str_arg, "replace"),
    "replace-tags": functools.partial(str_arg, "replace-tags"),
    "exclude-tags": functools.partial(str_arg, "exclude-tags"),
    "include-tags": functools.partial(str_arg, "include-tags"),
    "order": functools.partial(str_arg, "order"),
    # bool
    "comments": functools.partial(arg, "comments"),
    "preserve-includer-indent": functools.partial(
        arg,
        "preserve-includer-indent",
    ),
    "dedent": functools.partial(arg, "dedent"),
    "trailing-newlines": functools.partial(arg, "trailing-newlines"),
    "rewrite-relative-urls": functools.partial(arg, "rewrite-relative-urls"),
    "recursive": functools.partial(arg, "recursive"),
    # int
    "heading-offset": functools.partial(arg, "heading-offset"),
}

INCLUDE_MARKDOWN_DIRECTIVE_ARGS = set(ARGUMENT_REGEXES)
INCLUDE_DIRECTIVE_ARGS = {
    key
    for key in ARGUMENT_REGEXES
    if key
    not in (
        "rewrite-relative-urls",
        "heading-offset",
        "comments",
    )
}

WARN_INVALID_DIRECTIVE_ARGS_REGEX = re.compile(
    rf"[\w-]*=[{RE_ESCAPED_PUNCTUATION}\w]*",
)


def _maybe_arguments_iter(arguments_string: str) -> Iterable[str]:
    """Iterate over parts of the string that look like arguments."""
    current_string_opening = ""  # can be either `'` or `"`
    inside_string = False
    escaping = False
    opening_argument = False  # whether we are at the beginning of an argument
    current_value: list[str] = []

    for c in arguments_string:
        if inside_string:
            if c == "\\":
                escaping = not escaping
                continue
            elif c == current_string_opening and not escaping:
                inside_string = False
                current_string_opening = ""
            else:
                escaping = False
        elif c == "=":
            current_value_str = "".join(current_value)
            new_current_value = ""
            for ch in reversed(current_value_str):
                if ch in string.whitespace:
                    current_value_str = new_current_value[::-1]
                    break
                new_current_value += ch
            yield current_value_str
            current_value = []
            opening_argument = True
        elif opening_argument:
            opening_argument = False
            if c in ('"', "'"):
                current_string_opening = c
                inside_string = True
                current_value.append(c)
                current_value.append(c)
        else:
            current_value.append(c)


def warn_invalid_directive_arguments(
    arguments_string: str,
    directive_lineno: Callable[[], int],
    directive: Literal["include", "include-markdown"],
    page_src_path: str | None,
    docs_dir: str,
) -> list[str]:
    """Warns about the invalid arguments passed to a directive."""
    used_arguments = []
    valid_args = INCLUDE_DIRECTIVE_ARGS if directive == "include" else INCLUDE_MARKDOWN_DIRECTIVE_ARGS
    for maybe_arg in _maybe_arguments_iter(arguments_string):
        if maybe_arg not in valid_args:
            location = file_lineno_message(
                page_src_path,
                docs_dir,
                directive_lineno(),
            )
            logger.warning(
                f"Invalid argument '{maybe_arg}' in" f" '{directive}' directive at {location}. Ignoring...",
            )
        else:
            used_arguments.append(maybe_arg)
    return used_arguments


def parse_filename_argument(
    match: re.Match[str],
) -> tuple[str | None, str | None]:
    """Return filename argument matched by ``match``."""
    raw_filename = match["double_quoted_filename"]
    if raw_filename is None:
        raw_filename = match["single_quoted_filename"]
        if raw_filename is None:
            filename = None
        else:
            filename = raw_filename.replace(r"\'", "'")
    else:
        filename = raw_filename.replace(r"\"", '"')
    return filename, raw_filename


def parse_string_argument(match: re.Match[str] | None) -> str | None:
    """Return the string argument matched by ``match``."""
    if match is None:  # pragma: no cover
        return None
    value = match[1]
    if value is None:
        value = match[3]
        if value is not None:
            value = value.replace(r"\'", "'")
    else:
        value = value.replace(r"\"", '"')
    return value


def create_include_tag(
    opening_tag: str,
    closing_tag: str,
    tag: str,
) -> re.Pattern[str]:
    """Create a regex pattern to match an inclusion tag directive.

    Replaces the substrings '$OPENING_TAG' and '$CLOSING_TAG' from
    INCLUDE_TAG_RE by the effective tag.
    """
    pattern = INCLUDE_TAG_RE
    if tag != "include":
        pattern = pattern.replace(
            " include",
            (" include-markdown" if tag == "include-markdown" else f" {re.escape(tag)}"),
            1,
        )

    if opening_tag != "{%":
        pattern = pattern.replace(r"\{%", re.escape(opening_tag), 1)

    if closing_tag != "%}":
        pattern = pattern.replace(r"%\}", re.escape(closing_tag), 1)

    return re.compile(pattern, flags=re.VERBOSE | re.DOTALL)


def parse_bool_options(
    option_names: list[str],
    defaults: DefaultValues,
    arguments_string: str,
    used_arguments: list[str],
) -> tuple[DirectiveBoolArgumentsDict, list[str]]:
    """Parse boolean options from arguments string."""
    invalid_args: list[str] = []

    bool_options: dict[str, DirectiveBoolArgument] = {}
    for option_name in option_names:
        bool_options[option_name] = DirectiveBoolArgument(
            value=defaults[option_name],  # type: ignore
            regex=ARGUMENT_REGEXES[option_name],
        )

    for arg_name, arg in bool_options.items():
        if arg_name not in used_arguments:
            continue
        bool_arg_match = arg.regex().search(arguments_string)
        try:
            bool_options[arg_name].value = TRUE_FALSE_STR_BOOL[(bool_arg_match and bool_arg_match[1]) or TRUE_FALSE_BOOL_STR[arg.value]]
        except KeyError:
            invalid_args.append(arg_name)
    return bool_options, invalid_args


def resolve_file_paths_to_include(  # noqa: PLR0912
    include_string: str,
    includer_page_src_path: str | None,
    docs_dir: str,
    ignore_paths: list[str],
    order: str,
) -> tuple[list[str], bool]:
    """Resolve the file paths to include for a directive."""
    if is_url(include_string):
        return [include_string], True

    if is_absolute_path(include_string):
        if os.name == "nt":  # pragma: no cover
            # Windows
            fpath = os.path.normpath(include_string)
            try:
                is_file = stat.S_ISREG(os.stat(fpath).st_mode)
            except (FileNotFoundError, OSError):
                is_file = False
            if not is_file:
                return [], False

            paths = filter_paths([fpath], ignore_paths)
            is_url_ = False
            return sort_paths(paths, parse_order_option(order)), is_url_

        try:
            is_file = stat.S_ISREG(os.stat(include_string).st_mode)
        except (FileNotFoundError, OSError):
            is_file = False
        paths = filter_paths(
            (
                [include_string]
                if is_file
                else glob.iglob(
                    include_string,
                    flags=GLOB_FLAGS,
                )
            ),
            ignore_paths,
        )
        is_url_ = False
        sort_paths(paths, parse_order_option(order))
        return paths, is_url_

    if is_relative_path(include_string):
        if includer_page_src_path is None:  # pragma: no cover
            raise PluginError(
                "Relative paths are not allowed when the includer page" " source path is not provided. The include string" f" '{include_string}' is located inside a generated page.",
            )
        root_dir = os.path.abspath(
            os.path.dirname(includer_page_src_path),
        )
        paths = []
        include_path = os.path.join(root_dir, include_string)
        try:
            is_file = stat.S_ISREG(os.stat(include_path).st_mode)
        except (FileNotFoundError, OSError):
            is_file = False
        if is_file:
            paths.append(include_path)
        else:
            for fp in glob.iglob(
                include_string,
                flags=GLOB_FLAGS,
                root_dir=root_dir,
            ):
                paths.append(os.path.join(root_dir, fp))
        paths = filter_paths(paths, ignore_paths)
        is_url_ = False
        sort_paths(paths, parse_order_option(order))
        return paths, is_url_

    # relative to docs_dir
    paths = []
    root_dir = docs_dir
    include_path = os.path.join(root_dir, include_string)
    try:
        is_file = stat.S_ISREG(os.stat(include_path).st_mode)
    except (FileNotFoundError, OSError):
        is_file = False
    if is_file:
        paths.append(include_path)
    else:
        for fp in glob.iglob(
            include_string,
            flags=GLOB_FLAGS,
            root_dir=root_dir,
        ):
            paths.append(os.path.join(root_dir, fp))
    paths = filter_paths(paths, ignore_paths)
    is_url_ = False
    sort_paths(paths, parse_order_option(order))
    return paths, is_url_


def resolve_file_paths_to_exclude(
    exclude_string: str,
    includer_page_src_path: str | None,
    docs_dir: str,
) -> list[str]:
    """Resolve the file paths to exclude for a directive."""
    if is_absolute_path(exclude_string):
        return glob.glob(exclude_string, flags=GLOB_FLAGS)

    if is_relative_path(exclude_string):
        if includer_page_src_path is None:  # pragma: no cover
            raise PluginError(
                "Relative paths are not allowed when the includer page" " source path is not provided. The exclude string" f" '{exclude_string}' is located inside a generated page.",
            )
        root_dir = os.path.abspath(
            os.path.dirname(includer_page_src_path),
        )
        return [
            os.path.normpath(
                os.path.join(root_dir, fp),
            )
            for fp in glob.glob(
                exclude_string,
                flags=GLOB_FLAGS,
                root_dir=root_dir,
            )
        ]

    return glob.glob(  # pragma: no cover
        exclude_string,
        flags=GLOB_FLAGS,
        root_dir=docs_dir,
    )


def validate_order_option(
    order: str,
    page_src_path: str | None,
    docs_dir: str,
    directive_lineno: Callable[[], int],
    directive: str,
) -> None:
    """Validate the 'order' option."""
    regex = get_order_option_regex()
    match = regex.match(order)
    if not match:
        location = file_lineno_message(
            page_src_path,
            docs_dir,
            directive_lineno(),
        )
        raise PluginError(
            f"Invalid value '{order}' for the 'order' argument in" f" '{directive}' directive at {location}. The argument" " 'order' must be a string that matches the regex" f" '{regex.pattern}'.",
        )


@functools.cache
def get_order_option_regex() -> re.Pattern[str]:
    """Return the compiled regex to validate the 'order' option."""
    return re.compile(
        r"^-?" r"(?:" r"(?:alpha|natural)?(?:-?(?:path|name|extension))?" r"|system|random|size|mtime|ctime|atime" r")?$",
    )


def parse_order_option(order: str) -> OrderOption:
    """Parse the 'order' option into a tuple."""
    ascending = False
    order_type = "alpha"
    order_by = "path"
    if order.startswith("-"):
        ascending = True
        order = order[1:]
    order_split = order.split("-", 1)
    if len(order_split) == 2:  # noqa: PLR2004
        order_type, order_by = order_split
    elif order_split[0] in (
        "alpha",
        "random",
        "natural",
        "system",
        "size",
        "mtime",
        "ctime",
        "atime",
    ):
        order_type = order_split[0]
    elif order_split[0] in ("name", "path", "extension"):
        order_by = order_split[0]
    return ascending, order_type, order_by
