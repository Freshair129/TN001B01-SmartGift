# -*- coding: utf-8 -*-
"""
ZURI Infographic Dataset and Generator Script
Generates all 30 infographics in high resolution (1200x1200px) matching the reference sample.
"""

import os
import sys
import json
import subprocess

# Ensure UTF-8
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"C:\Users\pc\workspace\Org-01\.agents\Visual-Agent-Fleet-Scope\infographics"
HTML_DIR = os.path.join(OUTPUT_DIR, "html")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(HTML_DIR, exist_ok=True)

# SVG Icons & Mascot definitions
MASCOT_SVG = '''<svg viewBox="0 0 100 100" width="76" height="76" class="mascot-avatar">
  <circle cx="50" cy="50" r="46" fill="#FFF8F0" stroke="#E8820C" stroke-width="3"/>
  <path d="M22,48 C20,30 35,16 50,16 C65,16 80,30 78,48 C78,48 84,45 84,52 C84,58 78,58 78,58 C78,65 65,78 50,78 C35,78 22,65 22,58 C22,58 16,58 16,52 C16,45 22,48 22,48 Z" fill="#1F2937"/>
  <circle cx="50" cy="50" r="28" fill="#FDDCB5"/>
  <path d="M26,38 C32,24 68,24 74,38 C68,30 56,28 50,28 C44,28 32,30 26,38 Z" fill="#111827"/>
  <rect x="30" y="42" width="16" height="12" rx="4" fill="none" stroke="#1F2937" stroke-width="2.5"/>
  <rect x="54" y="42" width="16" height="12" rx="4" fill="none" stroke="#1F2937" stroke-width="2.5"/>
  <line x1="46" y1="48" x2="54" y2="48" stroke="#1F2937" stroke-width="2.5"/>
  <circle cx="38" cy="48" r="2.5" fill="#111827"/>
  <circle cx="62" cy="48" r="2.5" fill="#111827"/>
  <circle cx="39" cy="47" r="0.8" fill="#FFFFFF"/>
  <circle cx="63" cy="47" r="0.8" fill="#FFFFFF"/>
  <ellipse cx="32" cy="56" rx="4" ry="2" fill="#F87171" opacity="0.6"/>
  <ellipse cx="68" cy="56" rx="4" ry="2" fill="#F87171" opacity="0.6"/>
  <path d="M44,58 Q50,64 56,58" fill="none" stroke="#1F2937" stroke-width="2" stroke-linecap="round"/>
  <path d="M30,76 C36,70 64,70 70,76 L74,92 C62,96 38,96 26,92 Z" fill="#E8820C"/>
  <path d="M46,74 L50,82 L54,74 Z" fill="#FFFFFF"/>
</svg>'''

ICONS = {
    "target": '''<svg class="icon icon-target" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>''',
    "doc": '''<svg class="icon icon-doc" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>''',
    "screen": '''<svg class="icon icon-screen" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>''',
    "check": '''<svg class="icon icon-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>''',
    "alert": '''<svg class="icon icon-alert" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>''',
    "bulb": '''<svg class="icon icon-bulb" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/></svg>''',
    "users": '''<svg class="icon icon-users" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>''',
    "layers": '''<svg class="icon icon-layers" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>''',
    "clock": '''<svg class="icon icon-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>''',
    "shield": '''<svg class="icon icon-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>''',
    "sparkles": '''<svg class="icon icon-sparkles" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>''',
    "link": '''<svg class="icon icon-link" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>''',
    "workflow": '''<svg class="icon icon-workflow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="3" width="6" height="6" rx="1"/><rect x="9" y="15" width="6" height="6" rx="1"/><path d="M6 9v3a3 3 0 0 0 3 3h3m6-6v3a3 3 0 0 1-3 3h-3"/></svg>''',
    "bookmark": '''<svg class="icon icon-bookmark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>'''
}

