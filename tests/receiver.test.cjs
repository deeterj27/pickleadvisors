const {test}=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');const crypto=require('node:crypto');
const headers=['Timestamp','Company','Contact','Industry','Revenue','Team Size','Website','Email','Phone','Tools','Channels','Bottlenecks','Financials','AI Usage','Manual Hours','Inventory','Budget','10 Extra Hours','90-Day Success','Source','Request ID','Payload Hash','Receipt Status','Owner Alert Status'];
function setup(options={}) {
 const tables={Sheet1:options.legacy || []};const sent=[];let locked=false,flushes=0,opens=0,failFlush=options.failFlush||0,failAppend=options.failAppend;
 function sheet(name) {
  const rows=tables[name];
  return {
   getLastRow:()=>rows.length,
   appendRow(row){if(failAppend)throw Error('storage');rows.push([...row]);},
   getRange(row,col,height=1,width=1) {
    return {
     getValue:()=>rows[row-1]?.[col-1]??'',
     getValues:()=>Array.from({length:height},(_,i)=>Array.from({length:width},(_,j)=>rows[row+i-1]?.[col+j-1]??'')),
     setValue(value){rows[row-1][col-1]=value;},
     getRow:()=>row,
     createTextFinder(value) {
      return {
       matchEntireCell(){return this;},matchCase(){return this;},useRegularExpression(){return this;},
       findNext(){const index=rows.findIndex((r,i)=>i>=row-1 && i<row-1+height && r[col-1]===value);return index<0?null:{getRow:()=>index+1};}
      };
     }
    };
   }
  };
 }

 const book={getSheetByName:name=>tables[name]?sheet(name):null,insertSheet(name){tables[name]=[];return sheet(name);}};
 const context={ContentService:{MimeType:{JSON:'json'},createTextOutput:text=>({setMimeType:()=>JSON.parse(text)})},Utilities:{getUuid:()=> 'legacy-request-1234567890',DigestAlgorithm:{SHA_256:'sha256'},Charset:{UTF_8:'utf8'},computeDigest:(_,text)=>crypto.createHash('sha256').update(text).digest(),base64Encode:bytes=>Buffer.from(bytes).toString('base64')},LockService:{getScriptLock:()=>({waitLock(){if(options.failLock)throw Error('busy');locked=true;},hasLock:()=>locked,releaseLock(){locked=false;}})},SpreadsheetApp:{openById:()=>{opens++;return book;},flush(){flushes++;if(flushes===failFlush)throw Error('flush');}},MailApp:{getRemainingDailyQuota(){if(options.failQuota)throw Error('auth');return options.quota??100;},sendEmail(message){sent.push(message);if(options.failMail)throw Error('mail uncertain');}}};
 vm.createContext(context);vm.runInContext(fs.readFileSync('backend/Code.gs','utf8'),context);context.AUDIT_MAIL_ENABLED=options.mail??true;
 return {context,tables,sent,state:()=>({locked,flushes,opens}),submit:data=>context.doPost({parameter:{data:JSON.stringify(data)}})};
}
const valid={request_id:'request-1234567890-abcdef',company_name:'Brand',contact_name:'Operator',email:'operator@example.org',phone:'555-0100',q1_tools:['Other'],q1_tools_other:'Custom stock app',q2_channels:['Retail'],q3_bottleneck:['Other'],q3_bottleneck_other:'Inventory missing from orders',revenue_range:'$75K+',q8_budget:'$500-$2,000/mo'};
test('storage maps every field to canonical headers and preserves legacy values byte for byte',()=>{
 const legacy=[['Timestamp','Company','Contact','Industry','Revenue','Team','Website','Email','Tools','Channels'],['old','legacy','','','','','','','historical tools','historical channel']];const before=JSON.stringify(legacy);
 const t=setup({legacy});assert.equal(t.submit(valid).saved,true);const rows=t.tables['Audit Intake v2'];assert.deepEqual(rows[0],headers);assert.equal(rows[1][8],'555-0100');assert.match(rows[1][9],/Custom stock app/);assert.match(rows[1][11],/Inventory missing/);assert.equal(JSON.stringify(legacy),before);assert.equal(t.state().locked,false);
});
test('same ID and payload returns one lead and exactly one of each email',()=>{const t=setup();assert.equal(t.submit(valid).notifications,'sent');assert.equal(t.submit(valid).receiptId,valid.request_id);assert.equal(t.tables['Audit Intake v2'].length,2);assert.equal(t.sent.length,2);assert.equal(t.sent[0].to,valid.email);assert.equal(t.sent[1].to,'jonathan@pickleadvisors.com');assert.equal(t.sent[1].replyTo,valid.email);assert.match(t.sent[0].body,/No call has been booked/);assert.match(t.sent[0].body,/free 30-minute conversation/);assert.match(t.sent[0].body,/audit is free/);assert.match(t.sent[0].body,/implementation work would be scoped and priced separately/);});
test('same ID with changed content reports conflict instead of silently losing edits',()=>{const t=setup();t.submit(valid);assert.equal(t.submit({...valid,company_name:'Changed'}).error,'request_id_conflict');assert.equal(t.tables['Audit Intake v2'].length,2);assert.equal(t.sent.length,2);});
test('invalid input and lock/write failures never confirm or send',()=>{for(const data of [{...valid,email:'bad'},{...valid,email:'a@x.org,b@y.org'},{...valid,company_url:'bot'},{...valid,q1_tools:[{}]},{...valid,q3_bottleneck_other:'x'.repeat(1501)}]){const t=setup();assert.equal(t.submit(data).saved,false);assert.equal(t.sent.length,0);}for(const option of ['failAppend','failLock']){const t=setup({[option]:true});assert.equal(t.submit(valid).saved,false);assert.equal(t.sent.length,0);assert.equal(t.state().locked,false);}});
test('flush failure does not confirm; retry recovers appended row without duplicate',()=>{const t=setup({failFlush:2});assert.equal(t.submit(valid).saved,false);assert.equal(t.sent.length,0);assert.equal(t.submit(valid).saved,true);assert.equal(t.tables['Audit Intake v2'].length,2);assert.equal(t.sent.length,2);});
test('mail error preserves saved receipt and uncertain sends are never retried',()=>{const t=setup({failMail:true});assert.equal(t.submit(valid).saved,true);assert.deepEqual(t.tables['Audit Intake v2'][1].slice(22),['review','review']);t.submit(valid);t.context.retryPendingAuditNotifications();assert.equal(t.sent.length,2);});
test('quota/auth failures and disabled mail preserve pending rows without sending',()=>{for(const options of [{quota:0},{failQuota:true},{mail:false}]){const t=setup(options);assert.equal(t.submit(valid).saved,true);assert.equal(t.sent.length,0);assert.deepEqual(t.tables['Audit Intake v2'][1].slice(22),['pending','pending']);}});
test('pending mail can be retried independently without a second lead',()=>{const t=setup({mail:false});t.submit(valid);t.context.AUDIT_MAIL_ENABLED=true;t.context.retryPendingAuditNotifications();t.context.retryPendingAuditNotifications();assert.equal(t.sent.length,2);assert.equal(t.tables['Audit Intake v2'].length,2);});
test('failed sent-status flush never causes another delivery',()=>{const t=setup({failFlush:4});t.submit(valid);t.submit(valid);assert.equal(t.sent.length,2);});
test('schema mismatch fails closed without overwriting any values',()=>{const t=setup();t.tables['Audit Intake v2']=[['Custom schema']];assert.equal(t.submit(valid).saved,false);assert.deepEqual(t.tables['Audit Intake v2'],[['Custom schema']]);});
test('legacy request IDs deduplicate without backfilling mail or changing old rows',()=>{const legacy=[headers.slice(0,21),Array(21).fill('')];legacy[1][20]=valid.request_id;const t=setup({legacy});assert.equal(t.submit(valid).notifications,'legacy');assert.equal(t.sent.length,0);assert.equal(t.tables['Audit Intake v2'],undefined);});
test('health check is read only; legacy GET remains compatible; formulas escaped',()=>{const t=setup();assert.equal(t.context.doGet({parameter:{}}).status,'ready');assert.equal(t.state().opens,0);assert.equal(t.context.doGet({parameter:{data:JSON.stringify({...valid,company_name:'=IMPORTXML("bad")'})}}).saved,true);assert.equal(t.tables['Audit Intake v2'][1][1][0],"'");});

