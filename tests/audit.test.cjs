const {test} = require('node:test');
const assert = require('node:assert/strict');
const core = require('../assets/audit-core.js');
const valid = {company_name:'Sample brand',contact_name:'Sample operator',email:'operator@example.org',q3_bottleneck_other:'Orders do not match inventory',q1_tools:['Shopify'],q2_channels:['Retail (grocery, specialty)'],revenue_range:'$75K+',q8_budget:'$500-$2,000/mo',website:''};
test('each step validates only its own questions',()=>{
 assert.equal(core.validate(valid,0),null);assert.equal(core.validate(valid,1),null);assert.equal(core.validate(valid,2),null);
 assert.equal(core.validate({...valid,q1_tools:[]},0),null);
 assert.equal(core.validate({...valid,q1_tools:[]},1).field,'q1_tools');
 assert.equal(core.validate({...valid,q2_channels:[]},1).field,'q2_channels');
 assert.equal(core.validate({...valid,q8_budget:''},2).field,'q8_budget');
});
test('personal email website requirement is explicit and domain parsing is robust',()=>{
 assert.equal(core.validate({...valid,email:'OPERATOR@GMAIL.COM'},2).code,'website_required');
 assert.equal(core.validate({...valid,email:'operator@gmail.com',website:'example.org'},2),null);
 assert.equal(core.websiteHost('https://example.org/path'),'example.org');
 assert.equal(core.websiteHost('javascript:alert(1)'), '');
 assert.equal(core.websiteHost('https://name:password@example.org'), '');
});
test('missing input and honeypot fail without elapsed-time restrictions',()=>{
 assert.equal(core.validate({...valid,company_name:''},0).field,'company_name');
 assert.equal(core.validate({...valid,email:'invalid'},0).field,'email');
 assert.equal(core.validate({...valid,company_url:'spam'},0).code,'blocked');
 assert.equal(core.validate({...valid,email:'operator@example.org'},0,['operator@example.org']).code,'blocked');
 assert.equal(core.validate({...valid,q3_bottleneck_other:'x'.repeat(1501)},0).code,'too_long');
});
test('payload retains the receiver fields and preserves the problem, idempotency key, and honeypot',()=>{
 const data=core.payload({...valid,company_url:'do not send',secret:'not allowed'});
 assert.deepEqual(data.q3_bottleneck,['Other']);assert.equal(data.q3_bottleneck_other,valid.q3_bottleneck_other);
 assert.equal(data.phone,'');assert.equal(data.company_url,'do not send');assert.equal(data.secret,undefined);
});
test('one private POST follows the result redirect without an automatic retry',async()=>{
 let calls=0;
 const result=await core.send('https://example.org/receiver',{...valid,request_id:'test-request-id-123456789'},async(url,options)=>{calls++;assert.equal(url,'https://example.org/receiver');assert.equal(options.method,'POST');assert.equal(options.redirect,'follow');assert.equal(options.credentials,'omit');assert.equal(JSON.parse(options.body.get('data')).request_id,'test-request-id-123456789');return {ok:true,json:async()=>({saved:true,receiptId:'test-receipt'})};});
 assert.equal(result.state,'confirmed');assert.equal(calls,1);
});
test('only a saved receipt can count as a confirmed lead',async()=>{
 assert.equal((await core.send('https://example.org',valid,async()=>({ok:true,json:async()=>({saved:true,receiptId:'test-receipt'})}))).state,'confirmed');
 for (const body of [{ok:true},{saved:true},{saved:false,receiptId:'x'}]) await assert.rejects(core.send('https://example.org',valid,async()=>({ok:true,json:async()=>body})));
});
test('network failure is not automatically retried',async()=>{let calls=0;await assert.rejects(core.send('https://example.org',valid,async()=>{calls++;throw new Error('offline');}));assert.equal(calls,1);});
