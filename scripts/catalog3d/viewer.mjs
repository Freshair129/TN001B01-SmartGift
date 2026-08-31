import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const canvas=document.querySelector('#model-canvas');
const notice=document.querySelector('#notice');
const product=document.querySelector('#product');
const category=document.querySelector('#category');
const coverage=document.querySelector('#coverage');
const buttons=[...document.querySelectorAll('.zoom-controls button')];
const referencePanel=document.querySelector('#reference-panel');
const referenceToggle=document.querySelector('#reference-toggle');
const referenceImage=document.querySelector('#reference-image');
const compareGrid=document.querySelector('#compare-grid');
let renderer, scene, camera, controls, current, sequence=0, request, distance=1, viewerIndex, availableAssets=new Map();

function dispose(model) {
  const materials=new Set();
  model.traverse(node=>{ if(node.isMesh){node.geometry.dispose(); materials.add(node.material);} });
  for(const material of materials) material.dispose();
}
function render() { renderer.render(scene,camera); }
function showError(message) {
  notice.hidden=false; notice.dataset.error='true'; notice.replaceChildren();
  const text=document.createElement('p'); text.textContent=message;
  const retry=document.createElement('button'); retry.textContent='ลองเปิดโมเดลอีกครั้ง';
  retry.addEventListener('click',()=>loadModel(product.value)); notice.append(text,retry);
}
function changeColor(variant) {
  current.traverse(node=>{ if(node.isMesh && variant.slots[node.material.name]) node.material.color.set(variant.slots[node.material.name]); });
  for(const button of document.querySelectorAll('.swatch')) button.setAttribute('aria-pressed',String(button.dataset.name===variant.name));
  document.querySelector('#color-name').textContent=variant.name;
  render();
}
function fit() {
  const bounds=new THREE.Box3().setFromObject(current), size=bounds.getSize(new THREE.Vector3()), center=bounds.getCenter(new THREE.Vector3());
  distance=Math.max(size.y,size.x/camera.aspect)*2.7;
  controls.target.copy(center);
  controls.minDistance=Math.max(size.x,size.y,size.z)*0.8;
  controls.maxDistance=distance*3;
  camera.position.copy(center).add(new THREE.Vector3(0.55,0.22,1).normalize().multiplyScalar(distance));
  controls.update(); render();
}
function zoom(factor) {
  if(!current) return;
  const offset=camera.position.clone().sub(controls.target);
  offset.setLength(THREE.MathUtils.clamp(offset.length()*factor,controls.minDistance,controls.maxDistance));
  camera.position.copy(controls.target).add(offset); controls.update(); render();
}
function coverageText(categoryId) {
  const item=categoryId === 'all' ? viewerIndex.categories.reduce((total,current)=>({ total:total.total+current.total, local_ready:total.local_ready+current.local_ready, held:total.held+current.held }),{total:0,local_ready:0,held:0}) : viewerIndex.categories.find(entry=>entry.id===categoryId);
  return `${item.total} canonical ProductMaster · local-ready ${item.local_ready} · รอหลักฐาน ${item.held}`;
}
function assetsForCategory(categoryId) {
  const assets=[...viewerIndex.local_ready_assets, ...viewerIndex.review_candidates];
  return assets.filter(asset=>categoryId === 'all' || asset.category_id === categoryId || asset.candidate_category_id === categoryId);
}
function showNoAsset() {
  product.replaceChildren(); const option=document.createElement('option'); option.value=''; option.textContent='ยังไม่มีโมเดลที่ผ่านหลักฐาน'; product.append(option); product.disabled=true;
  if (current) { scene.remove(current); dispose(current); current=null; render(); }
  document.querySelector('#model-name').textContent='ไม่มีโมเดลในหมวดนี้';
  document.querySelector('#download').hidden=true;
  document.querySelector('#colors').replaceChildren(); document.querySelector('#color-name').textContent='';
  referencePanel.hidden=true; compareGrid.classList.remove('reference-open'); referenceToggle.setAttribute('aria-expanded','false'); referenceToggle.textContent='เทียบภาพต้นฉบับ';
  referenceToggle.disabled=true;
  notice.hidden=false; notice.dataset.error='false'; notice.textContent='หมวดนี้ยังไม่มีโมเดลที่ผ่านหลักฐานเพียงพอ';
  buttons.forEach(button=>button.disabled=true);
}
function populateProducts() {
  const assets=assetsForCategory(category.value); product.replaceChildren(); availableAssets=new Map(assets.map(asset=>[asset.asset_key,asset]));
  coverage.textContent=coverageText(category.value);
  if (!assets.length) { showNoAsset(); return; }
  product.disabled=false;
  for (const asset of assets) { const option=document.createElement('option'); option.value=asset.asset_key; option.textContent=asset.mapping_status === 'unresolved' ? `${asset.asset_key} — กำลังตรวจ identity` : asset.asset_key; product.append(option); }
  loadModel(product.value);
}
async function loadViewerIndex() {
  const response=await fetch('/viewer-index.json'); if (!response.ok) throw Error('ไม่พบ generated viewer index');
  viewerIndex=await response.json();
  category.replaceChildren();
  const all=document.createElement('option'); all.value='all'; all.textContent='ทั้งหมด (ตรวจทาน)'; category.append(all);
  for (const item of viewerIndex.categories) { const option=document.createElement('option'); option.value=item.id; option.textContent=item.name; category.append(option); }
  category.disabled=false; populateProducts();
}
async function loadModel(code) {
  if (!availableAssets.has(code)) return;
  const ticket=++sequence;
  request?.abort(); request=new AbortController();
  notice.hidden=false; notice.dataset.error='false'; notice.textContent='กำลังเปิดโมเดล…';
  buttons.forEach(button=>button.disabled=true);
  document.querySelector('#colors').replaceChildren(); document.querySelector('#color-name').textContent='';
  document.querySelector('#model-name').textContent=code;
  referenceToggle.disabled=false;
  document.querySelector('#download').hidden=false;
  document.querySelector('#download').href=`/assets/${code}/model.glb`;
  document.querySelector('#download').download=`${code}.glb`;
  referenceImage.src=`/reference/${code}.png`;
  referenceImage.alt=`ภาพต้นฉบับสินค้า ${code} จาก catalog สำหรับเทียบรูปทรง`;
  if(current){ scene.remove(current); dispose(current); current=null; render(); }
  try {
    const responses=await Promise.all(['model.glb','variants.json'].map(file=>fetch(`/assets/${code}/${file}`,{signal:request.signal})));
    if(responses.some(response=>!response.ok)) throw Error('ไม่พบไฟล์โมเดลหรือข้อมูลสี กรุณาตรวจว่า local server ยังทำงานอยู่');
    const [bytes,colors]=await Promise.all([responses[0].arrayBuffer(),responses[1].json()]);
    const loaded=await new GLTFLoader().parseAsync(bytes,'');
    if(ticket!==sequence){dispose(loaded.scene);return;}
    current=loaded.scene; scene.add(current);
    for(const variant of colors.variants) {
      const button=document.createElement('button'); button.type='button'; button.className='swatch';
      button.dataset.name=variant.name; button.style.setProperty('--swatch',variant.slots.shell);
      button.setAttribute('aria-label',`เลือกสี ${variant.name}`); button.title=variant.name;
      button.setAttribute('aria-pressed','false'); button.addEventListener('click',()=>changeColor(variant));
      document.querySelector('#colors').append(button);
    }
    fit(); changeColor(colors.variants.find(variant=>variant.name===colors.default));
    buttons.forEach(button=>button.disabled=false); notice.hidden=true;
  } catch(error) {
    if(ticket!==sequence || error.name==='AbortError') return;
    showError('เปิดโมเดลไม่สำเร็จ กรุณาตรวจว่า local server ยังทำงานอยู่ แล้วลองอีกครั้ง');
  }
}

