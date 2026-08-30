"""
SmartGift Offline Customer Catalog Builder
(SPEC-WEB-OFFLINE-CATALOG-INTERACTION-2026-08-30 §6)

Builds, from the customer-safe snapshot only:
  1. output/offline/SmartGift-Catalog-Offline-<version>.html
     — single file, opens from file://, zero network requests, flipbook UX
  2. output/offline/SmartGift-Catalog-Offline-<version>.pdf
     — print proof rendered via headless Chrome (selectable Thai text)
  3. output/offline/SmartGift-Catalog-Offline-<version>.zip
     — HTML + PDF + README-เปิดใช้งาน.txt
  4. data-pipeline/04_review_reports/offline_bundle_manifest.json (internal audit)

Boundary: ADR-004 #3 / SPEC §4. Sources are public/data/pricelist_public.json,
public/data/catalog_media.json and the customer-safe product manifest — never
pricelist_master or factory evidence. A fail-closed scan runs before writing
the ZIP; the build aborts if any forbidden marker or external reference is
found, or if the HTML exceeds the 25 MB budget.
"""

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone

from PIL import Image
from fontTools import subset as ftsubset

sys.stdout.reconfigure(encoding="utf-8")

FONTS_DIR = "pipeline/fonts"
FONT_FACES = (("Sarabun-Regular.ttf", 400), ("Sarabun-Bold.ttf", 700))
FONT_CSS_PLACEHOLDER = "/*__FONT_CSS__*/"


def build_font_css(sample_text):
    """Subset Sarabun (OFL, pipeline/fonts/) to the characters actually used
    and return @font-face rules with WOFF data URIs. Returns "" when the font
    assets are absent so the system stack remains the sole fallback."""
    faces = []
    chars = "".join(sorted(set(sample_text))) + "0123456789฿.,:;+-×%()·—…"
    for filename, weight in FONT_FACES:
        path = os.path.join(FONTS_DIR, filename)
        if not os.path.exists(path):
            return ""
        options = ftsubset.Options(flavor="woff")
        font = ftsubset.load_font(path, options)
        subsetter = ftsubset.Subsetter(options)
        subsetter.populate(text=chars)
        subsetter.subset(font)
        buf = io.BytesIO()
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        faces.append(
            "@font-face{font-family:'Sarabun';font-style:normal;"
            f"font-weight:{weight};"
            f"src:url(data:font/woff;base64,{b64}) format('woff');}}"
        )
    return "".join(faces)

PRICELIST_PUBLIC = "public/data/pricelist_public.json"
CATALOG_MEDIA = "public/data/catalog_media.json"
PUBLIC_MANIFEST = "public/data/product_manifest.json"
ASSETS_ROOT = "public"
OUT_DIR = "output/offline"
AUDIT_MANIFEST = "data-pipeline/04_review_reports/offline_bundle_manifest.json"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

SIZE_BUDGET_BYTES = 25 * 1024 * 1024
IMG_MAX_DIM = 720
HERO_MAX_DIM = 1080
WEBP_QUALITY = 72

FORBIDDEN_MARKERS = (
    "data-pipeline", "factory", "freight", "cbm", "landed",
    "supplier_code", "profit_evaluation", "flowaccount",
)
# Only these substrings containing "http" may appear (SVG/XML namespaces).
ALLOWED_HTTP_NS = ("http://www.w3.org",)

SEASONAL_OCCASIONS = ("christmas_2026", "new_year_2027")
OCCASION_TH = {"christmas_2026": "Christmas 2026", "new_year_2027": "New Year 2027"}
STATUS_TH = {
    "pass": "พร้อมเสนอราคา", "approved": "พร้อมเสนอราคา",
    "below_minimum": "ยังไม่เปิดรับออเดอร์", "rejected": "ยังไม่เปิดรับออเดอร์",
}


