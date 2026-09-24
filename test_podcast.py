"""Protect the regularly refreshed podcast player and its static fallback."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from scripts.build_site import podcast_episode

class Elements(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.frames = []
        self.links = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag == 'iframe': self.frames.append(dict(attrs))
        if tag == 'a': self.links.append(dict(attrs))

class PodcastTest(unittest.TestCase):
    def setUp(self):
        self.item = json.loads(Path('content/podcast.json').read_text())

    def test_both_pages_include_accessible_player_and_direct_fallback(self):
        for path in ('index.html', 'media/index.html'):
            with self.subTest(path=path):
                page = Elements(Path(path).read_text())
                self.assertEqual(len(page.frames), 1)
                frame = page.frames[0]
                suffix = '/video' if self.item['video'] else ''
                self.assertEqual(frame['src'], 'https://open.spotify.com/embed/episode/' + self.item['episode_id'] + suffix + '?utm_source=generator')
                self.assertIn(self.item['title'], frame['title'])
                self.assertEqual(frame['loading'], 'lazy')
                self.assertIn('allowfullscreen', frame)
                self.assertTrue(any(a['href'] == 'https://www.youtube.com/watch?v=' + self.item['youtube_id'] for a in page.links))
                self.assertTrue(any(a['href'] == 'https://podcasts.apple.com/us/podcast/unpackaged-goods/id1841218206?i=' + self.item['apple_episode_id'] for a in page.links))
                self.assertTrue(any(a['href'] == 'https://open.spotify.com/episode/' + self.item['episode_id'] for a in page.links))

    def test_refresh_cannot_inject_markup_or_an_arbitrary_player(self):
        item = dict(self.item, title='<script>alert(1)</script>', summary='" onload="alert(1)')
        result = podcast_episode(item)
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)
        self.assertEqual(len(Elements(result).frames), 1)
        for changes in ({'episode_id': 'https://example.com'}, {'interview_start':'14:99'}, {'video':'true'}, {'title':''}, {'youtube_id':'javascript:alert(1)'}, {'apple_episode_id':'1&other=2'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                podcast_episode(dict(self.item, **changes))

    def test_no_timestamp_is_invented_for_future_episodes(self):
        result = podcast_episode(dict(self.item, interview_start='', video=False))
        self.assertNotIn('Interview starts at', result)
        self.assertNotIn('/video?', result)
