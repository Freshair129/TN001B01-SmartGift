# -*- coding: utf-8 -*-
"""
Structured datasets for all 30 documents in Visual-Agent-Fleet-Scope.
Each entry maps directly to 1 file in the workspace.
"""

DOCUMENTS = [
    # 1. BA/Doc for BA-PO.md (Matched with sample reference)
    {
        "file_rel": "BA/Doc for BA-PO.md",
        "output_name": "BA_Doc_for_BA_PO",
        "tag": "ZURI ACADEMY • DAY 30",
        "title_plain": "เอกสารที่ BA / PO ควรมี ?",
        "title_html": "เอกสารที่ BA / PO <span class=\"danger-highlight\">ควรมี ?</span>",
        "subtitle": "มีเท่าที่จำเป็น แต่ต้องพอให้ทีมเข้าใจและทำงานต่อได้",
        "sticky_text": "เอกสารชัด ทีมไม่งง งานไม่หลุด! 💡",
        "equation": "เอกสารที่ดี = เป้าหมายชัด + ขอบเขตชัด + รายละเอียดพอ + ส่งต่อทีมได้",
        "card1_title": "1) ความหมาย",
        "card1_subtitle": "เอกสารของ BA / PO คือชุดของข้อมูลที่ช่วยให้ทีมเข้าใจตรงกันว่า:",
        "card1_items": [
            "ทำอะไร และทำไปเพื่ออะไร",
            "ขอบเขตแค่ไหน (In/Out Scope)",
            "ใครเป็นผู้ใช้งาน และ Flow เป็นอย่างไร",
            "แบบไหนถึงเรียกว่าทำเสร็จ (Done)"
        ],
        "card2_title": "2) เอกสารหลักที่ควรมี",
        "card2_items": [
            {"title": "Business Need / Problem Statement", "desc": "เป้าหมายธุรกิจ", "icon": "target"},
            {"title": "Requirement / User Story", "desc": "สิ่งที่ระบบต้องทำ", "icon": "doc"},
            {"title": "Flow / Screen / Wireframe", "desc": "ขั้นตอนและหน้าจอ", "icon": "screen"},
            {"title": "Business Rule / Acceptance Criteria", "desc": "เงื่อนไขยอมรับ", "icon": "check"},
            {"title": "Backlog / Priority / UAT Cases", "desc": "ลำดับงาน & การตรวจรับ", "icon": "layers"}
        ],
        "card2_footer": "ไม่จำเป็นต้องแยกเป็นหลายไฟล์เสมอไป แต่ข้อมูลสำคัญควรมีครบ",
        "card3_title": "3) ลำดับเอกสารที่ใช้บ่อย",
        "flow_steps": [
            {"title": "Business Need", "icon": "target"},
            {"title": "Requirement", "icon": "doc"},
            {"title": "Flow / Screen", "icon": "screen"},
            {"title": "Acceptance Criteria", "icon": "check"},
            {"title": "Dev / QA / UAT", "icon": "users"}
        ],
        "card3_subcaption": "ยิ่งข้อมูลต่อกันได้ ทีมยิ่งทำงานต่อได้เร็ว",
        "card4_title": "4) เช็คง่าย ๆ ว่าเอกสารพอไหม",
        "card4_items": [
            "อ่านแล้วรู้เป้าหมายของงาน",
            "In Scope / Out of Scope ชัดเจน",
            "เห็น Flow หรือหน้าจอที่เกี่ยวข้อง",
            "มีเงื่อนไขสำคัญและผลลัพธ์ที่คาดหวัง",
            "ทีม Dev / QA อ่านแล้วทำงานต่อได้",
            "เวลาเปลี่ยน Requirement รู้ว่ากระทบอะไรบ้าง"
        ],
        "card4_warning": "ถ้าอ่านแล้วต้องถามกลับทุกบรรทัด แปลว่ายังไม่พอ",
        "card5_title": "5) สรุป",
        "card5_icon": "link",
        "card5_text": "เอกสารของ BA / PO <strong>ไม่ใช่ทำให้เยอะ</strong> แต่ต้องทำให้พอ เพื่อให้ทีมเข้าใจตรงกัน ลดการเดา ลด Rework และส่งงานต่อได้ตั้งแต่ต้นจนจบ",
        "memory_pills": ["BA / PO ควรมี", "เป้าหมายชัด", "รายละเอียดชัด", "ส่งต่อทีมได้"]
    },

    # 2. PO/Doc for BA-PO.md
    {
        "file_rel": "PO/Doc for BA-PO.md",
        "output_name": "PO_Doc_for_BA_PO",
        "tag": "ZURI PRODUCT • PO VIEW",
        "title_plain": "เอกสารที่ PO ต้องถือและดูแล",
        "title_html": "เอกสารที่ PO <span class=\"highlight\">ต้องถือและดูแล</span>",
        "subtitle": "ควบคุมทิศทาง คุมคุณค่า และจัดลำดับงานให้คุ้มค่าที่สุด",
        "sticky_text": "PO ชี้เป้าชัด ทีมโฟกัสถูกจุด ส่งมอบคุณค่าเต็มร้อย! 💡",
        "equation": "PO เอกสารนิ่ง = Product Vision + Prioritized Backlog + Release Strategy",
        "card1_title": "1) บทบาทของ PO ต่อเอกสาร",
        "card1_subtitle": "PO ไม่ใช่แค่คนสั่งงาน แต่เป็นเจ้าของวิสัยทัศน์ที่ต้องตอบได้ว่า:",
        "card1_items": [
            "ฟีเจอร์นี้สร้าง Value อะไรให้ธุรกิจและผู้ใช้",
            "ทำไมต้องทำตอนนี้ และงานไหนควรทำก่อน-หลัง",
            "Release ไหนต้องปล่อยอะไรสู่ตลาด",
            "เกณฑ์การตรวจรับมอบงาน (Acceptance) คืออะไร"
        ],
        "card2_title": "2) สิ่งที่ PO ต้องมีในมือ",
        "card2_items": [
            {"title": "Product Vision & Roadmap", "desc": "ทิศทางระยะสั้น-ยาว", "icon": "target"},
            {"title": "Prioritized Product Backlog", "desc": "งานเรียงลำดับ Value", "icon": "layers"},
            {"title": "Epic & User Story with Value", "desc": "โจทย์ที่ชัดเจน", "icon": "doc"},
            {"title": "Release Plan & Milestone", "desc": "กำหนดการปล่อยของ", "icon": "clock"},
            {"title": "Feedback & Success Metrics", "desc": "ตัวชี้วัดความสำเร็จ", "icon": "sparkles"}
        ],
        "card2_footer": "PO ถือเข็มทิศ Value ให้ทีมเสมอ",
        "card3_title": "3) วงจรการบริหารจัดการของ PO",
        "flow_steps": [
            {"title": "Vision", "icon": "target"},
            {"title": "Backlog", "icon": "layers"},
            {"title": "Refine", "icon": "doc"},
            {"title": "Sprint Commit", "icon": "screen"},
            {"title": "Accept & Feedback", "icon": "sparkles"}
        ],
        "card3_subcaption": "ตัดสินใจบนพื้นฐานของข้อมูลและผลตอบรับจริง",
        "card4_title": "4) สัญญาณเตือน PO เอกสารไม่พอ",
        "card4_items": [
            "ตอบไม่ได้ว่าฟีเจอร์นี้ทำไปเพื่ออะไร",
            "Backlog ไม่มีลำดับความสำคัญ ทุกอย่างด่วนหมด",
            "ปล่อยให้ Dev คิด Business Logic เอง",
            "เปลี่ยนทิศทางกะทันหันโดยไม่มีข้อมูลรองรับ",
            "ไม่เคยตรวจรับงานตาม AC ที่วางไว้"
        ],
        "card4_warning": "ถ้า PO ไม่ชัดเจน ทีมจะหลงทางและเสียแรงฟรี",
        "card5_title": "5) สรุป",
        "card5_icon": "shield",
        "card5_text": "เอกสารของ PO คือ<strong>เครื่องมือนำทางธุรกิจ</strong> เพื่อให้มั่นใจว่าทุกนาทีที่ทีม Dev ลงแรง จะสร้างผลตอบแทนสูงสุดให้แก่ผู้ใช้และองค์กร",
        "memory_pills": ["PO เอกสารดี", "Vision ชัด", "Backlog นิ่ง", "สร้าง Value จริง"]
    },

    # 3. Acceptance Criteria.md
    {
        "file_rel": "Acceptance Criteria.md",
        "output_name": "Acceptance_Criteria",
        "tag": "ZURI ACADEMY • DEV & QA READY",
        "title_plain": "Acceptance Criteria เขียนยังไง ?",
        "title_html": "Acceptance Criteria <span class=\"highlight\">เขียนยังไง ?</span>",
        "subtitle": "เงื่อนไขที่บอกว่างานนี้ต้องเป็นแบบไหน ถึงจะเรียกว่า 'เสร็จ'",
        "sticky_text": "AC ชัด Dev โค้ดตรง QA เทสง่าย ผ่านฉลุย! 💡",
        "equation": "User Story = สิ่งที่อยากได้ | Acceptance Criteria = แบบไหนถึงเรียกว่าเสร็จ",
        "card1_title": "1) Acceptance Criteria คืออะไร?",
        "card1_subtitle": "เงื่อนไขและข้อกำหนดที่ใช้ยืนยันความถูกต้องของงาน:",
        "card1_items": [
            "ตอบคำถามว่า: แบบไหนเรียกว่าเสร็จและส่งมอบได้",
            "ช่วยให้ Dev เข้าใจขอบเขตการเขียนโค้ด",
            "ช่วยให้ QA นำไปแตก Test Case ได้แม่นยำ",
            "ลดการถกเถียงและคาดเดาความต้องการเอง"
        ],
        "card2_title": "2) โครงสร้าง Given / When / Then",
        "card2_items": [
            {"title": "Given (สถานะเริ่มต้น)", "desc": "เงื่อนไขก่อนเริ่มทำ Action", "icon": "doc"},
            {"title": "When (การกระทำ)", "desc": "สิ่งที่ผู้ใช้กดหรือทำในระบบ", "icon": "screen"},
            {"title": "Then (ผลลัพธ์ที่เกิด)", "desc": "สิ่งที่ระบบต้องแสดงหรือบันทึก", "icon": "check"},
            {"title": "And (เงื่อนไขเสริม)", "desc": "รายละเอียดเพิ่มเติม", "icon": "link"}
        ],
        "card2_footer": "เขียนให้อ่านง่าย กระชับ และตรงไปตรงมา",
        "card3_title": "3) ตัวอย่าง AC ที่ดี vs ควรเลี่ยง",
        "flow_steps": [
            {"title": "Given ข้อมูลครบ", "icon": "doc"},
            {"title": "When กด Submit", "icon": "screen"},
            {"title": "Then ส่งคำขอใหม่", "icon": "check"},
            {"title": "And สถานะ Pending", "icon": "layers"}
        ],
        "card3_subcaption": "ชัดเจนจน QA สามารถนำไปเขียน Test Script ได้ทันที",
        "card4_title": "4) ข้อความกำกวมที่ควรระวัง",
        "card4_items": [
            "⚠️ 'ระบบต้องใช้งานง่าย' ➔ ไม่ระบุนิยามความง่าย",
            "⚠️ 'ต้องแจ้งเตือน' ➔ ไม่บอกช่องทางและข้อความ",
            "⚠️ 'กดแล้วต้องเร็ว' ➔ ไม่ระบุเวลาเป็นวินาที",
            "⚠️ 'ข้อมูลต้องถูกต้อง' ➔ ไม่บอกเงื่อนไข Validation",
            "⚠️ 'ระบบรองรับทุกคน' ➔ ไม่ระบุประเภท Role"
        ],
        "card4_warning": "เปลี่ยนคำคุณศัพท์ลอย ๆ ให้เป็นเงื่อนไขที่วัดผลได้จริง",
        "card5_title": "5) เช็กลิสต์ก่อนส่งงาน",
        "card5_icon": "check",
        "card5_text": "AC ที่ดีไม่จำเป็นต้องยาว <strong>แต่ต้อง Test ได้ วัดผลได้</strong> ครอบคลุมทั้ง Positive, Negative และ Edge Cases สำคัญครบถ้วน",
        "memory_pills": ["AC ชัดเจน", "Given / When / Then", "วัดผลได้", "Test ผ่านได้จริง"]
    },

    # 4. Agile.md
    {
        "file_rel": "Agile.md",
        "output_name": "Agile_Mindset",
        "tag": "ZURI AGILE • TEAM FOUNDATION",
        "title_plain": "ใน Agile มีใครบ้าง ? แต่ละคนทำอะไร ?",
        "title_html": "ใน Agile มีใครบ้าง ? <span class=\"highlight\">แต่ละคนทำอะไร ?</span>",
        "subtitle": "รวมพลังทีมส่งมอบคุณค่าอย่างต่อเนื่องและปรับตัวได้ไว",
        "sticky_text": "หน้าที่ชัดเจน ร่วมมือใกล้ชิด ส่งงานไว ไม่มีสะดุด! 💡",
        "equation": "Agile Team = Product Owner (Value) + Scrum Master (Flow) + Dev Team (Build)",
        "card1_title": "1) หัวใจสำคัญของ Agile",
        "card1_subtitle": "การทำงานที่เน้นการสื่อสาร การส่งมอบจริง และการปรับตัว:",
        "card1_items": [
            "เน้นส่งมอบซอฟต์แวร์ที่ใช้งานได้จริงทีละรอบ (Sprint)",
            "ปรับเปลี่ยนตามความต้องการและ Feedback ได้ทันท่วงที",
            "สื่อสารข้ามสายงานโดยตรง ไม่รอส่งต่อเอกสารหนาๆ",
            "ทุกคนในทีมรับผิดชอบเป้าหมายร่วมกัน"
        ],
        "card2_title": "2) 3 บทบาทหลักใน Scrum Team",
        "card2_items": [
            {"title": "Product Owner (PO)", "desc": "กำหนด Vision จัด Backlog และเลือกงานที่มี Value สูงสุด", "icon": "target"},
            {"title": "Scrum Master (SM)", "desc": "ดูแล Process ขจัดอุปสรรค และช่วยให้ทีมทำงานลื่นไหล", "icon": "shield"},
            {"title": "Development Team", "desc": "วิเคราะห์ ออกแบบ เขียนโค้ด และทดสอบระบบคุณภาพ", "icon": "users"}
        ],
        "card2_footer": "ไม่มีลำดับขั้นแบบเจ้านาย-ลูกน้อง แต่ทำงานแบบคู่คิด",
        "card3_title": "3) จังหวะการส่งมอบงานใน Agile",
        "flow_steps": [
            {"title": "Backlog", "icon": "layers"},
            {"title": "Sprint Plan", "icon": "doc"},
            {"title": "Daily Build", "icon": "screen"},
            {"title": "Review Demo", "icon": "sparkles"},
            {"title": "Retro Improve", "icon": "shield"}
        ],
        "card3_subcaption": "รอบการทำงานสั้น 1-2 สัปดาห์ ส่งมอบชิ้นงานที่พร้อมใช้",
        "card4_title": "4) ความเข้าใจผิดยอดฮิต",
        "card4_items": [
            "❌ Agile คือไม่ต้องทำเอกสารอะไรเลย",
            "❌ Agile คือเปลี่ยน Requirement ได้ทุกนาทีตามใจชอบ",
            "❌ PO มีหน้าที่แค่สั่งงาน ส่วน Dev ทำตามคำสั่ง",
            "❌ Agile คือการเร่งงานให้เสร็จไวขึ้นโดยไม่สนใจคุณภาพ"
        ],
        "card4_warning": "Agile คือวินัยในการส่งมอบคุณค่า ไม่ใช่การทำงานไร้ระเบียบ",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "Agile สำเร็จได้เมื่อ<strong>ทุกคนเข้าใจบทบาทของตนเอง</strong> ไว้วางใจซึ่งกันและกัน และมุ่งมั่นส่งมอบสิ่งที่มีคุณค่าที่สุดให้แก่ผู้ใช้งาน",
        "memory_pills": ["Agile Team", "PO ชี้เป้า", "SM เคลียร์ทาง", "Dev สร้างจริง"]
    },

    # 5. Agile Ceremonies.md
    {
        "file_rel": "Agile Ceremonies.md",
        "output_name": "Agile_Ceremonies",
        "tag": "ZURI SCRUM • 5 CEREMONIES",
        "title_plain": "Agile Ceremonies 5 พิธีกรรมที่ต้องรู้ !",
        "title_html": "Agile Ceremonies <span class=\"highlight\">5 พิธีกรรมที่ต้องรู้ !</span>",
        "subtitle": "ไม่ใช่การประชุมเยอะ แต่คือจังหวะซิงก์งานที่ถูกต้องและมีประสิทธิภาพ",
        "sticky_text": "ประชุมถูกเรื่อง ถูกเวลา งานเดินหน้าไม่มีสะดุด! 💡",
        "equation": "Scrum Events = Plan งาน + Sync ทุกวัน + เตรียมล่วงหน้า + Demo รับ Feedback + ปรับปรุงทีม",
        "card1_title": "1) Sprint Planning & Daily Scrum",
        "card1_subtitle": "เริ่มต้นและขับเคลื่อนประจำวัน:",
        "card1_items": [
            "Sprint Planning: เลือกงานจาก Backlog กำหนด Sprint Goal และวางแผนงานร่วมกัน",
            "Daily Scrum (15 นาที): เมื่อวานทำอะไร วันนี้จะทำอะไร มีปัญหาอะไรติดขัดไหม",
            "เน้น sync ปัญหาเพื่อเคลียร์บล็อกเกอร์ให้เร็วที่สุด"
        ],
        "card2_title": "2) Review, Retro & Refinement",
        "card2_items": [
            {"title": "Sprint Review", "desc": "Demo ชิ้นงานจริงให้ Stakeholder ดูเพื่อรับ Feedback", "icon": "sparkles"},
            {"title": "Sprint Retrospective", "desc": "ทีมคุยทบทวนวิธีทำงาน หาจุดปรับปรุงในรอบถัดไป", "icon": "shield"},
            {"title": "Backlog Refinement", "desc": "ขัดเกลางานล่วงหน้า แตก Story และใส่ AC ให้พร้อม", "icon": "doc"}
        ],
        "card2_footer": "ทุกกิจกรรมต้องมี Time-box ชัดเจน",
        "card3_title": "3) ลำดับการเกิด Ceremonies ใน 1 Sprint",
        "flow_steps": [
            {"title": "Planning", "icon": "target"},
            {"title": "Daily Sync", "icon": "clock"},
            {"title": "Refinement", "icon": "doc"},
            {"title": "Review", "icon": "sparkles"},
            {"title": "Retro", "icon": "shield"}
        ],
        "card3_subcaption": "หมุนเวียนต่อเนื่องทุกสัปดาห์หรือทุก 2 สัปดาห์",
        "card4_title": "4) สัญญาณอันตรายในพิธีกรรม",
        "card4_items": [
            "Daily กลายเป็นเวทีรายงานความคืบหน้าให้หัวหน้า",
            "Sprint Planning ไม่มี Sprint Goal ที่ชัดเจน",
            "Sprint Review กลายเป็นการตรวจรับงานแบบจับผิด",
            "จบ Retrospective แล้วไม่มี Action Item นำไปปรับปรุงจริง"
        ],
        "card4_warning": "ถ้าประชุมแล้วไม่ช่วยให้งานเดินหน้า แปลว่ากำลังทำผิดวิธี",
        "card5_title": "5) สรุป",
        "card5_icon": "check",
        "card5_text": "Agile Ceremonies คือ<strong>เครื่องมือสร้างความโปร่งใส</strong> ช่วยให้ทีมเห็นปัญหาตั้งแต่เนิ่นๆ และร่วมมือกันส่งมอบคุณภาพได้อย่างยั่งยืน",
        "memory_pills": ["5 Ceremonies", "Plan ชัด", "Daily กระชับ", "Demo จริง", "Retro พัฒนา"]
    },

    # 6. backlog.md
    {
        "file_rel": "backlog.md",
        "output_name": "Backlog_Management",
        "tag": "ZURI PRODUCT • BACKLOG MANAGEMENT",
        "title_plain": "จัด Backlog ยังไง ไม่ให้รกและหลุดเป้า ?",
        "title_html": "จัด Backlog ยังไง <span class=\"highlight\">ไม่ให้รกและหลุดเป้า ?</span>",
        "subtitle": "ไม่ใช่ถังขยะเก็บไอเดีย แต่คือรายการงานที่พร้อมสร้างคุณค่าให้ธุรกิจ",
        "sticky_text": "Backlog คุณภาพ จัดการง่าย ทีมหยิบทำได้ทันที! 💡",
        "equation": "DEEP Backlog = Detailed Appropriately + Estimated + Emergent + Prioritized",
        "card1_title": "1) Product Backlog คืออะไร?",
        "card1_subtitle": "ศูนย์กลางรายการงานทั้งหมดของ Product:",
        "card1_items": [
            "Single Source of Truth สำหรับทุกฟีเจอร์ บั๊ก และงานปรับปรุง",
            "มีการจัดเรียงลำดับตาม Business Value และความสำคัญ",
            "มีการอัปเดตและปรับเปลี่ยนอยู่เสมอตามสถานการณ์",
            "ช่วยให้ทีมและ Stakeholder เห็นภาพงานในอนาคตตรงกัน"
        ],
        "card2_title": "2) โครงสร้างงานที่ดีใน Backlog",
        "card2_items": [
            {"title": "Epic (เป้าหมายใหญ่)", "desc": "กลุ่มงานขนาดใหญ่ที่ต้องใช้เวลาหลาย Sprint", "icon": "target"},
            {"title": "Feature (ความสามารถ)", "desc": "ฟังก์ชันที่ตอบโจทย์การใช้งานของผู้ใช้", "icon": "screen"},
            {"title": "User Story (งานย่อย)", "desc": "ชิ้นงานขนาดเล็กที่มีคุณค่าและส่งมอบได้ใน Sprint", "icon": "doc"},
            {"title": "Bug / Tech Debt", "desc": "งานซ่อมแซมและปรับปรุงเชิงเทคนิค", "icon": "shield"}
        ],
        "card2_footer": "ด้านบนต้องละเอียดพร้อมทำ ด้านล่างเก็บไอเดียกว้างๆ",
        "card3_title": "3) วงจรการดูแล Backlog ให้มีชีวิต",
        "flow_steps": [
            {"title": "Capture Idea", "icon": "bulb"},
            {"title": "Filter & Prioritize", "icon": "layers"},
            {"title": "Refine & Detail", "icon": "doc"},
            {"title": "Ready for Sprint", "icon": "check"}
        ],
        "card3_subcaption": "หมั่นตัดงานที่ไม่สำคัญออกอย่างสม่ำเสมอ",
        "card4_title": "4) สัญญาณว่า Backlog กำลังพัง",
        "card4_items": [
            "มีการ์ดค้างดองอยู่เกิน 6 เดือนโดยไม่มีใครแตะ",
            "ทุกการ์ดถูกปักเป็น Priority 1 ทั้งหมด",
            "การ์ดไม่มีรายละเอียด ไม่มี Acceptance Criteria",
            "งานด้านบนยังไม่พร้อมให้ Dev หยิบไปทำใน Planning"
        ],
        "card4_warning": "Backlog ที่ดีต้องมีขนาดพอเหมาะและได้รับการ Refine เสมอ",
        "card5_title": "5) สรุป",
        "card5_icon": "layers",
        "card5_text": "Backlog ที่มีคุณภาพ<strong>ช่วยประหยัดเวลาทั้งทีม</strong> ทำให้ PO บริหารงานได้ง่าย และ Dev มีงานที่ชัดเจนพร้อมลุยตลอดเวลา",
        "memory_pills": ["Backlog คุณภาพ", "บนละเอียด", "ล่างกว้าง", "ตัดสิ่งไม่จำเป็น"]
    },

    # 7. Checklist-Dev.md
    {
        "file_rel": "Checklist-Dev.md",
        "output_name": "Checklist_Dev",
        "tag": "ZURI DELIVERY • DEFINITION OF READY",
        "title_plain": "Checklist ก่อนส่งงานให้ Dev (DoR)",
        "title_html": "Checklist <span class=\"highlight\">ก่อนส่งงานให้ Dev (DoR)</span>",
        "subtitle": "เช็กให้ชัวร์ก่อนเริ่มโค้ด ลดการถามกลับ ลดงานแก้ ลดบั๊ก",
        "sticky_text": "ส่งงานเป๊ะ Dev โค้ดไว บั๊กไม่โผล่! 💡",
        "equation": "Definition of Ready = Goal ชัด + Flow ครบ + Scope นิ่ง + AC พร้อม + UI เคลียร์",
        "card1_title": "1) ทำไมต้องมี DoR Checklist?",
        "card1_subtitle": "ป้องกันไม่ให้ทีมเริ่มงานจากความคลุมเครือ:",
        "card1_items": [
            "ลดการหยุดชะงักระหว่าง Sprint เพราะข้อมูลไม่พอ",
            "ช่วยให้ Dev สามารถประเมินเวลาและแรงงานได้แม่นยำ",
            "ลดการรื้อโค้ดใหม่เพราะเข้าใจ Requirement ไม่ตรงกัน",
            "สร้างมาตรฐานการส่งต่องานระหว่าง BA/PO กับ Dev"
        ],
        "card2_title": "2) 6 ข้อต้องเช็กให้ผ่านก่อน Hand-off",
        "card2_items": [
            {"title": "1. User & Role ชัดเจน", "desc": "ใครเป็นคนใช้ และมีสิทธิ์อะไรบ้าง", "icon": "users"},
            {"title": "2. Flow & Screen ครบ", "desc": "มีทั้ง Happy Path และ Error States", "icon": "screen"},
            {"title": "3. Business Rules เคลียร์", "desc": "ตรรกะการคำนวณและเงื่อนไขถูกต้อง", "icon": "target"},
            {"title": "4. Acceptance Criteria ครบ", "desc": "เขียน Given/When/Then ชัดเจน", "icon": "check"},
            {"title": "5. Data & API พร้อม", "desc": "ระบุ Data Schema และ Field ที่ต้องการ", "icon": "doc"},
            {"title": "6. Out of Scope ชัด", "desc": "ระบุสิ่งที่ไม่ทำในรอบนี้", "icon": "shield"}
        ],
        "card2_footer": "ผ่านครบทุกข้อจึงจะอนุญาตให้นำเข้า Sprint",
        "card3_title": "3) ลำดับขั้นตอนการ Hand-off",
        "flow_steps": [
            {"title": "Draft Story", "icon": "doc"},
            {"title": "Refinement Walk", "icon": "users"},
            {"title": "Checklist DoR", "icon": "check"},
            {"title": "Sprint Ready", "icon": "sparkles"}
        ],
        "card3_subcaption": "Dev และ QA ต้องมีส่วนร่วมในการตรวจสอบ DoR เสมอ",
        "card4_title": "4) จุดที่คนมักมองข้าม",
        "card4_items": [
            "ลืมระบุสถานะตอนโหลดช้า (Loading State)",
            "ลืมระบุข้อความแจ้งเตือนเมื่อระบบมีปัญหา (Error Message)",
            "ลืมเงื่อนไขข้อมูลว่างเปล่า (Empty State)",
            "ไม่ได้ระบุผลกระทบต่อระบบเดิม (Dependency Impact)"
        ],
        "card4_warning": "เตรียมงานเพิ่ม 20% ต้นน้ำ ประหยัดเวลาแก้บั๊กปลายน้ำได้ 80%",
        "card5_title": "5) สรุป",
        "card5_icon": "check",
        "card5_text": "DoR ไม่ใช่กำแพงกั้นทีม <strong>แต่คือสัญญาใจด้านคุณภาพ</strong> ที่ช่วยให้ทั้งทีมทำงานด้วยความมั่นใจและส่งมอบงานได้ทันเวลา",
        "memory_pills": ["DoR Checklist", "Role ชัด", "Flow ครบ", "AC พร้อม", "Dev ลุยได้"]
    },

    # 8. MoSCoW.md
    {
        "file_rel": "MoSCoW.md",
        "output_name": "MoSCoW_Method",
        "tag": "ZURI STRATEGY • PRIORITIZATION",
        "title_plain": "MoSCoW Method จัดลำดับงานแบบมือโปร",
        "title_html": "MoSCoW Method <span class=\"highlight\">จัดลำดับงานแบบมือโปร</span>",
        "subtitle": "ตัดส่วนเกิน เพิ่มส่วนสำคัญ ส่งมอบงานตรงเวลาและไม่เกินงบ",
        "sticky_text": "แยกงานขาด ปล่อยงานไว ไร้ปัญหา Deadlines พัง! 💡",
        "equation": "MoSCoW = Must Have (ต้องมี) + Should Have (ควรมี) + Could Have (มีก็ดี) + Won't Have (ตัดก่อน)",
        "card1_title": "1) ความหมายของ 4 ระดับ",
        "card1_subtitle": "เกณฑ์แบ่งหมวดหมู่ฟีเจอร์ตามความจำเป็นจริง:",
        "card1_items": [
            "Must Have: ขาดไม่ได้ ถ้าไม่มีระบบใช้งานไม่ได้หรือผิดกฎหมาย",
            "Should Have: สำคัญมาก แต่ถ้าไม่มีในรอบนี้ยังมีทางออกชั่วคราว",
            "Could Have: มีแล้วดี ผู้ใช้ชอบ แต่ไม่มีผลกระทบต่อการทำงานหลัก",
            "Won't Have: ตกลงกันว่าจะไม่ทำในรอบนี้ (เก็บไว้รอบหน้า)"
        ],
        "card2_title": "2) สัดส่วนทองคำในการจัดสรร",
        "card2_items": [
            {"title": "Must Have (ไม่เกิน 60%)", "desc": "เพื่อไม่ให้ทีมแบกรับความเสี่ยงสูงเกินไป", "icon": "target"},
            {"title": "Should Have (~20%)", "desc": "ช่วยเพิ่มคุณค่าและความสมบูรณ์ของระบบ", "icon": "doc"},
            {"title": "Could Have (~20%)", "desc": "เป็น Buffer ที่พร้อมตัดออกถ้าเวลาไม่พอ", "icon": "sparkles"},
            {"title": "Won't Have (ชัดเจน)", "desc": "ช่วยดับความคาดหวังที่ไม่ตรงกัน", "icon": "shield"}
        ],
        "card2_footer": "สัดส่วนนี้ช่วยการันตีว่า Deadlines จะไม่เลื่อนแน่นอน",
        "card3_title": "3) ขั้นตอนการนำ MoSCoW ไปใช้",
        "flow_steps": [
            {"title": "รวบรวม Scope", "icon": "doc"},
            {"title": "ประเมินความจำเป็น", "icon": "layers"},
            {"title": "ต่อรอง Stakeholder", "icon": "users"},
            {"title": "ล็อก Commitment", "icon": "check"}
        ],
        "card3_subcaption": "ต้องได้รับความเห็นชอบจาก Decision Maker ทุกฝ่าย",
        "card4_title": "4) กับดักที่พบบ่อย",
        "card4_items": [
            "ทุกคนบอกว่าฟีเจอร์ของตัวเองเป็น Must Have ทั้งหมด",
            "ไม่กล้าปฏิเสธ ทำให้ไม่มีรายการ Won't Have เลย",
            "จัดเป็น Could Have แต่สุดท้ายบังคับให้ทำทุกอย่าง",
            "ไม่ยอมตัด Scope เมื่อเกิดปัญหาความล่าช้า"
        ],
        "card4_warning": "ถ้าทุกอย่างเป็น Must Have แปลว่าไม่มีการจัดลำดับความสำคัญเลย",
        "card5_title": "5) สรุป",
        "card5_icon": "target",
        "card5_text": "MoSCoW ช่วยสร้าง<strong>ความจริงใจในการบริหารขอบเขตงาน</strong> ทำให้ส่งมอบ Core Value ได้ตรงเวลา และบริหารความคาดหวังได้อย่างยอดเยี่ยม",
        "memory_pills": ["MoSCoW", "Must (ต้องมี)", "Should (ควรมี)", "Could (ถ้าทัน)", "Won't (ตัดก่อน)"]
    },

    # 9. Prioritization.md
    {
        "file_rel": "Prioritization.md",
        "output_name": "Prioritization_Techniques",
        "tag": "ZURI STRATEGY • PRIORITY MATRIX",
        "title_plain": "Prioritization ทำไมต้องเลือก และเลือกอย่างไร ?",
        "title_html": "Prioritization <span class=\"highlight\">ทำไมต้องเลือก และเลือกอย่างไร ?</span>",
        "subtitle": "ทรัพยากรและเวลามีจำกัด ต้องโฟกัสงานที่สร้างผลลัพธ์สูงสุด",
        "sticky_text": "เลือกงานถูกจุด ธุรกิจโตไว ทีมไม่เหนื่อยฟรี! 💡",
        "equation": "Priority Score = (Business Value + User Impact) ÷ (Effort + Risk)",
        "card1_title": "1) ทำไมต้องจัดลำดับความสำคัญ?",
        "card1_subtitle": "เพราะเราทำทุกอย่างพร้อมกันไม่ได้:",
        "card1_items": [
            "ปกป้องโฟกัสและพลังงานของทีม ไม่ให้ทำงานสะเปะสะปะ",
            "การันตีว่าฟีเจอร์ที่มีผลต่อรายได้และผู้ใช้จะถูกส่งมอบก่อน",
            "ช่วยให้ Stakeholder เข้าใจว่าทำไมบางงานจึงต้องรอ",
            "ลดความเสี่ยงจากการลงทุนในฟีเจอร์ที่ไม่มีคนใช้งาน"
        ],
        "card2_title": "2) 5 มิติในการประเมินงาน",
        "card2_items": [
            {"title": "1. Business Value", "desc": "สร้างรายได้หรือลดต้นทุนให้ธุรกิจได้มากแค่ไหน", "icon": "sparkles"},
            {"title": "2. User Impact", "desc": "แก้ Pain Point ของผู้ใช้ได้ตรงจุดหรือไม่", "icon": "users"},
            {"title": "3. Urgency", "desc": "มีความเร่งด่วนทางกฎหมายหรือตลาดไหม", "icon": "clock"},
            {"title": "4. Effort / Cost", "desc": "ต้องใช้คน เวลา และงบประมาณเท่าใด", "icon": "layers"},
            {"title": "5. Risk & Dependency", "desc": "มีความเสี่ยงหรือต้องพึ่งพาระบบอื่นไหม", "icon": "shield"}
        ],
        "card2_footer": "ประเมินรอบด้าน อย่ามองแค่มิติเดียว",
        "card3_title": "3) เฟรมเวิร์กยอดนิยมที่เลือกใช้ได้",
        "flow_steps": [
            {"title": "Value vs Effort", "icon": "target"},
            {"title": "MoSCoW", "icon": "layers"},
            {"title": "RICE Scoring", "icon": "sparkles"},
            {"title": "Kano Model", "icon": "users"}
        ],
        "card3_subcaption": "เลือกเฟรมเวิร์กที่เหมาะกับขนาดทีมและความซับซ้อนของงาน",
        "card4_title": "4) หลุมพรางที่ต้องระวัง",
        "card4_items": [
            "ทำตามคนเสียงดังหรือคนตำแหน่งสูงสุด (HiPPO)",
            "เลือกทำแต่งานง่ายๆ แต่งานสร้าง Value สูงถูกผลัดผ่อน",
            "เปลี่ยน Priority รายวันจนทีมตั้งหลักไม่ทัน",
            "ตัดสินใจตามความรู้สึกส่วนตัวโดยไม่มีข้อมูลรองรับ"
        ],
        "card4_warning": "การ Prioritize ที่ดีต้องอิงจาก Data และเป้าหมายทางธุรกิจจริง",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "การจัดลำดับความสำคัญคือ<strong>ศิลปะแห่งการกล้าปฏิเสธ</strong> เพื่อมุ่งมั่นทุ่มเททรัพยากรให้กับสิ่งที่สร้างคุณค่าสูงสุดแก่ผู้ใช้และองค์กร",
        "memory_pills": ["Prioritization", "เช็ก Value", "เทียบ Effort", "ดู Impact", "เลือกสิ่งที่ใช่"]
    },

    # 10. refinement.md
    {
        "file_rel": "refinement.md",
        "output_name": "Backlog_Refinement",
        "tag": "ZURI SCRUM • GROOMING & SLICING",
        "title_plain": "Backlog Refinement เตรียมงานยังไงให้ลื่นไหล ?",
        "title_html": "Backlog Refinement <span class=\"highlight\">เตรียมงานยังไงให้ลื่นไหล ?</span>",
        "subtitle": "การเตรียมความพร้อมล่วงหน้า คือหัวใจของความเร็วในการพัฒนา",
        "sticky_text": "Refine ดี Sprint วิ่งฉิว ไม่มีสะดุดกลางคัน! 💡",
        "equation": "Good Refinement = แตก Story ย่อย + AC เคลียร์ + ปลด Dependency + กะ Effort ตรง",
        "card1_title": "1) Refinement คืออะไร?",
        "card1_subtitle": "กิจกรรมที่ PO, BA, Dev และ QA ร่วมกันขัดเกลางาน:",
        "card1_items": [
            "ทำความเข้าใจเป้าหมายของแต่ละ User Story ร่วมกัน",
            "ตรวจเช็กและเติม Acceptance Criteria ให้สมบูรณ์",
            "แตกงานขนาดใหญ่ (Epic) ให้กลายเป็น Story ย่อยที่ทำจบใน Sprint",
            "ค้นหาและปลดล็อก Technical Dependency ล่วงหน้า"
        ],
        "card2_title": "2) สิ่งที่ต้องทำใน Session",
        "card2_items": [
            {"title": "1. อธิบายโจทย์และที่มา", "desc": "PO/BA เล่า Pain Point ของผู้ใช้", "icon": "target"},
            {"title": "2. แตกชิ้นงาน (Slicing)", "desc": "ซอยงานให้เล็กลงแต่ยังสร้าง Value ได้", "icon": "layers"},
            {"title": "3. ทบทวน Acceptance Criteria", "desc": "Dev/QA ร่วมกันตั้งคำถามและดักเคส", "icon": "check"},
            {"title": "4. ประเมินความซับซ้อน", "desc": "ร่วมกันให้ Story Points หรือ Effort", "icon": "clock"}
        ],
        "card2_footer": "แนะนำให้จัดสัปดาห์ละ 1-2 ครั้ง ครั้งละไม่เกิน 1 ชม.",
        "card3_title": "3) เส้นทางจาก Idea สู่ Sprint Ready",
        "flow_steps": [
            {"title": "Draft Idea", "icon": "bulb"},
            {"title": "Team Review", "icon": "users"},
            {"title": "Slice & Add AC", "icon": "doc"},
            {"title": "Mark DoR Ready", "icon": "check"}
        ],
        "card3_subcaption": "เตรียมงานล่วงหน้าอย่างน้อย 1-2 Sprint เสมอ",
        "card4_title": "4) ข้อผิดพลาดที่พบบ่อย",
        "card4_items": [
            "มารอคุยรายละเอียดและแตกงานใน Sprint Planning",
            "PO มาเล่าแต่ไม่มีภาพ Wireframe หรือ Flow ประกอบ",
            "Dev นั่งฟังเฉยๆ โดยไม่ตั้งคำถามหรือทักท้วงความเสี่ยง",
            "รับงานชิ้นใหญ่ที่ยังไม่พร้อมเข้าสู่ Sprint"
        ],
        "card4_warning": "ถ้าไม่ Refine ล่วงหน้า Sprint Planning จะกลายเป็นการประชุมที่ยาวนานและเหนื่อยล้า",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "Refinement คือการ<strong>ลงทุนเวลาล่วงหน้าเพื่อซื้อความเร็ว</strong> ช่วยให้ทีมเห็นภาพเดียวกัน และเริ่มงานใน Sprint ได้ทันทีโดยไม่ต้องสะดุด",
        "memory_pills": ["Refinement", "เล่าโจทย์", "แตกงานย่อย", "ล็อก AC", "พร้อมลุย Sprint"]
    },

    # 11. respon.md
    {
        "file_rel": "respon.md",
        "output_name": "Roles_Responsibilities",
        "tag": "ZURI ROLES • RACI MATRIX",
        "title_plain": "บทบาทหน้าที่ PM, PO, BA, Dev, QA ใครทำอะไร ?",
        "title_html": "บทบาทหน้าที่ <span class=\"highlight\">PM, PO, BA, Dev, QA ใครทำอะไร ?</span>",
        "subtitle": "แบ่งหน้าที่ให้ชัดเจน ทำงานประสานกันเป็นทีมอย่างมืออาชีพ",
        "sticky_text": "หน้าที่ชัด สื่อสารง่าย ไม่ก้าวก่าย ไม่ทิ้งงาน! 💡",
        "equation": "Team Success = PM (แผน/เสี่ยง) + PO (คุณค่า) + BA (วิเคราะห์/Flow) + Dev (สร้าง) + QA (คุณภาพ)",
        "card1_title": "1) ฝ่ายบริหารและวิสัยทัศน์",
        "card1_subtitle": "กำหนดทิศทาง ควบคุมแผนงาน และความคุ้มค่า:",
        "card1_items": [
            "PM (Project Manager): บริหารไทม์ไลน์ งบประมาณ แผนงาน และความเสี่ยงภาพรวม",
            "PO (Product Owner): กำหนดวิสัยทัศน์ จัดลำดับ Backlog และเพิ่ม Value สูงสุดให้ Product",
            "ทำงานร่วมกันเพื่อบาลานซ์ระหว่างเวลา คุณค่า และทรัพยากร"
        ],
        "card2_title": "2) ฝ่ายวิเคราะห์และพัฒนาคุณภาพ",
        "card2_items": [
            {"title": "BA (Business Analyst)", "desc": "วิเคราะห์ Requirement ออกแบบ Flow เขียน AC และประสานงาน", "icon": "doc"},
            {"title": "Dev (Developer)", "desc": "ออกแบบสถาปัตยกรรม เขียนโค้ด พัฒนาระบบ และ Unit Test", "icon": "screen"},
            {"title": "QA (Quality Assurance)", "desc": "วางแผน Test Scenario ตรวจจับบั๊ก และการันตีคุณภาพ", "icon": "shield"}
        ],
        "card2_footer": "ทุกตำแหน่งคือเพื่อนร่วมทีมที่ส่งเสริมซึ่งกันและกัน",
        "card3_title": "3) สายธารการส่งต่องานในโปรเจกต์",
        "flow_steps": [
            {"title": "Business Need", "icon": "target"},
            {"title": "PO & BA Scope", "icon": "doc"},
            {"title": "Dev Build", "icon": "screen"},
            {"title": "QA Test", "icon": "shield"},
            {"title": "Release Value", "icon": "sparkles"}
        ],
        "card3_subcaption": "ส่งต่องานอย่างต่อเนื่องพร้อมข้อมูลที่ชัดเจน",
        "card4_title": "4) ข้อควรระวังเรื่องบทบาท",
        "card4_items": [
            "ให้ BA ตัดสินใจทิศทางธุรกิจแทน PO โดยพลการ",
            "โยนหน้าที่การบริหารเวลาทั้งหมดให้ Dev",
            "มองว่า QA เป็นคนเดียวที่ต้องรับผิดชอบเรื่องคุณภาพ",
            "ต่างคนต่างทำงานในไซโลของตนเองโดยไม่สื่อสารกัน"
        ],
        "card4_warning": "คุณภาพและความสำเร็จของ Product คือความรับผิดชอบร่วมกันของทุกคนในทีม",
        "card5_title": "5) สรุป",
        "card5_icon": "users",
        "card5_text": "การแบ่งบทบาทที่ชัดเจน<strong>ไม่ได้สร้างกำแพงกั้น</strong> แต่ช่วยให้ทุกคนรู้จุดโฟกัสของตนเอง และส่งมอบงานได้อย่างมีประสิทธิภาพสูงสุด",
        "memory_pills": ["ทีมเวิร์กเป๊ะ", "PO คุมทิศ", "PM คุมแผน", "BA เคลียร์โจทย์", "Dev สร้าง", "QA เช็ก"]
    },

    # 12. RICE.md
    {
        "file_rel": "RICE.md",
        "output_name": "RICE_Scoring",
        "tag": "ZURI PRODUCT • SCORING MODEL",
        "title_plain": "RICE Scoring คิดคะแนน Priority แบบมีเหตุผล",
        "title_html": "RICE Scoring <span class=\"highlight\">คิดคะแนน Priority แบบมีเหตุผล</span>",
        "subtitle": "เปลี่ยนการเถียงด้วยความรู้สึก เป็นการตัดสินใจด้วยตัวเลขที่พิสูจน์ได้",
        "sticky_text": "คำนวณเป๊ะ ตัดสินใจโปร เลิกเถียงตามอารมณ์! 💡",
        "equation": "RICE Score = (Reach × Impact × Confidence) ÷ Effort",
        "card1_title": "1) 4 ตัวแปรของ RICE Model",
        "card1_subtitle": "สูตรคำนวณมาตรฐานระดับสากล:",
        "card1_items": [
            "Reach (การเข้าถึง): ฟีเจอร์นี้จะเข้าถึงผู้ใช้กี่คนใน 1 ไตรมาส",
            "Impact (ผลกระทบ): สร้างการเปลี่ยนแปลงต่อผู้ใช้มากแค่ไหน (0.25 - 3)",
            "Confidence (ความมั่นใจ): เรามั่นใจในข้อมูลนี้แค่ไหน (50% - 100%)",
            "Effort (แรงงาน): ทีมต้องใช้เวลากี่คน-เดือน (Person-Months) ในการทำ"
        ],
        "card2_title": "2) เกณฑ์คะแนน Impact & Confidence",
        "card2_items": [
            {"title": "Impact 3 = Massive", "desc": "เปลี่ยนชีวิตผู้ใช้หรือธุรกิจอย่างมหาศาล", "icon": "sparkles"},
            {"title": "Impact 2 = High", "desc": "ส่งผลกระทบอย่างมีนัยสำคัญ", "icon": "target"},
            {"title": "Impact 1 = Medium / 0.5 = Low", "desc": "ผลกระทบปานกลางหรือเล็กน้อย", "icon": "doc"},
            {"title": "Confidence 100% = High", "desc": "มี Data รองรับชัดเจน (80%=Medium, 50%=Low)", "icon": "shield"}
        ],
        "card2_footer": "ยิ่ง Reach, Impact, Confidence สูง และ Effort ต่ำ คะแนนจะยิ่งสูง",
        "card3_title": "3) ขั้นตอนการคำนวณคะแนน",
        "flow_steps": [
            {"title": "ลิสต์ฟีเจอร์", "icon": "doc"},
            {"title": "ใส่คะแนน 4 ค่า", "icon": "layers"},
            {"title": "คำนวณ RICE", "icon": "sparkles"},
            {"title": "เรียงลำดับทำก่อน", "icon": "target"}
        ],
        "card3_subcaption": "ช่วยอธิบายกับผู้บริหารได้อย่างสมเหตุสมผล",
        "card4_title": "4) ข้อควรระวังในการใช้ RICE",
        "card4_items": [
            "ใส่ Confidence 100% ทั้งที่คิดเอาเองโดยไม่มีข้อมูล",
            "ประเมิน Effort ต่ำเกินจริงโดยไม่ได้ปรึกษาทีม Dev",
            "นำคะแนนดิบมาตัดสินโดยไม่ดู Strategic Alignment อื่นๆ",
            "ใช้ RICE กับงานเล็กๆ รายวันจนเสียเวลาเกินจำเป็น"
        ],
        "card4_warning": "RICE คือเครื่องมือช่วยตัดสินใจ ไม่ใช่สิ่งที่มาแทนที่การคิดวิเคราะห์",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "RICE ช่วยเปลี่ยนการถกเถียงในที่ประชุม<strong>ให้เป็นการวิเคราะห์บนพื้นฐานของข้อมูล</strong> ทำให้ทีมสามารถโฟกัสงานที่คุ้มค่าที่สุดได้อย่างมั่นใจ",
        "memory_pills": ["RICE Model", "Reach (คน)", "Impact (ผล)", "Confidence (มั่นใจ)", "÷ Effort (แรง)"]
    },

    # 13. roadmap.md
    {
        "file_rel": "roadmap.md",
        "output_name": "Product_Roadmap",
        "tag": "ZURI ROADMAP • PRODUCT STRATEGY",
        "title_plain": "Roadmap ต่างจาก Timeline อย่างไร ?",
        "title_html": "Roadmap <span class=\"highlight\">ต่างจาก Timeline อย่างไร ?</span>",
        "subtitle": "Roadmap คือทิศทางและผลลัพธ์ Timeline คือตารางเวลาปฏิบัติการ",
        "sticky_text": "มองเห็นทิศทาง ปรับตัวยืดหยุ่น ถึงเป้าหมายแน่นอน! 💡",
        "equation": "Product Roadmap = วิสัยทัศน์ + ปัญหาที่แก้ + ผลลัพธ์ทางธุรกิจ (Outcome-based)",
        "card1_title": "1) ข้อแตกต่างที่สำคัญ",
        "card1_subtitle": "อย่าสับสนระหว่างวิสัยทัศน์กับตารางนัดหมาย:",
        "card1_items": [
            "Roadmap: เน้น Outcome และ Strategic Theme มุ่งบอกว่า 'จะแก้ปัญหาอะไรและทำไม' มีความยืดหยุ่นสูง",
            "Timeline: เน้น Output และ Deadline มุ่งบอกว่า 'จะส่งมอบฟีเจอร์อะไร เมื่อไหร่' มีวันที่ล็อกแน่นอน",
            "ทีมต้องการ Roadmap นำทาง และใช้ Timeline บริหารการส่งมอบ"
        ],
        "card2_title": "2) โครงสร้าง Now / Next / Later",
        "card2_items": [
            {"title": "Now (กำลังทำตอนนี้)", "desc": "ชัดเจนสูงมาก กำลังอยู่ในกระบวนการพัฒนา", "icon": "screen"},
            {"title": "Next (จะทำต่อไป)", "desc": "ชัดเจนปานกลาง กำลังเตรียมความพร้อมและค้นคว้า", "icon": "doc"},
            {"title": "Later (อนาคต)", "desc": "วิสัยทัศน์ระยะยาว ปรับเปลี่ยนได้ตาม Feedback", "icon": "sparkles"},
            {"title": "Strategic Goals", "desc": "ตัวชี้วัดความสำเร็จของแต่ละช่วงเวลา", "icon": "target"}
        ],
        "card2_footer": "ช่วยลดการผูกมัดวันส่งมอบระยะยาวเกินความเป็นจริง",
        "card3_title": "3) ขั้นตอนการสร้าง Roadmap ที่ดี",
        "flow_steps": [
            {"title": "Product Goal", "icon": "target"},
            {"title": "User Needs", "icon": "users"},
            {"title": "Group Themes", "icon": "layers"},
            {"title": "Now/Next/Later", "icon": "sparkles"}
        ],
        "card3_subcaption": "สื่อสารอย่างโปร่งใสกับทั้งทีมและผู้บริหาร",
        "card4_title": "4) หลุมพรางที่พบบ่อย",
        "card4_items": [
            "เอา Gantt Chart รายวันมาเรียกว่าเป็น Roadmap",
            "สัญญาวันปล่อยฟีเจอร์ล่วงหน้า 1 ปี ทั้งที่ยังไม่รู้รายละเอียด",
            "ใส่รายชื่อฟีเจอร์อัดแน่นโดยไม่ระบุผลลัพธ์ทางธุรกิจ",
            "ไม่เคยทบทวนหรืออัปเดต Roadmap เลยตลอดทั้งปี"
        ],
        "card4_warning": "Roadmap ที่ล็อกตายตัวคือศัตรูตัวร้ายของความคล่องตัวในยุคดิจิทัล",
        "card5_title": "5) สรุป",
        "card5_icon": "target",
        "card5_text": "Roadmap ที่ยอดเยี่ยม<strong>ต้องบอกทิศทางและแรงบันดาลใจ</strong> ช่วยให้ทุกคนในองค์กรมองเห็นภาพชัยชนะร่วมกัน และพร้อมปรับเปลี่ยนเพื่อสิ่งที่ดีกว่า",
        "memory_pills": ["Roadmap vs Timeline", "Roadmap (นำทิศทาง)", "Timeline (ลงตาราง)", "มุ่งเน้น Outcome"]
    },

    # 14. Scope-Creep.md
    {
        "file_rel": "Scope-Creep.md",
        "output_name": "Scope_Creep",
        "tag": "ZURI GOVERNANCE • SCOPE CONTROL",
        "title_plain": "Scope Creep ปัญหางานบวม แก้อย่างไร ?",
        "title_html": "Scope Creep <span class=\"danger-highlight\">ปัญหางานบวม แก้อย่างไร ?</span>",
        "subtitle": "ควบคุมขอบเขตงานให้อยู่ในร่องในรอย ส่งงานตรงเวลาโดยทีมไม่ Burnout",
        "sticky_text": "คุม Scope นิ่ง ส่งงานตรงเวลา ทีมไม่ Burnout! 💡",
        "equation": "Scope Creep = Requirement คลุมเครือ + ขาด Change Control + รับปากง่ายเกินไป",
        "card1_title": "1) Scope Creep คืออะไร?",
        "card1_subtitle": "การที่งานงอกเพิ่มขึ้นเรื่อยๆ โดยไม่ได้เพิ่มเวลาหรืองบ:",
        "card1_items": [
            "เกิดขึ้นอย่างเงียบๆ จากคำขอเล็กๆ น้อยๆ ระหว่างทาง",
            "ส่งผลให้ทีมต้องทำงานล่วงเวลา คุณภาพระบบลดลง",
            "โปรเจกต์ล่าช้า งบบานปลาย และเสี่ยงส่งงานไม่ทัน",
            "เป็นสาเหตุอันดับต้นๆ ที่ทำให้ทีมพัฒนาหมดไฟ"
        ],
        "card2_title": "2) สาเหตุหลักที่ทำให้งานบวม",
        "card2_items": [
            {"title": "1. Out of Scope ไม่ชัด", "desc": "ไม่ได้เขียนสิ่งที่ 'ไม่ทำ' ไว้อย่างชัดเจน", "icon": "shield"},
            {"title": "2. User นึกเพิ่มตอนเห็นของ", "desc": "ไม่ได้จัด Workshop ทำความเข้าใจแต่แรก", "icon": "screen"},
            {"title": "3. รับปากปากเปล่า", "desc": "ทีมเกรงใจยอมรับงานเพิ่มโดยไม่ผ่านระบบ", "icon": "alert"},
            {"title": "4. ขาด Change Request (CR)", "desc": "ไม่มีขั้นตอนประเมินผลกระทบก่อนเริ่มทำ", "icon": "doc"}
        ],
        "card2_footer": "การเกรงใจโดยไม่ประเมินผลกระทบคือต้นเหตุของความเสียหาย",
        "card3_title": "3) วิธีรับมือและป้องกันอย่างมือโปร",
        "flow_steps": [
            {"title": "รับฟังความต้องการ", "icon": "users"},
            {"title": "ประเมิน Impact", "icon": "clock"},
            {"title": "เสนอ Trade-off", "icon": "layers"},
            {"title": "ทำ Change Request", "icon": "check"}
        ],
        "card3_subcaption": "ถ้าจะเพิ่มงานใหม่ ต้องยอมเลื่อนงานเดิมออกหรือเพิ่มงบ/เวลา",
        "card4_title": "4) คำพูดอันตรายที่ต้องระวัง",
        "card4_items": [
            "⚠️ 'นิดเดียวเอง เพิ่มปุ่มนี้ให้หน่อยนะ'",
            "⚠️ 'ไหนๆ ก็เขียนหน้านี้แล้ว ขอเพิ่มอีก 3 ฟิลด์นะ'",
            "⚠️ 'อันนี้ง่ายๆ น่าจะใช้เวลาแค่ 5 นาที'",
            "⚠️ 'คิดว่าระบบควรจะมีอันนี้อยู่แล้วนะ'"
        ],
        "card4_warning": "ทุกฟังก์ชันที่เพิ่มเข้ามา ล้วนมีต้นทุนการดูแลรักษาในอนาคตเสมอ",
        "card5_title": "5) สรุป",
        "card5_icon": "shield",
        "card5_text": "การควบคุม Scope <strong>ไม่ใช่การใจร้ายปฏิเสธลูกค้า</strong> แต่คือการปกป้องคุณภาพงานและรักษาสัจจะว่าจะส่งมอบสิ่งที่ดีที่สุดให้ตรงตามกำหนด",
        "memory_pills": ["คุม Scope นิ่ง", "นิยามชัด", "ประเมิน Impact", "ใช้ Change Request", "ส่งงานตรงเวลา"]
    },

    # 15. sprint.md
    {
        "file_rel": "sprint.md",
        "output_name": "Sprint_Execution",
        "tag": "ZURI SCRUM • SPRINT CYCLE",
        "title_plain": "Sprint ใน Agile ทำงานอย่างไรให้เวิร์ก ?",
        "title_html": "Sprint ใน Agile <span class=\"highlight\">ทำงานอย่างไรให้เวิร์ก ?</span>",
        "subtitle": "รอบการทำงานสั้นๆ ที่ส่งมอบซอฟต์แวร์ที่ใช้งานได้จริงอย่างสม่ำเสมอ",
        "sticky_text": "โฟกัสชัด ส่งมอบจริง สปริ้นต์จบ งานจบ มีความสุข! 💡",
        "equation": "Sprint Success = Sprint Goal นิ่ง + ความมุ่งมั่นของทีม + DoD ผ่าน 100%",
        "card1_title": "1) Sprint คืออะไร?",
        "card1_subtitle": "กรอบเวลาคงที่ (Time-box) ขนาด 1-2 สัปดาห์:",
        "card1_items": [
            "ทีมมีสมาธิโฟกัสกับเป้าหมายเดียวที่ตกลงร่วมกัน",
            "ผลลัพธ์ตอนจบ Sprint ต้องเป็นชิ้นงานที่พร้อมใช้งานได้จริง",
            "ช่วยให้ได้รับ Feedback จากผู้ใช้อย่างรวดเร็วและต่อเนื่อง",
            "รักษาระดับความเร็วในการทำงานที่ยั่งยืน (Sustainable Pace)"
        ],
        "card2_title": "2) องค์ประกอบสำคัญของ Sprint",
        "card2_items": [
            {"title": "Sprint Goal (เป้าหมายหลัก)", "desc": "เหตุผลสำคัญว่าทำไมเราถึงต้องทำ Sprint นี้", "icon": "target"},
            {"title": "Sprint Backlog (ชุดงาน)", "desc": "รายการ Story และ Task ที่ทีม Commit ว่าจะส่งมอบ", "icon": "layers"},
            {"title": "Team Capacity (กำลังคน)", "desc": "เวลาและความพร้อมจริงของทีมในรอบนี้", "icon": "users"},
            {"title": "Definition of Done (DoD)", "desc": "เกณฑ์ความสมบูรณ์ที่ผ่านการเทสครบถ้วน", "icon": "check"}
        ],
        "card2_footer": "Sprint Goal ไม่ควรถูกเปลี่ยนแปลงระหว่างทาง",
        "card3_title": "3) ลำดับการทำงานตลอดทั้ง Sprint",
        "flow_steps": [
            {"title": "Day 1: Planning", "icon": "target"},
            {"title": "Day 2-9: Build & Daily", "icon": "screen"},
            {"title": "Day 10: Review Demo", "icon": "sparkles"},
            {"title": "Day 10: Retro", "icon": "shield"}
        ],
        "card3_subcaption": "ทำงานร่วมกันอย่างใกล้ชิดระหว่าง Dev, QA และ PO",
        "card4_title": "4) ข้อห้ามระหว่าง Sprint",
        "card4_items": [
            "เปลี่ยน Sprint Goal หรือเพิ่มงานแทรกโดยไม่ตัดงานเก่าออก",
            "ปล่อยให้มีคนแอบสั่งงาน Dev นอกรอบโดยไม่ผ่าน PO",
            "ตัดขั้นตอนการทำ Automated Test หรือ QA เพื่อเร่งงาน",
            "ไม่ยอมยกมือบอกปัญหาใน Daily Scrum จนวันสุดท้าย"
        ],
        "card4_warning": "Sprint ไม่ใช่การวิ่งแข่งระยะสั้น แต่คือการสร้างจังหวะก้าวที่มั่นคง",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "Sprint ที่มีประสิทธิภาพ<strong>ช่วยลดความเครียดของทีม</strong> สร้างความไว้วางใจ และส่งมอบคุณค่าที่จับต้องได้ให้กับลูกค้าในทุกๆ สัปดาห์",
        "memory_pills": ["Sprint สำเร็จ", "ล็อก Sprint Goal", "สร้างชิ้นงานจริง", "ตรวจรับ Feedback", "พัฒนาต่อเนื่อง"]
    },

    # 16. test case.md
    {
        "file_rel": "test case.md",
        "output_name": "Test_Case_vs_AC",
        "tag": "ZURI QA • TESTING & QUALITY",
        "title_plain": "Test Case กับ Acceptance Criteria ต่างกันยังไง ?",
        "title_html": "Test Case กับ AC <span class=\"highlight\">ต่างกันยังไง ?</span>",
        "subtitle": "AC บอกเกณฑ์ความสำเร็จในภาพรวม Test Case บอกขั้นตอนตรวจรับอย่างละเอียด",
        "sticky_text": "เทสครอบคลุม ดักบั๊กอยู่หมัด ส่งมอบงานอย่างมั่นใจ! 💡",
        "equation": "Acceptance Criteria (สิ่งที่ต้องผ่าน) ➔ แตกออกเป็น ➔ Multiple Test Cases",
        "card1_title": "1) ความแตกต่างที่สำคัญ",
        "card1_subtitle": "บทบาทและผู้รับผิดชอบที่ส่งเสริมกัน:",
        "card1_items": [
            "Acceptance Criteria (AC): เขียนโดย PO/BA อธิบาย 'เงื่อนไข' ที่ทำให้ Story สำเร็จ เป็นภาษาระดับธุรกิจ",
            "Test Case: เขียนโดย QA อธิบาย 'ขั้นตอนทีละสเต็ป' ข้อมูลที่ต้องกรอก และผลลัพธ์ที่คาดหวังเชิงเทคนิค",
            "1 User Story หรือ 1 AC สามารถแตกออกมาเป็นได้หลาย Test Case"
        ],
        "card2_title": "2) ส่วนประกอบของ Test Case ที่ดี",
        "card2_items": [
            {"title": "Test ID & Description", "desc": "รหัสและชื่อเคสที่สื่อความหมายชัดเจน", "icon": "doc"},
            {"title": "Pre-condition", "desc": "สถานะตั้งต้นที่ต้องเตรียมก่อนเริ่มทดสอบ", "icon": "layers"},
            {"title": "Test Steps & Test Data", "desc": "ลำดับขั้นตอนการคลิกและชุดข้อมูลที่ใช้", "icon": "screen"},
            {"title": "Expected Result", "desc": "ผลลัพธ์ที่ถูกต้องซึ่งระบบต้องแสดงผล", "icon": "check"}
        ],
        "card2_footer": "ใครมาอ่านก็ต้องสามารถทดสอบตามและได้ผลลัพธ์เดียวกัน",
        "card3_title": "3) ประเภทของ Test Case ที่ต้องมี",
        "flow_steps": [
            {"title": "Positive Path", "icon": "check"},
            {"title": "Negative Path", "icon": "alert"},
            {"title": "Boundary / Edge", "icon": "shield"},
            {"title": "Security / Role", "icon": "users"}
        ],
        "card3_subcaption": "อย่าเทสเฉพาะกรณีปกติ ต้องดักจับกรณีผิดพลาดให้ครบ",
        "card4_title": "4) ข้อผิดพลาดที่พบบ่อย",
        "card4_items": [
            "เขียน Test Step คลุมเครือ เช่น 'ทดสอบว่าล็อกอินได้'",
            "ไม่มีการเตรียม Test Data ล่วงหน้า ทำให้เสียเวลาหาข้อมูล",
            "ทดสอบเฉพาะ Happy Path แล้วละเลย Error Handling",
            "ไม่อัปเดต Test Case เมื่อ Requirement มีการเปลี่ยนแปลง"
        ],
        "card4_warning": "Test Case ที่คลุมเครือจะทำให้ปล่อยบั๊กหลุดรอดไปถึงผู้ใช้จริง",
        "card5_title": "5) สรุป",
        "card5_icon": "shield",
        "card5_text": "AC ชี้เป้าว่าต้องถึงไหน ส่วน Test Case คือ<strong>แว่นขยายที่คอยตรวจสอบทุกย่างก้าว</strong> เพื่อการันตีว่าซอฟต์แวร์มีคุณภาพสูงสุดก่อนส่งมอบ",
        "memory_pills": ["AC vs Test Case", "AC (เกณฑ์ภาพรวม)", "Test Case (ขั้นตอนเทส)", "ดักครบทุกเคส"]
    },

    # 17. UAT.md
    {
        "file_rel": "UAT.md",
        "output_name": "UAT_Preparation",
        "tag": "ZURI QA & GO-LIVE • USER TESTING",
        "title_plain": "UAT คืออะไร ? เตรียมตัวอย่างไรก่อน Go-Live ?",
        "title_html": "UAT คืออะไร ? <span class=\"highlight\">เตรียมตัวอย่างไรก่อน Go-Live ?</span>",
        "subtitle": "ด่านทดสอบสุดท้ายโดยผู้ใช้งานจริง เพื่อยืนยันว่าระบบตอบโจทย์ธุรกิจ",
        "sticky_text": "UAT ผ่านฉลุย ผู้ใช้มั่นใจ Go-live ไร้กังวล! 💡",
        "equation": "UAT Sign-off = Flow ธุรกิจถูกต้อง + บั๊ก Critical เป็นศูนย์ + User มั่นใจในระบบ",
        "card1_title": "1) UAT คืออะไร?",
        "card1_subtitle": "User Acceptance Testing การตรวจรับมอบระบบ:",
        "card1_items": [
            "ทดสอบโดยตัวแทนผู้ใช้งานจริง (End Users หรือ Business Owners)",
            "ทดสอบบนกระบวนการทำงานจริง (End-to-End Business Flow)",
            "ยืนยันว่าระบบสามารถทำงานได้ตามวัตถุประสงค์ของธุรกิจ",
            "เป็นด่านสุดท้ายในการอนุมัติก่อนเปิดใช้งานจริง (Go-Live)"
        ],
        "card2_title": "2) สิ่งที่ต้องเตรียมก่อนเริ่ม UAT",
        "card2_items": [
            {"title": "1. UAT Test Scenarios", "desc": "โจทย์การทดสอบตามขั้นตอนการทำงานจริง", "icon": "doc"},
            {"title": "2. Master Data & Accounts", "desc": "ข้อมูลตั้งต้นและสิทธิ์ผู้ใช้เสมือนจริง", "icon": "users"},
            {"title": "3. Environment พร้อม", "desc": "ระบบทดสอบที่มีความเสถียรและข้อมูลตรง", "icon": "screen"},
            {"title": "4. Defect Log & Severity", "desc": "แบบฟอร์มบันทึกและเกณฑ์จัดระดับบั๊ก", "icon": "alert"}
        ],
        "card2_footer": "เตรียมคู่มือและบรีฟทำความเข้าใจกับ User ล่วงหน้า",
        "card3_title": "3) ขั้นตอนกระบวนการ UAT",
        "flow_steps": [
            {"title": "Kick-off Brief", "icon": "users"},
            {"title": "User Execution", "icon": "screen"},
            {"title": "Log Defect & Fix", "icon": "alert"},
            {"title": "Re-test & Sign-off", "icon": "check"}
        ],
        "card3_subcaption": "บันทึกผลการทดสอบและเอกสารลงนามอนุมัติอย่างเป็นทางการ",
        "card4_title": "4) ข้อควรระวังใน UAT",
        "card4_items": [
            "User เข้าใจผิดว่า UAT คือช่วงเวลาขอเพิ่มฟีเจอร์ใหม่",
            "ไม่ได้เตรียมข้อมูลทดสอบ ทำให้ติดขัดระหว่างการทำ Flow",
            "ไม่มีเกณฑ์ Sign-off ที่ชัดเจน ทำให้ปิด UAT ไม่ลง",
            "ให้ User ทดสอบโดยไม่มีทีมงานคอยซัพพอร์ตตอบคำถาม"
        ],
        "card4_warning": "ต้องแยกให้ชัดเจนระหว่าง บั๊กของระบบ (Defect) กับ คำขอใหม่ (Change Request)",
        "card5_title": "5) สรุป",
        "card5_icon": "check",
        "card5_text": "UAT ที่ประสบความสำเร็จ<strong>ช่วยสร้างความมั่นใจสูงสุดให้แก่องค์กร</strong> ทำให้การเปลี่ยนผ่านระบบใหม่เป็นไปอย่างราบรื่นและไร้รอยต่อ",
        "memory_pills": ["UAT สำเร็จ", "เตรียม Scenario", "User เทสจริง", "เคลียร์บั๊กครบ", "Sign-off Go-Live"]
    },

    # 18. User Story.md
    {
        "file_rel": "User Story.md",
        "output_name": "User_Story_Mastery",
        "tag": "ZURI AGILE • USER STORY",
        "title_plain": "User Story เขียนยังไงให้ทรงพลัง ?",
        "title_html": "User Story <span class=\"highlight\">เขียนยังไงให้ทรงพลัง ?</span>",
        "subtitle": "อธิบายความต้องการจากมุมมองของผู้ใช้ พร้อมมอบคุณค่าที่แท้จริง",
        "sticky_text": "User ชัดเจน Goal ตรงจุด Benefit โดนใจ! 💡",
        "equation": "User Story = As a [User], I want [Action/Goal], So that [Benefit/Value]",
        "card1_title": "1) องค์ประกอบ 3Cs",
        "card1_subtitle": "หัวใจสำคัญของ User Story ที่ดี:",
        "card1_items": [
            "Card: สรุปความต้องการสั้นๆ กระชับ บนการ์ดหรือกระดาน",
            "Conversation: บทสนทนาแลกเปลี่ยนระหว่าง PO, BA, Dev และ QA",
            "Confirmation: ข้อตกลงร่วมกันว่าแบบไหนถึงเรียกว่าเสร็จ (AC)"
        ],
        "card2_title": "2) หลักการ INVEST Framework",
        "card2_items": [
            {"title": "Independent", "desc": "แยกเป็นอิสระจาก Story อื่นให้ได้มากที่สุด", "icon": "layers"},
            {"title": "Negotiable & Valuable", "desc": "ปรับเปลี่ยนต่อรองได้ และสร้างคุณค่าจริง", "icon": "sparkles"},
            {"title": "Estimable & Small", "desc": "ประเมินแรงงานได้ และมีขนาดเล็กพอทำใน Sprint", "icon": "clock"},
            {"title": "Testable", "desc": "สามารถเขียนการทดสอบเพื่อพิสูจน์ผลลัพธ์ได้", "icon": "check"}
        ],
        "card2_footer": "Story ที่ดีต้องตอบโจทย์ครบทั้ง 6 ด้านของ INVEST",
        "card3_title": "3) ตัวอย่างที่ดี vs ตัวอย่างที่ไม่ดี",
        "flow_steps": [
            {"title": "As a ผู้ซื้อ", "icon": "users"},
            {"title": "I want ประวัติสั่งซื้อ", "icon": "doc"},
            {"title": "So that เบิกเงินบริษัทได้", "icon": "sparkles"},
            {"title": "AC: มี PDF ใบเสร็จ", "icon": "check"}
        ],
        "card3_subcaption": "ดี: ระบุประโยชน์ชัดเจน | ไม่ดี: 'ทำหน้าประวัติคำสั่งซื้อให้สวยๆ'",
        "card4_title": "4) ข้อผิดพลาดที่พบบ่อย",
        "card4_items": [
            "เขียนเป็น Technical Task แทนที่จะเป็นมุมมองของผู้ใช้",
            "ละเลยส่วน 'So that' ทำให้ทีมไม่รู้ว่าสร้างไปเพื่ออะไร",
            "Story ใหญ่เกินไปจนทำไม่เสร็จภายใน 1 Sprint",
            "ไม่มี Acceptance Criteria แนบมาด้วย"
        ],
        "card4_warning": "User Story ไม่ใช่สเปกสำเร็จรูป แต่เป็นคำเชิญให้ทีมมาร่วมสนทนากัน",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "User Story ที่ยอดเยี่ยม<strong>ช่วยเชื่อมต่อใจของผู้ใช้เข้ากับโค้ดของทีม</strong> ทำให้ทุกฟีเจอร์ที่ปล่อยออกมาสร้างผลกระทบเชิงบวกได้อย่างแท้จริง",
        "memory_pills": ["User Story", "ใคร (As a)", "ทำอะไร (I want)", "เพื่ออะไร (So that)", "ตรวจรับด้วย AC"]
    },

    # 19. BA/comunication-rule01-BA-DEV.md
    {
        "file_rel": "BA/comunication-rule01-BA-DEV.md",
        "output_name": "BA_Dev_Communication",
        "tag": "ZURI COLLABORATION • RULES OF ENGAGEMENT",
        "title_plain": "กฎเหล็กการสื่อสารระหว่าง BA กับ Dev",
        "title_html": "กฎเหล็กการสื่อสาร <span class=\"highlight\">ระหว่าง BA กับ Dev</span>",
        "subtitle": "ลดช่องว่างภาษาธุรกิจและเทคนิค ทำงานประสานกันอย่างราบรื่น",
        "sticky_text": "คุยเคลียร์ ส่งงานเป๊ะ ไม่เดาใจ สบายใจทั้งสองฝ่าย! 💡",
        "equation": "Smooth Collaboration = เล่าปัญหาไม่ใช่สั่ง Solution + ใช้ Flowchart + ล็อก AC เป็นลายลักษณ์อักษร",
        "card1_title": "1) กฎข้อที่ 1 & 2: เริ่มต้นด้วยความเข้าใจ",
        "card1_subtitle": "ปรับทัศนคติการพูดคุย:",
        "card1_items": [
            "กฎที่ 1: เล่า 'ปัญหาและเป้าหมายของธุรกิจ' ไม่ใช่มาสั่งวิธีการทางเทคนิค ปล่อยให้ Dev ช่วยออกแบบ Solution ที่ดีที่สุด",
            "กฎที่ 2: สื่อสารด้วยภาพ Flowchart, Wireframe และ Data Model เสมอ ดีกว่าการใช้ตัวหนังสือบรรยายยาวเหยียด"
        ],
        "card2_title": "2) กฎข้อที่ 3 & 4: ความชัดเจนและวินัย",
        "card2_items": [
            {"title": "กฎที่ 3: ดักทุกทาง", "desc": "ระบุทั้ง Happy Path, Negative Case และ Edge Case ให้ครบ", "icon": "shield"},
            {"title": "กฎที่ 4: ลายลักษณ์อักษร", "desc": "ห้ามเปลี่ยน Requirement ปากเปล่า ต้องอัปเดตการ์ดงานเสมอ", "icon": "doc"},
            {"title": "กฎที่ 5: ฟังมุมมอง Tech", "desc": "เปิดรับข้อจำกัดด้านสถาปัตยกรรมและ Performance", "icon": "screen"}
        ],
        "card2_footer": "ความชัดเจนช่วยสร้างความไว้วางใจระหว่างสายงาน",
        "card3_title": "3) จังหวะการพูดคุยที่ถูกต้อง",
        "flow_steps": [
            {"title": "ชวน Dev ฟัง Req", "icon": "users"},
            {"title": "Walkthrough Flow", "icon": "screen"},
            {"title": "Clarify AC", "icon": "check"},
            {"title": "Sprint Support", "icon": "sparkles"}
        ],
        "card3_subcaption": "คุยกันบ่อยๆ แต่สั้นและตรงประเด็น ดีกว่ารอประชุมยาวรอบเดียว",
        "card4_title": "4) พฤติกรรมต้องห้าม",
        "card4_items": [
            "โยนเอกสารหนาๆ ให้ Dev อ่านเองโดยไม่มีการบรีฟ",
            "Dev ตัดสินใจเปลี่ยน Business Logic เองโดยไม่ปรึกษา BA",
            "แอบแก้ Requirement กลางคันโดยไม่แจ้งผลกระทบ",
            "กล่าวโทษกันเมื่อเกิดข้อผิดพลาดแทนที่จะช่วยกันแก้ปัญหา"
        ],
        "card4_warning": "ความเงียบคือศัตรูตัวร้าย หากมีข้อสงสัยให้รีบถามทันที",
        "card5_title": "5) สรุป",
        "card5_icon": "users",
        "card5_text": "BA และ Dev คือ<strong>พาร์ตเนอร์ร่วมสร้างสรรค์ผลงาน</strong> เมื่อสื่อสารด้วยความเข้าอกเข้าใจและข้อมูลที่ชัดเจน งานจะสำเร็จได้อย่างงดงาม",
        "memory_pills": ["BA & Dev ซิงก์", "เล่าเป้าหมาย", "สื่อสารด้วย Flow", "ล็อก AC", "อัปเดตทุกการแก้"]
    },

    # 20. case-study/CASE-01.md
    {
        "file_rel": "case-study/CASE-01.md",
        "output_name": "Case_01_Mid_Sprint_Change",
        "tag": "ZURI CASE STUDY • INCIDENT 01",
        "title_plain": "CASE 01: ลูกค้าขอเปลี่ยนงานกลาง Sprint",
        "title_html": "CASE 01: ลูกค้าขอเปลี่ยนงาน <span class=\"danger-highlight\">กลาง Sprint !</span>",
        "subtitle": "วิธีรับมืออย่างมืออาชีพเมื่อมีคำขอด่วนแทรกเข้ามาระหว่างทาง",
        "sticky_text": "รับฟังอย่างเข้าใจ ประเมินผลกระทบ เจรจาด้วยทางเลือก! 💡",
        "equation": "Mid-Sprint Handling = รับฟังความจำเป็น ➔ ประเมิน Impact ➔ เสนอ Trade-off ➔ สรุป Decision",
        "card1_title": "1) เหตุการณ์ที่พบ (Scenario)",
        "card1_subtitle": "Sprint กำลังดำเนินไปได้ครึ่งทาง:",
        "card1_items": [
            "ลูกค้าหรือ Stakeholder ขอปรับ Flow การทำงานกะทันหัน",
            "ต้องการเพิ่มฟิลด์และเงื่อนไขใหม่ทันทีในรอบนี้",
            "หากรับเข้ามาตรงๆ จะทำให้งานเดิมที่ Commit ไว้ทำไม่เสร็จ",
            "ทีม Dev เริ่มเกิดความสับสนและกังวลเรื่องเวลาส่งมอบ"
        ],
        "card2_title": "2) ขั้นตอนการจัดการ 4 สเต็ป",
        "card2_items": [
            {"title": "1. รับฟังและเข้าใจปัญหา", "desc": "ถามเหตุผลทางธุรกิจว่าทำไมต้องด่วนตอนนี้", "icon": "users"},
            {"title": "2. ประเมินผลกระทบ (Impact)", "desc": "คำนวณเวลากับ Dev และเช็กผลต่อ Sprint Goal", "icon": "clock"},
            {"title": "3. เสนอทางเลือก (Options)", "desc": "ให้ Stakeholder เป็นผู้ตัดสินใจเลือก", "icon": "layers"},
            {"title": "4. บันทึกลงในระบบ", "desc": "อัปเดต Backlog และบันทึกข้อตกลงเป็นทางการ", "icon": "doc"}
        ],
        "card2_footer": "ไม่ตอบปฏิเสธทันที แต่ตอบด้วยทางเลือกและผลกระทบ",
        "card3_title": "3) 2 ทางเลือกหลักในการเจรจา",
        "flow_steps": [
            {"title": "คำขอใหม่เข้ามา", "icon": "alert"},
            {"title": "Option A: Sprint หน้า", "icon": "doc"},
            {"title": "Option B: Swap งานออก", "icon": "layers"},
            {"title": "ล็อกข้อตกลง", "icon": "check"}
        ],
        "card3_subcaption": "ถ้าเลือก Option B ต้องถอดงานเดิมออกด้วย Effort ที่เท่ากัน",
        "card4_title": "4) สิ่งที่ไม่ควรทำเด็ดขาด",
        "card4_items": [
            "รับปากทันทีโดยไม่ปรึกษาทีม Dev และ QA",
            "ปฏิเสธเสียงแข็งโดยไม่รับฟังเหตุผลทางธุรกิจของลูกค้า",
            "แอบเพิ่มงานเข้ากระดานโดยไม่แจ้งให้ทีมทราบ",
            "บังคับให้ทีมทำงานล่วงเวลาเพื่อยัดงานที่เพิ่มเข้ามา"
        ],
        "card4_warning": "Sprint Goal คือสัญญาใจ การรับงานแทรกโดยไม่ตัดงานเก่าจะทำให้ระบบพัง",
        "card5_title": "5) บทเรียนสำคัญ",
        "card5_icon": "shield",
        "card5_text": "ความเป็นมืออาชีพวัดกันที่<strong>ความสามารถในการบริหารความคาดหวัง</strong> อธิบายผลกระทบอย่างตรงไปตรงมา และร่วมกันหาทางออกที่ win-win ทุกฝ่าย",
        "memory_pills": ["เคสงานแทรก", "เข้าใจเหตุผล", "ประเมิน Impact", "แลกงานออก หรือ รอสปริ้นต์หน้า"]
    },

    # 21. case-study/CASE-02.md
    {
        "file_rel": "case-study/CASE-02.md",
        "output_name": "Case_02_Project_Delay",
        "tag": "ZURI CASE STUDY • INCIDENT 02",
        "title_plain": "CASE 02: งานติดคอขวด โปรเจกต์จ่อ Delay",
        "title_html": "CASE 02: งานติดคอขวด <span class=\"danger-highlight\">โปรเจกต์จ่อ Delay !</span>",
        "subtitle": "แก้วิกฤตงานค้างและกู้คืนความเร็วในการส่งมอบได้อย่างทันท่วงที",
        "sticky_text": "เจอเร็ว แก้ตรงจุด ตัด Scope ทันเวลา ไม่ปล่อยให้พัง! 💡",
        "equation": "Crisis Recovery = ค้นหา Root Cause ➔ ตัดส่วนไม่จำเป็น ➔ รวมพลัง Swarming ➔ สื่อสารความจริง",
        "card1_title": "1) เหตุการณ์ที่พบ (Scenario)",
        "card1_subtitle": "เหลือเวลาอีก 3 วันจะหมด Sprint:",
        "card1_items": [
            "งานเกือบทั้งหมดยังติดค้างอยู่ในสถานะ In Progress / Blocked",
            "QA ยังไม่ได้เริ่มเทสเพราะยังไม่มีชิ้นงานส่งมาถึงมือ",
            "มีปัญหาทางเทคนิคและ Dependency ภายนอกที่ยังไม่คลี่คลาย",
            "มีแนวโน้มสูงมากที่จะส่งมอบงานตามเป้าหมายไม่ทัน"
        ],
        "card2_title": "2) วิเคราะห์สาเหตุที่แท้จริง (Root Cause)",
        "card2_items": [
            {"title": "Task ใหญ่เกินไป", "desc": "ไม่ได้ซอยงานให้เล็กพอที่จะทยอยส่งมอบได้", "icon": "layers"},
            {"title": "Unplanned Dependency", "desc": "ติดรอ API หรือสิทธิ์เข้าถึงจากทีมอื่น", "icon": "shield"},
            {"title": "ไม่ยกปัญหาใน Daily", "desc": "พยายามแก้คนเดียวจนเวลาล่วงเลย", "icon": "alert"},
            {"title": "ขาดคนช่วยรีวิวโค้ด", "desc": "เกิดคอขวดในขั้นตอน Code Review", "icon": "users"}
        ],
        "card2_footer": "ต้องระบุสาเหตุให้ชัดเพื่อแก้ไขให้ตรงจุด",
        "card3_title": "3) แผนกู้วิกฤตแบบเร่งด่วน",
        "flow_steps": [
            {"title": "รวมพลัง Swarming", "icon": "users"},
            {"title": "Descope งานรอง", "icon": "layers"},
            {"title": "ส่งของให้ QA เทส", "icon": "shield"},
            {"title": "อัปเดตสถานะจริง", "icon": "sparkles"}
        ],
        "card3_subcaption": "โฟกัสส่งมอบเฉพาะ Core Value ที่สำคัญที่สุดก่อน",
        "card4_title": "4) การสื่อสารกับ Stakeholder",
        "card4_items": [
            "แจ้งเตือนล่วงหน้าทันที ไม่รอจนถึงวันสุดท้ายของ Sprint",
            "อธิบายอย่างโปร่งใสว่าอะไรที่จะเสร็จ และอะไรที่ต้องเลื่อน",
            "นำเสนอแผนฟื้นฟูและกำหนดการใหม่ที่ชัดเจน",
            "จัด Retrospective เพื่อวางระบบป้องกันไม่ให้เกิดขึ้นซ้ำ"
        ],
        "card4_warning": "ความล้มเหลวไม่ใช่การส่งงานไม่ครบ แต่คือการปกปิดปัญหาจนนาทีสุดท้าย",
        "card5_title": "5) บทเรียนสำคัญ",
        "card5_icon": "sparkles",
        "card5_text": "ความโปร่งใสคือหัวใจของความเชื่อมั่น <strong>กล้าเผชิญหน้ากับความจริงเร็ว</strong> จะช่วยให้ทีมปรับกระบวนท่าและกอบกู้สถานการณ์กลับมาได้เสมอ",
        "memory_pills": ["แก้งาน Delay", "เปิดเผยปัญหา", "ตัดงานรองออก", "ช่วยกันปลดบล็อก", "ส่งมอบ Core Value"]
    },

    # 22. case-study/CASE-03.md
    {
        "file_rel": "case-study/CASE-03.md",
        "output_name": "Case_03_Ambiguous_Requirement",
        "tag": "ZURI CASE STUDY • INCIDENT 03",
        "title_plain": "CASE 03: Requirement ไม่ชัด ทีมตีความคนละภาพ",
        "title_html": "CASE 03: Requirement ไม่ชัด <span class=\"danger-highlight\">ทีมตีความคนละภาพ !</span>",
        "subtitle": "แก้ปัญหาการรื้อระบบใหม่ และสร้างความเข้าใจตรงกันตั้งแต่ต้นน้ำ",
        "sticky_text": "เคลียร์ภาพให้ตรงกันตั้งแต่ Day 1 ลดการรื้อทิ้ง 100%! 💡",
        "equation": "Zero Misunderstanding = Wireframe + Given/When/Then + Confirmation Sign-off",
        "card1_title": "1) เหตุการณ์ที่พบ (Scenario)",
        "card1_subtitle": "ในวัน Sprint Demo ตรวจรับงาน:",
        "card1_items": [
            "Dev พัฒนาระบบตรงตามตัวหนังสือที่เขียนไว้ใน Story ทุกบรรทัด",
            "แต่ User อุทานว่า 'ไม่ใช่แบบที่คิดไว้เลย ทำไมใช้งานแบบนี้'",
            "ต้องรื้อหน้าจอและโค้ดใหม่ทั้งหมด เสียเวลาไปทั้ง Sprint",
            "เกิดความขัดแย้งและความผิดหวังระหว่างทีมธุรกิจกับทีมเทคนิค"
        ],
        "card2_title": "2) สาเหตุของช่องว่างความเข้าใจ",
        "card2_items": [
            {"title": "ใช้ข้อความบรรยายล้วน", "desc": "ไม่มีภาพหน้าจอหรือ Mockup ให้เห็นภาพจริง", "icon": "doc"},
            {"title": "ขาด Acceptance Criteria", "desc": "ไม่ได้ระบุเงื่อนไข Given/When/Then", "icon": "check"},
            {"title": "ต่างคนต่างคิดเอาเอง", "desc": "ไม่มีการ Walkthrough ซักถามก่อนเริ่มทำ", "icon": "alert"},
            {"title": "ไม่มีตัวอย่าง Data", "desc": "ไม่ได้แสดงตัวอย่างข้อมูลเข้าและผลลัพธ์", "icon": "screen"}
        ],
        "card2_footer": "ตัวหนังสือ 1 บรรทัด คน 10 คนตีความได้ 10 แบบ",
        "card3_title": "3) วิธีแก้และป้องกันไม่ให้เกิดขึ้นอีก",
        "flow_steps": [
            {"title": "จัด 30-min Alignment", "icon": "users"},
            {"title": "กาง Wireframe คู่ Flow", "icon": "screen"},
            {"title": "เขียน AC ดัก Edge Case", "icon": "check"},
            {"title": "ยืนยันตรงกันก่อนโค้ด", "icon": "sparkles"}
        ],
        "card3_subcaption": "ต้องมีภาพและผลลัพธ์ที่ตกลงร่วมกันก่อนเริ่มเขียนโค้ดเสมอ",
        "card4_title": "4) กฎเหล็ก 3Cs ในการเขียน Story",
        "card4_items": [
            "Card: การ์ดสรุปเป้าหมายสั้นๆ",
            "Conversation: นัดพูดคุยซักถามเพื่อทำความเข้าใจให้ลึกซึ้ง",
            "Confirmation: เขียนเกณฑ์การตรวจรับให้ชัดเจนเป็นลายลักษณ์อักษร"
        ],
        "card4_warning": "อย่าเริ่มเขียนโค้ดแม้แต่บรรทัดเดียว หากยังไม่เห็นภาพผลลัพธ์ตรงกัน",
        "card5_title": "5) บทเรียนสำคัญ",
        "card5_icon": "check",
        "card5_text": "ภาพหนึ่งภาพมีค่ามากกว่าตัวหนังสือพันคำ <strong>การสื่อสารด้วยภาพและตัวอย่างจริง</strong> จะช่วยป้องกันการรื้อโค้ดและรักษาความสัมพันธ์ในทีมได้อย่างดีที่สุด",
        "memory_pills": ["เคลียร์ Requirement", "วาดภาพให้ดู", "เขียน AC ให้ครบ", "ซักถามให้เคลียร์", "ยืนยันตรงกัน"]
    },

    # 23. case-study/CASE-06.md
    {
        "file_rel": "case-study/CASE-06.md",
        "output_name": "Case_06_AI_Agent_Audit",
        "tag": "ZURI CASE STUDY • AI GOVERNANCE",
        "title_plain": "CASE 06: AI Agent ส่งงานไม่ตรงสเปก ตรวจสอบอย่างไร ?",
        "title_html": "CASE 06: AI Agent ส่งงานไม่ตรงสเปก <span class=\"danger-highlight\">ตรวจสอบอย่างไร ?</span>",
        "subtitle": "วิธีตรวจสอบ แก้ไข และสร้าง Guardrails เมื่อ AI ทำงานหลุดกรอบ",
        "sticky_text": "Prompt ชัด สเปกเป๊ะ Guardrail แน่น AI ทำงานแม่นยำ 100%! 💡",
        "equation": "AI Reliability = Precise Context + Canonical Schema + Automated Validation Gates",
        "card1_title": "1) เหตุการณ์ที่พบ (Scenario)",
        "card1_subtitle": "เมื่อ AI Agent ส่งมอบงาน:",
        "card1_items": [
            "โค้ดหรือเอกสารที่สร้างขึ้นมีโครงสร้างไม่ตรงกับ Canonical Schema",
            "เกิดอาการ Hallucination สร้าง Entity หรือ API ที่ไม่มีอยู่จริง",
            "ระบบ Linting และ Unit Test แจ้งเตือนข้อผิดพลาด",
            "จำเป็นต้องมีขั้นตอน Audit และปรับแต่ง Guardrail อย่างเป็นระบบ"
        ],
        "card2_title": "2) ขั้นตอนการ Audit 5 สเต็ป",
        "card2_items": [
            {"title": "1. ตรวจกับ Schema Contract", "desc": "เทียบผลลัพธ์กับ schema_genesisblock.yaml", "icon": "shield"},
            {"title": "2. เช็ก Prompt & System Context", "desc": "ดูว่าได้รับ Context เพียงพอและถูกต้องหรือไม่", "icon": "doc"},
            {"title": "3. แยกแยะปัญหา", "desc": "แยกให้ออกว่าเป็น Bug, Data Gap หรือ Prompt Ambiguity", "icon": "alert"},
            {"title": "4. ปรับ System Directive", "desc": "เพิ่มตัวอย่าง One-shot/Few-shot ที่ถูกต้อง", "icon": "sparkles"},
            {"title": "5. รัน Automated Gate", "desc": "ใช้ Linter และ Test ตรวจสอบก่อน Accept", "icon": "check"}
        ],
        "card2_footer": "ไม่แก้ไขที่ปลายทางอย่างเดียว ต้องแก้ที่ต้นเหตุของ Context",
        "card3_title": "3) สถาปัตยกรรมกำกับดูแล AI (AI Guardrail)",
        "flow_steps": [
            {"title": "Strict Schema", "icon": "shield"},
            {"title": "Prompt Context", "icon": "doc"},
            {"title": "AI Execution", "icon": "screen"},
            {"title": "Validation Gate", "icon": "check"}
        ],
        "card3_subcaption": "ต้อง Fail Closed ทันทีหากข้อมูลไม่ตรงตาม Schema Contract",
        "card4_title": "4) สัญญาณอันตรายของ AI Output",
        "card4_items": [
            "สร้าง Primary Key หรือ ID Format ที่ผิดแปลกจากระบบเดิม",
            "หลุดข้อมูล PII หรือข้อมูลลับที่ไม่ได้รับอนุญาต",
            "โค้ดทำงานได้แต่ข้าม Invariants สำคัญทางธุรกิจ",
            "ให้คำตอบแบบคาดเดาโดยไม่มีหลักฐานอ้างอิง"
        ],
        "card4_warning": "AI คือผู้ช่วยที่ทรงพลัง แต่ต้องอยู่ภายใต้ Governance ที่รัดกุมเสมอ",
        "card5_title": "5) บทเรียนสำคัญ",
        "card5_icon": "shield",
        "card5_text": "ความแม่นยำของ AI ขึ้นอยู่กับ<strong>คุณภาพของ Context และ Schema</strong> การสร้าง Guardrail ตรวจสอบอัตโนมัติจะช่วยให้ใช้งาน AI ได้อย่างปลอดภัยและมั่นใจ",
        "memory_pills": ["AI Governance", "Schema นิ่ง", "Context ครบ", "มี Gate ตรวจสอบ", "ปลอดภัย 100%"]
    },

    # 24. PM/PM-req.md
    {
        "file_rel": "PM/PM-req.md",
        "output_name": "PM_Risk_Management",
        "tag": "ZURI MANAGEMENT • RISK GOVERNANCE",
        "title_plain": "6 ความเสี่ยงสำคัญที่ PM ต้องเฝ้าระวัง !",
        "title_html": "6 ความเสี่ยงสำคัญที่ <span class=\"highlight\">PM ต้องเฝ้าระวัง !</span>",
        "subtitle": "มองเห็นปัญหาล่วงหน้า วางแผนป้องกัน บริหารโครงการได้ตามเป้าหมาย",
        "sticky_text": "มองการณ์ไกล ดักความเสี่ยง คุมงบและเวลาอยู่หมัด! 💡",
        "equation": "Risk Management = ระบุความเสี่ยง ➔ ประเมินความน่าจะเป็น ➔ วางแผนป้องกัน (Mitigation)",
        "card1_title": "1) Scope & Schedule Risk",
        "card1_subtitle": "ความเสี่ยงด้านขอบเขตและเวลา:",
        "card1_items": [
            "Scope Risk: ขอบเขตงานบวม ไม่ชัดเจน มีการแก้งานบ่อย",
            "Schedule Risk: งานดีเลย์ ติดรอ Dependency ภายนอก ส่งมอบไม่ทัน",
            "วิธีแก้: ทำ In/Out Scope ชัดเจน และมี Buffer Time เสมอ"
        ],
        "card2_title": "2) Resource & Technical Risk",
        "card2_items": [
            {"title": "Resource Risk", "desc": "ทีมงานลาออก ขาดทักษะเฉพาะทาง ทีมหมดไฟ", "icon": "users"},
            {"title": "Technical Risk", "desc": "ระบบเก่าซับซ้อน ติดสิทธิ์ Security หรือ Performance ตก", "icon": "screen"},
            {"title": "Stakeholder Risk", "desc": "ผู้บริหารเปลี่ยนทิศทาง ติดต่อคนตัดสินใจยาก", "icon": "alert"},
            {"title": "Quality Risk", "desc": "บั๊กสะสมเยอะ UAT ไม่ผ่านตามเกณฑ์", "icon": "shield"}
        ],
        "card2_footer": "จัดทำ Risk Register อัปเดตทุกสัปดาห์",
        "card3_title": "3) ลำดับการบริหารความเสี่ยงอย่างมือโปร",
        "flow_steps": [
            {"title": "Identify Risk", "icon": "alert"},
            {"title": "Assess Impact", "icon": "layers"},
            {"title": "Plan Mitigation", "icon": "shield"},
            {"title": "Monitor Weekly", "icon": "clock"}
        ],
        "card3_subcaption": "ดักจับตั้งแต่สัญญาณเตือนแรก อย่ารอให้กลายเป็นวิกฤต",
        "card4_title": "4) หลุมพรางที่ PM มักพลาด",
        "card4_items": [
            "วางแผนแบบ Best-case Scenario โดยไม่มีแผนสำรอง",
            "เกรงใจผู้บริหารจนไม่กล้าบอกความจริงเรื่องความเสี่ยง",
            "มัวแต่วุ่นกับเอกสารจนลืมสังเกตความผิดปกติในทีม",
            "ไม่เคยทบทวนความเสี่ยงใหม่ๆ ระหว่างโครงการ"
        ],
        "card4_warning": "PM ที่ดีไม่ได้วัดจากการไม่มีปัญหา แต่วัดจากความพร้อมในการรับมือ",
        "card5_title": "5) สรุป",
        "card5_icon": "shield",
        "card5_text": "หน้าที่ของ PM คือ<strong>การถางทางและขจัดอุปสรรคให้ทีม</strong> การบริหารความเสี่ยงที่ดีจะช่วยให้โปรเจกต์ส่งมอบความสำเร็จได้อย่างราบรื่น",
        "memory_pills": ["PM คุมเสี่ยง", "ส่อง 6 มิติ", "ประเมิน Impact", "วางแผนป้องกัน", "ขับเคลื่อนโปรเจกต์"]
    },

    # 25. PO/PO-req.md
    {
        "file_rel": "PO/PO-req.md",
        "output_name": "PO_Decision_Making",
        "tag": "ZURI PRODUCT • PO STRATEGY",
        "title_plain": "PO ตัดสินใจจากอะไร ? 5 ปัจจัยเลือกงานเข้า Product",
        "title_html": "PO ตัดสินใจจากอะไร ? <span class=\"highlight\">5 ปัจจัยเลือกงานเข้า Product</span>",
        "subtitle": "เพิ่ม Value สูงสุด ตอบโจทย์ผู้ใช้ และคุ้มค่าต่อการลงทุนของธุรกิจ",
        "sticky_text": "ตัดสินใจแม่นยำ สร้าง Impact ชัดเจน ขับเคลื่อน Product สู่เป้าหมาย! 💡",
        "equation": "PO Decision = Business Strategy + User Value + Data Evidence + Feasibility + ROI",
        "card1_title": "1) ปัจจัยด้านธุรกิจและผู้ใช้",
        "card1_subtitle": "เป้าหมายหลักในการสร้างผลลัพธ์:",
        "card1_items": [
            "1. Business Strategy: ฟีเจอร์นี้สอดคล้องกับเป้าหมายหลักขององค์กรหรือไม่",
            "2. User Value: แก้ไขปัญหา Pain Point ที่แท้จริงของผู้ใช้ได้ตรงจุดแค่ไหน",
            "3. Data & Feedback: มีข้อมูลตัวเลขหรือผลตอบรับจากผู้ใช้จริงรองรับหรือไม่"
        ],
        "card2_title": "2) ปัจจัยด้านเทคนิคและความคุ้มค่า",
        "card2_items": [
            {"title": "4. Feasibility & Effort", "desc": "ความเป็นไปได้ทางเทคนิคและแรงงานที่ต้องใช้", "icon": "screen"},
            {"title": "5. Risk & Dependency", "desc": "ความเสี่ยงทางกฎหมาย ความปลอดภัย และระบบข้างเคียง", "icon": "shield"},
            {"title": "ROI Analysis", "desc": "ผลตอบแทนที่ได้รับเทียบกับทรัพยากรที่ลงทุน", "icon": "sparkles"}
        ],
        "card2_footer": "ทุกการตัดสินใจต้องสามารถอธิบายเหตุผลได้อย่างโปร่งใส",
        "card3_title": "3) ขั้นตอนการกลั่นกรองงานของ PO",
        "flow_steps": [
            {"title": "รับไอเดีย", "icon": "bulb"},
            {"title": "กรอง 5 ปัจจัย", "icon": "layers"},
            {"title": "Prioritize", "icon": "target"},
            {"title": "Sprint Commit", "icon": "check"}
        ],
        "card3_subcaption": "กล้าปฏิเสธไอเดียที่ไม่สร้างคุณค่าอย่างสุภาพ",
        "card4_title": "4) กับดักที่ PO ต้องระวัง",
        "card4_items": [
            "ตัดสินใจตามอารมณ์หรือความชอบส่วนตัว",
            "พยายามเอาใจทุกคนจนทำให้ Product ไร้จุดยืน",
            "เลือกทำแต่งานง่ายๆ ที่ไม่สร้างผลกระทบต่อธุรกิจ",
            "ไม่เคยกลับมาวัดผลหลังจากปล่อยฟีเจอร์ไปแล้ว"
        ],
        "card4_warning": "PO ที่ยอดเยี่ยมต้องกล้าปฏิเสธ 90% ของคำขอ เพื่อมุ่งเน้น 10% ที่สำคัญที่สุด",
        "card5_title": "5) สรุป",
        "card5_icon": "target",
        "card5_text": "การเป็น PO คือ<strong>การเป็นผู้พิทักษ์คุณค่าของ Product</strong> เมื่อตัดสินใจบนพื้นฐานของข้อมูลและเป้าหมายที่ชัดเจน ความสำเร็จจะตามมาอย่างแน่นอน",
        "memory_pills": ["PO ตัดสินใจ", "ตรงเป้าธุรกิจ", "ผู้ใช้ได้ประโยชน์", "มีข้อมูลรองรับ", "คุ้มค่าการลงแรง"]
    },

    # 26. Requirement/Bad-Requirement.md
    {
        "file_rel": "Requirement/Bad-Requirement.md",
        "output_name": "Bad_Requirement_Fixes",
        "tag": "ZURI REQUIREMENTS • PITFALLS & FIXES",
        "title_plain": "5 สัญญาณเตือน Bad Requirement และวิธีแก้ไข",
        "title_html": "5 สัญญาณเตือน <span class=\"danger-highlight\">Bad Requirement และวิธีแก้ไข</span>",
        "subtitle": "กำจัดความคลุมเครือ ลดความเสี่ยงในการพัฒนาซอฟต์แวร์",
        "sticky_text": "จับสัญญาณเตือน แก้ไขแต่เนิ่นๆ ป้องกันโปรเจกต์ล่ม! 💡",
        "equation": "Bad Requirement = คำกว้าง + ขาด Persona + ไม่มี Goal + ไร้ AC + Test ไม่ได้",
        "card1_title": "1) สัญญาณเตือนข้อที่ 1 & 2",
        "card1_subtitle": "ความกำกวมและไร้ตัวตน:",
        "card1_items": [
            "สัญญาณ 1: ใช้คำกว้างๆ ลอยๆ เช่น 'ระบบต้องเร็ว', 'ใช้งานง่าย', 'ปลอดภัย'",
            "วิธีแก้: ระบุตัวเลขชัดเจน เช่น 'ตอบสนองภายใน 1.5 วินาทีเมื่อมี 1,000 Concurrent'",
            "สัญญาณ 2: ระบุผู้ใช้ไม่ชัดเจน เช่น 'ผู้ใช้ทุกคนสามารถ...'",
            "วิธีแก้: ระบุ Persona และ Role ให้เฉพาะเจาะจง เช่น 'Admin ฝ่ายบัญชี'"
        ],
        "card2_title": "2) สัญญาณเตือนข้อที่ 3, 4 & 5",
        "card2_items": [
            {"title": "3. ขาด Business Goal", "desc": "ไม่บอกว่าทำไปทำไม ทำให้แก้ปัญหาไม่ตรงจุด", "icon": "target"},
            {"title": "4. ไม่มี Acceptance Criteria", "desc": "Dev และ QA ไม่รู้ว่าเกณฑ์ผ่านคืออะไร", "icon": "check"},
            {"title": "5. ทดสอบไม่ได้ (Untestable)", "desc": "ไม่มีขั้นตอนที่พิสูจน์ผลลัพธ์ได้จริง", "icon": "shield"}
        ],
        "card2_footer": "Requirement ที่ดีต้องสามารถทดสอบได้เสมอ",
        "card3_title": "3) เปลี่ยน Bad เป็น Good ใน 4 ขั้นตอน",
        "flow_steps": [
            {"title": "หาคำกำกวม", "icon": "alert"},
            {"title": "แปลงเป็นตัวเลข", "icon": "doc"},
            {"title": "ใส่ Role & Flow", "icon": "screen"},
            {"title": "เติม AC ให้ครบ", "icon": "check"}
        ],
        "card3_subcaption": "อ่านทบทวนร่วมกันระหว่าง BA, Dev และ QA",
        "card4_title": "4) ผลกระทบจาก Requirement แย่ๆ",
        "card4_items": [
            "Dev เขียนโค้ดตามความเข้าใจของตัวเอง",
            "QA แตก Test Case ไม่ได้และดักบั๊กไม่หมด",
            "User ปฏิเสธการรับมอบงานตอนจบ Sprint",
            "ต้องรื้อระบบและเขียนโค้ดใหม่ทั้งหมด"
        ],
        "card4_warning": "ต้นทุนการแก้ Requirement ตอนเริ่มต้นถูกกว่าการแก้ตอนส่งมอบถึง 100 เท่า",
        "card5_title": "5) สรุป",
        "card5_icon": "check",
        "card5_text": "Requirement ที่ดี<strong>ไม่ได้วัดที่ความยาวของเอกสาร</strong> แต่วัดที่ความชัดเจน ความถูกต้อง และความเข้าใจตรงกันของทุกคนในทีม",
        "memory_pills": ["Bad ➔ Good Req", "แปลงคำเป็นตัวเลข", "ระบุ Role ชัด", "ใส่ Goal ให้ครบ", "ล็อก AC ให้เทสได้"]
    },

    # 27. Requirement/How-to-refinment-Requirement.md
    {
        "file_rel": "Requirement/How-to-refinment-Requirement.md",
        "output_name": "Requirement_Refinement_Guide",
        "tag": "ZURI REQUIREMENTS • STEP-BY-STEP",
        "title_plain": "ขั้นตอนการ Refine Requirement ทีละสเต็ป",
        "title_html": "ขั้นตอนการ Refine <span class=\"highlight\">Requirement ทีละสเต็ป</span>",
        "subtitle": "เปลี่ยนความต้องการดิบๆ ให้กลายเป็นงานที่พร้อมส่งต่อให้ทีมพัฒนา",
        "sticky_text": "กลั่นกรองละเอียด แตกย่อยชัดเจน พร้อมลุยงานต่อทันที! 💡",
        "equation": "Requirement Refined = เข้าใจปัญหา ➔ กำหนด Scope ➔ วาด Flow ➔ ล็อก AC ➔ Dev Review",
        "card1_title": "1) Step 1 & 2: ทำความเข้าใจและล้อมกรอบ",
        "card1_subtitle": "เริ่มต้นจากรากฐานที่ถูกต้อง:",
        "card1_items": [
            "Step 1: สัมภาษณ์และทำความเข้าใจ Pain Point ที่แท้จริงของผู้ใช้ (ไม่ใช่แค่สิ่งที่เขาขอ)",
            "Step 2: กำหนดขอบเขต In-Scope (สิ่งที่ทำ) และ Out-of-Scope (สิ่งที่ไม่ทำในรอบนี้) ให้เด็ดขาด"
        ],
        "card2_title": "2) Step 3 & 4: ออกแบบภาพและเงื่อนไข",
        "card2_items": [
            {"title": "Step 3: วาด User Flow", "desc": "แสดงขั้นตอนตั้งแต่เริ่มต้นจนจบ พร้อมทางแยก", "icon": "screen"},
            {"title": "Step 4: แตก User Story & AC", "desc": "เขียน Given/When/Then ให้ครบทุกกรณี", "icon": "check"},
            {"title": "Data Specification", "desc": "ระบุฟิลด์ข้อมูล ประเภท และเงื่อนไข Validation", "icon": "doc"}
        ],
        "card2_footer": "ยิ่งเห็นภาพชัด ความผิดพลาดยิ่งเป็นศูนย์",
        "card3_title": "3) 5 ขั้นตอนการ Refine ทีละสเต็ป",
        "flow_steps": [
            {"title": "1. ถาม Pain Point", "icon": "target"},
            {"title": "2. ล้อม Scope", "icon": "shield"},
            {"title": "3. วาด Flow", "icon": "screen"},
            {"title": "4. ใส่ AC", "icon": "check"},
            {"title": "5. Walkthrough", "icon": "users"}
        ],
        "card3_subcaption": "นำทีม Dev และ QA มาร่วม Walkthrough ในขั้นตอนที่ 5 เสมอ",
        "card4_title": "4) เช็กลิสต์ความพร้อมก่อนส่งมอบ",
        "card4_items": [
            "มีครบทั้ง Happy Flow และ Exception / Error Flow",
            "ระบุสิทธิ์การใช้งานของแต่ละ User Role ชัดเจน",
            "ทีม Dev และ QA ไม่มีข้อสงสัยค้างคาใจ",
            "ผ่านเกณฑ์ Definition of Ready (DoR) 100%"
        ],
        "card4_warning": "อย่าปล่อยให้มีจุดที่ต้อง 'ไว้ค่อยคุยกันตอนเริ่มโค้ด'",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "การ Refine Requirement คือ<strong>สะพานเชื่อมระหว่างจินตนาการกับความจริง</strong> ช่วยให้ทีมพัฒนาสร้างซอฟต์แวร์ได้อย่างรวดเร็วและแม่นยำ",
        "memory_pills": ["5 Steps Refine", "เข้าใจโจทย์", "ล้อม Scope", "วาด Flow", "ใส่ AC", "ซิงก์กับทีม"]
    },

    # 28. Requirement/Requirement Traceability.md
    {
        "file_rel": "Requirement/Requirement Traceability.md",
        "output_name": "Requirement_Traceability",
        "tag": "ZURI TRACEABILITY • RTM MATRIX",
        "title_plain": "Requirement Traceability เมทริกซ์เชื่อมโยงงาน",
        "title_html": "Requirement Traceability <span class=\"highlight\">เมทริกซ์เชื่อมโยงงาน</span>",
        "subtitle": "ติดตามงานตั้งแต่ต้นน้ำยันปลายน้ำ ไม่มีหลุด ไม่ตกหล่น และตรวจสอบได้",
        "sticky_text": "เช็กเส้นทางงาน ตรวจสอบง่าย ตรวจรับงานไร้รอยต่อ! 💡",
        "equation": "Traceability = Business Need ➔ System Req ➔ User Story ➔ Code ➔ Test Case ➔ Release",
        "card1_title": "1) Traceability Matrix คืออะไร?",
        "card1_subtitle": "ตารางเชื่อมโยงความสัมพันธ์ของงานตลอดทั้งวงจร:",
        "card1_items": [
            "ช่วยยืนยันว่าทุกความต้องการของธุรกิจถูกนำไปพัฒนาจริง (Forward Traceability)",
            "ช่วยยืนยันว่าทุกโค้ดที่เขียนมีเหตุผลทางธุรกิจรองรับ ไม่ใช่งานงอก (Backward Traceability)",
            "ช่วยให้วิเคราะห์ผลกระทบเมื่อมีการขอแก้งาน (Impact Analysis) ได้อย่างแม่นยำ"
        ],
        "card2_title": "2) โครงสร้างของตาราง RTM",
        "card2_items": [
            {"title": "1. Business Req ID", "desc": "รหัสความต้องการของธุรกิจ", "icon": "target"},
            {"title": "2. Functional Req / Story ID", "desc": "รหัสฟังก์ชันหรือการ์ดงาน", "icon": "doc"},
            {"title": "3. Dev Task & Module", "desc": "ส่วนของโค้ดหรือระบบที่พัฒนา", "icon": "screen"},
            {"title": "4. QA Test Case ID", "desc": "รหัสเคสที่ใช้ตรวจสอบความถูกต้อง", "icon": "shield"},
            {"title": "5. Status & Sign-off", "desc": "สถานะการส่งมอบและการตรวจรับ", "icon": "check"}
        ],
        "card2_footer": "สร้างความโปร่งใสและง่ายต่อการ Audit ตรวจสอบ",
        "card3_title": "3) สายธารความเชื่อมโยงระดับระบบ",
        "flow_steps": [
            {"title": "Business Need", "icon": "target"},
            {"title": "User Story", "icon": "doc"},
            {"title": "Source Code", "icon": "screen"},
            {"title": "Test Case", "icon": "shield"},
            {"title": "Go-Live", "icon": "sparkles"}
        ],
        "card3_subcaption": "มองเห็นเส้นทางของทุกความต้องการตั้งแต่จุดเริ่มต้นจนถึงมือผู้ใช้",
        "card4_title": "4) ประโยชน์ที่ได้รับจริง",
        "card4_items": [
            "ป้องกันฟังก์ชันตกหล่นระหว่างการพัฒนา",
            "เมื่อลูกค้าขอแก้ Requirement รู้ทันทีว่ากระทบโค้ดและเคสไหนบ้าง",
            "ช่วยให้ผู้บริหารและลูกค้ามั่นใจในการส่งมอบงาน",
            "ลดเวลาในการเตรียมเอกสารตรวจรับมอบงานและ Audit"
        ],
        "card4_warning": "RTM ต้องได้รับการอัปเดตอย่างต่อเนื่อง ไม่ใช่ทำเสร็จแล้วทิ้งไว้",
        "card5_title": "5) สรุป",
        "card5_icon": "link",
        "card5_text": "Traceability คือ<strong>แผนที่นำทางแห่งความรับผิดชอบ</strong> ช่วยให้โปรเจกต์มีความเป็นมืออาชีพ ควบคุมความเปลี่ยนแปลงได้ และส่งมอบได้อย่างสมบูรณ์แบบ",
        "memory_pills": ["Traceability Matrix", "ผูก Need", "แปลงเป็น Req", "ส่งเข้า Code", "ตรวจด้วย Test Case"]
    },

    # 29. Requirement/Requirement.md
    {
        "file_rel": "Requirement/Requirement.md",
        "output_name": "Requirement_Fundamentals",
        "tag": "ZURI FOUNDATIONS • REQUIREMENT 101",
        "title_plain": "Requirement คืออะไร ? หัวใจของการพัฒนา",
        "title_html": "Requirement คืออะไร ? <span class=\"highlight\">หัวใจของการพัฒนา</span>",
        "subtitle": "สะพานเชื่อมระหว่างความต้องการทางธุรกิจกับระบบเทคโนโลยี",
        "sticky_text": "เข้าใจแก่นแท้ สื่อสารตรงจุด สร้างระบบได้ตรงใจ! 💡",
        "equation": "Good Requirement = Business Need (ทำไม) + Functional Spec (ทำอะไร) + Non-Functional (คุณภาพ)",
        "card1_title": "1) นิยามของ Requirement",
        "card1_subtitle": "ข้อกำหนดและเงื่อนไขที่ระบบต้องมี:",
        "card1_items": [
            "คำอธิบายความสามารถและคุณสมบัติที่ระบบต้องมีเพื่อแก้ปัญหาให้ผู้ใช้",
            "เป็นข้อตกลงร่วมกันระหว่างฝั่งธุรกิจ ผู้ใช้งาน และทีมพัฒนา",
            "เป็นพิมพ์เขียวสำหรับการออกแบบ การเขียนโค้ด และการทดสอบ",
            "หาก Requirement ผิดพลาด ทุกอย่างที่สร้างตามมาจะผิดพลาดทั้งหมด"
        ],
        "card2_title": "2) 2 ประเภทหลักที่ต้องแยกให้ออก",
        "card2_items": [
            {"title": "Functional Requirements", "desc": "ระบบต้อง 'ทำอะไรได้บ้าง' เช่น สมัครสมาชิก, ชำระเงิน, ออกรายงาน", "icon": "screen"},
            {"title": "Non-Functional Requirements", "desc": "ระบบต้อง 'มีคุณภาพระดับไหน' เช่น ความเร็ว, ความปลอดภัย, ความเสถียร", "icon": "shield"},
            {"title": "Business Rules", "desc": "กฎและเงื่อนไขทางธุรกิจที่ระบบต้องบังคับใช้", "icon": "doc"}
        ],
        "card2_footer": "ต้องมีครบทั้งสองด้านจึงจะถือเป็นระบบที่สมบูรณ์",
        "card3_title": "3) องค์ประกอบสำคัญของ Requirement",
        "flow_steps": [
            {"title": "Business Need", "icon": "target"},
            {"title": "User Persona", "icon": "users"},
            {"title": "System Feature", "icon": "screen"},
            {"title": "Acceptance Rule", "icon": "check"}
        ],
        "card3_subcaption": "ตอบคำถาม: ใคร ทำอะไร เพื่ออะไร และวัดผลอย่างไร",
        "card4_title": "4) คุณสมบัติของ Requirement ที่ยอดเยี่ยม",
        "card4_items": [
            "Clear & Unambiguous: ชัดเจน ไม่ตีความได้หลายแบบ",
            "Complete: ข้อมูลครบถ้วน ทั้งกรณีปกติและกรณีผิดพลาด",
            "Consistent: ไม่ขัดแย้งกับ Requirement ข้ออื่น",
            "Verifiable & Testable: สามารถทดสอบและพิสูจน์ผลได้จริง"
        ],
        "card4_warning": "อย่าเริ่มลงมือสร้าง หากยังไม่เข้าใจว่าสร้างไปเพื่อตอบโจทย์อะไร",
        "card5_title": "5) สรุป",
        "card5_icon": "sparkles",
        "card5_text": "Requirement ที่ดี<strong>คือรากฐานที่มั่นคงของทุกความสำเร็จ</strong> ช่วยให้ทีมสร้างของได้ถูกต้องตั้งแต่ครั้งแรก และส่งมอบคุณค่าที่แท้จริงให้แก่ผู้ใช้งาน",
        "memory_pills": ["Requirement 101", "โจทย์ธุรกิจ (Need)", "ฟังก์ชันระบบ (Function)", "คุณภาพ (Quality)", "เกณฑ์วัดผล (AC)"]
    },

    # 30. Requirement/Workshop - Requirement.md
    {
        "file_rel": "Requirement/Workshop - Requirement.md",
        "output_name": "Requirement_Workshop",
        "tag": "ZURI ELICITATION • WORKSHOP GUIDE",
        "title_plain": "เทคนิคจัด Workshop เก็บ Requirement ให้ตรงจุด",
        "title_html": "เทคนิคจัด Workshop <span class=\"highlight\">เก็บ Requirement ให้ตรงจุด</span>",
        "subtitle": "ดึงความต้องการที่แท้จริงจาก Stakeholder อย่างมีประสิทธิภาพและสนุกสนาน",
        "sticky_text": "นำ Workshop โปร ดึงไอเดียเด่น ได้ Requirement ตรงจุด! 💡",
        "equation": "Successful Workshop = เตรียมโจทย์ล่วงหน้า + เปิดกว้างรับฟัง + กิจกรรม Interactive + สรุป Action ชัดเจน",
        "card1_title": "1) การเตรียมตัวก่อนเริ่ม Workshop",
        "card1_subtitle": "ความพร้อมก่อนเข้าสู่ห้องประชุม:",
        "card1_items": [
            "กำหนดเป้าหมายของเซสชันให้ชัดเจน (เช่น คัดเลือก Scope สำหรับ MVP)",
            "เชิญผู้เกี่ยวข้องตัวจริงที่มีอำนาจตัดสินใจและตัวแทนผู้ใช้งาน",
            "เตรียมเทมเพลต กระดานจำลอง (Miro/FigJam/Post-it) และโจทย์นำ",
            "ส่งข้อมูลพื้นฐานให้ผู้เข้าร่วมอ่านล่วงหน้าอย่างน้อย 1-2 วัน"
        ],
        "card2_title": "2) เทคนิคการดึงความคิดเห็นใน Session",
        "card2_items": [
            {"title": "1. User Journey Mapping", "desc": "พา Stakeholder เดินตามขั้นตอนการใช้งานจริง", "icon": "screen"},
            {"title": "2. Silent Brainstorming", "desc": "ให้เขียนลง Post-it เงียบๆ ก่อน เพื่อไม่ให้คนเสียงดังครอบงำ", "icon": "doc"},
            {"title": "3. 5 Whys Technique", "desc": "ถามเจาะลึก 'ทำไม' เพื่อค้นหา Pain Point ที่แท้จริง", "icon": "target"},
            {"title": "4. Dot Voting", "desc": "ให้โหวตเลือกไอเดียที่มี Impact สูงสุดอย่างเป็นประชาธิปไตย", "icon": "sparkles"}
        ],
        "card2_footer": "สร้างบรรยากาศที่ปลอดภัยและทุกคนกล้าออกความคิดเห็น",
        "card3_title": "3) ขั้นตอนการดำเนินกิจกรรม",
        "flow_steps": [
            {"title": "ตั้งโจทย์ปัญหา", "icon": "target"},
            {"title": "ระดมไอเดีย", "icon": "bulb"},
            {"title": "จัดกลุ่มหมวดหมู่", "icon": "layers"},
            {"title": "โหวต Priority", "icon": "check"},
            {"title": "สรุป Action Plan", "icon": "sparkles"}
        ],
        "card3_subcaption": "จบเซสชันด้วยข้อตกลงที่ชัดเจนพร้อมผู้รับผิดชอบ",
        "card4_title": "4) สิ่งที่ต้องหลีกเลี่ยงใน Workshop",
        "card4_items": [
            "ปล่อยให้ผู้เข้าร่วมบางคนผูกขาดการพูดตลอดเวลา",
            "เถียงกันเรื่องรายละเอียดทางเทคนิคจนลืมโฟกัสปัญหาของ User",
            "จบการประชุมโดยไม่มีการสรุปข้อตกลงและ Next Steps",
            "เปิดรับทุกไอเดียโดยไม่มีการจัดลำดับความสำคัญ (No Scope)"
        ],
        "card4_warning": "Workshop ที่ดีต้องได้ผลลัพธ์ที่เป็นรูปธรรม ไม่ใช่แค่คุยกันสนุกสนาน",
        "card5_title": "5) สรุป",
        "card5_icon": "users",
        "card5_text": "Workshop ที่ยอดเยี่ยม<strong>ช่วยเปลี่ยนความเห็นที่กระจัดกระจายให้เป็นเป้าหมายร่วม</strong> สร้างความผูกพันและทำให้ทุกคนพร้อมขับเคลื่อนโปรเจกต์ไปด้วยกัน",
        "memory_pills": ["Workshop มือโปร", "เตรียมโจทย์", "ระดมความคิด", "แมป Journey", "จัด Priority", "สรุป Action Plan"]
    }
]

print(f"Loaded {len(DOCUMENTS)} document specifications successfully.")
