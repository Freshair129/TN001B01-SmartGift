import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const output = path.join(root, 'output/catalog-3d');
const safeKey = value => typeof value === 'string' && /^[A-Za-z0-9-]+$/.test(value);
const safeHash = value => typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value);

export async function createViewerServer() {
  const viewerIndexBytes = await readFile(path.join(output, 'viewer_index.json'));
  const viewerIndex = JSON.parse(viewerIndexBytes);
  if (!Array.isArray(viewerIndex.categories) || !Array.isArray(viewerIndex.review_candidates) || !Array.isArray(viewerIndex.local_ready_assets)) throw Error('Invalid viewer index');
  const products = [...viewerIndex.review_candidates, ...viewerIndex.local_ready_assets];
  const assets = new Map();
  assets.set('/viewer-index.json', ['application/json', Buffer.from(JSON.stringify(viewerIndex))]);
  for (const product of products) {
    if (!safeKey(product.asset_key) || !/^v\d{3}$/.test(product.asset_version) || !safeHash(product.glb_sha256) ||
        !safeKey(product.reference?.route_key) || product.reference.route_key !== product.asset_key || !safeHash(product.reference.sha256)) throw Error('Invalid viewer asset index');
    const referencePath = product.reference.source_path || `output/catalog-internal/refs/single-${product.asset_key}-source.png`;
    if (!/^(output\/catalog-internal\/refs\/single-[A-Za-z0-9-]+-source\.png|public\/assets\/catalog-media\/source-offer-[A-Za-z0-9-]+\.jpg|output\/catalog-3d\/reference-images\/[A-Za-z0-9-]+\.(png|jpeg))$/.test(referencePath)) throw Error('Invalid viewer reference path');
    const code = product.asset_key;
    const folder = path.resolve(output, code, product.asset_version);
    const model = await readFile(path.join(folder, 'model.glb'));
    if (createHash('sha256').update(model).digest('hex') !== product.glb_sha256) throw Error(`Model hash mismatch: ${code}`);
    assets.set(`/assets/${code}/model.glb`, ['model/gltf-binary', model]);
    const variants = JSON.parse(await readFile(path.join(folder, 'variants.json'), 'utf8'));
    assets.set(`/assets/${code}/variants.json`, ['application/json', Buffer.from(JSON.stringify({
      default: variants.default, variants: variants.variants.map(({name,slots}) => ({name,slots})),
    }))]);
    const reference = await readFile(path.resolve(root, referencePath));
    if (createHash('sha256').update(reference).digest('hex') !== product.reference.sha256) throw Error(`Reference hash mismatch: ${code}`);
    assets.set(`/reference/${code}.png`, [/\.(jpg|jpeg)$/.test(referencePath) ? 'image/jpeg' : 'image/png', reference]);
  }
  const files = new Map([
    ['/', 'viewer.html'], ['/viewer.mjs', 'viewer.mjs'], ['/viewer.css', 'viewer.css'],
    ...['build/three.module.js','examples/jsm/loaders/GLTFLoader.js','examples/jsm/controls/OrbitControls.js',
      'examples/jsm/environments/RoomEnvironment.js','examples/jsm/utils/BufferGeometryUtils.js']
      .map(file => [`/three/${file}`, `node_modules/three/${file}`]),
  ]);
  const server = createServer(async (request, response) => {
    const port = server.address().port;
    const localHosts = [`127.0.0.1:${port}`, `localhost:${port}`];
    if (!localHosts.includes(request.headers.host) ||
        (request.headers.origin && !localHosts.map(host=>`http://${host}`).includes(request.headers.origin)) ||
        request.headers['sec-fetch-site'] === 'cross-site') {
      response.writeHead(403); response.end('Local origin required'); return;
    }
    if (!['GET','HEAD'].includes(request.method)) { response.writeHead(405,{Allow:'GET, HEAD'}); response.end(); return; }
    response.setHeader('X-Content-Type-Options','nosniff');
    response.setHeader('Cache-Control','no-store');
    response.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data: blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");
    try {
      let data, type;
      if (assets.has(request.url)) [type,data] = assets.get(request.url);
      else if (files.has(request.url)) {
        const filename = files.get(request.url);
        data = await readFile(path.join(here,filename));
        type = filename.endsWith('.html') ? 'text/html; charset=utf-8' : filename.endsWith('.css') ? 'text/css' : 'text/javascript';
      } else { response.writeHead(404); response.end('Not found'); return; }
      response.writeHead(200, {'Content-Type':type, 'Content-Length':data.length});
      response.end(request.method === 'HEAD' ? undefined : data);
    } catch { response.writeHead(500); response.end('Viewer file unavailable'); }
  });
  return server;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const port = Number(process.argv[2] || 5190);
  if (!Number.isInteger(port) || port < 1024 || port > 65535) throw Error('Invalid local port');
  const server = await createViewerServer();
  server.on('error', error => { console.error(error.message); process.exitCode=1; });
  server.listen(port, '127.0.0.1', () => console.log(`SmartGift 3D viewer: http://127.0.0.1:${port}/`));
  process.on('SIGINT',()=>{ server.closeAllConnections(); server.close(); });
}
