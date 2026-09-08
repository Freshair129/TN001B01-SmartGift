# -*- coding: utf-8 -*-
"""
High-Grade Infographic Engine with Full Illustrated Elements:
- Tree hierarchy lines & junction dots
- Circular process loop with curved SVG arrows & central target
- X/T/I skill diagrams
- Notebook lined texture & binder spiral
- Pastel column fills with rich avatars & icons
- Authentic hand-drawn style typography (Mali + Kanit + Prompt)
"""

import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT_HTML = r"C:\Users\pc\workspace\Org-01\.agents\Visual-Agent-Fleet-Scope\infographics\test_highgrade.html"
OUT_PNG = r"C:\Users\pc\workspace\Org-01\.agents\Visual-Agent-Fleet-Scope\infographics\test_highgrade.png"

# ================= RICH SVG CHARACTERS =================
CHAR_PRESENTER = '''<svg viewBox="0 0 100 110" width="75" height="85">
  <!-- Body / Suit -->
  <path d="M26,62 C32,54 68,54 74,62 L82,105 L18,105 Z" fill="#1D4ED8"/>
  <path d="M42,60 L50,72 L58,60 Z" fill="#FFFFFF"/>
  <path d="M48,72 L52,72 L54,96 L50,100 L46,96 Z" fill="#DC2626"/>
  <!-- Pointing Arm Left -->
  <path d="M26,65 L10,50 L6,54 L20,74 Z" fill="#1D4ED8"/>
  <circle cx="8" cy="52" r="5" fill="#FDDCB5"/>
  <line x1="8" y1="52" x2="2" y2="40" stroke="#1E293B" stroke-width="2.5" stroke-linecap="round"/>
  <!-- Head & Face -->
  <circle cx="50" cy="38" r="25" fill="#FDDCB5"/>
  <path d="M24,36 C24,18 36,10 50,10 C64,10 76,18 76,36 C76,26 68,20 50,20 C32,20 24,26 24,36 Z" fill="#0F172A"/>
  <!-- Glasses -->
  <rect x="33" y="32" width="14" height="10" rx="3" fill="none" stroke="#0F172A" stroke-width="2.2"/>
  <rect x="53" y="32" width="14" height="10" rx="3" fill="none" stroke="#0F172A" stroke-width="2.2"/>
  <line x1="47" y1="36" x2="53" y2="36" stroke="#0F172A" stroke-width="2.2"/>
  <circle cx="40" cy="37" r="2.2" fill="#0F172A"/><circle cx="60" cy="37" r="2.2" fill="#0F172A"/>
  <circle cx="41" cy="36" r="0.8" fill="#FFFFFF"/><circle cx="61" cy="36" r="0.8" fill="#FFFFFF"/>
  <ellipse cx="32" cy="44" rx="4" ry="2" fill="#F87171" opacity="0.6"/>
  <ellipse cx="68" cy="44" rx="4" ry="2" fill="#F87171" opacity="0.6"/>
  <path d="M44,46 Q50,52 56,46" fill="none" stroke="#991B1B" stroke-width="2" stroke-linecap="round"/>
</svg>'''

CHAR_BA = '''<svg viewBox="0 0 80 90" width="60" height="68">
  <path d="M20,54 C26,48 54,48 60,54 L66,88 L14,88 Z" fill="#DC2626"/>
  <path d="M34,52 L40,64 L46,52 Z" fill="#FFFFFF"/>
  <circle cx="40" cy="34" r="22" fill="#FDDCB5"/>
  <path d="M18,32 C18,14 30,8 40,8 C50,8 62,14 62,32 C62,24 55,16 40,16 C25,16 18,24 18,32 Z" fill="#1E293B"/>
  <circle cx="32" cy="33" r="2" fill="#0F172A"/><circle cx="48" cy="33" r="2" fill="#0F172A"/>
  <path d="M36,41 Q40,45 44,41" fill="none" stroke="#0F172A" stroke-width="1.8" stroke-linecap="round"/>
  <!-- Holding Magnifier -->
  <circle cx="60" cy="62" r="7" fill="none" stroke="#F59E0B" stroke-width="2.5"/>
  <line x1="65" y1="67" x2="72" y2="76" stroke="#78350F" stroke-width="3" stroke-linecap="round"/>
</svg>'''

