import { createHash, randomUUID } from 'node:crypto';
import { readFile, writeFile, rename, realpath } from 'node:fs/promises';
import path from 'node:path';
import validator from 'gltf-validator';

export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');

export async function validateGLB(bytes) {
  if (bytes.length < 20 || bytes.toString('ascii', 0, 4) !== 'glTF' || bytes.readUInt32LE(4) !== 2 || bytes.readUInt32LE(8) !== bytes.length) throw Error('invalid GLB header');
  const json = JSON.parse(bytes.toString('utf8', 20, 20 + bytes.readUInt32LE(12)));
  if ([...(json.buffers || []), ...(json.images || [])].some(item => item.uri)) throw Error('GLB must be self-contained');
  if (bytes.length > 5 * 1024 * 1024) throw Error('GLB exceeds 5 MiB budget');
  const report = await validator.validateBytes(new Uint8Array(bytes), { maxIssues: 100 });
  if (report.issues.numErrors) throw Error(`GLB validation errors: ${JSON.stringify(report.issues)}`);
  return report;
}

export async function verifySources(root, sources) {
  const base = await realpath(root);
  const checked = [];
  for (const source of sources) {
    const target = path.resolve(base, source.path);
    const within = p => { const r = path.relative(base, p); return r && !r.startsWith('..') && !path.isAbsolute(r); };
    if (!within(target) || !within(await realpath(target))) throw Error('source outside workspace');
    const actual = sha256(await readFile(target));
    if (actual !== source.sha256) throw Error(`source hash mismatch: ${source.path}`);
    checked.push({ ...source, verified_sha256: actual });
  }
  return checked;
}

export function validateMetadata(record) {
  // This pilot deliberately cannot promote source codes into canonical records.
  if (record.canonical_product_id !== null || record.mapping_status !== 'unresolved') throw Error('canonical mapping requires separate verified approval');
  if (!['source-annotated', 'estimated'].includes(record.dimension_status)) throw Error('dimension status required');
  if (!Array.isArray(record.estimated_regions) || !record.estimated_regions.length) throw Error('estimated regions required for photo reconstruction');
  if (record.review_status !== 'review-ready' || record.rights_status !== 'pending-owner-review') throw Error('owner review required');
}

export async function publishIndex(root, next, recheck) {
  const destination = path.join(root, 'model_catalog.json');
  let previous;
  try { previous = await readFile(destination); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  if (previous && JSON.parse(previous).generator !== 'smartgift-catalog3d') throw Error('index owner mismatch');
  if (next.generator !== 'smartgift-catalog3d') throw Error('index owner mismatch');
  if (next.models.some(model => model.review_status !== 'approved')) throw Error('only owner-approved models can be published as ready');
  const temporary = path.join(root, `.index-${randomUUID()}.tmp`);
  await writeFile(temporary, JSON.stringify(next, null, 2) + '\n', { flag: 'wx' });
  await recheck();
  let current;
  try { current = await readFile(destination); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  if (String(current) !== String(previous)) throw Error('index changed during build');
  await rename(temporary, destination);
}
