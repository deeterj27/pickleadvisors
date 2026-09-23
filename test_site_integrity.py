import html,json,re,unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,unquote
ROOT=Path(__file__).parent
class Document(HTMLParser):
 def __init__(self,s):super().__init__();self.nodes=[];self.feed(s)
 def handle_starttag(self,t,a):self.nodes.append((t,dict(a)))
class SiteIntegrity(unittest.TestCase):
 def test_pages_have_consistent_navigation_and_resolving_links(self):
  expected=[x['href'] for x in json.loads((ROOT/'content/site.json').read_text())['navigation']]
  for route in ['','advisory','media','about','audit']:
   p=ROOT/route/'index.html';s=p.read_text();d=Document(s)
   ids=[a['id'] for t,a in d.nodes if 'id' in a]
   self.assertEqual(len(ids),len(set(ids)),route)
   nav=re.search(r'<nav class="primary-nav".*?</nav>',s,re.S).group()
   self.assertEqual([a['href'] for t,a in Document(nav).nodes if t=='a'],expected)
   self.assertIn('Skip to content',s);self.assertEqual(sum(t=='main' for t,a in d.nodes),1)
   for t,a in d.nodes:
    for key in (['href'] if t in ['a','link'] else ['src'] if t in ['img','script'] else []):
     url=a.get(key,'');u=urlparse(url)
     if u.scheme and u.netloc!='pickleadvisors.com':continue
     if not url:continue
     dest=(ROOT/u.path.lstrip('/') if u.path.startswith('/') else p.parent/u.path) if u.path else p
     if dest.is_dir():dest=dest/'index.html'
     self.assertTrue(dest.exists(),str(p)+': '+url)
     if u.fragment and dest.suffix=='.html':self.assertIn(unquote(u.fragment),[b.get('id') for _,b in Document(dest.read_text()).nodes],url)
    if t=='img':
     for attr in ['alt','width','height']:self.assertTrue(a.get(attr),a)
 def test_intake_controls_have_accessible_names_and_autocomplete(self):
  s=(ROOT/'audit/index.html').read_text();d=Document(s);labels={a.get('for') for t,a in d.nodes if t=='label'}
  for t,a in d.nodes:
   if t not in ['input','select','textarea'] or a.get('type')=='checkbox':continue
   self.assertIn(a.get('id'),labels,a)
  self.assertIn('autocomplete="name"',s);self.assertIn('autocomplete="email"',s);self.assertIn('autocomplete="organization"',s)
  self.assertEqual(s.count('class="audit-step"'),3)
  self.assertIn('role="alert"',s);self.assertIn('aria-live="polite"',s)
 def test_all_pages_have_indexable_metadata_and_unique_share_images(self):
  images=[]
  for route in ['','advisory','media','about','audit']:
   d=Document((ROOT/route/'index.html').read_text());meta={a.get('name',a.get('property')):a.get('content') for t,a in d.nodes if t=='meta'}
   self.assertEqual(meta['robots'],'index,follow,max-image-preview:large');self.assertEqual(meta['og:image'],meta['twitter:image'])
   self.assertEqual(meta['og:image:width'],'1200');self.assertEqual(meta['og:image:height'],'630');images.append(meta['og:image'])
  self.assertEqual(len(set(images)),5)
 def test_analytics_is_shared_and_answers_are_not_event_parameters(self):
  for route in ['','advisory','media','about','audit']:
   self.assertIn('/assets/analytics.js?',(ROOT/route/'index.html').read_text())
  source=(ROOT/'assets/analytics.js').read_text();self.assertIn("['step','error_code','inquiry_type']",source)
  self.assertNotIn('JSON.stringify',source)
 def test_demo_is_honest_and_content_has_single_sources(self):
  for route in ['','advisory']:
   source=(ROOT/route/'index.html').read_text();self.assertIn('not a client case study or a measured result',source)
  for route in ['home','media']:
   source=(ROOT/f'templates/pages/{route}.html').read_text();self.assertIn('{{newsletter}}',source);self.assertIn('{{social_cards}}',source)
 def test_newsletter_refresh_sanitizes_titles_and_limits_hosts(self):
  import sys
  sys.path.insert(0,str(ROOT/'scripts'))
  from build_site import clean_text
  self.assertEqual(clean_text('The Digest '+chr(0x1F963)),'The Digest')
  from refresh_newsletter import fetch
  for url in ['http://substackcdn.com/image','https://example.org/image','https://127.0.0.1/image']:
   with self.assertRaises(ValueError):fetch(url,{'substackcdn.com'},10)
