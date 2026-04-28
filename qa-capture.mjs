import fs from 'node:fs/promises';

const [url, widthArg, heightArg, outPath, portArg = '9224'] = process.argv.slice(2);
if (!url || !widthArg || !heightArg || !outPath) {
  console.error('usage: node qa-capture.mjs <url> <width> <height> <outPath> [port]');
  process.exit(1);
}
const width = Number(widthArg);
const height = Number(heightArg);
const resp = await fetch(`http://127.0.0.1:${portArg}/json`);
const pages = await resp.json();
const page = pages.find((p) => p.type === 'page');
if (!page) throw new Error('No page target');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  ws.addEventListener('open', resolve, { once: true });
  ws.addEventListener('error', reject, { once: true });
});
let id = 0;
const pending = new Map();
ws.addEventListener('message', (event) => {
  const msg = JSON.parse(event.data.toString());
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
  }
});
function send(method, params = {}) {
  return new Promise((resolve, reject) => {
    const messageId = ++id;
    pending.set(messageId, { resolve, reject });
    ws.send(JSON.stringify({ id: messageId, method, params }));
  });
}
await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', {
  width, height, deviceScaleFactor: 1, mobile: width < 700, screenWidth: width, screenHeight: height,
});
await send('Emulation.setTouchEmulationEnabled', { enabled: width < 700 });
await send('Page.navigate', { url });
await new Promise((resolve) => setTimeout(resolve, 1800));
const metrics = await send('Runtime.evaluate', {
  expression: `(() => ({
    url: location.href,
    title: document.title,
    h1: document.querySelector('h1')?.textContent?.trim(),
    innerWidth: window.innerWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    innerHeight: window.innerHeight,
    scrollHeight: document.documentElement.scrollHeight,
    links: [...document.querySelectorAll('a')].slice(0,20).map(a => ({text:a.textContent.trim(), href:a.href}))
  }))()`,
  returnByValue: true,
});
console.log(JSON.stringify(metrics.result.value, null, 2));
const screenshot = await send('Page.captureScreenshot', { format: 'png', fromSurface: true });
await fs.mkdir(new URL('.', `file://${outPath}`).pathname, { recursive: true }).catch(() => {});
await fs.writeFile(outPath, Buffer.from(screenshot.data, 'base64'));
ws.close();
