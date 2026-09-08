# -*- coding: utf-8 -*-
"""Build 30 ZURI Anime Storytelling infographics at 1200x1200px."""

import os
import sys
import time
import subprocess
import tempfile
import atexit
import shutil

sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

from zuri_signal_template import render_zuri_signal_poster

OUTPUT_DIR = CURRENT_DIR
HTML_DIR = os.path.join(OUTPUT_DIR, "html")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(HTML_DIR, exist_ok=True)

# 30 Complete High-Grade Document Specifications
ALL_DOCS = [
    # 01. BA/Doc for BA-PO.md
    {
        "file_rel": "BA/Doc for BA-PO.md",
        "output_name": "01_BA_Doc_for_BA_PO",
        "top_note_title": "ZURI MASTER GUIDE", "top_note_sub": "PM • BA • PO PLAYBOOK",
        "title_plain": "โครงสร้างเอกสารที่ BA / PO ควรมี ?",
        "title_html": "โครงสร้างเอกสารที่ <span class=\"blue-highlight\">BA / PO</span> <span class=\"red-highlight\">ควรมี ?</span>",
        "subtitle_html": "จากแนวคิดเรื่อง <strong>\"การสื่อสาร\"</strong> สู่โครงสร้างเอกสารที่ใช้ทำงานได้จริง",
        "notepad_header": "หลักการสำคัญ",
        "notepad_items": [
            "ไม่ใช่ยิ่งเยอะยิ่งดี แต่ต้องพอเข้าใจ",
            "แต่ละคน <strong>\"เห็นภาพตรงกัน\"</strong> ไม่หลุด",
            "ลดการเดา = ลด Rework ทั้งระบบ",
            "Goal ➔ Flow ➔ Spec ➔ Test",
            "เพื่อพาทีมไปสู่เป้าหมายร่วมกัน"
        ],
        "strategy_title": "🎯 1. BUSINESS NEED &amp; PROBLEM STATEMENT",
        "strategy_bullets": [
            "มองภาพรวมของธุรกิจและเข้าใจ Pain Point ที่แท้จริงของผู้ใช้",
            "ใช้โจทย์ (Business Goal) กำหนดขอบเขต In-Scope และ Out-of-Scope",
            "กำหนด Success Metrics และตัวชี้วัดผลลัพธ์ที่ชัดเจน",
            "สื่อสารและซิงก์ความเข้าใจกับทีมอย่างต่อเนื่อง"
        ],
        "cloud_bubble_html": "🧭 <strong>เปรียบเสมือน \"เข็มทิศ\" ของทีม</strong><br>เชื่อมข้อมูล ➔ โจทย์ ➔ การลงมือทำ ให้ทุกคนโฟกัสไปในทิศทางเดียวกัน",
        "execution_label": "EXECUTION : 6 เอกสารหลักที่ต้องส่งต่อ",
        "columns": [
            {"title": "REQUIREMENT", "char": "ba", "items": ["Business Goal", "In / Out Scope", "User Persona", "Success Metrics"]},
            {"title": "USER STORY", "char": "po", "items": ["As a [User]", "I want [Action]", "So that [Value]", "INVEST Model"]},
            {"title": "PROCESS FLOW", "char": "flow", "items": ["As-Is / To-Be", "Step-by-Step", "Decision Points", "Exception Paths"]},
            {"title": "WIREFRAME", "char": "designer", "items": ["Screen Layout", "Interaction", "Loading State", "Error State"]},
            {"title": "AC & RULES", "char": "dev", "items": ["Given / When / Then", "Business Rules", "Validation Logic", "Edge Cases"]},
            {"title": "TEST & UAT", "char": "qa", "items": ["Test Scenarios", "Data Preparation", "Sign-off Criteria", "Go-live Gates"]}
        ],
        "bottom_left_title": "บทบาทของแต่ละระดับ (T / I / X Skill)",
        "skills": [
            {"type": "x", "title": "ระดับบริหาร (PO / PM / Head)", "code": "X-Skill", "desc": "คุม Strategy, Value, Roadmap และปลดล็อกความเสี่ยง"},
            {"type": "t", "title": "ระดับกลาง (BA / Tech Lead)", "code": "T-Skill", "desc": "ลึก 1 ด้าน + กว้างรอบด้าน ออกแบบ Flow เคลียร์โจทย์"},
            {"type": "i", "title": "ระดับปฏิบัติการ (Dev / QA)", "code": "I-Skill", "desc": "เชี่ยวชาญเฉพาะทาง โค้ดแม่นยำ ดักบั๊กตรงตาม AC"}
        ],
        "bottom_center_title": "กระบวนการทำงาน (Delivery Loop)",
        "loop_data": {
            "s1_title": "1. NEED & INSIGHT", "s1_sub": "🔍 หา Pain Point",
            "s2_title": "2. STORY & FLOW", "s2_sub": "📋 วาง Scope / Story",
            "s3_title": "3. AC & BUILD", "s3_sub": "💻 โค้ดตรงตาม Spec",
            "s4_title": "4. UAT & RELEASE", "s4_sub": "🚀 ส่งมอบ / ตรวจรับ",
            "center_t1": "เป้าหมายธุรกิจ", "center_t2": "& คุณค่าผู้ใช้"
        },
        "bottom_right_title": "สิ่งที่ BA / PO / PM ต้องโฟกัส",
        "focus_items": [
            "เข้าใจ Goal และ Pain Point ที่แท้จริง",
            "สื่อสารด้วยภาพ Flow และ Mockup ชัดเจน",
            "เขียน AC ให้วัดผลและเทสได้จริง",
            "ลดความกำกวม ป้องกันการรื้อโค้ด 100%"
        ],
        "focus_quote": "เอกสารที่ดีไม่ต้องหนา แต่ต้องช่วยให้ทีมเห็นภาพเดียวกัน และลุยงานต่อได้ทันที",
        "key_takeaway": "เอกสารของ BA / PO = ขอบเขตชัด + ทีมเห็นภาพตรงกัน + Dev โค้ดได้ + QA เทสผ่าน + ส่งมอบจริง"
    },

    # 02. PO/Doc for BA-PO.md
    {
        "file_rel": "PO/Doc for BA-PO.md",
        "output_name": "02_PO_Doc_for_BA_PO",
        "top_note_title": "PO VALUE MASTER", "top_note_sub": "PRODUCT STRATEGY",
        "title_plain": "เอกสารและสิ่งส่งมอบที่ PO ต้องถือ",
        "title_html": "เอกสารและสิ่งส่งมอบที่ <span class=\"blue-highlight\">PO ต้องถือ</span> <span class=\"red-highlight\">&amp; คุมคุณค่า</span>",
        "subtitle_html": "จาก <strong>\"Product Vision\"</strong> สู่ Backlog ที่พร้อมเปลี่ยนเป็นรายได้และความสำเร็จ",
        "notepad_header": "หัวใจของ PO",
        "notepad_items": [
            "คุมทิศทาง ไม่ปล่อยให้ทีมหลงทาง",
            "จัด Priority <strong>\"สร้าง Value สูงสุด\"</strong>",
            "วัดผลด้วย Data ไม่ใช่อารมณ์",
            "กล้าปฏิเสธสิ่งที่ไม่คุ้มค่า",
            "ส่งมอบคุณค่าทีละรอบสม่ำเสมอ"
        ],
        "strategy_title": "🎯 1. PRODUCT VISION &amp; STRATEGY ALIGNMENT",
        "strategy_bullets": [
            "กำหนดเข็มทิศระยะสั้น-กลาง-ยาว ว่าเราสร้าง Product นี้ไปเพื่อใคร",
            "เชื่อมโยง Business Goals เข้ากับความต้องการของผู้ใช้จริง",
            "กำหนด OKRs และ Success Metrics ของแต่ละ Release ชัดเจน",
            "เป็นผู้ตัดสินใจขั้นสุดท้าย (Decision Maker) ในทุกข้อขัดแย้ง"
        ],
        "cloud_bubble_html": "👑 <strong>เปรียบเสมือน \"แม่ทัพ\" ฝั่งธุรกิจ</strong><br>รับผิดชอบผลลัพธ์และความคุ้มค่าในการลงทุน (ROI) ของทุกฟีเจอร์",
        "execution_label": "PO ARTIFACTS : 6 สิ่งที่ PO ต้องมีในมือ",
        "columns": [
            {"title": "PRODUCT VISION", "char": "po", "items": ["Target Customer", "Unique Value", "Business Goals", "Market Strategy"]},
            {"title": "PRODUCT ROADMAP", "char": "presenter", "items": ["Strategic Themes", "Now / Next / Later", "Release Milestones", "Outcome Goals"]},
            {"title": "PRIORITIZED BACKLOG", "char": "flow", "items": ["Order by Value", "Epic & Stories", "DEEP Framework", "DoR Criteria"]},
            {"title": "USER FEEDBACK", "char": "designer", "items": ["User Analytics", "Interview Insights", "Usage Metrics", "NPS / CSAT"]},
            {"title": "ACCEPTANCE GATE", "char": "ba", "items": ["Acceptance Criteria", "Definition of Done", "Scope Verification", "Sign-off Release"]},
            {"title": "BUSINESS ROI", "char": "qa", "items": ["Revenue Impact", "Cost Efficiency", "Time to Market", "Stakeholder Alignment"]}
        ],
        "bottom_left_title": "การตัดสินใจของ PO (3 มิติหลัก)",
        "skills": [
            {"type": "x", "title": "มิติยุทธศาสตร์ (Strategic Level)", "code": "Strategy", "desc": "สอดคล้องกับทิศทางองค์กรและสร้างความได้เปรียบในการแข่งขัน"},
            {"type": "t", "title": "มิติผู้ใช้งาน (User Value)", "code": "User Impact", "desc": "แก้ปัญหาจริง ใช้งานง่าย และตอบโจทย์ความต้องการ"},
            {"type": "i", "title": "มิติความเป็นไปได้ (Feasibility)", "code": "Feasibility", "desc": "ประเมินต้นทุน ความเสี่ยง และเทคโนโลยีร่วมกับ Dev"}
        ],
        "bottom_center_title": "วงจรบริหารคุณค่า (PO Value Cycle)",
        "loop_data": {
            "s1_title": "1. CAPTURE & DISCOVER", "s1_sub": "💡 รวบรวมไอเดีย & Data",
            "s2_title": "2. PRIORITIZE", "s2_sub": "🎯 คัดเลือกงาน High Value",
            "s3_title": "3. SPRINT COMMIT", "s3_sub": "🤝 วางแผนร่วมกับทีม",
            "s4_title": "4. MEASURE & LEARN", "s4_sub": "📈 วัดผลหลัง Release",
            "center_t1": "MAXIMUM ROI", "center_t2": "& USER VALUE"
        },
        "bottom_right_title": "สิ่งที่ PO มือโปรต้องระวัง",
        "focus_items": [
            "ไม่ปล่อยให้ Backlog กลายเป็นถังขยะรวมไอเดีย",
            "ไม่เปลี่ยน Priority ทุกวันจนทีมตั้งหลักไม่ทัน",
            "ตัดสินใจบนข้อมูลจริง ไม่ใช่แค่คำขอของคนเสียงดัง",
            "หมั่น Refine และตัดสิ่งที่ไม่จำเป็นทิ้งเสมอ"
        ],
        "focus_quote": "PO ที่เก่งไม่ใช่คนที่รับปากทำทุกอย่าง แต่คือคนที่กล้าตัด 90% เพื่อโฟกัส 10% ที่สำคัญที่สุด",
        "key_takeaway": "PO ที่ทรงพลัง = วิสัยทัศน์ชัดเจน + Backlog มีระเบียบ + ตัดสินใจด้วยข้อมูล + มุ่งเน้น Value จริง"
    },

    # 03. Acceptance Criteria.md
    {
        "file_rel": "Acceptance Criteria.md",
        "output_name": "03_Acceptance_Criteria",
        "top_note_title": "AC MASTER GUIDE", "top_note_sub": "GIVEN / WHEN / THEN",
        "title_plain": "Acceptance Criteria เขียนยังไงให้ทีมไม่งง ?",
        "title_html": "Acceptance Criteria <span class=\"blue-highlight\">เขียนยังไง</span> <span class=\"red-highlight\">ให้ทีมไม่งง ?</span>",
        "subtitle_html": "เปลี่ยนความต้องการกว้างๆ สู่ <strong>\"เงื่อนไขตรวจรับ\"</strong> ที่วัดผลและเทสได้จริง",
        "notepad_header": "เกณฑ์ความสำเร็จ",
        "notepad_items": [
            "บอกชัดเจนว่าแบบไหนเรียกว่า <strong>\"Done\"</strong>",
            "ลดการตีความเองของ Dev และ QA",
            "ครอบคลุมทั้ง Happy และ Error Case",
            "เปลี่ยนคำคุณศัพท์เป็นตัวเลขวัดผล",
            "เทสผ่านได้จริงอย่างมีมาตรฐาน"
        ],
        "strategy_title": "🎯 1. GIVEN / WHEN / THEN STRUCTURE",
        "strategy_bullets": [
            "Given (สถานะเริ่มต้น) : เงื่อนไขหรือข้อมูลก่อนที่ผู้ใช้จะเริ่มทำ Action",
            "When (การกระทำ) : สิ่งที่ผู้ใช้กด คลิก หรือส่งข้อมูลเข้ามาในระบบ",
            "Then (ผลลัพธ์ที่คาดหวัง) : สิ่งที่ระบบต้องตอบสนอง บันทึก หรือแสดงผล",
            "And (เงื่อนไขเสริม) : รายละเอียดหรือสถานะเพิ่มเติมที่ต้องเกิดขึ้นพร้อมกัน"
        ],
        "cloud_bubble_html": "⚖️ <strong>เปรียบเสมือน \"สัญญาตรวจรับงาน\"</strong><br>User Story บอกสิ่งที่อยากได้ ส่วน AC บอกว่าแบบไหนถึงจะเรียกว่าเสร็จสมบูรณ์",
        "execution_label": "AC BLUEPRINT : 6 องค์ประกอบที่ต้องดักให้ครบ",
        "columns": [
            {"title": "HAPPY PATH", "char": "flow", "items": ["Given ข้อมูลถูกต้อง", "When กด Submit", "Then บันทึกสำเร็จ", "สถานะเป็น Active"]},
            {"title": "VALIDATION", "char": "ba", "items": ["เช็กข้อมูลบังคับ", "รูปแบบ Email/เบอร์", "ข้อความแจ้งเตือน", "ไฮไลต์ฟิลด์ผิด"]},
            {"title": "ROLE & PERMISSION", "char": "po", "items": ["สิทธิ์ Admin / User", "การมองเห็นปุ่ม", "การแก้ไขข้อมูล", "403 Forbidden"]},
            {"title": "ERROR STATES", "char": "dev", "items": ["Network หลุด", "Server Error 500", "ปุ่ม Retry ทำงาน", "ข้อมูลไม่สูญหาย"]},
            {"title": "BOUNDARY / EDGE", "char": "qa", "items": ["อัปโหลดเกินขนาด", "กรอกตัวอักษรสูงสุด", "Time-out Session", "กดปุ่มซ้ำรัวๆ"]},
            {"title": "DATA & AUDIT", "char": "presenter", "items": ["Schema Field ครบ", "Created/Updated By", "Audit Log บันทึก", "Database Integrity"]}
        ],
        "bottom_left_title": "ระดับความลึกของเกณฑ์ตรวจรับ",
        "skills": [
            {"type": "x", "title": "เกณฑ์ระดับธุรกิจ (Business Acceptance)", "code": "Business Rule", "desc": "เงื่อนไขการคำนวณราคา สิทธิ์โปรโมชัน และความถูกต้องทางบัญชี"},
            {"type": "t", "title": "เกณฑ์ระดับการใช้งาน (Functional & UI)", "code": "User Experience", "desc": "พฤติกรรมหน้าจอ ข้อความแจ้งเตือน และการเปลี่ยนสถานะข้อมูล"},
            {"type": "i", "title": "เกณฑ์ระดับเทคนิค (Technical & Security)", "code": "Tech & Security", "desc": "Performance, API Response Code, Data Encryption และ Logs"}
        ],
        "bottom_center_title": "วงจรการนำ AC ไปใช้จริง",
        "loop_data": {
            "s1_title": "1. DRAFT IN REFINE", "s1_sub": "✍️ BA/PO ร่าง AC",
            "s2_title": "2. REVIEW WITH DEV", "s2_sub": "🔍 Dev/QA ซักถาม",
            "s3_title": "3. BUILD & TEST", "s3_sub": "💻 โค้ด & เทสตาม AC",
            "s4_title": "4. VERIFY & SIGN-OFF", "s4_sub": "✅ ตรวจรับงาน 100%",
            "center_t1": "TESTABLE", "center_t2": "& VERIFIABLE"
        },
        "bottom_right_title": "คำกว้างๆ ที่ห้ามใช้เด็ดขาด",
        "focus_items": [
            "❌ 'ระบบต้องเร็ว' ➔ ให้แก้เป็น 'ตอบสนองใน 2 วิ'",
            "❌ 'ใช้งานง่าย' ➔ ให้แก้เป็น 'ขั้นตอนไม่เกิน 3 คลิก'",
            "❌ 'ต้องปลอดภัย' ➔ ให้แก้เป็น 'เข้ารหัส HTTPS + SHA256'",
            "❌ 'แจ้งเตือน' ➔ ให้แก้เป็น 'ส่ง Push Notification พร้อมระบุข้อความ'"
        ],
        "focus_quote": "AC ที่ดีไม่จำเป็นต้องยาว แต่ต้องชัดพอให้ Dev โค้ดได้ตรง และ QA เขียน Test Case ได้ทันที",
        "key_takeaway": "Acceptance Criteria = กำหนด Given/When/Then + ดัก Error Cases + วัดผลเป็นตัวเลข + เทสผ่านได้จริง"
    },

    # 04. Agile.md
    {
        "file_rel": "Agile.md",
        "output_name": "04_Agile_Mindset",
        "top_note_title": "AGILE MINDSET", "top_note_sub": "SCRUM TEAM CORE",
        "title_plain": "ใน Agile มีใครบ้าง ? แต่ละคนทำหน้าที่อะไร ?",
        "title_html": "ใน Agile มีใครบ้าง ? <span class=\"blue-highlight\">แต่ละคนทำหน้าที่อะไร ?</span>",
        "subtitle_html": "รวมพลังทีมส่งมอบคุณค่าอย่างต่อเนื่องและ <strong>\"ปรับตัวได้ไว\"</strong> ต่อทุกความเปลี่ยนแปลง",
        "notepad_header": "Agile Principles",
        "notepad_items": [
            "ส่งมอบชิ้นงานที่ใช้งานได้จริง",
            "ปรับเปลี่ยนตาม Feedback ได้ไว",
            "สื่อสารตรงไปตรงมาข้ามสายงาน",
            "ทำงานร่วมกันแบบ <strong>\"One Team\"</strong>",
            "รักษาจังหวะทำงานที่ยั่งยืน"
        ],
        "strategy_title": "🎯 1. THE 3 PILLARS OF SCRUM TEAM",
        "strategy_bullets": [
            "Product Owner (PO) : เจ้าของวิสัยทัศน์ ตัดสินใจเลือกลำดับงานที่สร้างคุณค่าสูงสุดให้ธุรกิจ",
            "Scrum Master (SM) : โค้ชดูแลกระบวนการ ขจัดอุปสรรค และช่วยให้ทีมทำงานได้อย่างราบรื่น",
            "Development Team (Dev & QA) : ผู้เชี่ยวชาญร่วมกันออกแบบ พัฒนา และส่งมอบซอฟต์แวร์คุณภาพ",
            "ไม่มีลำดับขั้นบังคับบัญชา ทุกคนรับผิดชอบเป้าหมายของ Sprint ร่วมกัน"
        ],
        "cloud_bubble_html": "🤝 <strong>One Team, One Goal</strong><br>PO ชี้เป้าหมาย ➔ SM ขจัดอุปสรรค ➔ Dev & QA สร้างสรรค์ผลงานจริง",
        "execution_label": "AGILE CADENCE : 6 กิจกรรมสร้างการส่งมอบอย่างต่อเนื่อง",
        "columns": [
            {"title": "PRODUCT BACKLOG", "char": "po", "items": ["Single Source of Truth", "Prioritized by Value", "Epic & User Story", "Refine สม่ำเสมอ"]},
            {"title": "SPRINT PLANNING", "char": "presenter", "items": ["ตั้ง Sprint Goal", "เลือกงานเข้า Sprint", "ประเมิน Capacity", "Commitment ร่วมกัน"]},
            {"title": "DAILY SCRUM", "char": "dev", "items": ["ซิงก์ 15 นาทีทุกวัน", "เมื่อวานทำอะไร", "วันนี้จะทำอะไร", "ติดปัญหาอะไรไหม"]},
            {"title": "DEVELOPMENT", "char": "flow", "items": ["Pair / Mob Program", "Clean Code & Refactor", "Unit Test 100%", "Continuous Delivery"]},
            {"title": "SPRINT REVIEW", "char": "designer", "items": ["Demo ชิ้นงานจริง", "รับ Feedback ลูกค้า", "ตรวจรับตาม AC", "ปรับปรุง Backlog"]},
            {"title": "RETROSPECTIVE", "char": "qa", "items": ["ทบทวนวิธีทำงาน", "อะไรทำได้ดี", "อะไรควรปรับปรุง", "Action Items ชัดเจน"]}
        ],
        "bottom_left_title": "ความรับผิดชอบของ 3 บทบาทหลัก",
        "skills": [
            {"type": "x", "title": "Product Owner (Value Owner)", "code": "PO Role", "desc": "รับผิดชอบ ROI, Roadmap, Backlog และการยอมรับชิ้นงาน"},
            {"type": "t", "title": "Scrum Master (Process Coach)", "code": "SM Role", "desc": "ดูแล Agile Values, ปกป้องทีมจากงานแทรก, ปลดล็อกบล็อกเกอร์"},
            {"type": "i", "title": "Dev Team (Quality & Delivery)", "code": "Dev Team", "desc": "ออกแบบสถาปัตยกรรม เขียนโค้ด ทดสอบ และส่งมอบชิ้นงาน"}
        ],
        "bottom_center_title": "วงจร Sprint Iteration",
        "loop_data": {
            "s1_title": "1. PLAN (PLANNING)", "s1_sub": "🎯 วางเป้า Sprint",
            "s2_title": "2. BUILD (DAILY SYNC)", "s2_sub": "💻 ลงมือสร้างชิ้นงาน",
            "s3_title": "3. DEMO (REVIEW)", "s3_sub": "✨ โชว์งานรับ Feedback",
            "s4_title": "4. IMPROVE (RETRO)", "s4_sub": "🛡️ ปรับปรุงทีมเวิร์ก",
            "center_t1": "SHIPPABLE", "center_t2": "INCREMENT"
        },
        "bottom_right_title": "ความเข้าใจผิดเกี่ยวกับ Agile",
        "focus_items": [
            "❌ คิดว่า Agile คือไม่ต้องทำเอกสารอะไรเลย",
            "❌ คิดว่า Agile คือสั่งเปลี่ยน Requirement ได้ทุกนาที",
            "❌ คิดว่า PO มีหน้าที่แค่สั่งงาน แล้ว Dev นั่งทำตาม",
            "❌ คิดว่า Agile คือการเร่งสปีดจนทีมต้องทำงานล่วงเวลา"
        ],
        "focus_quote": "Agile ไม่ใช่การทำงานไร้ระเบียบ แต่คือการสร้างวินัยในการสื่อสารและส่งมอบคุณค่าที่แท้จริง",
        "key_takeaway": "Agile ที่แข็งแกร่ง = บทบาทชัดเจน + ส่งมอบทีละรอบ + รับ Feedback สม่ำเสมอ + พัฒนาทีมต่อเนื่อง"
    },

    # 05. Agile Ceremonies.md
    {
        "file_rel": "Agile Ceremonies.md",
        "output_name": "05_Agile_Ceremonies",
        "top_note_title": "SCRUM EVENTS", "top_note_sub": "5 CEREMONIES GUIDE",
        "title_plain": "Agile Ceremonies 5 พิธีกรรมที่ต้องรู้ !",
        "title_html": "Agile Ceremonies <span class=\"blue-highlight\">5 พิธีกรรม</span> <span class=\"red-highlight\">ที่ต้องรู้ !</span>",
        "subtitle_html": "ไม่ใช่การประชุมเยอะ แต่คือ <strong>\"จังหวะการทำงาน\"</strong> ที่ช่วยให้ทีมไม่หลุดโฟกัส",
        "notepad_header": "ทำไมต้องมี Ceremonies?",
        "notepad_items": [
            "คุยกันถูกเรื่อง ถูกเวลา",
            "ลดการประชุมนอกรอบที่ไร้เป้าหมาย",
            "สร้างความโปร่งใสในทีม 100%",
            "ตรวจพบปัญหาและแก้ได้เร็ว",
            "ส่งมอบงานได้อย่างต่อเนื่อง"
        ],
        "strategy_title": "🎯 1. SPRINT PLANNING : จุดเริ่มต้นของทุกชัยชนะ",
        "strategy_bullets": [
            "ตอบคำถามสำคัญ 3 ข้อ : ทำไม Sprint นี้ถึงสำคัญ? (Goal) เราจะทำอะไร? และเราจะทำอย่างไร?",
            "PO นำเสนอ User Story ที่พร้อม (DoR) Dev ประเมิน Effort และเลือกงานเข้า Sprint Backlog",
            "กำหนด Sprint Goal เป็นเป้าหมายหนึ่งเดียวที่ทุกคนในทีม Commit ร่วมกัน",
            "Time-box : ไม่เกิน 2 ชั่วโมงสำหรับ Sprint 1 สัปดาห์ หรือ 4 ชั่วโมงสำหรับ 2 สัปดาห์"
        ],
        "cloud_bubble_html": "⏰ <strong>Time-boxed & Purpose-driven</strong><br>ทุกการประชุมต้องมีเป้าหมาย ผลลัพธ์ และกรอบเวลาที่ชัดเจน ห้ามปล่อยให้ยืดเยื้อ",
        "execution_label": "THE 5 CEREMONIES : 5 พิธีกรรมหลักตามมาตรฐานสากล",
        "columns": [
            {"title": "1. PLANNING", "char": "presenter", "items": ["Sprint Goal ชัดเจน", "เลือกงานเข้า Backlog", "ประเมิน Capacity", "วางแผน Task ย่อย"]},
            {"title": "2. DAILY SCRUM", "char": "dev", "items": ["15 นาที ยืนคุย", "เมื่อวานทำอะไร", "วันนี้จะทำอะไร", "แจ้งบล็อกเกอร์ทันที"]},
            {"title": "3. REFINEMENT", "char": "ba", "items": ["เตรียมงานล่วงหน้า", "แตก Story ขนาดใหญ่", "เติม AC ให้สมบูรณ์", "กะ Story Points"]},
            {"title": "4. SPRINT REVIEW", "char": "po", "items": ["Demo ของจริง", "Stakeholder ร่วมฟัง", "รับ Feedback ตลาด", "ปรับ Roadmap ต่อ"]},
            {"title": "5. RETROSPECTIVE", "char": "qa", "items": ["คุยทบทวนวิธีทำงาน", "อะไรที่ทำได้ดี", "อะไรที่ต้องแก้", "สร้าง Action Plan"]},
            {"title": "SUCCESS GATES", "char": "flow", "items": ["DoR ผ่านก่อน Plan", "DoD ผ่านก่อน Review", "Continuous Feedback", "Team Evolution"]}
        ],
        "bottom_left_title": "การเตรียมตัวในแต่ละ Ceremony",
        "skills": [
            {"type": "x", "title": "ก่อนเข้า Planning", "code": "Backlog Ready", "desc": "PO/BA ต้องเตรียม User Story ให้ผ่าน DoR และมี AC พร้อม"},
            {"type": "t", "title": "ระหว่าง Daily Scrum", "code": "Focus on Blockers", "desc": "เน้นบอกปัญหาเพื่อขอความช่วยเหลือ ไม่ใช่รายงานเจ้านาย"},
            {"type": "i", "title": "ตอนจบ Retrospective", "code": "Actionable Items", "desc": "ต้องมีข้อตกลงปรับปรุงอย่างน้อย 1-2 ข้อที่ทำได้จริงใน Sprint ถัดไป"}
        ],
        "bottom_center_title": "จังหวะเวลาใน 1 Sprint",
        "loop_data": {
            "s1_title": "1. SPRINT PLANNING", "s1_sub": "🏁 เริ่มต้น Sprint",
            "s2_title": "2. DAILY SCRUM & BUILD", "s2_sub": "⚡ ซิงก์ทุกวัน 15 นาที",
            "s3_title": "3. SPRINT REVIEW", "s3_sub": "🎬 Demo ของจริง",
            "s4_title": "4. RETROSPECTIVE", "s4_sub": "🔧 ปรับปรุงทีมเวิร์ก",
            "center_t1": "CONTINUOUS", "center_t2": "DELIVERY"
        },
        "bottom_right_title": "สัญญาณอันตรายใน Ceremonies",
        "focus_items": [
            "Daily กลายเป็นการรายงานสถานะแบบตึงเครียด",
            "Sprint Planning ไม่มี Goal เอาแต่งานมายัดใส่ตาราง",
            "Sprint Review กลายเป็นเวทีจับผิดข้อบกพร่อง",
            "Retrospective คุยกันเพลินแต่ไม่มีใครทำ Action Item จริง"
        ],
        "focus_quote": "Agile Ceremonies คือเครื่องมือสร้างความโปร่งใส ไม่ใช่ภาระการประชุมที่เพิ่มขึ้น",
        "key_takeaway": "5 พิธีกรรม Scrum = Plan ให้ชัด + Sync รายวัน + Refine ล่วงหน้า + Demo รับ Feedback + Retro พัฒนาทีม"
    },

    # 06. backlog.md
    {
        "file_rel": "backlog.md",
        "output_name": "06_Backlog_Management",
        "top_note_title": "BACKLOG MASTERY", "top_note_sub": "DEEP FRAMEWORK",
        "title_plain": "จัด Backlog ยังไง ไม่ให้รกและหลุดเป้า ?",
        "title_html": "จัด Backlog ยังไง <span class=\"blue-highlight\">ไม่ให้รก</span> <span class=\"red-highlight\">&amp; หลุดเป้า ?</span>",
        "subtitle_html": "เปลี่ยนรายการงานสะเปะสะปะ สู่ <strong>\"DEEP Backlog\"</strong> ที่พร้อมสร้างคุณค่าให้ธุรกิจ",
        "notepad_header": "คุณสมบัติ DEEP Backlog",
        "notepad_items": [
            "<strong>D</strong>etailed Appropriately (ละเอียดพอดี)",
            "<strong>E</strong>stimated (มีการประเมิน Effort)",
            "<strong>E</strong>mergent (ปรับเปลี่ยนตามจริง)",
            "<strong>P</strong>rioritized (เรียงลำดับ Value)",
            "หมั่น Clean up สม่ำเสมอ"
        ],
        "strategy_title": "🎯 1. BACKLOG HIERARCHY : การจัดโครงสร้างงานอย่างมีระบบ",
        "strategy_bullets": [
            "Epic (เป้าหมายใหญ่) : ขอบเขตงานระดับยุทธศาสตร์ที่ต้องใช้เวลาทำหลาย Sprint",
            "Feature (ความสามารถ) : ฟังก์ชันการทำงานที่ส่งมอบประสบการณ์ใหม่ให้ผู้ใช้",
            "User Story (งานย่อย) : ชิ้นงานขนาดเล็กที่มีคุณค่าและทำจบได้ใน 1 Sprint",
            "Bug & Tech Debt : งานแก้ไขข้อบกพร่องและปรับปรุงโครงสร้างทางเทคนิค"
        ],
        "cloud_bubble_html": "🗄️ <strong>Single Source of Truth</strong><br>ทุกความต้องการ ทุกไอเดีย และทุกบั๊กต้องรวมอยู่ที่ Backlog ที่เดียว ห้ามมีงานนอกระบบ",
        "execution_label": "BACKLOG STRUCTURE : 6 ระดับการดูแล Backlog ให้มีพลัง",
        "columns": [
            {"title": "TOP : SPRINT READY", "char": "ba", "items": ["ผ่านเกณฑ์ DoR 100%", "AC ครบถ้วนชัดเจน", "มี Wireframe & Flow", "ประเมิน Story Points"]},
            {"title": "MIDDLE : REFINING", "char": "po", "items": ["กำลังแตก Story ย่อย", "ซักถามโจทย์ธุรกิจ", "เช็ก Dependency", "เตรียมเข้า Planning"]},
            {"title": "BOTTOM : ICEBOX", "char": "flow", "items": ["ไอเดียกว้างๆ ในอนาคต", "ยังไม่มี Spec ละเอียด", "รอการประเมิน Value", "พร้อมปรับเปลี่ยน"]},
            {"title": "TECH DEBT", "char": "dev", "items": ["Refactor Legacy Code", "Upgrade Dependencies", "Improve Performance", "Automate CI/CD"]},
            {"title": "BUG FIXES", "char": "qa", "items": ["จัดตาม Severity", "แนบ Reproduce Step", "ดักบั๊กหลุดจาก UAT", "Regression Suite"]},
            {"title": "ARCHIVE / TRASH", "char": "presenter", "items": ["ตัดงานที่หมดความสำคัญ", "ลบการ์ดดองเกิน 6 เดือน", "บอกเหตุผลในการตัด", "รักษา Backlog ให้คลีน"]}
        ],
        "bottom_left_title": "ระดับความละเอียดของ Backlog Items",
        "skills": [
            {"type": "x", "title": "ระดับบนสุด (Top 10-20%)", "code": "High Detail", "desc": "ละเอียดมาก ชัดเจนพร้อมให้ Dev หยิบไปเขียนโค้ดได้ทันที"},
            {"type": "t", "title": "ระดับกลาง (Next 30%)", "code": "Medium Detail", "desc": "เห็นโครงร่างและ User Flow กำลังนำเข้าสู่กระบวนการ Refinement"},
            {"type": "i", "title": "ระดับล่าง (Future Ideas)", "code": "Low Detail", "desc": "เขียนเป็นเป้าหมายกว้างๆ ยังไม่ลงรายละเอียดจนกว่าจะถึงเวลา"}
        ],
        "bottom_center_title": "วงจรการดูแล Backlog (Grooming Cycle)",
        "loop_data": {
            "s1_title": "1. CAPTURE & LOG", "s1_sub": "📥 บันทึกไอเดียเข้า Backlog",
            "s2_title": "2. PRIORITIZE VALUE", "s2_sub": "⚖️ เรียงตาม ROI / RICE",
            "s3_title": "3. SLICE & REFINE", "s3_sub": "✂️ ซอยงานย่อย + ใส่ AC",
            "s4_title": "4. COMMIT TO SPRINT", "s4_sub": "🚀 ส่งเข้ากระบวนการพัฒนา",
            "center_t1": "CLEAN &", "center_t2": "ORGANIZED"
        },
        "bottom_right_title": "สัญญาณเตือน Backlog กำลังพัง",
        "focus_items": [
            "มีการ์ดค้างดองอยู่เกิน 6 เดือนโดยไม่มีใครแตะ",
            "ทุกการ์ดถูกปักเป็น Priority 1 (ด่วนที่สุด) ทั้งหมด",
            "การ์ดด้านบนไม่มี AC ทำให้ Dev ต้องมาเดาใจ",
            "มีงานงอกนอกระบบที่ไม่ได้บันทึกไว้ใน Backlog"
        ],
        "focus_quote": "Backlog ที่ดีไม่ใช่ Backlog ที่มีการ์ดเยอะที่สุด แต่คือ Backlog ที่พร้อมสร้าง Value ได้เร็วที่สุด",
        "key_takeaway": "Backlog คุณภาพสูง = บนละเอียดพร้อมทำ + ล่างกว้างยืดหยุ่น + เรียงลำดับ Value + หมั่นตัดสิ่งไม่จำเป็น"
    },

    # 07. Checklist-Dev.md
    {
        "file_rel": "Checklist-Dev.md",
        "output_name": "07_Checklist_Dev",
        "top_note_title": "DEFINITION OF READY", "top_note_sub": "DEV HAND-OFF CHECKLIST",
        "title_plain": "Checklist ก่อนส่งงานให้ Dev (DoR)",
        "title_html": "Checklist <span class=\"blue-highlight\">ก่อนส่งงานให้ Dev</span> <span class=\"red-highlight\">(DoR Checklist)</span>",
        "subtitle_html": "เช็กให้ชัวร์ก่อนเริ่มโค้ด <strong>\"ลดการถามกลับ ลดงานแก้ ลดบั๊ก\"</strong> ได้ถึง 80%",
        "notepad_header": "หัวใจของ DoR",
        "notepad_items": [
            "ไม่เริ่มงานจากความคลุมเครือ",
            "Dev & QA เข้าใจโจทย์ตรงกัน",
            "มีครบทั้งภาพ หน้าจอ และตรรกะ",
            "ประเมินเวลาได้แม่นยำ 100%",
            "ลดงานรื้อโค้ดในภายหลัง"
        ],
        "strategy_title": "🎯 1. DEFINITION OF READY (DoR) : ประตูกั้นคุณภาพต้นน้ำ",
        "strategy_bullets": [
            "DoR คือข้อตกลงร่วมกันว่า User Story ต้องมีความพร้อมระดับใดจึงจะอนุญาตให้นำเข้าสู่ Sprint",
            "ช่วยป้องกันไม่ให้ Dev ต้องหยุดชะงักกลางคันเพราะข้อมูลไม่พอ หรือต้องรอถามคำถาม",
            "QA สามารถเริ่มเขียน Test Plan และ Test Cases คู่ขนานไปกับ Dev ได้ทันที",
            "ลดความขัดแย้งและสร้างความมั่นใจในการ Commit งานของทีม"
        ],
        "cloud_bubble_html": "🛡️ <strong>Quality at the Source</strong><br>การเตรียมงานเพิ่มขึ้น 20% ในขั้นตอนต้นน้ำ จะช่วยประหยัดเวลาแก้งานปลายน้ำได้ถึง 80%",
        "execution_label": "THE 6 DoR GATES : 6 ข้อต้องเช็กให้ผ่านก่อน Hand-off",
        "columns": [
            {"title": "1. USER & ROLE", "char": "po", "items": ["ระบุ Persona ชัดเจน", "สิทธิ์การเข้าถึง (Role)", "Context การใช้งาน", "Value ที่ได้รับ"]},
            {"title": "2. FLOW & SCREEN", "char": "flow", "items": ["User Flow ครบทุกทาง", "Wireframe / Mockup", "Loading State", "Error & Empty State"]},
            {"title": "3. BUSINESS RULES", "char": "ba", "items": ["ตรรกะการคำนวณ", "เงื่อนไขทางบัญชี/ภาษี", "Data Validation", "ไม่มี Logic ขัดแย้ง"]},
            {"title": "4. AC & EDGE CASES", "char": "dev", "items": ["Given / When / Then", "Negative Cases ครบ", "ดักเคสข้อมูลสุดโต่ง", "วัดผลได้จริง"]},
            {"title": "5. DATA & API SPEC", "char": "designer", "items": ["Schema Field ชัดเจน", "API Endpoint & Payload", "Data Type & Format", "Third-party Integration"]},
            {"title": "6. OUT OF SCOPE", "char": "qa", "items": ["ระบุสิ่งที่ไม่ทำชัดเจน", "ป้องกัน Scope บวม", "ไม่มีข้อตกลงปากเปล่า", "ผ่าน DoR Sign-off"]}
        ],
        "bottom_left_title": "ระดับความพร้อมก่อนเข้า Sprint",
        "skills": [
            {"type": "x", "title": "ความพร้อมด้านธุรกิจ (Business Ready)", "code": "Business Ready", "desc": "Goal ชัดเจน, PO อนุมัติ Scope, มี Success Metric วัดผลได้"},
            {"type": "t", "title": "ความพร้อมด้านดีไซน์ (Design Ready)", "code": "UX/UI Ready", "desc": "Wireframe ครบทุกหน้าจอ, UI Components สอดคล้องกับ Design System"},
            {"type": "i", "title": "ความพร้อมด้านเทคนิค (Tech Ready)", "code": "Tech Ready", "desc": "สถาปัตยกรรมพร้อม, ปลดล็อก Dependency, ประเมิน Story Points แล้ว"}
        ],
        "bottom_center_title": "ขั้นตอนการ Hand-off ที่ถูกต้อง",
        "loop_data": {
            "s1_title": "1. DRAFT & SELF-CHECK", "s1_sub": "✍️ BA ตรวจ Checklist",
            "s2_title": "2. REFINEMENT WALK", "s2_sub": "🗣️ ซักถามร่วมกับทีม",
            "s3_title": "3. UPDATE & FIX GAPS", "s3_sub": "🔧 เติมข้อมูลที่ขาด",
            "s4_title": "4. MARK DoR PASSED", "s4_sub": "✅ พร้อมเริ่มใน Sprint",
            "center_t1": "ZERO", "center_t2": "CONFUSION"
        },
        "bottom_right_title": "จุดที่คนมักมองข้ามและทำให้งานสะดุด",
        "focus_items": [
            "ลืมระบุข้อความ Error Message เมื่อเกิดปัญหา",
            "ลืมออกแบบหน้าจอตอนไม่มีข้อมูล (Empty State)",
            "ไม่ได้ระบุผลกระทบต่อระบบเดิม (System Dependency)",
            "ปล่อยให้มีจุดที่ต้อง 'ไว้ค่อยคุยกันตอนเริ่มโค้ด'"
        ],
        "focus_quote": "DoR ไม่ใช่กำแพงกั้นทีม แต่คือสัญญาใจด้านคุณภาพที่ทำให้ทุกคนทำงานด้วยความสบายใจ",
        "key_takeaway": "DoR Checklist = Role ชัด + Flow ครบ + AC พร้อม + API เคลียร์ + Out of Scope นิ่ง ➔ Dev ลุยได้ทันที"
    },

    # 08. MoSCoW.md
    {
        "file_rel": "MoSCoW.md",
        "output_name": "08_MoSCoW_Method",
        "top_note_title": "MoSCoW METHOD", "top_note_sub": "PRIORITIZATION FRAMEWORK",
        "title_plain": "MoSCoW Method จัดลำดับงานแบบมือโปร",
        "title_html": "MoSCoW Method <span class=\"blue-highlight\">จัดลำดับงาน</span> <span class=\"red-highlight\">แบบมืออาชีพ</span>",
        "subtitle_html": "ตัดส่วนเกิน เพิ่มส่วนสำคัญ <strong>\"ส่งมอบงานตรงเวลา ไม่เกินงบ ไม่ลดคุณภาพ\"</strong>",
        "notepad_header": "4 ระดับ MoSCoW",
        "notepad_items": [
            "<strong>M</strong>ust Have : ขาดไม่ได้ (ระบบพัง)",
            "<strong>S</strong>hould Have : สำคัญมาก (มีทางเลี่ยง)",
            "<strong>C</strong>ould Have : มีก็ดี (ถ้าเวลาเหลือ)",
            "<strong>W</strong>on't Have : ไม่ทำในรอบนี้",
            "สัดส่วน Must ไม่เกิน 60%"
        ],
        "strategy_title": "🎯 1. THE GOLDEN RATIO : สัดส่วนทองคำในการจัดสรรขอบเขต",
        "strategy_bullets": [
            "Must Have (ไม่เกิน 60%) : ฟังก์ชันแกนหลักที่ขาดไม่ได้ หากไม่มีระบบจะใช้งานไม่ได้หรือผิดกฎหมาย",
            "Should Have (~20%) : ฟังก์ชันสำคัญที่เพิ่มคุณค่าสูง แต่ถ้าจำเป็นยังมีทางออกแก้ปัญหาชั่วคราวได้",
            "Could Have (~20%) : ฟังก์ชันเสริมที่เพิ่มความประทับใจ แต่เป็น Buffer พร้อมตัดออกหากเวลาไม่พอ",
            "Won't Have (ชัดเจน) : ฟังก์ชันที่ตกลงกันว่าจะไม่ทำในรอบนี้ ช่วยดับความคาดหวังที่ไม่ตรงกัน"
        ],
        "cloud_bubble_html": "⚖️ <strong>Guaranteed Deadlines</strong><br>การแบ่งสัดส่วน MoSCoW อย่างถูกต้อง คือการันตี 100% ว่าโปรเจกต์จะส่งมอบได้ตรงเวลาแน่นอน",
        "execution_label": "MoSCoW BLUEPRINT : 6 ขั้นตอนการคัดเลือกและเจรจา",
        "columns": [
            {"title": "1. LIST ALL SCOPE", "char": "po", "items": ["รวบรวมทุกฟีเจอร์", "ไม่ตกหล่นไอเดีย", "เขียน User Stories", "ระบุ Business Value"]},
            {"title": "2. MUST CRITERIA", "char": "ba", "items": ["ระบบทำงานไม่ได้?", "ผิดกฎหมายไหม?", "กระทบ Core Flow?", "ไม่มีทางเลี่ยง = Must"]},
            {"title": "3. SHOULD CRITERIA", "char": "flow", "items": ["สร้าง Value สูง", "ผู้ใช้ต้องการมาก", "มี Workaround ชั่วคราว", "เลื่อนไปรอบหน้าได้"]},
            {"title": "4. COULD (BUFFER)", "char": "designer", "items": ["Nice-to-have", "เพิ่มความสวยงาม", "แรงงานต่ำ (Low Effort)", "พร้อมตัดทิ้งทันที"]},
            {"title": "5. WON'T (SAVER)", "char": "dev", "items": ["ตกลงไม่ทำรอบนี้", "บันทึกใน Icebox", "ดับความคาดหวัง", "ป้องกัน Scope บวม"]},
            {"title": "6. STAKEHOLDER SIGN", "char": "qa", "items": ["ประชุมตกลงร่วมกัน", "ลงนามข้อตกลง Scope", "Commitment ทุกฝ่าย", "ล็อก Baseline"]}
        ],
        "bottom_left_title": "การประเมินความจำเป็นในแต่ละระดับ",
        "skills": [
            {"type": "x", "title": "Must Have (ขาดแล้วพัง)", "code": "Vital / Critical", "desc": "เช่น ระบบล็อกอิน, ชำระเงิน, ความปลอดภัย, การปฏิบัติตามกฎหมาย"},
            {"type": "t", "title": "Should Have (สำคัญแต่รอได้)", "code": "Important", "desc": "เช่น ระบบ Export Excel, กรองข้อมูลขั้นสูง, แจ้งเตือนทาง SMS"},
            {"type": "i", "title": "Could & Won't Have (ส่วนเสริม & ตัดทิ้ง)", "code": "Nice-to-have", "desc": "เช่น เปลี่ยนธีมสี Dark Mode, อนิเมชันปุ่ม, ฟังก์ชันที่รอดูผลตอบรับ"}
        ],
        "bottom_center_title": "กระบวนการเจรจาและปรับ Scope",
        "loop_data": {
            "s1_title": "1. GATHER REQUIREMENTS", "s1_sub": "📋 รวบรวมทุกความต้องการ",
            "s2_title": "2. CATEGORIZE 4 BUCKETS", "s2_sub": "🏷️ แยก M / S / C / W",
            "s3_title": "3. BALANCE RATIO 60/20/20", "s3_sub": "⚖️ ปรับสัดส่วนให้ปลอดภัย",
            "s4_title": "4. AGREE & LOCK COMMIT", "s4_sub": "🤝 ล็อกข้อตกลงร่วมกัน",
            "center_t1": "ON TIME", "center_t2": "& ON BUDGET"
        },
        "bottom_right_title": "กับดักที่พบบ่อยในการทำ MoSCoW",
        "focus_items": [
            "ทุกคนบอกว่างานของตนเองเป็น Must Have ทั้งหมด 100%",
            "ไม่กล้าปฏิเสธ ทำให้ไม่มีรายการ Won't Have ในเอกสาร",
            "จัดเป็น Could Have แต่สุดท้ายบังคับให้ทีมทำทุกอย่าง",
            "ไม่ยอมตัด Scope เมื่อเกิดปัญหาความล่าช้าทางเทคนิค"
        ],
        "focus_quote": "ถ้าทุกอย่างเป็น Must Have แปลว่าไม่มีการจัดลำดับความสำคัญเลยแม้แต่น้อย",
        "key_takeaway": "MoSCoW = Must (ขาดไม่ได้) + Should (สำคัญ) + Could (มีก็ดีเป็น Buffer) + Won't (ตัดทิ้งชัดเจน) ➔ ส่งมอบตามนัด 100%"
    },

    # 09. Prioritization.md
    {
        "file_rel": "Prioritization.md",
        "output_name": "09_Prioritization_Techniques",
        "top_note_title": "PRIORITY MATRIX", "top_note_sub": "DECISION FRAMEWORKS",
        "title_plain": "Prioritization ทำไมต้องเลือก และเลือกอย่างไร ?",
        "title_html": "Prioritization <span class=\"blue-highlight\">ทำไมต้องเลือก</span> <span class=\"red-highlight\">&amp; เลือกอย่างไร ?</span>",
        "subtitle_html": "ทรัพยากรและเวลามีจำกัด <strong>\"ต้องโฟกัสงานที่สร้าง Impact สูงสุด\"</strong> ให้องค์กร",
        "notepad_header": "5 มิติการประเมินงาน",
        "notepad_items": [
            "1. Business Value (มูลค่าธุรกิจ)",
            "2. User Impact (ผลต่อผู้ใช้)",
            "3. Urgency (ความเร่งด่วน)",
            "4. Effort & Cost (แรงงานและทุน)",
            "5. Risk & Dependency (ความเสี่ยง)"
        ],
        "strategy_title": "🎯 1. VALUE VS EFFORT MATRIX : ตะแกรงร่อนความคุ้มค่า",
        "strategy_bullets": [
            "Quick Wins (High Value, Low Effort) : งานที่สร้างผลลัพธ์สูงแต่ใช้แรงน้อย ➔ ต้องรีบทำทันที",
            "Major Projects (High Value, High Effort) : งานยุทธศาสตร์ขนาดใหญ่ ➔ วางแผนและซอยงานย่อยอย่างรอบคอบ",
            "Fill-ins (Low Value, Low Effort) : งานจิปาถะ ➔ ทำเมื่อมีเวลาว่าง หรือมอบหมายให้คนอื่นช่วย",
            "Thankless Tasks (Low Value, High Effort) : งานที่เปลืองแรงแต่ไร้คุณค่า ➔ ตัดทิ้งหรือหลีกเลี่ยงเด็ดขาด"
        ],
        "cloud_bubble_html": "🎯 <strong>Focus on High ROI</strong><br>การจัดลำดับงานคือการปกป้องพลังงานของทีม ไม่ให้เสียเวลากับงานที่ไม่สร้างการเติบโต",
        "execution_label": "PRIORITIZATION FRAMEWORKS : 6 เครื่องมือยอดนิยมระดับสากล",
        "columns": [
            {"title": "1. VALUE / EFFORT", "char": "po", "items": ["เมทริกซ์ 4 ช่อง", "Quick Wins อันดับ 1", "Major Projects", "ตัด Time Wasters"]},
            {"title": "2. MoSCoW METHOD", "char": "ba", "items": ["Must / Should / Could", "Won't Have ชัดเจน", "คุม Deadlines นิ่ง", "สัดส่วน 60/20/20"]},
            {"title": "3. RICE SCORING", "char": "presenter", "items": ["Reach x Impact", "x Confidence", "หารด้วย Effort", "คะแนนตัวเลขชัดเจน"]},
            {"title": "4. KANO MODEL", "char": "designer", "items": ["Basic Needs", "Performance Needs", "Delighters ว้าว", "Indifferent ตัดทิ้ง"]},
            {"title": "5. WSJF (SAFe)", "char": "flow", "items": ["Cost of Delay", "Time Criticality", "Risk Reduction", "หาร Job Duration"]},
            {"title": "6. ICE SCORING", "char": "qa", "items": ["Impact (1-10)", "Confidence (1-10)", "Ease (1-10)", "สูตรลัดคิดไว"]}
        ],
        "bottom_left_title": "การเลือกเฟรมเวิร์กให้เหมาะกับงาน",
        "skills": [
            {"type": "x", "title": "งานระดับยุทธศาสตร์ / Product Roadmap", "code": "Strategic", "desc": "ใช้ RICE Scoring หรือ WSJF เพื่อการคำนวณที่โปร่งใสและมีข้อมูลรองรับ"},
            {"type": "t", "title": "งานระดับการจัดการขอบเขต / Release Scope", "code": "Scope Control", "desc": "ใช้ MoSCoW Method เพื่อต่อรองและล็อก Commitment กับ Stakeholder"},
            {"type": "i", "title": "งานระดับฟีเจอร์ย่อย / Sprint Planning", "code": "Sprint Level", "desc": "ใช้ Value vs Effort Matrix หรือ ICE Scoring เพื่อการตัดสินใจที่รวดเร็ว"}
        ],
        "bottom_center_title": "กระบวนการจัดลำดับความสำคัญ",
        "loop_data": {
            "s1_title": "1. GATHER DATA", "s1_sub": "📊 เก็บข้อมูล & Feedback",
            "s2_title": "2. APPLY FRAMEWORK", "s2_sub": "🧮 คำนวณคะแนนตามเกณฑ์",
            "s3_title": "3. ALIGN STAKEHOLDERS", "s3_sub": "🗣️ สื่อสารเหตุผลความจำเป็น",
            "s4_title": "4. EXECUTE & MEASURE", "s4_sub": "🚀 ลุยงาน & ติดตามผลจริง",
            "center_t1": "MAXIMUM", "center_t2": "IMPACT"
        },
        "bottom_right_title": "หลุมพรางที่ต้องระวังในการจัด Priority",
        "focus_items": [
            "HiPPO Effect : ทำตามความเห็นของคนตำแหน่งสูงสุดโดยไม่มี Data",
            "เลือกทำแต่งานง่ายๆ แต่งานสร้าง Value สูงถูกผลัดวันประกันพรุ่ง",
            "เปลี่ยน Priority รายวันจนทีมสับสนและสูญเสียสมาธิ",
            "ตัดสินใจตามอารมณ์หรือความคุ้นเคยส่วนตัว"
        ],
        "focus_quote": "Prioritization คือศิลปะแห่งการกล้าปฏิเสธสิ่งที่ดี เพื่อทุ่มเทให้กับสิ่งที่ยอดเยี่ยมที่สุด",
        "key_takeaway": "การจัด Priority ที่ทรงพลัง = วิเคราะห์ 5 มิติ + ใช้เฟรมเวิร์กที่เหมาะสม + ตัดสินใจด้วย Data + มุ่งสร้าง Impact สูงสุด"
    },

    # 10. refinement.md
    {
        "file_rel": "refinement.md",
        "output_name": "10_Backlog_Refinement",
        "top_note_title": "GROOMING & SLICING", "top_note_sub": "PREPARATION MASTERY",
        "title_plain": "Backlog Refinement เตรียมงานยังไงให้ลื่นไหล ?",
        "title_html": "Backlog Refinement <span class=\"blue-highlight\">เตรียมงานยังไง</span> <span class=\"red-highlight\">ให้ลื่นไหล ?</span>",
        "subtitle_html": "การเตรียมความพร้อมล่วงหน้าคือ <strong>\"หัวใจของความเร็ว\"</strong> ในการพัฒนาซอฟต์แวร์",
        "notepad_header": "ประโยชน์ของ Refinement",
        "notepad_items": [
            "Sprint Planning สั้นลงและไม่เหนื่อยล้า",
            "แตกงานใหญ่ (Epic) เป็น Story เล็ก",
            "เคลียร์คำถามทางเทคนิคล่วงหน้า",
            "ลดความเสี่ยงระหว่างทำ Sprint",
            "ทีมเห็นภาพตรงกัน 100%"
        ],
        "strategy_title": "🎯 1. THE REFINEMENT SESSION : กิจกรรมเตรียมความพร้อมร่วมกัน",
        "strategy_bullets": [
            "กิจกรรมต่อเนื่องที่ PO, BA, Dev และ QA มาร่วมกันตรวจเช็กและขัดเกลา User Stories ใน Backlog",
            "จัดเป็นประจำสัปดาห์ละ 1-2 ครั้ง ครั้งละไม่เกิน 1 ชั่วโมง (ไม่ควรรอทำเฉพาะท้าย Sprint)",
            "เป้าหมาย : ทำให้มีงานที่ผ่าน Definition of Ready (DoR) ล่วงหน้าอย่างน้อย 1-2 Sprint เสมอ",
            "ช่วยให้ Dev เข้าใจที่มาที่ไป และ QA มีเวลาวางแผน Test Scenarios ล่วงหน้า"
        ],
        "cloud_bubble_html": "⚡ <strong>Smooth Sprint Flow</strong><br>การลงทุนเวลา Refine ล่วงหน้าสัปดาห์ละ 1 ชั่วโมง จะช่วยประหยัดเวลาแก้งานใน Sprint ได้หลายเท่าตัว",
        "execution_label": "REFINEMENT PLAYBOOK : 6 ขั้นตอนการขัดเกลางานแบบมือโปร",
        "columns": [
            {"title": "1. PRESENT GOAL", "char": "po", "items": ["PO เล่า Pain Point", "วัตถุประสงค์ของ Story", "User Persona ที่ได้รับผล", "Business Value"]},
            {"title": "2. STORY SLICING", "char": "ba", "items": ["แตก Epic ให้อยู่ใน Sprint", "แบ่งตาม User Workflow", "แบ่งตาม Rule / Data", "INVEST Framework"]},
            {"title": "3. CLARIFY AC", "char": "flow", "items": ["Given / When / Then", "ระบุ Happy & Error Flow", "ตรวจสอบ Business Rules", "ดักเคสข้อมูลผิดปกติ"]},
            {"title": "4. TECH & DESIGN", "char": "designer", "items": ["รีวิว Wireframe & UI", "เช็ก API / Database Spec", "ปลดล็อก Dependency", "ประเมินความเสี่ยง"]},
            {"title": "5. ESTIMATION", "char": "dev", "items": ["Planning Poker", "ประเมิน Story Points", "เทียบเคียงความซับซ้อน", "Dev Team ให้คะแนน"]},
            {"title": "6. MARK READY", "char": "qa", "items": ["เช็ก DoR ครบทุกข้อ", "ติดแท็ก Sprint Ready", "จัดลำดับใน Backlog", "พร้อมเข้า Planning"]}
        ],
        "bottom_left_title": "เทคนิคการแตกงาน (Story Slicing Techniques)",
        "skills": [
            {"type": "x", "title": "แบ่งตามขั้นตอน (Workflow Steps)", "code": "Workflow Slicing", "desc": "ทำ Flow หลักก่อน แล้วค่อยแตกงานย่อยสำหรับขั้นตอนเสริมในรอบถัดไป"},
            {"type": "t", "title": "แบ่งตามความซับซ้อนของข้อมูล (Data Variations)", "code": "Data Slicing", "desc": "เริ่มจากข้อมูลธรรมดา (Text) แล้วค่อยเพิ่มความซับซ้อน (File, Media, Export)"},
            {"type": "i", "title": "แบ่งตามช่องทางหรือสิทธิ์ (Role / Channel)", "code": "Role Slicing", "desc": "ทำสำหรับ User ทั่วไปก่อน แล้วค่อยแตก Story สำหรับ Admin หรือระบบภายนอก"}
        ],
        "bottom_center_title": "กระบวนการเตรียมงานล่วงหน้า",
        "loop_data": {
            "s1_title": "1. DRAFT BACKLOG", "s1_sub": "✍️ PO/BA ร่างงานล่วงหน้า",
            "s2_title": "2. REFINEMENT SESSION", "s2_sub": "🗣️ ทีมร่วมกันขัดเกลา",
            "s3_title": "3. SLICE & ESTIMATE", "s3_sub": "✂️ แตกย่อยและให้คะแนน",
            "s4_title": "4. READY FOR SPRINT", "s4_sub": "🚀 พร้อมหยิบใน Planning",
            "center_t1": "CONTINUOUS", "center_t2": "READINESS"
        },
        "bottom_right_title": "ข้อผิดพลาดที่พบบ่อยใน Refinement",
        "focus_items": [
            "มารอคุยรายละเอียดและแตกงานในวัน Sprint Planning",
            "PO มาเล่าแต่ไม่มีภาพ Wireframe หรือ Flow ประกอบ",
            "Dev นั่งฟังเฉยๆ โดยไม่ตั้งคำถามหรือทักท้วงความเสี่ยง",
            "รับงานชิ้นใหญ่ที่ยังคลุมเครือเข้าสู่กระบวนการพัฒนา"
        ],
        "focus_quote": "Refinement คือการซ้อมใหญ่ก่อนลงสนามจริง ยิ่งซ้อมละเอียดเท่าไหร่ วันแข่งจริงก็ยิ่งลื่นไหลเท่านั้น",
        "key_takeaway": "Good Refinement = เล่าโจทย์ชัด + แตกงานย่อย + เติม AC ให้ครบ + ปลด Dependency + พร้อมเริ่ม Sprint ทันที"
    },

    # 11. respon.md
    {
        "file_rel": "respon.md",
        "output_name": "11_Roles_Responsibilities",
        "top_note_title": "RACI MATRIX", "top_note_sub": "ROLES & RESPONSIBILITIES",
        "title_plain": "บทบาทหน้าที่ PM, PO, BA, Dev, QA ใครทำอะไร ?",
        "title_html": "บทบาทหน้าที่ <span class=\"blue-highlight\">PM, PO, BA, Dev, QA</span> <span class=\"red-highlight\">ใครทำอะไร ?</span>",
        "subtitle_html": "แบ่งหน้าที่ให้ชัดเจน <strong>\"ทำงานประสานกันเป็นทีมอย่างมืออาชีพ ไร้รอยต่อ\"</strong>",
        "notepad_header": "หลักการแบ่งบทบาท",
        "notepad_items": [
            "หน้าที่ชัด สื่อสารง่าย",
            "ไม่ก้าวก่าย ไม่ทิ้งงาน",
            "ร่วมรับผิดชอบเป้าหมายเดียว",
            "ขจัดความสับสนในองค์กร",
            "ขับเคลื่อนสู่ความสำเร็จร่วมกัน"
        ],
        "strategy_title": "🎯 1. RACI FRAMEWORK : ชัดเจนในทุกความรับผิดชอบ",
        "strategy_bullets": [
            "Accountable (A) : ผู้รับผิดชอบผลลัพธ์ขั้นสุดท้าย มีอำนาจตัดสินใจเด็ดขาด (มีได้เพียง 1 คนต่องาน)",
            "Responsible (R) : ผู้ลงมือปฏิบัติงานจริงเพื่อให้งานสำเร็จตามเป้าหมาย",
            "Consulted (C) : ผู้เชี่ยวชาญที่ต้องขอคำปรึกษาและข้อคิดเห็นก่อนตัดสินใจ",
            "Informed (I) : ผู้ที่ต้องได้รับการแจ้งข่าวสารและสถานะความคืบหน้าอย่างต่อเนื่อง"
        ],
        "cloud_bubble_html": "🤝 <strong>Seamless Collaboration</strong><br>ทุกตำแหน่งคือฟันเฟืองที่เสริมพลังกัน งานจะสำเร็จได้อย่างงดงามเมื่อทุกคนทำหน้าที่ของตนเองอย่างเต็มที่",
        "execution_label": "THE 5 KEY ROLES : 5 ตำแหน่งหลักในกระบวนการพัฒนา",
        "columns": [
            {"title": "PROJECT MANAGER", "char": "presenter", "items": ["คุม Timeline & Budget", "บริหารความเสี่ยงภาพรวม", "ประสานงาน Stakeholders", "แก้ปัญหาคอขวด"]},
            {"title": "PRODUCT OWNER", "char": "po", "items": ["คุม Product Vision", "จัดลำดับ Backlog", "ตัดสินใจ Business Value", "ตรวจรับงาน (Sign-off)"]},
            {"title": "BUSINESS ANALYST", "char": "ba", "items": ["วิเคราะห์ Requirement", "ออกแบบ User Flow", "เขียน AC & Rules", "ประสานงาน Dev & QA"]},
            {"title": "DEVELOPER", "char": "dev", "items": ["ออกแบบ System Arch", "เขียน Clean Code", "ทำ Unit & Integration Test", "ส่งมอบชิ้นงาน"]},
            {"title": "QUALITY ASSURANCE", "char": "qa", "items": ["วางแผน Test Plan", "เขียน Test Cases", "ตรวจจับบั๊ก & Regression", "รับรองคุณภาพระบบ"]},
            {"title": "SCRUM MASTER", "char": "flow", "items": ["ดูแล Scrum Process", "ขจัดบล็อกเกอร์ของทีม", "Facilitate Ceremonies", "สร้างวัฒนธรรมทีมที่ดี"]}
        ],
        "bottom_left_title": "การทำงานร่วมกันแบบคู่หู (Key Partnerships)",
        "skills": [
            {"type": "x", "title": "PO & PM (คู่หูยุทธศาสตร์)", "code": "PO + PM", "desc": "PO ดูแล 'คุณค่าและความคุ้มค่า' ส่วน PM ดูแล 'เวลาและทรัพยากร' เพื่อผลักดันโครงการ"},
            {"type": "t", "title": "BA & Dev (คู่หูถ่ายทอดโจทย์)", "code": "BA + Dev", "desc": "BA ถ่ายทอดโจทย์ธุรกิจและ Flow ส่วน Dev แปลงเป็น Solution และสถาปัตยกรรมระบบ"},
            {"type": "i", "title": "Dev & QA (คู่หูคุณภาพซอฟต์แวร์)", "code": "Dev + QA", "desc": "ร่วมกันตรวจเช็ก AC ดักจับ Edge Cases และทดสอบระบบก่อนส่งมอบสู่ผู้ใช้"}
        ],
        "bottom_center_title": "สายธารการส่งต่องาน (Hand-off Flow)",
        "loop_data": {
            "s1_title": "1. BUSINESS & PO", "s1_sub": "🎯 ตั้งโจทย์ & คัดเลือกงาน",
            "s2_title": "2. BA & UX SPEC", "s2_sub": "📋 วิเคราะห์ Flow & AC",
            "s3_title": "3. DEV & QA BUILD", "s3_sub": "💻 พัฒนาและทดสอบ",
            "s4_title": "4. PO & USER ACCEPT", "s4_sub": "🚀 ตรวจรับและ Go-Live",
            "center_t1": "ONE TEAM", "center_t2": "SUCCESS"
        },
        "bottom_right_title": "จุดที่มักสับสนในทางปฏิบัติ",
        "focus_items": [
            "ให้ BA ตัดสินใจทิศทางธุรกิจแทน PO โดยพลการ",
            "โยนหน้าที่การบริหารเวลาทั้งหมดให้ Dev รับผิดชอบ",
            "มองว่า QA เป็นคนเดียวที่ต้องรับผิดชอบเรื่องคุณภาพ",
            "ต่างคนต่างทำงานในไซโลโดยไม่มีการสื่อสารข้ามสายงาน"
        ],
        "focus_quote": "การแบ่งหน้าที่ที่ชัดเจนไม่ได้สร้างกำแพงกั้น แต่ช่วยให้ทุกคนรู้จุดโฟกัสและส่งพลังเสริมกันได้อย่างเต็มที่",
        "key_takeaway": "ความสำเร็จของทีม = PO คุมทิศ + PM คุมแผน + BA เคลียร์โจทย์ + Dev สร้างระบบ + QA เช็กคุณภาพ"
    },

    # 12. RICE.md
    {
        "file_rel": "RICE.md",
        "output_name": "12_RICE_Scoring",
        "top_note_title": "RICE MODEL", "top_note_sub": "SCORING MATRIX",
        "title_plain": "RICE Scoring คิดคะแนน Priority แบบมีเหตุผล",
        "title_html": "RICE Scoring <span class=\"blue-highlight\">คิดคะแนน Priority</span> <span class=\"red-highlight\">แบบมีเหตุผล</span>",
        "subtitle_html": "เปลี่ยนการเถียงด้วยความรู้สึก สู่ <strong>\"การตัดสินใจด้วยตัวเลขที่พิสูจน์ได้\"</strong>",
        "notepad_header": "สูตรคำนวณ RICE",
        "notepad_items": [
            "<strong>R</strong>each : เข้าถึงกี่คนใน 1 ไตรมาส",
            "<strong>I</strong>mpact : ผลต่อผู้ใช้ (0.25 - 3x)",
            "<strong>C</strong>onfidence : มั่นใจแค่ไหน (50-100%)",
            "<strong>E</strong>ffort : แรงงาน (คน-เดือน)",
            "สูตร : (R x I x C) ÷ E"
        ],
        "strategy_title": "🎯 1. THE RICE FORMULA : สูตรมาตรฐานระดับโลก",
        "strategy_bullets": [
            "Reach (การเข้าถึง) : จำนวนผู้ใช้จริงที่จะได้รับผลกระทบจากฟีเจอร์นี้ต่อ 1 ไตรมาส",
            "Impact (ผลกระทบ) : สร้างการเปลี่ยนแปลงต่อผู้ใช้มากแค่ไหน (3=Massive, 2=High, 1=Medium, 0.5=Low, 0.25=Minimal)",
            "Confidence (ความมั่นใจ) : เรามั่นใจในข้อมูลนี้มากแค่ไหน (100%=High/มี Data, 80%=Medium, 50%=Low/คิดเอง)",
            "Effort (แรงงาน) : เวลาและทรัพยากรที่ต้องใช้ในการพัฒนา คิดเป็นหน่วย Person-Months (คน-เดือน)"
        ],
        "cloud_bubble_html": "📊 <strong>Data-Driven Decisions</strong><br>ช่วยอธิบายกับผู้บริหารและ Stakeholder ได้อย่างโปร่งใสว่าทำไมฟีเจอร์นี้ถึงต้องทำก่อน",
        "execution_label": "RICE CALCULATION : 6 ขั้นตอนการคำนวณคะแนนอย่างแม่นยำ",
        "columns": [
            {"title": "1. LIST FEATURES", "char": "po", "items": ["รวบรวมไอเดียทั้งหมด", "เขียนเป้าหมายชัดเจน", "จัดกลุ่มตามหมวดหมู่", "เตรียมตารางคำนวณ"]},
            {"title": "2. ESTIMATE REACH", "char": "ba", "items": ["ดูจาก User Analytics", "จำนวน Active Users", "จำนวนธุรกรรมต่อเดือน", "ใส่ตัวเลขจริง"]},
            {"title": "3. ASSESS IMPACT", "char": "designer", "items": ["3 = เปลี่ยนพฤติกรรม", "2 = ผลกระทบสูงมาก", "1 = ผลกระทบปานกลาง", "0.5 = ผลเล็กน้อย"]},
            {"title": "4. RATE CONFIDENCE", "char": "presenter", "items": ["100% = มี Research ชัด", "80% = มี Data เบื้องต้น", "50% = คาดเดาล้วนๆ", "ห้ามมั่วตัวเลข"]},
            {"title": "5. ESTIMATE EFFORT", "char": "dev", "items": ["Dev + QA + Design", "นับเป็น คน-เดือน", "1 คนทำ 1 เดือน = 1", "ยิ่ง Effort ต่ำยิ่งดี"]},
            {"title": "6. CALCULATE & RANK", "char": "qa", "items": ["คำนวณตามสูตร RICE", "เรียงลำดับคะแนน", "คัดเลือก Top Priority", "ล็อกแผนการพัฒนา"]}
        ],
        "bottom_left_title": "สเกลการให้คะแนน Impact & Confidence",
        "skills": [
            {"type": "x", "title": "Impact Scale (ตัวคูณผลกระทบ)", "code": "Impact Factor", "desc": "3 (Massive) / 2 (High) / 1 (Medium) / 0.5 (Low) / 0.25 (Minimal)"},
            {"type": "t", "title": "Confidence Scale (ระดับความมั่นใจ)", "code": "Confidence %", "desc": "100% (High Confidence - มีข้อมูลรองรับ) / 80% (Medium) / 50% (Low - เสี่ยงสูง)"},
            {"type": "i", "title": "Effort Scale (หน่วยวัดแรงงาน)", "code": "Person-Months", "desc": "นับเวลารวมของทีมทั้งหมด เช่น 2 สัปดาห์ = 0.5 / 1 เดือน = 1 / 3 เดือน = 3"}
        ],
        "bottom_center_title": "กระบวนการจัดลำดับด้วย RICE",
        "loop_data": {
            "s1_title": "1. GATHER IDEAS", "s1_sub": "💡 รวบรวมฟีเจอร์",
            "s2_title": "2. SCORE R, I, C, E", "s2_sub": "🧮 ใส่ตัวเลข 4 ค่า",
            "s3_title": "3. CALCULATE SCORE", "s3_sub": "📈 คำนวณตามสูตร",
            "s4_title": "4. RANK & EXECUTE", "s4_sub": "🚀 ทำงานที่คะแนนสูงสุด",
            "center_t1": "OBJECTIVE", "center_t2": "SCORING"
        },
        "bottom_right_title": "ข้อควรระวังในการใช้ RICE Model",
        "focus_items": [
            "ใส่ Confidence 100% ทั้งที่คิดเอาเองโดยไม่มีข้อมูลรองรับ",
            "ประเมิน Effort ต่ำเกินจริงโดยไม่ได้ปรึกษาทีม Dev และ QA",
            "ใช้ RICE กับงานแก้บั๊กเล็กๆ รายวันจนเสียเวลาเกินจำเป็น",
            "นำคะแนนดิบมาตัดสินใจโดยไม่ดู Strategic Alignment อื่นๆ"
        ],
        "focus_quote": "RICE ช่วยเปลี่ยนการถกเถียงในที่ประชุมให้เป็นการวิเคราะห์บนพื้นฐานของข้อมูลและตรรกะที่แท้จริง",
        "key_takeaway": "RICE Score = (Reach x Impact x Confidence) ÷ Effort ➔ ฟีเจอร์ที่เข้าถึงคนเยอะ ผลกระทบสูง มั่นใจ และใช้แรงน้อย คือสิ่งที่ต้องทำก่อน"
    }
]

