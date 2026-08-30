import * as THREE from 'https://esm.sh/three@0.160.0';
import { OrbitControls } from 'https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js';

// Gift Set Exploded Anatomy 3D Engine for SmartGift
// Modelled after pc-anatomy-3d.ts in pc-market-monitor

const canvas = document.querySelector("#gift-anatomy-canvas");
const stage = document.querySelector("#gift-anatomy-stage");
const statusEl = document.querySelector("#webgl-status");
const labelsLayer = document.querySelector("#gift-anatomy-labels");
const svgLayer = labelsLayer ? labelsLayer.querySelector("svg") : null;

if (canvas && stage) {
  init3DAnatomy();
}

function init3DAnatomy() {
  let width = stage.clientWidth || 600;
  let height = stage.clientHeight || 540;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0f141a);
  scene.fog = new THREE.FogExp2(0x0f141a, 0.035);

  const camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
  camera.position.set(7.5, 6.2, 8.5);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.maxDistance = 22;
  controls.minDistance = 3.5;
  controls.target.set(0, 0.2, 0);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xfff6ea, 2.2);
  dirLight.position.set(8, 12, 6);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 2048;
  dirLight.shadow.mapSize.height = 2048;
  dirLight.shadow.bias = -0.0001;
  scene.add(dirLight);

  const rimLight = new THREE.DirectionalLight(0x38d6df, 1.4);
  rimLight.position.set(-8, 6, -8);
  scene.add(rimLight);

  const pointLight = new THREE.PointLight(0xd4af37, 1.2, 12);
  pointLight.position.set(0, 3, 0);
  scene.add(pointLight);

  // Ground Grid & Shadow Plane
  const groundGeo = new THREE.PlaneGeometry(30, 30);
  const groundMat = new THREE.ShadowMaterial({ opacity: 0.35 });
  const ground = new THREE.Mesh(groundGeo, groundMat);
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -1.2;
  ground.receiveShadow = true;
  scene.add(ground);

  const gridHelper = new THREE.GridHelper(16, 24, 0x1e293b, 0x151c24);
  gridHelper.position.y = -1.19;
  scene.add(gridHelper);

  // Materials Library
  const materials = {
    boxExterior: new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.45, metalness: 0.2 }),
    boxInterior: new THREE.MeshStandardMaterial({ color: 0x090d12, roughness: 0.85, metalness: 0.05 }),
    boxGold: new THREE.MeshStandardMaterial({ color: 0xd4af37, roughness: 0.25, metalness: 0.85 }),
    leatherBlack: new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.65, metalness: 0.1 }),
    stainless: new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.22, metalness: 0.92 }),
    brushedMetal: new THREE.MeshStandardMaterial({ color: 0x94a3b8, roughness: 0.38, metalness: 0.8 }),
    walnutWood: new THREE.MeshStandardMaterial({ color: 0x5c3a21, roughness: 0.55, metalness: 0.05 }),
    brassGold: new THREE.MeshStandardMaterial({ color: 0xd4af37, roughness: 0.28, metalness: 0.9 }),
    umbrellaCloth: new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.7, metalness: 0.1 }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0xffffff, transmission: 0.9, opacity: 1, transparent: true, roughness: 0.1, ior: 1.5 }),
    ledGlow: new THREE.MeshBasicMaterial({ color: 0x38d6df }),
    accentCyan: new THREE.MeshStandardMaterial({ color: 0x08798a, roughness: 0.3, metalness: 0.5 })
  };

  const outlineMaterial = new THREE.LineBasicMaterial({ color: 0x38d6df, linewidth: 2 });

  // Parts Registry & Groups
  const partsGroup = new THREE.Group();
  scene.add(partsGroup);

  const interactiveMeshes = [];
  const partPositions = {};
  const partLabels = {};

  function addPartMesh(partId, mesh, isOutline = true) {
    mesh.userData.partId = partId;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    partsGroup.add(mesh);
    interactiveMeshes.push(mesh);

    if (isOutline) {
      const edges = new THREE.EdgesGeometry(mesh.geometry, 25);
      const line = new THREE.LineSegments(edges, outlineMaterial);
      line.position.copy(mesh.position);
      line.rotation.copy(mesh.rotation);
      line.scale.copy(mesh.scale).multiplyScalar(1.008);
      line.visible = false;
      line.userData.partId = partId;
      line.userData.isOutline = true;
      partsGroup.add(line);
    }
    return mesh;
  }

  // --- 1. Luxury Presentation Gift Box (Open Base & Exploded Lid) ---
  // Base Box
  const boxBase = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.7, 3.8), materials.boxExterior);
  boxBase.position.set(0, -0.75, 0);
  addPartMesh("box_base", boxBase, true);
  partPositions["box_base"] = new THREE.Vector3(0, -0.75, 0);

  // Box Inner Cushion Tray
  const innerTray = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.6, 3.6), materials.boxInterior);
  innerTray.position.set(0, -0.68, 0);
  addPartMesh("box_base", innerTray, false);

  // Exploded Box Lid (Floating high and tilted)
  const boxLid = new THREE.Mesh(new THREE.BoxGeometry(4.9, 0.4, 3.9), materials.boxExterior);
  boxLid.position.set(-2.6, 2.4, -2.6);
  boxLid.rotation.set(-0.25, 0.35, 0.15);
  addPartMesh("box_lid", boxLid, true);
  partPositions["box_lid"] = new THREE.Vector3(-2.6, 2.4, -2.6);

  // Gold Brand Ribbon on Lid
  const goldRibbon = new THREE.Mesh(new THREE.BoxGeometry(5.0, 0.42, 0.35), materials.boxGold);
  goldRibbon.position.copy(boxLid.position);
  goldRibbon.rotation.copy(boxLid.rotation);
  addPartMesh("box_lid", goldRibbon, false);

  // --- 2. Smart Powerbank Notebook (PM-NB) ---
  const nbGroup = new THREE.Group();
  const nbCover = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.22, 2.3), materials.leatherBlack);
  const nbCoil = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 2.2, 16), materials.brassGold);
  nbCoil.rotation.x = Math.PI / 2;
  nbCoil.position.set(-0.78, 0.05, 0);
  const nbLogo = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.02, 0.4), materials.boxGold);
  nbLogo.position.set(0, 0.12, 0.2);
  nbGroup.add(nbCover, nbCoil, nbLogo);
  nbGroup.position.set(-1.1, 0.15, 0.4);
  nbGroup.rotation.y = 0.08;
  addPartMesh("PM-NB", nbCover, true);
  partPositions["PM-NB"] = new THREE.Vector3(-1.1, 0.5, 0.4);

  // --- 3. MagSafe Wireless Powerbank 10000mAh (PM-PB10K) ---
  const pbGroup = new THREE.Group();
  const pbBody = new THREE.Mesh(new THREE.BoxGeometry(0.95, 0.24, 1.4), materials.brushedMetal);
  const pbRing = new THREE.Mesh(new THREE.RingGeometry(0.2, 0.28, 32), materials.accentCyan);
  pbRing.rotation.x = -Math.PI / 2;
  pbRing.position.set(0, 0.13, 0);
  const pbLed = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.02, 0.06), materials.ledGlow);
  pbLed.position.set(0.3, 0.13, 0.55);
  pbGroup.add(pbBody, pbRing, pbLed);
  pbGroup.position.set(-1.1, 0.7, -0.9);
  pbGroup.rotation.y = -0.12;
  addPartMesh("PM-PB10K", pbBody, true);
  partPositions["PM-PB10K"] = new THREE.Vector3(-1.1, 0.95, -0.9);

  // --- 4. Thermal Tumbler SUS316 (PM-TMB) ---
  const tmbGroup = new THREE.Group();
  const tmbBody = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.36, 1.9, 32), materials.stainless);
  const tmbCap = new THREE.Mesh(new THREE.CylinderGeometry(0.43, 0.43, 0.35, 32), materials.boxExterior);
  tmbCap.position.y = 1.0;
  const tmbRing = new THREE.Mesh(new THREE.CylinderGeometry(0.44, 0.44, 0.08, 32), materials.brassGold);
  tmbRing.position.y = 0.8;
  tmbGroup.add(tmbBody, tmbCap, tmbRing);
  tmbGroup.position.set(1.25, 0.45, 0.85);
  tmbGroup.rotation.z = -0.15;
  tmbGroup.rotation.x = 0.25;
  addPartMesh("PM-TMB", tmbBody, true);
  partPositions["PM-TMB"] = new THREE.Vector3(1.25, 1.2, 0.85);

  // --- 5. Smart LED Temperature Bottle (PM-BOTTLE-LED) ---
  const ledBotGroup = new THREE.Group();
  const botBody = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 2.1, 32), materials.boxExterior);
  const botCap = new THREE.Mesh(new THREE.CylinderGeometry(0.39, 0.39, 0.3, 32), materials.brushedMetal);
  botCap.position.y = 1.1;
  const botScreen = new THREE.Mesh(new THREE.CircleGeometry(0.24, 32), materials.ledGlow);
  botScreen.rotation.x = -Math.PI / 2;
  botScreen.position.set(0, 1.26, 0);
  ledBotGroup.add(botBody, botCap, botScreen);
  ledBotGroup.position.set(0.15, 1.4, -0.6);
  ledBotGroup.rotation.x = -0.3;
  ledBotGroup.rotation.y = 0.4;
  addPartMesh("PM-BOTTLE-LED", botBody, true);
  partPositions["PM-BOTTLE-LED"] = new THREE.Vector3(0.15, 1.8, -0.6);

  // --- 6. Solid Walnut Brass Gel Pen (PM-PEN) ---
  const penGroup = new THREE.Group();
  const penBody = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.6, 16), materials.walnutWood);
  const penTip = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.25, 16), materials.brassGold);
  penTip.position.y = -0.9;
  const penClip = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.5, 0.08), materials.brassGold);
  penClip.position.set(0, 0.5, 0.08);
  penGroup.add(penBody, penTip, penClip);
  penGroup.position.set(0.15, 0.22, 1.3);
  penGroup.rotation.z = Math.PI / 2 - 0.2;
  addPartMesh("PM-PEN", penBody, true);
  partPositions["PM-PEN"] = new THREE.Vector3(0.15, 0.5, 1.3);

  // --- 7. Auto UPF50+ Folding Umbrella (PM-UMB) ---
  const umbGroup = new THREE.Group();
  const umbCanopy = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 1.8, 24), materials.umbrellaCloth);
  const umbHandle = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.4, 24), materials.boxExterior);
  umbHandle.position.y = -1.0;
  const umbButton = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.12, 0.08), materials.brassGold);
  umbButton.position.set(0.24, -0.95, 0);
  umbGroup.add(umbCanopy, umbHandle, umbButton);
  umbGroup.position.set(1.5, 0.8, -0.7);
  umbGroup.rotation.x = 0.35;
  umbGroup.rotation.z = 0.2;
  addPartMesh("PM-UMB", umbCanopy, true);
  partPositions["PM-UMB"] = new THREE.Vector3(1.5, 1.2, -0.7);

  // --- 8. Double-Wall Borosilicate Tea Infuser (PM-TEA-INF) ---
  const teaGroup = new THREE.Group();
  const teaGlass = new THREE.Mesh(new THREE.CylinderGeometry(0.36, 0.36, 1.7, 32), materials.glass);
  const teaFilter = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.6, 24), materials.stainless);
  teaFilter.position.y = 0.25;
  const teaCap = new THREE.Mesh(new THREE.CylinderGeometry(0.37, 0.37, 0.25, 32), materials.walnutWood);
  teaCap.position.y = 0.95;
  teaGroup.add(teaGlass, teaFilter, teaCap);
  teaGroup.position.set(-0.35, 1.2, 0.95);
  teaGroup.rotation.x = 0.4;
  teaGroup.rotation.z = -0.3;
  addPartMesh("PM-TEA-INF", teaGlass, true);
  partPositions["PM-TEA-INF"] = new THREE.Vector3(-0.35, 1.6, 0.95);

  // --- 9. Dual Metal Flash Drive (PM-FLASH) ---
  const flashGroup = new THREE.Group();
  const flashBody = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.1, 0.6), materials.stainless);
  const flashSwivel = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.14, 0.45), materials.brassGold);
  flashSwivel.position.set(0, 0, 0.2);
  flashGroup.add(flashBody, flashSwivel);
  flashGroup.position.set(0.9, 0.2, 0.2);
  flashGroup.rotation.y = 0.5;
  addPartMesh("PM-FLASH", flashBody, true);
  partPositions["PM-FLASH"] = new THREE.Vector3(0.9, 0.45, 0.2);

  // Register Titles for HTML Annotations
  const partTitles = {
    "box_lid": { title: "Luxury Box Lid", sub: "กล่องของขวัญแข็งสั่งทำพิเศษ" },
    "box_base": { title: "Custom Cushion Tray", sub: "ฐานรองและช่องใส่กำมะหยี่" },
    "PM-NB": { title: "Smart Notebook (PM-NB)", sub: "สมุดโน้ตหนัง PU ฝัง Powerbank" },
    "PM-PB10K": { title: "MagSafe 10K (PM-PB10K)", sub: "พาวเวอร์แบงก์แม่เหล็กไร้สาย" },
    "PM-TMB": { title: "Tumbler SUS316 (PM-TMB)", sub: "แก้วทัมเบลอร์เก็บอุณหภูมิ" },
    "PM-BOTTLE-LED": { title: "LED Bottle (PM-BOTTLE-LED)", sub: "กระบอกน้ำบอกอุณหภูมิหน้าจอ" },
    "PM-PEN": { title: "Brass Walnut Pen (PM-PEN)", sub: "ปากกาไม้แท้หัวทองเหลือง" },
    "PM-UMB": { title: "Auto Umbrella (PM-UMB)", sub: "ร่มพับออโต้เคลือบกันแดด UPF50+" },
    "PM-TEA-INF": { title: "Tea Infuser (PM-TEA-INF)", sub: "กระบอกชงชาแก้ว Borosilicate" },
    "PM-FLASH": { title: "Dual USB Flash (PM-FLASH)", sub: "แฟลชไดร์ฟโลหะหมุน Type-C/USB" }
  };

  // Build HTML Annotation Elements
  if (labelsLayer) {
    labelsLayer.querySelectorAll(".anatomy-3d-label").forEach(el => el.remove());
    for (const [pid, info] of Object.entries(partTitles)) {
      const labelDiv = document.createElement("div");
      labelDiv.className = "pc-anatomy-label anatomy-3d-label";
      labelDiv.dataset.part = pid;
      labelDiv.innerHTML = `<strong>${info.title}</strong><span>${info.sub}</span>`;
      labelsLayer.appendChild(labelDiv);
      partLabels[pid] = labelDiv;
    }
  }

  // Raycasting & Interaction
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  let hoveredPartId = null;
  let selectedPartId = "PM-TMB";

  function highlightPart(partId, isHover = false) {
    for (const obj of partsGroup.children) {
      if (obj.userData.isOutline) {
        obj.visible = (obj.userData.partId === partId) || (obj.userData.partId === selectedPartId);
        if (obj.userData.partId === partId) {
          obj.material.color.setHex(0x38d6df);
        } else if (obj.userData.partId === selectedPartId) {
          obj.material.color.setHex(0xd4af37);
        }
      }
    }
    if (labelsLayer) {
      labelsLayer.querySelectorAll(".anatomy-3d-label").forEach(lbl => {
        const isActive = (lbl.dataset.part === partId) || (lbl.dataset.part === selectedPartId);
        lbl.classList.toggle("is-active", isActive);
      });
    }
  }

  function onPointerMove(e) {
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(interactiveMeshes, false);

    if (intersects.length > 0) {
      const pid = intersects[0].object.userData.partId;
      if (pid !== hoveredPartId) {
        hoveredPartId = pid;
        canvas.style.cursor = "pointer";
        highlightPart(hoveredPartId, true);
      }
    } else {
      if (hoveredPartId) {
        hoveredPartId = null;
        canvas.style.cursor = "default";
        highlightPart(selectedPartId, false);
      }
    }
  }

  function onPointerDown(e) {
    if (hoveredPartId) {
      selectedPartId = hoveredPartId;
      highlightPart(selectedPartId, false);
      // Dispatch event to window to sync with UI catalog
      window.dispatchEvent(new CustomEvent("gift-part-select", { detail: { partId: selectedPartId } }));
    }
  }

  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerdown", onPointerDown);

  // Viewport Control Buttons
  const btnReset = document.querySelector("#reset-3d-view");
  const btnRotL = document.querySelector("#rotate-3d-left");
  const btnRotR = document.querySelector("#rotate-3d-right");
  const btnZoomIn = document.querySelector("#zoom-3d-in");
  const btnZoomOut = document.querySelector("#zoom-3d-out");

  if (btnReset) btnReset.addEventListener("click", () => {
    camera.position.set(7.5, 6.2, 8.5);
    controls.target.set(0, 0.2, 0);
    controls.update();
  });
  if (btnRotL) btnRotL.addEventListener("click", () => {
    const angle = 0.4;
    const x = camera.position.x * Math.cos(angle) + camera.position.z * Math.sin(angle);
    const z = -camera.position.x * Math.sin(angle) + camera.position.z * Math.cos(angle);
    camera.position.x = x;
    camera.position.z = z;
    controls.update();
  });
  if (btnRotR) btnRotR.addEventListener("click", () => {
    const angle = -0.4;
    const x = camera.position.x * Math.cos(angle) + camera.position.z * Math.sin(angle);
    const z = -camera.position.x * Math.sin(angle) + camera.position.z * Math.cos(angle);
    camera.position.x = x;
    camera.position.z = z;
    controls.update();
  });
  if (btnZoomIn) btnZoomIn.addEventListener("click", () => {
    camera.position.multiplyScalar(0.85);
    controls.update();
  });
  if (btnZoomOut) btnZoomOut.addEventListener("click", () => {
    camera.position.multiplyScalar(1.15);
    controls.update();
  });

  // Update Projected 2D Annotations
  const projVec = new THREE.Vector3();
  function updateAnnotations() {
    if (!labelsLayer || !svgLayer) return;
    const w = stage.clientWidth;
    const h = stage.clientHeight;
    svgLayer.setAttribute("viewBox", `0 0 ${w} ${h}`);
    let svgPaths = "";

    for (const [pid, pos3D] of Object.entries(partPositions)) {
      projVec.copy(pos3D).project(camera);
      // Behind camera check
      if (projVec.z > 1) continue;

      const screenX = (projVec.x * 0.5 + 0.5) * w;
      const screenY = (-(projVec.y * 0.5) + 0.5) * h;

      const labelEl = partLabels[pid];
      if (labelEl) {
        const isRight = screenX > w * 0.5;
        const targetX = isRight ? Math.min(screenX + 45, w - 150) : Math.max(screenX - 150, 10);
        const targetY = screenY;

        labelEl.style.left = `${targetX}px`;
        labelEl.style.top = `${targetY}px`;

        const isActive = (pid === hoveredPartId) || (pid === selectedPartId);
        const strokeColor = isActive ? "#38d6df" : "#2d3e4c";
        const strokeWidth = isActive ? "1.8" : "1.0";
        svgPaths += `<path d="M ${screenX} ${screenY} L ${isRight ? targetX : targetX + 130} ${targetY}" stroke="${strokeColor}" stroke-width="${strokeWidth}" fill="none"/>`;
        svgPaths += `<circle cx="${screenX}" cy="${screenY}" r="${isActive ? 3.5 : 2.0}" fill="${strokeColor}"/>`;
      }
    }
    svgLayer.innerHTML = svgPaths;
  }

  // Animation Loop
  let reqId;
  function animate() {
    reqId = requestAnimationFrame(animate);
    controls.update();

    // Subtle idle floating motion
    const t = Date.now() * 0.001;
    boxLid.position.y = 2.4 + Math.sin(t * 1.2) * 0.08;
    ledBotGroup.position.y = 1.4 + Math.sin(t * 1.5 + 1) * 0.06;
    tmbGroup.position.y = 0.45 + Math.sin(t * 1.4 + 2) * 0.05;
    teaGroup.position.y = 1.2 + Math.sin(t * 1.3 + 3) * 0.07;

    renderer.render(scene, camera);
    updateAnnotations();
  }

  animate();

  // Resize Handling
  function onWindowResize() {
    if (!stage) return;
    width = stage.clientWidth || 600;
    height = stage.clientHeight || 540;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }
  window.addEventListener("resize", onWindowResize);

  if (statusEl) {
    statusEl.textContent = "3D Exploded Anatomy Ready";
    statusEl.style.color = "#187044";
  }
  stage.classList.add("webgl-ready");
}
