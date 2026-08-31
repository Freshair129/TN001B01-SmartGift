import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

export const RECIPES = {
  S1033: { code: 'S1033', body_mm: [69.3, 106.4, 17.1], corner_mm: 5.2, shell: '#deded9', detail: '#cbcbc7' },
  DW03: { code: 'DW03', body_mm: [67.3, 108.3, 23], corner_mm: 6.5, shell: '#ff8a26', detail: '#e66b27' },
};

export function makeModel(code, recipe = RECIPES[code]) {
  if (!RECIPES[code] || recipe?.code !== code) throw Error(`unsupported model ${code}`);
  const [w, h, d] = recipe.body_mm.map(n => n / 1000);
  if (![w, h, d].every(n => Number.isFinite(n) && n > 0)) throw Error('invalid dimensions');
  const root = new THREE.Group();
  root.name = code;
  const materials = {};
  const material = (name, color, roughness = 0.38, metalness = 0) => {
    materials[name] = new THREE.MeshStandardMaterial({ color, roughness, metalness });
    materials[name].name = name;
    return materials[name];
  };
  const shell = material('shell', recipe.shell, 0.28);
  const detail = material('detail', recipe.detail, 0.4);
  const silver = material('connector', '#a5a9ab', 0.28, 0.82);
  const dark = material('port', '#393b3c', 0.8);
  const pin = material('contact', '#d4ad61', 0.24, 0.72);

  function mesh(name, geometry, mat, position, rotation = [0, 0, 0], parent = root) {
    const part = new THREE.Mesh(geometry, mat);
    part.name = name;
    part.position.set(...position);
    part.rotation.set(...rotation);
    parent.add(part);
    return part;
  }
  function box(name, size, position, mat, radius = 0.001, rotation, parent) {
    return mesh(name, new RoundedBoxGeometry(...size, 3, Math.min(radius, ...size.map(n => n / 2))), mat, position, rotation, parent);
  }
  function disk(name, radius, depth, position, mat) {
    return mesh(name, new THREE.CylinderGeometry(radius, radius, depth, 80), mat, position, [Math.PI / 2, 0, 0]);
  }
  function ring(name, radius, tube, position, mat) {
    return mesh(name, new THREE.TorusGeometry(radius, tube, 8, 96), mat, position);
  }
  box('body', [w, h, d], [0, h / 2, 0], shell, recipe.corner_mm / 1000);

  if (code === 'DW03') {
    const face = d / 2;
    disk('charging-pad', 0.0285, 0.0013, [0, h - 0.0355, face + 0.0003], detail);
    ring('charging-pad-edge', 0.0278, 0.00065, [0, h - 0.0355, face + 0.0011], detail);
    box('charging-tail', [0.009, 0.022, 0.0013], [0, h - 0.069, face - 0.00015], detail, 0.0006);
    disk('charging-center', 0.012, 0.001, [0, h - 0.0355, face + 0.0013], shell);
    const boltMat = material('symbol', '#ffbd70', 0.55);
    const bolt = new THREE.Shape();
    [[0.0008,0.0055],[-0.0034,-0.001],[-0.0004,-0.001],[-0.001, -0.0055],[0.0035,0.001],[0.0003,0.001]].forEach(([x,y], i) => i ? bolt.lineTo(x,y) : bolt.moveTo(x,y));
    bolt.closePath();
    mesh('observed-lightning-symbol', new THREE.ShapeGeometry(bolt), boltMat, [0, h - 0.0355, face + 0.0019]);
    for (let i = 0; i < 4; i++) {
      const x = (i - 1.5) * 0.0141;
      const z = -face;
      box(`cable-channel-${i}`, [0.0128, h - 0.006, 0.00065], [x, h / 2, z - 0.0002], detail, 0.0003);
      box(`stowed-cable-${i}`, [0.011, 0.073, 0.0015], [x, 0.040, z - 0.0008], shell, 0.0007);
      box(`connector-grip-${i}`, [0.0117, 0.017, 0.0026], [x, 0.087, z - 0.0013], shell, 0.0011);
      box(`connector-tip-${i}`, [i === 3 ? 0.0102 : 0.0078, 0.007, 0.002], [x, 0.098, z - 0.0012], i === 3 ? detail : silver, 0.0008);
      if (i === 1) box('connector-opening', [0.0058, 0.0015, 0.0004], [x, 0.099, z - 0.0023], dark, 0.00018);
      if (i === 3) for (let j = 0; j < 4; j++) {
        box(`usb-contact-${j}`, [0.0009, 0.004, 0.00025], [x + (j - 1.5) * 0.0019, 0.098, z - 0.00235], pin, 0.0001);
      }
    }
  } else {
    const face = d / 2;
    disk('stand-face', 0.0302, 0.0018, [0, h - 0.0335, face + 0.0006], shell);
    ring('stand-fold-line', 0.0278, 0.0004, [0, h - 0.0335, face + 0.00165], detail);
    box('stand-release-tab', [0.0075, 0.019, 0.002], [0, 0.032, face + 0.0005], detail, 0.0009);
    // Pose inferred from the source's deployed stand; hinge internals are not modeled.
    const stand = new THREE.Group(); stand.name = 'rear-stand';
    stand.position.set(0, 0.055, -d / 2); stand.rotation.x = 0.35; root.add(stand);
    box('stand-panel', [w - 0.013, 0.052, 0.0022], [0, -0.026, 0], shell, 0.001, undefined, stand);
    box('stand-hinge-cover', [w - 0.018, 0.003, 0.003], [0, 0, -0.001], detail, 0.001, undefined, stand);
    for (const side of [-1, 1]) {
      const points = [
        [side * (w / 2 - 0.0015), 0.025, -0.003],
        [side * (w / 2 + 0.001), 0.058, -0.004],
        [side * (w / 2 + 0.01), 0.094, -0.003],
        [side * (w / 2 + 0.027), 0.111, -0.002],
      ].map(p => new THREE.Vector3(...p));
      const curve = new THREE.CatmullRomCurve3(points);
      const cable = new THREE.TubeGeometry(curve, 36, 1, 8, false);
      // Elliptical cross-section approximates the flat integrated cable visible in the photo.
      const pos = cable.attributes.position;
      for (let step = 0; step <= 36; step++) {
        const center = curve.getPointAt(step / 36);
        for (let radial = 0; radial <= 8; radial++) {
          const i = step * 9 + radial;
          pos.setXYZ(i, center.x + (pos.getX(i) - center.x) * 0.0022,
            center.y + (pos.getY(i) - center.y) * 0.0022,
            center.z + (pos.getZ(i) - center.z) * 0.00065);
        }
      }
      cable.computeVertexNormals();
      mesh(`integrated-cable-${side}`, cable, detail, [0, 0, 0]);
      const end = points.at(-1);
      box(`cable-grip-${side}`, [0.012, 0.006, 0.0034], [end.x + side * 0.004, end.y + 0.002, end.z], detail, 0.001, [0, 0, -side * 0.42]);
      box(`cable-tip-${side}`, [0.007, 0.0045, 0.0024], [end.x + side * 0.011, end.y + 0.005, end.z], silver, 0.0006, [0, 0, -side * 0.42]);
    }
  }
  root.updateMatrixWorld(true);
  return root;
}

