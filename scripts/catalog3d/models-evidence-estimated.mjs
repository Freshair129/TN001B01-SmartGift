import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const color = (name, hex) => ({ name, hex });
export const EVIDENCE_ESTIMATED_RECIPES = {
  'TDK01-1': { code:'TDK01-1', product_master_id:'pm:PM-BOTTLE-LED', category_id:'cat:eco-friendly', kind:'led-bottle', body_mm:[65,230,65], dimension_status:'estimated', colors:[color('Black','#14171a'),color('Blue','#174b7b'),color('Red','#a42125')] },
  'TJS00-1': { code:'TJS00-1', product_master_id:'pm:PM-CFMUG', category_id:'cat:novelty-self-care', kind:'travel-mug', body_mm:[90,145,90], dimension_status:'estimated', colors:[color('Purple','#71548d'),color('Blue','#246d9b'),color('Pink','#ce7d9e'),color('Green','#47876c'),color('Yellow','#d2ad3c')] },
  'TBY17-1': { code:'TBY17-1', product_master_id:'pm:PM-MSG', category_id:'cat:novelty-self-care', kind:'neck-massager', body_mm:[150,145,45], dimension_status:'source-annotated', colors:[color('White','#e7e7e2'),color('Orange','#e9812e'),color('Red','#b82e35'),color('Blue','#4277aa')] },
  'TN00-2': { code:'TN00-2', product_master_id:'pm:PM-MUG-HEAT', category_id:'cat:novelty-self-care', kind:'heated-mug', body_mm:[135,95,135], dimension_status:'estimated', colors:[color('White','#efefeb'),color('Pink','#d68b9e'),color('Red','#b8323b'),color('Green','#407a62')] },
  'TNA0014': { code:'TNA0014', product_master_id:'pm:PM-NB', category_id:'cat:executive-smart-tech', kind:'power-notebook', body_mm:[210,297,18], dimension_status:'estimated', colors:[color('Black','#212225')] },
  'TZJ00-1': { code:'TZJ00-1', product_master_id:'pm:PM-PB10K', category_id:'cat:executive-smart-tech', kind:'cable-powerbank', body_mm:[146,69,40], dimension_status:'source-annotated', colors:[color('Black','#27292b'),color('White','#e5e4df')] },
  'TYS01-1': { code:'TYS01-1', product_master_id:'pm:PM-UMB', category_id:'cat:eco-friendly', kind:'folded-umbrella', body_mm:[65,280,65], dimension_status:'estimated', colors:[color('Black','#25282a'),color('Red','#b52e33'),color('Gold','#ba923a'),color('Blue','#2d6da8'),color('Light Blue','#6fa6c9'),color('Pink','#d28eaa'),color('Orange','#d87930')] },
};

