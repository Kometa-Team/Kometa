#!/usr/bin/env python3
"""Run pyspelling on the files passed by pre-commit.

pyspelling's CLI requires a `-S` flag before each source path. pre-commit passes
filenames as positional arguments, so this small wrapper rewrites them into the
format pyspelling expects and runs a single check over all staged markdown files.
"""

import subprocess
import sys


def main() -> int:
    files = sys.argv[1:]
    if not files:
        return 0

    cmd = ["pyspelling", "--config", ".spellcheck.yml", "-n", "Markdown"]
    for path in files:
        cmd.extend(["-S", path])

    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
