import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export const W502_RECIPE = { code:'W502', body_mm:[71,110,18], corner_mm:5.5, shell:'#e3dfd2', detail:'#b8b1a4' };

export function makeW502Model(recipe=W502_RECIPE) {
  if (recipe?.code !== 'W502' || !Array.isArray(recipe.body_mm) || recipe.body_mm.length !== 3) throw Error('invalid W502 recipe');
  const [w,h,d]=recipe.body_mm.map(value=>value/1000);
  if (![w,h,d].every(value=>Number.isFinite(value)&&value>0)) throw Error('invalid W502 dimensions');
  const root=new THREE.Group(); root.name='W502';
  const materials={};
  const material=(name,color,roughness=.38,metalness=0)=>{
    const value=new THREE.MeshStandardMaterial({color,roughness,metalness}); value.name=name; materials[name]=value; return value;
  };
  const shell=material('shell',recipe.shell,.28);
  const detail=material('detail',recipe.detail,.42);
  const dark=material('port','#242528',.75);
  const metal=material('connector','#a7aaab',.28,.8);
  const box=(name,size,position,mat,radius=.001,parent=root,rotation=[0,0,0])=>{
    const mesh=new THREE.Mesh(new RoundedBoxGeometry(...size,3,Math.min(radius,...size.map(value=>value/2))),mat);
    mesh.name=name; mesh.position.set(...position); mesh.rotation.set(...rotation); parent.add(mesh); return mesh;
  };
  const disk=(name,radius,depth,position,mat)=>{
    const mesh=new THREE.Mesh(new THREE.CylinderGeometry(radius,radius,depth,80),mat);
    mesh.name=name; mesh.position.set(...position); mesh.rotation.x=Math.PI/2; root.add(mesh); return mesh;
  };
  const face=d/2;
  box('body',[w,h,d],[0,h/2,0],shell,recipe.corner_mm/1000);
  disk('magnetic-charging-pad',.0272,.0015,[0,h-.040,face+.00055],detail);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.0262,.00072,8,80),detail);
  ring.name='magnetic-charging-ring'; ring.position.set(0,h-.040,face+.00135); root.add(ring);
  box('charging-tail',[.0085,.021,.0014],[0,h-.073,face+.001],detail,.0006);
  box('top-button',[.010,.003,.0015],[-w*.30,h-.001,0],detail,.0008);
  box('usb-c-port',[.009,.002,.0035],[0,.002,-d*.16],dark,.00035);
  box('usb-a-port',[.012,.002,.004],[-.015,.002,-d*.16],dark,.0004);
  box('usb-a-frame',[.0135,.001,.005],[-.015,.0012,-d*.16],metal,.0004);
  const stand=new THREE.Group(); stand.name='rear-stand'; stand.position.set(0,.048,-face-.0005); stand.rotation.x=.38; root.add(stand);
  box('stand-panel',[w-.012,.067,.0022],[0,-.033,0],shell,.001,stand);
  box('stand-hinge',[w-.018,.003,.003],[0,.001,-.001],detail,.0008,stand);
  root.updateMatrixWorld(true);
  return root;
}
