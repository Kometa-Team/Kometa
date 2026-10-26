# Adapted from the Kometa include-markdown fork; see LICENSE and NOTICE in docs/docs-extension.
"""Recursive expansion of Kometa's existing include directives."""

from __future__ import annotations

import functools
import html
import json
import os
import re
import textwrap
from dataclasses import dataclass
from typing import TYPE_CHECKING

from kometa_docs._include import process
from kometa_docs._include.cache import Cache
from kometa_docs._include.directive import (
    ARGUMENT_REGEXES,
    GLOB_FLAGS,
    parse_bool_options,
    parse_filename_argument,
    parse_string_argument,
    resolve_file_paths_to_exclude,
    resolve_file_paths_to_include,
    validate_order_option,
    warn_invalid_directive_arguments,
)
from kometa_docs._include.files_watcher import FilesWatcher
from kometa_docs._include.logger import logger
from kometa_docs._include.placeholders import (
    escape_placeholders,
    save_placeholder,
    unescape_placeholders,
)
from wcmatch import glob

from .errors import IncludeError as PluginError

if TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict

    from kometa_docs._include.directive import DefaultValues

    IncludeTags = TypedDict(
        "IncludeTags",
        {
            "include": re.Pattern[str],
            "include-markdown": re.Pattern[str],
        },
    )


@dataclass
class Settings:  # noqa: D101
    exclude: list[str] | None
    include_from_url: bool = False


