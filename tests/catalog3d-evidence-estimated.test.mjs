import test from 'node:test';
import assert from 'node:assert/strict';
import { EVIDENCE_ESTIMATED_RECIPES, makeEvidenceEstimatedModel } from '../scripts/catalog3d/models-evidence-estimated.mjs';
import { applyVariant, geometryFingerprint, inspectModel } from '../scripts/catalog3d/models.mjs';

test('seven partial-evidence products create finite review geometry and color variants reuse it', () => {
  assert.deepEqual(Object.keys(EVIDENCE_ESTIMATED_RECIPES).sort(), ['TBY17-1','TDK01-1','TJS00-1','TN00-2','TNA0014','TYS01-1','TZJ00-1']);
  for (const recipe of Object.values(EVIDENCE_ESTIMATED_RECIPES)) {
    const model = makeEvidenceEstimatedModel(recipe.code);
    const metrics = inspectModel(model);
    assert.ok(metrics.meshes >= 3, recipe.code);
    assert.ok(metrics.triangles > 100 && metrics.triangles < 50000, recipe.code);
    assert.ok(recipe.colors.length >= 1, recipe.code);
    const before = geometryFingerprint(model);
    applyVariant(model, { shell: recipe.colors[0].hex });
    assert.equal(geometryFingerprint(model), before, recipe.code);
  }
});
