const {test}=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');
function setup({failWrite=false}={}){
 const rows=[];let locked=false,flushes=0,opens=0;
 const sheet={getLastRow:()=>rows.length,appendRow:row=>{if(failWrite)throw Error('storage error');rows.push(row)},getRange:(row,col)=>({setFontWeight(){},setValue(value){rows[row-1][col-1]=value},createTextFinder(value){return {matchEntireCell(){return this},findNext:()=>rows.slice(1).find(r=>r[20]===value)||null}}})};
 const context={ContentService:{MimeType:{JSON:'json'},createTextOutput:text=>({setMimeType:()=>JSON.parse(text)})},Utilities:{getUuid:()=> 'legacy-request-1234567890'},LockService:{getScriptLock:()=>({waitLock(){locked=true},hasLock:()=>locked,releaseLock(){locked=false}})},SpreadsheetApp:{openById:()=>{opens++;return {getSheets:()=>[sheet]}},flush(){flushes++}}};
 vm.createContext(context);vm.runInContext(fs.readFileSync('backend/Code.gs','utf8'),context);
 return {context,rows,state:()=>({locked,flushes,opens})};
}
const valid={request_id:'request-1234567890-abcdef',company_name:'Brand',contact_name:'Operator',email:'operator@example.org',q1_tools:['Other'],q1_tools_other:'Custom stock app',q2_channels:['Retail'],q3_bottleneck:['Other'],q3_bottleneck_other:'Inventory missing from orders',revenue_range:'$75K+',q8_budget:'$500-$2,000/mo'};
test('receiver stores the full problem and other answers, confirms only after flush, and deduplicates',()=>{
 const {context,rows,state}=setup();const submit=()=>context.doPost({parameter:{data:JSON.stringify(valid)}});
 assert.equal(submit().saved,true);assert.equal(rows.length,2);assert.match(rows[1][11],/Inventory missing/);assert.match(rows[1][9],/Custom stock app/);assert.equal(state().flushes,1);assert.equal(state().locked,false);
 assert.equal(submit().receiptId,valid.request_id);assert.equal(rows.length,2);assert.equal(state().flushes,1);
});
test('invalid input, honeypots, excessive strings and storage failures never report saved',()=>{
 for(const data of [{...valid,email:'bad'},{...valid,company_url:'bot'},{...valid,q1_tools:[{}]},{...valid,q3_bottleneck_other:'x'.repeat(1501)}]){const {context,rows}=setup();assert.equal(context.doPost({parameter:{data:JSON.stringify(data)}}).saved,false);assert.equal(rows.length,0)}
 const {context,state}=setup({failWrite:true});assert.equal(context.doPost({parameter:{data:JSON.stringify(valid)}}).saved,false);assert.equal(state().locked,false);
});
test('health checks expose no lead data and do not open the sheet; legacy GET remains compatible',()=>{
 const {context,rows,state}=setup();assert.equal(context.doGet({parameter:{}}).status,'ready');assert.equal(state().opens,0);
 assert.equal(context.doGet({parameter:{data:JSON.stringify(valid)}}).saved,true);assert.equal(rows.length,2);
});
test('spreadsheet formulas are escaped',()=>{const {context,rows}=setup();context.doPost({parameter:{data:JSON.stringify({...valid,company_name:'=IMPORTXML("bad")'})}});assert.equal(rows[1][1][0],"'");});
