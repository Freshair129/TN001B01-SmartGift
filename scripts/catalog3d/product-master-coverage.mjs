import { createHash, randomUUID } from 'node:crypto';
import { access, readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const CATEGORY_NAMES = {
  'eco-friendly':'Eco-Friendly', 'classic-oriental':'Classic Oriental',
  'novelty-self-care':'Novelty Self-Care', 'executive-smart-tech':'Executive Smart Tech',
};
const REQUIRED_EVIDENCE = [
  'owner_verified_source_code_cross_reference', 'original_source_image_hash_and_locator',
  'width_height_depth_dimensions', 'front_back_or_side_angle_evidence',
];
const sha256 = value => createHash('sha256').update(value).digest('hex');

function ensure(condition, message) { if (!condition) throw Error(message); }
function categorySlug(categoryId) { return categoryId.slice('cat:'.length); }
function validHash(value) { return typeof value === 'string' && /^[a-f0-9]{64}$/i.test(value); }

function validateQueue(queue) {
  ensure(queue?.schema_ref === 'smartgift://b2b/portfolio/v1', 'unexpected schema_ref');
  ensure(Array.isArray(queue.categories) && Array.isArray(queue.items), 'queue categories and items are required');
  const categories = new Map(queue.categories.map(category => [category.id, category]));
  const ids = new Set();
  for (const item of queue.items) {
    ensure(item.product_master_id?.startsWith('pm:'), 'ProductMaster requires pm: ID');
    ensure(!ids.has(item.product_master_id), 'duplicate ProductMaster ID'); ids.add(item.product_master_id);
    ensure(item.edge_type === 'IN_CATEGORY', 'ProductMaster requires IN_CATEGORY');
    ensure(item.category_id?.startsWith('cat:') && categories.has(item.category_id), 'ProductMaster category is invalid');
    ensure(categories.get(item.category_id).product_master_ids.includes(item.product_master_id), 'ProductMaster category edge mismatch');
  }
  return categories;
}

function validateEvidence(entries, knownIds) {
  const byId = new Map();
  for (const entry of entries || []) {
    ensure(entry?.product_master_id?.startsWith('pm:') && knownIds.has(entry.product_master_id), 'evidence references noncanonical ProductMaster');
    ensure(!byId.has(entry.product_master_id), 'duplicate ProductMaster evidence');
    byId.set(entry.product_master_id, entry);
  }
  return byId;
}

function evidenceState(entry) {
  if (!entry) return { status:'hold_needs_verified_reference', selected_source_code:null, reasons:[...REQUIRED_EVIDENCE] };
  const dimensions = entry.dimensions?.body_mm;
  const gate = {
    owner: typeof entry.owner_verified_source_code === 'string' && entry.owner_verified_source_code === entry.selected_source_code,
    image: validHash(entry.source_image_sha256) && typeof entry.source_locator === 'string' && entry.source_locator.length > 0,
    dimensions: Array.isArray(dimensions) && dimensions.length === 3 && dimensions.every(value => typeof value === 'number' && value > 0),
    angles: Array.isArray(entry.angles) && entry.angles.some(angle => ['back','side'].includes(angle)) && entry.angles.includes('front'),
  };
  const reasons = [
    !gate.owner && 'owner_verified_source_code_cross_reference', !gate.image && 'original_source_image_hash_and_locator',
    !gate.dimensions && 'width_height_depth_dimensions', !gate.angles && 'front_back_or_side_angle_evidence',
  ].filter(Boolean);
  if (reasons.length) return { status:'hold_needs_verified_reference', selected_source_code:entry.selected_source_code || null, reasons };
  if (entry.owner_review === 'approved') return { status:'owner-approved', selected_source_code:entry.selected_source_code, reasons:[] };
  if (entry.geometry_review === 'passed') return { status:'geometry-review', selected_source_code:entry.selected_source_code, reasons:[] };
  return { status:'reference-ready', selected_source_code:entry.selected_source_code, reasons:[] };
}

function validateCandidate(candidate) {
  ensure(typeof candidate?.asset_key === 'string' && /^[A-Za-z0-9-]+$/.test(candidate.asset_key), 'invalid candidate asset key');
  ensure(/^v\d{3}$/.test(candidate.asset_version), 'invalid candidate asset version');
  ensure(validHash(candidate.glb_sha256), 'invalid candidate GLB hash');
  ensure(candidate.canonical_product_id === null || candidate.canonical_product_id?.startsWith('pm:'), 'invalid candidate canonical ID');
  ensure(candidate.mapping_status === 'unresolved' || candidate.mapping_status === 'resolved', 'invalid candidate mapping status');
  ensure(candidate.reference?.route_key === candidate.asset_key && validHash(candidate.reference.sha256), 'invalid candidate reference');
  if (candidate.reference.source_path !== undefined) ensure(typeof candidate.reference.source_path === 'string' && /^(output\/catalog-internal\/refs\/single-[A-Za-z0-9-]+-source\.png|public\/assets\/catalog-media\/source-offer-[A-Za-z0-9-]+\.jpg|output\/catalog-3d\/reference-images\/[A-Za-z0-9-]+\.(png|jpeg))$/.test(candidate.reference.source_path), 'invalid candidate reference path');
  if (candidate.mapping_status === 'resolved' || candidate.canonical_product_id) ensure(candidate.review_status === 'owner-approved', 'resolved candidate requires owner-approved review');
  ensure(!candidate.lifecycle || ['review-candidate','local-ready'].includes(candidate.lifecycle), 'invalid candidate lifecycle');
  if (candidate.lifecycle === 'local-ready') ensure(candidate.mapping_status === 'resolved' && candidate.canonical_product_id && candidate.review_status === 'owner-approved', 'local-ready asset requires resolved owner-approved mapping');
}

export function buildProductMasterCoverage({ queue, evidence = [], candidates = [] }) {
  const categoryMap = validateQueue(queue);
  const evidenceById = validateEvidence(evidence, new Set(queue.items.map(item => item.product_master_id)));
  let productMasters = queue.items.map(item => {
    const supplied = evidenceById.get(item.product_master_id);
    const state = evidenceState(supplied);
    return {
      canonical_product_id:item.product_master_id, product_code:item.product_code, name_th:item.name_th,
      category_id:item.category_id, edge_type:'IN_CATEGORY', selected_source_code:state.selected_source_code,
      source_image_sha256:supplied?.source_image_sha256 || null, source_locator:supplied?.source_locator || null,
      colors:Array.isArray(supplied?.colors) ? supplied.colors : [], dimensions:supplied?.dimensions || null,
      estimated_regions:Array.isArray(supplied?.estimated_regions) ? supplied.estimated_regions : [],
      lifecycle_status:state.status, hold_reasons:state.reasons, required_evidence:state.status === 'hold_needs_verified_reference' ? state.reasons : [],
      owner_review:supplied?.owner_review || 'not-requested', geometry_review:supplied?.geometry_review || 'not-started',
    };
  });
  const indexedAssets = candidates.map(candidate => {
    validateCandidate(candidate);
    return {
      asset_key:candidate.asset_key, asset_version:candidate.asset_version, glb_sha256:candidate.glb_sha256,
      source_product_code:candidate.source_product_code, canonical_product_id:candidate.canonical_product_id,
      mapping_status:candidate.mapping_status, candidate_category_id:candidate.candidate_category_id || null,
      review_status:candidate.review_status, lifecycle:candidate.lifecycle || 'review-candidate',
      reference:{ route_key:candidate.reference.route_key, sha256:candidate.reference.sha256, ...(candidate.reference.source_path ? {source_path:candidate.reference.source_path} : {}) },
      counts_toward_product_master_completion:candidate.lifecycle === 'local-ready',
    };
  });
  const localReadyById = new Map();
  for (const asset of indexedAssets.filter(asset => asset.lifecycle === 'local-ready')) {
    ensure(!localReadyById.has(asset.canonical_product_id), 'duplicate local-ready ProductMaster asset');
    const master = productMasters.find(item => item.canonical_product_id === asset.canonical_product_id);
    ensure(master?.lifecycle_status === 'owner-approved', 'local-ready asset requires owner-approved ProductMaster evidence');
    ensure(asset.candidate_category_id === master.category_id, 'local-ready asset category mismatch');
    localReadyById.set(asset.canonical_product_id, asset);
  }
  productMasters = productMasters.map(item => localReadyById.has(item.canonical_product_id) ? { ...item, lifecycle_status:'local-ready' } : item);
  const countsFor = items => ({
    total:items.length, reference_ready:items.filter(item=>item.lifecycle_status==='reference-ready').length,
    geometry_review:items.filter(item=>item.lifecycle_status==='geometry-review').length,
    owner_approved:items.filter(item=>['owner-approved','local-ready'].includes(item.lifecycle_status)).length,
    local_ready:items.filter(item=>item.lifecycle_status==='local-ready').length,
    held:items.filter(item=>item.lifecycle_status==='hold_needs_verified_reference').length,
  });
  const categories = queue.categories.map(category => {
    const items = productMasters.filter(item => item.category_id === category.id);
    return { id:category.id, slug:category.slug, name:CATEGORY_NAMES[category.slug] || category.slug, ...countsFor(items) };
  });
  const reviewCandidates = indexedAssets.filter(asset => asset.lifecycle === 'review-candidate');
  const localReadyAssets = indexedAssets.filter(asset => asset.lifecycle === 'local-ready').map(asset => ({ ...asset, category_id:asset.candidate_category_id }));
  const summary = { product_masters:productMasters.length, ...countsFor(productMasters), review_candidates:reviewCandidates.length };
  return {
    generator:'smartgift-catalog3d-product-master-coverage', schema_ref:queue.schema_ref, schema_version:queue.schema_version,
    scope:'canonical ProductMaster coverage only; local review planning; no graph writes', categories, product_masters:productMasters,
    summary, viewer_index:{
      schema_ref:queue.schema_ref, generated_for:'local viewer only; no public catalog promotion',
      categories:categories.map(({id,slug,name,total,reference_ready,geometry_review,owner_approved,local_ready,held})=>({id,slug,name,total,reference_ready,geometry_review,owner_approved,local_ready,held})),
      review_candidates:reviewCandidates, local_ready_assets:localReadyAssets,
    },
  };
}

function evidenceTemplate(queue) {
  return {
    schema_ref:queue.schema_ref, schema_version:queue.schema_version,
    purpose:'Owner-supplied, local-only evidence input. Do not enter customer, cost, quote, or PII data.',
    entries:queue.items.map(item => ({
      product_master_id:item.product_master_id, selected_source_code:null, owner_verified_source_code:null,
      source_image_sha256:null, source_locator:null, angles:[], colors:[], dimensions:null,
      estimated_regions:[], geometry_review:'not-started', owner_review:'not-requested',
    })),
  };
}

function evidenceMatrix(coverage) {
  const lines = ['# 3D ProductMaster evidence request matrix','', 'Generated local-only request list. Do not add customer/cost/quote data.','', '| Category | ProductMaster | Status | Required evidence |','|---|---|---|---|'];
  for (const item of coverage.product_masters) lines.push(`| ${item.category_id} | ${item.canonical_product_id} — ${item.name_th} | ${item.lifecycle_status} | ${item.required_evidence.join(', ') || '—'} |`);
  return lines.join('\n') + '\n';
}

async function atomicWrite(file, data) {
  const temporary = path.join(path.dirname(file), `.${path.basename(file)}-${randomUUID()}.tmp`);
  await writeFile(temporary, data, { flag:'wx' }); await rename(temporary, file);
}

async function loadCandidates(root, catalog) {
  const entries = [...(catalog.models || []), ...(catalog.review_candidates || [])];
  const result = [];
  for (const entry of entries) {
    const metadataPath = path.resolve(root, 'output/catalog-3d', entry.metadata);
    const metadataRoot = path.resolve(root, 'output/catalog-3d') + path.sep;
    ensure(metadataPath.startsWith(metadataRoot), 'candidate metadata escapes output root');
    const metadata = JSON.parse(await readFile(metadataPath, 'utf8'));
    const source = metadata.sources?.find(item => ['original-catalog-crop','original-catalog-photo','viewer-allowlisted-reference-copy'].includes(item.visual_origin));
    const sourcePath = source?.path;
    const expectedCrop = `output/catalog-internal/refs/single-${entry.code}-source.png`;
    const expectedPhoto = `public/assets/catalog-media/source-offer-${entry.code}.jpg`, expectedExtracted = `output/catalog-3d/reference-images/${entry.code}${path.extname(sourcePath || '')}`;
    ensure(source && [expectedCrop,expectedPhoto,expectedExtracted].includes(sourcePath) && validHash(source.sha256), 'candidate original reference is invalid');
    const binding = metadata.evidence_binding || {};
    result.push({
      asset_key:entry.code, asset_version:path.basename(path.dirname(entry.path)), glb_sha256:entry.glb_sha256,
      source_product_code:metadata.source_product_code, canonical_product_id:metadata.canonical_product_id ?? null,
      mapping_status:metadata.mapping_status, candidate_category_id:binding.candidate_category_id || null,
      reference:{ route_key:entry.code, sha256:source.sha256, source_path:sourcePath }, review_status:metadata.review_status,
      lifecycle:(catalog.models || []).some(model => model.code === entry.code && model.path === entry.path) ? 'local-ready' : 'review-candidate',
    });
  }
  return result;
}

export async function writeProductMasterCoverage(root) {
  const output = path.join(root, 'output/catalog-3d');
  const queueBytes = await readFile(path.join(output, 'product_master_queue.json'));
  const catalogBytes = await readFile(path.join(output, 'model_catalog.json'));
  const inputPath = path.join(output, 'product_master_evidence_input.json');
  const queue = JSON.parse(queueBytes), catalog = JSON.parse(catalogBytes);
  try { await access(inputPath); } catch { await atomicWrite(inputPath, JSON.stringify(evidenceTemplate(queue), null, 2) + '\n'); }
  const evidenceBytes = await readFile(inputPath);
  const coverage = buildProductMasterCoverage({ queue, evidence:JSON.parse(evidenceBytes).entries, candidates:await loadCandidates(root, catalog) });
  coverage.source_snapshot = {
    queue:{ path:'output/catalog-3d/product_master_queue.json', sha256:sha256(queueBytes) },
    model_catalog:{ path:'output/catalog-3d/model_catalog.json', sha256:sha256(catalogBytes) },
    evidence_input:{ path:'output/catalog-3d/product_master_evidence_input.json', sha256:sha256(evidenceBytes) },
  };
  await atomicWrite(path.join(output, 'product_master_evidence_registry.json'), JSON.stringify(coverage, null, 2) + '\n');
  await atomicWrite(path.join(output, 'category_coverage_report.json'), JSON.stringify({ ...coverage.summary, categories:coverage.categories }, null, 2) + '\n');
  await atomicWrite(path.join(output, 'viewer_index.json'), JSON.stringify(coverage.viewer_index, null, 2) + '\n');
  await atomicWrite(path.join(output, 'evidence-request-matrix.md'), evidenceMatrix(coverage));
  return coverage;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const coverage = await writeProductMasterCoverage(path.resolve(here, '../..'));
  console.log(`3D coverage: ${coverage.summary.product_masters} ProductMasters, ${coverage.summary.local_ready} local-ready, ${coverage.summary.held} held`);
}
