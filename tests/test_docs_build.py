"""Checks for RTD version URLs and branch-local release notes."""

import importlib.util
import os
import subprocess
import tempfile
import tomllib
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

import markdown
from kometa_docs import IncludeRenderer

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_docs", ROOT / "scripts/build_docs.py")
build_docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_docs)


class DocumentationBuildTests(unittest.TestCase):
    def test_rtd_versions_and_pr_preview_keep_paths_and_remove_temporary_config(self):
        urls = ["https://kometa.wiki/en/latest/", "https://kometa.wiki/en/develop/", "https://kometa.wiki/en/nightly/", "https://kometa--42.org.readthedocs.build/en/42/"]
        for url in urls:
            with self.subTest(url=url), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                original = 'site_url = "https://kometa.wiki/en/latest/"\ndocs_dir = "docs"\n'
                (root / "zensical.toml").write_text(original, encoding="utf-8")
                configs = []

                def run(command, **kwargs):
                    config = Path(command[-1])
                    self.assertEqual(config.parent, root)
                    self.assertEqual(kwargs["cwd"], root)
                    self.assertTrue(kwargs["check"])
                    self.assertIn("--clean", command)
                    self.assertEqual(tomllib.loads(config.read_text())["site_url"], url)
                    configs.append(config)

                with patch.object(build_docs, "ROOT", root), patch.dict(os.environ, {"READTHEDOCS": "True", "READTHEDOCS_CANONICAL_URL": url}, clear=True), patch.object(build_docs.subprocess, "run", side_effect=run):
                    build_docs.build()
                self.assertEqual(len(configs), 1)
                self.assertFalse(configs[0].exists())
                self.assertEqual((root / "zensical.toml").read_text(), original)

    def test_failed_build_removes_temporary_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "zensical.toml").write_text('site_url = "https://example.com/"\n')
            with (
                patch.object(build_docs, "ROOT", root),
                patch.dict(os.environ, {"READTHEDOCS_CANONICAL_URL": "https://kometa.wiki/en/nightly/"}, clear=True),
                patch.object(build_docs.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "zensical")),
            ):
                with self.assertRaises(subprocess.CalledProcessError):
                    build_docs.build()
            self.assertEqual(list(root.glob(".zensical-rtd-*.toml")), [])

    def test_local_build_uses_original_configuration(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(build_docs.subprocess, "run") as run:
            build_docs.build()
        self.assertEqual(run.call_args.args[0][-2:], ["build", "--clean"])
        self.assertNotIn("--config-file", run.call_args.args[0])

    def test_rtd_without_canonical_url_fails_before_building(self):
        with patch.dict(os.environ, {"READTHEDOCS": "True"}, clear=True), patch.object(build_docs.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "READTHEDOCS_CANONICAL_URL"):
                build_docs.build()
        run.assert_not_called()

    def test_release_notes_embed_the_local_changelog_as_escaped_text(self):
        class SourceParser(HTMLParser):
            active = False

            def __init__(self):
                super().__init__()
                self.source = []

            def handle_starttag(self, tag, attrs):
                if dict(attrs).get("id") == "release-notes-source":
                    self.active = True

            def handle_endtag(self, tag):
                if tag == "pre":
                    self.active = False

            def handle_data(self, data):
                if self.active:
                    self.source.append(data)

        rendered = markdown.markdown(IncludeRenderer(ROOT / "docs").render(ROOT / "docs/kometa/release-notes.md"), extensions=["md_in_html", "fenced_code"])
        parser = SourceParser()
        parser.feed(rendered)

        # Markdown normalizes whitespace-only lines before processing fences.
        def normalize(text):
            return "\n".join(line.rstrip() for line in text.strip().splitlines())

        self.assertEqual(normalize("".join(parser.source)), normalize((ROOT / "CHANGELOG.md").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
