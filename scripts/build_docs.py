"""Build Zensical with the canonical URL supplied by Read the Docs."""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    config = ROOT / "zensical.toml"
    canonical_url = os.environ.get("READTHEDOCS_CANONICAL_URL")
    if os.environ.get("READTHEDOCS") == "True" and not canonical_url:
        raise ValueError("Read the Docs did not supply READTHEDOCS_CANONICAL_URL")
    if not canonical_url:
        subprocess.run([sys.executable, "-m", "zensical", "build", "--clean"], cwd=ROOT, check=True)
        return

    # Keep the temporary file beside the original: Zensical resolves paths
    # relative to its configuration, including docs_dir and custom_dir.
    content, count = re.subn(r"^site_url = .*$", lambda _: "site_url = " + json.dumps(canonical_url.rstrip("/") + "/"), config.read_text(encoding="utf-8"), count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError("Expected site_url in zensical.toml")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".toml", prefix=".zensical-rtd-", dir=ROOT, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        subprocess.run([sys.executable, "-m", "zensical", "build", "--clean", "--config-file", str(temporary)], cwd=ROOT, check=True)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    build()
