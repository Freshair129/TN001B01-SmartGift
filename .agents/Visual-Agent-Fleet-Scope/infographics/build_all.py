# -*- coding: utf-8 -*-
"""
Build all 30 ZURI infographics and generate gallery.
"""

import os
import sys
import time
import subprocess

# Ensure UTF-8
sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

from generator_base import render_html_page
from infographics_data import DOCUMENTS

OUTPUT_DIR = CURRENT_DIR
HTML_DIR = os.path.join(OUTPUT_DIR, "html")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(HTML_DIR, exist_ok=True)

print(f"==================================================")
print(f"🚀 Starting ZURI Infographic Generation Pipeline")
print(f"📁 Target documents: {len(DOCUMENTS)}")
print(f"🎨 Design System: Zuri Heritage v2 (Amber Citrus)")
print(f"==================================================")

rendered_images = []

for idx, doc in enumerate(DOCUMENTS, 1):
    out_name = f"{idx:02d}_{doc['output_name']}"
    html_path = os.path.join(HTML_DIR, f"{out_name}.html")
    png_path = os.path.join(OUTPUT_DIR, f"{out_name}.png")
    
    # 1. Generate HTML
    html_content = render_html_page(doc)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # 2. Render PNG via Headless Chrome
    file_url = "file:///" + html_path.replace("\\", "/")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--window-size=1200,1200",
        f"--screenshot={png_path}",
        file_url
    ]
    
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    
    file_size = os.path.getsize(png_path) if os.path.exists(png_path) else 0
    file_size_kb = file_size / 1024
    
    if os.path.exists(png_path) and file_size > 50000:
        print(f"[{idx:02d}/30] ✅ Rendered: {out_name}.png ({file_size_kb:.1f} KB) in {dt:.2f}s")
        rendered_images.append({
            "idx": idx,
            "filename": f"{out_name}.png",
            "html_filename": f"html/{out_name}.html",
            "title": doc["title_plain"],
            "tag": doc["tag"],
            "source": doc["file_rel"],
            "size_kb": f"{file_size_kb:.1f} KB"
        })
    else:
        print(f"[{idx:02d}/30] ❌ FAILED: {out_name}.png - Error: {res.stderr}")

print(f"\n✨ Rendered {len(rendered_images)} / {len(DOCUMENTS)} images successfully!")

# Generate Gallery index.html
gallery_cards_html = []
for item in rendered_images:
    gallery_cards_html.append(f"""
    <div class="gallery-card" data-title="{item['title'].lower()}" data-tag="{item['tag'].lower()}">
      <div class="card-img-wrapper" onclick="openModal('{item['filename']}', '{item['title']}')">
        <img src="{item['filename']}" alt="{item['title']}" loading="lazy" />
        <div class="img-overlay">🔍 คลิกดูภาพขนาดเต็ม</div>
      </div>
      <div class="card-body">
        <div class="card-tag">{item['tag']}</div>
        <h3 class="card-title">{item['idx']:02d}. {item['title']}</h3>
        <div class="card-meta">
          <span>📄 {item['source']}</span>
          <span>💾 {item['size_kb']}</span>
        </div>
        <div class="card-actions">
          <a href="{item['filename']}" download="{item['filename']}" class="btn-download">⬇️ ดาวน์โหลด PNG</a>
          <a href="{item['html_filename']}" target="_blank" class="btn-view-html">🌐 ดู HTML</a>
        </div>
      </div>
    </div>
    """)

gallery_html = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZURI Fleet Scope Infographics Gallery (30 Cheat-Sheets)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700;800&family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --brand-amber: #E8820C;
  --brand-amber-dark: #B86A08;
  --brand-amber-light: #FFF8F0;
  --slate-900: #111827;
  --slate-800: #1F2937;
  --slate-700: #374151;
  --slate-100: #F3F4F6;
  --slate-50: #F8FAFC;
  --border-color: #E2E8F0;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'Prompt', 'IBM Plex Sans Thai', sans-serif;
  background-color: #F8FAFC;
  color: var(--slate-900);
  padding: 32px 24px;
}}

.container {{
  max-width: 1400px;
  margin: 0 auto;
}}

/* Top Hero */
.hero {{
  background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
  color: #FFFFFF;
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 36px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  border: 1px solid #374151;
}}

.hero-left h1 {{
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 8px;
}}
.hero-left h1 span {{
  color: var(--brand-amber);
}}
.hero-left p {{
  font-size: 16px;
  color: #9CA3AF;
  max-width: 650px;
  line-height: 1.6;
}}

.hero-stats {{
  display: flex;
  gap: 20px;
}}
.stat-box {{
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 14px;
  padding: 18px 24px;
  text-align: center;
}}
.stat-number {{
  font-size: 32px;
  font-weight: 800;
  color: var(--brand-amber);
}}
.stat-label {{
  font-size: 13px;
  color: #D1D5DB;
  margin-top: 4px;
}}

