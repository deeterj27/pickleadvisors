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
            "operational drag costing your team time, margin, and attention",
            "pickle advisors builds systems",
            "deet's eats tracks the market",
            "pickle vc is a future selective investment platform",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, HOME_TEXT)
        match = re.search(r'<h1[^>]*>(.*?)</h1>', HOME_HTML, flags=re.I | re.S)
        self.assertIsNotNone(match)
        headline = re.sub(r'<[^>]+>', ' ', match.group(1) if match else '')
        self.assertLessEqual(len(re.findall(r"[A-Za-z']+", headline)), 10)

    def test_trust_objections_and_final_cta_reduce_purchase_friction(self):
        for phrase in [
            "10+ years",
            "daily market view",
            "will this become another software project",
            "is ai worth it for a team our size",
            "will you work with our existing team and tools",
            "manual work compounds",
            "no generic ai roadmap",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, HOME_TEXT)
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
        self.assertIn("the cost of waiting is compounding work", HOME_TEXT)

    def test_three_businesses_are_full_homepage_sections_and_bounded(self):
        for section_id in ["advisory", "media", "capital"]:
            self.assertRegex(HOME_HTML, rf'<section[^>]+id="{section_id}"')
        self.assertIn("coming soon", HOME_TEXT)
        self.assertIn("advisory does not guarantee capital", HOME_TEXT)
        self.assertIn("editorial judgment remains independent", HOME_TEXT)

    def test_media_uses_real_assets_and_compact_live_integrations(self):
        for asset in [
            "counter-service-ep060.webp",
            "breaking-news-shopify-doordash.webp",
            "unpackaged-goods-ep030.webp",
        ]:
            with self.subTest(asset=asset):
                self.assertIn(asset, MEDIA_HTML)
        self.assertIn("https://open.spotify.com/embed/show/6moZEYjORSb5XZ7LVu8b3f/video", MEDIA_HTML)
        self.assertRegex(MEDIA_HTML, r'width="624"[^>]*height="351"[^>]*title="Latest Unpackaged Goods episode')
        self.assertIn("https://open.spotify.com/show/6moZEYjORSb5XZ7LVu8b3f", MEDIA_HTML)
        self.assertNotIn("open.spotify.com/embed/episode/1zSN3tonCYxCceXIx5GfS9", MEDIA_HTML)
        self.assertNotIn("open.spotify.com/episode/1zSN3tonCYxCceXIx5GfS9", HOME_HTML)
        self.assertIn("https://deetseatsnyc.substack.com/embed", MEDIA_HTML)
        self.assertIn("Subscribe to The Deeter Digest on Substack", MEDIA_HTML)

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
        phrase = "consumer, wellness, and food culture"
        self.assertIn(phrase, HOME_TEXT)
        self.assertIn(phrase, MEDIA_TEXT)
        self.assertNotIn(">Publish<", HOME_HTML)


if __name__ == "__main__":
    unittest.main()
