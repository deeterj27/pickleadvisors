/* Pure intake rules shared by browser behavior and unit tests. */
(function(root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PickleAudit = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  const freeDomains = new Set(['gmail.com','googlemail.com','yahoo.com','hotmail.com','outlook.com','live.com','icloud.com','me.com','aol.com','proton.me','protonmail.com']);
  const personalEmail = email => freeDomains.has(String(email).trim().toLowerCase().split('@')[1]);
  function websiteHost(value) {
    if (!String(value).trim()) return '';
    try {
      const url = new URL(/^https?:\/\//i.test(value) ? value.trim() : 'https://' + value.trim());
      if (!['https:','http:'].includes(url.protocol) || !url.hostname.includes('.') || url.username || url.password) return '';
      return url.hostname;
    } catch (_) {return '';}
  }
  function validate(data, step, blockedEmails = []) {
    const error = (field,code,message) => ({field,code,message});
    if (step === 0) {
      for (const [field,label] of [['contact_name','your name and role'],['company_name','your company'],['q3_bottleneck_other','the main operating problem']]) {
        if (!String(data[field] || '').trim()) return error(field,'required','Please enter ' + label + '.');
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email || '')) return error('email','email','Please enter a valid email address.');
      if (blockedEmails.includes((data.email || '').trim().toLowerCase())) return error('email','blocked','We cannot accept this request through the form. Please contact Jonathan by email.');
      if ((data.q3_bottleneck_other || '').length > 1500) return error('q3_bottleneck_other','too_long','Please keep the operating problem under 1,500 characters.');
    }
    if (step === 1) {
      if (!data.q1_tools?.length) return error('q1_tools','tools','Choose at least one tool, or Other.');
      if (!data.q2_channels?.length) return error('q2_channels','channels','Choose at least one sales channel, or Other.');
    }
    if (step === 2) {
      if (!data.revenue_range) return error('revenue_range','revenue','Choose your monthly revenue range.');
      if (!data.q8_budget) return error('q8_budget','budget','Choose your implementation budget range.');
      if (personalEmail(data.email) && !websiteHost(data.website)) return error('website','website_required','Please include your company website when using a personal email address.');
      if (data.website && !websiteHost(data.website)) return error('website','website','Please enter a valid company website, such as yourcompany.com.');
    }
    if (data.company_url) return error('company_url','blocked','We could not send this request. Please contact Jonathan by email.');
    return null;
  }
  function payload(data) {
    const result = {};
    for (const key of ['company_name','contact_name','industry','revenue_range','team_size','website','email','phone','q8_budget','q11_source','q1_tools_other','q2_channels_other','q3_bottleneck_other','request_id','company_url']) result[key] = String(data[key] || '').trim();
    result.q1_tools = data.q1_tools || [];
    result.q2_channels = data.q2_channels || [];
    // Receiver combines selected categories and the written problem in its lead row.
    result.q3_bottleneck = ['Other'];
    return result;
  }
  async function send(endpoint, data, fetcher = fetch, signal) {
    const params = new URLSearchParams({data: JSON.stringify(payload(data))});
    // One POST, with an idempotency key. The redirect only retrieves Google’s result.
    const response = await fetcher(endpoint, {method:'POST', body:params, mode:'cors', credentials:'omit', redirect:'follow', cache:'no-store', signal});
    if (response.ok) {
      const result = await response.json();
      if (result.saved === true && typeof result.receiptId === 'string' && result.receiptId.length > 0) return {state:'confirmed'};
    }
    throw new Error('unconfirmed_receiver');
  }
  return {personalEmail, websiteHost, validate, payload, send};
});
