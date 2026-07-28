const [url, portArg = '9225'] = process.argv.slice(2);
if (!url) {
  console.error('usage: node qa-mobile-interactions.mjs <url> [port]');
  process.exit(1);
}

const pages = await (await fetch(`http://127.0.0.1:${portArg}/json`)).json();
const page = pages.find((candidate) => candidate.type === 'page');
if (!page) throw new Error('No page target');

const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  ws.addEventListener('open', resolve, { once: true });
  ws.addEventListener('error', reject, { once: true });
});

let id = 0;
const pending = new Map();
ws.addEventListener('message', (event) => {
  const message = JSON.parse(event.data.toString());
  if (!message.id || !pending.has(message.id)) return;
  const request = pending.get(message.id);
  pending.delete(message.id);
  message.error ? request.reject(new Error(JSON.stringify(message.error))) : request.resolve(message.result);
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const messageId = ++id;
  pending.set(messageId, { resolve, reject });
  ws.send(JSON.stringify({ id: messageId, method, params }));
});
const evaluate = async (expression, awaitPromise = false) => {
  const result = await send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
};

await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

const records = [];
for (const [width, height] of [[390, 844], [430, 932]]) {
  await send('Emulation.setDeviceMetricsOverride', {
    width, height, deviceScaleFactor: 1, mobile: true, screenWidth: width, screenHeight: height,
  });
  await send('Emulation.setTouchEmulationEnabled', { enabled: true });
  await send('Page.navigate', { url });
  await new Promise((resolve) => setTimeout(resolve, 1400));

  const result = await evaluate(`(async () => {
    const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const toggle = document.querySelector('[data-nav-toggle]');
    const menu = document.querySelector('[data-mobile-nav]');
    const firstMenuLink = menu?.querySelector('a');
    const mediaLink = [...(menu?.querySelectorAll('a') || [])].find((a) => a.getAttribute('href') === '#media');
    const toggleRect = toggle?.getBoundingClientRect();

    toggle?.click();
    await wait(60);
    const opened = toggle?.getAttribute('aria-expanded') === 'true' && menu?.classList.contains('is-open') && document.body.classList.contains('menu-open');
    const focusMoved = document.activeElement === firstMenuLink;

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    await wait(60);
    const escaped = toggle?.getAttribute('aria-expanded') === 'false' && !menu?.classList.contains('is-open') && document.activeElement === toggle;

    toggle?.click();
    mediaLink?.click();
    await wait(100);
    const menuLinkClosed = toggle?.getAttribute('aria-expanded') === 'false' && !menu?.classList.contains('is-open') && location.hash === '#media';

    const buttonRects = [...document.querySelectorAll('.button')].map((button) => {
      const rect = button.getBoundingClientRect();
      return { text: button.textContent.trim(), width: Math.round(rect.width), height: Math.round(rect.height), left: Math.round(rect.left), right: Math.round(rect.right) };
    });
    const sourceRects = [...document.querySelectorAll('.media-source-directory a')].map((link) => Math.round(link.getBoundingClientRect().height));
    const founder = document.querySelector('.clean-founder-photo img');
    const finalCta = document.querySelector('.ecosystem-close-action a[href="/audit/"]');
    const headings = [...document.querySelectorAll('.home-business-heading h2')].map((heading) => ({ text: heading.textContent.trim(), size: getComputedStyle(heading).fontSize }));

    return {
      width: innerWidth,
      noHorizontalOverflow: document.documentElement.scrollWidth === document.documentElement.clientWidth,
      nav: { opened, focusMoved, escaped, menuLinkClosed, toggleWidth: Math.round(toggleRect?.width || 0), toggleHeight: Math.round(toggleRect?.height || 0) },
      buttonsContained: buttonRects.every((rect) => rect.left >= 0 && rect.right <= innerWidth),
      buttonsMinHeight44: buttonRects.every((rect) => rect.height >= 44),
      buttonRects,
      sourceTapTargetsMin44: sourceRects.every((height) => height >= 44),
      sourceRects,
      founderImageLoaded: Boolean(founder?.complete && founder?.naturalWidth > 0),
      finalCtaPresent: Boolean(finalCta),
      fontsLoaded: document.fonts?.status === 'loaded',
      headings,
    };
  })()`, true);
  records.push(result);
}

const failures = [];
for (const record of records) {
  const checks = {
    noHorizontalOverflow: record.noHorizontalOverflow,
    navOpened: record.nav.opened,
    navFocusMoved: record.nav.focusMoved,
    navEscapeClosed: record.nav.escaped,
    navLinkClosed: record.nav.menuLinkClosed,
    navToggleMin44: record.nav.toggleWidth >= 44 && record.nav.toggleHeight >= 44,
    buttonsContained: record.buttonsContained,
    buttonsMinHeight44: record.buttonsMinHeight44,
    sourceTapTargetsMin44: record.sourceTapTargetsMin44,
    founderImageLoaded: record.founderImageLoaded,
    finalCtaPresent: record.finalCtaPresent,
    fontsLoaded: record.fontsLoaded,
  };
  for (const [name, passed] of Object.entries(checks)) {
    if (!passed) failures.push(`${record.width}px: ${name}`);
  }
}

console.log(JSON.stringify({ status: failures.length ? 'FAIL' : 'PASS', failures, records }, null, 2));
ws.close();
if (failures.length) process.exit(1);