print(f"Loaded full high-grade specifications for {len(ALL_DOCS)} files. Generating remaining specifications...")

# For the rest of documents (13 to 30), let's ensure they are fully populated in ALL_DOCS
REMAINING_SPECS = [
    # 13. roadmap.md
    {
        "file_rel": "roadmap.md",
        "output_name": "13_Product_Roadmap",
        "top_note_title": "ROADMAP GUIDE", "top_note_sub": "PRODUCT STRATEGY",
        "title_plain": "Roadmap ต่างจาก Timeline อย่างไร ?",
        "title_html": "Roadmap <span class=\"blue-highlight\">ต่างจาก Timeline</span> <span class=\"red-highlight\">อย่างไร ?</span>",
        "subtitle_html": "Roadmap คือ <strong>\"ทิศทางและผลลัพธ์\"</strong> ส่วน Timeline คือตารางเวลาปฏิบัติการ",
        "notepad_header": "Roadmap vs Timeline",
        "notepad_items": [
            "Roadmap = Outcome-based (มุ่งเน้นผลลัพธ์)",
            "Timeline = Output-based (มุ่งเน้นส่งมอบ)",
            "Roadmap ยืดหยุ่นปรับตัวได้",
            "Timeline มีวันที่ล็อกแน่นอน",
            "ใช้ร่วมกันเพื่อความสำเร็จ"
        ],
        "strategy_title": "🎯 1. OUTCOME-BASED ROADMAP : วิสัยทัศน์ที่นำทางทีม",
        "strategy_bullets": [
            "Roadmap ตอบคำถามว่า : เรากำลังมุ่งหน้าไปไหน? เราแก้ปัญหาอะไรให้ผู้ใช้? และทำไมเรื่องนี้ถึงสำคัญ?",
            "โครงสร้าง Now / Next / Later ช่วยให้ทีมมีโฟกัสที่ชัดเจนในปัจจุบัน โดยไม่ผูกมัดวันส่งมอบระยะยาวเกินจริง",
            "เชื่อมโยงเป้าหมายทางธุรกิจ (OKRs) เข้ากับธีมการพัฒนาอย่างเป็นรูปธรรม",
            "สื่อสารให้ Stakeholder เข้าใจภาพรวมและทิศทางการเติบโตของ Product"
        ],
        "cloud_bubble_html": "🧭 <strong>Vision & Strategy</strong><br>Roadmap ที่ดีต้องบอกทิศทางและแรงบันดาลใจ ไม่ใช่เอา Gantt Chart รายวันมาเปลี่ยนชื่อ",
        "execution_label": "ROADMAP FRAMEWORK : 6 องค์ประกอบของ Roadmap ที่ยอดเยี่ยม",
        "columns": [
            {"title": "PRODUCT VISION", "char": "po", "items": ["ทิศทางระยะยาว", "กลุ่มลูกค้าเป้าหมาย", "Value Proposition", "ความได้เปรียบทางธุรกิจ"]},
            {"title": "STRATEGIC THEMES", "char": "presenter", "items": ["จัดกลุ่มตามปัญหา", "เช่น User Retention", "เช่น ชำระเงินเร็วขึ้น", "Outcome Goals"]},
            {"title": "NOW (CURRENT)", "char": "dev", "items": ["กำลังทำใน Sprint", "ความชัดเจน 100%", "มี Spec & UI ครบ", "Commitment สูง"]},
            {"title": "NEXT (NEAR-TERM)", "char": "ba", "items": ["จะทำใน 1-3 เดือน", "กำลังค้นคว้า & Refine", "ความชัดเจนปานกลาง", "เตรียมความพร้อม"]},
            {"title": "LATER (FUTURE)", "char": "flow", "items": ["วิสัยทัศน์ในอนาคต", "ปรับเปลี่ยนได้ตลอด", "ไอเดียระดับกว้าง", "รอผลตอบรับตลาด"]},
            {"title": "SUCCESS METRICS", "char": "qa", "items": ["ตัวชี้วัดความสำเร็จ", "OKRs / KPIs", "User Adoption Rate", "Revenue Growth"]}
        ],
        "bottom_left_title": "โครงสร้าง Now / Next / Later",
        "skills": [
            {"type": "x", "title": "Now (ความชัดเจนสูงมาก)", "code": "Now Phase", "desc": "งานที่กำลังอยู่ในกระบวนการพัฒนา มีขอบเขตและแผนการส่งมอบที่แน่นอน"},
            {"type": "t", "title": "Next (ความชัดเจนปานกลาง)", "code": "Next Phase", "desc": "งานที่ผ่านการคัดเลือกแล้ว กำลังอยู่ในขั้นตอนการทำ Research และออกแบบ"},
            {"type": "i", "title": "Later (ความชัดเจนยืดหยุ่น)", "code": "Later Phase", "desc": "ทิศทางระยะยาวที่พร้อมปรับเปลี่ยนตามการเปลี่ยนแปลงของตลาดและผู้ใช้"}
        ],
        "bottom_center_title": "วงจรการปรับปรุง Roadmap",
        "loop_data": {
            "s1_title": "1. SET PRODUCT GOAL", "s1_sub": "🎯 กำหนดเป้าหมาย",
            "s2_title": "2. GROUP THEMES", "s2_sub": "🗂️ จัดหมวดหมู่ Outcome",
            "s3_title": "3. MAP NOW/NEXT/LATER", "s3_sub": "🗺️ วางไทม์ไลน์ยืดหยุ่น",
            "s4_title": "4. REVIEW & PIVOT", "s4_sub": "🔄 ทบทวนรายไตรมาส",
            "center_t1": "STRATEGIC", "center_t2": "DIRECTION"
        },
        "bottom_right_title": "หลุมพรางในการทำ Roadmap",
        "focus_items": [
            "เอา Gantt Chart รายวันมาเรียกว่าเป็น Product Roadmap",
            "สัญญาวันปล่อยฟีเจอร์ล่วงหน้า 1 ปี ทั้งที่ยังไม่รู้รายละเอียด",
            "ใส่รายชื่อฟีเจอร์อัดแน่นโดยไม่ระบุผลลัพธ์ทางธุรกิจ",
            "ไม่เคยทบทวนหรืออัปเดต Roadmap เลยตลอดทั้งปี"
        ],
        "focus_quote": "Roadmap ที่ล็อกตายตัวคือศัตรูตัวร้ายของความคล่องตัวในยุคดิจิทัล",
        "key_takeaway": "Roadmap = นำทิศทาง (Outcome) | Timeline = ลงตารางเวลา (Output) ➔ ใช้ Roadmap นำทาง และใช้ Timeline บริหารการส่งมอบ"
    },

    # 14. Scope-Creep.md
    {
        "file_rel": "Scope-Creep.md",
        "output_name": "14_Scope_Creep",
        "top_note_title": "SCOPE GOVERNANCE", "top_note_sub": "CHANGE CONTROL",
        "title_plain": "Scope Creep ปัญหางานบวม แก้อย่างไร ?",
        "title_html": "Scope Creep <span class=\"blue-highlight\">ปัญหางานบวม</span> <span class=\"red-highlight\">แก้อย่างไร ?</span>",
        "subtitle_html": "ควบคุมขอบเขตงานให้อยู่ในร่องในรอย <strong>\"ส่งงานตรงเวลา โดยทีมไม่ Burnout\"</strong>",
        "notepad_header": "สาเหตุ Scope บวม",
        "notepad_items": [
            "Out of Scope ไม่ชัดเจน",
            "User นึกเพิ่มตอนเห็นของจริง",
            "ทีมเกรงใจรับปากปากเปล่า",
            "ขาดระบบ Change Request",
            "ไม่ประเมินผลกระทบก่อนรับงาน"
        ],
        "strategy_title": "🎯 1. SCOPE MANAGEMENT : ควบคุมขอบเขตอย่างเป็นระบบ",
        "strategy_bullets": [
            "Scope Creep คือการที่งานขยายตัวเพิ่มขึ้นเรื่อยๆ โดยไม่มีการเพิ่มเวลา งบประมาณ หรือทรัพยากร",
            "ส่งผลให้ทีมต้องทำงานล่วงเวลา คุณภาพระบบลดลง และเสี่ยงส่งมอบงานไม่ทันตามกำหนด",
            "ต้องมีขั้นตอน Change Control Process ที่โปร่งใสและตกลงร่วมกันตั้งแต่เริ่มโครงการ",
            "การปฏิเสธอย่างมีเหตุผลและเสนอทางเลือก คือความเป็นมืออาชีพที่แท้จริง"
        ],
        "cloud_bubble_html": "🛑 <strong>Protect Team Focus</strong><br>การรับงานแทรกโดยไม่ตัดงานเก่าออก เปรียบเสมือนการเติมน้ำใส่แก้วที่เต็มแล้ว มีแต่จะพังทลาย",
        "execution_label": "CHANGE CONTROL PROCESS : 6 ขั้นตอนรับมือเมื่อมีงานงอก",
        "columns": [
            {"title": "1. LISTEN & LOG", "char": "po", "items": ["รับฟังความต้องการ", "เข้าใจ Pain Point จริง", "บันทึกลงระบบ CR", "ไม่รับปากทันที"]},
            {"title": "2. IMPACT ANALYSIS", "char": "ba", "items": ["ประเมินผลต่องบ/เวลา", "เช็กผลกระทบระบบเดิม", "คำนวณ Effort ร่วมกับ Dev", "เช็กผลต่อ Sprint Goal"]},
            {"title": "3. TRADE-OFF OFFER", "char": "presenter", "items": ["เสนอทางเลือก A / B", "Option A: รอ Sprint หน้า", "Option B: Swap งานออก", "Option C: เพิ่มงบ/เวลา"]},
            {"title": "4. STAKEHOLDER DECIDE", "char": "flow", "items": ["ให้ลูกค้าเป็นคนเลือก", "อธิบายผลกระทบชัดเจน", "เคารพการตัดสินใจ", "ไม่มีการบังคับ"]},
            {"title": "5. FORMAL APPROVAL", "char": "dev", "items": ["ลงนามอนุมัติ CR", "อัปเดต Baseline Scope", "ปรับตารางเวลาใหม่", "แจ้งทุกคนในทีม"]},
            {"title": "6. SPRINT ADJUST", "char": "qa", "items": ["ปรับการ์ดใน Backlog", "อัปเดต Test Scenarios", "รักษาคุณภาพการเทส", "ดำเนินงานตามแผนใหม่"]}
        ],
        "bottom_left_title": "กลยุทธ์การรับมือคำของานเพิ่ม",
        "skills": [
            {"type": "x", "title": "กลยุทธ์สลับงาน (Swap Strategy)", "code": "Swap Scope", "desc": "หากต้องการงานใหม่ด่วน ต้องยอมถอดงานเดิมที่มี Effort เท่ากันออกจาก Sprint"},
            {"type": "t", "title": "กลยุทธ์เข้าคิว (Backlog Strategy)", "code": "Next Sprint", "desc": "รับโจทย์ไว้และนำไปจัด Prioritize เพื่อทำใน Sprint ถัดไปอย่างมีคุณภาพ"},
            {"type": "i", "title": "กลยุทธ์ขยายทรัพยากร (Resource Strategy)", "code": "Add Budget/Time", "desc": "หากเป็นงานด่วนและไม่ยอมตัดงานเดิม ต้องขยายเวลาส่งมอบหรือเพิ่มงบประมาณ"}
        ],
        "bottom_center_title": "วงจรการจัดการ Change Request",
        "loop_data": {
            "s1_title": "1. REQUEST RECEIVED", "s1_sub": "📥 รับคำขอใหม่",
            "s2_title": "2. ASSESS IMPACT", "s2_sub": "🔍 ประเมินเวลา & ทุน",
            "s3_title": "3. PROPOSE TRADE-OFF", "s3_sub": "⚖️ เสนอทางเลือกสลับงาน",
            "s4_title": "4. SIGN-OFF & UPDATE", "s4_sub": "📝 อนุมัติและอัปเดตแผน",
            "center_t1": "ZERO", "center_t2": "SCOPE CREEP"
        },
        "bottom_right_title": "คำพูดอันตรายที่ต้องระวัง",
        "focus_items": [
            "⚠️ 'นิดเดียวเอง เพิ่มปุ่มนี้ให้หน่อยนะ'",
            "⚠️ 'ไหนๆ ก็เขียนหน้านี้แล้ว ขอเพิ่มอีก 3 ฟิลด์นะ'",
            "⚠️ 'อันนี้ง่ายๆ น่าจะใช้เวลาแค่ 5 นาที'",
            "⚠️ 'คิดว่าระบบควรจะมีอันนี้อยู่แล้วนะ'"
        ],
        "focus_quote": "การปฏิเสธอย่างมืออาชีพไม่ใช่การบอกว่า 'ทำไม่ได้' แต่คือการบอกว่า 'ทำได้เมื่อไหร่ และต้องแลกด้วยอะไร'",
        "key_takeaway": "คุม Scope อยู่หมัด = นิยาม Out-of-Scope ชัด + ใช้ระบบ Change Request + เสนอ Trade-off + บันทึกลงระบบทุกครั้ง"
    },

    # 15. sprint.md
    {
        "file_rel": "sprint.md",
        "output_name": "15_Sprint_Execution",
        "top_note_title": "SPRINT EXECUTION", "top_note_sub": "DELIVERY CADENCE",
        "title_plain": "Sprint ใน Agile ทำงานอย่างไรให้เกิดผลจริง ?",
        "title_html": "Sprint ใน Agile <span class=\"blue-highlight\">ทำงานอย่างไร</span> <span class=\"red-highlight\">ให้เกิดผลจริง ?</span>",
        "subtitle_html": "รอบการทำงานสั้นๆ ที่ส่งมอบ <strong>\"ชิ้นงานที่ใช้งานได้จริง (Shippable Increment)\"</strong> สม่ำเสมอ",
        "notepad_header": "Sprint Foundations",
        "notepad_items": [
            "Time-box คงที่ 1-2 สัปดาห์",
            "Sprint Goal นิ่ง ไม่เปลี่ยนกลางคัน",
            "ทำงานร่วมกันแบบ Cross-functional",
            "ผ่านเกณฑ์ Definition of Done 100%",
            "รักษาความเร็วที่ยั่งยืน"
        ],
        "strategy_title": "🎯 1. THE SPRINT HEARTBEAT : จังหวะการเต้นของทีม Agile",
        "strategy_bullets": [
            "Sprint คือกรอบเวลาคงที่ (Time-box) ที่ทีมมีสมาธิโฟกัสกับเป้าหมายเดียวที่ตกลงร่วมกัน",
            "ผลลัพธ์ตอนจบ Sprint ต้องเป็นชิ้นงานที่ผ่านการทดสอบและพร้อมใช้งานได้จริง (Potentially Shippable)",
            "ช่วยให้ได้รับ Feedback จากผู้ใช้และตลาดอย่างรวดเร็วเพื่อนำมาปรับทิศทางในรอบถัดไป",
            "ช่วยลดความเสี่ยงจากการพัฒนาโครงการยาวนานหลายเดือนโดยไม่มีการตรวจสอบ"
        ],
        "cloud_bubble_html": "🏃 <strong>Sustainable Pace</strong><br>Sprint ไม่ใช่การวิ่งแข่งสปีด 100 เมตร แต่คือการวิ่งมาราธอนที่รักษาระดับความเร็วได้อย่างสม่ำเสมอ",
        "execution_label": "SPRINT CADENCE : 6 สเต็ปตลอดวงจร 1 Sprint",
        "columns": [
            {"title": "1. PLANNING", "char": "presenter", "items": ["กำหนด Sprint Goal", "เลือกงานเข้า Sprint", "ประเมิน Capacity", "Commitment ร่วมกัน"]},
            {"title": "2. DAILY SYNC", "char": "dev", "items": ["ยืนคุย 15 นาทีทุกวัน", "อัปเดตงานบน Board", "แจ้งปัญหาทันที", "เคลียร์บล็อกเกอร์"]},
            {"title": "3. BUILD & PAIR", "char": "flow", "items": ["เขียน Clean Code", "Pair Programming", "Unit Test 100%", "Code Review เข้มงวด"]},
            {"title": "4. TEST & QA", "char": "qa", "items": ["Functional Testing", "Integration Testing", "ดักจับ Regression", "ผ่านเกณฑ์ DoD"]},
            {"title": "5. SPRINT REVIEW", "char": "po", "items": ["Demo ชิ้นงานจริง", "Stakeholder ร่วมฟัง", "รับ Feedback ตลาด", "ปรับ Backlog ต่อ"]},
            {"title": "6. RETROSPECTIVE", "char": "ba", "items": ["ทบทวนทีมเวิร์ก", "จุดแข็งที่ต้องรักษา", "จุดที่ต้องปรับปรุง", "Action Items ชัดเจน"]}
        ],
        "bottom_left_title": "เสาหลักแห่งความสำเร็จใน Sprint",
        "skills": [
            {"type": "x", "title": "Sprint Goal (เป้าหมายหนึ่งเดียว)", "code": "Sprint Goal", "desc": "เหตุผลสำคัญว่าทำไมเราถึงต้องทำ Sprint นี้ เพื่อให้ทีมมีโฟกัสร่วมกัน"},
            {"type": "t", "title": "Capacity & Commitment (ความพร้อมจริง)", "code": "Capacity", "desc": "คำนวณวันลา วันหยุด และแรงงานจริงก่อน Commit งานเข้าสู่กระบวนการ"},
            {"type": "i", "title": "Definition of Done (มาตรฐานความเสร็จ)", "code": "DoD Gate", "desc": "โค้ดผ่าน, เทสผ่าน, ผ่าน Code Review, และ Deploy บน Staging สำเร็จ"}
        ],
        "bottom_center_title": "วงจรการดำเนินงานใน 1 Sprint",
        "loop_data": {
            "s1_title": "DAY 1 : PLANNING", "s1_sub": "🎯 วางแผน & ล็อก Goal",
            "s2_title": "DAY 2-8 : BUILD & DAILY", "s2_sub": "💻 โค้ด เทส และซิงก์",
            "s3_title": "DAY 9 : REVIEW DEMO", "s3_sub": "✨ โชว์งานรับ Feedback",
            "s4_title": "DAY 10 : RETROSPECTIVE", "s4_sub": "🔧 ปรับปรุงทีมเวิร์ก",
            "center_t1": "SHIPPABLE", "center_t2": "PRODUCT"
        },
        "bottom_right_title": "ข้อห้ามระหว่างดำเนิน Sprint",
        "focus_items": [
            "เปลี่ยน Sprint Goal หรือเพิ่มงานแทรกโดยไม่ตัดงานเก่าออก",
            "ปล่อยให้มีคนแอบสั่งงาน Dev นอกรอบโดยไม่ผ่าน PO",
            "ตัดขั้นตอนการทำ Automated Test หรือ QA เพื่อเร่งงาน",
            "ไม่ยอมยกมือบอกปัญหาใน Daily Scrum จนถึงวันสุดท้าย"
        ],
        "focus_quote": "Sprint ที่มีประสิทธิภาพช่วยลดความเครียดของทีม และส่งมอบสิ่งที่มีคุณค่าให้แก่ลูกค้าอย่างต่อเนื่อง",
        "key_takeaway": "Sprint สำเร็จ = ล็อก Sprint Goal + โฟกัสสร้างงานจริง + ซิงก์รายวัน + DoD ผ่าน 100% + ปรับปรุงทีมทุกรอบ"
    }
]

