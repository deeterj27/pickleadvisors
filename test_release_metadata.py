import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.links = []
        self.json_ld = []
        self._json_script = False
        self._json_chunks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            if key:
                self.meta[key] = attrs.get("content", "")
        elif tag == "link":
            self.links.append(attrs)
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._json_script = True
            self._json_chunks = []

    def handle_data(self, data):
        if self._json_script:
            self._json_chunks.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._json_script:
            self.json_ld.append(json.loads("".join(self._json_chunks)))
            self._json_script = False
            self._json_chunks = []


def parse_head(path):
    parser = HeadParser()
    parser.feed((ROOT / path).read_text())
    return parser


def png_dimensions(path):
    data = (ROOT / path).read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


class ReleaseMetadataTest(unittest.TestCase):
    def test_homepage_social_card_is_complete_and_current(self):
        head = parse_head("index.html")
        expected = {
            "og:type": "website",
            "og:site_name": "Pickle Advisors",
            "og:url": "https://pickleadvisors.com/",
            "og:image": "https://pickleadvisors.com/og-image-v3.png",
            "og:image:width": "1200",
            "og:image:height": "630",
            "twitter:card": "summary_large_image",
            "twitter:image": "https://pickleadvisors.com/og-image-v3.png",
        }
        for key, value in expected.items():
            self.assertEqual(head.meta.get(key), value, key)
        for key in ["og:title", "og:description", "og:image:alt", "twitter:title", "twitter:description", "twitter:image:alt"]:
            self.assertTrue(head.meta.get(key), key)
        self.assertEqual(head.meta["og:title"], "Pickle Advisors | Build a Stronger Consumer Brand")
        self.assertEqual(head.meta["twitter:title"], "Pickle Advisors | Build a Stronger Consumer Brand")
        self.assertNotIn("operating system", head.meta["og:title"].lower())
        card_source = (ROOT / "assets/social/og-card.html").read_text()
        self.assertIn("Built for Consumer Brands", card_source)
        self.assertNotIn("Operating System", card_source)
        self.assertFalse((ROOT / "og-image-v2.png").exists())
        self.assertNotIn("three businesses built around", head.meta["og:title"].lower())
        self.assertEqual(png_dimensions("og-image-v3.png"), (1200, 630))

    def test_audit_has_its_own_social_card_and_canonical(self):
        head = parse_head("audit/index.html")
        self.assertEqual(head.meta["og:url"], "https://pickleadvisors.com/audit/")
        self.assertEqual(head.meta["og:image"], "https://pickleadvisors.com/audit-og-image.png")
        self.assertEqual(head.meta["twitter:image"], "https://pickleadvisors.com/audit-og-image.png")
        self.assertTrue(head.meta["og:image:alt"])
        canonical = [link for link in head.links if link.get("rel") == "canonical"]
        self.assertEqual(canonical[0]["href"], "https://pickleadvisors.com/audit/")
        self.assertEqual(png_dimensions("audit-og-image.png"), (1200, 630))

    def test_touch_icon_and_structured_data_are_valid(self):
        self.assertEqual(png_dimensions("apple-touch-icon.png"), (180, 180))
        for page in ["index.html", "audit/index.html"]:
            head = parse_head(page)
            touch = [link for link in head.links if link.get("rel") == "apple-touch-icon"]
            self.assertEqual(touch[0]["href"], "/apple-touch-icon.png")
            self.assertTrue(head.json_ld)
        home_graph = parse_head("index.html").json_ld[0]["@graph"]
        types = {entry["@type"] for entry in home_graph}
        self.assertEqual(types, {"Organization", "WebSite"})

    def test_audit_receiver_uses_single_write_redirect_handling(self):
        source = (ROOT / "audit/index.html").read_text()
        self.assertIn("mode: 'cors'", source)
        self.assertIn("redirect: 'manual'", source)
        self.assertIn("cache: 'no-store'", source)
        self.assertIn("response.type !== 'opaqueredirect'", source)
        self.assertNotIn("mode: 'no-cors'", source)
        catch_body = source.split("}).catch(() => {", 1)[1].split("});", 1)[0]
        self.assertIn("btn.disabled = false", catch_body)
        self.assertIn("We could not submit your audit", catch_body)
        self.assertNotIn("thankYou.style.display = 'block'", catch_body)

    def test_public_site_contains_no_emoji_or_decorative_arrows(self):
        public_suffixes = {".html", ".css", ".js", ".xml", ".svg"}
        excluded_parts = {".git", "qa", "evidence"}
        decorative_symbols = set("→↗↓✓")

        def is_emoji(character):
            codepoint = ord(character)
            return (
                0x1F000 <= codepoint <= 0x1FAFF
                or 0x2600 <= codepoint <= 0x27BF
                or codepoint == 0xFE0F
            )

        violations = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in public_suffixes:
                continue
            if excluded_parts.intersection(path.parts):
                continue
            for character in path.read_text(errors="ignore"):
                if character in decorative_symbols or is_emoji(character):
                    violations.append(f"{path.relative_to(ROOT)}: U+{ord(character):04X}")
        self.assertEqual(violations, [])

    def test_robots_and_sitemap_cover_public_conversion_routes(self):
        robots = (ROOT / "robots.txt").read_text()
        self.assertIn("Sitemap: https://pickleadvisors.com/sitemap.xml", robots)
        tree = ET.parse(ROOT / "sitemap.xml")
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {node.text for node in tree.findall("sm:url/sm:loc", namespace)}
        self.assertEqual(urls, {"https://pickleadvisors.com/", "https://pickleadvisors.com/audit/"})
        dates = [node.text for node in tree.findall("sm:url/sm:lastmod", namespace)]
        self.assertTrue(all(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value or "") for value in dates))


if __name__ == "__main__":
    unittest.main()