def get_file_content(  # noqa: PLR0913, PLR0915
    markdown: str,
    # Generated pages return `None` for `file.abs_src_path` because
    # they are not read from a file. In this case, page_src_path is
    # set to `None`.
    page_src_path: str | None,
    docs_dir: str,
    tags: IncludeTags,
    defaults: DefaultValues,
    settings: Settings,
    cumulative_heading_offset: int = 0,
    files_watcher: FilesWatcher | None = None,
    http_cache: Cache | None = None,
    replace_super: dict | None = None,
    replace_tags_super: dict | None = None,
) -> str:
    """Return the content of the file to include."""
    if settings.exclude:
        settings_ignore_paths = list(
            glob.glob(
                [os.path.join(docs_dir, fp) if not os.path.isabs(fp) else fp for fp in settings.exclude],
                flags=GLOB_FLAGS,
                root_dir=docs_dir,
            )
        )
        if page_src_path in settings_ignore_paths:
            return markdown
    else:
        settings_ignore_paths = []

    markdown = escape_placeholders(markdown)
    placeholders_contents: list[tuple[str, str]] = []

    def found_include_tag(  # noqa: PLR0912, PLR0915
        match: re.Match[str],
    ) -> str:
        directive_match_start = match.start()
        directive_lineno = functools.partial(
            process.lineno_from_content_start,
            markdown,
            directive_match_start,
        )

        includer_indent = match["_includer_indent"]

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            location = process.file_lineno_message(
                page_src_path,
                docs_dir,
                directive_lineno(),
            )
            raise PluginError(
                "Found no path passed including with 'include'" f" directive at {location}",
            )

        arguments_string = match["arguments"]

        used_arguments = warn_invalid_directive_arguments(
            arguments_string,
            directive_lineno,
            "include",
            page_src_path,
            docs_dir,
        )

        ignore_paths = [*settings_ignore_paths]
        if "exclude" in used_arguments:
            exclude_match = ARGUMENT_REGEXES["exclude"]().search(
                arguments_string,
            )
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'exclude' argument in 'include'" f" directive at {location}",
                )

            for path in resolve_file_paths_to_exclude(
                exclude_string,
                page_src_path,
                docs_dir,
            ):
                ignore_paths.append(path)

        order = defaults["order"]
        if "order" in used_arguments:
            order_match = ARGUMENT_REGEXES["order"]().search(
                arguments_string,
            )
            order_ = parse_string_argument(order_match)
            if order_ is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'order' argument in 'include'" f" directive at {location}",
                )
            validate_order_option(
                order_,
                page_src_path,
                docs_dir,
                directive_lineno,
                "include",
            )
            order = order_

        file_paths_to_include, is_url = resolve_file_paths_to_include(
            filename,
            page_src_path,
            docs_dir,
            ignore_paths,
            order,
        )

        if is_url:
            if "order" in used_arguments:  # pragma: no cover
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                logger.warning(
                    f"Ignoring 'order' argument of 'include' directive" f" at {location} because the included path is a URL",
                )

            if not settings.include_from_url:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    f"Including from URL at {location} is not allowed because" " include-markdown is configured with include_from_url set" " to false",
                )

        if not file_paths_to_include:
            location = process.file_lineno_message(
                page_src_path,
                docs_dir,
                directive_lineno(),
            )
            raise PluginError(
                f"No files found including '{raw_filename}' at {location}",
            )

        if files_watcher is not None and not is_url:
            files_watcher.included_files.extend(file_paths_to_include)

        start = defaults["start"]
        if "start" in used_arguments:
            start_match = ARGUMENT_REGEXES["start"]().search(arguments_string)
            start = parse_string_argument(start_match)
            if start is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'start' argument in 'include' directive" f" at {location}",
                )

        end = defaults["end"]
        if "end" in used_arguments:
            end_match = ARGUMENT_REGEXES["end"]().search(arguments_string)
            end = parse_string_argument(end_match)
            if end is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'end' argument in 'include' directive at" f" {location}",
                )

        encoding = defaults["encoding"]
        if "encoding" in used_arguments:
            encoding_match = ARGUMENT_REGEXES["encoding"]().search(
                arguments_string,
            )
            encoding_ = parse_string_argument(encoding_match)
            if encoding_ is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'encoding' argument in 'include'" f" directive at {location}",
                )
            encoding = encoding_

        bool_options, invalid_bool_args = parse_bool_options(
            [
                "preserve-includer-indent",
                "dedent",
                "trailing-newlines",
                "recursive",
            ],
            defaults,
            arguments_string,
            used_arguments,
        )
        if invalid_bool_args:
            location = process.file_lineno_message(
                page_src_path,
                docs_dir,
                directive_lineno(),
            )
            raise PluginError(
                f"Invalid value for '{invalid_bool_args[0]}' argument of" f" 'include' directive at {location}." f" Possible values are true or false.",
            )

        start_match = ARGUMENT_REGEXES["start"]().search(arguments_string)
        if start_match:
            start = parse_string_argument(start_match)
            if start is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'start' argument in 'include' directive at" f" {location}",
                )
        else:
            start = defaults["start"]

        end_match = ARGUMENT_REGEXES["end"]().search(arguments_string)
        if end_match:
            end = parse_string_argument(end_match)
            if end is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'end' argument in 'include' directive at" f" {location}",
                )
        else:
            end = defaults["end"]

        replace_match = ARGUMENT_REGEXES["replace"]().search(arguments_string)
        if replace_match:
            replace = parse_string_argument(replace_match)
            if replace is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'replace' argument in 'include-markdown'" f" directive at  {location}",
                )
            try:
                replace = json.loads(replace, strict=False)
                if not isinstance(replace, dict):
                    raise ValueError(f"object not a dictionary {replace}")
                if replace_super:
                    for k, v in replace_super.items():
                        replace[k] = v
            except ValueError as e:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid 'replace' argument in 'include-markdown'" f" directive at  {location}: {e}",
                )
        else:
            replace = defaults["replace"]

        replace_tags_match = ARGUMENT_REGEXES["replace-tags"]().search(arguments_string)
        if replace_tags_match:
            replace_tags = parse_string_argument(replace_tags_match)
            if replace_tags is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'replace-tags' argument in 'include-markdown'" f" directive at  {location}",
                )
            try:
                replace_tags = json.loads(replace_tags, strict=False)
                if not isinstance(replace_tags, dict):
                    raise ValueError(f"object not a dictionary {replace_tags}")
                if replace_tags_super:
                    for k, v in replace_tags_super.items():
                        replace_tags[k] = v
            except ValueError as e:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid 'replace-tags' argument in 'include-markdown'" f" directive at  {location}: {e}",
                )
        else:
            replace_tags = defaults["replace-tags"]

        exclude_tags_match = ARGUMENT_REGEXES["exclude-tags"]().search(arguments_string)
        if exclude_tags_match:
            exclude_tags = parse_string_argument(exclude_tags_match)
            if exclude_tags is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'exclude_tags' argument in 'include-markdown'" f" directive at  {location}",
                )
            exclude_tags = exclude_tags.split("|")
        else:
            exclude_tags = defaults["exclude-tags"]

        include_tags_match = ARGUMENT_REGEXES["include-tags"]().search(arguments_string)
        if include_tags_match:
            include_tags = parse_string_argument(include_tags_match)
            if include_tags is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'include_tags' argument in 'include-markdown'" f" directive at  {location}",
                )
            include_tags = include_tags.split("|")
        else:
            include_tags = defaults["include-tags"]

        text_to_include = ""
        expected_but_any_found = [start is not None, end is not None]
        for file_path in file_paths_to_include:
            if process.is_url(filename):
                new_text_to_include = process.read_url(
                    file_path,
                    http_cache,
                    encoding,
                )
            else:
                new_text_to_include = process.read_file(file_path, encoding)

            if start or end:
                new_text_to_include, *expected_not_found = process.filter_inclusions(
                    start,
                    end,
                    new_text_to_include,
                )
                for i in range(2):
                    if expected_but_any_found[i] and not expected_not_found[i]:
                        expected_but_any_found[i] = False

            if replace:
                new_text_to_include = process.replace_text(new_text_to_include, replace)

            # nested includes
            if bool_options["recursive"].value:
                new_text_to_include = get_file_content(
                    new_text_to_include,
                    file_path,
                    docs_dir,
                    tags,
                    defaults,
                    settings,
                    files_watcher=files_watcher,
                    http_cache=http_cache,
                    replace_super=replace,
                    replace_tags_super=replace_tags,
                )

            if replace:
                new_text_to_include = process.replace_text(new_text_to_include, replace)

            if replace_tags:
                new_text_to_include = process.replace_tags(new_text_to_include, replace_tags)

            if exclude_tags:
                new_text_to_include = process.exclude_tags(new_text_to_include, exclude_tags)

            if include_tags:
                new_text_to_include = process.include_tags(new_text_to_include, include_tags)

            # trailing newlines right stripping
            if not bool_options["trailing-newlines"].value:
                new_text_to_include = process.rstrip_trailing_newlines(
                    new_text_to_include,
                )

            if bool_options["dedent"].value:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options["preserve-includer-indent"].value:
                new_text_to_include = "".join(includer_indent + line for line in (new_text_to_include.splitlines(keepends=True) or [""]))
            else:
                new_text_to_include = includer_indent + new_text_to_include

            text_to_include += new_text_to_include

        # warn if expected start or ends haven't been found in included content
        for i, delimiter_name in enumerate(["start", "end"]):
            if expected_but_any_found[i]:
                delimiter_value = locals()[delimiter_name]
                readable_files_to_include = ", ".join([process.safe_os_path_relpath(fpath, docs_dir) for fpath in file_paths_to_include])
                plural_suffix = "s" if len(file_paths_to_include) > 1 else ""
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                logger.warning(
                    f"Delimiter {delimiter_name} '{delimiter_value}'" f" of 'include' directive at {location}" f" not detected in the file{plural_suffix}" f" {readable_files_to_include}",
                )

        return save_placeholder(placeholders_contents, text_to_include)

    def found_include_markdown_tag(  # noqa: PLR0912, PLR0915
        match: re.Match[str],
    ) -> str:
        directive_match_start = match.start()
        directive_lineno = functools.partial(
            process.lineno_from_content_start,
            markdown,
            directive_match_start,
        )

        includer_indent = match["_includer_indent"]
        filled_includer_indent = " " * len(includer_indent)

        filename, raw_filename = parse_filename_argument(match)
        if filename is None:
            location = process.file_lineno_message(
                page_src_path,
                docs_dir,
                directive_lineno(),
            )
            raise PluginError(
                "Found no path passed including with 'include-markdown'" f" directive at {location}",
            )

        arguments_string = match["arguments"]

        used_arguments = warn_invalid_directive_arguments(
            arguments_string,
            directive_lineno,
            "include-markdown",
            page_src_path,
            docs_dir,
        )

        ignore_paths = [*settings_ignore_paths]
        if "exclude" in used_arguments:
            exclude_match = ARGUMENT_REGEXES["exclude"]().search(
                arguments_string,
            )
            exclude_string = parse_string_argument(exclude_match)
            if exclude_string is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'exclude' argument in 'include-markdown'" f" directive at {location}",
                )
            for path in resolve_file_paths_to_exclude(
                exclude_string,
                page_src_path,
                docs_dir,
            ):
                ignore_paths.append(path)

        order = defaults["order"]
        if "order" in used_arguments:
            order_match = ARGUMENT_REGEXES["order"]().search(
                arguments_string,
            )
            order_ = parse_string_argument(order_match)
            if order_ is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'order' argument in 'include-markdown'" f" directive at {location}",
                )
            validate_order_option(
                order_,
                page_src_path,
                docs_dir,
                directive_lineno,
                "include-markdown",
            )
            order = order_

        file_paths_to_include, is_url = resolve_file_paths_to_include(
            filename,
            page_src_path,
            docs_dir,
            ignore_paths,
            order,
        )

        if is_url:
            if "order" in used_arguments:  # pragma: no cover
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                logger.warning(
                    f"Ignoring 'order' argument of 'include-markdown' directive" f" at {location} because the included path is a URL",
                )

            if not settings.include_from_url:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    f"Including from URL at {location} is not allowed because" " include-markdown is configured with include_from_url set" " to false",
                )

        if not file_paths_to_include:
            location = process.file_lineno_message(
                page_src_path,
                docs_dir,
                directive_lineno(),
            )
            raise PluginError(
                f"No files found including '{raw_filename}' at {location}",
            )

        if files_watcher is not None and not is_url:
            files_watcher.included_files.extend(file_paths_to_include)

        # start and end arguments
        start = defaults["start"]
        if "start" in used_arguments:
            start_match = ARGUMENT_REGEXES["start"]().search(arguments_string)
            start = parse_string_argument(start_match)
            if start is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'start' argument in" f" 'include-markdown' directive at {location}",
                )

        end = defaults["end"]
        if "end" in used_arguments:
            end_match = ARGUMENT_REGEXES["end"]().search(arguments_string)
            end = parse_string_argument(end_match)
            if end is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'end' argument in 'include-markdown'" f" directive at {location}",
                )

        replace_match = ARGUMENT_REGEXES["replace"]().search(arguments_string)
        if replace_match:
            replace = parse_string_argument(replace_match)
            if replace is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'replace' argument in 'include-markdown'" f" directive at  {location}",
                )
            try:
                replace = json.loads(replace, strict=False)
                if not isinstance(replace, dict):
                    raise ValueError(f"object not a dictionary {replace}")
                if replace_super:
                    for k, v in replace_super.items():
                        replace[k] = v
            except ValueError as e:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid 'replace' argument in 'include-markdown'" f" directive at  {location}: {e}",
                )
        else:
            replace = defaults["replace"]

        replace_tags_match = ARGUMENT_REGEXES["replace-tags"]().search(arguments_string)
        if replace_tags_match:
            replace_tags = parse_string_argument(replace_tags_match)
            if replace_tags is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'replace-tags' argument in 'include-markdown'" f" directive at  {location}",
                )
            try:
                replace_tags = json.loads(replace_tags, strict=False)
                if not isinstance(replace_tags, dict):
                    raise ValueError(f"object not a dictionary {replace_tags}")
                if replace_tags_super:
                    for k, v in replace_tags_super.items():
                        replace_tags[k] = v
            except ValueError as e:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid 'replace-tags' argument in 'include-markdown'" f" directive at  {location}: {e}",
                )
        else:
            replace_tags = defaults["replace-tags"]

        exclude_tags_match = ARGUMENT_REGEXES["exclude-tags"]().search(arguments_string)
        if exclude_tags_match:
            exclude_tags = parse_string_argument(exclude_tags_match)
            if exclude_tags is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'exclude_tags' argument in 'include-markdown'" f" directive at  {location}",
                )
            exclude_tags = exclude_tags.split("|")
        else:
            exclude_tags = defaults["exclude-tags"]

        include_tags_match = ARGUMENT_REGEXES["include-tags"]().search(arguments_string)
        if include_tags_match:
            include_tags = parse_string_argument(include_tags_match)
            if include_tags is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'include_tags' argument in 'include-markdown'" f" directive at  {location}",
                )
            include_tags = include_tags.split("|")
        else:
            include_tags = defaults["include-tags"]

        encoding = defaults["encoding"]
        if "encoding" in used_arguments:
            encoding_match = ARGUMENT_REGEXES["encoding"]().search(
                arguments_string,
            )
            encoding_ = parse_string_argument(encoding_match)
            if encoding_ is None:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'encoding' argument in" f" 'include-markdown' directive at {location}",
                )
            encoding = encoding_

        # heading offset
        offset = defaults["heading-offset"]
        if "heading-offset" in used_arguments:
            offset_match = ARGUMENT_REGEXES["heading-offset"]().search(
                arguments_string,
            )
            try:
                # Here None[1] would raise a TypeError
                offset_raw_value = offset_match[1]  # type: ignore
            except (IndexError, TypeError):  # pragma: no cover
                offset_raw_value = ""
            if offset_raw_value == "":
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    "Invalid empty 'heading-offset' argument in" f" 'include-markdown' directive at {location}",
                )
            try:
                offset = int(offset_raw_value)
            except ValueError:
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                raise PluginError(
                    f"Invalid 'heading-offset' argument" f" '{offset_raw_value}' in 'include-markdown'" f" directive at {location}",
                ) from None

        bool_options, invalid_bool_args = parse_bool_options(
            [
                "rewrite-relative-urls",
                "comments",
                "preserve-includer-indent",
                "dedent",
                "trailing-newlines",
                "recursive",
            ],
            defaults,
            arguments_string,
            used_arguments,
        )
        if invalid_bool_args:
            location = process.file_lineno_message(
                page_src_path,
                docs_dir,
                directive_lineno(),
            )
            raise PluginError(
                f"Invalid value for '{invalid_bool_args[0]}' argument of" " 'include-markdown' directive at" f" {location}. Possible values are true or false.",
            )

        separator = "\n" if bool_options["trailing-newlines"].value else ""
        if not start and not end:
            start_end_part = ""
        else:
            start_end_part = f"'{html.escape(start)}' " if start else "'' "
            start_end_part += f"'{html.escape(end)}' " if end else "'' "

        # if any start or end strings are found in the included content
        # but the arguments are specified, we must raise a warning
        #
        # `True` means that no start/end strings have been found in content
        # but they have been specified, so the warning(s) must be raised
        expected_but_any_found = [start is not None, end is not None]

        text_to_include_parts = []
        for file_path in file_paths_to_include:
            if process.is_url(filename):
                new_text_to_include = process.read_url(
                    file_path,
                    http_cache,
                    encoding,
                )
            else:
                new_text_to_include = process.read_file(file_path, encoding)

            if start or end:
                new_text_to_include, *expected_not_found = process.filter_inclusions(
                    start,
                    end,
                    new_text_to_include,
                )
                for i in range(2):
                    if expected_but_any_found[i] and not expected_not_found[i]:
                        expected_but_any_found[i] = False

            if replace:
                new_text_to_include = process.replace_text(new_text_to_include, replace)

            # nested includes
            if bool_options["recursive"].value:
                new_text_to_include = get_file_content(
                    new_text_to_include,
                    file_path,
                    docs_dir,
                    tags,
                    defaults,
                    settings,
                    files_watcher=files_watcher,
                    http_cache=http_cache,
                    replace_super=replace,
                    replace_tags_super=replace_tags,
                )

            if replace:
                new_text_to_include = process.replace_text(new_text_to_include, replace)

            if replace_tags:
                new_text_to_include = process.replace_tags(new_text_to_include, replace_tags)

            if exclude_tags:
                new_text_to_include = process.exclude_tags(new_text_to_include, exclude_tags)

            if include_tags:
                new_text_to_include = process.include_tags(new_text_to_include, include_tags)

            # trailing newlines right stripping
            if not bool_options["trailing-newlines"].value:
                new_text_to_include = process.rstrip_trailing_newlines(
                    new_text_to_include,
                )

            # relative URLs rewriting
            if bool_options["rewrite-relative-urls"].value:
                if page_src_path is None:  # pragma: no cover
                    logger.warning(
                        "Relative URLs rewriting is not supported in" " generated pages.",
                    )
                else:
                    new_text_to_include = process.rewrite_relative_urls(
                        new_text_to_include,
                        source_path=file_path,
                        destination_path=page_src_path,
                    )

            # comments
            if bool_options["comments"].value:
                new_text_to_include = f"{includer_indent}" f"<!-- BEGIN INCLUDE {html.escape(filename)}" f" {start_end_part}-->{separator}{new_text_to_include}" f"{separator}<!-- END INCLUDE -->"
            else:
                new_text_to_include = f"{includer_indent}{new_text_to_include}"

            # dedent
            if bool_options["dedent"].value:
                new_text_to_include = textwrap.dedent(new_text_to_include)

            # includer indentation preservation
            if bool_options["preserve-includer-indent"].value and (new_text_to_include):
                lines = new_text_to_include.splitlines(keepends=True)
                indented_lines = [lines[0]]
                for i in range(1, len(lines)):
                    indented_lines.append(filled_includer_indent + lines[i])
                new_text_to_include = "".join(indented_lines)

            if offset:
                new_text_to_include = process.increase_headings_offset(
                    new_text_to_include,
                    offset=offset + cumulative_heading_offset,
                )

            text_to_include_parts.append(new_text_to_include)

        text_to_include = "".join(text_to_include_parts)

        # warn if expected start or ends haven't been found in included content
        for i, delimiter_name in enumerate(["start", "end"]):
            if expected_but_any_found[i]:
                delimiter_value = locals()[delimiter_name]
                readable_files_to_include = ", ".join([process.safe_os_path_relpath(fpath, docs_dir) for fpath in file_paths_to_include])
                plural_suffix = "s" if len(file_paths_to_include) > 1 else ""
                location = process.file_lineno_message(
                    page_src_path,
                    docs_dir,
                    directive_lineno(),
                )
                logger.warning(
                    f"Delimiter {delimiter_name} '{delimiter_value}' of" f" 'include-markdown' directive at {location}" f" not detected in the file{plural_suffix}" f" {readable_files_to_include}",
                )

        return save_placeholder(placeholders_contents, text_to_include)

    # Replace contents by placeholders
    markdown = tags["include-markdown"].sub(
        found_include_markdown_tag,
        markdown,
    )
    markdown = tags["include"].sub(
        found_include_tag,
        markdown,
    )

    # Replace placeholders by contents
    for placeholder, text in placeholders_contents:
        markdown = markdown.replace(placeholder, text, 1)
    return unescape_placeholders(markdown)
