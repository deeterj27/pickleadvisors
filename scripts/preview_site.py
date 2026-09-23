#!/usr/bin/env python3
"""Local preview with a fake form receiver. Never sends preview leads to production."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import argparse,re
ROOT=Path(__file__).resolve().parents[1]
class Preview(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
 def do_POST(self):
  if not self.path.startswith('/qa-receiver/'):
   self.send_error(405);return
  self.rfile.read(int(self.headers.get('Content-Length',0)))
  return self.do_GET()
 def do_GET(self):
  parsed=urlparse(self.path)
  if parsed.path.startswith('/qa-receiver/'):
   mode=parsed.path.rstrip('/').rsplit('/',1)[1]
   status=200 if mode=='confirmed' else 500
   body=b'{"saved":true,"receiptId":"local-test-only"}' if status==200 else b'{"saved":false}'
   self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(body);return
  if parsed.path in ['/audit/','/audit/index.html']:
   mode=parse_qs(parsed.query).get('test',['confirmed'])[0]
   if mode not in ['confirmed','error']:mode='confirmed'
   source=(ROOT/'audit/index.html').read_text()
   source=re.sub(r'data-endpoint="[^"]+"',f'data-endpoint="/qa-receiver/{mode}"',source)
   body=source.encode();self.send_response(200);self.send_header('Content-Type','text/html;charset=utf-8');self.send_header('X-Robots-Tag','noindex');self.end_headers();self.wfile.write(body);return
  return super().do_GET()
 def log_message(self,format,*args):
  # Do not log form query strings in development.
  print(self.command,urlparse(self.path).path)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8882);args=p.parse_args()
 print('Local preview: audit submissions use a fake receiver, never the production endpoint.',flush=True)
 ThreadingHTTPServer(('127.0.0.1',args.port),Preview).serve_forever()