CSS_TEMPLATE = """
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700;800&family=IBM+Plex+Sans+Thai:wght@400;500;600;700&display=swap');

:root {
  --brand-amber: #E8820C;
  --brand-amber-light: #FFF8F0;
  --brand-amber-border: #FDE8D0;
  --slate-900: #111827;
  --slate-800: #1F2937;
  --slate-700: #374151;
  --slate-600: #4B5563;
  --slate-100: #F3F4F6;
  --slate-50: #F8FAFC;
  --card-border: #E2E8F0;
  --success: #16A34A;
  --blue-600: #1D4ED8;
  --blue-700: #1E40AF;
  --danger: #DC2626;
  --warning: #D97706;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  width: 1200px;
  height: 1200px;
  background-color: #F8FAFC;
  font-family: 'Prompt', 'IBM Plex Sans Thai', -apple-system, sans-serif;
  color: var(--slate-900);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.canvas {
  width: 1200px;
  height: 1200px;
  background: #FFFFFF;
  padding: 30px 36px 26px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  border: 1px solid #E2E8F0;
}

/* Header Area */
.header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 8px;
}

.header-left {
  display: flex;
  gap: 16px;
  align-items: center;
  flex: 1;
}

.header-badge-tag {
  background: var(--slate-900);
  color: #FFFFFF;
  font-size: 14px;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: inline-block;
  margin-bottom: 2px;
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.main-title {
  font-size: 36px;
  font-weight: 800;
  line-height: 1.15;
  color: var(--blue-700);
  letter-spacing: -0.5px;
}
.main-title .highlight {
  color: var(--brand-amber);
}
.main-title .danger-highlight {
  color: var(--danger);
}

.subtitle-pill {
  background: #FDE8D0;
  color: #B86A08;
  font-size: 16px;
  font-weight: 700;
  padding: 3px 16px;
  border-radius: 30px;
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  margin-top: 1px;
}

/* Sticky Note Top-Right */
.sticky-note {
  background: #FEF08A;
  border: 1px solid #FACC15;
  box-shadow: 0 4px 10px rgba(0,0,0,0.06);
  padding: 10px 14px;
  border-radius: 8px;
  transform: rotate(2.5deg);
  max-width: 220px;
  position: relative;
  text-align: center;
  flex-shrink: 0;
}
.sticky-note::before {
  content: "📌";
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 15px;
}
.sticky-note-text {
  font-size: 14px;
  font-weight: 700;
  color: #854D0E;
  line-height: 1.3;
}

/* Golden Equation Bar */
.golden-equation {
  border: 2px dashed #F59E0B;
  background: #FFFBEB;
  border-radius: 10px;
  padding: 6px 16px;
  font-size: 15px;
  font-weight: 600;
  color: #92400E;
  text-align: center;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

/* Main Grid Layout */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: 12px;
  flex: 1;
  margin-bottom: 8px;
}

.card {
  background: #FFFFFF;
  border: 1.5px solid var(--card-border);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.card-header-pill {
  font-size: 15px;
  font-weight: 700;
  color: #FFFFFF;
  padding: 3px 12px;
  border-radius: 20px;
  display: inline-block;
  align-self: flex-start;
  margin-bottom: 8px;
}

.pill-blue { background: #2563EB; }
.pill-green { background: #16A34A; }
.pill-red { background: #DC2626; }
.pill-amber { background: #D97706; }
.pill-purple { background: #7C3AED; }

/* Full Width Card */
.card-full {
  grid-column: span 2;
  background: #FAF5FF;
  border-color: #E9D5FF;
  padding: 10px 14px;
}

/* Items & Lists inside cards */
.list-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13.5px;
  color: var(--slate-800);
  line-height: 1.4;
  margin-bottom: 5px;
}
.list-item:last-child { margin-bottom: 0; }

.bullet-dot {
  width: 6px;
  height: 6px;
  background: var(--blue-600);
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.icon {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
  margin-top: 1px;
}
.icon-target { stroke: #DC2626; }
.icon-doc { stroke: #2563EB; }
.icon-screen { stroke: #0284C7; }
.icon-check { stroke: #16A34A; }
.icon-alert { stroke: #D97706; }
.icon-bulb { stroke: #CA8A04; }
.icon-users { stroke: #7C3AED; }
.icon-sparkles { stroke: #E8820C; }

/* Flow Steps Row */
.flow-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  margin: 4px 0;
}

.flow-step-box {
  background: #FFFFFF;
  border: 1.5px solid #CBD5E1;
  border-radius: 8px;
  padding: 6px 8px;
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
}
.flow-step-title {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--slate-800);
}
.flow-arrow {
  font-size: 16px;
  font-weight: 800;
  color: #94A3B8;
}

.flow-subcaption {
  text-align: center;
  font-size: 12.5px;
  font-weight: 600;
  color: #E11D48;
  margin-top: 3px;
}

/* Alert Warning Box */
.warning-box {
  background: #FFFBEB;
  border: 1px solid #FDE68A;
  border-radius: 8px;
  padding: 6px 10px;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  font-weight: 600;
  color: #B45309;
}

/* Summary Card Big Text */
.summary-content {
  display: flex;
  align-items: center;
  gap: 12px;
}
.summary-icon-wrapper {
  width: 48px;
  height: 48px;
  background: #DCFCE7;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}
.summary-text {
  font-size: 13.5px;
  font-weight: 500;
  line-height: 1.45;
  color: var(--slate-800);
}
.summary-text strong {
  color: var(--slate-900);
  font-weight: 700;
}

/* Memory Anchor Bar */
.memory-bar {
  background: #FFFFFF;
  border: 1.5px solid #FCD34D;
  border-radius: 10px;
  padding: 6px 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.memory-label {
  background: #FEF3C7;
  color: #92400E;
  font-size: 14px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.memory-flow {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 700;
  color: var(--slate-800);
}
.memory-pill {
  background: #F1F5F9;
  border: 1px solid #CBD5E1;
  padding: 2px 10px;
  border-radius: 16px;
}
.memory-arrow { color: #E8820C; font-weight: 800; }

/* Bottom Footer Banner */
.footer-banner {
  background: var(--slate-900);
  border-radius: 12px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #FFFFFF;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}
.footer-mascot {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #374151;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}
.footer-brand-title {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.5px;
  color: #FFFFFF;
  display: flex;
  align-items: center;
  gap: 5px;
}
.footer-brand-title .zuri-accent {
  color: var(--brand-amber);
}
.footer-brand-sub {
  font-size: 11.5px;
  color: #9CA3AF;
  font-weight: 400;
}

.footer-save-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13.5px;
  font-weight: 600;
  color: #E2E8F0;
}

.footer-follow-btn {
  background: #F59E0B;
  color: #78350F;
  font-size: 13.5px;
  font-weight: 700;
  padding: 5px 14px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 5px;
}
"""

