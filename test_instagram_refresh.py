import copy, json, sys, tempfile, unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent/'scripts'))
from update_instagram import update
class InstagramRefreshTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  (self.root/'content').mkdir();(self.root/'pickle-assets').mkdir();(self.root/'content/social.json').write_text('[]\n');(self.root/'sitemap.xml').write_text('<loc>https://pickleadvisors.com/</loc><lastmod>2026-09-21</lastmod>')
  self.cover=self.root/'cover.png';Image.new('RGB',(200,300),'green').save(self.cover)
  self.posts=[dict(url='https://www.instagram.com/deetseatsnyc/reel/test'+str(i)+'/',title='Verified cover',date='2026-09-'+str(21+i),format='REEL / WATCH',alt='Verified artwork',source_image=str(self.cover)) for i in range(3)]
 def test_orders_by_date_and_repeated_import_is_unchanged(self):
  self.assertTrue(update(self.posts,self.root));data=json.loads((self.root/'content/social.json').read_text());self.assertEqual(data[0]['date'],'2026-09-23');self.assertEqual(data[0]['width'],200);self.assertFalse(update(self.posts,self.root))
 def test_invalid_final_post_does_not_replace_snapshot_or_artwork(self):
  self.posts[2]['url']='https://example.com/unrelated'
  with self.assertRaises(ValueError):update(self.posts,self.root)
  self.assertEqual((self.root/'content/social.json').read_text(),'[]\n');self.assertEqual(list((self.root/'pickle-assets').iterdir()),[])
 def test_duplicate_and_older_snapshots_are_rejected(self):
  duplicate=copy.deepcopy(self.posts);duplicate[2]=duplicate[0]
  with self.assertRaises(ValueError):update(duplicate,self.root)
  update(self.posts,self.root);before=(self.root/'content/social.json').read_bytes()
  for post in self.posts:post['date']='2026-09-01'
  with self.assertRaises(ValueError):update(self.posts,self.root)
  self.assertEqual((self.root/'content/social.json').read_bytes(),before)
