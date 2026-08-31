import test from 'node:test';
import assert from 'node:assert/strict';
import { buildProductMasterCoverage } from '../scripts/catalog3d/product-master-coverage.mjs';

const queue = {
  schema_ref: 'smartgift://b2b/portfolio/v1', schema_version: '1.3.0',
  categories: [
    { id:'cat:eco-friendly', slug:'eco-friendly', product_master_ids:['pm:PM-BOTTLE-LED'] },
    { id:'cat:executive-smart-tech', slug:'executive-smart-tech', product_master_ids:['pm:PM-PB10K'] },
  ],
  items: [
    { product_master_id:'pm:PM-BOTTLE-LED', product_code:'PM-BOTTLE-LED', name_th:'ขวดน้ำ', category_id:'cat:eco-friendly', edge_type:'IN_CATEGORY', media_status:'no-code-matched-media', queue_status:'hold_needs_verified_reference', hold_reason:'no code-matched source-photo media' },
    { product_master_id:'pm:PM-PB10K', product_code:'PM-PB10K', name_th:'พาวเวอร์แบงก์', category_id:'cat:executive-smart-tech', edge_type:'IN_CATEGORY', media_status:'no-code-matched-media', queue_status:'hold_needs_verified_reference', hold_reason:'no code-matched source-photo media' },
  ],
};

test('coverage register holds unresolved ProductMasters and excludes unresolved candidates from completion', () => {
  const coverage = buildProductMasterCoverage({ queue, candidates:[{
    asset_key:'W502', asset_version:'v001', glb_sha256:'a'.repeat(64), source_product_code:'W502',
    canonical_product_id:null, mapping_status:'unresolved', candidate_category_id:'cat:executive-smart-tech',
    reference:{ sha256:'b'.repeat(64), route_key:'W502' }, review_status:'review-ready',
  }] });
  assert.equal(coverage.summary.product_masters,2);
  assert.equal(coverage.summary.held,2);
  assert.equal(coverage.summary.owner_approved,0);
  assert.equal(coverage.categories.find(category=>category.id==='cat:eco-friendly').held,1);
  assert.deepEqual(coverage.product_masters.map(item=>item.selected_source_code),[null,null]);
  assert.ok(coverage.product_masters.every(item=>item.required_evidence.includes('owner_verified_source_code_cross_reference')));
  assert.equal(coverage.viewer_index.review_candidates.length,1);
  assert.equal(coverage.viewer_index.review_candidates[0].canonical_product_id,null);
  assert.equal(coverage.viewer_index.review_candidates[0].counts_toward_product_master_completion,false);
  assert.equal(coverage.viewer_index.categories.length,2);
});

test('coverage register rejects noncanonical IDs, bad category edges, or candidates promoted without an approval', () => {
  assert.throws(()=>buildProductMasterCoverage({ queue:{...queue, items:[{...queue.items[0],product_master_id:'W502'}]}, candidates:[] }),/pm:/);
  assert.throws(()=>buildProductMasterCoverage({ queue:{...queue, items:[{...queue.items[0],category_id:'cat:wrong'}]}, candidates:[] }),/category/);
  assert.throws(()=>buildProductMasterCoverage({ queue, candidates:[{
    asset_key:'W502', asset_version:'v001', glb_sha256:'a'.repeat(64), source_product_code:'W502',
    canonical_product_id:'pm:PM-PB10K', mapping_status:'resolved', candidate_category_id:'cat:executive-smart-tech',
    reference:{ sha256:'b'.repeat(64), route_key:'W502' }, review_status:'review-ready',
  }] }),/owner-approved/);
});

test('owner-approved resolved asset becomes the only local-ready asset for its ProductMaster', () => {
  const evidence = [{
    product_master_id:'pm:PM-PB10K', selected_source_code:'W502', owner_verified_source_code:'W502',
    source_image_sha256:'b'.repeat(64), source_locator:'catalog page 7', angles:['front','side'],
    dimensions:{ body_mm:[71,110,18] }, colors:['White','Black'], estimated_regions:[], geometry_review:'passed', owner_review:'approved',
  }];
  const coverage = buildProductMasterCoverage({ queue, evidence, candidates:[{
    asset_key:'W502', asset_version:'v001', glb_sha256:'a'.repeat(64), source_product_code:'W502',
    canonical_product_id:'pm:PM-PB10K', mapping_status:'resolved', candidate_category_id:'cat:executive-smart-tech',
    reference:{ sha256:'b'.repeat(64), route_key:'W502' }, review_status:'owner-approved', lifecycle:'local-ready',
  }] });
  assert.equal(coverage.summary.local_ready,1);
  assert.equal(coverage.summary.owner_approved,1);
  assert.equal(coverage.viewer_index.local_ready_assets.length,1);
  assert.equal(coverage.viewer_index.review_candidates.length,0);
});

test('estimated BW00-0 keeps PM-TMB held and retains only its hash-pinned original reference route', () => {
  const evidence = [{
    product_master_id:'pm:PM-BOTTLE-LED', selected_source_code:'BW00-0', owner_verified_source_code:'BW00-0',
    source_image_sha256:'b'.repeat(64), source_locator:'Business Gift catalog page 77', angles:['front'],
    dimensions:null, colors:['Black'], estimated_regions:['body dimensions'], geometry_review:'not-started', owner_review:'not-requested',
  }];
  const coverage = buildProductMasterCoverage({ queue, evidence, candidates:[{
    asset_key:'BW00-0', asset_version:'v001', glb_sha256:'a'.repeat(64), source_product_code:'BW00-0',
    canonical_product_id:null, mapping_status:'unresolved', candidate_category_id:'cat:eco-friendly',
    reference:{ sha256:'b'.repeat(64), route_key:'BW00-0', source_path:'public/assets/catalog-media/source-offer-BW00-0.jpg' },
    review_status:'review-ready', lifecycle:'review-candidate',
  }] });
  const master = coverage.product_masters.find(item=>item.canonical_product_id==='pm:PM-BOTTLE-LED');
  assert.equal(master.lifecycle_status,'hold_needs_verified_reference');
  assert.deepEqual(master.hold_reasons,['width_height_depth_dimensions','front_back_or_side_angle_evidence']);
  const candidate = coverage.viewer_index.review_candidates[0];
  assert.equal(candidate.counts_toward_product_master_completion,false);
  assert.equal(candidate.reference.source_path,'public/assets/catalog-media/source-offer-BW00-0.jpg');
});
