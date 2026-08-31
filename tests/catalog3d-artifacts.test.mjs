import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { GLTFLoader } from '../scripts/catalog3d/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import { sha256, validateGLB, validateMetadata, verifySources } from '../scripts/catalog3d/contracts.mjs';
import { applyVariant, geometryFingerprint, inspectModel } from '../scripts/catalog3d/models.mjs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.join(root, 'output/catalog-3d');
const json = async file => JSON.parse(await readFile(file, 'utf8'));
const index = await json(path.join(output, 'model_catalog.json'));

test('published index is review-only, with the generated candidates and three held legacy sources', () => {
  assert.equal(index.models.length, 0);
  assert.equal(index.review_candidates.length, 11);
  assert.equal(index.held.length, 3);
  assert.equal(index.public_ready, false);
});

for (const candidate of index.review_candidates) {
  test(`${candidate.code}: saved GLB, provenance, variants and four renders are consistent`, async () => {
    const glb = await readFile(path.join(output, candidate.path));
    const folder = path.dirname(path.join(output, candidate.path));
    const metadata = await json(path.join(folder, 'metadata.json'));
    const variants = await json(path.join(folder, 'variants.json'));
    validateMetadata(metadata);
    await verifySources(root, metadata.sources);
    assert.equal(metadata.glb_sha256, sha256(glb));
    assert.equal(candidate.glb_sha256, sha256(glb));
    const generatorModel = metadata.generator.name === 'smartgift-catalog3d-w502' ? 'models-w502.mjs' : metadata.generator.name === 'smartgift-catalog3d-bw00-estimated' ? 'models-bw00-estimated.mjs' : metadata.generator.name === 'smartgift-catalog3d-evidence-estimated' ? 'models-evidence-estimated.mjs' : 'models.mjs';
    assert.equal(metadata.generator.models_sha256, sha256(await readFile(path.join(root, 'scripts/catalog3d', generatorModel))));
    const report = await validateGLB(glb);
    assert.equal(report.issues.numErrors, 0);
    assert.equal(report.issues.numWarnings, 0);
    const loaded = await new GLTFLoader().parseAsync(glb.buffer.slice(glb.byteOffset, glb.byteOffset + glb.byteLength), '');
    const metrics = inspectModel(loaded.scene);
    assert.equal(metrics.triangles, metadata.metrics.triangles);
    assert.ok(metrics.triangles <= 50000);
    const before = geometryFingerprint(loaded.scene);
    for (const variant of variants.variants) {
      applyVariant(loaded.scene, variant.slots);
      assert.equal(geometryFingerprint(loaded.scene), before);
    }
    assert.equal(Object.keys(metadata.renders).length, 4);
    for (const render of Object.values(metadata.renders)) {
      const png = await readFile(path.join(folder, render.path));
      assert.equal(png.toString('hex', 0, 8), '89504e470d0a1a0a');
      assert.equal(png.readUInt32BE(16), 1200);
      assert.equal(png.readUInt32BE(20), 1200);
      assert.equal(sha256(png), render.sha256);
      assert.ok(render.visible_pixels > 5000);
    }
  });
}