export function applyVariant(root, slots) {
  const known = new Map();
  root.traverse(node => { if (node.isMesh) known.set(node.material.name, node.material); });
  for (const [slot, color] of Object.entries(slots)) {
    if (!known.has(slot)) throw Error(`unknown material slot ${slot}`);
    known.get(slot).color.set(color);
  }
}

export function geometryFingerprint(root) {
  root.updateMatrixWorld(true);
  const entries = [];
  root.traverse(node => {
    if (node.isMesh) entries.push({ name: node.name, matrix: node.matrixWorld.toArray(),
      positions: Array.from(node.geometry.attributes.position.array), indices: node.geometry.index ? Array.from(node.geometry.index.array) : null });
  });
  return JSON.stringify(entries);
}

export function inspectModel(root) {
  let triangles = 0, meshes = 0;
  root.updateMatrixWorld(true);
  root.traverse(node => {
    if (!node.isMesh) return;
    meshes++;
    for (const attr of Object.values(node.geometry.attributes)) {
      if (!Array.from(attr.array).every(Number.isFinite)) throw Error('non-finite geometry');
    }
    if (!node.matrixWorld.elements.every(Number.isFinite)) throw Error('non-finite transform');
    const count = node.geometry.attributes.position.count;
    const indices = node.geometry.index;
    if (indices && Array.from(indices.array).some(n => n < 0 || n >= count)) throw Error('invalid mesh index');
    triangles += (indices ? indices.count : count) / 3;
  });
  const size = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3()).toArray();
  if (!meshes || size.some(n => !Number.isFinite(n) || n <= 0)) throw Error('empty or flat geometry');
  return { triangles, meshes, bounds: size };
}