try {
  renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,preserveDrawingBuffer:true});
  renderer.setClearColor(0x000000,0); renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.outputColorSpace=THREE.SRGBColorSpace; renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=0.85;
  scene=new THREE.Scene(); // Null background; no floor, shadow plane, or skybox.
  const pmrem=new THREE.PMREMGenerator(renderer), room=new RoomEnvironment();
  scene.environment=pmrem.fromScene(room,0.04).texture; room.dispose(); pmrem.dispose();
  scene.add(new THREE.HemisphereLight('#ffffff','#9f9c92',0.7));
  const light=new THREE.DirectionalLight('#ffffff',2); light.position.set(-0.15,0.25,0.23); scene.add(light);
  camera=new THREE.PerspectiveCamera(30,1,0.001,10);
  controls=new OrbitControls(camera,canvas); controls.enableDamping=false; controls.enablePan=false;
  controls.addEventListener('change',render);
  new ResizeObserver(()=>{
    const {width,height}=canvas.getBoundingClientRect();
    renderer.setSize(width,height,false); camera.aspect=width/height; camera.updateProjectionMatrix();
    if(current) fit(); else render();
  }).observe(canvas.parentElement);
  product.addEventListener('change',()=>product.value && loadModel(product.value));
  category.addEventListener('change',populateProducts);
  referenceToggle.addEventListener('click',()=>{
    const open=referencePanel.hidden;
    referencePanel.hidden=!open; compareGrid.classList.toggle('reference-open',open);
    referenceToggle.setAttribute('aria-expanded',String(open));
    referenceToggle.textContent=open?'ซ่อนภาพต้นฉบับ':'เทียบภาพต้นฉบับ';
  });
  document.querySelector('#zoom-in').addEventListener('click',()=>zoom(0.8));
  document.querySelector('#zoom-out').addEventListener('click',()=>zoom(1.25));
  document.querySelector('#reset').addEventListener('click',()=>current && fit());
  canvas.addEventListener('keydown',event=>{
    if(!current) return;
    if(['+','=','-'].includes(event.key)){event.preventDefault();zoom(event.key==='-'?1.2:0.8);return;}
    if(event.key==='Home'){event.preventDefault();fit();return;}
    if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key))return;
    event.preventDefault(); const spherical=new THREE.Spherical().setFromVector3(camera.position.clone().sub(controls.target));
    if(event.key==='ArrowLeft')spherical.theta-=0.15; if(event.key==='ArrowRight')spherical.theta+=0.15;
    if(event.key==='ArrowUp')spherical.phi-=0.15; if(event.key==='ArrowDown')spherical.phi+=0.15;
    spherical.makeSafe(); camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); controls.update();
  });
  await loadViewerIndex();
} catch(error) {
  notice.hidden=false; notice.dataset.error='true'; notice.textContent='เปิด WebGL ไม่สำเร็จ กรุณาเปิด viewer ในเบราว์เซอร์ที่รองรับ 3D';
  console.error(error);
}
