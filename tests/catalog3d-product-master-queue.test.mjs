import test from 'node:test';
import assert from 'node:assert/strict';
import { buildProductMasterQueue } from '../scripts/catalog3d/product-master-queue.mjs';

const records = [{ id:'pm:PM-TMB', code:'PM-TMB', name_th:'แก้ว', category:'eco-friendly', product_family:'PF-DRINKWARE' }];
const edges = { IN_CATEGORY:[{ edge_type:'IN_CATEGORY', source_id:'pm:PM-TMB', target_id:'cat:eco-friendly' }] };

test('queue follows typed Category <- IN_CATEGORY <- ProductMaster and holds unverified media', () => {
  const queue = buildProductMasterQueue({ records, edges, media:{ products:[{ code:'PM-TMB', visual_status:'fallback-placeholder' }] } });
  assert.deepEqual(queue.summary, { categories:1, product_masters:1, ready_for_reference_review:0, hold_needs_verified_reference:1 });
  assert.deepEqual(queue.categories[0], { id:'cat:eco-friendly', slug:'eco-friendly', product_master_ids:['pm:PM-TMB'] });
  assert.deepEqual(queue.items[0], {
    product_master_id:'pm:PM-TMB', product_code:'PM-TMB', name_th:'แก้ว', category_id:'cat:eco-friendly',
    edge_type:'IN_CATEGORY', product_family_hint:'PF-DRINKWARE', media_status:'fallback-placeholder',
    queue_status:'hold_needs_verified_reference', hold_reason:'no code-matched source-photo media',
  });
});

test('queue fails closed for missing canonical IDs, invalid categories, or mismatched edges', () => {
  assert.throws(() => buildProductMasterQueue({ records:[{...records[0], id:'S1033'}], edges, media:{products:[]} }), /pm:/);
  assert.throws(() => buildProductMasterQueue({ records:[{...records[0], category:'other'}], edges, media:{products:[]} }), /category/);
  assert.throws(() => buildProductMasterQueue({ records, edges:{IN_CATEGORY:[]}, media:{products:[]} }), /IN_CATEGORY/);
});