# Append the remaining specs to ALL_DOCS
ALL_DOCS.extend(REMAINING_SPECS)

# Let's add specifications for remaining files (16 to 30)
ADDITIONAL_SPECS = [
    # 16. test case.md
    {
        "file_rel": "test case.md",
        "output_name": "16_Test_Case_vs_AC",
        "top_note_title": "QA QUALITY SUITE", "top_note_sub": "TEST DESIGN GUIDE",
        "title_plain": "Test Case กับ Acceptance Criteria ต่างกันยังไง ?",
        "title_html": "Test Case กับ AC <span class=\"blue-highlight\">ต่างกันยังไง</span> <span class=\"red-highlight\">&amp; ออกแบบอย่างไร ?</span>",
        "subtitle_html": "AC บอกเงื่อนไขความสำเร็จภาพรวม <strong>\"Test Case บอกขั้นตอนตรวจรับอย่างละเอียด\"</strong>",
        "notepad_header": "AC vs Test Case",
        "notepad_items": [
            "AC = ภาษาธุรกิจ (Business Level)",
            "Test Case = ภาษาเทคนิค (Step-by-Step)",
            "1 AC แตกได้หลาย Test Cases",
            "ครอบคลุม Happy & Bad Path",
            "การันตีคุณภาพก่อนส่งมอบ"
        ],
        "strategy_title": "🎯 1. THE TEST HIERARCHY : จากความต้องการสู่เคสทดสอบ",
        "strategy_bullets": [
            "Acceptance Criteria (AC) : เขียนโดย PO/BA ระบุเงื่อนไขความสำเร็จระดับฟังก์ชันเพื่อตอบโจทย์ผู้ใช้",
            "Test Case : เขียนโดย QA ระบุขั้นตอนการคลิก (Steps), ข้อมูลที่ต้องกรอก (Data), และผลลัพธ์ที่คาดหวัง (Expected Result)",
            "1 User Story มักประกอบด้วย 3-5 AC และสามารถแตกเป็น Test Cases ได้ 10-20 เคสเพื่อความครอบคลุม",
            "ช่วยให้สามารถทำ Automated Test และ Regression Test ได้อย่างมีประสิทธิภาพ"
        ],
        "cloud_bubble_html": "🔍 <strong>Quality Magnifier</strong><br>AC ชี้เป้าหมายว่าต้องถึงไหน ส่วน Test Case คือแว่นขยายที่คอยตรวจสอบทุกย่างก้าวเพื่อไม่ให้มีบั๊กหลุดรอด",
        "execution_label": "TEST CASE STRUCTURE : 6 ส่วนประกอบของ Test Case ที่ดี",
        "columns": [
            {"title": "TEST ID & TITLE", "char": "qa", "items": ["รหัสอ้างอิงชัดเจน", "ชื่อสื่อความหมาย", "ผูกกับ User Story ID", "จัดตาม Priority"]},
            {"title": "PRE-CONDITION", "char": "ba", "items": ["สถานะตั้งต้นของระบบ", "สิทธิ์ผู้ใช้ที่ล็อกอิน", "ข้อมูลที่ต้องมีใน DB", "การตั้งค่าระบบ"]},
            {"title": "TEST STEPS", "char": "flow", "items": ["ขั้นตอน 1, 2, 3 ชัดเจน", "ระบุปุ่มและหน้าที่คลิก", "ใครมาอ่านก็ทำตามได้", "ไม่มีขั้นตอนคลุมเครือ"]},
            {"title": "TEST DATA", "char": "dev", "items": ["ข้อมูลตัวอย่างที่ใช้กรอก", "Username / Password", "ยอดเงิน / วันที่", "เคสข้อมูลผิดปกติ"]},
            {"title": "EXPECTED RESULT", "char": "designer", "items": ["ผลลัพธ์ที่ระบบต้องแสดง", "ข้อความแจ้งเตือนที่ขึ้น", "การเปลี่ยนสถานะใน DB", "Response API"]},
            {"title": "STATUS & LOGS", "char": "presenter", "items": ["Pass / Fail / Blocked", "แนบ Screenshot / Video", "บันทึก Defect ID", "วันเวลาที่ทดสอบ"]}
        ],
        "bottom_left_title": "ประเภทของ Test Cases ที่ต้องครอบคลุม",
        "skills": [
            {"type": "x", "title": "Positive Testing (Happy Path)", "code": "Happy Path", "desc": "ทดสอบการใช้งานปกติเมื่อผู้ใช้กรอกข้อมูลถูกต้องครบถ้วน ระบบต้องทำงานสำเร็จ"},
            {"type": "t", "title": "Negative Testing (Error Path)", "code": "Error Handling", "desc": "ทดสอบเมื่อผู้ใช้กรอกข้อมูลผิด ปล่อยว่าง หรือเน็ตหลุด ระบบต้องแจ้งเตือนถูกต้อง"},
            {"type": "i", "title": "Boundary & Edge Testing", "code": "Edge Cases", "desc": "ทดสอบค่าสูงสุด-ต่ำสุด อัปโหลดไฟล์ใหญ่เกิน หรือกดปุ่มซ้ำรัวๆ ระบบต้องไม่พัง"}
        ],
        "bottom_center_title": "วงจรการพัฒนา Test Cases",
        "loop_data": {
            "s1_title": "1. ANALYZE AC & STORY", "s1_sub": "📖 วิเคราะห์เงื่อนไข AC",
            "s2_title": "2. DESIGN TEST CASES", "s2_sub": "✍️ ออกแบบเคสครอบคลุม",
            "s3_title": "3. EXECUTE & LOG BUG", "s3_sub": "🧪 ทดสอบจริง & แจ้งบั๊ก",
            "s4_title": "4. RETEST & SIGN-OFF", "s4_sub": "✅ ตรวจซ้ำ & อนุมัติผ่าน",
            "center_t1": "ZERO", "center_t2": "DEFECTS"
        },
        "bottom_right_title": "ข้อผิดพลาดที่พบบ่อยในการเขียน Test Case",
        "focus_items": [
            "เขียน Test Step กว้างๆ เช่น 'ทดสอบว่าล็อกอินได้' โดยไม่บอกวิธีทำ",
            "ไม่มีการเตรียม Test Data ไว้ล่วงหน้า ทำให้เสียเวลาหาข้อมูล",
            "ทดสอบเฉพาะกรณีปกติ (Happy Path) แล้วละเลย Error Handling",
            "ไม่อัปเดต Test Case เมื่อ Requirement มีการเปลี่ยนแปลง"
        ],
        "focus_quote": "Test Case ที่ดีคือ Test Case ที่ใครมาอ่านก็สามารถทดสอบตามและได้ผลลัพธ์ที่ถูกต้องตรงกันเสมอ",
        "key_takeaway": "AC = เกณฑ์ผ่านภาพรวม | Test Case = ขั้นตอนเทสทีละสเต็ป ➔ ดักครบทั้ง Happy, Negative และ Edge Cases"
    },

    # 17. UAT.md
    {
        "file_rel": "UAT.md",
        "output_name": "17_UAT_Preparation",
        "top_note_title": "UAT READINESS", "top_note_sub": "USER ACCEPTANCE TESTING",
        "title_plain": "UAT คืออะไร ? เตรียมตัวอย่างไรก่อน Go-Live ?",
        "title_html": "UAT คืออะไร ? <span class=\"blue-highlight\">เตรียมตัวอย่างไร</span> <span class=\"red-highlight\">ก่อน Go-Live ?</span>",
        "subtitle_html": "ด่านทดสอบสุดท้ายโดยผู้ใช้งานจริง <strong>\"เพื่อยืนยันว่าระบบตอบโจทย์ธุรกิจ\"</strong>",
        "notepad_header": "หัวใจสำคัญของ UAT",
        "notepad_items": [
            "ทดสอบโดย User และ Business ตัวจริง",
            "ทดสอบบน Flow การทำงานจริง",
            "ด่านสุดท้ายก่อนเปิดใช้งาน (Go-Live)",
            "แยกบั๊ก (Defect) ออกจากคำขอใหม่ (CR)",
            "ลงนาม Sign-off อนุมัติรับมอบงาน"
        ],
        "strategy_title": "🎯 1. USER ACCEPTANCE TESTING : การตรวจรับมอบระบบ",
        "strategy_bullets": [
            "UAT ไม่ใช่การเทสหาบั๊กเทคนิคทั่วไป แต่เป็นการยืนยันว่า 'ระบบทำงานได้ตรงตามกระบวนการของธุรกิจจริง'",
            "ดำเนินการโดยตัวแทนผู้ใช้งานจริง (End Users) และเจ้าของธุรกิจ (Business Owners)",
            "ทดสอบบนสภาพแวดล้อมเสมือนจริง (UAT / Staging Environment) พร้อมข้อมูลจำลองที่สมบูรณ์",
            "ผลลัพธ์ของ UAT คือเอกสาร Sign-off เพื่ออนุมัติการเปิดใช้งานระบบจริง (Go-Live Approval)"
        ],
        "cloud_bubble_html": "🚀 <strong>Final Gate to Go-Live</strong><br>UAT ที่ประสบความสำเร็จช่วยสร้างความมั่นใจสูงสุดแก่องค์กร ทำให้การเปลี่ยนผ่านระบบเป็นไปอย่างราบรื่น",
        "execution_label": "UAT READINESS PLAYBOOK : 6 สิ่งที่ต้องเตรียมให้พร้อม",
        "columns": [
            {"title": "1. UAT SCENARIOS", "char": "ba", "items": ["โจทย์ตาม Flow จริง", "ครอบคลุมทุกแผนก", "ไม่ใช่แค่รายปุ่ม", "มีลำดับการส่งต่องาน"]},
            {"title": "2. TEST DATA & ACCOUNTS", "char": "po", "items": ["บัญชีทดสอบทุก Role", "Master Data ครบถ้วน", "จำลองเคสจริงในอดีต", "ข้อมูลไม่ปนระบบจริง"]},
            {"title": "3. ENVIRONMENT", "char": "dev", "items": ["UAT Server เสถียร", "เชื่อมโยง API ครบ", "Data Migration พร้อม", "Performance รองรับ"]},
            {"title": "4. BRIEF & TRAINING", "char": "presenter", "items": ["จัด Kick-off บรีฟ User", "แจกคู่มือการทดสอบ", "แนะนำวิธีการบันทึกผล", "มีทีมซัพพอร์ตใกล้ชิด"]},
            {"title": "5. DEFECT TRIAGE", "char": "qa", "items": ["จัดระดับความรุนแรง", "Critical / High ต้องแก้", "แยก Defect vs CR", "Daily Defect Sync"]},
            {"title": "6. SIGN-OFF GATE", "char": "flow", "items": ["บั๊ก Critical = 0", "User ยอมรับระบบ", "ลงนามเอกสารรับมอบ", "อนุมัติ Go-Live"]}
        ],
        "bottom_left_title": "การจัดการ Issue ในช่วง UAT (Defect vs CR)",
        "skills": [
            {"type": "x", "title": "Defect (บั๊กระบบ)", "code": "Defect / Bug", "desc": "ระบบทำงานไม่ตรงตาม Requirement หรือ AC ที่ตกลงไว้ ➔ ทีม Dev ต้องแก้ไขทันที"},
            {"type": "t", "title": "Change Request (คำขอใหม่)", "code": "New Feature / CR", "desc": "User เพิ่งนึกอยากได้เพิ่ม หรือขอนอกเหนือจาก Scope เดิม ➔ นำเข้า Backlog รอบถัดไป"},
            {"type": "i", "title": "User Mistake (ความเข้าใจผิด)", "code": "Training Issue", "desc": "ระบบทำงานถูกต้องแต่ User ใช้งานไม่เป็น ➔ ให้คำแนะนำและปรับปรุงคู่มือ"}
        ],
        "bottom_center_title": "ขั้นตอนกระบวนการ UAT",
        "loop_data": {
            "s1_title": "1. KICK-OFF & BRIEF", "s1_sub": "📢 บรีฟขั้นตอน & โจทย์",
            "s2_title": "2. USER EXECUTION", "s2_sub": "🧪 User ลงมือทดสอบจริง",
            "s3_title": "3. LOG & FIX DEFECTS", "s3_sub": "🔧 เคลียร์บั๊ก Critical",
            "s4_title": "4. RETEST & SIGN-OFF", "s4_sub": "📝 ลงนามอนุมัติ Go-Live",
            "center_t1": "CONFIDENT", "center_t2": "GO-LIVE"
        },
        "bottom_right_title": "ข้อควรระวังในการทำ UAT",
        "focus_items": [
            "User เข้าใจผิดว่า UAT คือช่วงเวลาสั่งเพิ่มฟีเจอร์ใหม่ตามใจชอบ",
            "ไม่ได้เตรียมข้อมูล Master Data ไว้ล่วงหน้าทำให้ User ติดขัด",
            "ไม่มีเกณฑ์ Sign-off ที่ชัดเจน ทำให้ไม่สามารถปิดจบ UAT ได้",
            "ปล่อยให้ User ทดสอบตามลำพังโดยไม่มีทีมงานคอยช่วยเหลือ"
        ],
        "focus_quote": "UAT คือการซ้อมใหญ่ของธุรกิจ ยิ่งทดสอบสมจริงเท่าไหร่ วันเปิดตัวจริงก็ยิ่งไร้กังวล",
        "key_takeaway": "UAT สำเร็จ = เตรียม Scenario ครบ + ข้อมูลพร้อม + User เทสจริง + เคลียร์บั๊ก Critical + Sign-off Go-Live"
    },

    # 18. User Story.md
    {
        "file_rel": "User Story.md",
        "output_name": "18_User_Story_Mastery",
        "top_note_title": "USER STORY MASTER", "top_note_sub": "INVEST & 3Cs MODEL",
        "title_plain": "User Story เขียนยังไงให้ทรงพลัง ?",
        "title_html": "User Story <span class=\"blue-highlight\">เขียนยังไง</span> <span class=\"red-highlight\">ให้ทรงพลัง ?</span>",
        "subtitle_html": "อธิบายความต้องการจากมุมมองของผู้ใช้ พร้อมมอบคุณค่าที่แท้จริง",
        "notepad_header": "หลักการ INVEST",
        "notepad_items": [
            "<strong>I</strong>ndependent : อิสระต่อกัน",
            "<strong>N</strong>egotiable : ต่อรองปรับเปลี่ยนได้",
            "<strong>V</strong>aluable : มีคุณค่าชัดเจน",
            "<strong>E</strong>stimable : ประเมินแรงงานได้",
            "<strong>S</strong>mall & <strong>T</strong>estable",
            "3Cs : Card, Convo, Confirm"
        ],
        "strategy_title": "🎯 1. THE USER STORY TEMPLATE : โครงสร้างมาตรฐานสากล",
        "strategy_bullets": [
            "As a [Persona / Role] : ในฐานะของผู้ใช้งานกลุ่มใด (ระบุให้เฉพาะเจาะจง)",
            "I want to [Action / Feature] : ฉันต้องการทำสิ่งใด หรือต้องการความสามารถอะไรในระบบ",
            "So that [Benefit / Value] : เพื่อให้ฉันได้รับคุณค่า ประโยชน์ หรือแก้ปัญหาอะไรได้",
            "เน้น 'ทำไมและได้อะไร' มากกว่าการสั่งวิธีการทางเทคนิค"
        ],
        "cloud_bubble_html": "💡 <strong>Invitation to Conversation</strong><br>User Story ไม่ใช่สเปกสำเร็จรูป แต่เป็นคำเชิญให้ทีมมาร่วมพูดคุยและหา Solution ที่ดีที่สุดร่วมกัน",
        "execution_label": "THE 3Cs FRAMEWORK : 3 เสาหลักของ User Story ที่สมบูรณ์",
        "columns": [
            {"title": "1. CARD (สรุปย่อ)", "char": "po", "items": ["As a...", "I want to...", "So that...", "ขนาดสั้นกระชับ"]},
            {"title": "2. CONVERSATION", "char": "ba", "items": ["พูดคุยซักถาม", "ทำความเข้าใจโจทย์", "แชร์มุมมอง Dev/QA", "ค้นหาทางออกที่ดีสุด"]},
            {"title": "3. CONFIRMATION", "char": "qa", "items": ["Acceptance Criteria", "Given/When/Then", "เกณฑ์การตรวจรับ", "DoD Definition"]},
            {"title": "4. VALUE FOCUS", "char": "presenter", "items": ["ไม่ลืมส่วน So that", "สร้างผลลัพธ์ธุรกิจ", "แก้ Pain Point จริง", "วัดผลเป็นรูปธรรม"]},
            {"title": "5. SMALL SLICE", "char": "flow", "items": ["ขนาดพอดี 1 Sprint", "แตก Story ย่อย", "ส่งมอบได้เร็ว", "ไม่เป็น Epic ยักษ์"]},
            {"title": "6. READY TO BUILD", "char": "dev", "items": ["ผ่านเกณฑ์ DoR", "มี Wireframe แนบ", "ประเมิน Points แล้ว", "พร้อมหยิบเข้า Sprint"]}
        ],
        "bottom_left_title": "เปรียบเทียบตัวอย่างที่ดี vs ตัวอย่างที่ไม่ดี",
        "skills": [
            {"type": "x", "title": "ตัวอย่างที่ดี (User & Value Focus)", "code": "Good Story", "desc": "'ในฐานะผู้จัดการฝ่ายขาย ฉันต้องการดูรายงานยอดขายรายวัน เพื่อปรับกลยุทธ์ทีมได้ทันเวลา'"},
            {"type": "t", "title": "ตัวอย่างที่ไม่ดี (Technical / ไม่มี Value)", "code": "Bad Story", "desc": "'สร้างตาราง SQL สำหรับเก็บข้อมูลยอดขาย' หรือ 'ทำหน้ารายงานให้สวยๆ' (ไม่บอกว่าใครใช้และทำไปทำไม)"},
            {"type": "i", "title": "การเขียน AC แนบท้าย Story", "code": "Confirmation", "desc": "Given มียอดขายในระบบ When เลือกช่วงวันที่ แล้วกดดู Then ต้องแสดงกราฟและตารางสรุปยอด"}
        ],
        "bottom_center_title": "กระบวนการสร้างสรรค์ User Story",
        "loop_data": {
            "s1_title": "1. USER RESEARCH", "s1_sub": "🔍 ศึกษาปัญหาผู้ใช้",
            "s2_title": "2. WRITE CARD (INVEST)", "s2_sub": "✍️ ร่าง Story สั้นกระชับ",
            "s3_title": "3. TEAM CONVERSATION", "s3_sub": "🗣️ พูดคุยตกผลึกร่วมกัน",
            "s4_title": "4. ADD CONFIRMATION (AC)", "s4_sub": "✅ ล็อกเกณฑ์ความสำเร็จ",
            "center_t1": "USER-CENTRIC", "center_t2": "VALUE"
        },
        "bottom_right_title": "ข้อผิดพลาดที่พบบ่อยในการเขียน User Story",
        "focus_items": [
            "เขียนเป็น Technical Task แทนที่จะเขียนจากมุมมองของผู้ใช้",
            "ละเลยส่วน 'So that' ทำให้ทีมไม่รู้ว่าสร้างฟีเจอร์นี้ไปเพื่ออะไร",
            "Story ใหญ่เกินไปจนไม่สามารถทำให้เสร็จภายใน 1 Sprint ได้",
            "ไม่มี Acceptance Criteria แนบมาด้วย ทำให้ตรวจรับงานไม่ได้"
        ],
        "focus_quote": "User Story ที่ยอดเยี่ยมช่วยเชื่อมต่อใจของผู้ใช้เข้ากับโค้ดของทีม ทำให้ทุกฟีเจอร์มีความหมาย",
        "key_takeaway": "User Story ที่ทรงพลัง = ใคร (As a) + ทำอะไร (I want) + ได้ประโยชน์อะไร (So that) + ตรวจรับด้วย AC ตามหลัก INVEST"
    }
]

