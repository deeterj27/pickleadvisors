from html.parser import HTMLParser
from pathlib import Path
import html
import re
import unittest

HOME_HTML = Path("index.html").read_text()
MEDIA_HTML = Path("media/index.html").read_text()


def visible_text(source: str) -> str:
    source = re.sub(r"<script\b[^>]*>.*?</script>", " ", source, flags=re.I | re.S)
    source = re.sub(r"<style\b[^>]*>.*?</style>", " ", source, flags=re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", source))).strip().lower()


HOME_TEXT = visible_text(HOME_HTML)
MEDIA_TEXT = visible_text(MEDIA_HTML)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._current = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._current = {"href": dict(attrs).get("href", ""), "text": ""}

    def handle_data(self, data):
        if self._current is not None:
            self._current["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._current is not None:
            self.links.append(self._current)
            self._current = None


class PickleHomepageContentTest(unittest.TestCase):
    def test_hero_explains_all_three_businesses_plainly(self):
        for phrase in [
            "three businesses built around better consumer brands",
            "pickle advisors installs ai operating systems",
            "pickle vc is a future investment platform",
            "deet's eats publishes food and consumer media",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, HOME_TEXT)

    def test_navigation_uses_business_names_not_abstract_verbs(self):
        parser = LinkParser()
        parser.feed(HOME_HTML)
        link_text = {link["text"].strip().lower() for link in parser.links}
        for label in ["advisory", "pickle vc", "deet's eats", "ai audit"]:
            self.assertIn(label, link_text)
        for old_label in ["build", "back", "publish"]:
            self.assertNotIn(old_label, link_text)

    def test_homepage_is_concise_and_revenue_led(self):
        self.assertLessEqual(len(re.findall(r"<section\b", HOME_HTML, flags=re.I)), 4)
        parser = LinkParser()
        parser.feed(HOME_HTML)
        audit_links = [link for link in parser.links if "/audit/" in link["href"]]
        self.assertGreaterEqual(len(audit_links), 3)
        self.assertIn("the highest-intent place to begin is the ai audit", HOME_TEXT)

    def test_three_businesses_are_visually_equal_and_bounded(self):
        self.assertEqual(HOME_HTML.count('class="business-card"'), 3)
        self.assertIn("pickle vc coming soon", HOME_TEXT)
        self.assertIn("each business stands on its own", HOME_TEXT)
        self.assertIn("advisory does not guarantee media coverage or capital", HOME_TEXT)

    def test_media_uses_real_assets_and_compact_live_integrations(self):
        for asset in [
            "counter-service-ep060.webp",
            "breaking-news-shopify-doordash.webp",
            "unpackaged-goods-ep030.webp",
        ]:
            with self.subTest(asset=asset):
                self.assertIn(asset, MEDIA_HTML)
        self.assertIn("https://open.spotify.com/embed/episode/1zSN3tonCYxCceXIx5GfS9", MEDIA_HTML)
        self.assertRegex(MEDIA_HTML, r'height="152"[^>]*title="Latest Unpackaged Goods episode')
        self.assertIn("https://deetseatsnyc.substack.com/embed", MEDIA_HTML)
        self.assertIn("Subscribe to The Deeter Digest on Substack", MEDIA_HTML)

    def test_retired_decorative_system_does_not_return(self):
        combined = HOME_HTML + MEDIA_HTML
        for retired in ["signal-rail", "dot-grid", "artifact-grid", "media-mosaic", "channel-list"]:
            with self.subTest(retired=retired):
                self.assertNotIn(retired, combined)
        self.assertNotIn("—", combined)
        self.assertNotIn("linktr.ee/deetseatnyc", combined)


if __name__ == "__main__":
    unittest.main()
