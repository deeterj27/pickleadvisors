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
            "og:image": "https://pickleadvisors.com/og-image-v2.png",
            "og:image:width": "1200",
            "og:image:height": "630",
            "twitter:card": "summary_large_image",
            "twitter:image": "https://pickleadvisors.com/og-image-v2.png",
        }
        for key, value in expected.items():
            self.assertEqual(head.meta.get(key), value, key)
        for key in ["og:title", "og:description", "og:image:alt", "twitter:title", "twitter:description", "twitter:image:alt"]:
            self.assertTrue(head.meta.get(key), key)
        self.assertNotIn("three businesses built around", head.meta["og:title"].lower())
        self.assertEqual(png_dimensions("og-image-v2.png"), (1200, 630))

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