CHAR_PO = '''<svg viewBox="0 0 80 90" width="60" height="68">
  <path d="M16,36 C16,14 28,8 40,8 C52,8 64,14 64,36 C64,50 68,64 62,72 C58,60 60,44 60,36 C60,18 52,14 40,14 C28,14 20,18 20,36 C20,44 22,60 18,72 C12,64 16,50 16,36 Z" fill="#9A3412"/>
  <circle cx="40" cy="34" r="22" fill="#FDDCB5"/>
  <circle cx="31" cy="32" r="2.2" fill="#0F172A"/><circle cx="49" cy="32" r="2.2" fill="#0F172A"/>
  <circle cx="32" cy="31" r="0.8" fill="#FFFFFF"/><circle cx="50" cy="31" r="0.8" fill="#FFFFFF"/>
  <ellipse cx="26" cy="38" rx="3.5" ry="1.8" fill="#F87171" opacity="0.7"/>
  <ellipse cx="54" cy="38" rx="3.5" ry="1.8" fill="#F87171" opacity="0.7"/>
  <path d="M35,42 Q40,47 45,42" fill="none" stroke="#991B1B" stroke-width="2" stroke-linecap="round"/>
  <path d="M22,54 C26,48 54,48 58,54 L64,88 L16,88 Z" fill="#EA580C"/>
  <path d="M32,52 L40,64 L48,52 Z" fill="#FFFFFF"/>
</svg>'''

CHAR_FLOW = '''<svg viewBox="0 0 80 90" width="60" height="68">
  <path d="M20,54 C24,48 56,48 60,54 L66,88 L14,88 Z" fill="#CA8A04"/>
  <circle cx="40" cy="34" r="22" fill="#FDDCB5"/>
  <path d="M18,30 C16,12 32,8 40,8 C48,8 64,12 62,30 C64,20 54,14 40,14 C26,14 16,20 18,30 Z" fill="#18181B"/>
  <circle cx="32" cy="33" r="2" fill="#0F172A"/><circle cx="48" cy="33" r="2" fill="#0F172A"/>
  <path d="M36,41 Q40,45 44,41" fill="none" stroke="#0F172A" stroke-width="1.8" stroke-linecap="round"/>
  <!-- Whiteboard Marker in Hand -->
  <rect x="56" y="58" width="6" height="18" rx="2" fill="#2563EB" transform="rotate(25 56 58)"/>
</svg>'''

CHAR_DESIGNER = '''<svg viewBox="0 0 80 90" width="60" height="68">
  <ellipse cx="40" cy="18" rx="26" ry="10" fill="#E11D48"/>
  <circle cx="40" cy="10" r="3" fill="#BE123C"/>
  <circle cx="40" cy="34" r="22" fill="#FDDCB5"/>
  <circle cx="31" cy="33" r="2.2" fill="#0F172A"/><circle cx="49" cy="33" r="2.2" fill="#0F172A"/>
  <path d="M35,42 Q40,46 45,42" fill="none" stroke="#0F172A" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M22,54 C26,48 54,48 58,54 L64,88 L16,88 Z" fill="#0891B2"/>
  <!-- Tablet -->
  <rect x="48" y="60" width="22" height="16" rx="2" fill="#1E293B"/>
  <rect x="50" y="62" width="18" height="12" rx="1" fill="#67E8F9"/>
</svg>'''

CHAR_DEV = '''<svg viewBox="0 0 80 90" width="60" height="68">
  <!-- Headset -->
  <path d="M18,34 C16,20 64,20 62,34" fill="none" stroke="#2563EB" stroke-width="3.5"/>
  <rect x="15" y="30" width="6" height="12" rx="2" fill="#2563EB"/>
  <rect x="59" y="30" width="6" height="12" rx="2" fill="#2563EB"/>
  <path d="M20,40 Q28,48 36,44" fill="none" stroke="#2563EB" stroke-width="2"/>
  <circle cx="36" cy="44" r="2" fill="#2563EB"/>
  <circle cx="40" cy="34" r="22" fill="#FDDCB5"/>
  <path d="M18,30 C16,12 32,8 40,8 C48,8 64,12 62,30 C64,20 54,14 40,14 C26,14 16,20 18,30 Z" fill="#18181B"/>
  <circle cx="31" cy="33" r="2" fill="#0F172A"/><circle cx="49" cy="33" r="2" fill="#0F172A"/>
  <path d="M35,42 Q40,46 45,42" fill="none" stroke="#0F172A" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M20,54 C24,48 56,48 60,54 L64,88 L16,88 Z" fill="#2563EB"/>
  <path d="M32,54 Q40,66 48,54" fill="none" stroke="#DBEAFE" stroke-width="2"/>
</svg>'''

