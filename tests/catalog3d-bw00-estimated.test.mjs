import test from 'node:test';
import assert from 'node:assert/strict';
import { makeBW00EstimatedModel, BW00_ESTIMATED_RECIPE } from '../scripts/catalog3d/models-bw00-estimated.mjs';
import { geometryFingerprint, inspectModel } from '../scripts/catalog3d/models.mjs';

test('BW00-0 estimated candidate has the 230mm cylindrical body and a temperature-display lid', () => {
  const model = makeBW00EstimatedModel();
  const metrics = inspectModel(model);
  assert.deepEqual(BW00_ESTIMATED_RECIPE.body_mm, [65, 230, 65]);
  assert.ok(metrics.meshes >= 6);
  assert.ok(metrics.triangles > 500 && metrics.triangles < 50000);
  assert.ok(model.getObjectByName('temperature-display'));
  assert.ok(model.getObjectByName('lid'));
  const before = geometryFingerprint(model);
  model.traverse(node => { if (node.isMesh && node.material.name === 'shell') node.material.color.set('#194c7c'); });
  assert.equal(geometryFingerprint(model), before);
});
