// Deployed in the existing AI Audit project. Set the existing lead-sheet ID locally;
// never publish its identifier or lead contents in this repository.
var AUDIT_SHEET_ID = 'SET_EXISTING_SHEET_ID_BEFORE_DEPLOYMENT';
var AUDIT_VERSION = '2026-09-23';
function jsonResponse_(value) {
  return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON);
}
function doGet(e) {
  // Keep legacy clients working during rollout. Health checks never access lead data.
  if (e && e.parameter && e.parameter.data) return receiveAudit_(e.parameter.data);
  return jsonResponse_({status:'ready', version:AUDIT_VERSION});
}
function doPost(e) {
  return receiveAudit_(e && e.parameter && e.parameter.data);
}
function receiveAudit_(raw) {
  var lock;
  try {
    if (typeof raw !== 'string' || raw.length > 16000) throw new Error('invalid_request');
    var data = JSON.parse(raw);
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('invalid_request');
    function text(key, limit) {
      var value = data[key] == null ? '' : data[key];
      if (typeof value !== 'string' || value.length > (limit || 500)) throw new Error('invalid_fields');
      return value.trim();
    }
    function choices(key, other) {
      var values = data[key] || [];
      if (!Array.isArray(values) || values.length > 25 || values.some(function(v){return typeof v !== 'string' || v.length > 200;})) throw new Error('invalid_fields');
      return values.join(', ') + (text(other,1500) ? ': ' + text(other,1500) : '');
    }
    var company=text('company_name'),contact=text('contact_name'),email=text('email',254);
    var tools=choices('q1_tools','q1_tools_other'),channels=choices('q2_channels','q2_channels_other'),problem=choices('q3_bottleneck','q3_bottleneck_other');
    if (!company || !contact || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !tools || !channels || !problem || !text('revenue_range') || !text('q8_budget') || text('company_url')) throw new Error('invalid_fields');
    var receipt=text('request_id',80) || Utilities.getUuid();
    if (!/^[a-zA-Z0-9-]{20,80}$/.test(receipt)) throw new Error('invalid_request_id');
    // Plain strings cannot execute spreadsheet formulas.
    function cell(value) { return /^[=+\-@\t\r]/.test(value) ? "'" + value : value; }
    var row=[new Date(),company,contact,text('industry'),text('revenue_range'),text('team_size'),text('website'),email,text('phone'),tools,channels,problem,text('q4_financials'),text('q5_ai_usage'),text('q6_manual_hours'),text('q7_inventory'),text('q8_budget'),text('q9_extra_time',1500),text('q10_success',1500),text('q11_source'),receipt];
    row=row.map(function(value){return typeof value==='string'?cell(value):value;});
    lock=LockService.getScriptLock();lock.waitLock(20000);
    var sheet=SpreadsheetApp.openById(AUDIT_SHEET_ID).getSheets()[0];
    var last=sheet.getLastRow();
    if (last===0) {
      sheet.appendRow(['Timestamp','Company','Contact','Industry','Revenue','Team Size','Website','Email','Phone','Tools','Channels','Bottlenecks','Financials','AI Usage','Manual Hours','Inventory','Budget','10 Extra Hours','90-Day Success','Source','Request ID']);
      sheet.getRange(1,1,1,21).setFontWeight('bold');
    } else {
      sheet.getRange(1,21).setValue('Request ID');
      if (last>1 && sheet.getRange(2,21,last-1,1).createTextFinder(receipt).matchEntireCell(true).findNext()) return jsonResponse_({saved:true,receiptId:receipt});
    }
    sheet.appendRow(row);
    SpreadsheetApp.flush();
    return jsonResponse_({saved:true,receiptId:receipt});
  } catch(error) {
    // Do not echo contact data, sheet identifiers, or internal exception details.
    return jsonResponse_({saved:false,error:'request_not_confirmed'});
  } finally {
    if (lock && lock.hasLock()) lock.releaseLock();
  }
}
