import { createServer } from 'node:http';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { publishIndex, sha256, validateGLB, validateMetadata, verifySources } from './contracts.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const output=path.join(root,'output/catalog-3d');
const sources=JSON.parse(await readFile(path.join(here,'sources.json'),'utf8'));
const source={...sources.products.find(item=>item.code==='W502'),body_mm:[71,110,18],colors:['White','Black'],dimension_source:'PDF page 7: Size 110*71*18mm; photographed deployed stand is visible'};
const inputs=[sources.pdf,sources.manifest,source];
const version=process.argv[2]||'v001';
if(!/^v\d{3}$/.test(version))throw Error('version must be vNNN');
if(!process.env.PLAYWRIGHT_MODULE||!process.env.CATALOG3D_CHROMIUM)throw Error('Set PLAYWRIGHT_MODULE and CATALOG3D_CHROMIUM to existing local installations; see README');
await verifySources(root,inputs);
const assets=new Map();
const server=createServer(async(request,response)=>{try{const url=new URL(request.url,'http://127.0.0.1');if(assets.has(url.pathname)){response.setHeader('Content-Type','model/gltf-binary');response.end(assets.get(url.pathname));return;}const files={'/':'render-w502.html','/models-w502.mjs':'models-w502.mjs'};if(url.pathname in files){response.setHeader('Content-Type',url.pathname==='/'?'text/html':'text/javascript');response.end(await readFile(path.join(here,files[url.pathname])));return;}if(url.pathname.startsWith('/three/')){const base=path.join(here,'node_modules/three'),file=path.resolve(base,decodeURIComponent(url.pathname.slice(7)));if(!file.startsWith(base+path.sep)||!file.endsWith('.js'))throw Error('denied');response.setHeader('Content-Type','text/javascript');response.end(await readFile(file));return;}response.writeHead(404);response.end();}catch{response.writeHead(404);response.end();}});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin=`http://127.0.0.1:${server.address().port}`;
let browser;
const writeJSON=(file,value)=>writeFile(file,JSON.stringify(value,null,2)+'\n',{flag:'wx'});
try{
 const {chromium}=await import(pathToFileURL(path.resolve(process.env.PLAYWRIGHT_MODULE)).href);
 browser=await chromium.launch({executablePath:process.env.CATALOG3D_CHROMIUM,headless:true,timeout:30000,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1200,height:1200}});await page.route('**/*',route=>route.request().url().startsWith(origin+'/')?route.continue():route.abort());await page.goto(origin);await page.waitForFunction(()=>window.ready===true);
 const directory=path.join(output,'W502',version);await mkdir(path.dirname(directory),{recursive:true});await mkdir(directory);
 const result=await page.evaluate(()=>window.worker.exportModel());const glb=Buffer.from(result.glb,'base64');const validation=await validateGLB(glb);if(result.metrics.triangles>50000||result.metrics.triangles!==result.imported.triangles)throw Error('geometry budget/import mismatch');
 await writeFile(path.join(directory,'model.glb'),glb,{flag:'wx'});assets.set('/relocated/W502/model.glb',await readFile(path.join(directory,'model.glb')));await page.evaluate(()=>window.worker.loadFile('/relocated/W502/model.glb'));
 const renders={};for(const view of ['front','back','side','straight']){const frame=await page.evaluate(view=>window.worker.capture(view),view);if(frame.visible_pixels<5000)throw Error(`blank render ${view}`);const filename=view==='front'?'preview.png':`preview-${view}.png`,bytes=Buffer.from(frame.png,'base64');await writeFile(path.join(directory,filename),bytes,{flag:'wx'});renders[view]={path:filename,sha256:sha256(bytes),visible_pixels:frame.visible_pixels};}
 const variants={geometry_sha256:sha256(result.geometry),default:'White',color_evidence:'PDF page 7 color list; RGB values are uncalibrated visual estimates',variants:[{name:'White',slots:{shell:'#e3dfd2',detail:'#b8b1a4'},finish_status:'estimated from source, not colorimetric'},{name:'Black',slots:{shell:'#232629',detail:'#343638'},finish_status:'estimated from source, not colorimetric'}]};
 for(const variant of variants.variants){const frame=await page.evaluate(slots=>window.worker.capture('front',slots),variant.slots);if(frame.metrics.triangles!==result.imported.triangles||frame.visible_pixels<5000)throw Error('variant render failed');}
 const generator={name:'smartgift-catalog3d-w502',version:'1.0.0',three:'0.160.0',chromium:browser.version(),models_sha256:sha256(await readFile(path.join(here,'models-w502.mjs'))),renderer_sha256:sha256(await readFile(path.join(here,'render-w502.html'))),method:'local-photo-referenced-parametric-mesh'};
 const metadata={asset_key:'W502',asset_version:version,source_product_code:'W502',canonical_product_id:null,mapping_status:'unresolved',evidence_binding:{candidate_product_master_id:'pm:PM-PB10K',candidate_category_id:'cat:executive-smart-tech',edge_type:'IN_CATEGORY',status:'evidence-supported-review-candidate',reason:'PDF page 7 says magnetic wireless 10000mAh; 110*71*18mm and deployed stand; canonical reference is MagSafe 10000mAh + stand at 105*68*16mm'},registry_refs:{doc_id:null,pic_id:null,status:'unregistered'},sources:[{...sources.pdf,page:source.page,locator_status:'page-code-visually-verified-2026-08-31'},{path:source.path,sha256:source.sha256,visual_origin:'original-catalog-crop'}],dimensions:{unit:'meter',body_xyz:source.body_mm.map(value=>value/1000),assembled_bounds_xyz:result.imported.bounds,source:source.dimension_source,source_annotation_not_factory_measurement:true},dimension_status:'source-annotated',estimated_regions:['underside','sidewall ports','stand hinge depth','connector details','material roughness'],geometry_sha256:variants.geometry_sha256,glb_sha256:sha256(glb),generator,review_status:'review-ready',rights_status:'pending-owner-review',public_ready:false,omitted_details:'unreadable tiny labels/certification marks and hidden mechanisms not fabricated',metrics:{...result.imported,glb_bytes:glb.length},renders};
 validateMetadata(metadata);await writeJSON(path.join(directory,'geometry-source.json'),{code:'W502',body_mm:source.body_mm,corner_mm:5.5,generator});await writeJSON(path.join(directory,'variants.json'),variants);await writeJSON(path.join(directory,'metadata.json'),metadata);await writeJSON(path.join(directory,'validation.json'),validation);
 const index=JSON.parse(await readFile(path.join(output,'model_catalog.json'),'utf8'));const candidate={code:'W502',path:`W502/${version}/model.glb`,metadata:`W502/${version}/metadata.json`,review_status:'review-ready',glb_sha256:metadata.glb_sha256};await publishIndex(output,{...index,review_candidates:[...index.review_candidates,candidate],held:index.held.filter(code=>code!=='W502'),hold_reason:'Owner likeness/identity review required before promotion',public_ready:false},()=>verifySources(root,inputs));
 console.log(JSON.stringify({code:'W502',...metadata.metrics,validation_errors:validation.issues.numErrors,validation_warnings:validation.issues.numWarnings}));
}finally{if(browser)await browser.close();server.closeAllConnections();await new Promise(resolve=>server.close(resolve));}