CHAR_QA = '''<svg viewBox="0 0 80 90" width="60" height="68">
  <path d="M16,36 C16,14 26,8 40,8 C54,8 64,14 64,36 C64,48 62,54 58,56 C58,38 56,16 40,16 C24,16 22,38 22,56 C18,54 16,48 16,36 Z" fill="#6B21A8"/>
  <circle cx="40" cy="34" r="22" fill="#FDDCB5"/>
  <circle cx="31" cy="33" r="2.2" fill="#0F172A"/><circle cx="49" cy="33" r="2.2" fill="#0F172A"/>
  <ellipse cx="26" cy="38" rx="3" ry="1.5" fill="#F472B6" opacity="0.8"/>
  <ellipse cx="54" cy="38" rx="3" ry="1.5" fill="#F472B6" opacity="0.8"/>
  <path d="M36,42 Q40,46 44,42" fill="none" stroke="#831843" stroke-width="1.8" stroke-linecap="round"/>
  <path d="M22,54 C26,48 54,48 58,54 L62,88 L18,88 Z" fill="#7C3AED"/>
  <!-- Checkmark Shield -->
  <path d="M52,60 L62,56 L72,60 L72,70 C72,76 62,82 62,82 C62,82 52,76 52,70 Z" fill="#16A34A"/>
  <path d="M57,68 L61,72 L67,64" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
</svg>'''

# ================= CIRCULAR PROCESS LOOP SVG =================
CIRCULAR_LOOP_SVG = '''<svg viewBox="0 0 320 220" width="100%" height="180">
  <!-- Center Target -->
  <circle cx="160" cy="110" r="32" fill="#FEF3C7" stroke="#F59E0B" stroke-width="2"/>
  <text x="160" y="106" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="11" font-weight="800" fill="#92400E">เป้าหมายธุรกิจ</text>
  <text x="160" y="120" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="10" font-weight="700" fill="#B45309">&amp; คุณค่าผู้ใช้</text>
  
  <!-- Step 1 (Top Left): Need & Insight -->
  <rect x="8" y="12" width="120" height="42" rx="8" fill="#EFF6FF" stroke="#1D4ED8" stroke-width="2"/>
  <text x="68" y="30" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="11.5" font-weight="800" fill="#1E40AF">1. NEED &amp; INSIGHT</text>
  <text x="68" y="44" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="10" font-weight="600" fill="#3B82F6">🔍 หา Pain Point / โอกาส</text>
  
  <!-- Step 2 (Top Right): Strategy & Story -->
  <rect x="192" y="12" width="120" height="42" rx="8" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
  <text x="252" y="30" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="11.5" font-weight="800" fill="#991B1B">2. STORY &amp; FLOW</text>
  <text x="252" y="44" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="10" font-weight="600" fill="#EF4444">📋 วาง Scope / User Story</text>
  
  <!-- Step 3 (Bottom Right): Build & Test -->
  <rect x="192" y="160" width="120" height="42" rx="8" fill="#FAF5FF" stroke="#7C3AED" stroke-width="2"/>
  <text x="252" y="178" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="11.5" font-weight="800" fill="#6B21A8">3. AC &amp; BUILD</text>
  <text x="252" y="192" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="10" font-weight="600" fill="#A855F7">💻 โค้ดตรงตาม Spec / AC</text>
  
  <!-- Step 4 (Bottom Left): UAT & Release -->
  <rect x="8" y="160" width="120" height="42" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>
  <text x="68" y="178" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="11.5" font-weight="800" fill="#15803D">4. UAT &amp; RELEASE</text>
  <text x="68" y="192" text-anchor="middle" font-family="'Prompt', sans-serif" font-size="10" font-weight="600" fill="#22C55E">🚀 ส่งมอบ / ตรวจรับงาน</text>

  <!-- Curved Connector Arrows -->
  <!-- Top: 1 -> 2 -->
  <path d="M 130 33 L 182 33" fill="none" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="4 2"/>
  <polygon points="186,33 178,29 178,37" fill="#1E293B"/>

  <!-- Right: 2 -> 3 -->
  <path d="M 252 56 L 252 150" fill="none" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="4 2"/>
  <polygon points="252,154 248,146 256,146" fill="#1E293B"/>

  <!-- Bottom: 3 -> 4 -->
  <path d="M 190 181 L 138 181" fill="none" stroke="#1E293B" stroke-width="2.5" stroke-dasharray="4 2"/>
  <polygon points="134,181 142,177 142,185" fill="#1E293B"/>

  <!-- Left: 4 -> 1 (Continuous Loop) -->
  <path d="M 68 158 L 68 64" fill="none" stroke="#16A34A" stroke-width="2.5" stroke-dasharray="4 2"/>
  <polygon points="68,60 64,68 72,68" fill="#16A34A"/>
</svg>'''

