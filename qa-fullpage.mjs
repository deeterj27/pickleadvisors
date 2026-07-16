import fs from 'node:fs/promises';

const [url, widthArg, heightArg, outPath, portArg = '9224'] = process.argv.slice(2);
if (!url || !widthArg || !heightArg || !outPath) {
  console.error('usage: node qa-fullpage.mjs <url> <width> <height> <outPath> [port]');
  process.exit(1);
}
const width = Number(widthArg);
const height = Number(heightArg);
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
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', {
  width,
  height,
  deviceScaleFactor: 1,
  mobile: width < 700,
  screenWidth: width,
  screenHeight: height,
});
await send('Emulation.setTouchEmulationEnabled', { enabled: width < 700 });
await send('Page.navigate', { url });
await new Promise((resolve) => setTimeout(resolve, 1800));
await send('Runtime.evaluate', {
  expression: `new Promise(async (resolve) => {
    const step = Math.max(500, window.innerHeight * 0.8);
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
      window.scrollTo(0, y);
      await new Promise((next) => setTimeout(next, 110));
    }
    window.scrollTo(0, 0);
    await new Promise((next) => setTimeout(next, 500));
    resolve(true);
  })`,
  awaitPromise: true,
  returnByValue: true,
});
const layout = await send('Page.getLayoutMetrics');
const content = layout.cssContentSize;
const result = await send('Page.captureScreenshot', {
  format: 'png',
  fromSurface: true,
  captureBeyondViewport: true,
  clip: { x: 0, y: 0, width: content.width, height: content.height, scale: 1 },
});
await fs.mkdir(new URL('.', `file://${outPath}`).pathname, { recursive: true }).catch(() => {});
await fs.writeFile(outPath, Buffer.from(result.data, 'base64'));
console.log(JSON.stringify({ url, width, viewportHeight: height, contentWidth: content.width, contentHeight: content.height, outPath }, null, 2));
ws.close();
