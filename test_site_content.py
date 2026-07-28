from html.parser import HTMLParser
from pathlib import Path
import html
import re
import unittest

HOME_HTML = Path("index.html").read_text()
MEDIA_HTML = HOME_HTML
SITE_CSS = Path("assets/site.css").read_text().lower()


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
    def test_hero_leads_with_buyer_outcome_and_explains_all_three_businesses(self):
        for phrase in [
            "build a stronger consumer brand, without more chaos",
            "practical ai workflows your team can trust and run",
            "built for cpg",
            "independent consumer-market intelligence",
            "an operator's edge in consumer",
            "operations + market",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, HOME_TEXT)
        match = re.search(r'<h1[^>]*>(.*?)</h1>', HOME_HTML, flags=re.I | re.S)
        self.assertIsNotNone(match)
        headline = re.sub(r'<[^>]+>', ' ', match.group(1) if match else '')
        self.assertLessEqual(len(re.findall(r"[A-Za-z']+", headline)), 10)

    def test_founder_proof_and_ecosystem_close_tie_the_businesses_together(self):
        for phrase in [
            "built for cpg",
            "human-controlled",
            "build the company",
            "read the market",
            "back what earns conviction",
            "three businesses. clear boundaries",
            "available now",
            "publishing now",
            "coming soon",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, HOME_TEXT)
        for retired in ["the honest answers", "manual work compounds", "will this become another software project"]:
            with self.subTest(retired=retired):
                self.assertNotIn(retired, HOME_TEXT)
        self.assertNotIn("placeholder testimonial", HOME_TEXT)
        self.assertNotIn("client name", HOME_TEXT)

    def test_business_order_matches_current_revenue_and_maturity(self):
        advisor = HOME_HTML.index('id="advisory"')
        media = HOME_HTML.index('id="media"')
        capital = HOME_HTML.index('id="capital"')
        self.assertLess(advisor, media)
        self.assertLess(media, capital)

    def test_navigation_uses_business_names_not_abstract_verbs(self):
        parser = LinkParser()
        parser.feed(HOME_HTML)
        link_text = {link["text"].strip().lower() for link in parser.links}
        for label in ["advisory", "pickle vc", "deet's eats", "ai audit"]:
            self.assertIn(label, link_text)
        site_js = Path("assets/site.js").read_text()
        self.assertIn("scrollIntoView", site_js)
        self.assertIn("document.fonts", site_js)
        for old_label in ["build", "back", "publish"]:
            self.assertNotIn(old_label, link_text)
        self.assertIn("cover", HOME_TEXT)

    def test_homepage_is_concise_and_revenue_led(self):
        self.assertEqual(len(re.findall(r"<section\b", HOME_HTML, flags=re.I)), 5)
        parser = LinkParser()
        parser.feed(HOME_HTML)
        audit_links = [link for link in parser.links if "/audit/" in link["href"]]
        self.assertGreaterEqual(len(audit_links), 3)
        self.assertIn("start with the ai audit", HOME_TEXT)
        self.assertIn("the pickle view", HOME_TEXT)
        self.assertIn("available now", HOME_TEXT)

    def test_three_businesses_are_full_homepage_sections_and_bounded(self):
        for section_id in ["advisory", "media", "capital"]:
            self.assertRegex(HOME_HTML, rf'<section[^>]+id="{section_id}"')
        self.assertIn("coming soon", HOME_TEXT)
        self.assertIn("advisory does not guarantee capital", HOME_TEXT)
        self.assertIn("editorial judgment remains independent", HOME_TEXT)

    def test_media_uses_a_permanent_source_directory(self):
        self.assertIn("media-source-directory", MEDIA_HTML)
        for destination in [
            "https://www.instagram.com/deetseatsnyc/",
            "https://www.tiktok.com/@deetseatsnyc",
            "https://open.spotify.com/show/6moZEYjORSb5XZ7LVu8b3f",
            "https://deetseatsnyc.substack.com/",
        ]:
            with self.subTest(destination=destination):
                self.assertIn(destination, MEDIA_HTML)
        for stale_or_dynamic in [
            "counter-service-ep060.webp",
            "unpackaged-goods-ep030.webp",
            "breaking-news-shopify-doordash.webp",
            "image-cdn-ak.spotifycdn.com",
            "open.spotify.com/embed/",
            "deetseatsnyc.substack.com/embed",
        ]:
            with self.subTest(stale_or_dynamic=stale_or_dynamic):
                self.assertNotIn(stale_or_dynamic, MEDIA_HTML)

    def test_retired_decorative_system_does_not_return(self):
        combined = HOME_HTML + MEDIA_HTML
        for retired in ["signal-rail", "dot-grid", "artifact-grid", "media-mosaic", "channel-list"]:
            with self.subTest(retired=retired):
                self.assertNotIn(retired, combined)
        self.assertNotIn("—", combined)
        self.assertNotIn("linktr.ee/deetseatnyc", combined)

    def test_approved_deets_palette_and_brand_layer_are_locked(self):
        for token in [
            "--canvas:#e8ded0",
            "--surface:#fffdf7",
            "--ink:#10110f",
            "--green:#087b36",
            "--lime:#b8ff38",
            "background-size:7px 7px",
            "approved deet's eats brand layer",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, SITE_CSS)
        self.assertNotIn("#faf8f3", SITE_CSS)
        self.assertNotIn("#ddf77a", SITE_CSS)

    def test_media_scope_is_broad_and_concise(self):
        for phrase in [
            "independent consumer-market intelligence",
            "the weekly signal behind the daily feed",
            "founder conversations beyond the launch story",
        ]:
            self.assertIn(phrase, HOME_TEXT)
            self.assertIn(phrase, MEDIA_TEXT)
        self.assertNotIn(">Publish<", HOME_HTML)


if __name__ == "__main__":
    unittest.main()