# ================= SKILL DIAGRAMS SVG =================
SKILL_X_SVG = '''<svg viewBox="0 0 40 40" width="36" height="36">
  <line x1="8" y1="8" x2="32" y2="32" stroke="#1D4ED8" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="32" y1="8" x2="8" y2="32" stroke="#1D4ED8" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="8" cy="8" r="3.5" fill="#DC2626"/><circle cx="32" cy="8" r="3.5" fill="#F59E0B"/>
  <circle cx="8" cy="32" r="3.5" fill="#16A34A"/><circle cx="32" cy="32" r="3.5" fill="#7C3AED"/>
  <circle cx="20" cy="20" r="4.5" fill="#0F172A"/>
</svg>'''

SKILL_T_SVG = '''<svg viewBox="0 0 40 40" width="36" height="36">
  <rect x="4" y="6" width="32" height="8" rx="2" fill="#0D9488" stroke="#0F172A" stroke-width="1.5"/>
  <rect x="16" y="14" width="8" height="20" rx="2" fill="#0D9488" stroke="#0F172A" stroke-width="1.5"/>
</svg>'''

SKILL_I_SVG = '''<svg viewBox="0 0 40 40" width="36" height="36">
  <rect x="8" y="6" width="24" height="6" rx="2" fill="#7C3AED" stroke="#0F172A" stroke-width="1.5"/>
  <rect x="16" y="12" width="8" height="16" rx="2" fill="#7C3AED" stroke="#0F172A" stroke-width="1.5"/>
  <rect x="8" y="28" width="24" height="6" rx="2" fill="#7C3AED" stroke="#0F172A" stroke-width="1.5"/>
</svg>'''

HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>โครงสร้างเอกสารที่ BA / PO ควรมี - ZURI High-Grade Master Note</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700;800;900&family=Mali:ital,wght@0,500;0,600;0,700;1,600&family=Kanit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  width: 1200px;
  height: 1200px;
  background-color: #E2E8F0;
  font-family: 'Prompt', -apple-system, sans-serif;
  color: #1E293B;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}}

.poster-canvas {{
  width: 1200px;
  height: 1200px;
  background: #FFFDF9;
  border: 3.5px solid #0F172A;
  border-radius: 14px;
  padding: 22px 26px 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  box-shadow: 0 20px 45px rgba(0,0,0,0.12);
}}

/* ================= HEADER SECTION ================= */
.header-row {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  gap: 14px;
}}

/* Taped Post-it Note Top Left */
.taped-note {{
  background: #FEF08A;
  border: 2.5px solid #0F172A;
  box-shadow: 3.5px 4.5px 0px #0F172A;
  padding: 10px 14px;
  border-radius: 4px;
  transform: rotate(-3.5deg);
  width: 185px;
  text-align: center;
  position: relative;
  flex-shrink: 0;
}}
.taped-note::before {{
  content: "";
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 70px;
  height: 20px;
  background: rgba(245, 158, 11, 0.45);
  border: 1px dashed rgba(180, 83, 9, 0.7);
  border-radius: 2px;
}}
.taped-note-title {{
  font-family: 'Kanit', sans-serif;
  font-size: 17px;
  font-weight: 900;
  color: #78350F;
  line-height: 1.2;
}}
.taped-note-sub {{
  font-family: 'Mali', cursive;
  font-size: 13px;
  font-weight: 700;
  color: #92400E;
  margin-top: 2px;
}}

/* Center Main Header */
.main-header-center {{
  text-align: center;
  flex: 1;
}}
.main-title {{
  font-family: 'Kanit', sans-serif;
  font-size: 44px;
  font-weight: 900;
  line-height: 1.05;
  color: #0F172A;
  letter-spacing: -0.5px;
}}
.main-title span.blue-highlight {{
  color: #1D4ED8;
}}
.main-title span.red-highlight {{
  color: #DC2626;
}}
.main-subtitle {{
  font-family: 'Mali', cursive;
  font-size: 20px;
  font-weight: 600;
  color: #334155;
  margin-top: 3px;
}}
.main-subtitle strong {{
  color: #92400E;
  background: #FEF3C7;
  padding: 2px 10px;
  border-radius: 6px;
  border: 1.5px solid #FCD34D;
}}

