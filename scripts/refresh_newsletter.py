#!/usr/bin/env python3
"""Refresh three public RSS stories. Failure retains the last complete snapshot."""
import argparse, hashlib, io, json, re, warnings
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps
from build_site import ROOT, clean_text
USER_AGENT='PickleAdvisors-Newsletter/1.0 (+https://pickleadvisors.com)'
def fetch(url, hosts, limit):
 parsed=urlparse(url)
 if parsed.scheme!='https' or parsed.hostname not in hosts:raise ValueError('Unapproved feed or image host')
 with urlopen(Request(url,headers={'User-Agent':USER_AGENT}),timeout=25) as response:
  final=urlparse(response.url)
  if final.scheme!='https' or final.hostname not in hosts:raise ValueError('Unapproved redirect host')
  blob=response.read(limit+1)
 if len(blob)>limit:raise ValueError('Feed or image exceeds limit')
 return blob

def refresh(feed_bytes=None):
 site=json.loads((ROOT/'content/site.json').read_text())
 blob=feed_bytes or fetch(site['newsletter_feed'],{'deetseatsnyc.substack.com'},5_000_000)
 feed=ET.fromstring(blob);items=feed.findall('./channel/item')[:3]
 if len(items)<3:raise ValueError('Feed does not contain three complete articles')
 staged=[];articles=[]
 for item in items:
  title=clean_text(item.findtext('title') or '');url=item.findtext('link') or ''
  parsed=urlparse(url)
  if parsed.scheme!='https' or parsed.hostname!='deetseatsnyc.substack.com' or not parsed.path.startswith('/p/') or not title:raise ValueError('Invalid article')
  published=parsedate_to_datetime(item.findtext('pubDate')).astimezone(timezone.utc).date().isoformat()
  enclosure=item.find('enclosure')
  if enclosure is None:raise ValueError('Article image missing')
  source=enclosure.attrib['url']
  image_bytes=fetch(source,{'substackcdn.com','substack-post-media.s3.amazonaws.com','images.substackcdn.com'},15_000_000)
  with warnings.catch_warnings():
   warnings.simplefilter('error',Image.DecompressionBombWarning)
   with Image.open(io.BytesIO(image_bytes)) as original:
    picture=ImageOps.exif_transpose(original).convert('RGB');picture.thumbnail((1000,1250))
    buffer=io.BytesIO();picture.save(buffer,format='WEBP',quality=83)
    width,height=picture.size
  name='newsletter-'+hashlib.sha256(url.encode()+buffer.getvalue()).hexdigest()[:16]+'.webp'
  staged.append((ROOT/'pickle-assets'/name,buffer.getvalue()))
  articles.append({'title':title,'url':url,'date':published,'image':'/pickle-assets/'+name,'width':width,'height':height,'alt':title+' — newsletter cover'})
 # Write only after all articles and artwork have passed validation.
 for path,data in staged:path.write_bytes(data)
 content=ROOT/'content/newsletter.json';new=json.dumps(articles,indent=2,ensure_ascii=False)+'\n'
 changed=not content.exists() or content.read_text()!=new
 content.write_text(new)
 if changed:
  from datetime import date
  p=ROOT/'sitemap.xml';text=p.read_text()
  for url in ['https://pickleadvisors.com/','https://pickleadvisors.com/media/']:
   text=re.sub(r'(<loc>'+re.escape(url)+r'</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+date.today().isoformat(),text)
  p.write_text(text)
 print('Updated three newsletter stories.' if changed else 'Newsletter is current.')
 return changed
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--feed-file',type=Path);parser.add_argument('--allow-stale',action='store_true');args=parser.parse_args()
 try:refresh(args.feed_file.read_bytes() if args.feed_file else None)
 except Exception as error:
  if args.allow_stale and (ROOT/'content/newsletter.json').exists():print('::warning::Newsletter refresh failed; retained previous complete snapshot. '+str(error))
  else:raise
