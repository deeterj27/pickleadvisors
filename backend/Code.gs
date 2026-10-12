// Keep the existing spreadsheet, execution identity, and web-app access at deployment.
var AUDIT_SHEET_ID = 'SET_EXISTING_SHEET_ID_BEFORE_DEPLOYMENT';
var AUDIT_VERSION = '2026-10-12-receipt2';
var AUDIT_TAB = 'Audit Intake v2';
var AUDIT_OWNER = 'jonathan@pickleadvisors.com';
// Enable only after approval of script.send_mail and a controlled live email test.
var AUDIT_MAIL_ENABLED = false;
var AUDIT_HEADERS = ['Timestamp','Company','Contact','Industry','Revenue','Team Size','Website','Email','Phone','Tools','Channels','Bottlenecks','Financials','AI Usage','Manual Hours','Inventory','Budget','10 Extra Hours','90-Day Success','Source','Request ID','Payload Hash','Receipt Status','Owner Alert Status'];
function jsonResponse_(value) {
  return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON);
}
function doGet(e) {
  // Preserve legacy clients during rollout. Health checks never open the sheet.
  if (e && e.parameter && e.parameter.data) return receiveAudit_(e.parameter.data);
  return jsonResponse_({status:'ready', version:AUDIT_VERSION});
}
function doPost(e) { return receiveAudit_(e && e.parameter && e.parameter.data); }
function auditSheet_(book) {
  var sheet = book.getSheetByName(AUDIT_TAB);
  if (!sheet) sheet = book.insertSheet(AUDIT_TAB);
  if (!sheet.getLastRow()) {
    sheet.appendRow(AUDIT_HEADERS);
    SpreadsheetApp.flush();
  }
  var headers = sheet.getRange(1,1,1,AUDIT_HEADERS.length).getValues()[0];
  if (JSON.stringify(headers) !== JSON.stringify(AUDIT_HEADERS)) throw new Error('schema_mismatch');
  return sheet;
}
function findReceipt_(sheet, receipt) {
  var count=sheet.getLastRow()-1;
  if (count < 1) return null;
  return sheet.getRange(2,21,count,1).createTextFinder(receipt).matchEntireCell(true).matchCase(true).useRegularExpression(false).findNext();
}
function receiveAudit_(raw) {
  var lock, saved=false, receipt;
  try {
    if (typeof raw !== 'string' || raw.length > 16000) throw new Error('invalid_request');
    var data=JSON.parse(raw);
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('invalid_request');
    function text(key,limit) {
      var value=data[key] == null ? '' : data[key];
      if (typeof value !== 'string' || value.length > (limit || 500)) throw new Error('invalid_fields');
      return value.trim();
    }
    function choices(key,other) {
      var values=data[key] || [];
      if (!Array.isArray(values) || values.length>25 || values.some(function(v){return typeof v!=='string' || !v.trim() || v.length>200;})) throw new Error('invalid_fields');
      var extra=text(other,1500);
      return values.join(', ') + (extra ? ': '+extra : '');
    }
    var company=text('company_name'),contact=text('contact_name'),email=text('email',254);
    var tools=choices('q1_tools','q1_tools_other'),channels=choices('q2_channels','q2_channels_other'),problem=choices('q3_bottleneck','q3_bottleneck_other');
    if (!company || !contact || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || /[,;\r\n]/.test(email) || !tools || !channels || !problem || !text('revenue_range') || !text('q8_budget') || text('company_url')) throw new Error('invalid_fields');
    receipt=text('request_id',80) || Utilities.getUuid();
    if (!/^[a-zA-Z0-9-]{20,80}$/.test(receipt)) throw new Error('invalid_request_id');
    var answers=[company,contact,text('industry'),text('revenue_range'),text('team_size'),text('website'),email,text('phone'),tools,channels,problem,text('q4_financials'),text('q5_ai_usage'),text('q6_manual_hours'),text('q7_inventory'),text('q8_budget'),text('q9_extra_time',1500),text('q10_success',1500),text('q11_source')];
    var hash=Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,JSON.stringify(answers),Utilities.Charset.UTF_8));
    function cell(value) {return /^[=+\-@\t\r]/.test(value) ? "'"+value : value;}
    lock=LockService.getScriptLock();lock.waitLock(20000);
    var book=SpreadsheetApp.openById(AUDIT_SHEET_ID);
    // Historical rows were written under inconsistent headers. Never relabel or move them.
    var legacy=book.getSheetByName('Sheet1');
    if (legacy && legacy.getLastRow()>1 && legacy.getRange(1,21).getValue()==='Request ID' && findReceipt_(legacy,receipt)) {
      return jsonResponse_({saved:true,receiptId:receipt,notifications:'legacy'});
    }
    var sheet=auditSheet_(book),match=findReceipt_(sheet,receipt),rowNumber;
    if (match) {
      rowNumber=match.getRow();
      if (sheet.getRange(rowNumber,22).getValue()!==hash) return jsonResponse_({saved:false,error:'request_id_conflict'});
      SpreadsheetApp.flush();
    } else {
      sheet.appendRow([new Date()].concat(answers.map(cell),[receipt,hash,'pending','pending']));
      SpreadsheetApp.flush();
      rowNumber=sheet.getLastRow();
    }
    saved=true;
    notifyAudit_(sheet,rowNumber);
    return jsonResponse_({saved:true,receiptId:receipt,notifications:notificationStatus_(sheet,rowNumber)});
  } catch(error) {
    // A mail failure must never invite a second lead submission after durable storage.
    return jsonResponse_(saved ? {saved:true,receiptId:receipt,notifications:'pending'} : {saved:false,error:'request_not_confirmed'});
  } finally {if (lock && lock.hasLock()) lock.releaseLock();}
}
function notificationStatus_(sheet,row) {
  var statuses=sheet.getRange(row,23,1,2).getValues()[0];
  return statuses.every(function(s){return s==='sent';}) ? 'sent' : 'pending';
}
function notifyAudit_(sheet,row) {
  if (!AUDIT_MAIL_ENABLED) return;
  var values=sheet.getRange(row,1,1,AUDIT_HEADERS.length).getValues()[0];
  var receipt=values[20];
  [23,24].forEach(function(column) {
    var status=sheet.getRange(row,column);
    // 'sending'/'review' means delivery is ambiguous: never automatically resend.
    if (status.getValue()!=='pending') return;
    try {
      if (MailApp.getRemainingDailyQuota()<1) return;
      var owner=column===24;
      var recipient=String(values[7]).replace(/^'(?=[=+\-@])/, '');
      var message=owner ? {
        to:AUDIT_OWNER,name:'Pickle Advisors',replyTo:recipient,
        subject:'New AI audit request — '+receipt,
        body:'A new AI audit request is saved.\n\n'+AUDIT_HEADERS.slice(1,20).map(function(label,i){return label+': '+values[i+1];}).join('\n')+'\n\nReference: '+receipt+'\nReview the '+AUDIT_TAB+' tab in the existing AI Audit Responses spreadsheet.'
      } : auditReceiptMessage_(recipient,receipt);
      status.setValue('sending');SpreadsheetApp.flush();
      try {MailApp.sendEmail(message);} catch(error) {status.setValue('review');SpreadsheetApp.flush();return;}
      status.setValue('sent');SpreadsheetApp.flush();
    } catch(error) {
      // Preserve pending before send or sending after an uncertain send. No lead loss.
    }
  });
}
// Run only by the owner, or an approved time trigger. Never exposed by HTTP.
// Processes only pending messages; historical rows and uncertain sends are excluded.
function retryPendingAuditNotifications() {
  if (!AUDIT_MAIL_ENABLED) return;
  var lock=LockService.getScriptLock();lock.waitLock(20000);
  try {
    var sheet=auditSheet_(SpreadsheetApp.openById(AUDIT_SHEET_ID));
    var processed=0;
    for (var row=2;row<=sheet.getLastRow() && processed<20;row++) {
      if (sheet.getRange(row,23,1,2).getValues()[0].indexOf('pending')!==-1) {notifyAudit_(sheet,row);processed++;}
    }
  } finally {lock.releaseLock();}
}

// Shared content keeps the HTML email and plain-text fallback in sync.
function auditReceiptMessage_(recipient,receipt) {
  var paragraphs=[
    'Hi there,',
    "Thanks for reaching out. I've received your request for a free AI audit.",
    "I'll review your answers and email you with next steps. If it looks like a fit, we'll arrange a free 30-minute conversation. No call has been booked yet.",
    'The audit is free. Any implementation work would be scoped and priced separately.',
    "If you'd like to add anything, just reply to this email."
  ];
  function escape(value) {return String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
  var body=paragraphs.join('\n\n')+'\n\nJonathan\nPickle Advisors\n\nReference: '+receipt;
  var html='<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="margin:0;padding:0;background:#ffffff;">'+
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="left" style="padding:24px 16px;">'+
    '<div style="max-width:560px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#202020;">'+
    paragraphs.map(function(p){return '<p style="margin:0 0 18px;">'+escape(p)+'</p>';}).join('')+
    '<p style="margin:24px 0 0;">Jonathan<br><span style="color:#555555;">Pickle Advisors</span></p>'+
    '<p style="margin:28px 0 0;padding-top:16px;border-top:1px solid #e5e5e5;font-size:12px;line-height:1.5;color:#666666;word-break:break-all;">Reference: '+escape(receipt)+'</p>'+
    '</div></td></tr></table></body></html>';
  return {to:recipient,name:'Jonathan at Pickle Advisors',replyTo:AUDIT_OWNER,subject:'Your free AI audit request is in',body:body,htmlBody:html};
}
