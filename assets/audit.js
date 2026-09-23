(() => {
  const form = document.getElementById('auditForm');
  if (!form) return;
  const core = window.PickleAudit;
  const config = JSON.parse(document.getElementById('auditConfig').textContent);
  const steps = [...form.querySelectorAll('.audit-step')];
  const back = document.getElementById('previousStep');
  const next = document.getElementById('nextStep');
  const submit = document.getElementById('submitAudit');
  const errorBox = document.getElementById('formError');
  const status = document.getElementById('sendingStatus');
  const requestId = crypto.randomUUID();
  let step = 0, started = false, submitting = false, completed = false;
  const track = (name,detail) => window.pickleTrack?.(name,detail);
  function collect() {
    const fd = new FormData(form), data = Object.fromEntries(fd.entries());
    data.q1_tools = fd.getAll('q1_tools'); data.q2_channels = fd.getAll('q2_channels');
    data.request_id = requestId;
    return data;
  }
  function start() {if (!started) {started = true; track('audit_start');}}
  form.addEventListener('input', start, {once:true});
  form.addEventListener('change', start, {once:true});
  function clearError() {
    errorBox.hidden = true; errorBox.textContent = '';
    form.querySelectorAll('[aria-invalid]').forEach(el => {el.removeAttribute('aria-invalid');el.setAttribute('aria-describedby',(el.getAttribute('aria-describedby') || '').split(' ').filter(x => x && x !== 'formError').join(' '));});
  }
  function showError(error) {
    errorBox.textContent = error.message; errorBox.hidden = false;
    const field = form.elements.namedItem(error.field);
    const focus = field instanceof Element ? field : field?.[0];
    if (focus && error.field !== 'company_url') {
      focus.setAttribute('aria-invalid','true');
      focus.setAttribute('aria-describedby',((focus.getAttribute('aria-describedby') || '') + ' formError').trim());
      focus.focus();
    } else errorBox.focus();
    track('audit_validation_error',{step:step+1,error_code:error.code});
  }
  function updateWebsite() {
    const required = core.personalEmail(form.elements.email.value);
    form.elements.website.required = required;
    document.getElementById('websiteRequirement').textContent = required ? '(required with a personal email)' : '(optional)';
  }
  function review() {
    const data = collect();const dl = document.getElementById('reviewAnswers');dl.replaceChildren();
    for (const [key,label] of [['contact_name','Name and role'],['company_name','Company'],['email','Email'],['q3_bottleneck_other','Operating problem'],['q1_tools','Tools'],['q2_channels','Sales channels'],['revenue_range','Monthly revenue'],['q8_budget','Implementation budget'],['website','Website']]) {
      const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=Array.isArray(data[key])?data[key].join(', '):data[key] || 'Not supplied';row.append(dt,dd);dl.append(row);
    }
  }
  function showStep(value,focus=true) {
    step=value;steps.forEach((el,i)=>{el.hidden=i!==step;});
    form.querySelectorAll('[data-step-label]').forEach((el,i)=>{if(i===step)el.setAttribute('aria-current','step');else el.removeAttribute('aria-current');});
    back.hidden=step===0;next.hidden=step===2;submit.hidden=step!==2;
    next.textContent=step===0?'Continue to your workflow':'Continue to fit + review';
    document.getElementById('stepStatus').textContent='Step '+(step+1)+' of 3';
    if(step===2){updateWebsite();review();}
    if(focus){steps[step].setAttribute('tabindex','-1');steps[step].focus();}
    track('audit_step_view',{step:step+1});
  }
  function advance() {start();clearError();const error=core.validate(collect(),step,config.blocked_emails);if(error){showError(error);return;}showStep(step+1);}
  next.addEventListener('click',advance);
  back.addEventListener('click',()=>{clearError();showStep(step-1);});
  form.elements.email.addEventListener('input',updateWebsite);
  form.addEventListener('input',()=>{if(step===2)review();});
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(submitting || completed)return;
    if(step<2){advance();return;}
    clearError();const data=collect();
    for(let i=0;i<3;i++){const error=core.validate(data,i,config.blocked_emails);if(error){showStep(i,false);showError(error);return;}}
    submitting=true;submit.disabled=true;back.disabled=true;submit.textContent='Sending request…';
    status.textContent='Sending once. Please keep this page open.';track('audit_submit_attempt');
    const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),25000);
    try{
      await core.send(form.dataset.endpoint,data,fetch,controller.signal);
      completed=true;form.hidden=true;
      const thanks=document.getElementById('thankYou');thanks.hidden=false;
      document.getElementById('responseTitle').textContent='Your request is received.';
      document.getElementById('responseDetail').textContent='Jonathan will review your answers and email next steps. A call has not been booked automatically.';
      track('generate_lead');thanks.focus();
    }catch(error){
      status.textContent='';
      errorBox.replaceChildren();const text=document.createElement('p');text.textContent='We could not confirm your request. It may have reached us, so please email Jonathan before trying again.';
      const link=document.createElement('a');link.href='mailto:'+config.email;link.textContent=config.email;errorBox.append(text,link);errorBox.hidden=false;errorBox.focus();
      track('audit_submit_error',{error_code:error.name==='AbortError'?'timeout':'unconfirmed'});
      submit.textContent='Retry request';submit.disabled=false;back.disabled=false;
    }finally{clearTimeout(timer);submitting=false;}
  });
  showStep(0,false);
})();
