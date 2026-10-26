"""Regression checks for the repository-owned Zensical include extension."""

import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

import markdown
from kometa_docs import IncludeRenderer
from zensical.extensions.context import ContextExtension, Page

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs"


class IncludeRendererTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "docs"
        self.source.mkdir()
        self.adapter = IncludeRenderer(self.source)

    def write(self, relative, content, encoding="utf-8"):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return path

    def test_supplied_docker_directive_unchanged(self):
        self.write(
            "templates/walkthrough/header.md",
            """<!--all-->
# SYSTEM_NAME RUN_TYPE APP_NAME RETRIEVE RUN_NAME FULL_NAME
[Link](./image.png)
<!--all-->
<!--local-->
LOCAL ONLY
<!--local-->
<!--docker-->
DOCKER ONLY
<!--docker-->
""",
        )
        page = self.write(
            "kometa/install/walkthroughs/docker.md",
            """{%
    include-markdown "./../../../templates/walkthrough/header.md"
    include-tags='all|docker|local-docker|docker-unraid'
    replace='{
        "SYSTEM_NAME": "Docker",
        "RUN_TYPE": "via Docker",
        "APP_NAME": "Docker",
        "RETRIEVE": "docker",
        "RUN_NAME": "docker",
        "FULL_NAME": "a Docker container"
    }'
    rewrite-relative-urls=false
%}
""",
        )
        result = self.adapter.render(page)
        self.assertIn("# Docker via Docker Docker docker docker a Docker container", result)
        self.assertIn("[Link](./image.png)", result)
        self.assertIn("DOCKER ONLY", result)
        self.assertNotIn("LOCAL ONLY", result)
        self.assertIn(self.source / "templates/walkthrough/header.md", self.adapter.dependencies)

    def test_nested_sections_encoding_and_external_repository_file(self):
        (self.root / "README.md").write_text("before<!--start-->readme<!--end-->after", encoding="utf-8")
        self.write("templates/nested.md", "{% include-markdown '../../README.md' start='<!--start-->' end='<!--end-->' comments=false %}")
        self.write("templates/latin.txt", "café", encoding="latin-1")
        page = self.write("page.md", "{% include-markdown './templates/nested.md' comments=false %}\n{% include './templates/latin.txt' encoding='latin-1' %}")
        result = self.adapter.render(page)
        self.assertIn("readme", result)
        self.assertNotIn("before", result)
        self.assertIn("café", result)

    def test_remote_include_uses_original_renderer(self):
        page = self.write("page.md", """{% include-markdown "https://example.com/source.md" replace='{"KEY": "value"}' comments=false %}""")
        with patch("kometa_docs._include.process.read_url", return_value="KEY") as download:
            self.assertEqual(self.adapter.render(page), "value")
        download.assert_called_once()

    def test_failures_report_original_source_and_cycles_terminate(self):
        for name, content in [("missing.md", "{% include-markdown './absent.md' %}"), ("invalid.md", "{% include-markdown './invalid.md' replace='bad json' %}"), ("cycle.md", "{% include-markdown './cycle.md' %}")]:
            page = self.write(name, content)
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Include expansion failed") as error:
                self.adapter.render(page)
            self.assertIn(str(page), str(error.exception))

    def test_direct_markdown_extension_uses_zensical_context(self):
        self.write("templates/shared.md", "# VALUE")
        page = self.write("nested/page.md", "{% include-markdown '../templates/shared.md' replace='{\"VALUE\": \"Native\"}' %}")
        # page.path is relative to docs_dir in Zensical's rendering context.
        renderer = markdown.Markdown(extensions=[ContextExtension(page=Page(url="nested/page/", path="nested/page.md"), config={"docs_dir": str(self.source)}), "kometa_docs"])
        self.assertIn("<h1>Native</h1>", renderer.convert(page.read_text(encoding="utf-8")))
        self.write("templates/shared.md", "# Changed VALUE")
        self.assertIn("<h1>Changed Native</h1>", renderer.reset().convert(page.read_text(encoding="utf-8")))

    def test_extension_reports_missing_context(self):
        renderer = markdown.Markdown(extensions=["kometa_docs"])
        with self.assertRaisesRegex(ValueError, "page context"):
            renderer.convert("{% include-markdown 'file.md' %}")

    def test_remote_failure_reports_page(self):
        page = self.write("page.md", '{% include-markdown "https://example.com/missing.md" %}')
        with patch("kometa_docs._include.process.read_url", side_effect=OSError("Network unavailable")):
            with self.assertRaisesRegex(ValueError, "Network unavailable"):
                self.adapter.render(page)

    def test_navigation_targets_exist(self):
        config = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))

        def check(value):
            if isinstance(value, str) and value.endswith(".md") and not value.startswith(("https://", "http://")):
                self.assertTrue((SOURCE / value).is_file(), value)
            elif isinstance(value, list):
                for item in value:
                    check(item)
            elif isinstance(value, dict):
                for item in value.values():
                    check(item)

        check(config["project"]["nav"])

    def test_authored_pages_have_self_contained_local_includes(self):
        adapter = IncludeRenderer(SOURCE)
        with (
            patch("kometa_docs._include.process.read_url", return_value="Remote documentation fixture"),
            patch("kometa_docs._include.logger.logger.warning"),
        ):
            for page in SOURCE.rglob("*.md"):
                if page.relative_to(SOURCE).parts[0] in {"templates", "overrides"}:
                    continue
                with self.subTest(page=str(page.relative_to(SOURCE))):
                    adapter.render(page)
        self.assertTrue(adapter.dependencies, "Expected shared documentation sources")
        for path in adapter.dependencies:
            with self.subTest(include=str(path)):
                self.assertTrue(path.is_relative_to(SOURCE) or path == ROOT / "CHANGELOG.md", "Unexpected include outside docs")
                self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