def status_label(status):
    return STATUS_TH.get(status, "รอยืนยันรายละเอียด")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def image_data_uri(rel_url, max_dim=IMG_MAX_DIM):
    """Downscale + recompress an allowlisted asset into a webp data URI."""
    path = ASSETS_ROOT + rel_url
    if not os.path.exists(path):
        return None
    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((max_dim, max_dim), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=WEBP_QUALITY, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def ladder_from_prices(price_rows, offer_code, limit=4):
    rows = sorted(
        (r for r in price_rows
         if r["offer_code"] == offer_code and r.get("qty_tier") and (r.get("unit_price") or 0) > 0),
        key=lambda r: r["qty_tier"],
    )
    return [{"qty": r["qty_tier"], "unit_price": r["unit_price"]} for r in rows[:limit]]


def build_dataset():
    pl = load(PRICELIST_PUBLIC)
    cm = load(CATALOG_MEDIA)
    manifest = load(PUBLIC_MANIFEST)

    snapshot_sha = hashlib.sha256(
        json.dumps(
            {
                "pricelist_public": manifest["data_integrity_hashes"]["pricelist_public"]["sha256"],
                "catalog_media": manifest["data_integrity_hashes"]["catalog_media"]["sha256"],
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()

    images = {}

    def register_image(code, rel_url, max_dim=IMG_MAX_DIM):
        if code in images or not rel_url:
            return
        uri = image_data_uri(rel_url, max_dim)
        if uri:
            images[code] = uri

    hero = cm.get("hero") or {}
    if hero.get("image"):
        register_image("__hero__", hero["image"], HERO_MAX_DIM)

    categories = {
        c["slug"]: {"slug": c["slug"], "name_th": c["name_th"], "name_en": c["name_en"]}
        for c in pl.get("portfolio_catalogs", [])
    }

    products = []
    for p in pl.get("srp_reference_products", []):
        code = p["product_code"]
        media = next((m for m in cm.get("products", []) if m["code"] == code), None)
        if media:
            register_image(code, media["image"])
        products.append({
            "code": code,
            "name_th": p.get("name_th"),
            "name_en": p.get("name_en"),
            "category_slug": p.get("category_slug"),
            "srp_price": p.get("srp_price"),
            "price_tiers": (p.get("price_tiers") or [])[:5],
            "visual_status": media.get("visual_status") if media else None,
            "source_label": (media or {}).get("source_label", ""),
        })

    offers_by_code = {o.get("code"): o for o in pl.get("catalog_offers", [])}
    sets = []
    for m in cm.get("sets", []):
        code = m["code"]
        register_image(code, m["image"])
        offer = offers_by_code.get(code) or {}
        ladder = ladder_from_prices(pl.get("prices", []), code)
        media_title = (m.get("title") or "").strip()
        generic = (not media_title or media_title == code
                   or media_title.startswith("ภาพสินค้า") or media_title.startswith("ภาพชุด"))
        title = (offer.get("name_th") or offer.get("name")) if generic else media_title
        sets.append({
            "code": code,
            "title": title or media_title or code,
            "gift_tier": offer.get("gift_tier"),
            "unboxing": offer.get("unboxing_experience") or "",
            "ladder": ladder,
            "visual_status": m.get("visual_status"),
            "source_label": m.get("source_label", ""),
        })

    seasonal_by_id = {o["id"]: o for o in pl.get("seasonal_offers", [])}
    packages = []
    for pkg in pl.get("pkg", []):
        if pkg.get("occasion") not in SEASONAL_OCCASIONS:
            continue
        components = []
        for opt in pkg.get("options", []) or []:
            offer = seasonal_by_id.get(opt.get("offer_id")) or {}
            for comp in offer.get("contains", []) or []:
                components.append({
                    "product_code": comp.get("product_code"),
                    "qty": comp.get("qty"),
                })
        packages.append({
            "code": pkg.get("code"),
            "name": pkg.get("name"),
            "occasion": OCCASION_TH.get(pkg.get("occasion"), pkg.get("occasion")),
            "gift_tier": pkg.get("gift_tier"),
            "recipient_segment": pkg.get("recipient_segment"),
            "status_label": status_label(pkg.get("status")),
            "components": components,
            "ad": {
                "headline": (pkg.get("ad_creative") or {}).get("headline_th", ""),
                "copy": (pkg.get("ad_creative") or {}).get("supporting_copy_th", ""),
            },
        })

    return {
        "catalog_version": manifest["catalog_version"],
        "snapshot_sha256": snapshot_sha,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "operating_entity": manifest.get("operating_entity", ""),
        "disclaimer_th": cm.get("disclaimer_th")
            or "เอกสารนี้เป็น customer catalog snapshot สำหรับอ้างอิงสินค้า ราคาสุทธิยืนยันผ่านใบเสนอราคาเท่านั้น",
        "categories": list(categories.values()),
        "products": products,
        "sets": sets,
        "packages": packages,
        "hero_title": hero.get("title", ""),
        "images": images,
    }


# --------------------------------------------------------------------------
# Page rendering (server-side): each page is a <section class="page"> string.
# --------------------------------------------------------------------------

def esc(v):
    return (str(v if v is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def money(v):
    if isinstance(v, (int, float)):
        return f"฿{v:,.0f}"
    return "สอบถามราคา"


def img_or_placeholder(data, code, alt, cls="ph-img"):
    uri = data["images"].get(code)
    if uri:
        return f'<img class="{cls}" src="{uri}" alt="{esc(alt)}" loading="lazy">'
    return f'<div class="{cls} no-media">ยังไม่มีภาพที่ยืนยัน</div>'


def render_pages(data):
    pages = []  # (title, html)

    ver = esc(data["catalog_version"])
    sha8 = esc(data["snapshot_sha256"][:12])
    hero_img = data["images"].get("__hero__")
    hero_html = (
        f'<img class="cover-hero" src="{hero_img}" alt="SmartGift hero">'
        if hero_img else '<div class="cover-hero no-media">ยังไม่มีภาพที่ยืนยัน</div>'
    )
    pages.append(("ปก", f"""
      <div class="cover">
        <div class="cover-brand"><span class="logo-sg">SG</span> Smart Gift Thailand</div>
        {hero_html}
        <h1>SmartGift Corporate Catalog</h1>
        <p class="cover-sub">ชุดของขวัญองค์กร · Offline Customer Catalog</p>
        <p class="cover-meta">เวอร์ชัน {ver} · snapshot {sha8}…</p>
        <p class="cover-disclaimer">{esc(data["disclaimer_th"])}</p>
      </div>"""))

    toc_entries = []  # filled after layout below; use placeholder now
    pages.append(("สารบัญ", "__TOC__"))

    prods_by_cat = {}
    for p in data["products"]:
        prods_by_cat.setdefault(p["category_slug"], []).append(p)
    for cat in data["categories"]:
        items = prods_by_cat.get(cat["slug"], [])
        cards = []
        for p in items:
            tiers = "".join(
                f'<tr><td>{esc(t["min_qty"])}+</td><td>{money(t["unit_price"])}</td></tr>'
                for t in p["price_tiers"]
            )
            table = (f'<table class="mini-ladder"><thead><tr><th>จำนวน</th><th>ราคา/ชิ้น</th></tr></thead>'
                     f'<tbody>{tiers}</tbody></table>') if tiers else '<p class="ask">สอบถามราคา</p>'
            cards.append(f"""
              <article class="prod-card" data-code="{esc(p["code"])}">
                {img_or_placeholder(data, p["code"], p["name_th"])}
                <h4>{esc(p["name_th"])}</h4>
                <div class="code-line">{esc(p["code"])} · SRP {money(p["srp_price"])}</div>
                {table}
              </article>""")
        toc_entries.append((f'สินค้า: {cat["name_th"]}', len(pages)))
        pages.append((cat["name_th"], f"""
          <div class="page-head"><span class="eyebrow">สินค้ารายชิ้น</span>
            <h2>{esc(cat["name_th"])}</h2><p>{esc(cat["name_en"])}</p></div>
          <div class="prod-grid">{"".join(cards) or '<p class="ask">ยังไม่มีรายละเอียดที่ยืนยัน</p>'}</div>"""))

    per_page = 4
    set_chunks = [data["sets"][i:i + per_page] for i in range(0, len(data["sets"]), per_page)]
    if set_chunks:
        toc_entries.append(("ชุดของขวัญ (Gift Sets)", len(pages)))
    for idx, chunk in enumerate(set_chunks):
        cards = []
        for s in chunk:
            ladder = " · ".join(
                f'{t["qty"]}+ {money(t["unit_price"])}' for t in s["ladder"]
            ) or "สอบถามราคา"
            tier = f' <span class="tier">{esc(s["gift_tier"])}</span>' if s["gift_tier"] else ""
            cards.append(f"""
              <article class="set-card" data-code="{esc(s["code"])}">
                {img_or_placeholder(data, s["code"], s["title"])}
                <h4>{esc(s["title"])}</h4>
                <div class="code-line">{esc(s["code"])}{tier}</div>
                <div class="ladder-line">{esc(ladder)}</div>
                <div class="src-line">{esc(s["source_label"] or "ภาพอ้างอิงจาก Catalog")}</div>
              </article>""")
        pages.append((f"ชุดของขวัญ {idx + 1}", f"""
          <div class="page-head"><span class="eyebrow">Gift Sets · หน้า {idx + 1}/{len(set_chunks)}</span>
            <h2>ชุดของขวัญองค์กร</h2></div>
          <div class="set-grid">{"".join(cards)}</div>"""))

    pkg_chunks = [data["packages"][i:i + 2] for i in range(0, len(data["packages"]), 2)]
    if pkg_chunks:
        toc_entries.append(("Seasonal Packages", len(pages)))
    for idx, chunk in enumerate(pkg_chunks):
        cards = []
        for pkg in chunk:
            comps = "".join(
                f'<span class="pill">{esc(c["product_code"])}{"" if c["qty"] is None else f" ×{esc(c[chr(113)+chr(116)+chr(121)])}"}</span>'
                for c in pkg["components"]
            ) or '<span class="pill muted">รอยืนยันส่วนประกอบ</span>'
            cards.append(f"""
              <article class="pkg-card">
                <div class="pkg-head"><div>
                  <div class="code-line">{esc(pkg["code"])} · {esc(pkg["occasion"])}</div>
                  <h3>{esc(pkg["name"])}</h3></div>
                  <span class="badge">{esc(pkg["status_label"])}</span></div>
                <p class="pkg-copy">{esc(pkg["ad"]["headline"] or "Seasonal SmartGift")} — {esc(pkg["ad"]["copy"] or "ชุดของขวัญองค์กรจากสินค้าที่มีจริง")}</p>
                <div class="pkg-facts">
                  <div><span>Tier / Segment</span><strong>{esc(pkg["gift_tier"] or "Mixed")} · {esc(pkg["recipient_segment"] or "mixed")}</strong></div>
                  <div><span>ราคา package</span><strong>สอบถามราคา</strong></div>
                </div>
                <div class="pills">{comps}</div>
              </article>""")
        pages.append((f"Seasonal {idx + 1}", f"""
          <div class="page-head"><span class="eyebrow">Seasonal Expo · หน้า {idx + 1}/{len(pkg_chunks)}</span>
            <h2>Seasonal Packages: Christmas & New Year</h2></div>
          <div class="pkg-grid">{"".join(cards)}</div>"""))

    pages.append(("ติดต่อ", f"""
      <div class="cover">
        <div class="cover-brand"><span class="logo-sg">SG</span> Smart Gift Thailand</div>
        <h2>ขอใบเสนอราคา</h2>
        <p class="cover-sub">แจ้งรหัสสินค้า/ชุดที่สนใจและจำนวนโดยประมาณกับทีมขาย SmartGift<br>
        ราคาสุทธิ เงื่อนไขงานสกรีนโลโก้ และกำหนดส่ง ยืนยันผ่านใบเสนอราคาเท่านั้น</p>
        <p class="cover-meta">{esc(data["operating_entity"])}</p>
        <p class="cover-meta">เวอร์ชัน {ver} · snapshot {sha8}… · สร้างเมื่อ {esc(data["generated_at"][:10])}</p>
        <p class="cover-disclaimer">{esc(data["disclaimer_th"])}</p>
      </div>"""))

    toc_html = "".join(
        f'<button class="toc-item" data-page="{n}"><span>{esc(t)}</span><span class="toc-page">หน้า {n + 1}</span></button>'
        for t, n in toc_entries
    )
    for i, (title, html) in enumerate(pages):
        if html == "__TOC__":
            pages[i] = (title, f"""
              <div class="page-head"><span class="eyebrow">สารบัญ</span><h2>เนื้อหาในเล่ม</h2></div>
              <div class="toc">{toc_html}</div>
              <p class="cover-disclaimer">รายการที่ยังไม่ยืนยันภาพหรือส่วนประกอบจะแสดงสถานะตามจริง ไม่ใช้ภาพหรือข้อความแทน</p>""")
    return pages


def render_flipbook(data, pages):
    detail_index = {}
    for p in data["products"]:
        detail_index[p["code"]] = {
            "kind": "product", "name": p["name_th"], "code": p["code"],
            "srp": p["srp_price"], "tiers": p["price_tiers"],
            "label": p["source_label"],
        }
    for s in data["sets"]:
        detail_index[s["code"]] = {
            "kind": "set", "name": s["title"], "code": s["code"],
            "tier": s["gift_tier"], "ladder": s["ladder"],
            "unboxing": s["unboxing"], "label": s["source_label"],
        }

    payload = {
        "catalog_version": data["catalog_version"],
        "snapshot_sha256": data["snapshot_sha256"],
        "details": detail_index,
        "images": data["images"],
        "titles": [t for t, _ in pages],
    }
    payload_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    sections = "".join(
        f'<section class="page" data-page="{i}" data-title="{esc(t)}" {"hidden" if i else ""}>{html}</section>'
        for i, (t, html) in enumerate(pages)
    )

    css = """/*__FONT_CSS__*/
:root{--orange:#FC5900;--brown:#675443;--gold:#D6A641;--paper:#FFF8F0;--ink:#2C241F;}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{background:var(--brown);color:var(--ink);font-family:"Sarabun","Leelawadee UI","Segoe UI",Tahoma,"Noto Sans Thai",sans-serif;overflow:hidden}
#book-wrap{position:absolute;inset:52px 0 0 0;display:flex;align-items:center;justify-content:center;overflow:auto}
#book{background:var(--paper);width:min(1060px,96vw);aspect-ratio:297/210;max-height:calc(100vh - 76px);box-shadow:0 18px 60px rgba(0,0,0,.45);border-radius:8px;position:relative;transform-origin:center top}
.page{position:absolute;inset:0;padding:34px 40px;overflow:auto;transition:opacity .28s ease, transform .28s ease}
.page[hidden]{display:none}
.page.flip-out{opacity:0;transform:perspective(1200px) rotateY(-9deg)}
.page.flip-in{opacity:0;transform:perspective(1200px) rotateY(9deg)}
@media (prefers-reduced-motion: reduce){.page{transition:none}}
.eyebrow{color:var(--orange);font-weight:800;font-size:11px;letter-spacing:.08em;text-transform:uppercase}
.page-head h2{font-size:24px;margin:2px 0 4px}
.page-head p{color:#8a7a6c;font-size:13px}
.cover{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:10px}
.cover-brand{font-weight:900;color:var(--brown);display:flex;align-items:center;gap:8px}
.logo-sg{background:var(--orange);color:#fff;border-radius:8px;padding:4px 8px;font-weight:900}
.cover-hero{max-width:46%;max-height:38%;object-fit:contain;border-radius:10px;box-shadow:0 8px 26px rgba(103,84,67,.28)}
.cover h1{font-size:30px;color:var(--ink)}
.cover-sub{color:#7c6a5b;font-size:14px}
.cover-meta{font-size:11.5px;color:#9c8a79}
.cover-disclaimer{font-size:11px;color:#9c8a79;max-width:70%;margin-top:6px}
.toc{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:16px 0}
.toc-item{display:flex;justify-content:space-between;gap:10px;padding:12px 14px;border:1px solid #eadfd2;border-radius:10px;background:#fff;font:inherit;font-weight:700;color:var(--ink);cursor:pointer}
.toc-item:hover{border-color:var(--orange)}
.toc-page{color:var(--orange)}
.prod-grid,.set-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;margin-top:12px}
.prod-card,.set-card{background:#fff;border:1px solid #eee1d3;border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:6px}
.ph-img{width:100%;height:120px;object-fit:contain;border-radius:8px;background:#fff}
.no-media{display:flex;align-items:center;justify-content:center;background:#f4ece2;color:#9c8a79;font-size:12px}
.prod-card h4,.set-card h4{font-size:13.5px;line-height:1.35}
.code-line{font-size:11px;color:#8a7a6c;font-weight:700}
.tier{color:var(--gold);font-weight:800}
.ladder-line{font-size:11.5px;color:var(--ink)}
.src-line{font-size:10px;color:#a29284}
.mini-ladder{width:100%;border-collapse:collapse;font-size:11px}
.mini-ladder th,.mini-ladder td{border-top:1px solid #f0e6d8;padding:3px 4px;text-align:left}
.mini-ladder th{color:#8a7a6c;font-weight:700}
.ask{color:var(--orange);font-weight:800;font-size:12px}
.pkg-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:12px}
.pkg-card{background:#fff;border:1px solid #eee1d3;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:8px}
.pkg-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.pkg-head h3{font-size:16px}
.badge{background:#fbf3e7;border:1px solid var(--gold);color:var(--brown);border-radius:999px;padding:3px 10px;font-size:10.5px;font-weight:800;white-space:nowrap}
.pkg-copy{font-size:12px;color:#6f5f51}
.pkg-facts{display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11.5px}
.pkg-facts span{color:#9c8a79;display:block}
.pills{display:flex;flex-wrap:wrap;gap:6px}
.pill{background:#fff4ea;border:1px solid #f4d9c2;color:var(--brown);border-radius:999px;padding:2px 9px;font-size:10.5px;font-weight:700}
.pill.muted{opacity:.7}
#toolbar{position:fixed;top:0;left:0;right:0;height:52px;background:var(--brown);display:flex;align-items:center;gap:6px;padding:0 10px;z-index:30;box-shadow:0 2px 8px rgba(0,0,0,.3)}
#toolbar .brand{color:#fff;font-weight:900;margin-right:6px;white-space:nowrap}
#toolbar .brand b{color:var(--orange)}
#toolbar button,#toolbar select{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);color:#fff;border-radius:8px;padding:6px 9px;font:inherit;font-size:12px;cursor:pointer}
#toolbar button:hover{background:var(--orange);border-color:var(--orange)}
#toolbar button[aria-pressed="true"]{background:var(--orange);border-color:var(--orange)}
#page-counter{color:#fff;font-size:12px;display:flex;align-items:center;gap:4px}
#page-jump{width:44px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:#fff;border-radius:6px;padding:4px;text-align:center;font:inherit;font-size:12px}
#search-box{flex:1;max-width:230px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:#fff;border-radius:8px;padding:6px 10px;font:inherit;font-size:12px}
#search-box::placeholder{color:rgba(255,255,255,.55)}
#search-results{position:fixed;top:52px;left:0;right:0;max-height:40vh;overflow:auto;background:#fff;z-index:40;box-shadow:0 10px 30px rgba(0,0,0,.3);display:none}
#search-results button{display:block;width:100%;text-align:left;padding:10px 16px;border:0;border-bottom:1px solid #f0e6d8;background:#fff;font:inherit;font-size:12.5px;cursor:pointer}
#search-results button:hover{background:#fff4ea}
#thumb-rail{position:fixed;left:0;top:52px;bottom:0;width:150px;background:rgba(44,36,31,.94);overflow:auto;z-index:25;padding:8px;display:none}
#thumb-rail.open{display:block}
.thumb{width:100%;background:var(--paper);border:2px solid transparent;border-radius:6px;margin-bottom:8px;padding:6px;font:inherit;font-size:10.5px;font-weight:700;color:var(--brown);cursor:pointer;text-align:center}
.thumb img{width:100%;height:56px;object-fit:contain;display:block;margin-bottom:3px}
.thumb[aria-current="true"]{border-color:var(--orange)}
.nav-arrow{position:fixed;top:50%;transform:translateY(-50%);z-index:26;background:rgba(44,36,31,.65);color:#fff;border:0;border-radius:50%;width:44px;height:44px;font-size:19px;cursor:pointer}
.nav-arrow:hover{background:var(--orange)}
#prev-arrow{left:12px}#next-arrow{right:12px}
#overlay{position:fixed;inset:0;background:rgba(44,36,31,.7);z-index:50;display:none;align-items:center;justify-content:center;padding:20px}
#overlay.open{display:flex}
#overlay .sheet{background:var(--paper);border-radius:14px;max-width:640px;width:100%;max-height:84vh;overflow:auto;padding:22px}
#overlay .sheet h3{margin-bottom:6px}
#overlay .close-row{display:flex;justify-content:flex-end}
#overlay .close-row button{background:var(--orange);color:#fff;border:0;border-radius:8px;padding:6px 14px;font:inherit;cursor:pointer}
.detail-item{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:10px 0;border-bottom:1px solid #eee1d3;font-size:12.5px}
.detail-item img{width:100%;object-fit:contain;border-radius:8px;background:#fff}
kbd{background:#eee;border-radius:4px;padding:1px 5px;font-size:11px}
"""

    js = """
(function(){
  "use strict";
  var DATA = JSON.parse(document.getElementById("catalog-data").textContent);
  var pages = Array.prototype.slice.call(document.querySelectorAll(".page"));
  var total = pages.length, current = 0, zoom = 1, autoTimer = null;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var book = document.getElementById("book");

  function show(n, dir){
    n = Math.max(0, Math.min(total - 1, n));
    if (n === current && dir !== "init") return;
    var prev = pages[current];
    current = n;
    pages.forEach(function(p, i){ p.hidden = i !== n; p.classList.remove("flip-out","flip-in"); });
    if (!reduced && dir && dir !== "init"){
      var el = pages[n];
      el.classList.add(dir === "next" ? "flip-in" : "flip-out");
      requestAnimationFrame(function(){ requestAnimationFrame(function(){ el.classList.remove("flip-in","flip-out"); }); });
    }
    document.getElementById("page-num").textContent = (n + 1);
    document.getElementById("page-jump").value = (n + 1);
    var thumbs = document.querySelectorAll(".thumb");
    thumbs.forEach(function(t, i){ t.setAttribute("aria-current", String(i === n)); });
    var cur = document.querySelector('.thumb[aria-current="true"]');
    if (cur && document.getElementById("thumb-rail").classList.contains("open")) cur.scrollIntoView({block:"nearest"});
  }
  function next(){ show(current + 1, "next"); }
  function prev(){ show(current - 1, "prev"); }

  document.getElementById("prev-arrow").addEventListener("click", prev);
  document.getElementById("next-arrow").addEventListener("click", next);
  document.getElementById("btn-first").addEventListener("click", function(){ show(0, "prev"); });
  document.getElementById("btn-last").addEventListener("click", function(){ show(total - 1, "next"); });
  document.getElementById("btn-toc").addEventListener("click", function(){ show(1, "prev"); });
  document.getElementById("page-total").textContent = total;
  document.getElementById("page-jump").addEventListener("change", function(){
    var v = parseInt(this.value, 10); if (!isNaN(v)) show(v - 1, v - 1 > current ? "next" : "prev");
  });
  document.addEventListener("click", function(e){
    var t = e.target.closest(".toc-item"); if (t) show(parseInt(t.dataset.page, 10), "next");
  });

  var rail = document.getElementById("thumb-rail");
  pages.forEach(function(p, i){
    var b = document.createElement("button");
    b.className = "thumb"; b.type = "button";
    var img = p.querySelector("img");
    b.innerHTML = (img ? '<img alt="" src="' + img.getAttribute("src") + '">' : "") +
      (i + 1) + " · " + (p.dataset.title || "");
    b.addEventListener("click", function(){ show(i, i > current ? "next" : "prev"); });
    rail.appendChild(b);
  });
  document.getElementById("btn-thumbs").addEventListener("click", function(){
    rail.classList.toggle("open");
    this.setAttribute("aria-pressed", String(rail.classList.contains("open")));
  });

  var searchBox = document.getElementById("search-box");
  var results = document.getElementById("search-results");
  var index = pages.map(function(p){ return (p.dataset.title + " " + p.textContent).toLowerCase(); });
  searchBox.addEventListener("input", function(){
    var q = this.value.trim().toLowerCase();
    results.innerHTML = ""; results.style.display = q ? "block" : "none";
    if (!q) return;
    var hits = 0;
    index.forEach(function(text, i){
      if (hits >= 12 || text.indexOf(q) < 0) return;
      hits++;
      var pos = text.indexOf(q);
      var snippet = text.substring(Math.max(0, pos - 30), pos + 40).replace(/\\s+/g, " ");
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = "หน้า " + (i + 1) + " · " + (pages[i].dataset.title || "") + " — …" + snippet + "…";
      b.addEventListener("click", function(){ results.style.display = "none"; searchBox.value = ""; show(i, "next"); });
      results.appendChild(b);
    });
    if (!hits){ var d = document.createElement("button"); d.type = "button"; d.textContent = "ไม่พบ \\"" + q + "\\" ในเล่ม"; results.appendChild(d); }
  });
  document.addEventListener("click", function(e){
    if (!results.contains(e.target) && e.target !== searchBox) results.style.display = "none";
  });

  function applyZoom(){ book.style.transform = "scale(" + zoom + ")"; }
  document.getElementById("btn-zoom-in").addEventListener("click", function(){ zoom = Math.min(2.4, zoom + 0.2); applyZoom(); });
  document.getElementById("btn-zoom-out").addEventListener("click", function(){ zoom = Math.max(0.6, zoom - 0.2); applyZoom(); });
  document.getElementById("btn-zoom-fit").addEventListener("click", function(){ zoom = 1; applyZoom(); });

  var autoBtn = document.getElementById("btn-auto");
  var speedSel = document.getElementById("auto-speed");
  function stopAuto(){ if (autoTimer){ clearInterval(autoTimer); autoTimer = null; } autoBtn.setAttribute("aria-pressed", "false"); }
  function startAuto(){
    if (reduced) { autoBtn.title = "ปิดตามการตั้งค่า reduced motion"; return; }
    stopAuto();
    autoTimer = setInterval(function(){ current >= total - 1 ? stopAuto() : next(); }, parseInt(speedSel.value, 10));
    autoBtn.setAttribute("aria-pressed", "true");
  }
  autoBtn.addEventListener("click", function(){ autoTimer ? stopAuto() : startAuto(); });
  speedSel.addEventListener("change", function(){ if (autoTimer) startAuto(); });
  if (reduced){ autoBtn.disabled = true; }

  document.getElementById("btn-full").addEventListener("click", function(){
    document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
  });

  var overlay = document.getElementById("overlay");
  var sheet = document.getElementById("overlay-body");
  function openOverlay(html){ sheet.innerHTML = html; overlay.classList.add("open"); }
  function closeOverlay(){ overlay.classList.remove("open"); }
  overlay.addEventListener("click", function(e){ if (e.target === overlay) closeOverlay(); });
  document.getElementById("overlay-close").addEventListener("click", closeOverlay);

  function moneyTh(v){ return (typeof v === "number") ? "฿" + v.toLocaleString("th-TH") : "สอบถามราคา"; }
  document.getElementById("btn-detail").addEventListener("click", function(){
    var codes = Array.prototype.map.call(pages[current].querySelectorAll("[data-code]"), function(el){ return el.dataset.code; });
    if (!codes.length){ openOverlay("<h3>สินค้าในหน้านี้</h3><p>หน้านี้ไม่มีรายการสินค้า</p>"); return; }
    var html = "<h3>สินค้าในหน้านี้ (" + codes.length + ")</h3>";
    codes.forEach(function(code){
      var d = DATA.details[code]; if (!d) return;
      var img = DATA.images[code];
      var priceLine;
      if (d.kind === "product"){
        priceLine = "SRP " + moneyTh(d.srp) + (d.tiers && d.tiers.length ? " · " + d.tiers.map(function(t){ return t.min_qty + "+ " + moneyTh(t.unit_price); }).join(" · ") : "");
      } else {
        priceLine = d.ladder && d.ladder.length ? d.ladder.map(function(t){ return t.qty + "+ " + moneyTh(t.unit_price); }).join(" · ") : "สอบถามราคา";
      }
      html += '<div class="detail-item">' +
        (img ? '<img alt="" src="' + img + '">' : '<div class="no-media" style="height:90px;border-radius:8px">ยังไม่มีภาพที่ยืนยัน</div>') +
        "<div><strong>" + code + "</strong> — " + (d.name || "") +
        (d.tier ? ' <span class="tier">' + d.tier + "</span>" : "") +
        "<div>" + priceLine + "</div>" +
        (d.unboxing ? '<div style="color:#8a7a6c">' + d.unboxing + "</div>" : "") +
        (d.label ? '<div style="color:#a29284;font-size:11px">' + d.label + "</div>" : "") +
        "</div></div>";
    });
    openOverlay(html);
  });

  document.getElementById("btn-share").addEventListener("click", function(){
    openOverlay("<h3>แชร์ไฟล์นี้</h3>" +
      "<p>ลิงก์คัดลอกไม่ได้เมื่อเปิดจากไฟล์ (file://) — ให้แนบ<strong>ไฟล์นี้ทั้งไฟล์</strong>ในอีเมลหรือแชตแทน</p>" +
      "<p style='margin-top:8px'>ชื่อไฟล์: <strong>" + decodeURIComponent((location.pathname.split("/").pop() || "SmartGift-Catalog-Offline.html")) + "</strong></p>" +
      "<p style='margin-top:8px;color:#8a7a6c'>เวอร์ชัน " + DATA.catalog_version + " · snapshot " + DATA.snapshot_sha256.substring(0, 12) + "…</p>");
  });

  document.addEventListener("keydown", function(e){
    if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
    if (e.key === "ArrowRight" || e.key === "PageDown") next();
    else if (e.key === "ArrowLeft" || e.key === "PageUp") prev();
    else if (e.key === "Home") show(0, "prev");
    else if (e.key === "End") show(total - 1, "next");
    else if (e.key === "Escape"){ closeOverlay(); results.style.display = "none"; }
  });

  show(0, "init");
})();
"""

    toolbar = """
  <div id="toolbar">
    <span class="brand"><b>SG</b> SmartGift</span>
    <button id="btn-toc" type="button" title="สารบัญ">☰ สารบัญ</button>
    <button id="btn-first" type="button" title="หน้าแรก">⏮</button>
    <span id="page-counter"><span id="page-num">1</span>/<span id="page-total">1</span></span>
    <input id="page-jump" type="number" min="1" value="1" aria-label="ไปหน้าที่">
    <button id="btn-last" type="button" title="หน้าสุดท้าย">⏭</button>
    <button id="btn-thumbs" type="button" aria-pressed="false" title="Thumbnails">🗂</button>
    <input id="search-box" type="search" placeholder="ค้นหาในเล่ม…" aria-label="ค้นหาในเล่ม">
    <button id="btn-zoom-out" type="button" title="ซูมออก">−</button>
    <button id="btn-zoom-in" type="button" title="ซูมเข้า">＋</button>
    <button id="btn-zoom-fit" type="button" title="พอดีจอ">Fit</button>
    <button id="btn-auto" type="button" aria-pressed="false" title="Auto Flip">▶ Auto</button>
    <select id="auto-speed" aria-label="ความเร็ว Auto Flip">
      <option value="6000">ช้า</option><option value="4000" selected>ปกติ</option><option value="2500">เร็ว</option>
    </select>
    <button id="btn-detail" type="button" title="ดูสินค้าในหน้านี้">🛍 สินค้าในหน้านี้</button>
    <button id="btn-share" type="button" title="แชร์ไฟล์">📤 แชร์ไฟล์</button>
    <button id="btn-full" type="button" title="เต็มจอ">⛶</button>
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SmartGift Offline Catalog {esc(data["catalog_version"])}</title>
<style>{css}</style>
</head>
<body>
{toolbar}
<div id="search-results"></div>
<div id="thumb-rail" aria-label="Thumbnails"></div>
<button id="prev-arrow" class="nav-arrow" type="button" aria-label="หน้าก่อนหน้า">‹</button>
<button id="next-arrow" class="nav-arrow" type="button" aria-label="หน้าถัดไป">›</button>
<div id="book-wrap"><div id="book">{sections}</div></div>
<div id="overlay" role="dialog" aria-modal="true">
  <div class="sheet">
    <div class="close-row"><button id="overlay-close" type="button">ปิด</button></div>
    <div id="overlay-body"></div>
  </div>
</div>
<script id="catalog-data" type="application/json">{payload_json}</script>
<script>{js}</script>
</body>
</html>"""


def render_print_html(data, pages):
    body = "".join(
        f'<section class="p-page">{html}</section>' for _, html in pages
    )
    return f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="utf-8">
<title>SmartGift Offline Catalog {esc(data["catalog_version"])} — print proof</title>
<style>
{FONT_CSS_PLACEHOLDER}
@page{{size:A4 landscape;margin:10mm}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:"Sarabun","Leelawadee UI","Segoe UI",Tahoma,"Noto Sans Thai",sans-serif;color:#2C241F;background:#fff}}
.p-page{{page-break-after:always;padding:6mm;min-height:180mm}}
{RENDER_SHARED_PRINT_CSS}
</style></head><body>{body}</body></html>"""


RENDER_SHARED_PRINT_CSS = """
.eyebrow{color:#FC5900;font-weight:800;font-size:10px;letter-spacing:.08em;text-transform:uppercase}
.page-head h2{font-size:20px;margin:2px 0 4px}
.page-head p{color:#8a7a6c;font-size:11px}
.cover{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:8px;min-height:170mm}
.cover-brand{font-weight:900;color:#675443}
.logo-sg{background:#FC5900;color:#fff;border-radius:8px;padding:3px 7px;font-weight:900}
.cover-hero{max-width:45%;max-height:70mm;object-fit:contain;border-radius:8px}
.cover h1{font-size:26px}
.cover-sub{color:#7c6a5b;font-size:12px}
.cover-meta,.cover-disclaimer{font-size:9.5px;color:#9c8a79}
.toc{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0}
.toc-item{display:flex;justify-content:space-between;padding:8px 12px;border:1px solid #eadfd2;border-radius:8px;font-size:11px;font-weight:700}
.toc-page{color:#FC5900}
.prod-grid,.set-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:8px}
.prod-card,.set-card{border:1px solid #eee1d3;border-radius:8px;padding:8px;font-size:10px;page-break-inside:avoid}
.ph-img{width:100%;height:70px;object-fit:contain}
.no-media{display:flex;align-items:center;justify-content:center;background:#f4ece2;color:#9c8a79;font-size:9px}
.prod-card h4,.set-card h4{font-size:10.5px;margin:3px 0}
.code-line{font-size:9px;color:#8a7a6c;font-weight:700}
.tier{color:#D6A641;font-weight:800}
.ladder-line,.src-line{font-size:8.5px;color:#7c6a5b}
.mini-ladder{width:100%;border-collapse:collapse;font-size:8.5px}
.mini-ladder th,.mini-ladder td{border-top:1px solid #f0e6d8;padding:2px 3px;text-align:left}
.ask{color:#FC5900;font-weight:800;font-size:10px}
.pkg-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px}
.pkg-card{border:1px solid #eee1d3;border-radius:8px;padding:10px;font-size:10px;page-break-inside:avoid}
.pkg-head{display:flex;justify-content:space-between;gap:8px}
.pkg-head h3{font-size:12px}
.badge{border:1px solid #D6A641;color:#675443;border-radius:999px;padding:2px 8px;font-size:8.5px;font-weight:800;white-space:nowrap}
.pkg-copy{color:#6f5f51;margin:4px 0}
.pkg-facts{display:grid;grid-template-columns:1fr 1fr;gap:4px}
.pkg-facts span{color:#9c8a79;display:block}
.pills{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}
.pill{border:1px solid #f4d9c2;color:#675443;border-radius:999px;padding:1px 7px;font-size:8.5px;font-weight:700}
"""


def scan_offline_html(html_text):
    violations = []
    # Base64 image payloads are random data and can contain any letter
    # sequence — scan only the human-readable parts of the document.
    import re
    low = re.sub(r"data:(?:image|font)/[a-z0-9+-]+;base64,[A-Za-z0-9+/=]+", "", html_text).lower()
    for marker in FORBIDDEN_MARKERS:
        if marker in low:
            violations.append(f"forbidden marker: '{marker}'")
    probe = low
    for ns in ALLOWED_HTTP_NS:
        probe = probe.replace(ns, "")
    for needle in ("http://", "https://", "fetch(", "xmlhttprequest", "navigator.sendbeacon", "websocket", "@import", "<link"):
        if needle in probe:
            violations.append(f"external/network reference: '{needle}'")
    return violations


def main():
    print("🔨 Building SmartGift offline customer catalog…")
    os.makedirs(OUT_DIR, exist_ok=True)
    data = build_dataset()
    pages = render_pages(data)
    version = data["catalog_version"]
    base = f"SmartGift-Catalog-Offline-{version}"

    html = render_flipbook(data, pages)
    font_css = build_font_css(html)
    html = html.replace(FONT_CSS_PLACEHOLDER, font_css, 1)
    if font_css:
        print(f"🔤 Sarabun subset embedded ({len(font_css)/1024:.0f} KB CSS, weights 400/700)")
    else:
        print("⚠️ Sarabun assets not found — shipping with system Thai font stack only")
    violations = scan_offline_html(html)
    if violations:
        for v in violations:
            print(f"⛔ OFFLINE BOUNDARY VIOLATION: {v}")
        raise SystemExit(1)
    html_bytes = html.encode("utf-8")
    if len(html_bytes) > SIZE_BUDGET_BYTES:
        print(f"⛔ SIZE BUDGET EXCEEDED: {len(html_bytes)/1e6:.1f} MB > 25 MB")
        raise SystemExit(1)

    html_path = os.path.join(OUT_DIR, base + ".html")
    with open(html_path, "wb") as f:
        f.write(html_bytes)
    print(f"✅ {html_path} ({len(html_bytes)/1e6:.2f} MB, {len(pages)} pages)")

    print_path = os.path.join(OUT_DIR, "_print_proof.html")
    with open(print_path, "w", encoding="utf-8") as f:
        f.write(render_print_html(data, pages).replace(FONT_CSS_PLACEHOLDER, font_css, 1))
    pdf_path = os.path.join(OUT_DIR, base + ".pdf")
    pdf_ok = False
    if os.path.exists(CHROME):
        result = subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
             f"--print-to-pdf={os.path.abspath(pdf_path)}", os.path.abspath(print_path)],
            capture_output=True, timeout=180,
        )
        pdf_ok = result.returncode == 0 and os.path.exists(pdf_path)
    if pdf_ok:
        print(f"✅ {pdf_path} ({os.path.getsize(pdf_path)/1e6:.2f} MB)")
    else:
        print("⚠️ PDF proof not generated (Chrome unavailable or failed) — ZIP will ship without it")
    os.remove(print_path)

    readme = f"""SmartGift Offline Customer Catalog — วิธีเปิดใช้งาน
====================================================

1) ดับเบิลคลิกไฟล์ {base}.html เพื่อเปิดใน Chrome หรือ Edge
   - ไม่ต้องต่ออินเทอร์เน็ต ข้อมูลและรูปทั้งหมดอยู่ในไฟล์เดียว
2) ปุ่มบนแถบเครื่องมือ: สารบัญ · เปลี่ยนหน้า/ไปหน้าที่ต้องการ · Thumbnails ·
   ค้นหาในเล่ม · ซูม/Fit · Auto Flip · สินค้าในหน้านี้ · แชร์ไฟล์ · เต็มจอ
   คีย์บอร์ด: ลูกศรซ้าย/ขวา เปลี่ยนหน้า, Home/End, Esc ปิดหน้าต่างย่อย
3) {base}.pdf ใช้สำหรับพิมพ์หรือเปิดในเครื่องที่ไม่มีเบราว์เซอร์

เวอร์ชัน: {version}
Snapshot: {data['snapshot_sha256'][:16]}…
เอกสารนี้เป็น customer catalog snapshot สำหรับอ้างอิงสินค้า
ราคาสุทธิยืนยันผ่านใบเสนอราคาจากทีมขาย SmartGift เท่านั้น
{data['operating_entity']}
"""
    zip_path = os.path.join(OUT_DIR, base + ".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(html_path, base + ".html")
        if pdf_ok:
            z.write(pdf_path, base + ".pdf")
        z.writestr("README-เปิดใช้งาน.txt", readme)
    print(f"✅ {zip_path} ({os.path.getsize(zip_path)/1e6:.2f} MB)")

    manifest = load(PUBLIC_MANIFEST)
    audit = {
        "artifact": "offline_customer_catalog",
        "catalog_version": version,
        "snapshot_sha256": data["snapshot_sha256"],
        "generated_at": data["generated_at"],
        "pages": len(pages),
        "embedded_images": len(data["images"]),
        "size_bytes": {"html": len(html_bytes),
                       "pdf": os.path.getsize(pdf_path) if pdf_ok else None,
                       "zip": os.path.getsize(zip_path)},
        "size_budget_bytes": SIZE_BUDGET_BYTES,
        "font_strategy": ("embedded Sarabun OFL subset (woff, weights 400/700) + system Thai fallback stack"
                          if font_css else "system Thai font stack (Sarabun assets missing)"),
        "sources": {
            "pricelist_public": manifest["data_integrity_hashes"]["pricelist_public"],
            "catalog_media": manifest["data_integrity_hashes"]["catalog_media"],
        },
        "boundary_scan": "passed (forbidden markers + external references)",
        "deliverables": [os.path.basename(p) for p in (html_path, pdf_path, zip_path) if os.path.exists(p)],
        "sha256": {
            os.path.basename(p): hashlib.sha256(open(p, "rb").read()).hexdigest()
            for p in (html_path, pdf_path, zip_path) if os.path.exists(p)
        },
    }
    with open(AUDIT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    print(f"✅ audit manifest → {AUDIT_MANIFEST}")
    print("🛡️ boundary scan passed · size within 25 MB budget")


if __name__ == "__main__":
    main()
