# Shared Collection Variables

These variables are shared by the default collection files. File-specific variables are documented on each Defaults page.

{%
    include-markdown "../templates/defaults/base/collection/shared.md"
    rewrite-relative-urls=false
    replace='{
        "../../../../defaults/": "",
        "../../config/": "../config/operations.md",
        "../../defaults/": ""
    }'
%}
