#!/usr/bin/env python3
"""Render plain HTML from shared, versioned content. No network calls or dependencies."""
import argparse, hashlib, html, json, re
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
def read_json(name):return json.loads((ROOT/'content'/name).read_text())
def esc(value):return html.escape(str(value),quote=True)
def clean_text(text):
 return ''.join(c for c in text if not (0x1F000<=ord(c)<=0x1FAFF or 0x2600<=ord(c)<=0x27BF or 0x2190<=ord(c)<=0x21FF or ord(c) in (0xFE0F,0x200D,0x20E3))).strip()
def render(template,context):
 def replace(m):
  if m[1] not in context:raise ValueError('Unknown template field '+m[1])
  return context[m[1]]
 return re.sub(r'{{([a-z_]+)}}',replace,template)
def date_label(value):return date.fromisoformat(value).strftime('%B %d, %Y').replace(' 0',' ')
def image(item):return f'<img src="{esc(item["image"])}" width="{int(item["width"])}" height="{int(item["height"])}" alt="{esc(clean_text(item["alt"]))}" loading="lazy" decoding="async">'
def newsletter(items):
 first,*rest=items
 feature=f'<a class="feature" href="{esc(first["url"])}" target="_blank" rel="noopener"><div class="feature-art">{image(first)}</div><div class="feature-body"><span class="meta">The Deeter Digest · <time datetime="{first["date"]}">{date_label(first["date"])}</time></span><h3>{esc(clean_text(first["title"]))}</h3><p>Consumer-brand news and the decisions underneath it.</p><span class="textlink">Read this issue</span></div></a>'
 stories=''.join(f'<a class="story" href="{esc(x["url"])}" target="_blank" rel="noopener">{image(x)}<div><span class="meta"><time datetime="{x["date"]}">{date_label(x["date"])}</time></span><h3>{esc(clean_text(x["title"]))}</h3><span class="read">Read the story</span></div></a>' for x in rest)
 return '<div class="digest-grid">'+feature+'<div class="story-list">'+stories+'<div class="subscribe-panel"><span class="eyebrow">A little signal for your inbox</span><h3>The moves worth knowing.</h3><p>Your regular briefing from The Deeter Digest.</p><a class="button" href="https://deetseatsnyc.substack.com/" target="_blank" rel="noopener">Subscribe on Substack</a></div></div></div>'
def social_cards(items):
 return ''.join(f'<a class="social-post" href="{esc(x["url"])}" target="_blank" rel="noopener"><div class="social-image">{image(x)}<span class="format">{esc(x["format"])}</span></div><span class="meta">Instagram · <time datetime="{x["date"]}">{date_label(x["date"])}</time></span><h3>{esc(clean_text(x["title"]))}</h3><p>See the original post</p></a>' for x in items)
def choices(key,label,values):
 controls=''.join(f'<label class="choice"><input type="checkbox" name="{key}" value="{esc(v)}"><span>{esc(v)}</span></label>' for v in values)
 extra=f'<label for="{key}_other">If other, tell us more <span>(optional)</span></label><input id="{key}_other" name="{key}_other" maxlength="300">'
 return f'<fieldset class="choice-group" data-required-group="{key}" aria-describedby="{key}-hint"><legend>{label} (choose at least one)</legend><p id="{key}-hint" class="field-hint">Required. Select all that apply.</p><div class="choice-grid">{controls}</div>{extra}</fieldset>'
def build(check=False):
 site=read_json('site.json');articles=read_json('newsletter.json');posts=read_json('social.json');audit=read_json('audit.json');facts=read_json('advisory.json')
 version=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT/'assets').glob('*.css')))+b''.join(p.read_bytes() for p in sorted((ROOT/'assets').glob('*.js')))).hexdigest()[:12]
 common={'email':esc(site['email']),'asset_version':version,'audit_endpoint':esc(site['audit_endpoint']), 'newsletter':newsletter(articles),'social_cards':social_cards(posts)}
 common['footer_navigation']=''.join(f'<a href="{esc(x["href"])}">{esc(x["label"])}</a>' for x in site['navigation'])
 common['social_links']=''.join(f'<a href="{esc(x["href"])}" target="_blank" rel="noopener">{esc(x["label"])}</a>' for x in site['social'])
 common['proof']=(ROOT/'templates/partials/proof.html').read_text()
 common['service_facts']='<section class="section service-facts"><div class="container"><span class="eyebrow">Working with Pickle</span><h2>A clear starting point.</h2><dl>'+''.join(f'<div><dt>{label}</dt><dd>{esc(facts[k])}</dd></div>' for k,label in [('audience','Who it is for'),('starting_point','How to start'),('audit_focus','What the audit covers'),('implementation','What implementation includes'),('boundaries','Clear boundaries')])+'</dl></div></section>'
 common['tool_choices']=choices('q1_tools','Which tools are involved?',audit['q1_tools'])
 common['channel_choices']=choices('q2_channels','Where do you sell?',audit['q2_channels'])
 common['revenue_choices']=''.join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in audit['revenue_range'])
 common['budget_choices']=''.join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in audit['q8_budget'])
 common['audit_body']=render((ROOT/'templates/partials/audit-body.html').read_text(),common) + '<script type="application/json" id="auditConfig">' + json.dumps({'email':site['email'],'blocked_emails':site['blocked_emails']}).replace('<','\\u003c') + '</script>'
 common['footer']=render((ROOT/'templates/partials/footer.html').read_text(),common)
 common['head_assets']=f'<link rel="stylesheet" href="/assets/fonts/brand.css"><link rel="stylesheet" href="/assets/site.css?v={version}"><script src="/assets/site.js?v={version}" defer></script><script async src="https://www.googletagmanager.com/gtag/js?id={esc(site["analytics_id"])}"></script><script src="/assets/analytics.js?v={version}" defer data-analytics-id="{esc(site["analytics_id"])}"></script>'
 outputs={}
 for name in ['home','advisory','media','about','audit']:
  route='/' if name=='home' else '/'+name+'/'
  context=dict(common)
  context['navigation']=''.join(f'<a href="{esc(x["href"])}"'+(' class="nav-cta"' if x['href']=='/audit/' else '')+(' aria-current="page"' if x['href']==route else '')+f'>{esc(x["label"])}</a>' for x in site['navigation'])
  context['header']=render((ROOT/'templates/partials/header.html').read_text(),context)
  body=render((ROOT/f'templates/pages/{name}.html').read_text(),context)
  body='\n'.join(line.rstrip() for line in body.splitlines())+'\n'
  outputs[ROOT/('index.html' if name=='home' else name+'/index.html')]=body
 if check:
  wrong=[str(p.relative_to(ROOT)) for p,s in outputs.items() if not p.exists() or p.read_text()!=s]
  if wrong:raise SystemExit('Generated pages are stale: '+', '.join(wrong))
 else:
  for p,s in outputs.items():p.write_text(s)
 print('Checked' if check else 'Built',len(outputs),'pages from shared content.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');build(p.parse_args().check)
