"""Regression coverage for the single-homepage navigation contract."""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
ROOT=Path(__file__).parent
class Page(HTMLParser):
 def __init__(self,source):
  super().__init__();self.ids={};self.navs=[];self.nav=None;self.feed(source)
 def handle_starttag(self,tag,attrs):
  data=dict(attrs)
  if 'id' in data:self.ids[data['id']]=data
  if tag=='nav':self.nav=[];self.navs.append(self.nav)
  if tag=='a' and self.nav is not None:self.nav.append(data.get('href'))
 def handle_endtag(self,tag):
  if tag=='nav':self.nav=None
class HomeNavigation(unittest.TestCase):
 def test_all_primary_navigation_targets_home_sections_from_every_route(self):
  expected=['/#advisory','/#media','/#jonathan','/#capital','/#audit']
  home=Page((ROOT/'index.html').read_text())
  self.assertEqual([x['href'] for x in json.loads((ROOT/'content/site.json').read_text())['navigation']],expected)
  for href in expected:self.assertEqual(home.ids[href.split('#')[1]]['tabindex'],'-1')
  for name in ['index.html','advisory/index.html','media/index.html','about/index.html','audit/index.html']:
   with self.subTest(page=name):
    navs=Page((ROOT/name).read_text()).navs
    self.assertEqual(navs[0],expected);self.assertEqual(navs[1],expected)
 def test_existing_intake_and_legacy_routes_survive(self):
  self.assertIn('href="/audit/">Start the audit intake', (ROOT/'index.html').read_text())
  for route in ['advisory','media','about','audit','capital','resources']:
   self.assertTrue((ROOT/route/'index.html').exists())
