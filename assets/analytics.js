(() => {
  const tag = document.currentScript;
  if (!['pickleadvisors.com', 'www.pickleadvisors.com'].includes(location.hostname)) {
    window.pickleTrack = () => {};
    return;
  }
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', tag.dataset.analyticsId);
  const allowed = new Set(['audit_start','audit_step_view','audit_validation_error','audit_submit_attempt','audit_submit_error','generate_lead','inquiry_click']);
  window.pickleTrack = (name, detail = {}) => {
    if (!allowed.has(name)) return;
    const params = {};
    // Only categorical fields: never contact details, answers, receipt IDs, or URLs.
    for (const key of ['step','error_code','inquiry_type']) {
      if (typeof detail[key] === 'number' || /^[a-z_]{1,40}$/.test(detail[key] || '')) params[key] = detail[key];
    }
    window.gtag('event', name, params);
  };
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link) return;
    const url = new URL(link.href, location.href);
    if (url.protocol === 'mailto:') window.pickleTrack('inquiry_click', {inquiry_type: url.search.toLowerCase().includes('media') || link.textContent.toLowerCase().includes('media') ? 'media' : 'contact'});
    else if (url.origin === location.origin && url.pathname === '/audit/') window.pickleTrack('inquiry_click', {inquiry_type:'audit'});
  });
})();