/* Search & Filter Bar */
.filter-bar {{
  background: #FFFFFF;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 30px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}}

.search-input {{
  flex: 1;
  font-family: inherit;
  font-size: 15px;
  padding: 10px 16px;
  border: 1.5px solid var(--border-color);
  border-radius: 10px;
  outline: none;
  transition: all 0.2s;
}}
.search-input:focus {{
  border-color: var(--brand-amber);
  box-shadow: 0 0 0 3px rgba(232, 130, 12, 0.15);
}}

/* Grid Gallery */
.gallery-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}}

.gallery-card {{
  background: #FFFFFF;
  border: 1.5px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}}
.gallery-card:hover {{
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08);
  border-color: #CBD5E1;
}}

.card-img-wrapper {{
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  background: #F1F5F9;
  cursor: pointer;
  overflow: hidden;
}}
.card-img-wrapper img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}}
.card-img-wrapper:hover img {{
  transform: scale(1.03);
}}
.img-overlay {{
  position: absolute;
  inset: 0;
  background: rgba(17, 24, 39, 0.4);
  color: #FFFFFF;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 15px;
  font-weight: 700;
  opacity: 0;
  transition: opacity 0.2s;
}}
.card-img-wrapper:hover .img-overlay {{
  opacity: 1;
}}

.card-body {{
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}}

.card-tag {{
  font-size: 12px;
  font-weight: 700;
  color: var(--brand-amber-dark);
  background: var(--brand-amber-light);
  padding: 3px 10px;
  border-radius: 12px;
  align-self: flex-start;
}}

.card-title {{
  font-size: 16px;
  font-weight: 700;
  color: var(--slate-900);
  line-height: 1.35;
}}

.card-meta {{
  font-size: 12px;
  color: #64748B;
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
}}

.card-actions {{
  display: flex;
  gap: 8px;
  margin-top: 10px;
}}
.btn-download, .btn-view-html {{
  flex: 1;
  text-align: center;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 10px;
  border-radius: 8px;
  transition: all 0.2s;
}}
.btn-download {{
  background: var(--slate-900);
  color: #FFFFFF;
}}
.btn-download:hover {{
  background: var(--brand-amber);
}}
.btn-view-html {{
  background: #EFF6FF;
  color: #1D4ED8;
  border: 1px solid #BFDBFE;
}}
.btn-view-html:hover {{
  background: #DBEAFE;
}}

/* Modal Lightbox */
.modal {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.85);
  z-index: 999;
  justify-content: center;
  align-items: center;
  padding: 24px;
}}
.modal.active {{
  display: flex;
}}
.modal-content {{
  max-width: 90vh;
  max-height: 90vh;
  position: relative;
  background: #FFFFFF;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}}
.modal-img {{
  width: 100%;
  height: 100%;
  display: block;
}}
.modal-close {{
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0,0,0,0.6);
  color: #FFFFFF;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}}
</style>
</head>
<body>
<div class="container">
  <!-- Hero -->
  <div class="hero">
    <div class="hero-left">
      <h1>ZURI <span>Infographics</span> Gallery</h1>
      <p>คลังภาพสรุปความรู้ระดับ High-DPI (1200x1200px) สำหรับเอกสารทั้งหมด 30 ไฟล์ ใน Fleet Scope ออกแบบตาม ZURI Heritage Design System เพื่อการเรียนรู้และการส่งมอบงานที่ยอดเยี่ยม</p>
    </div>
    <div class="hero-stats">
      <div class="stat-box">
        <div class="stat-number">30</div>
        <div class="stat-label">ภาพสรุปทั้งหมด</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">100%</div>
        <div class="stat-label">ครอบคลุมทุกไฟล์</div>
      </div>
    </div>
  </div>

  <!-- Filter Bar -->
  <div class="filter-bar">
    <input type="text" class="search-input" id="searchBox" placeholder="🔍 ค้นหาหัวข้อ, หมวดหมู่ หรือชื่อไฟล์ (เช่น AC, Agile, Backlog, UAT, Case Study)..." onkeyup="filterCards()">
  </div>

  <!-- Gallery Grid -->
  <div class="gallery-grid" id="galleryGrid">
    {"".join(gallery_cards_html)}
  </div>
</div>

<!-- Modal -->
<div class="modal" id="imageModal" onclick="closeModal()">
  <div class="modal-content" onclick="event.stopPropagation()">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <img id="modalImg" class="modal-img" src="" alt="Full View">
  </div>
</div>

<script>
function filterCards() {{
  const query = document.getElementById('searchBox').value.toLowerCase();
  const cards = document.querySelectorAll('.gallery-card');
  cards.forEach(card => {{
    const title = card.getAttribute('data-title');
    const tag = card.getAttribute('data-tag');
    if (title.includes(query) || tag.includes(query)) {{
      card.style.display = 'flex';
    }} else {{
      card.style.display = 'none';
    }}
  }});
}}

function openModal(imgSrc, title) {{
  document.getElementById('modalImg').src = imgSrc;
  document.getElementById('imageModal').classList.add('active');
}}

function closeModal() {{
  document.getElementById('imageModal').classList.remove('active');
}}

document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') closeModal();
}});
</script>
</body>
</html>
"""

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(gallery_html)

print(f"🎉 Generated interactive gallery: {os.path.join(OUTPUT_DIR, 'index.html')}")