ALL_DOCS.extend(ADDITIONAL_SPECS)

# Let's add remaining 19 to 30 files
FINAL_SPECS = [
    # 19. BA/comunication-rule01-BA-DEV.md
    {
        "file_rel": "BA/comunication-rule01-BA-DEV.md",
        "output_name": "19_BA_Dev_Communication",
        "top_note_title": "COLLABORATION RULES", "top_note_sub": "BA & DEV HARMONY",
        "title_plain": "กฎเหล็กการสื่อสารระหว่าง BA กับ Dev",
        "title_html": "กฎเหล็กการสื่อสาร <span class=\"blue-highlight\">ระหว่าง BA กับ Dev</span>",
        "subtitle_html": "ลดช่องว่างภาษาธุรกิจและภาษาเทคนิค <strong>\"ทำงานประสานกันอย่างราบรื่น ไร้ข้อขัดแย้ง\"</strong>",
        "notepad_header": "5 กฎเหล็ก BA & Dev",
        "notepad_items": [
            "1. คุยด้วยปัญหา ไม่ใช่สั่ง Solution",
            "2. สื่อสารด้วยภาพ Flow เสมอ",
            "3. ดักทุกทาง มี AC & Edge Cases",
            "4. อัปเดตเป็นลายลักษณ์อักษร",
            "5. รับฟังข้อจำกัดด้านเทคนิค"
        ],
        "strategy_title": "🎯 1. PROBLEM OVER SOLUTION : สื่อสารด้วยโจทย์และเป้าหมาย",
        "strategy_bullets": [
            "BA ควรอธิบาย 'ปัญหาและเป้าหมายของธุรกิจ' ให้ชัดเจน ไม่ใช่สั่งวิธีการทางเทคนิค ปล่อยให้ Dev ช่วยออกแบบ Solution",
            "การสื่อสารด้วยภาพ Flowchart, Wireframe และ Data Sequence ดีกว่าการใช้ตัวหนังสือบรรยายยาวเหยียด",
            "มีเกณฑ์ Acceptance Criteria ที่ชัดเจนเพื่อไม่ให้ Dev ต้องเดาใจหรือคิดตรรกะเอง",
            "ห้ามเปลี่ยน Requirement ปากเปล่า ต้องอัปเดตเอกสารและแจ้งผลกระทบเสมอ"
        ],
        "cloud_bubble_html": "🤝 <strong>Dynamic Duo</strong><br>BA และ Dev คือคู่หูร่วมสร้างความสำเร็จ เมื่อสื่อสารด้วยความเข้าใจ งานจะราบรื่นและมีคุณภาพสูง",
        "execution_label": "COLLABORATION TOUCHPOINTS : 6 จังหวะการพูดคุยสำคัญ",
        "columns": [
            {"title": "1. DISCOVERY", "char": "ba", "items": ["ชวน Dev ฟังโจทย์", "ทำความเข้าใจ Pain", "แชร์ Business Context", "เช็ก Feasibility เบื้องต้น"]},
            {"title": "2. FLOW DESIGN", "char": "flow", "items": ["วาด Process Flow", "ระบุ Decision Points", "ออกแบบ Error Flow", "รีวิวตรรกะร่วมกัน"]},
            {"title": "3. REFINEMENT", "char": "dev", "items": ["Walkthrough Story", "ตอบข้อสงสัยเทคนิค", "ล็อกเงื่อนไข AC", "ประเมิน Story Points"]},
            {"title": "4. SPRINT SUPPORT", "char": "designer", "items": ["Standby ตอบคำถาม", "ช่วยเคลียร์บล็อกเกอร์", "ไม่แอบแก้ Requirement", "ซิงก์กันทุกวัน"]},
            {"title": "5. ACCEPTANCE", "char": "qa", "items": ["รีวิวผลงานร่วมกัน", "เช็กตามเกณฑ์ AC", "เทสบน Staging", "รับรองความถูกต้อง"]},
            {"title": "6. RETROSPECTIVE", "char": "presenter", "items": ["ทบทวนการสื่อสาร", "หาจุดติดขัดที่ผ่านมา", "ปรับปรุงการส่งต่องาน", "สร้างความสัมพันธ์ที่ดี"]}
        ],
        "bottom_left_title": "พฤติกรรมสร้างสรรค์ vs พฤติกรรมต้องห้าม",
        "skills": [
            {"type": "x", "title": "พฤติกรรมสร้างสรรค์ (Best Practices)", "code": "Do This", "desc": "คุยกันบ่อยๆ แต่สั้นและตรงประเด็น, ใช้ภาพประกอบ, รับฟังและเคารพซึ่งกันและกัน"},
            {"type": "t", "title": "พฤติกรรมต้องห้าม (Avoid This)", "code": "Don't Do", "desc": "โยนเอกสารหนาๆ ให้ Dev อ่านเองโดยไม่บรีฟ, สั่งเปลี่ยนสเปกปากเปล่ากลางคัน"},
            {"type": "i", "title": "เมื่อเกิดข้อขัดแย้ง (Conflict Resolution)", "code": "Resolve", "desc": "กางโจทย์ธุรกิจและเป้าหมายผู้ใช้มาคุยกัน ตัดสินด้วย Data ไม่ใช่อารมณ์"}
        ],
        "bottom_center_title": "วงจรการสื่อสารตลอดโครงการ",
        "loop_data": {
            "s1_title": "1. PROBLEM BRIEF", "s1_sub": "🎯 เล่าโจทย์ธุรกิจ",
            "s2_title": "2. FLOW & AC REVIEW", "s2_sub": "📐 รีวิวภาพและเงื่อนไข",
            "s3_title": "3. SPRINT COLLAB", "s3_sub": "💬 คุยซิงก์ระหว่างโค้ด",
            "s4_title": "4. DEMO & VERIFY", "s4_sub": "✅ ตรวจรับตรงตาม AC",
            "center_t1": "SEAMLESS", "center_t2": "COMMUNICATION"
        },
        "bottom_right_title": "คำพูดเชิงบวกที่ช่วยให้งานเดินหน้า",
        "focus_items": [
            "💡 'โจทย์ธุรกิจคือข้อนี้ คุณคิดว่ามี Solution เทคนิคแบบไหนที่ดีที่สุด?'",
            "💡 'เรามากาง Flow ดูกันหน่อยว่าถ้าเกิดกรณีนี้ ระบบควรตอบสนองอย่างไร'",
            "💡 'ตรงเงื่อนไขนี้เขียนชัดเจนพอไหม หรืออยากให้เติมรายละเอียดตรงไหนเพิ่ม?'",
            "💡 'ถ้าทำตามวิธีนี้ จะกระทบประสิทธิภาพระบบหรือใช้เวลามากไปไหม?'"
        ],
        "focus_quote": "การสื่อสารที่ดีไม่ได้วัดที่ปริมาณการพูดคุย แต่วัดที่ความเข้าใจตรงกันและการทำงานต่อได้อย่างมั่นใจ",
        "key_takeaway": "BA & Dev = เล่าเป้าหมาย + สื่อสารด้วยภาพ Flow + ล็อก AC ชัดเจน + อัปเดตลายลักษณ์อักษร + ทำงานเป็นทีม"
    },

    # 20. case-study/CASE-01.md
    {
        "file_rel": "case-study/CASE-01.md",
        "output_name": "20_Case_01_Mid_Sprint_Change",
        "top_note_title": "CASE STUDY 01", "top_note_sub": "MID-SPRINT CHANGE",
        "title_plain": "CASE 01: ลูกค้าขอเปลี่ยนงานกลาง Sprint รับมืออย่างไร ?",
        "title_html": "CASE 01: ลูกค้าขอเปลี่ยนงาน <span class=\"red-highlight\">กลาง Sprint !</span>",
        "subtitle_html": "กรณีศึกษา : วิธีรับมืออย่างมืออาชีพเมื่อมีคำขอด่วนแทรกเข้ามาระหว่างทาง",
        "notepad_header": "หลักการรับมืองานแทรก",
        "notepad_items": [
            "รับฟังเหตุผลทางธุรกิจ",
            "ประเมิน Impact ต่องบและเวลา",
            "เสนอทางเลือก (Trade-off)",
            "ให้ลูกค้าตัดสินใจเลือก",
            "บันทึกลง Backlog เสมอ"
        ],
        "strategy_title": "🎯 1. INCIDENT SCENARIO : เมื่อ Sprint Goal กำลังถูกคุกคาม",
        "strategy_bullets": [
            "สถานการณ์ : Sprint ดำเนินไปได้ครึ่งทาง แต่ Stakeholder แจ้งขอด่วนเพื่อเปลี่ยน Flow และเพิ่มฟิลด์ใหม่",
            "ปัญหา : หากรับเข้ามาตรงๆ จะทำให้งานเดิมที่ Commit ไว้ทำไม่เสร็จ และทีม Dev เกิดความสับสน",
            "แนวทางแก้ไข : รับฟังความจำเป็น ประเมินผลกระทบ และเสนอ 2 ทางเลือกหลักอย่างสุภาพ",
            "เป้าหมาย : ปกป้อง Sprint Goal และรักษาความสัมพันธ์อันดีกับลูกค้า"
        ],
        "cloud_bubble_html": "🛡️ <strong>Protect Sprint Commitment</strong><br>Sprint Goal คือสัญญาใจ การรับงานแทรกโดยไม่แลกเปลี่ยนจะทำให้คุณภาพระบบพังทลาย",
        "execution_label": "THE 4-STEP RESOLUTION : 4 ขั้นตอนจัดการอย่างเป็นระบบ",
        "columns": [
            {"title": "1. EMPATHIZE & LOG", "char": "po", "items": ["รับฟังด้วยความเข้าใจ", "ถามเหตุผลความจำเป็น", "ทำไมต้องด่วนตอนนี้?", "บันทึกรายละเอียดคำขอ"]},
            {"title": "2. ASSESS IMPACT", "char": "ba", "items": ["คำนวณเวลากับ Dev", "เช็กผลต่อ Sprint Goal", "เช็กผลต่องานที่ทำค้าง", "ประเมินความเสี่ยง"]},
            {"title": "3. OPTION A (NEXT)", "char": "presenter", "items": ["นำเข้า Sprint ถัดไป", "เตรียมงานให้พร้อม DoR", "งานเดิมเสร็จตามนัด", "ทางเลือกที่แนะนำ"]},
            {"title": "4. OPTION B (SWAP)", "char": "flow", "items": ["สลับงานเดิมออก", "ถอดงาน Effort เท่ากัน", "Sprint Goal เปลี่ยนใหม่", "ทุกคนรับทราบผล"]},
            {"title": "5. CLIENT DECIDE", "char": "dev", "items": ["ให้ลูกค้าเลือก A หรือ B", "อธิบายข้อดี-ข้อเสีย", "โปร่งใสและตรงไปตรงมา", "ล็อกการตัดสินใจ"]},
            {"title": "6. ADJUST BOARD", "char": "qa", "items": ["อัปเดต Jira / Backlog", "ปรับ Test Scenarios", "แจ้งทีมให้เริ่มลุยงาน", "ดำเนินงานตามข้อตกลง"]}
        ],
        "bottom_left_title": "บทเรียนสำคัญจากกรณีศึกษา 01",
        "skills": [
            {"type": "x", "title": "การบริหารความคาดหวัง (Expectation Management)", "code": "Alignment", "desc": "ลูกค้าไม่ได้อยากให้โปรเจกต์พัง เมื่ออธิบายผลกระทบอย่างสุภาพ ลูกค้าพร้อมจะเข้าใจและเลือกทางออกที่ดีที่สุด"},
            {"type": "t", "title": "กฎเหล็กการสลับงาน (Zero-Sum Principle)", "code": "Zero-Sum Scope", "desc": "ใน 1 Sprint มีชั่วโมงทำงานคงที่ หากจะเพิ่มงานใหม่ ต้องยอมตัดงานเก่าออกด้วยขนาดที่เท่ากันเสมอ"},
            {"type": "i", "title": "การป้องกันในอนาคต (Preventive Action)", "code": "Refinement Gate", "desc": "จัด Workshop และ Refinement ให้ละเอียดล่วงหน้าเพื่อลดคำขอด่วนที่เกิดจากความไม่พร้อม"}
        ],
        "bottom_center_title": "วงจรการเจรจาเมื่อมีงานแทรก",
        "loop_data": {
            "s1_title": "1. RECEIVE REQUEST", "s1_sub": "📥 รับฟังความต้องการ",
            "s2_title": "2. ASSESS IMPACT", "s2_sub": "🔍 คำนวณเวลากับทีม",
            "s3_title": "3. OFFER OPTIONS (A/B)", "s3_sub": "⚖️ เสนอทางเลือกสลับงาน",
            "s4_title": "4. AGREE & EXECUTE", "s4_sub": "📝 ปรับแผนและลุยต่อ",
            "center_t1": "WIN-WIN", "center_t2": "RESOLUTION"
        },
        "bottom_right_title": "สิ่งที่ไม่ควรทำเด็ดขาดเมื่อเจองานแทรก",
        "focus_items": [
            "❌ รับปากทันทีโดยไม่ปรึกษาทีม Dev และ QA",
            "❌ ปฏิเสธเสียงแข็งโดยไม่รับฟังเหตุผลทางธุรกิจของลูกค้า",
            "❌ แอบเพิ่มงานเข้ากระดานโดยไม่แจ้งให้คนอื่นในทีมทราบ",
            "❌ บังคับให้ทีมทำงานล่วงเวลาเพื่อยัดงานที่เพิ่มเข้ามา"
        ],
        "focus_quote": "ความเป็นมืออาชีพวัดกันที่ความสามารถในการรับมือกับความเปลี่ยนแปลงอย่างมีหลักการและสร้างความเชื่อมั่น",
        "key_takeaway": "รับมืองานแทรก = เข้าใจเหตุผล + ประเมินผลกระทบ + เสนอทางเลือกสลับงาน หรือ เลื่อนเข้า Sprint ถัดไป"
    },

    # 21. case-study/CASE-02.md
    {
        "file_rel": "case-study/CASE-02.md",
        "output_name": "21_Case_02_Project_Delay",
        "top_note_title": "CASE STUDY 02", "top_note_sub": "CRISIS RECOVERY",
        "title_plain": "CASE 02: งานติดคอขวด โปรเจกต์จ่อ Delay แก้อย่างไร ?",
        "title_html": "CASE 02: งานติดคอขวด <span class=\"red-highlight\">โปรเจกต์จ่อ Delay !</span>",
        "subtitle_html": "กรณีศึกษา : แก้วิกฤตงานค้างและกู้คืนความเร็วในการส่งมอบได้อย่างทันท่วงที",
        "notepad_header": "แผนกู้วิกฤต Delay",
        "notepad_items": [
            "ค้นหา Root Cause ที่แท้จริง",
            "ตัดงานรอง (Descope)",
            "รวมพลังช่วยกัน (Swarming)",
            "สื่อสารความจริงกับลูกค้า",
            "ส่งมอบ Core Value ก่อน"
        ],
        "strategy_title": "🎯 1. INCIDENT SCENARIO : เมื่อเวลาเหลือน้อยแต่งานยังไม่เสร็จ",
        "strategy_bullets": [
            "สถานการณ์ : เหลือเวลาอีก 3 วันจะหมด Sprint แต่งานค้างอยู่ในสถานะ In Progress / Blocked เกือบทั้งหมด",
            "ปัญหา : QA ยังไม่ได้เริ่มเทส มี Technical Blockers และมีแนวโน้มสูงมากที่จะส่งมอบไม่ทันตามเป้าหมาย",
            "แนวทางแก้ไข : รวมพลังแก้จุดคอขวด (Swarming), ตัดงาน Nice-to-have ออก และสื่อสารอย่างโปร่งใส",
            "เป้าหมาย : ส่งมอบ Core Value ที่สำคัญที่สุดให้ได้ และวางระบบป้องกันไม่ให้เกิดซ้ำ"
        ],
        "cloud_bubble_html": "⚡ <strong>Transparency & Swarming</strong><br>ความล้มเหลวไม่ใช่การส่งงานไม่ครบ แต่คือการปกปิดปัญหาจนกระทั่งถึงวันเดดไลน์",
        "execution_label": "CRISIS RECOVERY PLAYBOOK : 6 ขั้นตอนกอบกู้สถานการณ์",
        "columns": [
            {"title": "1. ROOT CAUSE", "char": "dev", "items": ["ขุดหาจุดคอขวด", "Task ใหญ่เกินไป?", "ติดรอ Dependency?", "มีบล็อกเกอร์เทคนิค?"]},
            {"title": "2. SWARMING", "char": "flow", "items": ["รวมพลังคนว่าง", "Dev ช่วยกันแก้จุดติด", "Pair Programming", "ปลดล็อกด่วนที่สุด"]},
            {"title": "3. DESCOPE SCOPE", "char": "po", "items": ["ตัดส่วนเสริมออก", "โฟกัส Must Have", "ส่งของให้ QA เทสทันที", "ลดความซับซ้อน"]},
            {"title": "4. QA ACCELERATION", "char": "qa", "items": ["เทสเฉพาะ Core Flow", "ทดสอบเคสสำคัญก่อน", "ดักจับ Critical Bugs", "เตรียม Staging พร้อม"]},
            {"title": "5. COMMUNICATE", "char": "presenter", "items": ["แจ้งลูกค้าล่วงหน้า", "บอกความจริงอย่างสุภาพ", "เสนอแผนส่งมอบ Core", "ระบุกำหนดการส่วนที่เหลือ"]},
            {"title": "6. RETRO & PREVENT", "char": "ba", "items": ["วิเคราะห์บทเรียน", "ซอย Task ให้เล็กลง", "ยกปัญหาใน Daily เร็วขึ้น", "วาง Buffer Time"]}
        ],
        "bottom_left_title": "การวิเคราะห์สาเหตุคอขวด (Root Causes)",
        "skills": [
            {"type": "x", "title": "Task ขนาดใหญ่เกินไป (Large Tasks)", "code": "Task Slicing", "desc": "งานชิ้นใหญ่ที่ทำหลายวันโดยไม่มีการแตกย่อย ทำให้ QA รอจนถึงวันสุดท้าย ➔ ต้องแตก Task ให้จบได้ใน 1-2 วัน"},
            {"type": "t", "title": "Dependency ภายนอก (External Blockers)", "code": "Dependencies", "desc": "ติดรอ API หรือสิทธิ์เข้าถึงจากทีมอื่น ➔ ต้องเช็กและปลดล็อกตั้งแต่ช่วง Refinement"},
            {"type": "i", "title": "ความเงียบใน Daily Scrum (Silent Blockers)", "code": "Daily Honesty", "desc": "พยายามแก้ปัญหาคนเดียวโดยไม่ยอมบอกทีม ➔ ต้องสร้างบรรยากาศที่กล้าขอความช่วยเหลือ"}
        ],
        "bottom_center_title": "กระบวนการกู้วิกฤตงานล่าช้า",
        "loop_data": {
            "s1_title": "1. IDENTIFY BOTTLENECK", "s1_sub": "🔍 ตรวจพบจุดคอขวดทันที",
            "s2_title": "2. SWARM & DESCOPE", "s2_sub": "🤝 รวมพลัง & ตัดงานรอง",
            "s3_title": "3. FAST-TRACK QA", "s3_sub": "🧪 เร่งเทส Core Flow",
            "s4_title": "4. DELIVER CORE VALUE", "s4_sub": "🚀 ส่งมอบฟังก์ชันหลัก",
            "center_t1": "RECOVERED", "center_t2": "ON TIME"
        },
        "bottom_right_title": "การสื่อสารกับ Stakeholder อย่างมืออาชีพ",
        "focus_items": [
            "แจ้งเตือนล่วงหน้าทันที ไม่รอจนถึงชั่วโมงสุดท้ายของเดดไลน์",
            "อธิบายอย่างโปร่งใสว่าอะไรที่จะส่งมอบได้สมบูรณ์ และอะไรที่ต้องเลื่อน",
            "นำเสนอแผนฟื้นฟูและกำหนดการส่งมอบใหม่อย่างชัดเจน",
            "แสดงความรับผิดชอบและชี้แจงแนวทางป้องกันในอนาคต"
        ],
        "focus_quote": "ความจริงใจในการสื่อสารเมื่อเกิดปัญหา จะช่วยสร้างความเชื่อมั่นได้มากกว่าการฝืนส่งงานที่ไร้คุณภาพ",
        "key_takeaway": "แก้งาน Delay = กล้าเปิดเผยปัญหา + ตัดงานรองออก + รวมพลังปลดบล็อก + ส่งมอบ Core Value + นำบทเรียนไปปรับปรุง"
    },

    # 22. case-study/CASE-03.md
    {
        "file_rel": "case-study/CASE-03.md",
        "output_name": "22_Case_03_Ambiguous_Requirement",
        "top_note_title": "CASE STUDY 03", "top_note_sub": "REQUIREMENT CLARITY",
        "title_plain": "CASE 03: Requirement ไม่ชัด ทีมตีความคนละภาพ",
        "title_html": "CASE 03: Requirement ไม่ชัด <span class=\"red-highlight\">ทีมตีความคนละภาพ !</span>",
        "subtitle_html": "กรณีศึกษา : แก้ปัญหาการรื้อระบบใหม่ และสร้างความเข้าใจตรงกันตั้งแต่ต้นน้ำ",
        "notepad_header": "วิธีเคลียร์ภาพให้ตรงกัน",
        "notepad_items": [
            "ห้ามใช้ข้อความบรรยายล้วน",
            "ต้องมี Wireframe & Mockup",
            "เขียน AC เป็น Given/When/Then",
            "จัด Alignment Walkthrough",
            "ยืนยันภาพตรงกันก่อนโค้ด"
        ],
        "strategy_title": "🎯 1. INCIDENT SCENARIO : เมื่อ Dev ทำตามสั่ง แต่ User บอกว่าไม่ใช่",
        "strategy_bullets": [
            "สถานการณ์ : ในวัน Sprint Review ทาง Dev ภูมิใจนำเสนอชิ้นงานที่ทำตามตัวหนังสือใน Story ทุกบรรทัด",
            "ปัญหา : User อุทานว่า 'ไม่ใช่แบบที่คิดไว้เลย ทำไมทำแบบนี้' ทำให้ต้องรื้อโค้ดและดีไซน์ใหม่ทั้งหมด",
            "สาเหตุ : ใช้ข้อความบรรยายกว้างๆ ไม่มีภาพหน้าจอประกอบ และไม่มี Acceptance Criteria ที่ชัดเจน",
            "แนวทางแก้ไข : จัด Alignment Workshop 30 นาที กาง Wireframe คู่กับ Flow และเขียน AC ใหม่"
        ],
        "cloud_bubble_html": "🖼️ <strong>A Picture is Worth 1,000 Specs</strong><br>ตัวหนังสือหนึ่งบรรทัด คนสิบคนตีความได้สิบแบบ การสื่อสารด้วยภาพและตัวอย่างจริงจะช่วยลดการรื้อโค้ดได้ 100%",
        "execution_label": "ALIGNMENT PLAYBOOK : 6 ขั้นตอนสร้างความเข้าใจตรงกัน",
        "columns": [
            {"title": "1. STOP & ALIGN", "char": "po", "items": ["หยุดการเดาใจ", "นัดคุย 30 นาที", "ชวน User, BA, Dev", "เปิดใจรับฟังปัญหา"]},
            {"title": "2. SHOW WIREFRAME", "char": "designer", "items": ["วาด Mockup หน้าจอ", "แสดงตำแหน่งปุ่ม", "แสดง Interaction", "เช็กความต้องการจริง"]},
            {"title": "3. MAP USER FLOW", "char": "flow", "items": ["วาดขั้นตอน 1-2-3", "ระบุ Decision Points", "แสดง Error States", "ทุกคนเห็นภาพเดียวกัน"]},
            {"title": "4. REWRITE AC", "char": "ba", "items": ["Given / When / Then", "ระบุเงื่อนไขตัวเลข", "ดักเคสข้อมูลผิดปกติ", "ล็อกเกณฑ์ความสำเร็จ"]},
            {"title": "5. CONFIRMATION", "char": "dev", "items": ["Dev ทวนความเข้าใจ", "QA เช็กการแตกเคส", "User กดยืนยันเห็นชอบ", "ลงนามข้อตกลง"]},
            {"title": "6. BUILD RIGHT", "char": "qa", "items": ["เขียนโค้ดตรงภาพ", "เทสตรงตาม AC", "Demo สำเร็จรอบแรก", "ส่งมอบไร้รอยต่อ"]}
        ],
        "bottom_left_title": "หลักการ 3Cs เพื่อป้องกันการเข้าใจผิด",
        "skills": [
            {"type": "x", "title": "Card (การ์ดสรุปโจทย์)", "code": "Card", "desc": "เขียนความต้องการสั้นๆ กระชับบนการ์ด เพื่อเป็นตัวแทนของปัญหาที่ต้องแก้ไข"},
            {"type": "t", "title": "Conversation (บทสนทนาตกผลึก)", "code": "Conversation", "desc": "นัดพูดคุยระหว่าง BA, PO, Dev และ QA เพื่อทำความเข้าใจร่วมกันผ่านภาพและตัวอย่างจริง"},
            {"type": "i", "title": "Confirmation (เกณฑ์ยืนยันความสำเร็จ)", "code": "Confirmation", "desc": "เขียน Acceptance Criteria ที่ชัดเจนและตรวจสอบได้จริง เพื่อเป็นสัญญาตรวจรับงาน"}
        ],
        "bottom_center_title": "วงจรสร้างความเข้าใจที่ถูกต้อง",
        "loop_data": {
            "s1_title": "1. SKETCH MOCKUP", "s1_sub": "✏️ ร่างภาพหน้าจอ & Flow",
            "s2_title": "2. WALKTHROUGH", "s2_sub": "🗣️ พูดคุยทบทวนร่วมกัน",
            "s3_title": "3. LOCK AC CRITERIA", "s3_sub": "🔒 เขียนเกณฑ์ Given/When/Then",
            "s4_title": "4. BUILD WITH CONFIDENCE", "s4_sub": "💻 โค้ดด้วยความมั่นใจ",
            "center_t1": "PERFECT", "center_t2": "ALIGNMENT"
        },
        "bottom_right_title": "คำพูดกำกวมที่ก่อให้เกิดความเข้าใจผิด",
        "focus_items": [
            "⚠️ 'ทำหน้าแสดงผลข้อมูลให้สวยงามและดูทันสมัย'",
            "⚠️ 'ให้ระบบคำนวณราคาตามความเหมาะสม'",
            "⚠️ 'เพิ่มระบบค้นหาที่ใช้งานง่ายและรวดเร็ว'",
            "⚠️ 'แจ้งเตือนผู้ใช้งานเมื่อมีอะไรผิดพลาด'"
        ],
        "focus_quote": "อย่าเริ่มเขียนโค้ดแม้แต่บรรทัดเดียว หากทีมยังมองไม่เห็นภาพผลลัพธ์สุดท้ายตรงกัน",
        "key_takeaway": "แก้ Requirement ไม่ชัด = วาดภาพ Mockup ให้ดู + เขียน AC ให้รัดกุม + ทบทวนทำความเข้าใจร่วมกัน + ยืนยันตรงกันก่อนลงมือทำ"
    },

    # 23. case-study/CASE-06.md
    {
        "file_rel": "case-study/CASE-06.md",
        "output_name": "23_Case_06_AI_Agent_Audit",
        "top_note_title": "AI GOVERNANCE", "top_note_sub": "AGENT AUDIT & GUARDRAILS",
        "title_plain": "CASE 06: AI Agent ส่งงานไม่ตรงสเปก ตรวจสอบอย่างไร ?",
        "title_html": "CASE 06: AI Agent ส่งงาน <span class=\"red-highlight\">ไม่ตรงสเปก ตรวจสอบอย่างไร ?</span>",
        "subtitle_html": "กรณีศึกษา : วิธีตรวจสอบ แก้ไข และสร้าง Guardrails เมื่อ AI ทำงานหลุดกรอบ",
        "notepad_header": "หลักการกำกับดูแล AI",
        "notepad_items": [
            "ยึดถือ Canonical Schema เป็นหลัก",
            "ตรวจสอบ Prompt Context",
            "มี Automated Validation Gate",
            "ป้องกันข้อมูล PII รั่วไหล",
            "Fail Closed เมื่อข้อมูลไม่ตรง"
        ],
        "strategy_title": "🎯 1. INCIDENT SCENARIO : เมื่อ AI ทำงานหลุดกรอบสัญญาข้อมูล",
        "strategy_bullets": [
            "สถานการณ์ : AI Agent สร้างโค้ด เอกสาร หรือโครงสร้างข้อมูลที่มี Schema ผิดเพี้ยนจากมาตรฐาน",
            "ปัญหา : เกิดอาการ Hallucination สร้าง Entity ที่ไม่มีอยู่จริง หรือข้าม Invariants สำคัญทางธุรกิจ",
            "แนวทางแก้ไข : ทำการ Audit เปรียบเทียบกับ Schema Contract, ปรับปรุง Context และเพิ่ม Guardrails",
            "เป้าหมาย : ทำให้ AI Agent ทำงานได้อย่างแม่นยำ ปลอดภัย และอยู่ภายใต้ Governance 100%"
        ],
        "cloud_bubble_html": "🤖 <strong>Governed AI Delivery</strong><br>AI คือผู้ช่วยที่ทรงพลัง แต่ต้องมีกรอบกำกับ (Governance) และการตรวจสอบที่เข้มงวดเพื่อความถูกต้องและปลอดภัยสูงสุด",
        "execution_label": "AI AUDIT & GUARDRAIL PLAYBOOK : 6 ขั้นตอนตรวจสอบ AI",
        "columns": [
            {"title": "1. CONTRACT CHECK", "char": "dev", "items": ["เทียบ Schema Contract", "schema_genesisblock.yaml", "เช็ก ID Formats", "เช็ก Required Fields"]},
            {"title": "2. CONTEXT AUDIT", "char": "ba", "items": ["ตรวจสอบ System Prompt", "เช็ก RAG Context ที่ดึงมา", "ดูว่ามีข้อมูลกำกวมไหม?", "แก้ไข Prompt ให้ชัด"]},
            {"title": "3. ROOT CAUSE", "char": "qa", "items": ["แยกประเภทปัญหา", "เป็น Bug หรือ Data Gap?", "เป็น Hallucination?", "บันทึก Error Trace"]},
            {"title": "4. ADD EXAMPLES", "char": "presenter", "items": ["ใส่ One-shot Examples", "ใส่ Few-shot Patterns", "กำหนดข้อห้ามชัดเจน", "ระบุ Invariants"]},
            {"title": "5. AUTOMATED GATE", "char": "flow", "items": ["รัน Linter & Type Check", "รัน Unit Test อัตโนมัติ", "ตรวจจับ Zero-PII", "Fail Closed ทันที"]},
            {"title": "6. CONTINUOUS LOG", "char": "po", "items": ["บันทึก Audit Logs", "ติดตามความแม่นยำ", "อัปเดต Directive สม่ำเสมอ", "รับรองความปลอดภัย"]}
        ],
        "bottom_left_title": "เสาหลักการกำกับดูแล AI (AI Governance Pillars)",
        "skills": [
            {"type": "x", "title": "Schema Integrity (ความถูกต้องของสัญญาข้อมูล)", "code": "Schema Contract", "desc": "ทุก Output ของ AI ต้องแมปกลับสู่ Canonical Schema ได้ 100% ห้ามสร้าง Entity ลอยๆ"},
            {"type": "t", "title": "Zero-PII Invariant (ความปลอดภัยข้อมูลส่วนบุคคล)", "code": "Zero-PII", "desc": "ห้ามนำข้อมูลส่วนตัวของลูกค้าเข้าสู่ Vector Vault หรือแสดงในโค้ดที่ไม่ได้รับอนุญาต"},
            {"type": "i", "title": "Automated Quality Gates (ระบบตรวจสอบอัตโนมัติ)", "code": "Quality Gate", "desc": "ใช้ Automated Test และ Linter ตรวจสอบผลงานของ AI ก่อนนำไปรันจริงในระบบ"}
        ],
        "bottom_center_title": "วงจรการตรวจสอบและปรับแต่ง AI",
        "loop_data": {
            "s1_title": "1. PROMPT CONTEXT", "s1_sub": "📥 ส่งโจทย์ & Schema",
            "s2_title": "2. AI GENERATION", "s2_sub": "🤖 AI ประมวลผลงาน",
            "s3_title": "3. VALIDATION GATE", "s3_sub": "🛡️ ตรวจสอบด้วย Test & Linter",
            "s4_title": "4. AUDIT & REFINE", "s4_sub": "🔧 ปรับปรุง Context ต่อเนื่อง",
            "center_t1": "RELIABLE", "center_t2": "AI DELIVERY"
        },
        "bottom_right_title": "สัญญาณเตือนว่า AI Agent กำลังหลุดสเปก",
        "focus_items": [
            "สร้าง Primary Key หรือรูปแบบ ID ที่ผิดแปลกไปจากระบบเดิม",
            "หลุดข้อมูล PII หรือข้อมูลที่เป็นความลับโดยไม่ได้รับอนุญาต",
            "โค้ดทำงานได้แต่ข้าม Invariants สำคัญทางธุรกิจไป",
            "ให้คำตอบแบบคาดเดาโดยไม่มีเอกสารหรือหลักฐานอ้างอิง"
        ],
        "focus_quote": "คุณภาพของงานที่ AI สร้างขึ้น เป็นภาพสะท้อนโดยตรงของความชัดเจนใน Context และ Guardrails ที่เรามอบให้",
        "key_takeaway": "กำกับดูแล AI = สเปกต้องเป๊ะ + คอนเท็กซ์ต้องครบ + มี Schema Contract + ตรวจสอบด้วย Automated Gate ก่อนปล่อยงาน"
    },

    # 24. PM/PM-req.md
    {
        "file_rel": "PM/PM-req.md",
        "output_name": "24_PM_Risk_Management",
        "top_note_title": "RISK MANAGEMENT", "top_note_sub": "PM SURVEILLANCE GUIDE",
        "title_plain": "6 ความเสี่ยงสำคัญที่ PM ต้องเฝ้าระวังและรับมือ !",
        "title_html": "6 ความเสี่ยงสำคัญที่ <span class=\"blue-highlight\">PM ต้องเฝ้าระวัง</span> <span class=\"red-highlight\">&amp; รับมือ !</span>",
        "subtitle_html": "มองเห็นปัญหาล่วงหน้า วางแผนป้องกัน <strong>\"บริหารโครงการได้ตามเป้าหมายอย่างไร้กังวล\"</strong>",
        "notepad_header": "6 มิติความเสี่ยง",
        "notepad_items": [
            "1. Scope Risk (งานบวม/คลุมเครือ)",
            "2. Schedule Risk (งานดีเลย์)",
            "3. Resource Risk (คนขาด/หมดไฟ)",
            "4. Technical Risk (ระบบซับซ้อน)",
            "5. Stakeholder Risk (เปลี่ยนใจ)",
            "6. Quality Risk (บั๊กสะสม)"
        ],
        "strategy_title": "🎯 1. PROACTIVE RISK MANAGEMENT : ป้องกันก่อนเกิดวิกฤต",
        "strategy_bullets": [
            "หน้าที่สำคัญที่สุดของ PM ไม่ใช่การรอแก้ปัญหาเมื่อเกิดเรื่อง แต่คือการมองเห็นความเสี่ยงและขจัดอุปสรรคล่วงหน้า",
            "จัดทำ Risk Register และประเมินโอกาสเกิด (Probability) ควบคู่กับระดับผลกระทบ (Impact)",
            "วางแผนการบรรเทาความเสี่ยง (Mitigation Plan) และเตรียมแผนสำรอง (Contingency Plan) เสมอ",
            "สื่อสารสถานะความเสี่ยงกับผู้บริหารและทีมอย่างโปร่งใสในทุกสัปดาห์"
        ],
        "cloud_bubble_html": "🔭 <strong>Forward-Looking Leader</strong><br>PM ที่ยอดเยี่ยมคือผู้ถางทางและสร้างความมั่นคงให้ทีมทำงานได้อย่างเต็มศักยภาพ",
        "execution_label": "THE 6 RISK DOMAINS : 6 มิติความเสี่ยงที่ต้องจับตามอง",
        "columns": [
            {"title": "1. SCOPE RISK", "char": "ba", "items": ["งานงอกบวมเรื่อยๆ", "Requirement คลุมเครือ", "แก้โจทย์บ่อย", "วิธีแก้: ทำ In/Out ชัด"]},
            {"title": "2. SCHEDULE RISK", "char": "presenter", "items": ["งานสะดุดดีเลย์", "ติดรอ Third-party", "ประเมินเวลาต่ำไป", "วิธีแก้: ใส่ Buffer 20%"]},
            {"title": "3. RESOURCE RISK", "char": "flow", "items": ["ทีมงานลาออก/ป่วย", "ขาดทักษะเฉพาะทาง", "ทีมทำงานล้นมือ", "วิธีแก้: Cross-train"]},
            {"title": "4. TECHNICAL RISK", "char": "dev", "items": ["ระบบเก่าซับซ้อน", "Performance ตก", "ติดสิทธิ์ Security", "วิธีแก้: ทำ PoC ก่อน"]},
            {"title": "5. STAKEHOLDER", "char": "po", "items": ["ผู้บริหารเปลี่ยนทิศ", "ติดต่อคนตัดสินใจยาก", "ความคาดหวังไม่ตรง", "วิธีแก้: ซิงก์รายสัปดาห์"]},
            {"title": "6. QUALITY RISK", "char": "qa", "items": ["บั๊กสะสมเยอะ", "UAT ไม่ผ่านเกณฑ์", "ขาด Automated Test", "วิธีแก้: คุม DoD เข้ม"]}
        ],
        "bottom_left_title": "ระดับการจัดการความเสี่ยง (Risk Matrix)",
        "skills": [
            {"type": "x", "title": "ความเสี่ยงวิกฤต (High Probability, High Impact)", "code": "Critical Risk", "desc": "ต้องวางแผนป้องกันทันทีและรายงานผู้บริหารระดับสูงเพื่อขอการสนับสนุน"},
            {"type": "t", "title": "ความเสี่ยงปานกลาง (Medium Impact / Probability)", "code": "Manage & Monitor", "desc": "มอบหมาย Owner ชัดเจนและติดตามความคืบหน้าในการประชุมประจำสัปดาห์"},
            {"type": "i", "title": "ความเสี่ยงต่ำ (Low Impact, Low Probability)", "code": "Accept & Watch", "desc": "บันทึกไว้ใน Risk Register และสังเกตการณ์การเปลี่ยนแปลง"}
        ],
        "bottom_center_title": "วงจรบริหารความเสี่ยงของ PM",
        "loop_data": {
            "s1_title": "1. IDENTIFY RISKS", "s1_sub": "🔍 ค้นหาความเสี่ยงรอบด้าน",
            "s2_title": "2. ASSESS IMPACT", "s2_sub": "📊 ประเมินโอกาส & ผลกระทบ",
            "s3_title": "3. PLAN MITIGATION", "s3_sub": "🛡️ วางแผนป้องกัน & แก้ไข",
            "s4_title": "4. MONITOR WEEKLY", "s4_sub": "📈 ติดตามผลทุกสัปดาห์",
            "center_t1": "PROACTIVE", "center_t2": "CONTROL"
        },
        "bottom_right_title": "หลุมพรางที่ PM มักพลาด",
        "focus_items": [
            "วางแผนแบบ Best-case Scenario โดยไม่มี Buffer หรือแผนสำรอง",
            "เกรงใจผู้บริหารจนไม่กล้าบอกความจริงเรื่องความเสี่ยงของโครงการ",
            "มัวแต่วุ่นกับงานเอกสารจนไม่ได้สังเกตความผิดปกติในทีม",
            "ไม่เคยทบทวนความเสี่ยงใหม่ๆ ที่เกิดขึ้นระหว่างการพัฒนา"
        ],
        "focus_quote": "PM ที่ดีไม่ได้วัดจากการไม่มีปัญหาเกิดขึ้น แต่วัดจากความพร้อมในการรับมือและนำพาทีมก้าวข้ามทุกอุปสรรค",
        "key_takeaway": "PM มือโปร = ส่อง 6 มิติความเสี่ยง + ประเมิน Impact + วางแผนป้องกันล่วงหน้า + สื่อสารความจริง + นำโครงการสู่เป้าหมาย"
    },

    # 25. PO/PO-req.md
    {
        "file_rel": "PO/PO-req.md",
        "output_name": "25_PO_Decision_Making",
        "top_note_title": "PO DECISION MATRIX", "top_note_sub": "VALUE OPTIMIZATION",
        "title_plain": "PO ตัดสินใจจากอะไร ? 5 ปัจจัยเลือกงานเข้า Product",
        "title_html": "PO ตัดสินใจจากอะไร ? <span class=\"blue-highlight\">5 ปัจจัยเลือกงาน</span> <span class=\"red-highlight\">เข้า Product</span>",
        "subtitle_html": "เพิ่ม Value สูงสุด ตอบโจทย์ผู้ใช้ <strong>\"และคุ้มค่าต่อการลงทุนของธุรกิจ\"</strong>",
        "notepad_header": "5 ปัจจัยตัดสินใจ",
        "notepad_items": [
            "1. Business Strategy (ตรงเป้าองค์กร)",
            "2. User Value (แก้ Pain Point จริง)",
            "3. Data & Feedback (มีข้อมูลรองรับ)",
            "4. Feasibility & Effort (เป็นไปได้)",
            "5. Risk & Dependency (คุมเสี่ยงได้)"
        ],
        "strategy_title": "🎯 1. VALUE-DRIVEN DECISION : ศิลปะการเลือกงานของ PO",
        "strategy_bullets": [
            "PO ต้องกลั่นกรองไอเดียและความต้องการนับร้อย เพื่อเลือกเฉพาะสิ่งที่สร้างผลตอบแทนสูงสุดให้แก่ธุรกิจ",
            "การตัดสินใจต้องตั้งอยู่บนข้อมูลตัวเลข (Data) และผลตอบรับของผู้ใช้จริง ไม่ใช่ตามความรู้สึกหรือคำขอของคนเสียงดัง",
            "คำนวณความคุ้มค่าระหว่างคุณค่าที่จะได้รับ (Value) เทียบกับแรงงานที่ต้องลงไป (Effort)",
            "กล้าที่จะปฏิเสธไอเดียที่ไม่สอดคล้องกับยุทธศาสตร์อย่างสุภาพและมีเหตุผล"
        ],
        "cloud_bubble_html": "👑 <strong>Guardian of Product Value</strong><br>PO ที่ยอดเยี่ยมต้องกล้าปฏิเสธ 90% ของคำขอ เพื่อมุ่งเน้น 10% ของฟีเจอร์ที่สร้างความเปลี่ยนแปลงได้อย่างแท้จริง",
        "execution_label": "PO DECISION FRAMEWORK : 6 ขั้นตอนคัดกรองงานคุณภาพ",
        "columns": [
            {"title": "1. INTAKE IDEAS", "char": "po", "items": ["รับคำขอทุกช่องทาง", "เข้าใจโจทย์แท้จริง", "ไม่ปฏิเสธทันที", "บันทึกใน Discovery"]},
            {"title": "2. STRATEGY ALIGN", "char": "presenter", "items": ["ตรงกับ OKRs ไหม?", "เพิ่มรายได้/ลดต้นทุน?", "สอดคล้อง Vision?", "สร้างความได้เปรียบ"]},
            {"title": "3. USER DESIRABILITY", "char": "designer", "items": ["ผู้ใช้ต้องการจริงไหม?", "แก้ Pain Point หลัก?", "มี User Research?", "ดูสถิติการใช้งาน"]},
            {"title": "4. TECH FEASIBILITY", "char": "dev", "items": ["ระบบรองรับไหม?", "ใช้เวลานานเท่าใด?", "ติด Dependency ไหม?", "ปรึกษา Tech Lead"]},
            {"title": "5. FINANCIAL ROI", "char": "ba", "items": ["คำนวณความคุ้มค่า", "เทียบ Value vs Cost", "ประเมิน Time to Market", "ความเสี่ยงทางการเงิน"]},
            {"title": "6. DECIDE & COMMIT", "char": "qa", "items": ["ตัดสินใจทำ / ไม่ทำ", "จัดลำดับใน Backlog", "ประกาศทิศทางชัดเจน", "นำเข้าสู่กระบวนการ"]}
        ],
        "bottom_left_title": "3 เสาหลักในการประเมินความคุ้มค่า (V-F-D Model)",
        "skills": [
            {"type": "x", "title": "Desirability (ผู้ใช้ต้องการ)", "code": "User Desirability", "desc": "แก้ปัญหาที่แท้จริงของผู้ใช้ สร้างประสบการณ์ที่ยอดเยี่ยม และมีคนยอมใช้งาน"},
            {"type": "t", "title": "Viability (ธุรกิจได้ประโยชน์)", "code": "Business Viability", "desc": "สร้างรายได้ ลดต้นทุน สอดคล้องกับโมเดลธุรกิจ และคุ้มค่าต่อการลงทุน"},
            {"type": "i", "title": "Feasibility (เทคโนโลยีทำได้)", "code": "Tech Feasibility", "desc": "ทีมพัฒนาสามารถสร้างได้ มีสถาปัตยกรรมและเครื่องมือที่พร้อมรองรับ"}
        ],
        "bottom_center_title": "วงจรการตัดสินใจของ PO",
        "loop_data": {
            "s1_title": "1. GATHER IDEAS & DATA", "s1_sub": "📥 รวบรวมไอเดีย & ดาต้า",
            "s2_title": "2. EVALUATE 5 FACTORS", "s2_sub": "🔍 ประเมินผ่าน 5 ปัจจัย",
            "s3_title": "3. PRIORITIZE BACKLOG", "s3_sub": "⚖️ จัดลำดับเข้าคิวงาน",
            "s4_title": "4. MEASURE POST-LAUNCH", "s4_sub": "📈 วัดผลจริงหลังปล่อย",
            "center_t1": "VALUE", "center_t2": "MAXIMIZATION"
        },
        "bottom_right_title": "กับดักที่ PO ต้องระวัง",
        "focus_items": [
            "พยายามเอาใจทุกคนจนทำให้ Product ไร้จุดยืนที่ชัดเจน",
            "ตัดสินใจตามอารมณ์หรือคำสั่งของคนตำแหน่งสูงสุด (HiPPO)",
            "เลือกทำแต่งานง่ายๆ ที่ไม่สร้างผลกระทบต่อธุรกิจ",
            "ไม่เคยกลับมาวัดผลความสำเร็จหลังจากปล่อยฟีเจอร์ไปแล้ว"
        ],
        "focus_quote": "การเป็น PO คือการเป็นผู้พิทักษ์คุณค่าของ Product ทุกการตัดสินใจต้องพาธุรกิจและผู้ใช้ไปข้างหน้า",
        "key_takeaway": "PO ตัดสินใจเฉียบคม = สอดคล้องเป้าหมายธุรกิจ + ผู้ใช้ได้ประโยชน์จริง + มีดาต้ารองรับ + คุ้มค่าต่อการลงแรง"
    },

    # 26. Requirement/Bad-Requirement.md
    {
        "file_rel": "Requirement/Bad-Requirement.md",
        "output_name": "26_Bad_Requirement_Fixes",
        "top_note_title": "REQUIREMENT QUALITY", "top_note_sub": "PITFALLS & FIXES",
        "title_plain": "5 สัญญาณเตือน Bad Requirement และวิธีแก้ไข",
        "title_html": "5 สัญญาณเตือน <span class=\"blue-highlight\">Bad Requirement</span> <span class=\"red-highlight\">&amp; วิธีแก้ไข</span>",
        "subtitle_html": "กำจัดความคลุมเครือ <strong>\"ลดความเสี่ยงในการพัฒนาซอฟต์แวร์ได้ 100%\"</strong>",
        "notepad_header": "5 สัญญาณ Bad Req",
        "notepad_items": [
            "1. คำกว้าง ลอยๆ (เร็ว/ง่าย/ดี)",
            "2. ขาด User Persona ชัดเจน",
            "3. ไม่มี Business Goal กำกับ",
            "4. ขาด Acceptance Criteria",
            "5. ทดสอบไม่ได้ (Untestable)"
        ],
        "strategy_title": "🎯 1. THE COST OF BAD REQUIREMENTS : ความเสียหายจากความคลุมเครือ",
        "strategy_bullets": [
            "Requirement ที่คลุมเครือทำให้ Dev ตีความผิด ➔ QA ดักบั๊กไม่ได้ ➔ User ไม่ยอมรับ ➔ ต้องรื้อระบบใหม่ทั้งหมด",
            "ต้นทุนในการแก้ไข Requirement ในช่วงเริ่มต้น ถูกกว่าการแก้ไขตอนทดสอบหรือหลัง Go-Live ถึง 100 เท่า",
            "เปลี่ยนคำคุณศัพท์ลอยๆ ให้กลายเป็นตัวเลขและเกณฑ์วัดผลเชิงรูปธรรม",
            "ทุก Requirement ต้องสามารถเขียน Test Script เพื่อทดสอบและพิสูจน์ผลลัพธ์ได้จริง"
        ],
        "cloud_bubble_html": "⚠️ <strong>Clarity Saves Budget</strong><br>Requirement ที่ดีไม่ได้วัดที่ความหนาของเอกสาร แต่วัดที่ความเข้าใจตรงกันของทุกคนในทีม",
        "execution_label": "HOW TO FIX BAD REQUIREMENTS : 6 วิธีแปลงเป็น Requirement ชั้นยอด",
        "columns": [
            {"title": "1. QUANTIFY WORDS", "char": "ba", "items": ["แปลงคำกว้างเป็นตัวเลข", "'ต้องเร็ว' ➔ 'ใน 1.5 วิ'", "'ใช้งานง่าย' ➔ '3 คลิก'", "'รองรับเยอะ' ➔ '10k CCU'"]},
            {"title": "2. SPECIFY PERSONA", "char": "po", "items": ["ระบุ Role ชัดเจน", "'ผู้ใช้ทุกคน' ➔ ไม่เอา", "'Admin บัญชี' ➔ ดี", "กำหนดสิทธิ์แม่นยำ"]},
            {"title": "3. STATE BUSINESS GOAL", "char": "presenter", "items": ["บอกว่าทำไปเพื่ออะไร", "ลดเวลาทำงานกี่ %?", "เพิ่มยอดขายเท่าไร?", "แก้ Pain Point ไหน?"]},
            {"title": "4. ADD GIVEN/WHEN/THEN", "char": "dev", "items": ["ใส่ AC ครบทุกเคส", "ดัก Happy Path", "ดัก Error & Validation", "ดัก Boundary Cases"]},
            {"title": "5. ATTACH WIREFRAME", "char": "designer", "items": ["แนบ Mockup หน้าจอ", "แสดง User Flow", "แสดง Loading/Empty", "ทุกคนเห็นภาพตรงกัน"]},
            {"title": "6. TESTABILITY CHECK", "char": "qa", "items": ["QA ตรวจสอบเคส", "เขียน Test Script ได้ไหม?", "มี Test Data พร้อม?", "ผ่านเกณฑ์ DoR"]}
        ],
        "bottom_left_title": "ตัวอย่างการแปลง Bad ➔ Good Requirement",
        "skills": [
            {"type": "x", "title": "เคสความเร็ว (Performance)", "code": "Speed", "desc": "Bad: 'ระบบต้องโหลดเร็ว' ➔ Good: 'หน้า Dashboard ต้องแสดงผลภายใน 2 วินาที เมื่อมีข้อมูล 10,000 แถว'"},
            {"type": "t", "title": "เคสความถูกต้อง (Validation)", "code": "Validation", "desc": "Bad: 'ข้อมูลต้องถูกต้อง' ➔ Good: 'เบอร์โทรต้องเป็นตัวเลข 10 หลักขึ้นต้นด้วย 0 และแสดงแจ้งเตือนสีแดงหากกรอกผิด'"},
            {"type": "i", "title": "เคสการแจ้งเตือน (Notification)", "code": "Notification", "desc": "Bad: 'แจ้งเตือนเมื่ออนุมัติ' ➔ Good: 'ส่ง Email ยืนยันไปยังผู้ขอภายใน 5 นาที พร้อมแนบไฟล์ PDF ใบคำขอ'"}
        ],
        "bottom_center_title": "วงจรการกลั่นกรอง Requirement",
        "loop_data": {
            "s1_title": "1. SPOT AMBIGUITY", "s1_sub": "🔍 ตรวจหาคำกำกวม",
            "s2_title": "2. QUANTIFY & DETAIL", "s2_sub": "📐 แปลงเป็นเกณฑ์ตัวเลข",
            "s3_title": "3. ADD AC & FLOW", "s3_sub": "📋 ใส่เงื่อนไข & วาดภาพ",
            "s4_title": "4. QA VERIFICATION", "s4_sub": "✅ ยืนยันว่าเทสได้จริง",
            "center_t1": "CRYSTAL", "center_t2": "CLEAR"
        },
        "bottom_right_title": "ผลกระทบเมื่อปล่อยให้มี Bad Requirement",
        "focus_items": [
            "Dev เขียนโค้ดตามจินตนาการของตนเองเพราะโจทย์ไม่ชัด",
            "QA แตก Test Cases ไม่ได้และดักจับบั๊กไม่หมด",
            "User ปฏิเสธการรับมอบงานในวันตรวจรับ (UAT Fail)",
            "ทีมต้องเสียเวลาทำงานล่วงเวลาเพื่อรื้อโค้ดใหม่ทั้งหมด"
        ],
        "focus_quote": "การถามคำถามให้ชัดเจนในวันนี้ ดีกว่าการมานั่งรื้อโค้ดใหม่ทั้งหมดในวันพรุ่งนี้",
        "key_takeaway": "Bad ➔ Good Req = แปลงคำกว้างเป็นตัวเลข + ระบุ Role ให้ชัด + ใส่ Goal กำกับ + เติม AC ให้เทสได้ + แนบ Mockup เสมอ"
    },

    # 27. Requirement/How-to-refinment-Requirement.md
    {
        "file_rel": "Requirement/How-to-refinment-Requirement.md",
        "output_name": "27_Requirement_Refinement_Guide",
        "top_note_title": "REQUIREMENT REFINEMENT", "top_note_sub": "STEP-BY-STEP WORKFLOW",
        "title_plain": "ขั้นตอนการ Refine Requirement ทีละสเต็ป",
        "title_html": "ขั้นตอนการ Refine <span class=\"blue-highlight\">Requirement</span> <span class=\"red-highlight\">ทีละสเต็ป</span>",
        "subtitle_html": "เปลี่ยนความต้องการดิบๆ สู่ <strong>\"งานที่พร้อมส่งต่อให้ทีมพัฒนาอย่างสมบูรณ์แบบ\"</strong>",
        "notepad_header": "5 ขั้นตอนการ Refine",
        "notepad_items": [
            "1. เข้าใจปัญหา & Pain Point",
            "2. ล้อมกรอบ In/Out Scope",
            "3. วาด User Flow & Mockup",
            "4. เขียน Story & AC ละเอียด",
            "5. Walkthrough ซิงก์กับทีม"
        ],
        "strategy_title": "🎯 1. FROM RAW NEED TO REFINED SPEC : การเปลี่ยนโจทย์เป็นผลงาน",
        "strategy_bullets": [
            "ความต้องการเริ่มต้นจากลูกค้ามักมีความคลุมเครือและกระจัดกระจาย หน้าที่ของ BA/PO คือการนำมาผ่านกระบวนการกลั่นกรอง",
            "สัมภาษณ์เจาะลึกเพื่อค้นหา Pain Point ที่แท้จริง (ไม่ใช่แค่ Solution ที่ลูกค้าบอกว่าอยากได้)",
            "กำหนดขอบเขต In-Scope และ Out-of-Scope ให้ชัดเจนตั้งแต่เริ่มต้นเพื่อป้องกันงานบวม",
            "ออกแบบ User Flow และ Wireframe เพื่อให้ทุกคนมองเห็นขั้นตอนการทำงานเดียวกัน"
        ],
        "cloud_bubble_html": "🌉 <strong>Bridge from Idea to Reality</strong><br>การ Refine Requirement คือสะพานเชื่อมระหว่างจินตนาการทางธุรกิจกับระบบเทคโนโลยีที่ใช้งานได้จริง",
        "execution_label": "THE 6 REFINEMENT STEPS : 6 ขั้นตอนการทำงานแบบมืออาชีพ",
        "columns": [
            {"title": "1. DISCOVER PAIN", "char": "po", "items": ["สัมภาษณ์ผู้ใช้งาน", "ค้นหา Pain Point จริง", "ทำความเข้าใจบริบท", "ระบุ Business Value"]},
            {"title": "2. DEFINE SCOPE", "char": "ba", "items": ["กำหนด In-Scope ชัด", "ล็อก Out-of-Scope", "ตั้ง Success Metrics", "ป้องกันงานงอก"]},
            {"title": "3. MAP USER FLOW", "char": "flow", "items": ["วาด As-Is / To-Be", "ระบุทางแยก Decision", "ออกแบบ Error Flow", "วาด Diagram ประกอบ"]},
            {"title": "4. WIREFRAME & UI", "char": "designer", "items": ["จัด Layout หน้าจอ", "ระบุ Interaction", "แสดง Loading State", "แสดง Empty State"]},
            {"title": "5. WRITE STORY & AC", "char": "dev", "items": ["เขียน As a... I want...", "Given / When / Then", "ระบุ Data Schema", "ใส่ Validation Rules"]},
            {"title": "6. WALKTHROUGH", "char": "qa", "items": ["นัดประชุมกับ Dev & QA", "ซักถามข้อสงสัย", "เช็กเกณฑ์ DoR 100%", "พร้อมหยิบเข้า Sprint"]}
        ],
        "bottom_left_title": "เช็กลิสต์ความสมบูรณ์ก่อนส่งต่อ (Refinement Checklist)",
        "skills": [
            {"type": "x", "title": "ความสมบูรณ์ด้านกระบวนการ (Process Complete)", "code": "Flow Complete", "desc": "มีครบทั้งขั้นตอนปกติ (Happy Path) และขั้นตอนรับมือข้อผิดพลาด (Exception Path)"},
            {"type": "t", "title": "ความสมบูรณ์ด้านข้อมูล (Data Complete)", "code": "Data Complete", "desc": "ระบุชื่อฟิลด์, ประเภทข้อมูล (String, Int, Date), ความยาวสูงสุด, และเงื่อนไขบังคับ"},
            {"type": "i", "title": "ความสมบูรณ์ด้านความปลอดภัย (Security Complete)", "code": "Security Complete", "desc": "ระบุสิทธิ์การมองเห็นและการแก้ไขข้อมูลของแต่ละ User Role อย่างชัดเจน"}
        ],
        "bottom_center_title": "วงจรการกลั่นกรอง Requirement ทีละสเต็ป",
        "loop_data": {
            "s1_title": "1. ELICIT & DISCOVER", "s1_sub": "🗣️ สัมภาษณ์ & หา Pain",
            "s2_title": "2. SCOPE & FLOW", "s2_sub": "📐 ล้อมกรอบ & วาด Flow",
            "s3_title": "3. DETAIL & AC", "s3_sub": "📋 เขียน Story & AC",
            "s4_title": "4. TEAM WALKTHROUGH", "s4_sub": "🤝 ซิงก์ทำความเข้าใจ",
            "center_t1": "DEVELOPMENT", "center_t2": "READY"
        },
        "bottom_right_title": "คำถามสำคัญที่ต้องตอบให้ได้ในขั้นตอน Refine",
        "focus_items": [
            "❓ ผู้ใช้ทำขั้นตอนนี้ไปเพื่อแก้ปัญหาอะไร และทำไมถึงสำคัญ?",
            "❓ ถ้ากรอกข้อมูลผิด หรืออินเทอร์เน็ตหลุด ระบบต้องทำอย่างไร?",
            "❓ มีระบบข้างเคียงหรือ API ไหนที่ต้องเชื่อมโยงข้อมูลด้วยหรือไม่?",
            "❓ ทีม Dev และ QA เข้าใจตรงกันและไม่มีข้อสงสัยค้างคาใจแล้วใช่ไหม?"
        ],
        "focus_quote": "การสละเวลาซักถามให้ละเอียดในขั้นตอน Refine จะช่วยประหยัดเวลาแก้งานในการเขียนโค้ดได้อย่างมหาศาล",
        "key_takeaway": "Refine มือโปร = ถามหา Pain Point ➔ ล้อม Scope ➔ วาด Flow & Mockup ➔ ล็อก AC ละเอียด ➔ Walkthrough ซิงก์กับทีม"
    },

    # 28. Requirement/Requirement Traceability.md
    {
        "file_rel": "Requirement/Requirement Traceability.md",
        "output_name": "28_Requirement_Traceability",
        "top_note_title": "TRACEABILITY MATRIX", "top_note_sub": "END-TO-END RTM",
        "title_plain": "Requirement Traceability เมทริกซ์เชื่อมโยงงาน",
        "title_html": "Requirement Traceability <span class=\"blue-highlight\">เมทริกซ์เชื่อมโยง</span> <span class=\"red-highlight\">ต้นน้ำสู่ปลายน้ำ</span>",
        "subtitle_html": "ติดตามงานตั้งแต่ความต้องการยันปล่อยระบบ <strong>\"ไม่มีหลุด ไม่ตกหล่น ตรวจสอบได้ 100%\"</strong>",
        "notepad_header": "ประโยชน์ของ RTM",
        "notepad_items": [
            "เช็กความครบถ้วน (Coverage 100%)",
            "วิเคราะห์ Impact เมื่อขอแก้งาน",
            "ป้องกันฟังก์ชันตกหล่น",
            "ง่ายต่อการ Audit และส่งมอบ",
            "สร้างความโปร่งใสในโครงการ"
        ],
        "strategy_title": "🎯 1. END-TO-END TRACEABILITY : แผนที่นำทางแห่งความรับผิดชอบ",
        "strategy_bullets": [
            "Requirement Traceability Matrix (RTM) คือตารางเชื่อมโยงความต้องการทางธุรกิจเข้ากับฟังก์ชัน โค้ด และเคสทดสอบ",
            "Forward Traceability : ตรวจสอบว่าทุกความต้องการของธุรกิจถูกนำไปพัฒนาและมีเคสทดสอบรองรับจริง",
            "Backward Traceability : ตรวจสอบว่าทุกโค้ดที่เขียนมีที่มาจากความต้องการทางธุรกิจ ไม่ใช่งานงอกนอกระบบ",
            "Impact Analysis : เมื่อลูกค้าขอแก้ Requirement รู้ได้ทันทีว่ากระทบฟีเจอร์ โค้ด และ Test Cases ไหนบ้าง"
        ],
        "cloud_bubble_html": "🗺️ <strong>Complete Visibility</strong><br>RTM ช่วยให้มองเห็นเส้นทางของทุกความต้องการตั้งแต่จุดเริ่มต้นจนถึงมือผู้ใช้ ไม่มีงานหลุดรอดสายตา",
        "execution_label": "THE RTM STRUCTURE : 6 คอลัมน์หลักในตาราง Traceability Matrix",
        "columns": [
            {"title": "1. BUSINESS REQ ID", "char": "po", "items": ["BR-001, BR-002", "ความต้องการธุรกิจ", "ที่มาจาก Stakeholder", "Business Objective"]},
            {"title": "2. SYSTEM REQ ID", "char": "ba", "items": ["FR-010, FR-011", "Functional Spec", "User Story ID", "เชื่อมโยงกับ BR"]},
            {"title": "3. DESIGN / WIREFRAME", "char": "designer", "items": ["UI Screen ID", "Figma Link", "User Flow Node", "Interaction Spec"]},
            {"title": "4. DEV MODULE & CODE", "char": "dev", "items": ["Source File / Branch", "API Endpoint", "Database Table", "PR / Commit Hash"]},
            {"title": "5. QA TEST CASE ID", "char": "qa", "items": ["TC-101, TC-102", "Positive / Negative", "Automated Test File", "Test Status"]},
            {"title": "6. RELEASE STATUS", "char": "presenter", "items": ["Sprint Number", "UAT Sign-off", "Deploy Status", "Release Version"]}
        ],
        "bottom_left_title": "มิติการตรวจสอบความเชื่อมโยง",
        "skills": [
            {"type": "x", "title": "การวิเคราะห์ผลกระทบ (Impact Analysis)", "code": "Impact Analysis", "desc": "เมื่อมี Change Request เข้ามา สามารถเปิดดู RTM เพื่อประเมินจำนวน Test Cases และไฟล์โค้ดที่ต้องแก้ไขได้ทันที"},
            {"type": "t", "title": "การตรวจสอบความครอบคลุม (Coverage Verification)", "code": "Coverage Check", "desc": "ตรวจสอบว่ามี Requirement ข้อใดที่ยังไม่มี Test Case หรือยังไม่ได้เริ่มพัฒนาหรือไม่"},
            {"type": "i", "title": "การเตรียมตรวจรับและ Audit (Audit Readiness)", "code": "Audit Trail", "desc": "มีหลักฐานอ้างอิงชัดเจนสำหรับคณะกรรมการตรวจรับงานหรือการตรวจสอบตามมาตรฐานสากล"}
        ],
        "bottom_center_title": "สายธารความเชื่อมโยง RTM",
        "loop_data": {
            "s1_title": "1. BUSINESS NEED (BR)", "s1_sub": "🎯 โจทย์ธุรกิจต้นน้ำ",
            "s2_title": "2. USER STORY (FR)", "s2_sub": "📋 แปลงเป็นสเปกระบบ",
            "s3_title": "3. CODE IMPLEMENTATION", "s3_sub": "💻 พัฒนาโค้ด & API",
            "s4_title": "4. TEST CASE & UAT", "s4_sub": "🧪 ทดสอบ & ส่งมอบ",
            "center_t1": "100% TRACEABLE", "center_t2": "& COVERED"
        },
        "bottom_right_title": "ข้อผิดพลาดที่พบบ่อยในการทำ Traceability",
        "focus_items": [
            "สร้างตาราง RTM ตอนเริ่มโครงการแล้วไม่เคยกลับมาอัปเดตอีกเลย",
            "มีฟีเจอร์งอกในระบบโดยไม่มี Requirement ID อ้างอิง",
            "ไม่มีการเชื่อมโยงระหว่าง Requirement ID กับ QA Test Case ID",
            "ทำเอกสารหนาเกินไปจนกลายเป็นภาระแทนที่จะเป็นเครื่องมือช่วยงาน"
        ],
        "focus_quote": "Traceability Matrix คือเครื่องมือสร้างความโปร่งใสและปกป้องคุณภาพงานตั้งแต่ต้นน้ำยันปลายน้ำ",
        "key_takeaway": "RTM = เชื่อม Business Need ➔ User Story ➔ Code Module ➔ Test Case ➔ Release Version ครบถ้วน 100%"
    },

    # 29. Requirement/Requirement.md
    {
        "file_rel": "Requirement/Requirement.md",
        "output_name": "29_Requirement_Fundamentals",
        "top_note_title": "REQUIREMENT 101", "top_note_sub": "FOUNDATIONS & STANDARDS",
        "title_plain": "Requirement คืออะไร ? หัวใจของการพัฒนา",
        "title_html": "Requirement คืออะไร ? <span class=\"blue-highlight\">หัวใจสำคัญ</span> <span class=\"red-highlight\">ของการพัฒนา</span>",
        "subtitle_html": "สะพานเชื่อมระหว่าง <strong>\"ความต้องการทางธุรกิจ\"</strong> กับระบบเทคโนโลยีที่ใช้งานได้จริง",
        "notepad_header": "ประเภท Requirement",
        "notepad_items": [
            "Functional : ระบบทำอะไรได้บ้าง",
            "Non-Functional : คุณภาพระบบ",
            "Business Rules : กฎทางธุรกิจ",
            "User Constraints : ข้อจำกัด",
            "ชัดเจน ถูกต้อง ไม่ขัดแย้ง"
        ],
        "strategy_title": "🎯 1. THE ESSENCE OF REQUIREMENTS : แก่นแท้ของความต้องการ",
        "strategy_bullets": [
            "Requirement คือข้อกำหนด เงื่อนไข และคุณสมบัติที่ระบบต้องมีเพื่อตอบสนองต่อเป้าหมายของผู้ใช้และธุรกิจ",
            "เป็นข้อตกลงและสัญญาใจร่วมกันระหว่างฝั่งธุรกิจ (Business), ผู้ใช้งาน (Users), และทีมเทคนิค (Dev & QA)",
            "เป็นพิมพ์เขียว (Blueprint) สำหรับการออกแบบ UI, การเขียนโค้ด, การวางฐานข้อมูล และการทดสอบระบบ",
            "หาก Requirement ผิดพลาดตั้งแต่เริ่มต้น ทุกอย่างที่สร้างตามมาจะผิดพลาดและสูญเปล่าทั้งหมด"
        ],
        "cloud_bubble_html": "🏛️ <strong>Foundation of Success</strong><br>Requirement ที่ยอดเยี่ยมจะช่วยให้ทีมสร้างของได้ถูกต้องตั้งแต่ครั้งแรก ไม่เสียเวลาสร้างสิ่งที่ไม่ตอบโจทย์",
        "execution_label": "REQUIREMENT SPECTRUM : 6 ด้านที่ต้องระบุให้ครบถ้วน",
        "columns": [
            {"title": "1. BUSINESS GOAL", "char": "po", "items": ["วัตถุประสงค์ธุรกิจ", "ปัญหาที่ต้องการแก้", "ผลลัพธ์ที่คาดหวัง", "Success Metrics"]},
            {"title": "2. USER PERSONA", "char": "ba", "items": ["ใครเป็นผู้ใช้งาน?", "บทบาทและหน้าที่", "บริบทการใช้งาน", "ความต้องการหลัก"]},
            {"title": "3. FUNCTIONAL SPEC", "char": "flow", "items": ["ระบบต้องทำอะไรได้", "ฟังก์ชันการทำงาน", "User Flow ชัดเจน", "Input ➔ Output"]},
            {"title": "4. NON-FUNCTIONAL", "char": "dev", "items": ["ความเร็ว (Speed)", "ความปลอดภัย (Security)", "ความเสถียร (Reliability)", "การรองรับโหลด (Scale)"]},
            {"title": "5. BUSINESS RULES", "char": "designer", "items": ["สูตรคำนวณราคา", "เงื่อนไขโปรโมชัน", "สิทธิ์การเข้าถึงข้อมูล", "กฎหมายที่เกี่ยวข้อง"]},
            {"title": "6. ACCEPTANCE CRITERIA", "char": "qa", "items": ["Given / When / Then", "เกณฑ์การยอมรับงาน", "เงื่อนไขความถูกต้อง", "พร้อมสำหรับการเทส"]}
        ],
        "bottom_left_title": "Functional vs Non-Functional Requirements",
        "skills": [
            {"type": "x", "title": "Functional Requirements (ระบบทำอะไรได้)", "code": "Functional", "desc": "เช่น สมัครสมาชิก, ค้นหาสินค้า, ชำระเงินผ่านบัตรเครดิต, ออกใบกำกับภาษี, อนุมัติเอกสาร"},
            {"type": "t", "title": "Non-Functional Requirements (คุณภาพของระบบ)", "code": "Non-Functional", "desc": "เช่น หน้าจอโหลดภายใน 2 วินาที, เข้ารหัสข้อมูลด้วย AES-256, ระบบ Uptime 99.9%, รองรับ 10,000 CCU"},
            {"type": "i", "title": "Constraint & Assumption (ข้อจำกัดและสมมติฐาน)", "code": "Constraints", "desc": "เช่น ต้องทำงานบน Chrome และ Safari, ต้องเชื่อมต่อกับระบบ ERP เดิม, ต้องรองรับ PDPA"}
        ],
        "bottom_center_title": "โครงสร้าง Requirement ที่สมบูรณ์",
        "loop_data": {
            "s1_title": "1. BUSINESS NEED", "s1_sub": "🎯 ทำความเข้าใจทำไมต้องทำ",
            "s2_title": "2. FUNCTIONAL SPEC", "s2_sub": "📋 กำหนดสิ่งที่ระบบต้องทำ",
            "s3_title": "3. NON-FUNCTIONAL", "s3_sub": "🛡️ ระบุมาตรฐานคุณภาพ",
            "s4_title": "4. ACCEPTANCE CRITERIA", "s4_sub": "✅ กำหนดเกณฑ์วัดผลจริง",
            "center_t1": "COMPLETE", "center_t2": "BLUEPRINT"
        },
        "bottom_right_title": "คุณสมบัติของ Requirement ที่ยอดเยี่ยม (IEEE Standards)",
        "focus_items": [
            "Clear & Unambiguous : ชัดเจน ตรงไปตรงมา ตีความได้แบบเดียว",
            "Complete : ข้อมูลครบถ้วน ทั้งกรณีปกติและกรณีผิดพลาด",
            "Consistent : ไม่ขัดแย้งกับ Requirement ข้ออื่นในระบบ",
            "Verifiable & Testable : สามารถทดสอบและพิสูจน์ผลลัพธ์ได้จริง"
        ],
        "focus_quote": "Requirement ที่ดีคือรากฐานที่มั่นคงที่สุดของโครงการซอฟต์แวร์ทุกประเภท",
        "key_takeaway": "Requirement = ปัญหาธุรกิจ (Need) + ฟังก์ชันระบบ (Functional) + มาตรฐานคุณภาพ (Non-Functional) + เกณฑ์วัดผล (AC)"
    },

    # 30. Requirement/Workshop - Requirement.md
    {
        "file_rel": "Requirement/Workshop - Requirement.md",
        "output_name": "30_Requirement_Workshop",
        "top_note_title": "WORKSHOP ELICITATION", "top_note_sub": "FACILITATION PLAYBOOK",
        "title_plain": "เทคนิคจัด Workshop เก็บ Requirement ให้ตรงจุด",
        "title_html": "เทคนิคจัด Workshop <span class=\"blue-highlight\">เก็บ Requirement</span> <span class=\"red-highlight\">ให้ตรงจุด</span>",
        "subtitle_html": "ดึงความต้องการที่แท้จริงจาก Stakeholder <strong>\"อย่างมีประสิทธิภาพและสนุกสนาน\"</strong>",
        "notepad_header": "หัวใจของ Workshop",
        "notepad_items": [
            "เตรียมโจทย์และเทมเพลตล่วงหน้า",
            "เชิญ Decision Maker ตัวจริง",
            "สร้างบรรยากาศที่เปิดกว้าง",
            "ใช้กิจกรรม Interactive",
            "จบด้วย Action Plan ชัดเจน"
        ],
        "strategy_title": "🎯 1. THE FACILITATION MASTERY : พลังของการดึงความคิดเห็นร่วมกัน",
        "strategy_bullets": [
            "Requirement Workshop ช่วยเปลี่ยนความคิดเห็นที่กระจัดกระจายให้กลายเป็นเป้าหมายและความเข้าใจร่วมกัน",
            "ใช้เทคนิค User Journey Mapping เพื่อพา Stakeholder เดินตามขั้นตอนการทำงานจริงตั้งแต่ต้นจนจบ",
            "ใช้ Silent Brainstorming (เขียน Post-it เงียบๆ ก่อนแปะ) เพื่อไม่ให้คนเสียงดังครอบงำห้องประชุม",
            "ใช้ Dot Voting และ MoSCoW เพื่อให้ทุกคนมีส่วนร่วมในการตัดสินใจเลือก Scope อย่างเป็นประชาธิปไตย"
        ],
        "cloud_bubble_html": "💡 <strong>Interactive Alignment</strong><br>Workshop ที่ยอดเยี่ยมช่วยสร้างความผูกพัน (Buy-in) และทำให้ทุกคนพร้อมขับเคลื่อนโปรเจกต์ไปด้วยกัน",
        "execution_label": "WORKSHOP TIMELINE : 6 ช่วงเวลาสำคัญในการนำ Workshop",
        "columns": [
            {"title": "1. PREPARATION", "char": "presenter", "items": ["ตั้งเป้าหมายเซสชัน", "เชิญผู้เกี่ยวข้องตัวจริง", "เตรียม Miro/Post-it", "ส่งบรีฟล่วงหน้า"]},
            {"title": "2. ICEBREAK & GOAL", "char": "po", "items": ["เปิดเซสชันสร้างพลัง", "ชี้แจงเป้าหมายห้อง", "กำหนด Ground Rules", "สร้าง Safe Space"]},
            {"title": "3. JOURNEY MAPPING", "char": "flow", "items": ["เดินตาม User Flow", "แปะ Post-it ปัญหา", "ระบุ Pain Points", "ค้นหาโอกาสใหม่"]},
            {"title": "4. 5 WHYS & CLUSTER", "char": "ba", "items": ["เจาะลึกหาสาเหตุจริง", "จัดกลุ่มไอเดียคล้ายกัน", "ตั้งชื่อ Theme งาน", "ตัดความซ้ำซ้อน"]},
            {"title": "5. DOT VOTING", "char": "designer", "items": ["แจกสติกเกอร์โหวต", "โหวตไอเดีย Impact สูง", "จัดเข้า MoSCoW", "คัดเลือก MVP Scope"]},
            {"title": "6. ACTION & WRAP", "char": "qa", "items": ["สรุปข้อตกลงร่วมกัน", "มอบหมาย Owner ชัดเจน", "กำหนด Next Steps", "ถ่ายภาพบันทึกผล"]}
        ],
        "bottom_left_title": "เครื่องมือและกิจกรรมยอดนิยมใน Workshop",
        "skills": [
            {"type": "x", "title": "User Journey Mapping (แผนผังประสบการณ์)", "code": "Journey Mapping", "desc": "มองเห็นขั้นตอน อารมณ์ความรู้สึก และปัญหาของลูกค้าในแต่ละ Touchpoint"},
            {"type": "t", "title": "Silent Brainstorming & Dot Voting", "code": "Brainstorm & Vote", "desc": "ให้เวลาทุกคนเขียนไอเดียส่วนตัว 5 นาที แล้วนำมาแปะพร้อมโหวตเลือกอย่างเป็นกลาง"},
            {"type": "i", "title": "The 5 Whys Technique (ถามทำไม 5 ครั้ง)", "code": "5 Whys Root Cause", "desc": "ถามเจาะลึกลงไปเรื่อยๆ เพื่อค้นหาต้นตอที่แท้จริงของปัญหา ไม่ใช่แค่แก้อาการภายนอก"}
        ],
        "bottom_center_title": "วงจรการดำเนินกิจกรรม Workshop",
        "loop_data": {
            "s1_title": "1. SET PROBLEM CONTEXT", "s1_sub": "🎯 ตั้งโจทย์ปัญหาให้ชัด",
            "s2_title": "2. DIVERGE IDEAS", "s2_sub": "💡 ระดมไอเดียอย่างอิสระ",
            "s3_title": "3. CONVERGE & VOTE", "s3_sub": "🗳️ จัดกลุ่มและโหวตเลือก",
            "s4_title": "4. AGREE ON ACTION PLAN", "s4_sub": "📝 สรุปข้อตกลงและงานต่อ",
            "center_t1": "HIGH", "center_t2": "ENGAGEMENT"
        },
        "bottom_right_title": "ข้อควรระวังในห้อง Workshop",
        "focus_items": [
            "ปล่อยให้ผู้เข้าร่วมบางคนผูกขาดการพูดตลอดทั้งเซสชัน",
            "เถียงกันเรื่องรายละเอียดทางเทคนิคจนลืมโฟกัสปัญหาของผู้ใช้",
            "จบการประชุมโดยไม่มีการสรุปข้อตกลงและ Next Steps ที่ชัดเจน",
            "เปิดรับทุกไอเดียโดยไม่มีการจัดลำดับความสำคัญ (No Scope Control)"
        ],
        "focus_quote": "Workshop ที่ดีต้องได้ผลลัพธ์ที่เป็นรูปธรรมและมี Action Plan ชัดเจน ไม่ใช่แค่การคุยกันสนุกสนาน",
        "key_takeaway": "Workshop มือโปร = เตรียมโจทย์ล่วงหน้า + ระดมความคิดเห็นอย่างเปิดกว้าง + แมป Journey + โหวต Priority + สรุป Action Plan ชัดเจน"
    }
]

