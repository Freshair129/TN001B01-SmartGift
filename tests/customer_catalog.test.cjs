const { test } = require('node:test');
const assert = require('node:assert/strict');
const { buildCatalog, selectItems, sourcePhotos, detailComponents } = require('../public/customer-catalog.js');

const master = {
  canonical_products: [
    { code: 'ONE', name_th: 'กระบอกน้ำ', category_slug: 'eco-friendly', srp_price: 100, factory_cost: 40 },
    { code: 'TWO', name_th: 'สมุด', category_slug: 'executive-smart-tech' },
  ],
  catalog_offers: [
    { offer_code: 'SET', name: 'ชุดของขวัญ', interest_theme_slug: 'executive-smart-tech', components: [{ product_code: 'ONE', qty: 2 }] },
    { offer_code: 'TGC09-3', name: 'ชุดขัดแย้ง', interest_theme_slug: 'executive-smart-tech', components: [{ product_code: 'TWO', qty: 2 }] },
  ],
};
const media = { products: [
  { code: 'ONE', title: 'กระบอกน้ำ', image: '/assets/catalog-media/one.webp', generated_from_catalog: false, visual_status: 'source-photo' },
  { code: 'TWO', title: 'สมุด', image: '/assets/catalog-media/two.webp', generated_from_catalog: true, visual_status: 'generated-clean' },
] };

test('exact source-photo identity only; never generated or similar SKU', () => {
  const rows = buildCatalog(master, media);
  assert.equal(rows[0].image, '/assets/catalog-media/one.webp');
  assert.equal(rows[1].image, '');
  assert.equal(buildCatalog({ canonical_products: [{ code: 'ONE-2' }] }, media)[0].image, '');
});

test('selection covers exact category and kind, with no stale or truncated results', () => {
  const rows = buildCatalog(master, media);
  assert.deepEqual(selectItems(rows, 'eco-friendly', 'single').map(r => r.code), ['ONE']);
  assert.deepEqual(selectItems(rows, 'executive-smart-tech', 'set').map(r => r.code), ['SET', 'TGC09-3']);
  assert.equal(selectItems(rows, 'novelty-self-care', 'set').length, 0);
  assert.equal(selectItems(rows, '', 'set').length, 2);
});

test('customer records omit internal cost, arbitrary metadata and unapproved prices', () => {
  const row = buildCatalog(master, media)[0];
  assert.equal(row.factory_cost, undefined);
  assert.equal(row.srp_price, undefined);
  assert.equal(row.priceLabel, 'สอบถามราคา');
  assert.equal(JSON.stringify(row).includes('factory_cost'), false);
});

test('unverified BOM and known source conflict never presented as confirmed contents', () => {
  assert.equal(detailComponents(master.catalog_offers[0], master).status, 'pending');
  assert.equal(detailComponents(master.catalog_offers[1], master).status, 'conflict');
  assert.deepEqual(detailComponents(master.catalog_offers[0], master).items, []);
});

test('only explicitly verified BOM with valid component references and quantity can display', () => {
  const offer = { ...master.catalog_offers[0], bom_status: 'verified' };
  assert.deepEqual(detailComponents(offer, master), { status: 'verified', items: [{ name: 'กระบอกน้ำ', qty: 2 }] });
  assert.equal(detailComponents({ ...offer, components: [{ product_code: 'MISSING', qty: 1 }] }, master).status, 'pending');
  assert.equal(detailComponents({ ...offer, components: [{ product_code: 'ONE', qty: 0 }] }, master).status, 'pending');
});

test('source photo allowlist rejects path traversal, external URLs, ambiguous duplicate codes', () => {
  const products = [
    ...media.products,
    { ...media.products[0], code: 'BAD', image: '/assets/catalog-media/../private.webp' },
    { ...media.products[0], code: 'REMOTE', image: 'https://example.com/a.webp' },
    { ...media.products[0], code: 'QUERY', image: '/assets/catalog-media/a.webp?q=x' },
  ];
  assert.deepEqual(sourcePhotos({ products }).map(p => p.code), ['ONE']);
  assert.equal(sourcePhotos({ products: [products[0], products[0]] }).length, 0);
});

test('handles absent/malformed collections, escapes only at DOM boundary and isolates identities', () => {
  assert.deepEqual(buildCatalog(null, null), []);
  assert.deepEqual(buildCatalog({ canonical_products: {}, catalog_offers: null }), []);
  assert.deepEqual(sourcePhotos({ products: 'bad' }), []);
  const rows = buildCatalog({ canonical_products: [{ code: 'X', name_th: '<script>alert(1)</script>' }], catalog_offers: [{ offer_code: 'X', name: 'ชุด' }] });
  assert.equal(rows[0].name, '<script>alert(1)</script>');
  assert.notEqual(rows[0].id, rows[1].id);
});

test('supplier tags are not included in customer display names', () => {
  const rows = buildCatalog({catalog_offers:[{offer_code:'A', name:'ชุดกระบอกน้ำ A(P-02)'},{offer_code:'B',name:'ชุดสมุด B(P-16'}]});
  assert.equal(rows[0].name, 'ชุดกระบอกน้ำ A');
  assert.equal(rows[1].name, 'ชุดสมุด B');
});

test('offer-table membership is not proof that a record is a physical gift set', () => {
  const rows = buildCatalog(master, media);
  assert.equal(rows[0].kindLabel, 'สินค้ารายชิ้น');
  assert.equal(rows[2].kindLabel, 'รายการจากแคตตาล็อก');
});

test('HTML inline scripts remain valid and the customer page is wired before initialization', () => {
  const fs = require('node:fs');
  const vm = require('node:vm');
  const html = fs.readFileSync(require('node:path').join(__dirname, '../public/index.html'), 'utf8');
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  assert.ok(scripts.length > 0);
  scripts.forEach((match, index) => assert.doesNotThrow(() => new vm.Script(match[1], {filename:`inline-${index}`})));
  assert.ok(html.indexOf('src="./customer-catalog.js"') < html.indexOf('let catalogMaster'));
});