def render_html_page(doc_data):
    c = doc_data
    
    # Card 1
    c1_items = "".join([f'<div class="list-item"><span class="bullet-dot"></span><span>{item}</span></div>' for item in c["card1_items"]])
    
    # Card 2
    c2_items = "".join([f'<div class="list-item">{ICONS.get(item.get("icon", "doc"), ICONS["doc"])}<span><strong>{item["title"]}</strong> {item.get("desc", "")}</span></div>' for item in c["card2_items"]])
    c2_footer = f'<div style="margin-top:6px; font-size:11.5px; font-weight:600; color:#16A34A; background:#DCFCE7; padding:2px 8px; border-radius:6px; text-align:center;">{c["card2_footer"]}</div>' if c.get("card2_footer") else ""
    
    # Card 3 (Workflow / Flow)
    flow_steps = []
    for i, step in enumerate(c["flow_steps"]):
        flow_steps.append(f'''<div class="flow-step-box">
          <div class="flow-step-title">{step["title"]}</div>
          {ICONS.get(step.get("icon", "doc"), ICONS["doc"])}
        </div>''')
        if i < len(c["flow_steps"]) - 1:
            flow_steps.append('<div class="flow-arrow">➔</div>')
    flow_steps_html = "".join(flow_steps)
    
    # Card 4
    c4_items = "".join([f'<div class="list-item">{ICONS["check"]}<span>{item}</span></div>' for item in c["card4_items"]])
    c4_warning = f'<div class="warning-box">{ICONS["alert"]}<span>{c["card4_warning"]}</span></div>' if c.get("card4_warning") else ""
    
    # Card 5
    c5_summary = f'''<div class="summary-content">
      <div class="summary-icon-wrapper">{ICONS.get(c.get("card5_icon", "link"), ICONS["link"])}</div>
      <div class="summary-text">{c["card5_text"]}</div>
    </div>'''
    
    # Memory Flow
    mem_pills = []
    for i, p in enumerate(c["memory_pills"]):
        mem_pills.append(f'<span class="memory-pill">{p}</span>')
        if i < len(c["memory_pills"]) - 1:
            mem_pills.append('<span class="memory-arrow">➔</span>')
    mem_flow_html = "".join(mem_pills)
    
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{c['title_plain']} - ZURI Infographic</title>
<style>
{CSS_TEMPLATE}
</style>
</head>
<body>
<div class="canvas">
  <!-- Header Area -->
  <div class="header-wrapper">
    <div class="header-left">
      {MASCOT_SVG}
      <div class="header-text-group">
        <div class="header-badge-tag">{c['tag']}</div>
        <div class="main-title">{c['title_html']}</div>
        <div class="subtitle-pill">{c['subtitle']}</div>
      </div>
    </div>
    <div class="sticky-note">
      <div class="sticky-note-text">{c['sticky_text']}</div>
    </div>
  </div>

  <!-- Golden Equation Bar -->
  <div class="golden-equation">
    <span>{c['equation']}</span>
  </div>

  <!-- Main Content Grid -->
  <div class="main-grid">
    <!-- Card 1 -->
    <div class="card">
      <div class="card-header-pill pill-blue">{c['card1_title']}</div>
      <div style="font-size: 13.5px; font-weight:600; color:#1E40AF; margin-bottom:6px;">{c['card1_subtitle']}</div>
      {c1_items}
    </div>

    <!-- Card 2 -->
    <div class="card">
      <div class="card-header-pill pill-green">{c['card2_title']}</div>
      <div style="display:flex; flex-direction:column; gap:3px;">
        {c2_items}
      </div>
      {c2_footer}
    </div>

    <!-- Card 3: Full Width Workflow -->
    <div class="card card-full">
      <div class="card-header-pill pill-red">{c['card3_title']}</div>
      <div class="flow-row">
        {flow_steps_html}
      </div>
      <div class="flow-subcaption">{c['card3_subcaption']}</div>
    </div>

    <!-- Card 4 -->
    <div class="card">
      <div class="card-header-pill pill-blue">{c['card4_title']}</div>
      <div style="display:flex; flex-direction:column; gap:3px;">
        {c4_items}
      </div>
      {c4_warning}
    </div>

    <!-- Card 5 -->
    <div class="card">
      <div class="card-header-pill pill-purple">{c['card5_title']}</div>
      {c5_summary}
    </div>
  </div>

  <!-- Memory Anchor Bar -->
  <div class="memory-bar">
    <div class="memory-label">{ICONS['bulb']} จำง่าย ๆ:</div>
    <div class="memory-flow">
      {mem_flow_html}
    </div>
  </div>

  <!-- Footer Banner -->
  <div class="footer-banner">
    <div class="footer-brand">
      <div class="footer-mascot">{MASCOT_SVG}</div>
      <div>
        <div class="footer-brand-title">ZURI <span class="zuri-accent">ACADEMY</span></div>
        <div class="footer-brand-sub">AI-Native Business OS | ความรู้ PM / BA / PO / Dev ฉบับใช้งานจริง</div>
      </div>
    </div>
    <div class="footer-save-btn">
      {ICONS['bookmark']}
      <span>Save ไว้ก่อนน้า ไม่พลาดความรู้ดี ๆ</span>
    </div>
    <div class="footer-follow-btn">
      {ICONS['sparkles']}
      <span>Follow ไว้น้า ✨ สรุปให้จบในแผ่นเดียว!</span>
    </div>
  </div>
</div>
</body>
</html>
"""
    return html
