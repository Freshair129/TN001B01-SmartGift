(function () {
  'use strict';

  const categories = [
    ['eco-friendly', 'รักษ์โลก'],
    ['executive-smart-tech', 'เทคโนโลยีและการทำงาน'],
    ['classic-oriental', 'ศิลปะและวัฒนธรรม'],
    ['novelty-self-care', 'ไลฟ์สไตล์และการดูแลตัวเอง'],
  ];
  const array = value => Array.isArray(value) ? value : [];
  const label = value => typeof value === 'string' ? value.trim() : '';
  const customerName = value => label(value).replace(/\s*\(P-[A-Z0-9]+\)?\s*$/i, '').trim();

  function sourcePhotos(media) {
    const entries = [
      ...array(media?.products).map(item => ({ ...item, kind: 'single' })),
      ...array(media?.sets).map(item => ({ ...item, kind: 'set' })),
    ];
    const counts = new Map();
    for (const entry of entries) {
      const id = `${entry.kind}:${label(entry.code)}`;
      counts.set(id, (counts.get(id) || 0) + 1);
    }
    return entries.filter(item => label(item.code) &&
      counts.get(`${item.kind}:${label(item.code)}`) === 1 &&
      item.generated_from_catalog === false && item.visual_status === 'source-photo' &&
      /^\/assets\/catalog-media\/[a-zA-Z0-9_-][a-zA-Z0-9_.-]*\.(?:png|webp|jpg|jpeg)$/.test(item.image) &&
      !item.image.includes('..')
    ).map(item => ({ code: label(item.code), name: label(item.title) || label(item.code), image: item.image, kind: item.kind }));
  }

  function detailComponents(offer, master) {
    // Source photograph contradicts this legacy BOM. Do not silently repair data.
    if (label(offer?.offer_code) === 'TGC09-3') return { status: 'conflict', items: [] };
    const parts = array(offer?.components);
    if (offer?.bom_status !== 'verified' || !parts.length) return { status: 'pending', items: [] };
    const products = array(master?.canonical_products);
    const items = [];
    for (const part of parts) {
      const matches = products.filter(p => label(p?.code) === label(part?.product_code));
      if (matches.length !== 1 || !Number.isInteger(part.qty) || part.qty <= 0) return { status: 'pending', items: [] };
      items.push({ name: customerName(matches[0].name_th) || customerName(matches[0].name_en) || label(part.product_code), qty: part.qty });
    }
    return { status: 'verified', items };
  }

  function buildCatalog(master, media) {
    const photos = new Map(sourcePhotos(media).map(item => [`${item.kind}:${item.code}`, item]));
    const rows = [];
    const seen = new Set();
    for (const [kind, records] of [['single', array(master?.canonical_products)], ['set', array(master?.catalog_offers)]]) {
      for (const record of records) {
        if (!record || typeof record !== 'object') continue;
        const code = label(kind === 'single' ? record.code : record.offer_code || record.code);
        const id = `${kind}:${code}`;
        if (!code || seen.has(id)) continue;
        seen.add(id);
        rows.push({
          id, code, kind,
          kindLabel: kind === 'single' ? 'สินค้ารายชิ้น' : 'รายการจากแคตตาล็อก',
          name: customerName(kind === 'single' ? record.name_th || record.name_en : record.name) || code,
          category: label(kind === 'single' ? record.category_slug : record.interest_theme_slug),
          image: photos.get(id)?.image || '',
          // No sale-price authority is established by an SRP or price-tier number alone.
          priceLabel: 'สอบถามราคา',
          contents: kind === 'set' ? detailComponents(record, master) : null,
        });
      }
    }
    return rows;
  }

  function selectItems(items, category, kind) {
    return items.filter(item => (!category || item.category === category) && item.kind === kind)
      .sort((a, b) => Number(Boolean(b.image)) - Number(Boolean(a.image)));
  }

  const api = { buildCatalog, selectItems, sourcePhotos, detailComponents };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;

  const root = document.querySelector('#customer-catalog');
  if (!root) return;
  const internalTitle = document.title;
  let items = [];
  let photos = [];
  let category = '';
  let kind = 'set';
  let limit = 24;
  let loaded = false;
  let failed = false;
  let returnFocus = null;

  const element = (tag, className, text) => {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  };
  const button = (text, className, handler) => {
    const el = element('button', className, text);
    el.type = 'button';
    el.addEventListener('click', handler);
    return el;
  };

  root.innerHTML = `
    <header class="customer-header"><a class="customer-brand" href="#/catalog" aria-label="SmartGift หน้ารวมสินค้า">SmartGift<span>ของขวัญองค์กร</span></a><span class="customer-header-note">เลือกจากสิ่งที่ใช่ ให้ได้อย่างใส่ใจ</span></header>
    <main class="customer-main">
      <div class="customer-intro"><h1>สินค้าและชุดของขวัญองค์กร</h1><p>ดูภาพ เลือกหมวด แล้วเปิดดูรายละเอียดสินค้าที่สนใจ</p></div>
      <section class="customer-browse" aria-labelledby="customer-browse-title">
        <h2 id="customer-browse-title">เลือกดูสินค้า</h2>
        <div class="customer-categories" role="group" aria-label="หมวดสินค้า"></div>
        <div class="customer-list-head"><div class="customer-types" role="group" aria-label="ประเภทรายการ"></div><p class="customer-count" aria-live="polite" aria-atomic="true"></p></div>
        <div class="customer-feedback" role="status"></div>
        <div class="customer-items"></div>
        <div class="customer-more"></div>
      </section>
      <section class="customer-references" aria-labelledby="customer-references-title" hidden>
        <div class="customer-section-head"><h2 id="customer-references-title">ภาพอ้างอิงเพิ่มเติม</h2><span>ภาพต้นฉบับ</span></div>
        <p class="customer-reference-note">รูปอ้างอิงเหล่านี้ยังไม่จับคู่กับรายการขาย จึงยังไม่แสดงราคาและข้อมูลชุดร่วมกัน</p>
        <div class="customer-photo-grid"></div>
      </section>
      <footer class="customer-footer">ภาพและรายละเอียดช่วยประกอบการเลือกสินค้า กรุณายืนยันราคาและรายละเอียดก่อนสั่งซื้อ</footer>
    </main>
    <dialog class="customer-dialog" aria-labelledby="customer-detail-title"><div class="customer-dialog-bar"><span>รายละเอียดสินค้า</span><button type="button" class="customer-close" aria-label="ปิดรายละเอียด">ปิด <span aria-hidden="true">×</span></button></div><div class="customer-detail"></div></dialog>
  `;
  const dialog = root.querySelector('dialog');
  root.querySelector('.customer-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('customer-dialog-open');
    if (returnFocus?.isConnected && !root.hidden) returnFocus.focus();
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });

  function picture(item, eager = false) {
    const wrap = element('div', 'customer-picture');
    if (!item.image) {
      wrap.classList.add('customer-no-photo');
      wrap.append(element('span', '', 'ยังไม่มีภาพสินค้า'));
      return wrap;
    }
    const img = element('img');
    img.src = item.image;
    img.alt = item.name;
    img.loading = eager ? 'eager' : 'lazy';
    img.decoding = 'async';
    img.addEventListener('error', () => {
      wrap.classList.add('customer-no-photo');
      wrap.replaceChildren(element('span', '', 'ยังไม่มีภาพสินค้า'));
    }, { once: true });
    wrap.append(img);
    return wrap;
  }

  function openDetails(item, reference, trigger) {
    returnFocus = trigger;
    const content = root.querySelector('.customer-detail');
    content.replaceChildren();
    if (item.image) content.append(picture(item, true));
    const copy = element('div', 'customer-detail-copy');
    const heading = element('h2', '', item.name);
    heading.id = 'customer-detail-title';
    copy.append(element('p', 'customer-overline', reference ? 'ภาพอ้างอิงจากแคตตาล็อก' : item.kindLabel), heading);
    copy.append(element('p', 'customer-reference-code', `รหัสอ้างอิง ${item.code}`));
    if (reference) {
      copy.append(element('p', 'customer-notice', 'ภาพต้นฉบับจากแคตตาล็อก ยังไม่จับคู่กับรายการขาย จึงไม่ใช้ภาพนี้ยืนยันราคา ส่วนประกอบ หรือความพร้อมจำหน่าย'));
    } else {
      copy.append(element('p', 'customer-detail-price', item.priceLabel));
      if (!item.image) copy.append(element('p', 'customer-notice', 'ยังไม่มีภาพที่ยืนยันตรงกับรายการนี้'));
      if (item.kind === 'set') {
        if (item.contents.status === 'verified') {
          copy.append(element('h3', '', 'ในชุดประกอบด้วย'));
          const list = element('ul', 'customer-contents');
          for (const part of item.contents.items) list.append(element('li', '', `${part.name} × ${part.qty}`));
          copy.append(list);
        } else {
          copy.append(element('p', 'customer-notice', 'รูปแบบสินค้าและส่วนประกอบอยู่ระหว่างยืนยัน'));
        }
      } else {
        copy.append(element('p', 'customer-notice', 'รายละเอียดวัสดุ สี ขนาด และจำนวนสั่งซื้ออยู่ระหว่างยืนยัน'));
      }
      copy.append(element('p', 'customer-detail-note', 'โปรดแจ้งรหัสอ้างอิงนี้เมื่อติดต่อทีมขาย เพื่อยืนยันรายละเอียดก่อนสั่งซื้อ'));
    }
    content.append(copy);
    document.body.classList.add('customer-dialog-open');
    dialog.showModal();
    root.querySelector('.customer-close').focus();
  }

  function renderReferences() {
    // Unmapped photographs remain a separate, explicitly labelled source gallery.
    const ids = new Set(items.map(item => item.id));
    const unmatched = photos.filter(photo => !ids.has(`${photo.kind}:${photo.code}`));
    const section = root.querySelector('.customer-references');
    section.hidden = !unmatched.length;
    const grid = root.querySelector('.customer-photo-grid');
    grid.replaceChildren();
    for (const [index, item] of unmatched.entries()) {
      const tile = button('', 'customer-photo-tile', event => openDetails(item, true, event.currentTarget));
      tile.setAttribute('aria-label', `ดูภาพอ้างอิง ${item.code}`);
      tile.append(picture(item, index < 4), element('span', 'customer-photo-name', item.name), element('span', 'customer-photo-code', item.code));
      grid.append(tile);
    }
  }

  function filterChanged() {
    limit = 24;
    if (dialog.open) dialog.close();
    renderList();
  }

  for (const [code, title] of [['', 'ทั้งหมด'], ...categories]) {
    const control = button(title, 'customer-category', () => { category = code; filterChanged(); });
    control.dataset.category = code;
    root.querySelector('.customer-categories').append(control);
  }
  for (const [value, title] of [['set', 'รายการจากแคตตาล็อก'], ['single', 'สินค้ารายชิ้น']]) {
    const control = button(title, 'customer-type', () => { kind = value; filterChanged(); });
    control.dataset.kind = value;
    root.querySelector('.customer-types').append(control);
  }

  function renderList() {
    root.querySelectorAll('[data-category]').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.category === category)));
    root.querySelectorAll('[data-kind]').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.kind === kind)));
    const visible = selectItems(items, category, kind);
    root.querySelector('.customer-count').textContent = loaded ? `${visible.length.toLocaleString('th-TH')} รายการ` : '';
    const feedback = root.querySelector('.customer-feedback');
    feedback.replaceChildren();
    root.querySelector('.customer-browse').setAttribute('aria-busy', String(!loaded && !failed));
    if (failed) {
      feedback.append(element('p', '', 'ยังโหลดรายการสินค้าไม่ได้ กรุณาลองอีกครั้ง'), button('ลองโหลดสินค้าอีกครั้ง', 'customer-retry', () => location.reload()));
    } else if (!loaded) {
      feedback.append(element('p', '', 'กำลังโหลดรายการสินค้า…'));
    } else if (!visible.length) {
      feedback.append(element('p', '', 'ยังไม่มีรายการในหมวดนี้ ลองเลือกหมวดอื่นหรือประเภทรายการอื่น'));
    }
    feedback.hidden = loaded && visible.length > 0;
    const list = root.querySelector('.customer-items');
    list.replaceChildren();
    for (const item of visible.slice(0, limit)) {
      const article = element('article', 'customer-item');
      if (item.image) article.classList.add('customer-item-with-photo');
      const action = button('', 'customer-item-action', event => openDetails(item, false, event.currentTarget));
      action.setAttribute('aria-label', `ดูรายละเอียด ${item.name} ${item.code}`);
      const copy = element('div', 'customer-item-copy');
      copy.append(element('span', 'customer-item-code', item.code), element('h3', '', item.name));
      const meta = element('div', 'customer-item-meta');
      meta.append(element('span', 'customer-item-price', item.priceLabel), element('span', 'customer-item-link', 'ดูรายละเอียด →'));
      action.append(picture(item), copy, meta);
      article.append(action);
      list.append(article);
    }
    const more = root.querySelector('.customer-more');
    more.replaceChildren();
    if (visible.length > limit) {
      more.append(element('p', '', `แสดง ${limit} จาก ${visible.length} รายการ`));
      more.append(button('แสดงสินค้าเพิ่มเติม', 'customer-load-more', () => {
        const previous = limit;
        limit += 24;
        renderList();
        root.querySelectorAll('.customer-item-action')[previous]?.focus();
      }));
    }
  }

  window.CustomerCatalog = {
    setRoute(active) {
      root.hidden = !active;
      document.title = active ? 'SmartGift — สินค้าและชุดของขวัญองค์กร' : internalTitle;
      document.body.classList.toggle('customer-view', active);
      if (!active && dialog.open) dialog.close();
    },
    setData(master, media) {
      if (dialog.open) dialog.close();
      items = buildCatalog(master, media);
      photos = sourcePhotos(media);
      loaded = true;
      failed = false;
      renderReferences();
      renderList();
    },
    setError() { failed = true; loaded = false; items = []; photos = []; renderReferences(); renderList(); },
  };
  renderList();
})();
