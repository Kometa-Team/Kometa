"""Regression checks for the authored navigation and documentation redirects."""

import tomllib
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs"


def nav_pages(items):
    for item in items:
        if isinstance(item, str):
            yield item
        else:
            for value in item.values():
                if isinstance(value, list):
                    yield from nav_pages(value)
                else:
                    yield value


def published_path(source):
    path = urlsplit(source).path
    return path.removesuffix("index.md") if path.endswith("index.md") else path.removesuffix(".md") + "/"


class DocumentationNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = tomllib.loads((ROOT / "zensical.toml").read_text(encoding="utf-8"))["project"]
        cls.pages = list(nav_pages(cls.project["nav"]))
        cls.redirects = cls.project["plugins"]["redirects"]["redirect_maps"]

    def test_every_navigation_target_exists_and_has_one_location(self):
        self.assertEqual(len(self.pages), len(set(self.pages)), "A page is listed in multiple sidebar locations")
        for page in self.pages:
            with self.subTest(page=page):
                self.assertTrue((SOURCE / page).is_file())

    def test_folders_only_group_explicit_individual_pages(self):
        def check(items):
            for item in items:
                self.assertIsInstance(item, dict, "Every page must have an explicit navigation label")
                for label, value in item.items():
                    if isinstance(value, list):
                        with self.subTest(section=label):
                            self.assertTrue(value, "Navigation folders must not be empty")
                        check(value)

        self.assertNotIn("navigation.indexes", self.project["theme"]["features"])
        check(self.project["nav"])

    def test_redirects_have_final_destinations_without_output_collisions(self):
        published = {published_path(page) for page in self.pages}
        for source, destination in self.redirects.items():
            with self.subTest(source=source):
                self.assertNotIn(published_path(source), published)
                self.assertFalse((SOURCE / source).exists(), "A redirect would overwrite an authored page")

    def test_only_external_redirects_are_configured(self):
        self.assertNotIn("redirect_fragments", self.project["extra"])
        self.assertEqual(
            self.redirects,
            {
                "discord.md": "https://discord.com/invite/kometa-822460010649878528",
                "redact.md": "https://regex101.com/r/DMo1DQ/latest",
                "link.md": "https://discord.com/invite/kometa-822460010649878528",
            },
        )

    def test_merged_services_and_help_are_not_hidden_from_contents(self):
        merged = [page for page in self.pages if page.startswith("files/builders/") and "/categories/" not in page and page != "files/builders/index.md"]
        self.assertEqual(len(merged), 34)
        for page in [*merged, "kometa/help.md"]:
            with self.subTest(page=page):
                self.assertNotIn("  - toc", (SOURCE / page).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