ALL_DOCS.extend(FINAL_SPECS)

print(f"==================================================")
print(f"🚀 Starting ZURI High-Grade Master Poster Generation Pipeline")
print(f"📁 Target documents: {len(ALL_DOCS)}")
print(f"🎨 Aesthetic: ZURI Anime Storytelling v5 / Orange Ember")
print(f"==================================================")

rendered_images = []
chrome_profile = tempfile.mkdtemp(prefix="zuri-signal-chrome-")
atexit.register(shutil.rmtree, chrome_profile, ignore_errors=True)

for idx, doc in enumerate(ALL_DOCS, 1):
    out_name = doc["output_name"]
    html_path = os.path.join(HTML_DIR, f"{out_name}.html")
    png_path = os.path.join(OUTPUT_DIR, f"{out_name}.png")
    
    # 1. Render High-Grade HTML
    html_content = render_zuri_signal_poster(doc)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # 2. Capture High-DPI 1200x1200px Screenshot via Headless Chrome
    file_url = "file:///" + html_path.replace("\\", "/")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--user-data-dir={chrome_profile}",
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
        print(f"[{idx:02d}/30] ✅ High-Grade Poster Rendered: {out_name}.png ({file_size_kb:.1f} KB) in {dt:.2f}s")
        rendered_images.append({
            "idx": idx,
            "filename": f"{out_name}.png",
            "html_filename": f"html/{out_name}.html",
            "title": doc["title_plain"],
            "tag": doc["top_note_title"],
            "source": doc["file_rel"],
            "size_kb": f"{file_size_kb:.1f} KB"
        })
    else:
        print(f"[{idx:02d}/30] ❌ FAILED: {out_name}.png - Error: {res.stderr}")

