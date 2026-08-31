import test from 'node:test';
import assert from 'node:assert/strict';
import { makeW502Model, W502_RECIPE } from '../scripts/catalog3d/models-w502.mjs';
import { geometryFingerprint, inspectModel } from '../scripts/catalog3d/models.mjs';

test('W502 is a volumetric magnetic powerbank candidate and preserves geometry across its source colors', () => {
  const model = makeW502Model();
  const metrics = inspectModel(model);
  assert.ok(metrics.meshes >= 8);
  assert.ok(metrics.triangles > 1000 && metrics.triangles < 50000);
  assert.deepEqual(W502_RECIPE.body_mm,[71,110,18]);
  assert.ok(model.getObjectByName('magnetic-charging-pad'));
  assert.ok(model.getObjectByName('rear-stand'));
  const before=geometryFingerprint(model);
  model.traverse(node=>{if(node.isMesh && node.material.name==='shell')node.material.color.set('#171717');});
  assert.equal(geometryFingerprint(model),before);
});