test('formula-safe email storage does not corrupt a plus-prefixed mailbox',()=>{const t=setup();assert.equal(t.submit({...valid,email:'+qa@example.org'}).saved,true);assert.equal(t.sent[0].to,'+qa@example.org');});

test('receipt HTML and text retain matching paragraphs, readable mobile spacing, and safe references',()=>{
 const t=setup();const message=t.context.auditReceiptMessage_('jonathan@pickleadvisors.com','<test&reference>');
 assert.equal(message.subject,'Your free AI audit request is in');
 assert.equal(message.name,'Jonathan at Pickle Advisors');
 assert.match(message.body,/Hi there,\n\nThanks for reaching out/);
 assert.match(message.body,/Jonathan\nPickle Advisors/);
 assert.match(message.htmlBody,/width="100%"/);assert.match(message.htmlBody,/max-width:560px/);
 assert.match(message.htmlBody,/font-size:16px/);assert.match(message.htmlBody,/margin:0 0 18px/);
 assert.match(message.htmlBody,/&lt;test&amp;reference&gt;/);assert.doesNotMatch(message.htmlBody,/<test&reference>/);
 const decode=s=>s.replace(/&#39;/g,"'").replace(/&quot;/g,'"').replace(/&gt;/g,'>').replace(/&lt;/g,'<').replace(/&amp;/g,'&');
 for(const paragraph of message.body.split('\n\n').slice(0,5))assert.ok(decode(message.htmlBody).includes(paragraph));
 t.submit(valid);assert.ok(t.sent[0].htmlBody);assert.equal(t.sent[1].htmlBody,undefined);
});
