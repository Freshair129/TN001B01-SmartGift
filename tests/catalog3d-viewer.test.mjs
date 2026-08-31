import test from 'node:test';
import assert from 'node:assert/strict';
import { request } from 'node:http';
import { createViewerServer } from '../scripts/catalog3d/viewer-server.mjs';

test('viewer exposes only local allowlisted assets and rejects unsafe requests', async () => {
  const server = await createViewerServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  const get = (url, options={}) => new Promise((resolve,reject) => {
    const req = request({ hostname:'127.0.0.1', port, path:url, ...options }, res => {
      const chunks=[]; res.on('data', b=>chunks.push(b));
      res.on('end',()=>resolve({ status:res.statusCode, headers:res.headers, body:Buffer.concat(chunks) }));
    }); req.on('error',reject); req.end();
  });
  try {
    const page = await get('/'); assert.equal(page.status,200);
    assert.match(page.body.toString(), /canvas/);
    assert.match(page.body.toString(), /reference-toggle/);
    assert.match(page.body.toString(), /category/);
    assert.match(page.headers['content-security-policy'], /connect-src 'self'/);
    const index = await get('/viewer-index.json'); assert.equal(index.status,200);
    const viewerIndex = JSON.parse(index.body);
    assert.equal(viewerIndex.categories.length,4);
    assert.deepEqual(viewerIndex.review_candidates.map(candidate=>candidate.asset_key).sort(), ['BW00-0','DW03','S1033','TBY17-1','TDK01-1','TJS00-1','TN00-2','TNA0014','TYS01-1','TZJ00-1','W502']);
    assert.deepEqual(viewerIndex.local_ready_assets,[]);
    assert.ok(viewerIndex.review_candidates.every(candidate=>candidate.counts_toward_product_master_completion === false));
    for (const url of ['/viewer.mjs','/viewer.css','/three/build/three.module.js',
      '/three/examples/jsm/loaders/GLTFLoader.js','/three/examples/jsm/controls/OrbitControls.js',
      '/three/examples/jsm/environments/RoomEnvironment.js','/three/examples/jsm/utils/BufferGeometryUtils.js']) {
      assert.equal((await get(url)).status,200,url);
    }
    for (const code of ['S1033','DW03','W502','BW00-0','TDK01-1','TJS00-1','TBY17-1','TN00-2','TNA0014','TZJ00-1','TYS01-1']) {
      const glb = await get(`/assets/${code}/model.glb`); assert.equal(glb.status,200);
      assert.equal(glb.body.toString('ascii',0,4),'glTF');
      const variants = await get(`/assets/${code}/variants.json`); assert.equal(variants.status,200);
      const colors=JSON.parse(variants.body);
      assert.deepEqual(Object.keys(colors).sort(),['default','variants']);
      assert.ok(colors.variants.length >= 1);
      assert.ok(colors.variants.some(variant=>variant.name===colors.default));
      for (const variant of colors.variants) assert.deepEqual(Object.keys(variant).sort(),['name','slots']);
      const reference = await get(`/reference/${code}.png`); assert.equal(reference.status,200);
      if (['BW00-0','TDK01-1'].includes(code)) {
        assert.equal(reference.headers['content-type'],'image/jpeg');
        assert.deepEqual(reference.body.subarray(0,3),Buffer.from([255,216,255]));
      } else {
        assert.equal(reference.headers['content-type'],'image/png');
        assert.deepEqual(reference.body.subarray(0,8),Buffer.from([137,80,78,71,13,10,26,10]));
      }
    }
    for (const url of ['/AGENTS.md','/metadata.json','/assets/DW03/metadata.json','/assets/W502/metadata.json',
      '/reference/UNKNOWN.png','/reference/DW03.pdf','/reference/DW03.png?file=../../AGENTS.md','/reference/../../output/catalog-internal/refs/single-DW03-source.png',
      '/product_master_evidence_registry.json','/product_master_evidence_input.json','/category_coverage_report.json','/evidence-request-matrix.md',
      '/data-pipeline/02_prepared/ProductMaster.json','/assets/UNKNOWN/model.glb','/three/../../package.json','/three/%2e%2e%2fpackage.json','/viewer.mjs?file=../../AGENTS.md']) {
      assert.equal((await get(url)).status,404,url);
    }
    assert.equal((await get('/',{method:'POST'})).status,405);
    assert.equal((await get('/',{headers:{origin:'https://not-local.example'}})).status,403);
    assert.equal((await get('/',{headers:{host:'not-local.example'}})).status,403);
    assert.equal((await get('/',{headers:{'sec-fetch-site':'cross-site'}})).status,403);
    assert.equal((await get('/',{method:'HEAD'})).body.length,0);
  } finally { server.closeAllConnections(); await new Promise(resolve=>server.close(resolve)); }
});