export function makeEvidenceEstimatedModel(code, recipe=EVIDENCE_ESTIMATED_RECIPES[code]) {
  if (!recipe || recipe.code !== code) throw Error(`unsupported evidence model ${code}`);
  const [w,h,d]=recipe.body_mm.map(value=>value/1000);
  if (![w,h,d].every(value=>Number.isFinite(value) && value>0)) throw Error('invalid estimated dimensions');
  const root=new THREE.Group(); root.name=code;
  const materials={};
  const material=(name,hex,roughness=.42,metalness=0)=>{ const value=new THREE.MeshStandardMaterial({color:hex,roughness,metalness}); value.name=name; materials[name]=value; return value; };
  const shell=material('shell',recipe.colors[0].hex,.34), detail=material('detail','#3b3d3e',.5), metal=material('metal','#a9afb0',.24,.78), accent=material('accent','#d3ad57',.34,.35), dark=material('dark','#151617',.72);
  const mesh=(name,geometry,mat,position=[0,0,0],rotation=[0,0,0],parent=root)=>{const node=new THREE.Mesh(geometry,mat);node.name=name;node.position.set(...position);node.rotation.set(...rotation);parent.add(node);return node;};
  const box=(name,size,position,mat=shell,r=.002,rotation=[0,0,0],parent=root)=>mesh(name,new RoundedBoxGeometry(...size,3,Math.min(r,...size.map(value=>value/2))),mat,position,rotation,parent);
  const cylinder=(name,radius,depth,position,mat=shell,rotation=[0,0,0])=>mesh(name,new THREE.CylinderGeometry(radius,radius,depth,64),mat,position,rotation);
  const torus=(name,radius,tube,position,mat=detail,rotation=[0,0,0])=>mesh(name,new THREE.TorusGeometry(radius,tube,10,80),mat,position,rotation);
  if(recipe.kind==='led-bottle') {
    cylinder('insulated-body',w/2,h*.86,[0,h*.43,0]); cylinder('lid',w*.46,h*.12,[0,h*.92,0],dark);
    cylinder('temperature-display',w*.18,.003,[0,h*.985,0],accent); torus('lid-seam',w*.45,.0015,[0,h*.86,0],metal);
  } else if(recipe.kind==='travel-mug') {
    cylinder('cup-body',w*.42,h*.82,[0,h*.41,0]); cylinder('three-way-lid',w*.45,h*.12,[0,h*.88,0],dark);
    const handle=new THREE.TorusGeometry(w*.23,.008,10,48,Math.PI*1.35); mesh('handle',handle,detail,[w*.37,h*.46,0],[0,Math.PI/2,-.72]);
  } else if(recipe.kind==='neck-massager') {
    const curve=new THREE.CatmullRomCurve3([[-w*.38,h*.9,0],[-w*.48,h*.58,0],[-w*.3,h*.15,0],[0,h*.04,0],[w*.3,h*.15,0],[w*.48,h*.58,0],[w*.38,h*.9,0]].map(point=>new THREE.Vector3(...point)));
    mesh('neckband',new THREE.TubeGeometry(curve,80,d*.28,12,false),shell);
    for(const side of [-1,1]) { cylinder(`electrode-${side}`,d*.22,.006,[side*w*.32,h*.19,d*.18],metal,[Math.PI/2,0,0]); box(`control-${side}`,[w*.12,h*.17,d*.35],[side*w*.39,h*.31,0],detail,.006); }
  } else if(recipe.kind==='heated-mug') {
    box('heating-pad',[w,h*.18,d],[0,h*.09,0],detail,.01); cylinder('ceramic-cup',w*.29,h*.72,[0,h*.53,0],shell);
    const handle=new THREE.TorusGeometry(w*.17,.006,8,40,Math.PI*1.35); mesh('cup-handle',handle,detail,[w*.28,h*.52,0],[0,Math.PI/2,-.72]); cylinder('heat-ring',w*.22,.002,[0,h*.185,0],accent);
  } else if(recipe.kind==='power-notebook') {
    box('pu-cover',[w,h,d],[0,h/2,0],shell,.008); box('page-block',[w*.88,h*.86,d*.18],[0,h*.49,d*.52],accent,.002);
    torus('wireless-charge-ring',w*.16,.002,[0,h*.72,d*.52],metal,[Math.PI/2,0,0]); box('powerbank-spine',[w*.14,h*.82,d*.35],[-w*.33,h*.5,d*.55],dark,.002);
  } else if(recipe.kind==='cable-powerbank') {
    box('powerbank-body',[w,h,d],[0,h/2,0],shell,.008); cylinder('status-button',h*.075,.004,[w*.32,h*.65,d*.52],metal,[Math.PI/2,0,0]);
    for(const side of [-1,1]) { const points=[new THREE.Vector3(side*w*.42,h*.15,-d*.5),new THREE.Vector3(side*w*.57,h*.32,-d*.66),new THREE.Vector3(side*w*.48,h*.55,-d*.6)]; mesh(`integrated-cable-${side}`,new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),24,d*.06,8,false),detail); }
  } else if(recipe.kind==='folded-umbrella') {
    cylinder('folded-canopy',w*.42,h*.56,[0,h*.65,0],shell); cylinder('canopy-cap',w*.3,h*.06,[0,h*.95,0],metal);
    box('silicone-band',[w*.9,h*.07,d*.9],[0,h*.59,0],accent,.004); cylinder('shaft',w*.11,h*.62,[0,h*.3,0],metal); box('handle',[w*.36,h*.22,d*.36],[0,h*.11,0],dark,.012);
  } else throw Error(`unsupported estimated kind ${recipe.kind}`);
  root.updateMatrixWorld(true); return root;
}
