import * as THREE from 'three';

export const BW00_ESTIMATED_RECIPE = {
  code:'BW00-0',
  // Estimate approved for visual review only: diameter x height x diameter.
  body_mm:[65,230,65], shell:'#111315', detail:'#24272a',
};

export function makeBW00EstimatedModel(recipe = BW00_ESTIMATED_RECIPE) {
  if (recipe?.code !== 'BW00-0' || !Array.isArray(recipe.body_mm) || recipe.body_mm.length !== 3) throw Error('invalid BW00-0 recipe');
  const [widthMm, heightMm, depthMm] = recipe.body_mm;
  if (![widthMm,heightMm,depthMm].every(value=>Number.isFinite(value) && value > 0) || widthMm !== depthMm) throw Error('BW00-0 requires a round estimated body');
  const radius = widthMm / 2000, height = heightMm / 1000;
  const root = new THREE.Group(); root.name = 'BW00-0';
  const material = (name,color,roughness=.38,metalness=0) => { const value = new THREE.MeshStandardMaterial({color,roughness,metalness}); value.name = name; return value; };
  const shell = material('shell',recipe.shell,.24,.72), detail = material('detail',recipe.detail,.3,.65);
  const display = material('display','#020405',.18,.1), displayEdge = material('display-edge','#8a9297',.22,.8);
  const add = (name,geometry,mat,position) => { const mesh = new THREE.Mesh(geometry,mat); mesh.name=name; mesh.position.set(...position); root.add(mesh); return mesh; };
  add('body',new THREE.CylinderGeometry(radius,radius,height,96,1,false),shell,[0,height/2,0]);
  add('base-ring',new THREE.CylinderGeometry(radius*.985,radius*.99,.004,96),detail,[0,.002,0]);
  const lidHeight=.030;
  add('lid',new THREE.CylinderGeometry(radius*1.012,radius*1.012,lidHeight,96),detail,[0,height+lidHeight/2,0]);
  add('lid-seam',new THREE.TorusGeometry(radius*1.013,.0009,8,96),shell,[0,height+.004,0]).rotation.x=Math.PI/2;
  add('temperature-display-edge',new THREE.CylinderGeometry(.012,.012,.0018,64),displayEdge,[0,height+lidHeight+.0009,0]);
  add('temperature-display',new THREE.CylinderGeometry(.0105,.0105,.002,64),display,[0,height+lidHeight+.0024,0]);
  root.updateMatrixWorld(true);
  return root;
}
