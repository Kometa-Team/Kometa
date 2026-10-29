"""Validate the merged installation document and its client-side route selection."""

import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
from kometa_docs import IncludeRenderer as IncludeAdapter

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs/kometa/install/index.md"


class DocumentTree(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.root = {"tag": "document", "attrs": {}, "children": [], "text": ""}
        self.stack = [self.root]
        self.nodes = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": [], "text": ""}
        self.stack[-1]["children"].append(node)
        self.nodes.append(node)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1]["text"] += data


class InstallationDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = IncludeAdapter().render(PAGE)
        renderer = markdown.Markdown(extensions=["md_in_html", "attr_list", "toc", "admonition", "pymdownx.details", "pymdownx.superfences"])
        cls.html = renderer.convert(cls.content)
        cls.tree = DocumentTree(cls.html + '<nav class="md-nav--secondary">' + renderer.toc + "</nav>")
        cls.ids = [node["attrs"]["id"] for node in cls.tree.nodes if "id" in node["attrs"]]
        cls.project = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))["project"]

    def test_unique_ids_and_all_platform_sections_are_rendered(self):
        self.assertEqual([key for key, count in Counter(self.ids).items() if count > 1], [])
        for route in ("local", "docker", "compose", "unraid", "qnap", "synology", "truenas", "kubernetes", "generic-docker"):
            self.assertIn("path-" + route, self.ids)
        self.assertEqual(self.html.count('<section class="install-path"'), 9)
        self.assertEqual(sum(node["tag"] == "h1" for node in self.tree.nodes), 1)
        # Literal examples can contain this text; only live attributes are errors.
        self.assertFalse(any("markdown" in node["attrs"] for node in self.tree.nodes))
        self.assertNotIn("{%", self.html)

    def test_links_images_and_fragments_resolve(self):
        for node in self.tree.nodes:
            for attr in ("src", "href"):
                url = node["attrs"].get(attr, "")
                parsed = urlsplit(url)
                if not url or parsed.scheme or url.startswith("/"):
                    continue
                if not parsed.path:
                    self.assertIn(unquote(parsed.fragment), self.ids, url)
                else:
                    self.assertTrue((PAGE.parent / unquote(parsed.path)).exists(), url)

    def test_static_fallback_and_accessible_controls(self):
        by_id = {node["attrs"]["id"]: node for node in self.tree.nodes if "id" in node["attrs"]}
        self.assertIn("hidden", by_id["install-questionnaire"]["attrs"])
        self.assertNotIn("hidden", by_id["install-instructions"]["attrs"])
        self.assertNotIn("hidden", by_id["install-fallback"]["attrs"])
        labels = {node["attrs"].get("for") for node in self.tree.nodes if node["tag"] == "label"}
        for field in ("env", "method", "launch", "version"):
            self.assertIn("install-" + field, labels)
        self.assertEqual(by_id["install-summary"]["attrs"]["aria-live"], "polite")

    @unittest.skipUnless(shutil.which("node"), "Node is required for the questionnaire checks")
    def test_questionnaire_routes_and_history(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory) / "installation.json"
            fixture.write_text(json.dumps(self.tree.root), encoding="utf-8")
            result = subprocess.run([shutil.which("node"), str(ROOT / "tests/docs_installation.cjs"), str(fixture)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
