// SmartGift Floating 2.5D Glassmorphism Anatomy Engine
// High-fidelity isometric multi-layer exploded gift box decomposition

(function() {
  const stage = document.querySelector("#gift-anatomy-stage");
  if (!stage) return;

  const deck = document.querySelector("#deck-viewport");
  const explodeSlider = document.querySelector("#explode-slider");
  const explodeValText = document.querySelector("#explode-val-text");
  const btnCompact = document.querySelector("#preset-compact");
  const btnFloat = document.querySelector("#preset-float");
  const btnExplode = document.querySelector("#preset-explode");
  const btnAutoRotate = document.querySelector("#preset-rotate");

  let explodeZ = 75; // default 2.5D float distance in px
  let isAutoRotating = false;
  let currentRotX = 52;
  let currentRotZ = -26;
  let targetRotX = 52;
  let targetRotZ = -26;
  let autoAngle = 0;

  function updateExplodeDistance(val) {
    explodeZ = parseInt(val, 10);
    stage.style.setProperty("--explode-z", `${explodeZ}px`);
    if (explodeSlider) explodeSlider.value = explodeZ;
    if (explodeValText) explodeValText.textContent = `${explodeZ}px`;

    if (btnCompact) btnCompact.setAttribute("aria-pressed", String(explodeZ === 0));
    if (btnFloat) btnFloat.setAttribute("aria-pressed", String(explodeZ > 0 && explodeZ <= 90));
    if (btnExplode) btnExplode.setAttribute("aria-pressed", String(explodeZ > 90));
  }

  if (explodeSlider) {
    explodeSlider.addEventListener("input", e => updateExplodeDistance(e.target.value));
  }

  if (btnCompact) btnCompact.addEventListener("click", () => updateExplodeDistance(0));
  if (btnFloat) btnFloat.addEventListener("click", () => updateExplodeDistance(75));
  if (btnExplode) btnExplode.addEventListener("click", () => updateExplodeDistance(140));
  if (btnAutoRotate) {
    btnAutoRotate.addEventListener("click", () => {
      isAutoRotating = !isAutoRotating;
      btnAutoRotate.setAttribute("aria-pressed", String(isAutoRotating));
      btnAutoRotate.classList.toggle("active-pulse", isAutoRotating);
    });
  }

  // Mouse Parallax 2.5D Tilt Interaction
  stage.addEventListener("mousemove", e => {
    if (isAutoRotating) return;
    const rect = stage.getBoundingClientRect();
    const nx = (e.clientX - rect.left) / rect.width - 0.5; // -0.5 to 0.5
    const ny = (e.clientY - rect.top) / rect.height - 0.5;

    targetRotX = 52 - ny * 18;
    targetRotZ = -26 + nx * 24;
  });

  stage.addEventListener("mouseleave", () => {
    if (!isAutoRotating) {
      targetRotX = 52;
      targetRotZ = -26;
    }
  });

  // Animation Loop with smooth dampening
  function renderLoop() {
    requestAnimationFrame(renderLoop);

    if (isAutoRotating) {
      autoAngle += 0.008;
      targetRotX = 52 + Math.sin(autoAngle * 0.8) * 8;
      targetRotZ = -26 + Math.sin(autoAngle) * 35;
    }

    currentRotX += (targetRotX - currentRotX) * 0.08;
    currentRotZ += (targetRotZ - currentRotZ) * 0.08;

    if (deck) {
      deck.style.transform = `rotateX(${currentRotX.toFixed(2)}deg) rotateZ(${currentRotZ.toFixed(2)}deg)`;
    }
  }

  renderLoop();

  // Handle Product Item Hover & Click in 2.5D
  const items = stage.querySelectorAll(".glass-product-card");
  items.forEach(card => {
    card.addEventListener("click", () => {
      items.forEach(c => c.classList.remove("selected-active"));
      card.classList.add("selected-active");
      const pid = card.dataset.part;
      window.dispatchEvent(new CustomEvent("gift-part-select", { detail: { partId: pid } }));
    });
  });

  // Initial set
  updateExplodeDistance(75);
})();
