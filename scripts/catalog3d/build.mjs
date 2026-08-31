import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { sha256, verifySources, validateMetadata, validateGLB, publishIndex } from './contracts.mjs';
import { RECIPES } from './models.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const output = path.join(root, 'output/catalog-3d');
const sourceSet = JSON.parse(await readFile(path.join(here, 'sources.json'), 'utf8'));
const inputs = [sourceSet.pdf, sourceSet.manifest, ...sourceSet.products];
const requestedVersion = process.argv[2] || 'v001';
if (!/^v\d{3}$/.test(requestedVersion)) throw Error('version must be vNNN');
if (!process.env.PLAYWRIGHT_MODULE || !process.env.CATALOG3D_CHROMIUM) throw Error('Set PLAYWRIGHT_MODULE and CATALOG3D_CHROMIUM to existing local installations; see README');
await verifySources(root, inputs);
await mkdir(output, { recursive: true });

// The worker exposes only approved render modules and this run's GLB bytes.
// No repository-root static server, source document routes, or external requests.
const assets = new Map();
const server = createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://127.0.0.1');
    if (assets.has(url.pathname)) {
      response.setHeader('Content-Type', 'model/gltf-binary'); response.end(assets.get(url.pathname)); return;
    }
    let file;
    if (url.pathname === '/') file = path.join(here, 'render.html');
    else if (url.pathname === '/models.mjs') file = path.join(here, 'models.mjs');
    else if (url.pathname.startsWith('/three/')) {
      const base = path.join(here, 'node_modules/three');
      file = path.resolve(base, decodeURIComponent(url.pathname.slice(7)));
      if (!file.startsWith(base + path.sep) || !file.endsWith('.js')) throw Error('denied');
    } else { response.writeHead(404); response.end(); return; }
    response.setHeader('Content-Type', file.endsWith('.html') ? 'text/html' : 'text/javascript');
    response.end(await readFile(file));
  } catch { response.writeHead(404); response.end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
let browser;
const writeJSON = (file, value) => writeFile(file, JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
const candidates = [];
try {
  const { chromium } = await import(pathToFileURL(path.resolve(process.env.PLAYWRIGHT_MODULE)).href);
  console.log('Launching isolated local render worker');
  browser = await chromium.launch({ executablePath: process.env.CATALOG3D_CHROMIUM, headless: true, timeout: 30000,
    args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1200, height: 1200 }, deviceScaleFactor: 1 });
  const browserErrors = [];
  page.on('pageerror', error => { browserErrors.push(error.message); console.error(error.message); });
  await page.route('**/*', route => route.request().url().startsWith(origin + '/') ? route.continue() : route.abort());
  await page.goto(origin, { timeout: 30000 });
  await page.waitForFunction(() => window.ready === true, null, { timeout: 30000 });
  console.log('Render worker ready');
  const generator = { name: 'smartgift-catalog3d', version: '0.1.0', three: '0.160.0', chromium: browser.version(),
    models_sha256: sha256(await readFile(path.join(here, 'models.mjs'))),
    renderer_sha256: sha256(await readFile(path.join(here, 'render.html'))), method: 'local-photo-referenced-parametric-mesh' };
  for (const code of ['S1033', 'DW03']) {
    const source = sourceSet.products.find(item => item.code === code);
    const directory = path.join(output, code, requestedVersion);
    await mkdir(path.dirname(directory), { recursive: true });
    // Existing versions are immutable, including failed attempts.
    await mkdir(directory);
    const recipe = RECIPES[code];
    const result = await page.evaluate(async ({code,recipe}) => window.worker.exportModel(code, recipe), { code, recipe });
    const glb = Buffer.from(result.glb, 'base64');
    const validation = await validateGLB(glb);
    if (result.metrics.triangles > 50000 || result.imported.triangles !== result.metrics.triangles) throw Error('geometry budget/import mismatch');
    await writeFile(path.join(directory, 'model.glb'), glb, { flag: 'wx' });
    // Reopen the actual saved file, through a different URI, before taking any preview.
    assets.set(`/relocated/${code}/model.glb`, await readFile(path.join(directory, 'model.glb')));
    await page.evaluate(url => window.worker.loadFile(url), `/relocated/${code}/model.glb`);
    const renders = {};
    for (const view of ['front', 'back', 'side', 'straight']) {
      const frame = await page.evaluate(view => window.worker.capture(view), view);
      if (frame.visible_pixels < 5000) throw Error(`blank render ${code}/${view}`);
      const filename = view === 'front' ? 'preview.png' : `preview-${view}.png`;
      const bytes = Buffer.from(frame.png, 'base64');
      await writeFile(path.join(directory, filename), bytes, { flag: 'wx' });
      renders[view] = { path: filename, sha256: sha256(bytes), visible_pixels: frame.visible_pixels };
    }
    const palette = {
      White: ['#deded9','#cbcbc7','#999b97'], Black:['#232629','#343638','#111315'],
      Gray:['#8d9194','#73787c','#555a5d'], 'metal colour':['#acb0b1','#92989a','#71777a'],
      Blue:['#507ca7','#3a638d','#294463'], Purple:['#9877b0','#7e5d99','#604276'],
      Orange:['#ff8a26','#e66b27','#bc5420'],
    };
    const variants = { geometry_sha256: sha256(result.geometry), default: code === 'DW03' ? 'Orange' : 'White',
      color_evidence: `PDF page ${source.page} color list; RGB values are uncalibrated visual estimates`,
      variants: source.colors.map(name => ({ name, slots: Object.fromEntries(['shell','detail'].map((slot,i)=>[slot,palette[name][i]])),
        finish_status: name === 'metal colour' ? 'color-only approximation; finish not verified' : 'estimated from source, not colorimetric' })) };
    for (const variant of variants.variants) {
      const frame = await page.evaluate(slots => window.worker.capture('front', slots), variant.slots);
      if (frame.metrics.triangles !== result.imported.triangles || frame.visible_pixels < 5000) throw Error('variant render failed');
    }
    const metadata = {
      asset_key: code, asset_version: requestedVersion, source_product_code: code,
      canonical_product_id: null, mapping_status: 'unresolved',
      registry_refs: { doc_id: null, pic_id: null, status: 'unregistered', checked_by: 'exact source SHA-256 search of local registry: no match, 2026-08-31' },
      sources: [{ ...sourceSet.pdf, page: source.page, locator_status: 'page-code-visually-verified-2026-08-31' },
        { path: source.path, sha256: source.sha256, visual_origin: 'original-catalog-crop' }],
      dimensions: { unit: 'meter', body_xyz: source.body_mm.map(n=>n/1000), assembled_bounds_xyz: result.imported.bounds,
        source: source.dimension_source, source_annotation_not_factory_measurement: true },
      dimension_status: 'source-annotated',
      estimated_regions: code === 'S1033' ? ['rear stand angle and hinge depth','cable pose and cross section','underside','connector depth','material roughness'] :
        ['sidewall details','underside','connector depth and channel depth','case thickness profile','material roughness'],
      geometry_sha256: variants.geometry_sha256, glb_sha256: sha256(glb), generator,
      review_status: 'review-ready', rights_status: 'pending-owner-review', public_ready: false,
      omitted_details: 'unreadable tiny labels/certification marks and hidden mechanisms not fabricated',
      metrics: { ...result.imported, glb_bytes: glb.length }, renders,
    };
    validateMetadata(metadata);
    await writeJSON(path.join(directory, 'geometry-source.json'), { ...recipe, generator });
    await writeJSON(path.join(directory, 'variants.json'), variants);
    await writeJSON(path.join(directory, 'metadata.json'), metadata);
    await writeJSON(path.join(directory, 'validation.json'), validation);
    candidates.push({ code, path: `${code}/${requestedVersion}/model.glb`, metadata: `${code}/${requestedVersion}/metadata.json`,
      review_status: 'review-ready', glb_sha256: metadata.glb_sha256 });
    console.log(JSON.stringify({ code, ...metadata.metrics, validation_errors: validation.issues.numErrors, validation_warnings: validation.issues.numWarnings }));
  }
  if (browserErrors.length) throw Error(`render worker errors: ${browserErrors.join('; ')}`);
  await publishIndex(output, { generator: 'smartgift-catalog3d', schema_version: '0.1.0', models: [],
    review_candidates: candidates, held: ['S-1052', 'BST61401', 'UT3056', 'W502'],
    hold_reason: 'Owner review of first two models required before P2', public_ready: false }, () => verifySources(root, inputs));
  console.log('P1 package exported and re-import rendered; awaiting owner likeness review.');
} finally {
  if (browser) await browser.close();
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
}
