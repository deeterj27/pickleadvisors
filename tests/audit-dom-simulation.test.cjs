const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const core=require('../assets/audit-core.js');
test('simulated DOM handler reveals the populated trap, focuses it, and continues after manual clearing',()=>{
 class Element {
  constructor(){this.attrs={};this.events={};this.classes=new Set();this.classList={remove:x=>this.classes.delete(x),add:x=>this.classes.add(x)};}
  setAttribute(k,v){this.attrs[k]=v;} getAttribute(k){return this.attrs[k];} removeAttribute(k){delete this.attrs[k];}
  addEventListener(k,fn){this.events[k]=fn;} focus(){this.focused=true;}
 }
 const ids=Object.fromEntries(['auditForm','auditConfig','previousStep','nextStep','submitAudit','formError','sendingStatus','stepStatus','auditVerification'].map(id=>[id,new Element()]));
 ids.auditConfig.textContent=JSON.stringify({blocked_emails:[]});
 const steps=[new Element(),new Element(),new Element()];
 const form=ids.auditForm;
 form.elements={email:new Element(),company_url:new Element()};
 form.elements.namedItem=k=>form.elements[k];
 form.querySelectorAll=q=>q==='.audit-step'?steps:[];
 ids.auditVerification.classes.add('bot-trap');ids.auditVerification.setAttribute('aria-hidden','true');
 form.elements.company_url.setAttribute('tabindex','-1');
 const values={contact_name:'Synthetic QA',company_name:'QA brand',email:'qa@example.org',q3_bottleneck_other:'Synthetic test only',company_url:'flagged'};
 class FormData {entries(){return Object.entries(values);}getAll(){return [];}}
 vm.runInNewContext(fs.readFileSync(require.resolve('../assets/audit.js'),'utf8'),{document:{getElementById:id=>ids[id]},window:{PickleAudit:core},crypto:{randomUUID:()=> 'qa-reference-123456789'},Element,FormData});
 ids.nextStep.events.click();
 assert.equal(steps[0].hidden,false);
 assert.equal(ids.auditVerification.classes.has('bot-trap'),false);
 assert.equal(ids.auditVerification.getAttribute('aria-hidden'),undefined);
 assert.equal(form.elements.company_url.getAttribute('tabindex'),undefined);
 assert.equal(form.elements.company_url.focused,true);
 assert.equal(form.elements.company_url.getAttribute('aria-invalid'),'true');
 assert.match(ids.formError.textContent,/uncheck the verification box/);
 assert.equal(values.company_name,'QA brand');
 values.company_url='';
 ids.nextStep.events.click();
 assert.equal(steps[1].hidden,false);
 assert.equal(ids.formError.hidden,true);
});