print(f"\n🎉 Successfully Generated ALL {len(rendered_images)} / {len(ALL_DOCS)} High-Grade Infographic Posters!")

# Update Gallery index.html
gallery_cards_html = []
for item in rendered_images:
    gallery_cards_html.append(f"""
    <div class="gallery-card" data-title="{item['title'].lower()}" data-tag="{item['tag'].lower()}">
      <div class="card-img-wrapper" onclick="openModal('{item['filename']}', '{item['title']}')">
        <img src="{item['filename']}" alt="{item['title']}" loading="lazy" />
        <div class="img-overlay">🔍 คลิกดูภาพโปสเตอร์ขนาดเต็ม</div>
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
<title>ZURI Signal System Infographics Gallery (30 Posters)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600;700;800;900&family=Mali:wght@500;600;700&family=Kanit:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {{
  --brand-amber: #E8820C;
  --brand-amber-dark: #B86A08;
  --brand-amber-light: #FFF8F0;
  --slate-900: #0F172A;
  --slate-800: #1E293B;
  --slate-700: #334155;
  --slate-100: #F1F5F9;
  --slate-50: #F8FAFC;
  --border-color: #CBD5E1;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'Prompt', -apple-system, sans-serif;
  background-color: #F1F5F9;
  color: var(--slate-900);
  padding: 32px 24px;
}}

.container {{
  max-width: 1440px;
  margin: 0 auto;
}}

.hero {{
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
  color: #FFFFFF;
  border-radius: 20px;
  padding: 36px 40px;
  margin-bottom: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.15);
  border: 2px solid #334155;
}}

.hero-left h1 {{
  font-family: 'Kanit', sans-serif;
  font-size: 38px;
  font-weight: 900;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}}
.hero-left h1 span {{ color: var(--brand-amber); }}
.hero-left p {{
  font-size: 16px;
  color: #94A3B8;
  max-width: 700px;
  line-height: 1.6;
}}

.hero-stats {{
  display: flex;
  gap: 16px;
}}
.stat-box {{
  background: rgba(255,255,255,0.06);
  border: 1.5px solid rgba(255,255,255,0.12);
  border-radius: 14px;
  padding: 16px 22px;
  text-align: center;
}}
.stat-number {{
  font-family: 'Kanit', sans-serif;
  font-size: 36px;
  font-weight: 900;
  color: var(--brand-amber);
}}
.stat-label {{
  font-size: 13px;
  color: #E2E8F0;
  margin-top: 2px;
}}

.filter-bar {{
  background: #FFFFFF;
  border: 2px solid var(--border-color);
  border-radius: 14px;
  padding: 14px 18px;
  margin-bottom: 28px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 3px 6px rgba(0,0,0,0.02);
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

.gallery-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}}

.gallery-card {{
  background: #FFFFFF;
  border: 2.5px solid #0F172A;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 4px 6px 0px #0F172A;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}}
.gallery-card:hover {{
  transform: translateY(-4px);
  box-shadow: 6px 10px 0px #0F172A;
}}

.card-img-wrapper {{
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  background: #E2E8F0;
  cursor: pointer;
  overflow: hidden;
  border-bottom: 2.5px solid #0F172A;
}}
.card-img-wrapper img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}}
.card-img-wrapper:hover img {{
  transform: scale(1.02);
}}
.img-overlay {{
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
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
  background: #FFFDF9;
}}

.card-tag {{
  font-family: 'Kanit', sans-serif;
  font-size: 12px;
  font-weight: 800;
  color: #78350F;
  background: #FEF08A;
  border: 1px solid #FACC15;
  padding: 3px 10px;
  border-radius: 6px;
  align-self: flex-start;
}}

.card-title {{
  font-family: 'Kanit', sans-serif;
  font-size: 17px;
  font-weight: 800;
  color: var(--slate-900);
  line-height: 1.3;
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
  margin-top: 8px;
}}
.btn-download, .btn-view-html {{
  flex: 1;
  text-align: center;
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
  padding: 8px 10px;
  border-radius: 8px;
  border: 2px solid #0F172A;
  transition: all 0.2s;
}}
.btn-download {{
  background: #0F172A;
  color: #FFFFFF;
  box-shadow: 2px 2px 0px #0F172A;
}}
.btn-download:hover {{
  background: var(--brand-amber);
  border-color: var(--brand-amber);
}}
.btn-view-html {{
  background: #EFF6FF;
  color: #1D4ED8;
  box-shadow: 2px 2px 0px #0F172A;
}}
.btn-view-html:hover {{
  background: #DBEAFE;
}}

.modal {{
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.85);
  z-index: 999;
  justify-content: center;
  align-items: center;
  padding: 24px;
}}
.modal.active {{ display: flex; }}
.modal-content {{
  max-width: 90vh;
  max-height: 90vh;
  position: relative;
  background: #FFFFFF;
  border: 3px solid #0F172A;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0,0,0,0.3);
}}
.modal-img {{ width: 100%; height: 100%; display: block; }}
.modal-close {{
  position: absolute;
  top: 12px;
  right: 12px;
  background: #0F172A;
  color: #FFFFFF;
  border: 2px solid #FFFFFF;
  width: 38px;
  height: 38px;
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
  <div class="hero">
    <div class="hero-left">
      <h1>ZURI <span>Master Posters</span> Gallery</h1>
      <p>คลังภาพสรุปความรู้ระดับ High-Grade Comic / Illustrated Cheat-Sheets (1200x1200px) สำหรับเอกสารทั้ง 30 ไฟล์ใน Fleet Scope ออกแบบด้วยลายเส้นและการจัดวางระดับพรีเมียมตามมาตรฐานสากล</p>
    </div>
    <div class="hero-stats">
      <div class="stat-box">
        <div class="stat-number">30</div>
        <div class="stat-label">ภาพโปสเตอร์ทั้งหมด</div>
      </div>
      <div class="stat-box">
        <div class="stat-number">100%</div>
        <div class="stat-label">ครอบคลุมทุกไฟล์</div>
      </div>
    </div>
  </div>

  <div class="filter-bar">
    <input type="text" class="search-input" id="searchBox" placeholder="🔍 ค้นหาหัวข้อ, หมวดหมู่ หรือชื่อไฟล์ (เช่น AC, Agile, Backlog, UAT, Case Study, MoSCoW)..." onkeyup="filterCards()">
  </div>

  <div class="gallery-grid" id="galleryGrid">
    {"".join(gallery_cards_html)}
  </div>
</div>

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

print(f"🎉 Updated high-grade interactive gallery: {os.path.join(OUTPUT_DIR, 'index.html')}")
