#!/usr/bin/env python3
"""Import three browser-verified Instagram posts and local cover assets.

This script does not scrape Instagram or use credentials. The daily task verifies
public dates, links, and covers through the browser before supplying a manifest.
"""
import argparse, hashlib, io, json, re, warnings
from datetime import date
from pathlib import Path
from PIL import Image, ImageOps
from build_site import ROOT, clean_text

def update(posts, root=ROOT):
 if len(posts)!=3:raise ValueError('Exactly three verified posts are required')
 articles=[];staged=[];seen=set()
 for post in posts:
  url=post['url']
  if not re.fullmatch(r'https://www\.instagram\.com/deetseatsnyc/(?:p|reel)/[A-Za-z0-9_-]+/',url):raise ValueError('Expected a verified deetseatsnyc post URL')
  if url in seen:raise ValueError('Duplicate Instagram post')
  seen.add(url)
  published=date.fromisoformat(post['date'])
  if published>date.today():raise ValueError('Post date cannot be in the future')
  title=clean_text(post['title']);alt=clean_text(post['alt'])
  if not title or not alt or len(title)>180 or len(alt)>400:raise ValueError('A short verified title and image description are required')
  if post['format'] not in ['REEL / WATCH','CAROUSEL / READ','POST / READ']:raise ValueError('Unsupported format')
  path=Path(post['source_image'])
  if not path.is_absolute() or path.stat().st_size>15000000:raise ValueError('Expected a local cover file under 15 MB')
  with warnings.catch_warnings():
   warnings.simplefilter('error',Image.DecompressionBombWarning)
   with Image.open(path) as original:
    picture=ImageOps.exif_transpose(original).convert('RGB');picture.thumbnail((1000,1250))
    width,height=picture.size
    if min(width,height)<100:raise ValueError('Cover is too small')
    buffer=io.BytesIO();picture.save(buffer,format='WEBP',quality=83)
  image='instagram-'+hashlib.sha256(url.encode()+buffer.getvalue()).hexdigest()[:16]+'.webp'
  staged.append((root/'pickle-assets'/image,buffer.getvalue()))
  articles.append({'url':url,'title':title,'date':published.isoformat(),'format':post['format'],'image':'/pickle-assets/'+image,'width':width,'height':height,'alt':alt})
 # Stable sort retains observed grid order for posts sharing a date.
 articles.sort(key=lambda p:p['date'],reverse=True)
 target=root/'content/social.json'
 previous=json.loads(target.read_text()) if target.exists() else []
 if previous and articles[0]['date']<max(p['date'] for p in previous):raise ValueError('Refusing to replace newer posts with an older snapshot')
 snapshot=json.dumps(articles,indent=2,ensure_ascii=False)+'\n'
 if target.exists() and target.read_text()==snapshot:
  print('Instagram is current.');return False
 for path,blob in staged:path.write_bytes(blob)
 target.write_text(snapshot)
 sitemap=root/'sitemap.xml';text=sitemap.read_text()
 for url in ['https://pickleadvisors.com/','https://pickleadvisors.com/media/']:
  text=re.sub(r'(<loc>'+re.escape(url)+r'</loc>\s*<lastmod>)[^<]+',lambda m:m[1]+date.today().isoformat(),text)
 sitemap.write_text(text)
 print('Updated three Instagram posts.');return True
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('manifest',type=Path);args=parser.parse_args()
 update(json.loads(args.manifest.read_text()))
