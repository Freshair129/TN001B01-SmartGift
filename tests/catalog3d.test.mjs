import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { verifySources, validateMetadata, publishIndex, validateGLB } from '../scripts/catalog3d/contracts.mjs';
import { makeModel, geometryFingerprint, applyVariant, inspectModel } from '../scripts/catalog3d/models.mjs';

const hash = value => createHash('sha256').update(value).digest('hex');

test('source verification fails closed for missing, modified and escaping inputs', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'catalog3d-source-'));
  await writeFile(path.join(root, 'source.png'), 'synthetic reference');
  const sources = [{ path: 'source.png', sha256: hash('synthetic reference') }];
  assert.equal((await verifySources(root, sources)).length, 1);
  await assert.rejects(verifySources(root, [{ path: 'missing.png', sha256: hash('x') }]));
  await assert.rejects(verifySources(root, [{ path: '../outside.png', sha256: hash('x') }]), /outside/);
  await writeFile(path.join(root, 'source.png'), 'changed');
  await assert.rejects(verifySources(root, sources), /hash mismatch/);
});

test('unresolved source codes cannot masquerade as canonical ProductMaster IDs', () => {
  const record = { source_product_code: 'S1033', canonical_product_id: null,
    mapping_status: 'unresolved', dimension_status: 'source-annotated',
    estimated_regions: ['underside'], review_status: 'review-ready',
    rights_status: 'pending-owner-review', registry_refs: { status: 'unregistered' } };
  assert.doesNotThrow(() => validateMetadata(record));
  assert.throws(() => validateMetadata({ ...record, canonical_product_id: 'pm:S1033' }), /canonical/);
  assert.throws(() => validateMetadata({ ...record, dimension_status: undefined }), /dimension/);
});

test('publication is atomic, owner-review gated and preserves the previous index on failure', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'catalog3d-publish-'));
  const index = path.join(root, 'model_catalog.json');
  const previous = { generator: 'smartgift-catalog3d', models: [], review_candidates: [] };
  await writeFile(index, JSON.stringify(previous));
  await assert.rejects(publishIndex(root, { ...previous, models: ['new'] }, async () => { throw Error('input changed'); }));
  assert.deepEqual(JSON.parse(await readFile(index)), previous);
  await assert.rejects(publishIndex(root, { ...previous, models: [{ review_status: 'review-ready' }] }, async () => {}), /approved/);
  await writeFile(index, JSON.stringify({ generator: 'another-owner' }));
  await assert.rejects(publishIndex(root, previous, async () => {}), /owner/);
});

for (const code of ['S1033', 'DW03']) {
  test(`${code} has finite volumetric geometry and material changes reuse geometry`, () => {
    const model = makeModel(code);
    const result = inspectModel(model);
    assert.ok(result.triangles > 1000 && result.triangles <= 50000);
    assert.ok(result.bounds.every(size => size > 0.01));
    assert.ok(result.meshes > 8);
    for (const name of ['case-seam', 'back-cover', 'front-inset']) assert.ok(!model.getObjectByName(name), `unsupported panel ${name}`);
    const before = geometryFingerprint(model);
    applyVariant(model, { shell: '#101010' });
    assert.equal(geometryFingerprint(model), before);
    assert.throws(() => applyVariant(model, { nonexistent: '#ffffff' }), /material slot/);
    const mesh = model.getObjectByName('body');
    mesh.geometry.attributes.position.array[0] = NaN;
    assert.throws(() => inspectModel(model), /finite/);
  });
}
test('unknown model codes fail closed', () => assert.throws(() => makeModel('UNKNOWN'), /unsupported/));

test('DW03 charging tail sits below the disk face, without coplanar overlap', () => {
  const model = makeModel('DW03');
  assert.ok(model.getObjectByName('charging-tail').position.z < model.getObjectByName('charging-pad').position.z);
});

test('invalid GLB is rejected before publishing', async () => {
  await assert.rejects(validateGLB(Buffer.from('not a model')), /GLB/);
});
