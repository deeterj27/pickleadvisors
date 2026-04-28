from html.parser import HTMLParser
from pathlib import Path
import html
import re
import unittest

HTML = Path('index.html').read_text()
TEXT = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', HTML)).strip().lower())

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self._current = None
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self._current = {'href': dict(attrs).get('href', ''), 'text': ''}
    def handle_data(self, data):
        if self._current is not None:
            self._current['text'] += data
    def handle_endtag(self, tag):
        if tag == 'a' and self._current is not None:
            self.links.append(self._current)
            self._current = None

class PickleHomepageContentTest(unittest.TestCase):
    def test_hero_names_concrete_cpg_outcome_not_just_metaphor(self):
        self.assertIn('operational bottlenecks', TEXT)
        self.assertIn('food & beverage', TEXT)
        self.assertIn('ai-ready operating system', TEXT)

    def test_hero_has_ai_audit_secondary_conversion_path(self):
        parser = LinkParser(); parser.feed(HTML)
        audit_links = [l for l in parser.links if '/audit' in l['href'] and 'audit' in l['text'].lower()]
        self.assertGreaterEqual(len(audit_links), 2)
        self.assertIn('book a strategy call', TEXT)

    def test_above_fold_has_specific_proof_and_deliverables(self):
        self.assertIn('pricing', TEXT)
        self.assertIn('forecasting', TEXT)
        self.assertIn('dashboards', TEXT)
        self.assertIn('workflows', TEXT)
        self.assertIn('$1b+', TEXT)

if __name__ == '__main__':
    unittest.main()
