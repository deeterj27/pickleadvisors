from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote
import html
import re
import unittest

ROOT = Path(__file__).parent
PAGES = {
    "home": ROOT / "index.html",
    "advisory": ROOT / "advisory" / "index.html",
    "capital": ROOT / "capital" / "index.html",
    "media": ROOT / "media" / "index.html",
    "audit": ROOT / "audit" / "index.html",
}
LEGACY_ROUTES = [
    ROOT / "resources" / "index.html",
    ROOT / "resources" / "geo-checklist.html",
    ROOT / "GEO-Checklist-CPG-Founders.html",
]


def visible_text(path: Path) -> str:
    source = path.read_text()
    source = re.sub(r"<script\b[^>]*>.*?</script>", " ", source, flags=re.I | re.S)
    source = re.sub(r"<style\b[^>]*>.*?</style>", " ", source, flags=re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", source))).strip().lower()


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.h1_count = 0
        self.has_main = False
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "a":
            self.links.append(data.get("href", ""))
        elif tag == "img":
            self.images.append(data)
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "main":
            self.has_main = True
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def parse(path: Path) -> DocumentParser:
    parser = DocumentParser()
    parser.feed(path.read_text())
    return parser


class PickleEcosystemSiteTest(unittest.TestCase):
    def test_required_routes_exist(self):
        for name, path in PAGES.items():
            with self.subTest(name=name):
                self.assertTrue(path.exists(), path)
        for path in LEGACY_ROUTES:
            self.assertTrue(path.exists(), path)

    def test_every_primary_page_is_semantic_and_titled(self):
        for name, path in PAGES.items():
            with self.subTest(name=name):
                parser = parse(path)
                self.assertTrue(parser.title.strip())
                self.assertEqual(parser.h1_count, 1)
                self.assertTrue(parser.has_main)

    def test_homepage_names_the_full_ecosystem_and_primary_conversion(self):
        text = visible_text(PAGES["home"])
        for phrase in ["build", "back", "cover", "ai advisory", "pickle vc", "deet's eats", "ai audit"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        source = PAGES["home"].read_text()
        self.assertIn("jonathan.jpeg", source)
        self.assertIn("G-2X2CE22ZED", source)
        self.assertNotIn("the content engine behind the advisory", text)

    def test_navigation_reaches_each_ecosystem_pillar(self):
        links = parse(PAGES["home"]).links
        for href in ["/advisory/", "/capital/", "/media/", "/audit/"]:
            with self.subTest(href=href):
                self.assertIn(href, links)
        self.assertNotIn("/resources/", links)

    def test_advisory_explains_installation_not_generic_strategy(self):
        text = visible_text(PAGES["advisory"])
        for phrase in ["diagnose", "build", "operate", "workflows", "automation", "geo", "ai audit"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_capital_page_has_required_boundaries(self):
        text = visible_text(PAGES["capital"])
        home = visible_text(PAGES["home"])
        self.assertIn("pickle vc coming soon", home)
        self.assertIn("coming soon", text)
        for phrase in ["selective", "diligence", "private", "does not guarantee", "not an offer"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_media_page_uses_real_formats_and_boundary_language(self):
        text = visible_text(PAGES["media"])
        for phrase in ["counter service", "breaking news desk", "the deeter digest", "unpackaged goods", "paid partnerships", "editorial"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        source = PAGES["media"].read_text()
        self.assertIn("/assets/media/", source)
        self.assertIn("https://deetseatsnyc.substack.com/embed", source)
        self.assertIn("https://open.spotify.com/embed/show/6moZEYjORSb5XZ7LVu8b3f/video", source)
        self.assertIn("https://open.spotify.com/show/6moZEYjORSb5XZ7LVu8b3f", source)
        self.assertIn("https://www.instagram.com/deetseatsnyc/", source)
        self.assertNotIn("agency-partner-sell-sheet", source)

    def test_retired_resource_routes_redirect_to_media(self):
        for path in LEGACY_ROUTES:
            source = path.read_text().lower()
            with self.subTest(path=path):
                self.assertIn('content="0;url=/media/"', source)
                self.assertIn('name="robots" content="noindex"', source)

    def test_retired_design_and_content_do_not_return(self):
        for path in ROOT.rglob("*.html"):
            source = path.read_text()
            with self.subTest(path=path):
                self.assertNotIn("—", source)
                self.assertNotIn("logo-icon.svg", source)
                self.assertNotIn("agency-partner-sell-sheet", source)
        for path in PAGES.values():
            self.assertNotIn('/resources/', path.read_text())

    def test_no_public_advisory_pricing(self):
        for name in ["home", "advisory", "capital"]:
            text = visible_text(PAGES[name])
            with self.subTest(name=name):
                self.assertIsNone(re.search(r"\$\s?\d[\d,]*(?:\s?\/\s?month)?", text))

    def test_images_have_alt_attributes(self):
        for name, path in PAGES.items():
            for image in parse(path).images:
                with self.subTest(name=name, src=image.get("src")):
                    self.assertIn("alt", image)

    def test_internal_absolute_links_resolve_to_files(self):
        checked = set()
        for path in PAGES.values():
            for href in parse(path).links:
                if not href or href.startswith(("#", "mailto:", "tel:", "http://", "https://", "javascript:")):
                    continue
                route = urlparse(href).path
                if not route.startswith("/"):
                    continue
                route = unquote(route)
                if route in checked:
                    continue
                checked.add(route)
                candidate = ROOT / route.lstrip("/")
                if route.endswith("/"):
                    candidate = candidate / "index.html"
                self.assertTrue(candidate.exists(), f"Broken internal link: {href} -> {candidate}")


if __name__ == "__main__":
    unittest.main()
