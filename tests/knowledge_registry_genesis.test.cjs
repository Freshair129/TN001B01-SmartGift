// Synthetic metadata only. Each native database is isolated and closed by worker exit.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

test('Genesis persists typed metadata edges and reads them without embeddings', () => {
  const tmpRoot = path.resolve('tmp');
  fs.mkdirSync(tmpRoot, { recursive: true });
  const dir = fs.mkdtempSync(path.join(tmpRoot, 'knowledge-registry-capability-'));
  const write = `const {GenesisDatabase}=require('@freshair129/gks-genesis-block-native');
    (async()=>{const db=GenesisDatabase.open({path:process.argv[1]});
    await db.addNode({id:'doc:test',labels:['Document'],props:{scope:'test'}});
    await db.addNode({id:'ver:test',labels:['AssetVersion'],props:{scope:'test'}});
    await db.addEdge({id:'edge:test',from:'doc:test',to:'ver:test',rel:'HAS_VERSION'});
    await db.saveState(); console.log('WRITE_OK');})().catch(e=>{console.error(e);process.exitCode=1;});`;
  const first = spawnSync(process.execPath,['-e',write,dir],{encoding:'utf8',timeout:30000});
  assert.equal(first.status,0,first.stderr);
  assert.match(first.stdout,/WRITE_OK/);
  const read = `const {GenesisDatabase}=require('@freshair129/gks-genesis-block-native');
    (async()=>{const db=GenesisDatabase.open({path:process.argv[1],readOnly:true});
    const rows=await db.neighbors('doc:test',{depth:1,rels:['HAS_VERSION'],direction:'out',limit:10});
    const caps=db.queryIrCapabilities();
    console.log('RESULT:'+JSON.stringify({ids:rows.map(r=>r.node.id),caps,readOnly:db.statusSync().readOnly}));
    })().catch(e=>{console.error(e);process.exitCode=1;});`;
  const second=spawnSync(process.execPath,['-e',read,dir],{encoding:'utf8',timeout:30000});
  assert.equal(second.status,0,second.stderr);
  const result=JSON.parse(second.stdout.split('\n').find(x=>x.startsWith('RESULT:')).slice(7));
  assert.deepEqual(result.ids,['ver:test']);
  assert.equal(result.readOnly,true);
  assert.equal(result.caps.operations.traverse,'implemented');
});
