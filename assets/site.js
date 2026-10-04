(() => {
  const toggle = document.querySelector('[data-nav-toggle]');
  const menu = document.querySelector('[data-mobile-nav]');
  if (toggle && menu) {
    const close = () => {
      menu.classList.remove('is-open');
      menu.hidden = true;
      toggle.setAttribute('aria-label', 'Open navigation');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('menu-open');
    };
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      menu.classList.toggle('is-open', open);
      menu.hidden = !open;
      toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      document.body.classList.toggle('menu-open', open);
      if (open) menu.querySelector('a')?.focus();
    });
    menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
      close();
      const destination = new URL(link.href);
      if (destination.pathname === window.location.pathname) {
        document.getElementById(destination.hash.slice(1))?.focus({ preventScroll: true });
      }
    }));
    document.addEventListener('click', (event) => {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) close();
    });
    document.addEventListener('focusin', (event) => {
      if (!menu.contains(event.target) && !toggle.contains(event.target)) close();
    });
    window.matchMedia('(min-width: 641px)').addEventListener('change', (event) => {
      if (event.matches) close();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        close();
        toggle.focus();
      }
    });
  }

  const header = document.querySelector('.site-header');
  if (header && typeof ResizeObserver !== 'undefined') {
    new ResizeObserver(() => {
      document.documentElement.style.setProperty('--header-height', `${header.getBoundingClientRect().height}px`);
    }).observe(header);
  }
  const updateCurrent = () => {
    document.querySelectorAll('.primary-nav a, .mobile-nav a').forEach((link) => {
      const destination = new URL(link.href);
      if (destination.pathname === window.location.pathname && destination.hash === window.location.hash && destination.hash) {
        link.setAttribute('aria-current', 'location');
      } else link.removeAttribute('aria-current');
    });
  };
  window.addEventListener('hashchange', updateCurrent);
  window.addEventListener('pageshow', updateCurrent);
  updateCurrent();

  const year = document.querySelector('[data-year]');
  if (year) year.textContent = new Date().getFullYear();

  const alignInitialHash = () => {
    if (!window.location.hash) return;
    let id;
    try { id = decodeURIComponent(window.location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (target) {
      target.scrollIntoView({ block: 'start', behavior: 'auto' });
    }
  };
  if (window.location.hash) {
    const fontsReady = document.fonts?.ready || Promise.resolve();
    fontsReady.then(() => requestAnimationFrame(() => requestAnimationFrame(alignInitialHash)));
    window.addEventListener('load', () => setTimeout(alignInitialHash, 0), { once: true });
  }
})();
