#!/usr/bin/env python3
"""Optional local browser QA. Requires existing Python Playwright + Chromium.
All external requests are blocked; preview uses only its fake receiver.
Does not reproduce native autofill: deliberately seeds a synthetic trap value.
"""
from pathlib import Path
import json, subprocess, threading
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
from preview_site import Preview
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'audit-browser-qa'
OUT.mkdir(exist_ok=True)
server=ThreadingHTTPServer(('127.0.0.1',0),Preview)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
baseline='51433f63d3dfd6aa16af26f69f2c7864175f1597'
old=subprocess.check_output(['git','show',baseline+':assets/audit-core.js'],cwd=ROOT,text=True)
old_page=subprocess.check_output(['git','show',baseline+':audit/index.html'],cwd=ROOT,text=True)
old_handler=subprocess.check_output(['git','show',baseline+':assets/audit.js'],cwd=ROOT,text=True)
results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,chromium_sandbox=True)
  for width in (1280,390):
   context=browser.new_context(viewport={'width':width,'height':900})
   context.route('**/*',lambda route: route.continue_() if route.request.url.startswith(base+'/') else route.abort())
   page=context.new_page()
   def first_step():
    page.locator('#contact_name').fill('Synthetic browser QA')
    page.locator('#email').fill('jonathan@pickleadvisors.com')
    page.locator('#company_name').fill('QA TEST — local fake receiver only')
    page.locator('#q3_bottleneck_other').fill('Synthetic local validation. No lead or email should be sent.')
   page.route('**/assets/audit-core.js*',lambda route:route.fulfill(body=old,content_type='text/javascript'))
   page.route('**/assets/audit.js*',lambda route:route.fulfill(body=old_handler,content_type='text/javascript'))
   page.route('**/audit/',lambda route:route.fulfill(body=old_page,content_type='text/html'))
   page.goto(base+'/audit/')
   first_step()
   page.locator('#company_url').evaluate("el=>el.value='https://synthetic.example'")
   page.locator('#nextStep').click()
   assert page.locator('#formError').inner_text()=='We could not send this request. Please contact Jonathan by email.'
   assert page.locator('.bot-trap').get_attribute('aria-hidden')=='true'
   page.unroute('**/audit/')
   page.unroute('**/assets/audit-core.js*')
   page.unroute('**/assets/audit.js*')
   page.goto(base+'/audit/')
   first_step()
   assert page.locator('#company_url').get_attribute('type')=='checkbox'
   assert page.evaluate("new FormData(document.querySelector('#auditForm')).has('company_url')")==False
   page.locator('#company_url').evaluate('el=>el.checked=true')
   page.locator('#nextStep').click()
   trap=page.locator('#company_url')
   assert trap.is_visible() and trap.evaluate('el=>el===document.activeElement')
   metrics=trap.evaluate('el=>({height:el.getBoundingClientRect().height,font:getComputedStyle(el).fontSize})')
   assert metrics['height']>=24
   assert page.locator('label[for=company_url]').evaluate('el=>el.getBoundingClientRect().height')>=48
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   page.screenshot(path=str(OUT/f'recovery-{width}.png'),full_page=True)
   # Keyboard edits the real input; production collect() reads native FormData.
   trap.press('Space')
   assert not trap.is_checked()
   assert page.evaluate("new FormData(document.querySelector('#auditForm')).has('company_url')")==False
   assert page.locator('#company_name').input_value()=='QA TEST — local fake receiver only'
   page.locator('#nextStep').focus();page.keyboard.press('Enter')
   page.locator('input[name=q1_tools]').first.check()
   page.locator('input[name=q2_channels]').first.check()
   page.locator('#nextStep').click()
   page.locator('#revenue_range').select_option(index=1)
   page.locator('#q8_budget').select_option(index=1)
   page.locator('#submitAudit').click()
   page.locator('#thankYou').wait_for(state='visible')
   assert 'Your request is received.' in page.locator('#thankYou').inner_text()
   page.screenshot(path=str(OUT/f'success-{width}.png'),full_page=True)
   page.goto(base+'/audit/?test=error')
   first_step();page.locator('#nextStep').click()
   page.locator('input[name=q1_tools]').first.check();page.locator('input[name=q2_channels]').first.check()
   page.locator('#nextStep').click();page.locator('#revenue_range').select_option(index=1);page.locator('#q8_budget').select_option(index=1)
   sent=[]
   page.on('request',lambda request:sent.append(request.post_data) if '/qa-receiver/' in request.url and request.method=='POST' else None)
   page.locator('#submitAudit').click()
   page.get_by_role('button',name='Retry request').wait_for()
   page.get_by_role('button',name='Retry request').click()
   page.get_by_role('button',name='Retry request').wait_for()
   assert len(sent)==2 and sent[0]==sent[1]
   assert page.locator('#thankYou').is_hidden()
   results.append({'width':width,'old_error_reproduced_with_seeded_value':True,'keyboard_recovery':True,'fake_success':True,'fake_error_and_identical_retry':True,'no_horizontal_overflow':True})
   context.close()
  browser.close()
finally:server.shutdown()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
