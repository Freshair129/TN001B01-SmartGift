// Internal subprocess boundary: process exit releases native file handles on Windows.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const { GenesisDatabase } = require('@freshair129/gks-genesis-block-native');

async function main() {
  const [mode, inputPath, databasePath] = process.argv.slice(2);
  if (!['write', 'verify'].includes(mode)) throw Error('Unsupported projection operation');
  const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
  const nodes = new Map(input.nodes.map(n => [n.id, n]));
  assert.equal(nodes.size, input.nodes.length, 'duplicate node id');
  for (const node of nodes.values()) {
    assert.equal(node.tenant_id, 'Org-EtohGroup');
    assert.equal(node.business_id, 'SmartGift');
    assert.equal(node.classification, 'product_metadata');
    assert.equal(node.access_scope_ref, 'smartgift:internal:product-metadata');
  }
  for (const edge of input.edges) {
    assert(nodes.has(edge.from) && nodes.has(edge.to), 'dangling edge');
    assert.equal(edge.tenant_id, 'Org-EtohGroup');
    assert.equal(edge.business_id, 'SmartGift');
  }
  if (mode === 'write' && fs.existsSync(databasePath)) throw Error('Never overwrite a projection');
  const db = GenesisDatabase.open({path: databasePath, readOnly: mode === 'verify'});
  if (mode === 'write') {
    await db.bulkAddNodes(input.nodes.map(n => ({id: n.id, labels: [n.type], props: n})));
    await db.bulkAddEdges(input.edges.map(e => ({id: e.id, from: e.from, to: e.to, rel: e.rel,
      props: {tenant_id: e.tenant_id, business_id: e.business_id}})));
    await db.saveState();
    console.log('RESULT:' + JSON.stringify({written: true}));
    return;
  }
  assert.equal(db.statusSync().readOnly, true);
  const groups = new Map();
  for (const edge of input.edges) {
    for (const direction of ['out', 'in']) {
      const seed = direction === 'out' ? edge.from : edge.to;
      const target = direction === 'out' ? edge.to : edge.from;
      const key = JSON.stringify([seed, edge.rel, direction]);
      if (!groups.has(key)) groups.set(key, new Set());
      groups.get(key).add(target);
    }
  }
  const observed = new Set();
  for (const [key, expected] of groups) {
    // Offline rebuild verification, not a user query. Pilot contains 1,166 rows
    // from one prepared version; public reader limits remain 500 nodes/1,000 edges.
    if (expected.size > 5000) throw Error('Projection parity degree exceeds 5000; partition/review needed');
    const [seed, rel, direction] = JSON.parse(key);
    const rows = await db.neighbors(seed, {depth: 1, rels: [rel], direction, limit: expected.size + 1});
    assert.deepEqual(new Set(rows.map(r => r.node.id)), expected, 'native edge parity');
    for (const row of rows) {
      assert.deepEqual(row.node.props, nodes.get(row.node.id), 'native node metadata parity');
      observed.add(row.node.id);
    }
  }
  assert.equal(observed.size, nodes.size, 'unverified isolated nodes');
  console.log('RESULT:' + JSON.stringify({verified: true}));
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