/* Top Right Checklist Notepad (Ruled paper + spiral) */
.checklist-notepad {{
  background: #FFFFFF;
  background-image: repeating-linear-gradient(#FFFFFF, #FFFFFF 19px, #E2E8F0 20px);
  border: 2.5px solid #0F172A;
  border-radius: 8px;
  box-shadow: 3.5px 4.5px 0px #0F172A;
  padding: 10px 14px 10px 24px;
  width: 255px;
  flex-shrink: 0;
  position: relative;
}}
/* Spiral holes on left */
.checklist-notepad::before {{
  content: "•\\A•\\A•\\A•\\A•";
  white-space: pre-wrap;
  position: absolute;
  left: 6px;
  top: 10px;
  font-size: 14px;
  line-height: 18px;
  color: #94A3B8;
  font-weight: 900;
}}
.notepad-header {{
  font-family: 'Kanit', sans-serif;
  font-weight: 800;
  font-size: 13.5px;
  color: #0F172A;
  border-bottom: 2px solid #0F172A;
  padding-bottom: 3px;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.checklist-item {{
  font-size: 11.5px;
  font-weight: 600;
  color: #1E293B;
  line-height: 1.35;
  margin-bottom: 3px;
  display: flex;
  align-items: flex-start;
  gap: 4px;
}}

/* ================= STRATEGY BOX (CORE HEADER) ================= */
.strategy-box-wrapper {{
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 4px;
}}

.strategy-box {{
  background: #EFF6FF;
  border: 2.5px solid #0F172A;
  border-radius: 12px;
  box-shadow: 3.5px 4.5px 0px #0F172A;
  padding: 10px 18px;
  display: flex;
  align-items: center;
  gap: 16px;
  width: 710px;
}}
.strategy-title {{
  font-family: 'Kanit', sans-serif;
  font-size: 20px;
  font-weight: 900;
  color: #1D4ED8;
  margin-bottom: 3px;
  display: flex;
  align-items: center;
  gap: 6px;
}}
.strategy-bullets {{
  font-size: 13px;
  font-weight: 500;
  color: #0F172A;
  line-height: 1.35;
}}
.strategy-bullets li {{
  list-style-type: square;
  margin-left: 16px;
  margin-bottom: 2px;
}}

/* Cloud Callout Speech Bubble */
.cloud-bubble {{
  background: #FFFBEB;
  border: 2.5px solid #0F172A;
  border-radius: 14px;
  box-shadow: 3px 4px 0px #0F172A;
  padding: 10px 14px;
  width: 295px;
  font-size: 12.5px;
  font-weight: 600;
  color: #78350F;
  line-height: 1.35;
  position: relative;
}}
.cloud-bubble::before {{
  content: "";
  position: absolute;
  left: -14px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-top: 9px solid transparent;
  border-bottom: 9px solid transparent;
  border-right: 14px solid #0F172A;
}}
.cloud-bubble::after {{
  content: "";
  position: absolute;
  left: -10px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-top: 7px solid transparent;
  border-bottom: 7px solid transparent;
  border-right: 11px solid #FFFBEB;
}}

/* ================= TREE CONNECTOR & EXECUTION ================= */
.tree-connector-wrapper {{
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 2px 0 6px;
}}
.tree-trunk-line {{
  width: 3px;
  height: 12px;
  background: #0F172A;
}}
.execution-pill {{
  background: #0F172A;
  color: #FFFFFF;
  font-family: 'Kanit', sans-serif;
  font-size: 13.5px;
  font-weight: 800;
  padding: 3px 20px;
  border-radius: 14px;
  display: inline-block;
  letter-spacing: 0.5px;
  border: 1.5px solid #334155;
}}
.tree-branches-svg {{
  width: 100%;
  height: 14px;
  margin-top: -2px;
}}

/* 6-Column Execution Grid */
.columns-grid {{
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-bottom: 12px;
}}

.column-card {{
  border: 2.5px solid #0F172A;
  border-radius: 10px;
  box-shadow: 3px 4px 0px #0F172A;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}

/* Pastel Fills for Columns */
.col-card-1 {{ background: #FEF2F2; }}
.col-card-2 {{ background: #FFF7ED; }}
.col-card-3 {{ background: #FEFCE8; }}
.col-card-4 {{ background: #ECFEFF; }}
.col-card-5 {{ background: #EFF6FF; }}
.col-card-6 {{ background: #FAF5FF; }}

.col-header {{
  font-family: 'Kanit', sans-serif;
  font-size: 13.5px;
  font-weight: 900;
  text-align: center;
  padding: 5px 2px;
  color: #FFFFFF;
  border-bottom: 2.5px solid #0F172A;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.bg-col-1 {{ background: #DC2626; }}
.bg-col-2 {{ background: #EA580C; }}
.bg-col-3 {{ background: #CA8A04; }}
.bg-col-4 {{ background: #0891B2; }}
.bg-col-5 {{ background: #2563EB; }}
.bg-col-6 {{ background: #7C3AED; }}

.col-avatar {{
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 6px 0 2px;
  border-bottom: 1.5px dashed #94A3B8;
}}

.col-content {{
  padding: 8px 8px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.col-item {{
  font-size: 11.5px;
  font-weight: 700;
  color: #1E293B;
  line-height: 1.25;
  display: flex;
  align-items: flex-start;
  gap: 4px;
}}
.col-item::before {{
  content: "•";
  color: #0F172A;
  font-weight: 900;
  font-size: 13px;
  margin-top: -1px;
}}

/* ================= BOTTOM 3-CARD SECTION ================= */
.bottom-section {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  margin-bottom: 10px;
}}

.bottom-card {{
  background: #FFFFFF;
  border: 2.5px solid #0F172A;
  border-radius: 12px;
  box-shadow: 3px 4px 0px #0F172A;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
}}

.bottom-card-header {{
  font-family: 'Kanit', sans-serif;
  font-size: 14px;
  font-weight: 900;
  color: #FFFFFF;
  background: #0F172A;
  padding: 5px 12px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  letter-spacing: 0.3px;
}}
.header-blue {{ background: #1D4ED8; }}
.header-green {{ background: #15803D; }}
.header-gold {{ background: #D97706; }}

/* Left Card: Role Levels */
.role-row {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  padding-bottom: 4px;
  border-bottom: 1.5px dashed #E2E8F0;
}}
.role-row:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
.role-skill-icon {{
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}}
.role-text-title {{
  font-size: 12.5px;
  font-weight: 800;
  color: #0F172A;
}}
.role-text-desc {{
  font-size: 11.5px;
  color: #334155;
  line-height: 1.25;
}}
.role-text-desc strong {{
  color: #1D4ED8;
}}

/* Right Card: Focus Checklist */
.focus-item {{
  font-size: 12px;
  font-weight: 600;
  color: #1E293B;
  line-height: 1.35;
  margin-bottom: 4px;
  display: flex;
  align-items: flex-start;
  gap: 5px;
}}
.focus-quote-box {{
  background: #FEF3C7;
  border: 1.5px solid #FCD34D;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 700;
  color: #78350F;
  line-height: 1.35;
  margin-top: auto;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}}

/* ================= FOOTER RIBBON BANNER ================= */
.footer-ribbon {{
  background: #0F172A;
  border: 2.5px solid #0F172A;
  border-radius: 10px;
  padding: 8px 18px;
  color: #FFFFFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 3px 4px 0px #0F172A;
}}
.footer-ribbon-text {{
  font-size: 14px;
  font-weight: 700;
  color: #F8FAFC;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.footer-ribbon-text strong {{
  color: #FBBF24;
}}
.footer-zuri-badge {{
  background: #E8820C;
  color: #FFFFFF;
  font-family: 'Kanit', sans-serif;
  font-size: 14px;
  font-weight: 900;
  padding: 4px 16px;
  border-radius: 8px;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}}
</style>
</head>
<body>
<div class="poster-canvas">
  <!-- HEADER ROW -->
  <div class="header-row">
    <!-- Left Taped Note -->
    <div class="taped-note">
      <div class="taped-note-title">ZURI MASTER GUIDE</div>
      <div class="taped-note-sub">PM • BA • PO PLAYBOOK</div>
    </div>

    <!-- Center Main Title -->
    <div class="main-header-center">
      <div class="main-title">โครงสร้างเอกสารที่ <span class="blue-highlight">BA / PO</span> <span class="red-highlight">ควรมี ?</span></div>
      <div class="main-subtitle">จากแนวคิดเรื่อง <strong>"การสื่อสาร"</strong> สู่โครงสร้างเอกสารที่ใช้ทำงานได้จริง</div>
    </div>

    <!-- Right Notepad Checklist -->
    <div class="checklist-notepad">
      <div class="notepad-header">
        <span>หลักการสำคัญ</span>
        <span>💡</span>
      </div>
      <div class="checklist-item"><span>☑️</span><span>ไม่ใช่ยิ่งเยอะยิ่งดี แต่ต้องพอเข้าใจ</span></div>
      <div class="checklist-item"><span>☑️</span><span>แต่ละคน <strong>"เห็นภาพตรงกัน"</strong> ไม่หลุด</span></div>
      <div class="checklist-item"><span>☑️</span><span>ลดการเดา = ลด Rework ทั้งระบบ</span></div>
      <div class="checklist-item"><span>☑️</span><span>Goal ➔ Flow ➔ Spec ➔ Test</span></div>
      <div class="checklist-item"><span>☑️</span><span>เพื่อพาทีมไปสู่เป้าหมายร่วมกัน</span></div>
    </div>
  </div>

  <!-- STRATEGY CORE BOX -->
  <div class="strategy-box-wrapper">
    <div class="strategy-box">
      <div>{CHAR_PRESENTER}</div>
      <div>
        <div class="strategy-title">🎯 1. BUSINESS NEED &amp; PROBLEM STATEMENT</div>
        <ul class="strategy-bullets">
          <li>มองภาพรวมของธุรกิจและเข้าใจ Pain Point ที่แท้จริงของผู้ใช้</li>
          <li>ใช้โจทย์ (Business Goal) กำหนดขอบเขต In-Scope และ Out-of-Scope</li>
          <li>กำหนด Success Metrics และตัวชี้วัดผลลัพธ์ที่ชัดเจน</li>
          <li>สื่อสารและซิงก์ความเข้าใจกับทีมอย่างต่อเนื่อง</li>
        </ul>
      </div>
    </div>
    <div class="cloud-bubble">
      🧭 <strong>เปรียบเสมือน "เข็มทิศ" ของทีม</strong><br>
      เชื่อมข้อมูล ➔ โจทย์ ➔ การลงมือทำ ให้ทุกคนโฟกัสไปในทิศทางเดียวกัน
    </div>
  </div>

  <!-- TREE CONNECTOR -->
  <div class="tree-connector-wrapper">
    <div class="tree-trunk-line"></div>
    <span class="execution-pill">▼ EXECUTION : 6 เอกสารหลักที่ต้องส่งต่อ ▼</span>
    <!-- SVG Tree Branches going to 6 columns -->
    <svg class="tree-branches-svg" viewBox="0 0 1140 14">
      <line x1="570" y1="0" x2="570" y2="6" stroke="#0F172A" stroke-width="2.5"/>
      <line x1="95" y1="6" x2="1045" y2="6" stroke="#0F172A" stroke-width="2.5"/>
      <!-- Branch drops into 6 columns: 95, 285, 475, 665, 855, 1045 -->
      <line x1="95" y1="6" x2="95" y2="14" stroke="#0F172A" stroke-width="2.5"/>
      <line x1="285" y1="6" x2="285" y2="14" stroke="#0F172A" stroke-width="2.5"/>
      <line x1="475" y1="6" x2="475" y2="14" stroke="#0F172A" stroke-width="2.5"/>
      <line x1="665" y1="6" x2="665" y2="14" stroke="#0F172A" stroke-width="2.5"/>
      <line x1="855" y1="6" x2="855" y2="14" stroke="#0F172A" stroke-width="2.5"/>
      <line x1="1045" y1="6" x2="1045" y2="14" stroke="#0F172A" stroke-width="2.5"/>
    </svg>
  </div>

  <!-- 6-COLUMN EXECUTION GRID -->
  <div class="columns-grid">
    <!-- Col 1: Requirement -->
    <div class="column-card col-card-1">
      <div class="col-header bg-col-1">REQUIREMENT</div>
      <div class="col-avatar">{CHAR_BA}</div>
      <div class="col-content">
        <div class="col-item">Business Goal</div>
        <div class="col-item">In / Out Scope</div>
        <div class="col-item">User Persona</div>
        <div class="col-item">Success Metrics</div>
      </div>
    </div>

    <!-- Col 2: User Story -->
    <div class="column-card col-card-2">
      <div class="col-header bg-col-2">USER STORY</div>
      <div class="col-avatar">{CHAR_PO}</div>
      <div class="col-content">
        <div class="col-item">As a [User]</div>
        <div class="col-item">I want [Action]</div>
        <div class="col-item">So that [Value]</div>
        <div class="col-item">INVEST Model</div>
      </div>
    </div>

    <!-- Col 3: Process Flow -->
    <div class="column-card col-card-3">
      <div class="col-header bg-col-3">PROCESS FLOW</div>
      <div class="col-avatar">{CHAR_FLOW}</div>
      <div class="col-content">
        <div class="col-item">As-Is / To-Be</div>
        <div class="col-item">Step-by-Step</div>
        <div class="col-item">Decision Points</div>
        <div class="col-item">Exception Paths</div>
      </div>
    </div>

    <!-- Col 4: Wireframe -->
    <div class="column-card col-card-4">
      <div class="col-header bg-col-4">WIREFRAME</div>
      <div class="col-avatar">{CHAR_DESIGNER}</div>
      <div class="col-content">
        <div class="col-item">Screen Layout</div>
        <div class="col-item">Interaction</div>
        <div class="col-item">Loading State</div>
        <div class="col-item">Error State</div>
      </div>
    </div>

    <!-- Col 5: Acceptance Criteria -->
    <div class="column-card col-card-5">
      <div class="col-header bg-col-5">AC &amp; RULES</div>
      <div class="col-avatar">{CHAR_DEV}</div>
      <div class="col-content">
        <div class="col-item">Given / When / Then</div>
        <div class="col-item">Business Rules</div>
        <div class="col-item">Validation Logic</div>
        <div class="col-item">Edge Cases</div>
      </div>
    </div>

    <!-- Col 6: Test & UAT -->
    <div class="column-card col-card-6">
      <div class="col-header bg-col-6">TEST &amp; UAT</div>
      <div class="col-avatar">{CHAR_QA}</div>
      <div class="col-content">
        <div class="col-item">Test Scenarios</div>
        <div class="col-item">Data Preparation</div>
        <div class="col-item">Sign-off Criteria</div>
        <div class="col-item">Go-live Gates</div>
      </div>
    </div>
  </div>

  <!-- BOTTOM 3 CARDS SECTION -->
  <div class="bottom-section">
    <!-- Card 1: Role Levels (T/I/X Skill) -->
    <div class="bottom-card">
      <div class="bottom-card-header header-blue">
        <span>★</span> บทบาทของแต่ละระดับ (T / I / X Skill)
      </div>
      <div class="role-row">
        <div class="role-skill-icon">{SKILL_X_SVG}</div>
        <div>
          <div class="role-text-title">ระดับบริหาร (PO / PM / Head)</div>
          <div class="role-text-desc"><strong>X-Skill :</strong> คุม Strategy, Value, Roadmap และปลดล็อกความเสี่ยง</div>
        </div>
      </div>
      <div class="role-row">
        <div class="role-skill-icon">{SKILL_T_SVG}</div>
        <div>
          <div class="role-text-title">ระดับกลาง (BA / Tech Lead)</div>
          <div class="role-text-desc"><strong>T-Skill :</strong> ลึก 1 ด้าน + กว้างรอบด้าน ออกแบบ Flow เคลียร์โจทย์</div>
        </div>
      </div>
      <div class="role-row">
        <div class="role-skill-icon">{SKILL_I_SVG}</div>
        <div>
          <div class="role-text-title">ระดับปฏิบัติการ (Dev / QA)</div>
          <div class="role-text-desc"><strong>I-Skill :</strong> เชี่ยวชาญเฉพาะทาง โค้ดแม่นยำ ดักบั๊กตรงตาม AC</div>
        </div>
      </div>
    </div>

    <!-- Card 2: Delivery Process Circular Loop -->
    <div class="bottom-card">
      <div class="bottom-card-header header-green">
        <span>★</span> กระบวนการทำงาน (Delivery Loop)
      </div>
      {CIRCULAR_LOOP_SVG}
    </div>

    <!-- Card 3: Head/PM Focus Checklist -->
    <div class="bottom-card">
      <div class="bottom-card-header header-gold">
        <span>★</span> สิ่งที่ BA / PO / PM ต้องโฟกัส
      </div>
      <div class="focus-item"><span>☑️</span><span>เข้าใจ Goal และ Pain Point ที่แท้จริง</span></div>
      <div class="focus-item"><span>☑️</span><span>สื่อสารด้วยภาพ Flow และ Mockup ชัดเจน</span></div>
      <div class="focus-item"><span>☑️</span><span>เขียน AC ให้วัดผลและเทสได้จริง</span></div>
      <div class="focus-item"><span>☑️</span><span>ลดความกำกวม ป้องกันการรื้อโค้ด 100%</span></div>
      <div class="focus-quote-box">
        "เอกสารที่ดีไม่ต้องหนา แต่ต้องช่วยให้ทีมเห็นภาพเดียวกัน และลุยงานต่อได้ทันที"
      </div>
    </div>
  </div>

  <!-- FOOTER RIBBON BANNER -->
  <div class="footer-ribbon">
    <div class="footer-ribbon-text">
      <span>★</span>
      <span><strong>Key Takeaway :</strong> เอกสารของ BA / PO = ขอบเขตชัด + ทีมเห็นภาพตรงกัน + Dev โค้ดได้ + QA เทสผ่าน + ส่งมอบจริง</span>
    </div>
    <div class="footer-zuri-badge">
      ZURI ACADEMY
    </div>
  </div>
</div>
</body>
</html>
"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

file_url = "file:///" + OUT_HTML.replace("\\", "/")
cmd = [
    CHROME_PATH,
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--window-size=1200,1200",
    f"--screenshot={OUT_PNG}",
    file_url
]
subprocess.run(cmd, capture_output=True, text=True)
print("Rendered upgraded high-grade infographic successfully!")
