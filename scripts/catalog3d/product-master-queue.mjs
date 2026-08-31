import { createHash, randomUUID } from 'node:crypto';
import { readFile, rename, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const CATEGORY_SLUGS = ['eco-friendly', 'classic-oriental', 'novelty-self-care', 'executive-smart-tech'];
const here = path.dirname(fileURLToPath(import.meta.url));
const sha256 = value => createHash('sha256').update(value).digest('hex');

export function buildProductMasterQueue({ records, edges, media }) {
  if (!Array.isArray(records) || !Array.isArray(edges?.IN_CATEGORY)) throw Error('ProductMaster records and IN_CATEGORY edges are required');
  const canonical = new Map();
  for (const record of records) {
    if (!record?.id?.startsWith('pm:')) throw Error('ProductMaster requires pm: ID');
    if (!CATEGORY_SLUGS.includes(record.category)) throw Error('ProductMaster category is not in schema');
    if (canonical.has(record.id)) throw Error('duplicate ProductMaster ID');
    canonical.set(record.id, record);
  }
  const categoryEdges = new Map();
  for (const edge of edges.IN_CATEGORY) {
    if (edge?.edge_type !== 'IN_CATEGORY' || !edge.source_id?.startsWith('pm:') || !edge.target_id?.startsWith('cat:')) throw Error('invalid IN_CATEGORY edge');
    if (!canonical.has(edge.source_id)) throw Error('IN_CATEGORY references non-canonical ProductMaster');
    if (categoryEdges.has(edge.source_id)) throw Error('duplicate IN_CATEGORY edge');
    categoryEdges.set(edge.source_id, edge);
  }
  const mediaByCode = new Map((media?.products || []).map(item => [item.code, item]));
  const items = [...canonical.values()].map(record => {
    const categoryId = `cat:${record.category}`;
    const edge = categoryEdges.get(record.id);
    if (!edge || edge.target_id !== categoryId) throw Error('ProductMaster missing type-correct IN_CATEGORY edge');
    const source = mediaByCode.get(record.code);
    const mediaStatus = source?.visual_status || 'no-code-matched-media';
    const ready = mediaStatus === 'source-photo';
    return {
      product_master_id: record.id,
      product_code: record.code,
      name_th: record.name_th,
      category_id: categoryId,
      edge_type: 'IN_CATEGORY',
      product_family_hint: record.product_family || null,
      media_status: mediaStatus,
      queue_status: ready ? 'ready_for_reference_review' : 'hold_needs_verified_reference',
      hold_reason: ready ? null : 'no code-matched source-photo media',
    };
  });
  const categories = CATEGORY_SLUGS.map(slug => ({
    id: `cat:${slug}`,
    slug,
    product_master_ids: items.filter(item => item.category_id === `cat:${slug}`).map(item => item.product_master_id),
  })).filter(category => category.product_master_ids.length);
  return {
    generator: 'smartgift-catalog3d-product-master-queue',
    schema_ref: 'smartgift://b2b/portfolio/v1',
    schema_version: '1.3.0',
    queue_scope: 'canonical ProductMaster only; local review planning; no graph writes',
    categories,
    items,
    summary: {
      categories: categories.length,
      product_masters: items.length,
      ready_for_reference_review: items.filter(item => item.queue_status === 'ready_for_reference_review').length,
      hold_needs_verified_reference: items.filter(item => item.queue_status === 'hold_needs_verified_reference').length,
    },
  };
}

export async function writeProductMasterQueue(root) {
  const [productMasterBytes, mediaBytes, schemaBytes] = await Promise.all([
    readFile(path.join(root, 'data-pipeline/02_prepared/ProductMaster.json')),
    readFile(path.join(root, 'public/data/catalog_media.json')),
    readFile(path.join(root, 'config/schema_genesisblock.yaml')),
  ]);
  const productMaster = JSON.parse(productMasterBytes);
  const queue = buildProductMasterQueue({ records: productMaster.records, edges: productMaster.edges, media: JSON.parse(mediaBytes) });
  queue.source_snapshot = {
    product_master: { path:'data-pipeline/02_prepared/ProductMaster.json', sha256:sha256(productMasterBytes) },
    catalog_media: { path:'public/data/catalog_media.json', sha256:sha256(mediaBytes) },
    schema: { path:'config/schema_genesisblock.yaml', sha256:sha256(schemaBytes) },
  };
  const destination = path.join(root, 'output/catalog-3d/product_master_queue.json');
  const temporary = path.join(path.dirname(destination), `.product-master-queue-${randomUUID()}.tmp`);
  await writeFile(temporary, JSON.stringify(queue, null, 2) + '\n', { flag:'wx' });
  await rename(temporary, destination);
  return queue;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = path.resolve(here, '../..');
  const queue = await writeProductMasterQueue(root);
  console.log(`3D queue: ${queue.summary.product_masters} ProductMaster records, ${queue.summary.ready_for_reference_review} ready, ${queue.summary.hold_needs_verified_reference} held`);
}
